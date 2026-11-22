from dify_plugin import ModelProvider

from models.llm.llm import check_key


class MartLLMProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        # Reads the key's balance: confirms the key works without spending anything.
        check_key(credentials.get("api_key", ""))
