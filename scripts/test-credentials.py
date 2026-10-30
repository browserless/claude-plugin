#!/usr/bin/env python3
"""Run documented credential snippets offline. Requires Python 3, bash and zsh."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOKEN = "BROWSERLESS_TOKEN"
URL = "BROWSERLESS_API_URL"
SAVED = {TOKEN: "saved-token", URL: "https://saved.example"}
EXPORTED = {TOKEN: "exported $token ' with spaces", URL: "https://exported.example"}
CASES = [
    ("exports win", EXPORTED, SAVED, tuple(EXPORTED.values())),
    ("saved fallback", {}, SAVED, tuple(SAVED.values())),
    ("token only", {TOKEN: EXPORTED[TOKEN]}, SAVED, (EXPORTED[TOKEN], SAVED[URL])),
    ("URL only", {URL: EXPORTED[URL]}, SAVED, (SAVED[TOKEN], EXPORTED[URL])),
    ("empty exports", {TOKEN: "", URL: ""}, SAVED, tuple(SAVED.values())),
    ("no file", EXPORTED, None, tuple(EXPORTED.values())),
    ("no credentials", {}, None, ("", "https://production-sfo.browserless.io")),
    ("empty file", {}, {}, ("", "https://production-sfo.browserless.io")),
    ("saved token only", {}, {TOKEN: SAVED[TOKEN]}, (SAVED[TOKEN], "https://production-sfo.browserless.io")),
    ("saved URL only", {}, {URL: SAVED[URL]}, ("", SAVED[URL])),
]


def blocks(path):
    return re.findall(r"```bash\n(.*?)```", path.read_text(), re.S)


def rest_blocks():
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        if path.parent.name in ("auth", "agent"):
            continue
        for index, block in enumerate(blocks(path)):
            if "source ~/.browserless/.env" not in block:
                continue
            if "curl " not in block:
                # Observe the standalone authentication example inside its scope.
                if block.startswith("(\n"):
                    block = block.rstrip().removesuffix(")") + "curl\n)\n"
                else:
                    block += "curl\n"
            yield path.parent.name, index, block


OBSERVE = 'curl() { printf "%s\\n%s\\n" "${BROWSERLESS_TOKEN:-}" "${BROWSERLESS_API_URL:-https://production-sfo.browserless.io}"; }\n'


def run(shell, code, exported, saved):
    with tempfile.TemporaryDirectory(prefix="browserless test ") as home:
        if saved is not None:
            config = Path(home) / ".browserless" / ".env"
            config.parent.mkdir()
            config.write_text("".join(f"{key}={shlex.quote(value)}\n" for key, value in saved.items()))
        env = {"HOME": home, "PATH": os.environ["PATH"], **exported}
        return subprocess.run([shell, "-f", "-c", code], env=env, capture_output=True, text=True, check=True).stdout


class CredentialsTest(unittest.TestCase):
    def test_rest_snippets(self):
        # Execute the actual examples, replacing only the network boundary.
        # Re-sourcing without restoring either variable must fail this test.
        count = 0
        for skill, index, block in rest_blocks():
            count += 1
            code = OBSERVE + block * 2
            calls = len(re.findall(r"^curl(?: |$)", block, re.M))
            for shell in ("bash", "zsh"):
                for name, exported, saved, expected in CASES:
                    with self.subTest(skill=skill, block=index, shell=shell, case=name):
                        self.assertEqual(run(shell, code, exported, saved), ("\n".join(expected) + "\n") * calls * 2)
        self.assertGreater(count, 0)

    def test_saved_credentials_refresh_between_calls(self):
        change = "printf '%s\\n' 'BROWSERLESS_TOKEN=new-token' 'BROWSERLESS_API_URL=https://new.example' > ~/.browserless/.env\n"
        for skill, index, block in rest_blocks():
            calls = len(re.findall(r"^curl(?: |$)", block, re.M))
            for shell in ("bash", "zsh"):
                for exported, first, second in (
                    ({}, "saved-token\nhttps://saved.example\n", "new-token\nhttps://new.example\n"),
                    ({TOKEN: "override"}, "override\nhttps://saved.example\n", "override\nhttps://new.example\n"),
                    ({URL: "https://override.example"}, "saved-token\nhttps://override.example\n", "new-token\nhttps://override.example\n"),
                ):
                    with self.subTest(skill=skill, block=index, shell=shell, exported=exported):
                        self.assertEqual(run(shell, OBSERVE + block + change + block, exported, SAVED), first * calls + second * calls)

    def test_auth_validates_saved_credentials(self):
        validation = next(block for block in blocks(ROOT / "skills/auth/SKILL.md") if "curl " in block)
        code = 'curl() { printf "%s\\n" "$@"; }\n' + validation
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell):
                self.assertIn("https://saved.example/map?token=saved-token", run(shell, code, EXPORTED, SAVED))

    def test_auth_status_preserves_exported_url(self):
        status = next(block for block in blocks(ROOT / "skills/auth/SKILL.md") if "Not configured" in block)
        for shell in ("bash", "zsh"):
            with self.subTest(shell=shell):
                self.assertIn("API URL: https://exported.example", run(shell, status, {URL: EXPORTED[URL]}, SAVED))


if __name__ == "__main__":
    unittest.main()
