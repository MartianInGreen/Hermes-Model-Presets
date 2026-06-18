"""model-presets plugin — quick model switching slash commands.

Provides /codex, /flash, /glm, /pro, /kimi, /minimax, /mimo, /mimop with optional --global flag.

/codex [--global]  → OpenAI GPT-5.5 via Codex integration
/flash [--global]  → DeepSeek V4 Flash via OpenCode Go
/glm   [--global]  → GLM 5.2 via OpenCode Go
/pro   [--global]  → DeepSeek V4 Pro via OpenCode Go
/kimi  [--global]  → Kimi K2.7 Code via OpenCode Go
/minimax  [--global]  → MiniMax M3 via OpenCode Go
/mimo     [--global]  → MiMo-V2.5 via OpenCode Go
/mimop    [--global]  → MiMo-V2.5-Pro via OpenCode Go

In the CLI, the switch is applied to the running session immediately.
In the gateway (Discord/Telegram/etc.), the command is rewritten to the
equivalent /model call and dispatched normally so the session override
and config persistence both work correctly.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ── preset definitions ──────────────────────────────────────────────────
# (command_name, model_id, provider_slug, label)
PRESETS: Dict[str, Dict[str, str]] = {
    "codex": {
        "model": "gpt-5.5",
        "provider": "openai-codex",
        "label": "OpenAI GPT-5.5 (Codex)",
    },
    "flash": {
        "model": "deepseek-v4-flash",
        "provider": "opencode-go",
        "label": "DeepSeek V4 Flash (OpenCode Go)",
    },
    "glm": {
        "model": "glm-5.2",
        "provider": "opencode-go",
        "label": "GLM 5.2 (OpenCode Go)",
    },
    "pro": {
        "model": "deepseek-v4-pro",
        "provider": "opencode-go",
        "label": "DeepSeek V4 Pro (OpenCode Go)",
    },
    "kimi": {
        "model": "kimi-k2.7-code",
        "provider": "opencode-go",
        "label": "Kimi K2.7 Code (OpenCode Go)",
    },
    "minimax": {
        "model": "minimax/minimax-m3",
        "provider": "opencode-go",
        "label": "MiniMax M3 (OpenCode Go)",
    },
    "mimo": {
        "model": "mimo-v2.5",
        "provider": "opencode-go",
        "label": "MiMo-V2.5 (OpenCode Go)",
    },
    "mimop": {
        "model": "mimo-v2.5-pro",
        "provider": "opencode-go",
        "label": "MiMo-V2.5-Pro (OpenCode Go)",
    },
}

# Regex to match a preset command at the start of a message
_PRESET_CMD_RE = re.compile(
    r"^/(codex|flash|glm|pro|kimi|minimax|mimo|mimop)\b",
    re.IGNORECASE,
)


def _parse_preset_args(raw_args: str) -> tuple:
    """Parse raw args from a preset command, extracting --global.

    Returns (remaining_args, is_global).
    """
    is_global = False
    # Strip and normalize unicode dashes (Telegram/iOS)
    normalized = re.sub(
        r"[\u2012\u2013\u2014\u2015]global", "--global", raw_args
    )
    if "--global" in normalized:
        is_global = True
        normalized = normalized.replace("--global", "")
    remaining = " ".join(normalized.split()).strip()
    return remaining, is_global


def _build_model_command(cmd_name: str, is_global: bool) -> str:
    """Build the equivalent /model command for a preset."""
    preset = PRESETS[cmd_name]
    global_flag = " --global" if is_global else ""
    return (
        f"/model {preset['model']}"
        f" --provider {preset['provider']}"
        f"{global_flag}"
    )


# ── pre_gateway_dispatch hook ───────────────────────────────────────────

def _on_pre_gateway_dispatch(
    event: Any = None,
    gateway: Any = None,
    session_store: Any = None,
    **kwargs: Any,
) -> Optional[Dict[str, str]]:
    """Rewrite preset commands to /model before normal dispatch.

    Fires on every user-originated gateway message. Only acts when the
    message text starts with a known preset command (/codex, /flash, etc.).
    """
    if event is None:
        return None

    text = (getattr(event, "text", "") or "").strip()
    m = _PRESET_CMD_RE.match(text)
    if not m:
        return None

    cmd_name = m.group(1).lower()
    if cmd_name not in PRESETS:
        return None

    # Extract raw args (everything after the command name)
    raw_args = text[m.end():].strip()
    _, is_global = _parse_preset_args(raw_args)

    rewritten = _build_model_command(cmd_name, is_global)
    logger.info(
        "model-presets: rewriting /%s → %s",
        cmd_name, rewritten,
    )
    return {"action": "rewrite", "text": rewritten}


# ── plugin registration ─────────────────────────────────────────────────

def register(ctx):
    """Register slash commands and gateway hook."""

    # Build handlers inside register() so they can close over ctx
    def _make_handler(cmd_name: str):
        preset = PRESETS[cmd_name]

        def handler(raw_args: str) -> Optional[str]:
            _, is_global = _parse_preset_args(raw_args)

            # Try to apply via CLI ref (only available in CLI mode)
            cli = ctx._manager._cli_ref
            if cli is not None:
                cmd = _build_model_command(cmd_name, is_global)
                cli._handle_model_switch(cmd)
                return None  # _handle_model_switch handles all output

            # Gateway / other mode — the pre_gateway_dispatch hook handles
            # rewriting. If we land here (no CLI ref), return a helpful
            # status summary.
            global_note = (
                " (persisted as default)" if is_global else ""
            )
            lines = [
                f"⚡ Switch to **{preset['label']}**{global_note}",
                f"   Model: `{preset['model']}`",
                f"   Provider: `{preset['provider']}`",
            ]
            if is_global:
                lines.append(
                    "   Use `/reset` to start a fresh session with "
                    "the new model."
                )
            else:
                lines.append(
                    "   Add `--global` to persist this as the default model."
                )
            return "\n".join(lines)

        return handler

    # Register slash commands for CLI and gateway command discovery
    for cmd_name, preset in PRESETS.items():
        ctx.register_command(
            name=cmd_name,
            handler=_make_handler(cmd_name),
            description=(
                f"Switch to {preset['label']} "
                f"(provider: {preset['provider']})"
            ),
            args_hint="[--global]",
        )

    # Register the pre_gateway_dispatch hook for transparent gateway support
    ctx.register_hook("pre_gateway_dispatch", _on_pre_gateway_dispatch)

    logger.info(
        "model-presets plugin loaded: %d commands registered",
        len(PRESETS),
    )
