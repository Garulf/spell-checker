import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

from textblob import TextBlob, Word

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
