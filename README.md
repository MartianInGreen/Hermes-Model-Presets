# Hermes Model Presets

Quick model switching plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent) — adds `/luna`, `/terra`, `/sol`, `/luna-pro`, `/sol-pro`, `/flash`, `/pro`, `/kimi`, and other slash commands with an optional `--global` flag to persist your model choice across sessions.

## Commands

| Command | Model | Provider | Reasoning |
|---------|-------|----------|-----------|
| `/luna` | `gpt-5.6-luna` | `openai-codex` | medium |
| `/terra` | `gpt-5.6-terra` | `openai-codex` | medium |
| `/sol` | `gpt-5.6-sol` | `openai-codex` | medium |
| `/luna-pro` | `gpt-5.6-luna-pro` | `openai-codex` | high |
| `/sol-pro` | `gpt-5.6-sol-pro` | `openai-codex` | high |
| `/flash` | `deepseek-v4-flash` | `opencode-go` | — |
| `/glm` | `glm-5.2` | `opencode-go` | — |
| `/pro` | `deepseek-v4-pro` | `opencode-go` | — |
| `/kimi` | `kimi-k2.7-code` | `opencode-go` | — |
| `/minimax` | `minimax/minimax-m3` | `opencode-go` | — |
| `/mimo` | `mimo-v2.5` | `opencode-go` | — |
| `/mimop` | `mimo-v2.5-pro` | `opencode-go` | — |

Add `--global` to any command to persist the model (and its reasoning level, for GPT 5.6 presets) as your new default:

```
/luna --global      → sets GPT-5.6 Luna as the permanent default with medium reasoning
/luna-pro --global  → sets GPT-5.6 Luna Pro as the permanent default with high reasoning
/flash              → switches to DeepSeek V4 Flash for this session only
/pro --global       → makes DeepSeek V4 Pro your default model
```

## Installation

```bash
# Clone the repo into your Hermes plugins directory
git clone https://github.com/MartianInGreen/Hermes-Model-Presets.git ~/.hermes/plugins/model-presets

# Enable the plugin
hermes plugins enable model-presets

# Restart the gateway (if using Discord / Telegram / etc.)
hermes gateway restart
```

## How It Works

- **CLI mode:** the command handler calls Hermes' internal `_handle_model_switch` to apply the model change immediately, then updates the session reasoning config. With `--global`, the reasoning level is also saved to `agent.reasoning_effort` in `config.yaml`.
- **Gateway mode (Discord / Telegram / etc.):** a `pre_gateway_dispatch` hook rewrites the preset command to the equivalent `/model` call, which goes through the gateway's normal model-switch pipeline with session override and `--global` persistence. The hook also sets the session reasoning override for GPT 5.6 presets.

## Requirements

- Hermes Agent (any recent version with plugin support)
- Valid API keys for the providers you want to use (configured in `~/.hermes/.env`)

## License

MIT — see [LICENSE](LICENSE)
