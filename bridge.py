#!/usr/bin/env python3
"""Small, explicit polling bridge for an owner-controlled test server."""

import os
import shutil
import subprocess
import time
from pathlib import Path

REPO = Path(os.environ.get("BRIDGE_REPO_DIR", ".")).resolve()
INTERVAL = int(os.environ.get("BRIDGE_INTERVAL_SECONDS", "15"))
TIMEOUT = int(os.environ.get("BRIDGE_COMMAND_TIMEOUT_SECONDS", "300"))


def git(*args: str) -> None:
    subprocess.run(["git", "-C", str(REPO), *args], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)


def run_one(command: Path) -> None:
    ident = command.stem
    outbox = REPO / "outbox"
    processed = REPO / "processed"
    outbox.mkdir(exist_ok=True)
    processed.mkdir(exist_ok=True)
    stdout_path = outbox / f"{ident}.stdout"
    stderr_path = outbox / f"{ident}.stderr"
    status_path = outbox / f"{ident}.status"
    try:
        result = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", str(command)],
            cwd=str(REPO), capture_output=True, text=True, timeout=TIMEOUT,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                 "HOME": os.environ.get("HOME", "/tmp")},
        )
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        status_path.write_text(f"{result.returncode}\n", encoding="utf-8")
    except subprocess.TimeoutExpired as exc:
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text((exc.stderr or "") + "\nbridge: timeout\n", encoding="utf-8")
        status_path.write_text("124\n", encoding="utf-8")
    finally:
        shutil.move(str(command), str(processed / command.name))


def cycle() -> None:
    git("pull", "--ff-only")
    if os.environ.get("BRIDGE_ENABLE_EXECUTION") != "1":
        print("execution disabled; set BRIDGE_ENABLE_EXECUTION=1", flush=True)
        return
    for command in sorted((REPO / "inbox").glob("*.sh")):
        run_one(command)
    if list((REPO / "outbox").iterdir()) or list((REPO / "processed").iterdir()):
        git("add", "inbox", "processed", "outbox")
        if subprocess.run(["git", "-C", str(REPO), "diff", "--cached", "--quiet"]).returncode:
            git("commit", "-m", "bridge: record command result")
            git("push")


if __name__ == "__main__":
    (REPO / "inbox").mkdir(exist_ok=True)
    while True:
        try:
            cycle()
        except Exception as exc:
            print(f"bridge cycle failed: {exc}", flush=True)
        time.sleep(INTERVAL)

