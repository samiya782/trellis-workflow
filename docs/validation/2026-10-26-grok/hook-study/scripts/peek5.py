import json,glob,os,sys
out=[]
for r in sys.argv[1:]:
    sid=open(f"runs/{r}/session-id.txt").read().strip()
    base=os.path.dirname(glob.glob(os.path.expanduser(f"~/.grok/sessions/*/{sid}"))[0])
    for sub in sorted(os.listdir(f"{base}/{sid}/subagents")) if os.path.isdir(f"{base}/{sid}/subagents") else []:
        meta=json.load(open(f"{base}/{sid}/subagents/{sub}/meta.json"))
        ch=f"{base}/{sub}/chat_history.jsonl"
        if not os.path.exists(ch): out.append(f"{r} {sub} no chat"); continue
        rows=[json.loads(l) for l in open(ch)]
        u=[x for x in rows if x.get("type")=="user"]
        t=" ".join(json.dumps(x) for x in u[:3])
        marks={k:(k in t) for k in ["Active task","## PRD","prd.md","Spec","implement.jsonl","check.jsonl","<system-reminder>","inject-subagent-context","=== "]}
        st=meta.get("subagent_type") or meta.get("agent") or meta.get("name") or list(meta.keys())[:6]
        out.append(f"{r} sub={sub[:8]} type={st} first-user-msgs-chars={len(t)} markers={marks}")
print("\n".join(out))
