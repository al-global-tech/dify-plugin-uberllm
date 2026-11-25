# Privacy Policy: MartLLM plugin for Dify

Last updated: October 30, 2026

This policy covers the MartLLM model provider plugin for Dify. The MartLLM service itself is covered by the [MartLLM Privacy Policy](https://martllm.com/privacy).

## What the plugin collects

The plugin does not collect, store or log any user data of its own. It has no database, writes no files and keeps nothing between requests.

## What the plugin sends, and to whom

The plugin talks to one service only: MartLLM at `https://api.martllm.com`.

- **Your MartLLM API key.** Dify stores it, encrypted, in your Dify workspace, like every other model provider key. The plugin sends it to MartLLM with each request to prove who you are. The key is never written to logs or shown in error messages.
- **Your prompts and files.** When an app runs a model, the messages, pictures and tool definitions in that request are sent to MartLLM so it can answer. Dify may also send an anonymous end-user id with the request.
- **Checks when you save settings.** Saving your key reads your MartLLM balance. Adding a custom model looks up that model's name. Neither sends any prompt.

## What MartLLM does with it

Per the [MartLLM Privacy Policy](https://martllm.com/privacy):

- MartLLM does not store your prompts or the models' answers, does not sell your data and does not use it to train models.
- For billing, it keeps which model you called, how many tokens it used, what it cost, how long it took and when.
- To answer a request, MartLLM sends it to a third-party model provider (such as OpenAI, Anthropic, Google or DeepSeek, directly or through a marketplace of providers). That provider receives what you sent and handles it under its own terms and privacy policy.

## Your choices

- Remove the key from **Settings → Model Provider** in Dify, or uninstall the plugin, at any time.
- Delete a key on [martllm.com/dashboard/keys](https://martllm.com/dashboard/keys) to stop it working at once.
- To get a copy of your MartLLM data or delete your account, email contact@martllm.com from the address on your account.

## Contact

Questions about this policy: contact@martllm.com
