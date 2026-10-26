import json,sys,os
rows=["| run | fixture | hooks | start ran | start after user msg # | start seq | first main product edit seq | start before edits/workers | task status | pointer file | workers | <workflow-state> in ctx | <session-context> in ctx | hook reminders in ctx | subagent prompt has injected ctx |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in sys.argv[1:]:
    p=f"runs/{r}/analysis.json"
    if not os.path.exists(p): continue
    a=json.load(open(p)); s=a.get("start") or {}
    fe=(a.get("first_product_edit_by_main") or {}).get("seq_index")
    ss=s.get("seq_index")
    ran=ss is not None
    before = ran and (fe is None or ss<fe) and bool(a.get("start_before_workers"))
    subs=a.get("subagents") or []
    inj="n/a"
    if subs:
        inj=any(("inject" in json.dumps(x).lower() and "spec" in json.dumps(x).lower()) or "<trellis" in json.dumps(x).lower() for x in subs)
    _,fx,mode,_rn=r.split("-")
    rows.append(f"| {r} | {fx} | {mode} | {'YES' if ran else 'NO'} | {s.get('after_user_msg','-')} | {ss} | {fe} | {before} | {a.get('task_status')} | {', '.join((a.get('runtime_session_pointers') or {}).keys()) or 'none'} | {', '.join(a.get('spawns') or []) or 'inline (main agent)'} | {a.get('ctx_has_workflow_state_tag')} | {a.get('ctx_has_session_context_tag')} | {len(a.get('ctx_hook_reminders') or [])} | {inj} |")
print("\n".join(rows))
