#!/usr/bin/env bash
# create disposable run copies; "off" variants drop the hooks block from .claude/settings.json
set -euo pipefail
B=$HOME/tmp/trellis-grok-val-20261026
for r in "$@"; do            # e.g. hs-orig-on-r1
  fx=$(echo "$r" | cut -d- -f2); mode=$(echo "$r" | cut -d- -f3)
  rm -rf "$B/$r"; cp -a "$B/hs-tpl-$fx" "$B/$r"
  rm -f /tmp/trellis-hook-trace-$r.log; rm -rf /tmp/trellis-hook-trace-$r.d
  mkdir -p /tmp/grokval/hs/runs/$r
  if [ "$mode" = off ]; then
    python3 - "$B/$r/.claude/settings.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d.pop("hooks", None)
open(p, "w").write(json.dumps(d, indent=2) + "\n")
PY
    git -C "$B/$r" commit -qam "hook-study: hooks OFF (hooks block removed from .claude/settings.json)"
  fi
  (cd "$B/$r" && grok inspect --json > /tmp/grokval/hs/runs/$r/inspect.json 2>&1 || true)
  python3 -c "import json;d=json.load(open('/tmp/grokval/hs/runs/$r/inspect.json'));print('$r','trusted',d['projectTrusted'],'hooks',len(d['hooks']))"
done
