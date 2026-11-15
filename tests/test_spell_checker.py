import asyncio

import pytest

from launcher import KEEP_OPEN
from spell_checker import ICON, copy_to_clipboard, insert_query, query


def run(coroutine):
    return asyncio.run(coroutine)


def as_json(results):
    return [result.to_json() for result in results]


@pytest.mark.parametrize("text", ["", "a"])
def test_short_query_asks_for_a_word(text, clipboard_text):
    (result,) = as_json(run(query(text)))
    assert result["Title"] == "Enter any word to show word suggestions."
    assert result["JsonRPCAction"] is None


@pytest.mark.parametrize("text", ["two words", "   ", "one\ntwo"])
def test_clipboard_without_a_single_word_is_ignored(text, clipboard_text):
    clipboard_text["text"] = text
    (result,) = as_json(run(query("")))
    assert result["Title"] == "Enter any word to show word suggestions."


def test_single_word_on_clipboard_is_offered(clipboard_text, keyword):
    clipboard_text["text"] = "  recieve\r\n"
    (result,) = as_json(run(query("")))
    assert result["Title"] == "recieve"
    assert result["SubTitle"] == "Insert from clipboard"
    assert result["JsonRPCAction"]["Method"] == "insert_query"
    assert result["JsonRPCAction"]["Parameters"] == ["spell recieve"]


def test_insert_query_changes_query_and_keeps_window_open(invoked):
    assert run(insert_query("spell recieve")) == KEEP_OPEN
    assert invoked == [{"Method": "Flow.Launcher.ChangeQuery", "Parameters": ["spell recieve", False]}]


def test_word_suggestions_carry_definition_score_and_copy_action(clipboard_text):
    results = as_json(run(query("speling")))
    assert [r["Title"] for r in results] == ["spelling"]
    (result,) = results
    assert result["Score"] == 100
    assert result["SubTitle"].startswith("The act of one who spells")
    assert result["IcoPath"] == ICON
    assert result["JsonRPCAction"]["Method"] == "copy_to_clipboard"
    assert result["JsonRPCAction"]["Parameters"] == ["spelling"]


def test_ambiguous_word_lists_every_suggestion_by_confidence():
    results = as_json(run(query("teh")))
    titles = [r["Title"] for r in results]
    assert len(titles) > 1
    assert titles[0] == "the"
    scores = [r["Score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_unknown_word_has_empty_definition():
    results = as_json(run(query("zzzzqx")))
    assert results
    assert all(isinstance(r["SubTitle"], str) for r in results)


def test_sentence_is_corrected():
    (result,) = as_json(run(query("I havv goood speling")))
    assert result["Title"] == "I have good spelling"
    assert result["SubTitle"] == "Copy to clipboard"
    assert result["JsonRPCAction"]["Method"] == "copy_to_clipboard"
    assert result["JsonRPCAction"]["Parameters"] == ["I have good spelling"]


def test_copy_to_clipboard_copies_and_notifies(invoked):
    run(copy_to_clipboard("spelling"))
    assert invoked == [
        {"Method": "Flow.Launcher.CopyToClipboard", "Parameters": ["spelling", False, False]},
        {"Method": "Flow.Launcher.ShowMsg", "Parameters": ["Spell Checker", "spelling copied to clipboard", ICON]},
    ]
