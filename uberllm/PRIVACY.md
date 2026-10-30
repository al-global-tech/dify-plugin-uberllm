# Privacy Policy: UberLLM plugin for Dify

Last updated: October 30, 2026

This policy covers the UberLLM model provider plugin for Dify. The UberLLM service itself is covered by the [UberLLM Privacy Policy](https://uberllm.dev/privacy).

## What the plugin collects

The plugin does not collect, store or log any user data of its own. It has no database, writes no files and keeps nothing between requests.

## What the plugin sends, and to whom

The plugin talks to one service only: UberLLM at `https://api.uberllm.dev`.

- **Your UberLLM API key.** Dify stores it, encrypted, in your Dify workspace, like every other model provider key. The plugin sends it to UberLLM with each request to prove who you are. The key is never written to logs or shown in error messages.
- **Your prompts and files.** When an app runs a model, the messages, pictures and tool definitions in that request are sent to UberLLM so it can answer. Dify may also send an anonymous end-user id with the request.
- **Checks when you save settings.** Saving your key reads your UberLLM balance. Adding a custom model looks up that model's name. Neither sends any prompt.

## What UberLLM does with it

Per the [UberLLM Privacy Policy](https://uberllm.dev/privacy):

- UberLLM does not store your prompts or the models' answers, does not sell your data and does not use it to train models.
- For billing, it keeps which model you called, how many tokens it used, what it cost, how long it took and when.
- To answer a request, UberLLM sends it to a third-party model provider (such as OpenAI, Anthropic, Google or DeepSeek, directly or through a marketplace of providers). That provider receives what you sent and handles it under its own terms and privacy policy.

## Your choices

- Remove the key from **Settings → Model Provider** in Dify, or uninstall the plugin, at any time.
- Delete a key on [uberllm.dev/dashboard/keys](https://uberllm.dev/dashboard/keys) to stop it working at once.
- To get a copy of your UberLLM data or delete your account, email support@uberllm.dev from the address on your account.

## Contact

Questions about this policy: support@uberllm.dev
