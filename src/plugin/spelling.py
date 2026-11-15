import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import regex  # noqa: F401
except ImportError:
    # nltk imports the compiled regex package, which has no wheel that works
    # on every Python Flow Launcher may run. TextBlob's spell checker only
    # uses nltk's re based tokenizer, so the standard library stands in.
    sys.modules["regex"] = re

from textblob import TextBlob, Word  # noqa: E402

DICTIONARY = Path(__file__).resolve().parent / "dictionary.json"


def suggestions(word: str) -> List[Tuple[str, float]]:
    """Return (word, confidence) pairs for ``word``, most likely first."""
    return Word(word).spellcheck()


def correct(text: str) -> str:
    return str(TextBlob(text).correct())


@lru_cache(maxsize=1)
def definitions() -> Dict[str, str]:
    with DICTIONARY.open(encoding="utf-8") as file:
        return json.load(file)


def define(word: str) -> str:
    return definitions().get(word.upper(), "")
