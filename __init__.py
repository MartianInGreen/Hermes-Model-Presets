"""model-presets plugin — quick model switching slash commands.

Provides /luna, /terra, /sol, /luna-pro, /sol-pro, /flash, /glm, /pro, /kimi,
/minimax, /mimo, /mimop with optional --global flag.

/luna      [--global]  → OpenAI GPT-5.6 Luna   via Codex (reasoning: medium)
/terra     [--global]  → OpenAI GPT-5.6 Terra  via Codex (reasoning: medium)
/sol       [--global]  → OpenAI GPT-5.6 Sol    via Codex (reasoning: medium)
/luna-pro  [--global]  → OpenAI GPT-5.6 Luna Pro via Codex (reasoning: high)
/sol-pro   [--global]  → OpenAI GPT-5.6 Sol Pro  via Codex (reasoning: high)
/flash     [--global]  → DeepSeek V4 Flash via OpenCode Go
/glm       [--global]  → GLM 5.2 via OpenCode Go
/pro       [--global]  → DeepSeek V4 Pro via OpenCode Go
/kimi      [--global]  → Kimi K2.7 Code via OpenCode Go
/minimax   [--global]  → MiniMax M3 via OpenCode Go
/mimo      [--global]  → MiMo-V2.5 via OpenCode Go
/mimop     [--global]  → MiMo-V2.5-Pro via OpenCode Go

In the CLI, the switch is applied to the running session immediately.
In the gateway (Discord/Telegram/etc.), the command is rewritten to the
equivalent /model call and dispatched normally so the session override
and config persistence both work correctly.  Presets that specify a
reasoning level also apply that level to the session (and to config when
--global is used).
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ── preset definitions ──────────────────────────────────────────────────
# (command_name, model_id, provider_slug, label, reasoning_level)
PRESETS: Dict[str, Dict[str, str]] = {
    "luna": {
        "model": "gpt-5.6-luna",
        "provider": "openai-codex",
        "label": "OpenAI GPT-5.6 Luna",
        "reasoning": "medium",
    },
    "terra": {
        "model": "gpt-5.6-terra",
        "provider": "openai-codex",
        "label": "OpenAI GPT-5.6 Terra",
        "reasoning": "medium",
    },
    "sol": {
        "model": "gpt-5.6-sol",
        "provider": "openai-codex",
        "label": "OpenAI GPT-5.6 Sol",
        "reasoning": "medium",
    },
    "luna-pro": {
        "model": "gpt-5.6-luna-pro",
        "provider": "openai-codex",
        "label": "OpenAI GPT-5.6 Luna Pro",
        "reasoning": "high",
    },
    "sol-pro": {
        "model": "gpt-5.6-sol-pro",
        "provider": "openai-codex",
        "label": "OpenAI GPT-5.6 Sol Pro",
        "reasoning": "high",
    },
    "flash": {
        "model": "deepseek-v4-flash",
        "provider": "opencode-go",
        "label": "DeepSeek V4 Flash (OpenCode Go)",
        "reasoning": "",
    },
    "glm": {
        "model": "glm-5.2",
        "provider": "opencode-go",
        "label": "GLM 5.2 (OpenCode Go)",
        "reasoning": "",
    },
    "pro": {
        "model": "deepseek-v4-pro",
        "provider": "opencode-go",
        "label": "DeepSeek V4 Pro (OpenCode Go)",
        "reasoning": "",
    },
    "kimi": {
        "model": "kimi-k2.7-code",
        "provider": "opencode-go",
        "label": "Kimi K2.7 Code (OpenCode Go)",
        "reasoning": "",
    },
    "minimax": {
        "model": "minimax/minimax-m3",
        "provider": "opencode-go",
        "label": "MiniMax M3 (OpenCode Go)",
        "reasoning": "",
    },
    "mimo": {
        "model": "mimo-v2.5",
        "provider": "opencode-go",
        "label": "MiMo-V2.5 (OpenCode Go)",
        "reasoning": "",
    },
    "mimop": {
        "model": "mimo-v2.5-pro",
        "provider": "opencode-go",
        "label": "MiMo-V2.5-Pro (OpenCode Go)",
        "reasoning": "",
    },
}

# Valid reasoning levels for OpenAI-style providers.
_REASONING_LEVELS = {"none", "minimal", "low", "medium", "high", "xhigh"}

# Regex to match a preset command at the start of a message
_PRESET_CMD_RE = re.compile(
    r"^/(luna|terra|sol|luna-pro|sol-pro|flash|glm|pro|kimi|minimax|mimo|mimop)\b",
    re.IGNORECASE,
)


def _reasoning_config(level: str) -> Optional[dict]:
    """Convert a preset reasoning level into a reasoning_config dict.

    Returns None when no reasoning level is configured.  Mirrors the host
    CLI's _parse_reasoning_config() mapping so the preset and /reasoning
    commands produce the same runtime config.
    """
    level = (level or "").strip().lower()
    if not level:
        return None
    if level == "none":
        return {"enabled": False}
    if level in _REASONING_LEVELS:
        return {"enabled": True, "effort": level}
    logger.warning("model-presets: unknown reasoning level '%s', ignoring", level)
    return None


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


def _apply_reasoning_to_cli(cli: Any, reasoning_cfg: Optional[dict], is_global: bool, level: str) -> None:
    """Apply a reasoning config to the running CLI session and optionally persist it."""
    if reasoning_cfg is None:
        return

    # Update the CLI's own copy used when building the next agent.
    cli.reasoning_config = reasoning_cfg

    # Update the live agent, if any, so the change takes effect immediately.
    agent = getattr(cli, "agent", None)
    if agent is not None:
        try:
            agent.reasoning_config = reasoning_cfg
        except Exception as exc:
            logger.debug("model-presets: could not update agent.reasoning_config: %s", exc)

    if is_global and level:
        try:
            from hermes_cli.config import save_config_value
            save_config_value("agent.reasoning_effort", level)
        except Exception as exc:
            logger.warning("model-presets: failed to persist reasoning level: %s", exc)


def _apply_reasoning_to_gateway(
    gateway: Any,
    event: Any,
    reasoning_cfg: Optional[dict],
    is_global: bool,
    level: str,
) -> None:
    """Best-effort session reasoning override in gateway mode.

    The pre_gateway_dispatch hook runs before auth, so the session key may
    still be stabilizing.  We set the override using the best key we can
    compute; if it doesn't match the eventual session key the user can fall
    back to /reasoning <level>.
    """
    if reasoning_cfg is None:
        return

    try:
        source = getattr(event, "source", None)
        if source is None or gateway is None:
            return

        # Use the gateway's own helpers when available.
        normalize_fn = getattr(gateway, "_normalize_source_for_session_key", None)
        key_fn = getattr(gateway, "_session_key_for_source", None)
        set_override_fn = getattr(gateway, "_set_session_reasoning_override", None)

        if key_fn is None or set_override_fn is None:
            return

        normalized_source = source
        if normalize_fn is not None:
            try:
                normalized_source = normalize_fn(source)
            except Exception:
                pass

        session_key = key_fn(normalized_source)
        if is_global:
            # Persist to config and clear the session override so the next
            # agent picks up the saved default.
            try:
                from hermes_cli.config import save_config_value
                save_config_value("agent.reasoning_effort", level)
            except Exception as exc:
                logger.warning("model-presets: failed to persist reasoning level: %s", exc)
            set_override_fn(session_key, None)
        else:
            set_override_fn(session_key, reasoning_cfg)
    except Exception as exc:
        logger.debug("model-presets: gateway reasoning override failed: %s", exc)


# ── pre_gateway_dispatch hook ───────────────────────────────────────────

def _on_pre_gateway_dispatch(
    event: Any = None,
    gateway: Any = None,
    session_store: Any = None,
    **kwargs: Any,
) -> Optional[Dict[str, str]]:
    """Rewrite preset commands to /model before normal dispatch.

    Fires on every user-originated gateway message. Only acts when the
    message text starts with a known preset command (/luna, /flash, etc.).
    Presets that define a reasoning level also set the session reasoning
    override (and persist it with --global).
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

    preset = PRESETS[cmd_name]
    raw_args = text[m.end():].strip()
    _, is_global = _parse_preset_args(raw_args)

    reasoning_cfg = _reasoning_config(preset.get("reasoning", ""))
    if reasoning_cfg is not None:
        _apply_reasoning_to_gateway(
            gateway,
            event,
            reasoning_cfg,
            is_global,
            preset.get("reasoning", ""),
        )

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
        reasoning_level = preset.get("reasoning", "")
        reasoning_cfg = _reasoning_config(reasoning_level)

        def handler(raw_args: str) -> Optional[str]:
            _, is_global = _parse_preset_args(raw_args)

            # Try to apply via CLI ref (only available in CLI mode)
            cli = ctx._manager._cli_ref
            if cli is not None:
                cmd = _build_model_command(cmd_name, is_global)
                cli._handle_model_switch(cmd)
                _apply_reasoning_to_cli(cli, reasoning_cfg, is_global, reasoning_level)
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
            if reasoning_cfg is not None:
                lines.append(
                    f"   Reasoning: `{reasoning_level}`"
                )
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
