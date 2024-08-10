from abc import ABC, abstractmethod
from typing import List, Literal, Sequence, cast

from src.serializable import Serializable
from src.messages.utils import (
    AnyMessage,
    BaseMessage,
    HumanMessage,
    get_buffer_string,
)

from pydantic import BaseModel


class PromptValue(Serializable, ABC):
    """Base abstract class for input to any model"""

    @classmethod
    def is_serializable(cls) -> bool:
        """Is this class serializable. This is used to determine
                whether the class should be included in the schema.

                :return flag is this model serializable. Default True
                """
        return True

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object.
        This is used to determine the namespace of the object when serializing.
        Defaults to ["langchain", "schema", "prompt"].
        """
        return ['gpt_sdk', 'schema', 'prompt']

    @abstractmethod
    def to_string(self) -> str:
        """Return prompt value as string."""

    @abstractmethod
    def to_messages(self) -> List[BaseMessage]:
        """Return prompt value as list of messages"""


class StringPromptValue(PromptValue):
    type: Literal['StringPromptValue'] = 'StringPromptValue'
    text: str

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object.
        This is used to determine the namespace of the object when serializing.
        Defaults to ["langchain", "schema", "prompt"].
        """
        return ['gpt_sdk', 'prompt', 'base']

    def to_string(self) -> str:
        return self.text

    def to_messages(self) -> List[BaseMessage]:
        return [HumanMessage(content=self.text)]


class ChatPromptValue(PromptValue):
    """Chat prompt value.

    A type of a prompt value that is built from messages.
    """

    messages: Sequence[BaseMessage]
    """List of messages."""

    def to_string(self) -> str:
        """Return prompt as string."""
        return get_buffer_string(self.messages)

    def to_messages(self) -> List[BaseMessage]:
        """Return prompt as a list of messages."""
        return list(self.messages)

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object.
        This is used to determine the namespace of the object when serializing.
        Defaults to ["gpt_sdk", "prompts", "chat"].
        """
        return ['gpt_sdk', 'prompts', 'chat']


class ImageURL(BaseMessage):
    """Image URL."""

    detail: Literal['auto', 'low', 'high']
    """Specifies the detail level of the image. Defaults to "auto".
    Can be "auto", "low", or "high"."""

    url: str
    """Either a URL of the image or the base64 encoded image data."""


class ImagePromptValue(PromptValue):
    """Image prompt value."""

    image_url: ImageURL
    """Image URL."""
    type: Literal["ImagePromptValue"] = 'ImagePromptValue'

    def to_string(self) -> str:
        """Return prompt (image URL) as string."""
        return self.image_url['url']

    def to_messages(self) -> List[BaseMessage]:
        """Return prompt (image URL) as messages."""
        return [HumanMessage(content=[cast(dict, self.image_url.model_dump())])]


class ChatPromptValueConcrete(ChatPromptValue):
    """Chat prompt value which explicitly lists out the message types it accepts.
    For use in external schemas."""

    messages: Sequence[AnyMessage]
    """Sequence of messages."""

    type: Literal["ChatPromptValueConcrete"] = 'ChatPromptValueConcrete'

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object.
        This is used to determine the namespace of the object when serializing.
        Defaults to ["langchain", "prompts", "chat"].
        """
        return ['gpt_sdk', 'prompts', 'chat']
