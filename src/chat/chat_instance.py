from google import genai
from .state import RoomState
from ..state import GlobalState
from typing import Tuple
import json
from .functions import ChatModeFunctionCalling
from google.genai import types

chat_system_prompt = "Please handle the message below with calling functions, and reply in less than 2000 characters. message: "
summary_system_prompt = "Please handle the message below in short summary with calling functions, and reply in less than 2000 characters. message: "
client = None
gemini_config = None


class ChatInstance:
    function_calling_instance: ChatModeFunctionCalling
    function_calling_list = []
    chat: genai.chats.Chat

    def __init__(self, global_state: GlobalState, room_state: RoomState):
        # TODO: replace with global_state.genai
        global client, gemini_config

        if not client:
            client = genai.client.Client(api_key=config.gemini_api_key)

        function_calling_instance = ChatModeFunctionCalling()
        function_calling_list = [function_calling_instance.duckdb_stmt]

        gemini_config = types.GenerateContentConfig(
            tools=self.function_calling_list,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=10
            ),
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ),
        )
        self.chat = client.chats.create(
            model="gemini-2.0-flash", history=[], config=gemini_config
        )

    def get_response(
        self, message: str, serialized_history: str, summary_mode: bool = False
    ) -> Tuple[str, str]:
        global chat_system_prompt, summary_system_prompt, client, gemini_config
        if summary_mode:
            system_prompt = summary_system_prompt
        else:
            system_prompt = chat_system_prompt

        history = [
            types.Content.model_validate(json.loads(content_str))
            for content_str in json.loads(serialized_history)
        ]

        self.chat = client.chats.create(
            model="gemini-2.0-flash", history=history, config=gemini_config
        )
        prompt = system_prompt + message
        response = self.chat.send_message(prompt)

        return response.text, json.dumps(
            [
                types.Content.model_dump_json(content)
                for content in self.chat._curated_history
            ]
        )
