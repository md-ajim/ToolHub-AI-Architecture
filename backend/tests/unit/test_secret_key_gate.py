"""P0 regression: insecure default SECRET_KEY must fail closed in prod mode."""
import os
import subprocess
import sys

import pytest


def _import_base(extra_env):
    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    env.update(extra_env)
    # Ensure the dev .env cannot inject a real key for this check.
    env["SECRET_KEY"] = "django-insecure-default-key-for-dev-only"
    return subprocess.run(
        [sys.executable, "-c", "import config.settings.base"],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


class TestSecretKeyFailClosed:
    def test_default_key_rejected_when_debug_false(self):
        proc = _import_base({"DEBUG": "False"})
        assert proc.returncode != 0
        assert "SECRET_KEY" in (proc.stderr or "")

    def test_default_key_allowed_in_debug(self):
        proc = _import_base({"DEBUG": "True"})
        assert proc.returncode == 0, proc.stderr[-2000:]
