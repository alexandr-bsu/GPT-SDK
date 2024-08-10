from typing import Union, Sequence
from sdk.messages.system import SystemMessage
from sdk.messages.chat import ChatMessage
from sdk.messages.human import HumanMessage
from sdk.messages.base import BaseMessage

# TODO: Add Tool, Function and AI Messages
AnyMessage = Union[
    HumanMessage,
    ChatMessage,
    SystemMessage
]


# TODO: Add Tool, Function and AI Messages support
def get_buffer_string(messages: Sequence[BaseMessage], human_prefix="Human", ai_prefix="AI") -> str:
    """Convert a sequence of Messages to strings and concatenate them into one
    :param ai_prefix: The prefix to prepend to contents of AIMessages. Default is "AI"
    :param human_prefix: The prefix to prepend to contents of HumanMessages. Default is "Human"
    :param messages - Messages to be converted to strings
    :return A single string concatenation of all input messages.
    :raise If an unsupported message type is encountered.
    """

    string_messages = []
    for message in messages:
        if isinstance(message, HumanMessage):
            role = human_prefix
        elif isinstance(message, SystemMessage):
            role = 'system'
        elif isinstance(message, ChatMessage):
            role = message.role
        else:
            raise ValueError('Message has unsupported type')

        message_prep = f'{role}: {message.content}'
        string_messages.append(message_prep)

    return '\n'.join(string_messages)