from src.messages.human import HumanMessage
from src.messages.system import SystemMessage

messages = [
    SystemMessage(content="Ты помощник злого дракона"),
    HumanMessage(content="Эй! Вызови главного по фейерверкам!")
]

print(*[(m.content, m.type) for m in messages], sep='\n')