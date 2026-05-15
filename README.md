# hermes-model-presets

Quick model switching for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — adds `/codex`, `/flash`, `/pro`, and `/kimi` slash commands with an optional `--global` flag to persist your model choice across sessions.

## Commands

| Command | Model | Provider |
|---------|-------|----------|
| `/codex` | `gpt-5.5` | `openai-codex` (OpenAI Codex) |
| `/flash` | `deepseek-v4-flash` | `opencode-go` |
| `/pro` | `deepseek-v4-pro` | `opencode-go` |
| `/kimi` | `kimi-k2.6` | `opencode-go` |

Add `--global` to any command to persist the model as your new default:

```
/codex --global     → sets GPT-5.5 as the permanent default
/flash              → switches to DeepSeek V4 Flash for this session only
/pro --global       → makes DeepSeek V4 Pro your default model
```

## Installation

```bash
# Clone the repo into your Hermes plugins directory
git clone https://github.com/YOUR_USER/hermes-model-presets.git ~/.hermes/plugins/model-presets

# Enable the plugin
hermes plugins enable model-presets

# Restart the gateway (if using messaging platforms)
hermes gateway restart
```

Or copy manually:

```bash
cp -r hermes-model-presets ~/.hermes/plugins/model-presets
hermes plugins enable model-presets
```

## How It Works

- **CLI mode:** the command handler calls Hermes' internal `_handle_model_switch` to apply the model change immediately
- **Gateway mode (Discord / Telegram / etc.):** a `pre_gateway_dispatch` hook rewrites the preset command to the equivalent `/model` call, which goes through the gateway's normal model-switch pipeline with session override and `--global` persistence

## Requirements

- Hermes Agent (any recent version with plugin support)
- Valid API keys for the providers you want to use (configured in `~/.hermes/.env`)

## License

MIT
