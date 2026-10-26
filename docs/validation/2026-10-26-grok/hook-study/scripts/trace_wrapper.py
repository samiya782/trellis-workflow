#!/usr/bin/env python3
# hook-study TRACE WRAPPER: runs the original hook (<name>.orig.py) with the same
# stdin/argv/env, logs the call to /tmp/trellis-hook-trace-<fixture>.log, and
# re-emits the original stdout/stderr/exit code unchanged.
import datetime, json, os, pathlib, subprocess, sys, time

here = pathlib.Path(__file__).resolve()
orig = here.with_name(here.stem + ".orig.py")
vendor = here.parent.parent.name            # .claude / .codex
project = here.parent.parent.parent
fixture = project.name
log = pathlib.Path(f"/tmp/trellis-hook-trace-{fixture}.log")
outdir = pathlib.Path(f"/tmp/trellis-hook-trace-{fixture}.d")

raw = b"" if sys.stdin.isatty() else sys.stdin.buffer.read()
t0 = time.time()
p = subprocess.run([sys.executable, "-X", "utf8", str(orig), *sys.argv[1:]],
                   input=raw, capture_output=True)
dt = round(time.time() - t0, 3)
try:
    payload = json.loads(raw.decode("utf-8", "replace") or "{}")
except Exception:
    payload = {"_unparsed": raw[:300].decode("utf-8", "replace")}
if not isinstance(payload, dict):
    payload = {"_nondict": str(payload)[:300]}
out = p.stdout.decode("utf-8", "replace")
err = p.stderr.decode("utf-8", "replace")
ti = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
rec = {
    "ts_local": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "ts_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "fixture": fixture, "vendor": vendor, "hook": here.name,
    "event": payload.get("hook_event_name"), "tool_name": payload.get("tool_name"),
    "source": payload.get("source"), "payload_keys": sorted(payload.keys()),
    "tool_input_keys": sorted(ti.keys()),
    "subagent_type": ti.get("subagent_type") or ti.get("agent") or ti.get("agent_name") or ti.get("name"),
    "prompt_head": str(payload.get("prompt", ""))[:120],
    "session_id": payload.get("session_id"),
    "env": {k: (os.environ[k] if k in ("GROK_SESSION_ID", "TRELLIS_CONTEXT_ID") else "set")
            for k in sorted(os.environ) if k.startswith(("GROK", "CLAUDE", "CODEX", "TRELLIS"))},
    "cwd": os.getcwd(), "argv": sys.argv[1:], "exit": p.returncode, "secs": dt,
    "stdout_len": len(out), "stdout_head": out[:300], "stderr_head": err[:200],
}
try:
    outdir.mkdir(parents=True, exist_ok=True)
    n = len(list(outdir.iterdir()))
    stem = f"{n:04d}-{here.stem}-{rec['event'] or 'noevent'}"
    (outdir / f"{stem}.stdout.txt").write_text(out)
    (outdir / f"{stem}.stdin.json").write_bytes(raw)
    rec["full"] = stem
    with log.open("a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
except Exception as e:  # never break the hook
    sys.stderr.write(f"[trace-wrapper error {e}]\n")
sys.stdout.write(out); sys.stdout.flush()
sys.stderr.write(err)
sys.exit(p.returncode)
