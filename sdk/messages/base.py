from sdk.serializable import Serializable
from sdk.utils.merge import merge_lists, merge_dicts

from typing import Dict, List, Optional, Sequence, Union

from pydantic import Field
from pydantic_settings import SettingsConfigDict


class BaseMessage(Serializable):
    """Base abstract message class. Messages are inputs and outputs for models"""

    content: Union[str, List[Union[str, Dict]]]
    """String contents of the messages"""

    additional_kwargs: Dict = Field(default_factory=dict)
    """Reserved for additional payload data associated with the message.
    For example, for a message from an AI, this could include tool calls as
    encoded by the model provider."""

    response_metadata: Dict = Field(default_factory=dict)
    """Response metadata. For example: response headers, log probability, token counts, etc."""

    type: str
    """The purpose of this field is easy detection message's type for deserialization"""

    name: Optional[str] = None
    """Human-readable name of the message. Optional field, use only for convenience"""

    id: Optional[str] = None
    """Message's id. Should be provided by provider/model which created this message. Optional field"""

    model_config = SettingsConfigDict(extra='allow')

    @classmethod
    def is_serializable(cls) -> bool:
        """Is this class serializable. This is used to determine
        whether the class should be included in the schema.

        :return flag is this model serializable. Default True
        """

        return True

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the object
        For example: For if the class is `gpt_sdk.llms.Summarize`, then the
        namespace is ["gpt_sdk", "llms"]
        """

        return ['gpt_sdk', 'schema', 'messages']

    def __add__(self, other):
        """Concatenates this message to another message"""
        raise NotImplementedError()


def merge_content(
        first_content: Union[str, List[Union[str, Dict]]],
        *contents: Union[str, List[Union[str, Dict]]]
) -> Union[str, List[Union[str, Dict]]]:
    """Merges two contents
    :param first_content: The first content. Can be a string or a list.
    :param contents: Chunk of contents. Can be a string or a list.

    :returns merged content
    """

    merged = first_content
    for content in contents:
        if isinstance(merged, str):
            # if the next chunk is also a string, then merge it naively
            if isinstance(content, str):
                merged += content
            # if the next chunk is a list, add the current to the start of the list
            else:
                merged = [merged] + content

        elif isinstance(merged, list):
            # if both are lists
            merged = merge_lists(merged, content)
        # If the first content is a list, and the second content is a string
        else:
            # if the last element is a string, concat string to last element of the list
            if merged and isinstance(merged[-1], str):
                merged[-1] += content
            # If second content is an empty string, treat as a no-op
            elif content == "":
                pass
            else:
                # Otherwise, add the second content as a new element of the list
                merged.append(content)

    return merged


class BaseChunkMessage(BaseMessage):
    """Class Message chunk which can be merged with other message chunks"""

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the object
        For example: For if the class is `gpt_sdk.llms.Summarize`, then the
        namespace is ["gpt_sdk", "llms"]
        """

        return ['gpt_sdk', 'schema', 'messages']

    def __add__(self, other):
        """Message chunks support concatenation with other message chunks.
        This functionality is useful to combine message chunks yielded from
        a streaming model into a complete message.

        :param other - Another message chunk to concatenate with this one
        :returns A new message chunk that is the concatenation of this message chunk and the other message chunk.
        :raise TypeError: If the other object is not a message chunk.

        For example,
        AIMessageChunk(content="Hello") + AIMessageChunk(content=" World") = AIMessageChunk(content="Hello World")
        """

        if isinstance(other, BaseChunkMessage):
            # If both are (subclasses of) BaseMessageChunk,
            # concat into a single BaseMessageChunk

            return self.__class__(
                id=self.id,
                type=self.type,
                content=merge_content(self.content, other.content),
                additional_kwargs=merge_dicts(
                    self.additional_kwargs, other.additional_kwargs
                ),
                response_metadata=merge_dicts(
                    self.response_metadata, other.response_metadata
                )
            )

        elif isinstance(other, list) and all(isinstance(o, BaseChunkMessage) for o in other):
            content = merge_content(self.content, *(o.content for o in other))
            additional_kwargs = merge_dicts(
                self.additional_kwargs, *(o.additional_kwargs for o in other)
            )
            response_metadata = merge_dicts(
                self.response_metadata, *(o.response_metadata for o in other)
            )

            return self.__class__(
                id=self.id,
                type=self.type,
                content=content,
                additional_kwargs=additional_kwargs,
                response_metadata=response_metadata
            )

        else:
            raise TypeError('unsupported operand type(s) for +: "'
                f"{self.__class__.__name__}"
                f'" and "{other.__class__.__name__}"')


def message_to_dict(message: BaseMessage) -> dict:
    """Convert a Message to a dictionary.
    :param message: Message to convert.
    :returns
        Message as a dict. The dict will have a "type" key with the message type
        and a "data" key with the message data as a dict.
    """
    return {"type": message.type, "data": message.model_dump()}


def messages_to_dict(messages: Sequence[BaseMessage]) -> List[dict]:
    """Convert a sequence of Messages to a list of dictionaries.
    :param messages: Sequence of messages (as BaseMessages) to convert.
    :returns
        List of messages as dicts.
    """
    return [message_to_dict(m) for m in messages]


