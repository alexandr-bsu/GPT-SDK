from abc import ABC
from typing import List, Literal, Sequence

from src.serializable import Serializable
from src.messages.utils import (
    AnyMessage,
    BaseMessage,
    HumanMessage,
    get_buffer_string,
)


class PromptValue(Serializable, ABC):
    """Base abstract class for input to any model"""

    @classmethod
    def is_serializable(cls) -> bool:
        """Is this class serializable. This is used to determine
                whether the class should be included in the schema.

                :return flag is this model serializable. Default True
                """
        return True