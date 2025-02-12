from ..state import State

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
