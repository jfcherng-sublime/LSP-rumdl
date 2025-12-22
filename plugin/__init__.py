from __future__ import annotations

from LSP.plugin import register_plugin, unregister_plugin

from .client import LspRumdlPlugin

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ...
    "LspRumdlPlugin",
)


def plugin_loaded() -> None:
    """Executed when this plugin is loaded."""
    register_plugin(LspRumdlPlugin)


def plugin_unloaded() -> None:
    """Executed when this plugin is unloaded."""
    unregister_plugin(LspRumdlPlugin)
