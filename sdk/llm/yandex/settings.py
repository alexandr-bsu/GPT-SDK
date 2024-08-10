from pydantic_settings import BaseSettings, SettingsConfigDict
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))[:-len('sdk/llm/yandex')]
CONFIG_PATH = os.path.join(ROOT_DIR, '.env')


class YandexAuth(BaseSettings):
    """Credentials for Yandex Cloud from .env file"""
    yc_api_key_id: str
    yc_api_key: str
    yc_folder_id: str

    model_config = SettingsConfigDict(env_file=CONFIG_PATH, extra='ignore')

    @property
    def headers(self):
        """Returns auth headers"""
        return {
            'Authorization': f'Api-key {self.yc_api_key}',
            'x-folder-id': self.yc_folder_id
        }


class YException(Exception):
    pass
