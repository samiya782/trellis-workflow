set -e
B=/home/samiya/tmp/trellis-grok-val-20261026
cp -a $B/hs-tpl-ours $B/hs-tpl-fix2
cd $B/hs-tpl-fix2
python3 /tmp/grokval/hs/apply_fix2.py .
git add AGENTS.md docs/agents/matt-flow.md
git -c user.name=fixture -c user.email=fixture@example.invalid commit -q -m "hook-study: activation rule v2 (user-typed command only)"
git log --oneline -1
for d in hs-tpl-fix2 hs-fix2-on-r1 hs-fix2-on-r2; do grep -q "\"$B/$d\"" ~/.grok/trusted_folders.toml || printf "\n[folders.\"%s\"]\ntrusted = true\ndecided_at = %s\n" "$B/$d" "$(date +%s)" >> ~/.grok/trusted_folders.toml; done
