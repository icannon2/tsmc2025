from ..datasource import SQLRunner
from ..config import Config
from ..state import GlobalState
from discord import Role
from .functions import SQLFunctionCalling, CatalogFunctionCalling, FunctionCallingImpl
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

with open("src/chat/system_prompt/chat_system_prompt.txt", "r", encoding="utf-8") as f:
    chat_system_prompt = f.read()
with open(
    "src/chat/system_prompt/summary_system_prompt.txt", "r", encoding="utf-8"
) as f:
    summary_system_prompt = f.read()
with open("src/chat/system_prompt/language_prompt.txt", "r", encoding="utf-8") as f:
    language_prompt = f.read()
with open(
    "src/chat/system_prompt/language_json_schema.json", "r", encoding="utf-8"
) as f:
    language_json_schema = f.read()
with open("src/chat/system_prompt/chat_json_schema.json", "r", encoding="utf-8") as f:
    chat_json_schema = f.read()


client = None
gemini_config = None


class OpenaiWrapper:
    client: AsyncOpenAI
    messages: list[ChatCompletionMessageParam]
    tools: list[FunctionCallingImpl]
    model: str

    def __init__(
        self,
        openai: AsyncOpenAI,
        tools: list[FunctionCallingImpl] = None,
        system_prompt: str = "",
        model: str = "gpt-4o-mini",
    ):
        self.client = openai
        self.tools = [] if tools is None else tools

        self.messages = []
        self.messages.append({"role": "system", "content": system_prompt})
        self.model = model

    async def complete(self) -> str:
        if len(self.tools) == 0:
            res = await self.client.chat.completions.create(
                model=self.model, messages=self.messages
            )
        else:
            res = await self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=[tool.spec for tool in self.tools],
            )
        choice = res.choices[0]

        if choice.finish_reason != "tool_calls":
            self.messages.append(
                {"role": "assistant", "content": choice.message.content}
            )
            return choice.message.content

        for call in choice.message.tool_calls:
            matching_tool = next(
                (t for t in self.tools if t.spec.function.name == call.function.name),
                None,
            )
            if matching_tool is None:
                raise Exception(f"Tool {call.function.name} not found")
            tool_res = await matching_tool.process(call.tool.function.arguments)
            self.messages.append(choice.message)
            self.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": tool_res[:1024] + ".."
                    if len(tool_res) > 1024
                    else tool_res,
                }
            )
        return await self.complete()

    async def get_response(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        return await self.complete()

    @staticmethod
    async def one_shot(
        client: AsyncOpenAI,
        user_prompt: str,
        system_prompt: str = "",
        model: str = "gpt-4o-mini",
        tools: list[FunctionCallingImpl] = [],
    ) -> str:
        wrapper = OpenaiWrapper(client, tools, system_prompt, model)
        return await wrapper.get_response(user_prompt)


class RoomState:
    global_state: GlobalState
    sql_runner: SQLRunner
    roomtype: str
    wrapper: OpenaiWrapper | None
    language: str | None = None

    def __init__(
        self,
        config: Config,
        global_state: GlobalState,
        user_roles: list[Role],
        roomtype: str = "chat",
    ):
        self.global_state = global_state
        self.user_roles = user_roles
        self.roomtype = roomtype
        self.sql_runner = SQLRunner(
            config.datasource_path, [{"id": int(role.id)} for role in user_roles]
        )
        if roomtype == "summarize":
            self.wrapper = OpenaiWrapper(
                global_state.client, [], "summarize", "gpt-4o-mini"
            )

    async def get_response(self, message: str) -> str:
        if self.roomtype == "chat" and self.language is None:
            tools = [
                SQLFunctionCalling(self.sql_runner),
                CatalogFunctionCalling(self.sql_runner),
            ]
            self.language = await OpenaiWrapper.one_shot(
                self.global_state.client,
                message,
                """
You are a tool to determine user's perfered language.
User will input their question in their perfered language.
Output the language of the question.
available choices: english, chinese, spanish, french, german, italian, dutch, portuguese, russian, japanese, korean
                """,
            )
            self.wrapper = OpenaiWrapper(
                self.global_state.client,
                tools,
                f"""
You are now a financial chatbot and need to respond to the user's inquiry in {self.language} in a conversational manner, providing the financial information they seek. I have earnings call transcript and financial data (e.g. Cost of Goods Sold, Operating Expense, Operating Income, Revenue, Tax Expense, Total Asset, Gross profit margin, Operating margin.) on certain company within a specific period, so feel free to use function calls to get any data you need.

The user's question must satisfy all the rules below: 
1. The user's question must be relevant to tech companies from the following list: Amazon, AMD, Amkor, Apple, Applied Materials, Baidu, Broadcom, Cirrus Logic, Google, Himax, Intel, KLA, Marvell, Microchip, Microsoft, Nvidia, ON Semi, Qorvo, Qualcomm, Samsung, STM, Tencent, Texas Instruments, TSMC, and Western Digital.

2. The question should pertain to the valid period, with acceptable ranges including the years 2020, 2021, 2022, 2023, and 2024, and quarters Q1, Q2, Q3, or Q4.

3. The question must be relevent to finance.

If the user doesn't meet any requirements above, briefly explain to the user why you can't answer them as if you where a financial chatbot communicating directly to them. You can recommand the user some questions to ask .
-----------------------------------
However, if the user followed all rules, you can response them according to the earnings call transcript and financial data. You can use any function calls to get them. 
Additionally, incorporating charts can help users better understand the data.

These metrics are stored in an SQL database. You can generate charts in json format based on these metrics.
""",
                "gpt-4o-mini",
            )
        return await self.wrapper.get_response(message)

        """
        if mode == 'SUMMARY':
            system_prompt = summary_system_prompt
        else:
            system_prompt = chat_system_prompt

        history = [
            types.Content.model_validate(json.loads(content_str))
            for content_str in serialized_history
        ]
        
        self.chat = self.global_state.client.chats.create(
            model="gemini-2.0-flash", history=history, config=gemini_config
        )
        prompt = system_prompt + message
        response = self.chat.send_message(prompt)

        return response.text, [
                types.Content.model_dump_json(content)
                for content in self.chat._curated_history[-2:]
            ]
        """
