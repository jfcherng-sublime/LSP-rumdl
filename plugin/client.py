from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any

import sublime
from LSP.plugin import AbstractPlugin, DottedDict

from .constants import PACKAGE_NAME
from .log import log_info, log_warning
from .template import load_string_template
from .utils import decompress_buffer, rmtree_ex, sha256sum, simple_urlopen
from .version_manager import version_manager


class LspRumdlPlugin(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return PACKAGE_NAME

    @classmethod
    def configuration(cls) -> tuple[sublime.Settings, str]:
        basename = f"{cls.name()}.sublime-settings"
        filepath = f"Packages/{cls.name()}/{basename}"
        return sublime.load_settings(basename), filepath

    @classmethod
    def additional_variables(cls) -> dict[str, str] | None:
        return {
            "server_path": str(cls.server_path()),
        }

    @classmethod
    def needs_update_or_installation(cls) -> bool:
        return not cls.server_path().is_file()

    @classmethod
    def install_or_update(cls) -> None:
        rmtree_ex(cls.plugin_storage_dir(), ignore_errors=True)

        log_info(f"Downloading server tarball: {version_manager.server_download_url}")
        data = simple_urlopen(version_manager.server_download_url)

        hash_actual = sha256sum(data)  # already lowercase
        hash_golden = (
            simple_urlopen(version_manager.server_download_hash_url).decode().partition(" ")[0].strip().lower()
        )
        if hash_actual != hash_golden:
            raise ValueError(f"Mismatched downloaded file hash: {hash_actual} != {hash_golden}")

        decompress_buffer(
            io.BytesIO(data),
            filename=version_manager.THIS_TARBALL_NAME,
            dst_dir=cls.versioned_server_dir(),
        )

    @classmethod
    def should_ignore(cls, view: sublime.View) -> bool:
        return bool(
            # SublimeREPL views
            view.settings().get("repl")
            # syntax test files
            or os.path.basename(view.file_name() or "").startswith("syntax_test")
        )

    # ----- #
    # hooks #
    # ----- #

    def on_settings_changed(self, settings: DottedDict) -> None:
        super().on_settings_changed(settings)

        self.update_status_bar_text()

    # -------------- #
    # custom methods #
    # -------------- #

    @classmethod
    def plugin_storage_dir(cls) -> Path:
        """The storage directory for this plugin."""
        return Path(cls.storage_path()) / PACKAGE_NAME

    @classmethod
    def versioned_server_dir(cls) -> Path:
        """The directory specific to the current server version."""
        return cls.plugin_storage_dir() / f"v{version_manager.server_version}"

    @classmethod
    def server_path(cls) -> Path:
        """The path of the language server binary."""
        return cls.versioned_server_dir() / version_manager.THIS_TARBALL_BIN_PATH

    def update_status_bar_text(self, extra_variables: dict[str, Any] | None = None) -> None:
        if not (session := self.weaksession()):
            return

        variables: dict[str, Any] = {
            "server_version": version_manager.server_version,
        }

        if extra_variables:
            variables.update(extra_variables)

        rendered_text = ""
        if template_text := str(session.config.settings.get("statusText") or ""):
            try:
                rendered_text = load_string_template(template_text).render(variables)
            except Exception as e:
                log_warning(f'Invalid "statusText" template: {e}')
        session.set_config_status_async(rendered_text)
