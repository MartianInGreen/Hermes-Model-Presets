# Hermes Model Presets

Quick model switching plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent). The Discord picker exposes the following current presets:

| Command | Model | Provider | Reasoning |
|---|---|---|---|
| `/sol` | `gpt-5.6-sol` | `openai-codex` | medium |
| `/luna` | `gpt-5.6-luna` | `openai-codex` | medium |
| `/sol-high` | `gpt-5.6-sol` | `openai-codex` | high |
| `/luna-max` | `gpt-5.6-luna` | `openai-codex` | xhigh / maximum |
| `/luna-go` | `luna` | `opencode-go` | xhigh / maximum |
| `/flash` | `deepseek-v4-flash` | `opencode-go` | provider default |
| `/kimi` | `kimi-k3` | `opencode-go` | provider default |
| `/glm` | `glm-5.2` | `opencode-go` | provider default |

Add `--global` to persist the selected model and reasoning level as the default:

```text
/sol-high --global  → GPT-5.6 Sol with high reasoning
/luna-max           → GPT-5.6 Luna with maximum reasoning for this session
/luna-go            → Luna through OpenCode Go with maximum reasoning
/flash              → latest DeepSeek V4 Flash through OpenCode Go
/kimi               → Kimi K3 through OpenCode Go
/glm                → GLM 5.2 through OpenCode Go
```

## Installation

```bash
git clone https://github.com/MartianInGreen/Hermes-Model-Presets.git ~/.hermes/plugins/model-presets
hermes plugins enable model-presets
hermes gateway restart
```

The plugin works in CLI and gateway mode. In gateway mode, preset commands are rewritten to Hermes' normal `/model` pipeline, while GPT/Codex presets also apply their reasoning override.

## Requirements

- Hermes Agent with plugin support
- Valid provider credentials configured in `~/.hermes/.env`
- `openai-codex` configured for the Codex presets
- `opencode-go` configured for the OpenCode Go presets

## License

MIT — see [LICENSE](LICENSE)
