from typing import List, Any

import sdk.llm.yandex.model as ym
from sdk.messages.base import BaseMessage
from sdk.messages.human import HumanMessage
from sdk.messages.system import SystemMessage


class YandexChatGPT(ym.YandexGPT):

    @staticmethod
    def convert_message(message: BaseMessage, **kwargs: Any) -> ym.Message:
        """Convert BaseMessage to Yandex Message format"""
        if isinstance(message, HumanMessage):
            return ym.HumanMessage(text=message.content)
        if isinstance(message, SystemMessage):
            return ym.SystemMessage(text=message.content)

    def invoke(self, messages: List[BaseMessage], **kwargs):
        converted_messages = [self.convert_message(m, **kwargs) for m in messages]
        result = super().invoke(converted_messages)
        return result
