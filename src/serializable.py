from abc import ABC
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    cast,
)

from pydantic import BaseModel, model_serializer
from pydantic_settings import SettingsConfigDict


class BaseSerialized(BaseModel):
    """
    Base class for serialized objects
    :param version - version of the serialization format
    :param id - object's id
    :param name - object's name. Optional
    :param graph - object's graph. Optional
    """

    version: int
    id: List[str]
    name: Optional[str] = None
    graph: Optional[Dict[str, Any]] = None


class SerializedConstructor(BaseSerialized):
    """
    Class for serialized constructor
    :param type - object's type. Must be "constructor"
    :param kwargs - the constructor arguments
    """

    type: Literal['constructor']
    kwargs: Dict[str, Any]


class SerializedSecret(BaseSerialized):
    """
    Class for serialized secret
    :param type - object's type. Must be "secret"
    """

    type: Literal['secret']


class SerializedNotImplemented(BaseSerialized):
    """
    Class for serialized NotImplemented
    :param type - object's type. Must be "not_implemented"
    :param repr - object representation. Optional
    """

    type: Literal['not_implemented']
    repr: Optional[str]


def check_model_neq_default_value(model: BaseModel, key, value):
    """Check: value doesn't equal to field's default vault
    :param value
    :param key - field's name
    :param model - Model for check
    """
    return model.model_fields[key].default == value


class Serializable(BaseModel, ABC):
    """Serializable base class. This class is used to serialize objects to JSON

    :method is_serializable - is this class serializable. By design even if a class inherits from Serializable,
    it is not serializable by default. It is used to prevent accidental object of objects that should not be serialized.
    :method get_namespace - During deserialization, this namespace is used to identify the correct class to instantiate.
    :property secrets - A map of constructor argument names to secret ids.
    :property attributes -  List of additional attribute names that should be included
    as part of the serialized representation.
    """

    model_config = SettingsConfigDict(extra='ignore')

    @classmethod
    def is_serializable(cls) -> bool:
        """Is this class serializable.
        By design even if a class inherits from Serializable, it is not serializable by default.
        It is used to prevent accidental object of objects that should not be serialized
        :return flag is this model serializable. Default false
        """

        return False

    @classmethod
    def get_namespace(cls) -> List[str]:
        """Get the namespace of the object
        For example: For if the class is `RagYandexGPT.llms.Summarize`, then the
        namespace is ["RagYandexGPT", "llms"]
        """

        return cls.__module__.split('.')

    @property
    def secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids.
        For example, {"yandex_api.key": "YANDEX_API_KEY", "yandex_api.key_id": "KEY_ID_123", ...}"""
        return {}

    @property
    def attributes(self) -> Dict:
        """List of attribute names that should be included in the serialized kwargs.

        These attributes must be accepted by the constructor.
        Default is an empty dictionary.
        """
        return {}

    @classmethod
    def get_id(cls) -> List[str]:
        """A unique identifier for this class for serialization purposes.
        For example: For if the class is `RagYandexGPT.llms.Summarize`, then the
        namespace is ["RagYandexGPT", "llms", 'Summarize']
        """
        return [*cls.get_namespace(), cls.__name__]

    @model_serializer
    def to_json(self) -> Dict[str, Any]:
        """Serialize the object to JSON.
        :return serialized JSON object"""

        if not self.is_serializable():
            return to_json_not_implemented().model_dump()

        secrets = {}

        # Get field values from kwargs if they are not excluded for serialization and "useful"
        kwargs = {
            k: getattr(self, k, v)
            for k, v in self.model_fields.items()
            if not v.exclude and self._is_field_useful(k, v)
        }

        for cls in [None, *self.__class__.mro()]:
            if cls is Serializable:
                break

            # Why does it work???
            # Merge secrets from inherited models
            this = cast(Serializable, self if cls is None else super(cls, self))
            secrets.update(this.secrets)

            # Now also add the aliases for the secrets
            # This ensures known secret aliases are hidden.
            # Use list(secrets) instead of secrets.keys(), because dict can expand during iterations
            for key in list(secrets):
                value = secrets[key]
                if key in this.model_fields.keys():
                    if this.model_fields[key].alias is not None:
                        secrets[this.model_fields[key].alias] = value

            # Merge kwarg attributes from inherited models
            kwargs.update(this.attributes)

        # include all secrets, even if not specified in kwargs
        # as these secrets may be passed as an environment variable instead
        for key in secrets.keys():
            secret_value = getattr(self, key, None) or kwargs.get(key)
            if secret_value is not None:
                kwargs.update({key: secret_value})

        return {
            'version': 1,
            'type': 'constructor',
            'id': self.get_id(),
            'kwargs': kwargs
            if not secrets
            else Serializable._replace_secrets(kwargs, secrets),
        }

    def to_json_not_implemented(self) -> SerializedNotImplemented:
        return to_json_not_implemented(self)

    @staticmethod
    def _replace_secrets(root: Dict[Any, Any], secrets_map: Dict[str, str]) -> Dict[Any, Any]:
        result = root.copy()
        for path, secret_id in secrets_map.items():
            [*parts, last] = path.split(".")
            current = result
            for part in parts:
                if part not in current:
                    break
                current[part] = current[part].copy()
                current = current[part]
            if last in current:
                current[last] = {
                    'version': 1,
                    'type': 'secret',
                    'id': [secret_id],
                }
        return result

    def _is_field_useful(self, field_name, value):
        """Check if a field is useful as a constructor argument.

               Args:
                   field_name: Model field's name.
                   value: field's value.

               Returns:
                   Whether the field is useful. If the field is required, it is useful.
                   If the field is not required, it is useful if the value is not None.
                   If the field is not required and the value is None, it is useful if the
                   default value is different from the current value.
               """
        return (
                self.model_fields[field_name].is_required()
                or value
                or check_model_neq_default_value(self, field_name, value)
        )


def to_json_not_implemented(obj: Optional[object] = None) -> SerializedNotImplemented:
    """Serialize a "not implemented" object.
    :params obj - object to serialize.
    :returns SerializedNotImplemented
    """
    _id: List[str] = []
    try:
        if hasattr(obj, '__name__'):
            _id = [*obj.__module__.split('.'), obj.__name__]
        elif hasattr(obj, '__class__'):
            _id = [*obj.__class__.__module__.split('.'), obj.__class__.__name__]
    except Exception:
        pass

    result: SerializedNotImplemented = SerializedNotImplemented(version=1, id=_id, type='not_implemented', repr=None)

    try:
        result.repr = repr(obj)
    except Exception:
        pass
    return result


# class Test(Serializable):
#     test: int
#     yandex_api_key: str
#
#     @classmethod
#     def is_serializable(cls) -> bool:
#         return True
#
#     @property
#     def secrets(self) -> Dict[str, str]:
#         return {"yandex_api_key": "YANDEX_API_KEY"}
#
#
# test = Test(test=1, yandex_api_key='q1')
# print(test.to_json())
