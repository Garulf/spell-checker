import pytest

import clipboard
import spell_checker


@pytest.fixture
def clipboard_text(monkeypatch):
    content = {"text": None}
    monkeypatch.setattr(clipboard, "read_text", lambda: content["text"])
    return content


@pytest.fixture
def keyword():
    launcher = spell_checker.plugin.launcher
    launcher.action_keyword = "spell"
    yield launcher
    launcher.action_keyword = ""


@pytest.fixture
def invoked(monkeypatch):
    commands = []

    async def invoke(command):
        commands.append(command)

    monkeypatch.setattr(spell_checker.plugin.launcher.api, "invoke", invoke)
    return commands
