import json

from fastapi import FastAPI
import uvicorn

from api.prompts import system_prompt

from sdk.messages.human import HumanMessage
from sdk.messages.system import SystemMessage
from sdk.llm.yandex.chat_model import YandexChatGPT

app = FastAPI()


@app.get('/action-info')
def get_action_info_gpt(user_prompt: str):
    """Get action info from gpt response"""

    model = YandexChatGPT()

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    result = model.invoke(messages).replace('`', '')

    try:
        result = json.loads(result)
        return result

    except json.JSONDecodeError:
        return {'error': 'Непредвиденная ошибка. Попробуйте написать запрос иначе'}


uvicorn.run(app, host='0.0.0.0', port=3125)
# uvicorn.run(app)
