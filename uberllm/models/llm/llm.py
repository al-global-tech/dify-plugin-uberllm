import json
import re
from collections.abc import Generator
from typing import Optional, Union

import requests
from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model import AIModelEntity, ModelFeature
from dify_plugin.entities.model.llm import LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)

API_BASE = "https://api.uberllm.dev/v1"
KEYS_URL = "https://uberllm.dev/dashboard/keys"
CREDITS_URL = "https://uberllm.dev/dashboard/credits"
MODELS_URL = "https://uberllm.dev/models"
TIMEOUT = (10, 30)

# The SDK raises InvokeError("API request failed with status code <n>: <body>")
# for any non-200 answer. We read the status and UberLLM's error back out of it.
# ponytail: string parse of the SDK message; if the SDK rewords it we fall back
# to re-raising the SDK error unchanged, so nothing is lost.
_SDK_ERROR = re.compile(r"status code (\d{3}): (.*)", re.DOTALL)


def _error_code_and_message(response_text: str) -> tuple[str, str]:
    """UberLLM answers errors as {"error": {"code": ..., "message": ...}}."""
    try:
        err = json.loads(response_text).get("error") or {}
        if isinstance(err, dict):
            return str(err.get("code") or ""), str(err.get("message") or "")
        return "", str(err)
    except (ValueError, AttributeError):
        return "", response_text.strip()[:300]


def plain_error(status: int, response_text: str, model: str = "") -> InvokeError:
    """Turn an UberLLM error answer into a Dify error with a plain-words message."""
    code, message = _error_code_and_message(response_text)
    if status in (401, 403):
        return InvokeAuthorizationError(
            f"UberLLM did not accept this API key. Copy a key from {KEYS_URL} and paste it again."
        )
    if code == "insufficient_credits":
        return InvokeBadRequestError(
            f"Your UberLLM balance is too low for this request. Add credit at {CREDITS_URL}."
        )
    if code == "key_spend_cap_exceeded":
        return InvokeBadRequestError(
            f"This UberLLM key reached its spend limit. Raise the limit at {KEYS_URL} or use another key."
        )
    if status == 404 or code == "model_not_found":
        name = f"'{model}'" if model else "that name"
        return InvokeBadRequestError(
            f"UberLLM has no model called {name}. Copy the exact name from {MODELS_URL}."
        )
    if status == 429:
        return InvokeRateLimitError(
            "Too many requests on this UberLLM key right now. Wait a moment and try again."
        )
    if status >= 500:
        return InvokeServerUnavailableError(
            message or "UberLLM could not answer right now. Try again in a moment."
        )
    return InvokeBadRequestError(message or f"UberLLM refused the request (error {status}).")


def check_key(api_key: str) -> None:
    """Free check that the key works: reads the balance, spends nothing."""
    if not api_key:
        raise CredentialsValidateFailedError(f"Paste your UberLLM API key. Get one at {KEYS_URL}.")
    try:
        resp = requests.get(
            f"{API_BASE}/balance",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        raise CredentialsValidateFailedError(
            "Could not reach UberLLM. Check that this Dify server can open https://api.uberllm.dev."
        ) from None
    if resp.status_code != 200:
        raise CredentialsValidateFailedError(str(plain_error(resp.status_code, resp.text)))


def check_model(api_key: str, model: str) -> None:
    """Free check that the key works and the model is a chat model on UberLLM."""
    if not api_key:
        raise CredentialsValidateFailedError(f"Paste your UberLLM API key. Get one at {KEYS_URL}.")
    try:
        resp = requests.get(
            f"{API_BASE}/models/{model.strip()}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        raise CredentialsValidateFailedError(
            "Could not reach UberLLM. Check that this Dify server can open https://api.uberllm.dev."
        ) from None
    if resp.status_code != 200:
        raise CredentialsValidateFailedError(str(plain_error(resp.status_code, resp.text, model)))
    kind = (resp.json() or {}).get("type", "chat")
    if kind != "chat":
        raise CredentialsValidateFailedError(
            f"'{model}' is a {kind} model, not a chat model. Pick a chat model from {MODELS_URL}."
        )


class UberLLMLargeLanguageModel(OAICompatLargeLanguageModel):
    def _update_credential(self, model: str, credentials: dict) -> None:
        credentials["endpoint_url"] = API_BASE
        credentials["mode"] = "chat"  # UberLLM serves chat completions only
        schema = self.get_model_schema(model, credentials)
        if schema and {ModelFeature.TOOL_CALL, ModelFeature.MULTI_TOOL_CALL} & set(
            schema.features or []
        ):
            credentials["function_calling_type"] = "tool_call"

    def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity:
        credentials["mode"] = "chat"
        return super().get_customizable_model_schema(model, credentials)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        check_model(credentials.get("api_key", ""), model)

    def _transform_invoke_error(self, error: Exception) -> InvokeError:
        # Our errors already carry a plain-words message and the right type.
        if isinstance(error, InvokeError):
            return error
        return super()._transform_invoke_error(error)

    def _generate(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        self._update_credential(model, credentials)
        try:
            return super()._generate(
                model, credentials, prompt_messages, model_parameters, tools, stop, stream, user
            )
        except InvokeError as ex:
            match = _SDK_ERROR.search(str(ex))
            if not match:
                raise
            raise plain_error(int(match.group(1)), match.group(2), model) from None

    def get_num_tokens(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        tools: Optional[list[PromptMessageTool]] = None,
    ) -> int:
        self._update_credential(model, credentials)
        return super().get_num_tokens(model, credentials, prompt_messages, tools)
