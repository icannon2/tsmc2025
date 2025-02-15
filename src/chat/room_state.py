from ..visualize import Visualizer
from ..datasource import SQLRunner
from ..config import Config
from ..state import GlobalState
from discord import Role
from .functions import (
    SQLFunctionCalling,
    CatalogFunctionCalling,
    FunctionCallingImpl,
    IcebergeConntection,
)
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

        self.messages.append(choice.message)

        for call in choice.message.tool_calls:
            matching_tool = next(
                (
                    t
                    for t in self.tools
                    if t.spec["function"]["name"] == call.function.name
                ),
                None,
            )
            if matching_tool is None:
                raise Exception(f"Tool {call.function.name} not found")
            tool_res = await matching_tool.process(call.function.arguments)
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
                global_state.client,
                [],
                summary_system_prompt.replace("{tables}", self.sql_runner.get_tables()),
                "gpt-4o-mini",
            )

    async def get_response(self, arg: str | tuple) -> str:
        if self.roomtype == "chat" and self.language is None:
            tools = [
                SQLFunctionCalling(self.sql_runner),
                CatalogFunctionCalling(self.sql_runner),
                IcebergeConntection(self.sql_runner),
            ]
            self.language = await OpenaiWrapper.one_shot(
                self.global_state.client, arg, language_prompt
            )
            self.wrapper = OpenaiWrapper(
                self.global_state.client,
                tools,
                chat_system_prompt.replace("{language}", self.language).replace(
                    "{table}", str(self.sql_runner.get_tables())
                ),
                "gpt-4o-mini",
            )
        elif self.roomtype == "summarize":
            tools = [
                SQLFunctionCalling(self.sql_runner),
                CatalogFunctionCalling(self.sql_runner),
            ]
            prompt = (
                summary_system_prompt.replace("{language}", arg[0])
                .replace("{campany}", arg[1])
                .replace("{start_time}", arg[2])
                .replace("{end_time}", arg[3])
            )
            return await OpenaiWrapper.one_shot(
                client=self.global_state.client,
                user_prompt=prompt,
                system_prompt="",
                model="gpt-4o-mini",
                tools=tools,
            )
        return await self.wrapper.get_response(arg)

    def get_visualizer(self) -> Visualizer:
        return Visualizer(self.sql_runner)
