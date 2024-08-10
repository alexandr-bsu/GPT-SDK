from fastapi import FastAPI
import uvicorn

from api.schema.gpt import BaseGptTask

from sdk.messages.human import HumanMessage
from sdk.messages.system import SystemMessage
from sdk.llm.yandex.chat_model import YandexChatGPT

app = FastAPI()


@app.post('/gpt')
def invoke_gpt(task: BaseGptTask):
    """Provide access to GPT model"""

    model = YandexChatGPT()
    messages = [
        SystemMessage(content=task.instructions),
        HumanMessage(content=task.prompt)
    ]
    result = model.invoke(messages)
    return {'result': result}

uvicorn.run(app, port=8000)