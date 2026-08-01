# Sandbox command bridge

This private repository is a simple, pull-based command bridge for an
owner-controlled test server. The server polls this repository, runs queued
shell commands, and commits captured results back to `outbox/`.

## Run on the server

```sh
export BRIDGE_INTERVAL_SECONDS=15
./hello.py
```

Run the script from anywhere; it automatically uses the directory containing
the script as the repository root. The command loop is always enabled.

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
