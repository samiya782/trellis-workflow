#!/usr/bin/env python3
"""Per-run analysis for the Trellis hook study. Usage: analyze.py RUN [RUN...]"""
import json, sys, glob, os, subprocess, collections, re
B = os.path.expanduser("~/tmp/trellis-grok-val-20261026")
TASK = ".trellis/tasks/10-26-textstats-top"

def texts(content):
    if isinstance(content, str):
        return content
    out = []
    for c in content or []:
        if isinstance(c, dict):
            out.append(c.get("text") or c.get("content") or "")
    return "\n".join(x if isinstance(x, str) else json.dumps(x) for x in out)

def load(path):
    rows = []
    if os.path.exists(path):
        for l in open(path):
            try:
                rows.append(json.loads(l))
            except Exception:
                pass
    return rows

def analyze(run):
    R = f"/tmp/grokval/hs/runs/{run}"
    sid = open(f"{R}/session-id.txt").read().strip()
    sd = glob.glob(os.path.expanduser(f"~/.grok/sessions/*/{sid}"))[0]
    hist = load(sd + "/chat_history.jsonl")
    res = {"run": run, "session_id": sid, "session_dir": sd}
    seq = []          # ordered events
    user_turn = 0
    all_ctx = []      # every text the model saw (user + tool results)
    for e in hist:
        t = e.get("type")
        if t == "user":
            tx = texts(e.get("content"))
            all_ctx.append(tx)
            m = re.search(r"<user_query>\n?(.*?)\n?</user_query>", tx, re.S)
            if m:
                user_turn += 1
                seq.append(("USER", user_turn, m.group(1)[:90]))
        elif t == "tool_result":
            all_ctx.append(texts(e.get("content")))
        elif t == "assistant":
            for tc in e.get("tool_calls") or []:
                try:
                    a = json.loads(tc.get("arguments") or "{}")
                except Exception:
                    a = {}
                n = tc.get("name")
                if n == "run_terminal_command":
                    seq.append(("CMD", user_turn, a.get("command", "")[:220]))
                elif n == "spawn_subagent":
                    seq.append(("SPAWN", user_turn, f"{a.get('subagent_type')} :: {str(a.get('description') or '')[:60]} :: prompt_head={str(a.get('prompt',''))[:100]!r}"))
                elif n in ("write", "search_replace", "hashline_edit", "edit_file"):
                    seq.append(("EDIT", user_turn, f"{n} {a.get('file_path') or a.get('target_file') or a.get('path')}"))
                else:
                    seq.append(("TOOL", user_turn, n))
    ctx = "\n".join(all_ctx)
    res["tool_names"] = dict(collections.Counter(x[2] if x[0] == "TOOL" else x[0] for x in seq if x[0] != "USER"))
    res["ctx_has_workflow_state_tag"] = "<workflow-state>" in ctx
    res["ctx_has_session_context_tag"] = "<session-context>" in ctx or "Trellis SessionStart" in ctx
    res["ctx_hook_reminders"] = len(re.findall(r"<system-reminder>[^<]{0,400}(hook|inject-)", ctx, re.I))
    res["ctx_mentions_inject_hooks"] = sorted(set(re.findall(r"inject-[a-z-]+\.py|session-start\.py", ctx)))
    # start / spawn / edit ordering
    def first(pred):
        for i, x in enumerate(seq):
            if pred(x):
                return i, x
        return None, None
    i_start, x_start = first(lambda x: x[0] == "CMD" and re.search(r"task\.py\s+start\s+(?!-)\S", x[2]))
    i_spawn, x_spawn = first(lambda x: x[0] == "SPAWN")
    i_edit, x_edit = first(lambda x: x[0] == "EDIT" and re.search(r"textstats\.py|test_textstats", x[2]))
    res["start"] = {"seq_index": i_start, "after_user_msg": x_start[1] if x_start else None, "cmd": x_start[2] if x_start else None}
    res["first_spawn"] = {"seq_index": i_spawn, "detail": x_spawn[2] if x_spawn else None}
    res["first_product_edit_by_main"] = {"seq_index": i_edit, "detail": x_edit[2] if x_edit else None}
    res["spawns"] = [x[2].split(" :: ")[0] for x in seq if x[0] == "SPAWN"]
    res["start_before_workers"] = (i_start is not None) and (i_spawn is None or i_start < i_spawn) and (i_edit is None or i_start < i_edit)
    # subagent sessions: product edits + injected context
    subs = []
    for sh in glob.glob(sd + "/subagents/*/chat_history.jsonl") + glob.glob(sd + "/subagents/**/chat_history.jsonl", recursive=True):
        if any(s["path"] == sh for s in subs):
            continue
        h = load(sh)
        first_user = next((texts(e.get("content")) for e in h if e.get("type") == "user" and "<user_query>" in texts(e.get("content"))), "")
        allu = "\n".join(texts(e.get("content")) for e in h if e.get("type") in ("user", "tool_result"))
        edits = []
        for e in h:
            for tc in (e.get("tool_calls") or []) if e.get("type") == "assistant" else []:
                if tc.get("name") in ("write", "search_replace", "hashline_edit"):
                    try:
                        a = json.loads(tc.get("arguments") or "{}")
                    except Exception:
                        a = {}
                    edits.append(os.path.basename(str(a.get("file_path") or a.get("target_file") or a.get("path"))))
        subs.append({"path": sh, "query_head": re.sub(r"\s+", " ", first_user)[:260],
                     "has_injected_trellis_context": ("=== " in first_user and "prd.md" in first_user) or "<trellis-context" in first_user or "Active task:" in first_user,
                     "edits": sorted(set(edits)),
                     "ctx_workflow_state_tag": "<workflow-state>" in allu})
    res["subagents"] = subs
    # final state
    tj = json.load(open(f"{B}/{run}/{TASK}/task.json")) if os.path.exists(f"{B}/{run}/{TASK}/task.json") else None
    res["task_status"] = tj and tj.get("status")
    cur = subprocess.run(["python3", ".trellis/scripts/task.py", "current", "--source"], cwd=f"{B}/{run}", capture_output=True, text=True)
    res["task_current_source_no_session_env"] = (cur.stdout + cur.stderr).strip()[:300]
    rt = sorted(glob.glob(f"{B}/{run}/.trellis/.runtime/sessions/*"))
    res["runtime_session_pointers"] = {os.path.basename(p): open(p).read().strip()[:200] for p in rt if os.path.isfile(p)}
    res["git_status"] = subprocess.run(["git", "status", "--short"], cwd=f"{B}/{run}", capture_output=True, text=True).stdout.strip().splitlines()
    # hook trace summary
    tl = load(f"/tmp/trellis-hook-trace-{run}.log")
    res["trace_counts"] = dict(collections.Counter(f"{d['hook']}|{d['event']}|{d.get('tool_name')}|{d.get('subagent_type')}|stdout>0={d['stdout_len']>0}" for d in tl))
    res["trace_pretool"] = [{k: d.get(k) for k in ("ts_local", "tool_name", "subagent_type", "tool_input_keys", "exit", "stdout_len", "stdout_head")} for d in tl if d["event"] == "PreToolUse"]
    res["trace_posttool_nonempty"] = [{k: d.get(k) for k in ("ts_local", "tool_name", "stdout_len", "stdout_head")} for d in tl if d["event"] == "PostToolUse" and d["stdout_len"] > 0][:6]
    res["sequence"] = seq
    json.dump(res, open(f"{R}/analysis.json", "w"), indent=2, ensure_ascii=False)
    return res

for run in sys.argv[1:]:
    r = analyze(run)
    print(f"\n##### {run}  status={r['task_status']}  start_before_workers={r['start_before_workers']}")
    for k in ("start", "first_spawn", "first_product_edit_by_main", "spawns", "tool_names", "ctx_has_workflow_state_tag", "ctx_has_session_context_tag", "ctx_hook_reminders", "ctx_mentions_inject_hooks", "task_current_source_no_session_env", "runtime_session_pointers", "git_status", "trace_counts", "trace_pretool", "trace_posttool_nonempty"):
        print(f"  {k}: {json.dumps(r[k], ensure_ascii=False)[:900]}")
    for s in r["subagents"]:
        print(f"  SUB inj={s['has_injected_trellis_context']} wfs={s['ctx_workflow_state_tag']} edits={s['edits']} q={s['query_head'][:200]}")
