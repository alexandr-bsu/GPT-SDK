from typing import Generic, TypeVar, Optional, Type, get_args
from pydantic import BaseModel


Input = TypeVar('Input')
Output = TypeVar('Output')


class Runnable(Generic[Input, Output]):
    name: Optional[str]
    """"Name of Runnable. Use for dbug and tracing"""

    def get_name(self, suffix: Optional[str] = None, name: Optional[str] = None):

        """Get the name of the Runnable"""
        name = name or self.name or self.__class__.name

        if suffix:
            if name[0].isupper():
                return name + suffix.title()
            else:
                return f'{name}_{suffix.lower()}'
        else:
            return name

    @property
    def input_type(self) -> Type[Input]:
        """The type of input this Runnable accepts specified as a type annotation"""
        for cls in self.__class__.__orig_bases__:
            type_args = get_args(cls)
            if type_args and len(type_args) == 2:
               return type_args[0]

        raise TypeError(f'Runnable {self.get_name()} doesn\'t have an inferable InputType.'
                        'Override the input_type property to specify input type')

    @property
    def output_type(self) -> Type[Output]:
        """The type of output this Runnable accepts specified as a type annotation"""
        for cls in self.__class__.__orig_bases__:
            type_args = get_args(cls)
            if type_args and len(type_args) == 2:
                return type_args[1]

        raise TypeError(f'Runnable {self.get_name()} doesn\'t have an inferable OutputType.'
                        'Override the input_type property to specify input type')

    @property
    def input_schema(self) -> Type[BaseModel]:
        """The type of input this Runnable accepts specified as a pydantic model."""
        return self.get_input_schema()

    def get_input_schema(self, config: Optional = None) -> Type[BaseModel]:
        ...

    @property
    def output_schema(self) -> Type[BaseModel]:
        """The type of output this Runnable accepts specified as a pydantic model."""
        return self.get_output_schema()

