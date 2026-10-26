import json,glob,os,sys,re
for r in sys.argv[1:]:
    sid=open(f"runs/{r}/session-id.txt").read().strip()
    p=glob.glob(os.path.expanduser(f"~/.grok/sessions/*/{sid}/chat_history.jsonl"))[0]
    rows=[json.loads(l) for l in open(p)]
    print("=====",r)
    for i,x in enumerate(rows):
        c=x.get("content") or x.get("text") or ""
        if isinstance(c,list): c=" ".join(str(j.get("text","")) for j in c if isinstance(j,dict))
        c=str(c)
        if x.get("type")=="user" and i>3: print(i,"USER:",c[:150].replace("\n"," "))
        if x.get("type") in ("assistant","reasoning") and re.search(r"authori|user-only|user-typed|activation|1\.4",c):
            print(i,x["type"],":",c[:500].replace("\n"," "))
