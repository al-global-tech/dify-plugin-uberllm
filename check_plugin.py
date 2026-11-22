"""Check the MartLLM Dify plugin. Not shipped in the .difypkg.

Loads the plugin the way the Dify runtime does (manifest, provider and model
YAML, Python classes), then runs offline checks. With MARTLLM_KEY_FILE set to a
file holding an ull_ key, it also runs live checks: key validation (free),
custom-model validation (free) and one streamed + one non-streamed chat with
google/gemini-2.5-flash (a few tokens, well under $0.001).

    pip install "dify_plugin==0.10.2"
    python check_plugin.py                       # offline
    MARTLLM_KEY_FILE=~/ull_key python check_plugin.py   # offline + live
"""

import os
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent / "uberllm"
os.chdir(PLUGIN_DIR)
sys.path.insert(0, str(PLUGIN_DIR))

from dify_plugin.config.config import DifyPluginEnv  # noqa: E402
from dify_plugin.core.plugin_registration import PluginRegistration  # noqa: E402
from dify_plugin.entities.model import ModelFeature, ModelType  # noqa: E402
from dify_plugin.entities.model.message import UserPromptMessage  # noqa: E402
from dify_plugin.errors.model import (  # noqa: E402
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)

from models.llm.llm import plain_error  # noqa: E402

# --- offline -----------------------------------------------------------------
reg = PluginRegistration(DifyPluginEnv())
provider = reg.get_model_provider_instance("uberllm")
assert provider is not None, "provider did not load"
llm = reg.get_model_instance("uberllm", ModelType.LLM)
assert llm is not None, "LLM model class did not load"

schemas = {m.model: m for m in llm.predefined_models()}
assert len(schemas) == 20, f"expected 20 predefined models, got {len(schemas)}"
gemini = schemas["google/gemini-2.5-flash"]
assert ModelFeature.VISION in gemini.features and ModelFeature.MULTI_TOOL_CALL in gemini.features
assert all(r.name != "temperature" or r.max == 1 for r in schemas["anthropic/claude-opus-5.5"].parameter_rules)

body = '{"error":{"code":"%s","message":"m","type":"t"}}'
assert isinstance(plain_error(401, body % "invalid_api_key"), InvokeAuthorizationError)
assert "balance is too low" in str(plain_error(402, body % "insufficient_credits"))
assert "spend limit" in str(plain_error(402, body % "key_spend_cap_exceeded"))
assert "'x/y'" in str(plain_error(404, body % "model_not_found", "x/y"))
assert isinstance(plain_error(429, body % "rate_limited"), InvokeRateLimitError)
assert isinstance(plain_error(503, body % "no_available_provider"), InvokeServerUnavailableError)
assert str(plain_error(503, body % "no_available_provider")) == "m"
assert isinstance(plain_error(400, "not json"), InvokeBadRequestError)
print("offline: OK (plugin loads, 20 models, error messages)")

# --- live --------------------------------------------------------------------
key_file = os.environ.get("MARTLLM_KEY_FILE")
if not key_file:
    print("live: skipped (set MARTLLM_KEY_FILE)")
    sys.exit(0)
key = Path(key_file).expanduser().read_text().strip()

provider.validate_provider_credentials({"api_key": key})
try:
    provider.validate_provider_credentials({"api_key": "ull_" + "0" * 43})
    raise AssertionError("a wrong key was accepted")
except CredentialsValidateFailedError as e:
    assert "did not accept this API key" in str(e) and key not in str(e)
print("live: key check OK (good key accepted, wrong key refused in plain words)")

llm.validate_credentials("qwen/qwen3-coder", {"api_key": key})
for bad, words in (("google/not-a-model", "no model called"), ("black-forest-labs/flux-2-max-edit", "not a chat model")):
    try:
        llm.validate_credentials(bad, {"api_key": key})
        raise AssertionError(f"{bad} was accepted")
    except CredentialsValidateFailedError as e:
        assert words in str(e), str(e)
print("live: custom model check OK (chat model accepted, unknown and non-chat refused)")

msgs = [UserPromptMessage(content="Reply with the single word: pong")]
params = {"max_tokens": 16, "temperature": 0}


def run(stream: bool) -> tuple[str, int, object]:
    # The SDK always yields chunks; a non-streamed call yields one with the full reply.
    chunks = list(llm.invoke("google/gemini-2.5-flash", {"api_key": key}, msgs, dict(params), stream=stream, user="check"))
    text = "".join(c.delta.message.content or "" for c in chunks if isinstance(c.delta.message.content, str))
    assert text.strip(), f"empty reply (stream={stream})"
    return text.strip(), len(chunks), chunks[-1].delta.usage


for stream in (False, True):
    text, n, usage = run(stream)
    kind = "streamed" if stream else "non-streamed"
    print(f"live: {kind} OK -> {text!r} in {n} chunk(s) ({usage.prompt_tokens}+{usage.completion_tokens} tokens)")

try:
    list(llm.invoke("google/gemini-2.5-flash", {"api_key": "ull_" + "0" * 43}, msgs, dict(params), stream=False))
    raise AssertionError("a wrong key was accepted on chat")
except InvokeAuthorizationError as e:
    assert "did not accept this API key" in str(e)
print("live: wrong key on chat -> plain-words error OK")
