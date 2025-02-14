from google import genai
from ..datasource import SQLRunner
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from ..config import Config
from google import genai
from ..state import GlobalState
from discord import Role
import json
import csv
from .functions import FunctionCalling
from google.genai import types

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


class RoomState:
    function_calling_instance: FunctionCalling
    function_calling_list = []
    global_state: GlobalState
    chat: genai.chats.Chat
    engine: Engine
    session: Session
    user_roles: list[Role]
    sql_runner: SQLRunner
    roomtype: str

    def __init__(
        self, config: Config, global_state: GlobalState, user_roles: list[Role], roomtype: str
    ):
        global gemini_config
        self.global_state = global_state
        self.user_roles = user_roles
        self.roomtype = roomtype
        self.sql_runner = SQLRunner(
            config.datasource_path, [{"id": int(role.id)} for role in user_roles]
        )

        self.function_calling_instance = FunctionCalling(
            self.sql_runner, global_state.client
        )
        self.function_calling_list = [self.function_calling_instance.duckdb_stmt]

        gemini_config = types.GenerateContentConfig(
            tools=self.function_calling_list,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=10
            ),
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ),
        )

        self.chat = self.global_state.client.chats.create(
            model="gemini-2.0-flash", history=[], config=gemini_config
        )

    def _send_message(self, prompt: str, chat: genai.Client.chats) -> str:
        return chat.send_message(prompt).text

    def get_response(self, message: str, args = None) -> str:
        global chat_system_prompt, summary_system_prompt, language_prompt

        
        
        if self.roomtype == 'chat':

            language_prompt = language_prompt.replace("{question}", message)

            raw_language_list = self.global_state.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=language_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": json.loads(language_json_schema),
                },
            ).text

            language_list = json.loads(raw_language_list)["language"]

            if len(language_list) == 0:
                raise Exception("No language detected")
        
            system_prompt = chat_system_prompt
            response = self._send_message(
                system_prompt.replace("{question}", message).replace(
                    "{language}", language_list[0]
                ),
                self.chat,
            )
        else:
            system_prompt = summary_system_prompt
            prompt = system_prompt.replace("{company}", args[0]).replace("{language}", args[1]).replace("{start_time}", args[2]).replace("{end_time}", args[3])
            print(prompt)
            
            response = self._send_message(
                prompt, self.chat
            )

        

        return response

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
