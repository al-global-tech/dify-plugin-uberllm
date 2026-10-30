# UberLLM for Dify

**Author:** uberllm · **Type:** model provider · **Source:** https://github.com/PSA-Team-source/dify-plugin-uberllm

UberLLM gives you hundreds of chat models (OpenAI, Anthropic, Google, DeepSeek, Qwen, Kimi, GLM, Grok and more) behind one API key, at list price or less. This plugin adds UberLLM as a model provider in Dify, so you can pick any of those models in your apps, chatflows, workflows and agents.

What works:

- Chat, with streamed replies
- Tools (function calling) in agents and workflows
- Pictures as input, on models that can read them
- JSON replies, and replies that follow a JSON schema, on models that support them
- 20 popular models ready to pick, plus any other chat model on UberLLM by its name

## Setup

1. Sign in at [uberllm.dev](https://uberllm.dev) and add credit under **Dashboard → Credits**. Calls are prepaid, and a new account starts at $0.
2. Create an API key under [Dashboard → API keys](https://uberllm.dev/dashboard/keys). It starts with `ull_` and is shown once, so copy it.
3. In Dify, open **Settings → Model Provider**, find **UberLLM** and click **Setup**.
4. Paste the key and save. Dify checks the key by reading your balance, which costs nothing.

## Usage

Pick an UberLLM model in any LLM node, agent or chat app, like any other model in Dify.

To use a model that is not in the list, click **Add Model** on the UberLLM card and fill in:

| Field | What to enter |
| --- | --- |
| Model name | The exact name from [uberllm.dev/models](https://uberllm.dev/models), for example `qwen/qwen3-coder` |
| API key | Your `ull_` key |
| Context size (tokens) | The context length shown on the model's page |
| Longest reply (tokens) | The most the model may write in one reply |
| Can it read pictures? | Yes if the model's page lists image input |
| Can it use tools? | Yes if the model's page says it supports tools |

Dify checks that the name exists on UberLLM before saving. This check is free.

## Costs

Each call is billed what the provider charged, with no UberLLM fee added. Dify does not show UberLLM prices, because they change with the market. See every call and its exact cost under **Dashboard → Activity** on uberllm.dev, and current prices at [uberllm.dev/pricing](https://uberllm.dev/pricing).

## Connection requirements

- Your Dify server must be able to reach `https://api.uberllm.dev` over HTTPS (port 443). This is the only address the plugin connects to.
- Needs Dify 1.0.0 or later, on Dify Cloud or self-hosted.

## When something goes wrong

| If Dify says | What to do |
| --- | --- |
| UberLLM did not accept this API key | Create a new key at [Dashboard → API keys](https://uberllm.dev/dashboard/keys) and paste it again. |
| Your UberLLM balance is too low | Add credit at [Dashboard → Credits](https://uberllm.dev/dashboard/credits). |
| This UberLLM key reached its spend limit | Raise the key's limit on the API keys page, or use another key. |
| UberLLM has no model called ... | Copy the exact name from [uberllm.dev/models](https://uberllm.dev/models). |
| The model can't be served right now | Try again shortly, or pick another model. Nothing is charged. |

UberLLM retries failed calls for you before an error is shown. More detail: [uberllm.dev/docs/errors](https://uberllm.dev/docs/errors).

## Privacy

UberLLM does not store your prompts or the models' answers. See [PRIVACY.md](PRIVACY.md) and [uberllm.dev/privacy](https://uberllm.dev/privacy).

## Support

- Email: support@uberllm.dev
- Issues and source: https://github.com/PSA-Team-source/dify-plugin-uberllm
- Docs: [uberllm.dev/docs](https://uberllm.dev/docs)
