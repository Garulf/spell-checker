import subprocess
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1] / "src" / "plugin"

SCRIPT = """
import sys

class NoCompiledRegex:
    def find_spec(self, name, path=None, target=None):
        if name == "regex" or name.startswith("regex."):
            raise ImportError("No module named 'regex._regex'")

sys.meta_path.insert(0, NoCompiledRegex())
sys.path.insert(0, sys.argv[1])

import spelling

print(spelling.suggestions("speling")[0][0])
print(spelling.correct("I havv goood speling"))
"""


def test_spell_checker_works_without_the_compiled_regex_module():
    completed = subprocess.run(
        [sys.executable, "-c", SCRIPT, str(PLUGIN_DIR)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.splitlines() == ["spelling", "I have good spelling"]
