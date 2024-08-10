from sdk.messages.human import HumanMessage
from sdk.messages.system import SystemMessage
from sdk.llm.yandex.chat_model import YandexChatGPT

model = YandexChatGPT()
messages = [
    SystemMessage(content="Ты помощник злого дракона"),
    HumanMessage(content="Эй! Вызови главного по фейерверкам!")
]

print(model.invoke(messages))