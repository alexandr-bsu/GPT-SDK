from typing import List, Literal
from src.messages.base import BaseMessage, BaseChunkMessage, merge_content
from src.utils.merge import merge_dicts


class ChatMessage(BaseMessage):
    """Message that can be assigned an arbitrary speaker (i.e. role)."""

    role: str
    """The speaker / role of the Message."""

    type: Literal["chat"] = "chat"
    """The type of the message (used during serialization). Defaults to "chat"."""

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the object.
        Default is ["gpt_sdk", "schema", "messages"].
        """
        return ["gpt_sdk", "schema", "messages"]


# See use case: https://docs.pydantic.dev/latest/concepts/models/#rebuild-model-schema
ChatMessage.model_rebuild()


class ChatChunkMessage(BaseChunkMessage):
    type: Literal["ChatMessageChunk"] = "ChatMessageChunk"
    """The type of the message (used during serialization). Defaults to "ChatMessageChunk"."""

    @classmethod
    def get_namespace(cls) -> List[str]:
        return ['gpt_sdk', 'schema', 'messages']

    def __add__(self, other):
        if isinstance(other, ChatChunkMessage):
            if self.role != other.role:
                raise ValueError('Can\'t concat chunk messages with different roles')
            return self.__class__(
                id=self.id,
                role=self.role,
                content=merge_content(self.content, other.content),
                additional_kwargs=merge_dicts(self.additional_kwargs, other.additional_kwargs),
                response_metadata=merge_dicts(self.response_metadata, other.response_metadata)
            )
        elif isinstance(other, BaseMessage):
            return self.__class__(
                id=self.id,
                role=self.role,
                content=merge_content(self.content, other.content),
                additional_kwargs=merge_dicts(self.additional_kwargs, other.additional_kwargs),
                response_metadata=merge_dicts(self.response_metadata, other.response_metadata)
            )
        else:
            return super().__add__(other)
