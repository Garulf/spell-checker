import asyncio
from functools import partial
from pathlib import Path
from typing import List

from pyflowlauncher import Plugin, Result, api

import clipboard
import spelling
from launcher import KEEP_OPEN, SpellLauncher

NAME = "Spell Checker"
ICON = str(Path(__file__).resolve().parent.parent / "icon.png")

plugin = Plugin(launcher=SpellLauncher())


async def run_blocking(func, *args):
    """Run spell checking off the event loop so Flow Launcher can cancel stale queries."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args))


def full_query(text: str) -> str:
    keyword = plugin.launcher.action_keyword
    return f"{keyword} {text}" if keyword else text


def clipboard_word():
    text = clipboard.read_text()
    if text is None:
        return None
    words = text.split()
    return words[0] if len(words) == 1 else None


def prompt_results() -> List[Result]:
    word = clipboard_word()
    if word is not None:
        return [
            Result(title=word, subtitle="Insert from clipboard", icon=ICON).add_action(
                insert_query, [full_query(word)]
            )
        ]
    return [Result(title="Enter any word to show word suggestions.", icon=ICON)]


def sentence_results(text: str) -> List[Result]:
    return [Result(title=spelling.correct(text), subtitle="Copy to clipboard", icon=ICON)]


def word_results(word: str) -> List[Result]:
    return [
        Result(
            title=suggestion,
            subtitle=spelling.define(suggestion),
            score=int(confidence * 100),
            icon=ICON,
        ).add_action(copy_to_clipboard, [suggestion])
        for suggestion, confidence in spelling.suggestions(word)
    ]


@plugin.on_method
async def query(query: str):
    if len(query) <= 1:
        return prompt_results()
    if " " in query:
        return await run_blocking(sentence_results, query)
    return await run_blocking(word_results, query)


@plugin.on_method
async def insert_query(text: str):
    await plugin.launcher.api.invoke(api.change_query(text))
    return KEEP_OPEN


@plugin.on_method
async def copy_to_clipboard(text: str):
    await plugin.launcher.api.invoke(api.copy_to_clipboard(text, show_default_notification=False))
    await plugin.launcher.api.invoke(api.show_msg(NAME, f"{text} copied to clipboard", ICON))
