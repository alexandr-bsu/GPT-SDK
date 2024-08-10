from pydantic import BaseModel


class BaseGptTask(BaseModel):
    """Base class for any gpt task"""

    instructions: str
    """Instructions for gpt model. Manipulates its behaviour"""

    prompt: str
