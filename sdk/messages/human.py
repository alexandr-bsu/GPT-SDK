from typing import List, Literal
from sdk.messages.base import BaseMessage, BaseChunkMessage


class HumanMessage(BaseMessage):
    """Message from a human.
    HumanMessages are messages that are passed in from a human to the model."""

    type: Literal["human"] = "human"
    """The type of the message (used during serialization). Defaults to "human"."""

    example: bool = False
    """Use to denote that a message is part of an example conversation."""

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the object.
        Default is ["gpt_sdk", "schema", "messages"].
        """
        return ["gpt_sdk", "schema", "messages"]


# See use case: https://docs.pydantic.dev/latest/concepts/models/#rebuild-model-schema
HumanMessage.model_rebuild()


class HumanChunkMessage(HumanMessage, BaseChunkMessage):
    type: Literal["HumanChunkMessage"] = "HumanChunkMessage"
    """The type of the message (used during serialization). Defaults to "HumanChunkMessage"."""

    @classmethod
    def get_namespace(cls) -> List[str]:
        return ['gpt_sdk', 'schema', 'messages']
