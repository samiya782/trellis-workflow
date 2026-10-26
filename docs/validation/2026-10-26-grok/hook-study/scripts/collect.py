#!/usr/bin/env python3
"""Copy hook-study evidence into the audit dir with secrets redacted."""
import json, glob, os, re, shutil, sys
DST = os.path.expanduser("~/trellis/docs/validation/2026-10-26-grok/hook-study")
SRC = "/tmp/grokval/hs"
RUNS = sys.argv[1:]
PAT = [(re.compile(r"ctx7sk-[A-Za-z0-9_\-]+"), "ctx7sk-[REDACTED]"),
       (re.compile(r"xai-[A-Za-z0-9]{16,}"), "xai-[REDACTED]"),
       (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), "sk-[REDACTED]"),
       (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "gh_[REDACTED]"),
       (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{16,}"), r"\1[REDACTED]"),
       (re.compile(r"(?i)((?:api[_-]?key|token|secret|password)\"?\s*[:=]\s*\"?)[A-Za-z0-9._\-]{12,}"), r"\1[REDACTED]")]
hits = {}
def red(s, name):
    for p, r in PAT:
        s, n = p.subn(r, s)
        if n: hits[name] = hits.get(name, 0) + n
    return s
def put(rel, text):
    p = os.path.join(DST, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(red(text, rel))
def cp(src, rel):
    if os.path.exists(src): put(rel, open(src, errors="replace").read())
def trunc(o, n=2000):
    if isinstance(o, str): return o if len(o) <= n else o[:n] + f"...[truncated {len(o)-n} chars]"
    if isinstance(o, list): return [trunc(x, n) for x in o]
    if isinstance(o, dict): return {k: trunc(v, n) for k, v in o.items()}
    return o
for r in RUNS:
    d = f"{SRC}/runs/{r}"
    for f in ["analysis.json", "inspect.json", "interactions.log", "tmux-final-screen.txt", "tmux-scrollback.txt", "session-id.txt"]:
        cp(f"{d}/{f}", f"runs/{r}/{f}")
    sid = open(f"{d}/session-id.txt").read().strip()
    g = glob.glob(os.path.expanduser(f"~/.grok/sessions/*/{sid}/chat_history.jsonl"))
    if g:
        out = []
        for l in open(g[0]):
            x = json.loads(l)
            if x.get("type") == "system":
                x = {"type": "system", "content": f"[system prompt omitted, {len(l)} bytes]"}
            out.append(json.dumps(trunc(x), ensure_ascii=False))
        put(f"runs/{r}/chat_history.trimmed.jsonl", "\n".join(out) + "\n")
    t = f"/tmp/trellis-hook-trace-{r}"
    cp(t + ".log", f"runs/{r}/hook-trace.log")
    if os.path.isdir(t + ".d"):
        for f in sorted(os.listdir(t + ".d")):
            # keep every PreToolUse (subagent) record and the first UserPromptSubmit pair; PostToolUse are all 0-byte stdout, keep first 2
            keep = "PreToolUse" in f or f.startswith("0000-") or f.startswith("0001-")
            if not keep and "PostToolUse" in f:
                keep = len([k for k in os.listdir(t + ".d") if "PostToolUse" in k and k < f]) < 4
            if keep: cp(f"{t}.d/{f}", f"runs/{r}/hook-trace.d/{f}")
for f in ["comparison.md", "subagent-prompts.txt", "analyze-all.txt"]:
    cp(f"{SRC}/runs/{f}", f"evidence/{f}")
for f in ["replay-spawn_subagent.out", "replay-Task.out", "inspect-tpl-orig.json", "inspect-tpl-ours.json", "orig-init.log"]:
    cp(f"{SRC}/{f}", f"evidence/{f}")
for f in ["trace_wrapper.py", "wrap_hooks.sh", "setup.sh", "mkruns.sh", "launch.sh", "say.sh", "status.sh", "capture.sh", "analyze.py", "summ.py", "apply_fix.py", "apply_fix2.py", "mkfix2.sh", "peek3.py", "peek5.py", "collect.py"]:
    cp(f"{SRC}/{f}", f"scripts/{f}")
print("redactions:", hits)
