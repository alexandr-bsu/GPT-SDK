from typing import List, Literal
from src.messages.base import BaseMessage, BaseChunkMessage


class SystemMessage(BaseMessage):
    """Message that can be assigned an arbitrary speaker (i.e. role)."""

    type: Literal["system"] = "system"
    """The type of the message (used during serialization). Defaults to "system"."""

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the object.
        Default is ["gpt_sdk", "schema", "messages"].
        """
        return ["gpt_sdk", "schema", "messages"]


# See use case: https://docs.pydantic.dev/latest/concepts/models/#rebuild-model-schema
SystemMessage.model_rebuild()


class SystemChunkMessage(SystemMessage, BaseChunkMessage):
    type: Literal["SystemChunkMessage"] = "SystemChunkMessage"
    """The type of the message (used during serialization). Defaults to "SystemChunkMessage"."""

    @classmethod
    def get_namespace(cls) -> List[str]:
        return ['gpt_sdk', 'schema', 'messages']
