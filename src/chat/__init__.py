from google import genai
from config import Config


class Message:
    # content and image_base64 may be vaild at the same time
    content: str
    image_base64: str
    # user_roles and user_id are uuids string
    user_roles: list[str]
    user_id: str

    def __init__(self, content: str, image_base64: str):
        self.content = content
        self.image_base64 = image_base64


class State:
    client: genai.Client

    def __init__(self, config: Config):
        # read the config(may contain API_KEY) and initialize the client
        pass

    def process(self, message: Message):
        # process the message and return the response
        pass


"""
An abstract class for function calling.

We actually create new instances of this class when a chatroom is created.
"""


class FunctionCalling:
    name: str
    description: str
    parameters: any

    def __init__(self, state: State):
        pass

    """
    Process the request and return the response.

    request is a string that conforms to the function's parameters.

    For example, if the function is to add two numbers, request can be "{\"a\": 1, \"b\": 2 }".(serialized json string)
    """

    def process(self, request: str):
        pass
