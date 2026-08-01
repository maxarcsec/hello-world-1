# Sandbox command bridge

This private repository is a simple, pull-based command bridge for an
owner-controlled test server. The server polls this repository, runs queued
shell commands, and commits captured results back to `outbox/`.

## Enable on the server

```sh
export BRIDGE_ENABLE_EXECUTION=1
export BRIDGE_REPO_DIR=/opt/sandbox-command-bridge
export BRIDGE_INTERVAL_SECONDS=15
./bridge.py
```

The process must run as the least-privileged test user. It requires normal
Git credentials with read/write access to this private repository; do not put
tokens in files or command arguments.

## Queue a command

Create `inbox/<id>.sh`, commit, and push it. The bridge runs it once with
`/bin/bash --noprofile --norc`, then moves it to `processed/` and writes:

```text
outbox/<id>.stdout
outbox/<id>.stderr
outbox/<id>.status
```

Commands are capped at 5 minutes. Results may contain sensitive data; keep
this repository private and remove them when finished.

