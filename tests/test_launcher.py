import asyncio

from pyflowlauncher.jsonrpc import JsonRPCV2Client

from launcher import KEEP_OPEN, SpellLauncher


def test_keep_open_reply_is_sent_as_is():
    launcher = SpellLauncher()
    sent = []
    launcher._client.send = sent.append
    launcher._send_response(7, "insert_query", KEEP_OPEN)
    launcher._send_response(8, "copy_to_clipboard", None)
    assert sent == [
        {"id": 7, "result": {"hide": False}, "error": None},
        {"id": 8, "result": {}, "error": None},
    ]


def test_action_keyword_is_tracked_from_query_requests(monkeypatch):
    requests = [
        {"id": 1, "method": "query", "params": [{"search": "speling", "actionKeyword": "sp"}, {}]},
        {"id": 2, "method": "context_menu", "params": [[{}]]},
    ]

    async def messages(self):
        for request in requests:
            yield request

    monkeypatch.setattr(JsonRPCV2Client, "messages", messages)
    launcher = SpellLauncher()

    async def drain():
        return [request async for request in launcher._client.messages()]

    assert asyncio.run(drain()) == requests
    assert launcher.action_keyword == "sp"


def test_clipboard_reads_nothing_off_windows(monkeypatch):
    import clipboard

    monkeypatch.setattr(clipboard.sys, "platform", "linux")
    assert clipboard.read_text() is None
