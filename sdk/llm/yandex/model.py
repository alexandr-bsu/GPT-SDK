from typing import List, Any, Literal, Dict
from enum import Enum
import requests

from sdk.retry import retry_n_times
from sdk.llm.yandex.settings import YandexAuth
from pydantic import BaseModel


class Message(BaseModel):
    text: str
    role: str


class HumanMessage(Message):
    """Wrapper for user message"""
    role: Literal['user'] = 'user'


class AssistantMessage(Message):
    """Wrapper for ai message"""
    role: Literal['assistant'] = 'assistant'


class SystemMessage(Message):
    """Wrapper for model instructions"""
    role: Literal['system'] = 'system'


class YandexGPTModel(Enum):
    Lite = 'yandexgpt-lite/latest'
    Pro = 'yandexgpt/latest'
    Summarization = 'summarization/latest'


class YandexGPT:
    temperature: float = 0.4
    max_tokens: int = 1500

    model = YandexGPTModel.Lite
    auth = YandexAuth()
    base_url: str = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

    @property
    def _model_uri(self):
        """Return model URI"""
        return f'gpt://{self.auth.yc_folder_id}/{self.model.value}'

    def invoke(self, messages: List[Message]):
        msgs_dump = [m.model_dump() for m in messages]
        return self._generate_messages(msgs_dump)

    @retry_n_times(4)
    def _generate_messages(self,
                           prompts: List[Dict[str, str]],
                           **kwargs: Any,
                           ):
        req = {
            "modelUri": self._model_uri,
            "completionOptions": {
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            },
            "messages": prompts
        }

        headers = self.auth.headers
        llm_response = requests.post(self.base_url, headers=headers, json=req)
        text = llm_response.json()
        return text['result']['alternatives'][0]['message']['text']
