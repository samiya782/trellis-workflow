#!/usr/bin/env bash
# hook-study fixture builder (disposable fixtures only)
set -euo pipefail
B=$HOME/tmp/trellis-grok-val-20261026
HS=/tmp/grokval/hs
SRC=/tmp/hs-src
rm -rf "$SRC"; git clone -q "$B/recheck-tui" "$SRC"; git -C "$SRC" checkout -q 9164a53
T=.trellis/tasks/10-26-textstats-top

# ---------- (A) ORIGINAL: stock trellis init ----------
O=$B/hs-tpl-orig; rm -rf "$O"; mkdir -p "$O"; cd "$O"
git init -q -b main; git config user.name Fixture; git config user.email fixture@example.invalid
mkdir -p tests docs/adr
cp "$SRC/textstats.py" .; cp "$SRC/tests/test_textstats.py" tests/
cp "$SRC/GLOSSARY.md" .; cp "$SRC/docs/adr/0001-rank-exact-words.md" docs/adr/
printf '__pycache__/\n' > .gitignore
git add -A; git commit -qm "seed textstats demo"
trellis init --claude --grok -y -u fixture > "$HS/orig-init.log" 2>&1
git add -A; git commit -qm "stock trellis 0.7.0-beta.4 init --claude --grok -y -u fixture"
mkdir -p $T; cp "$SRC/$T"/{task.json,prd.md,implement.jsonl,check.jsonl} $T/
git add -A; git commit -qm "seed planned task textstats-top"

# ---------- (B) OURS: grok-branch fixture + ~/trellis platform files ----------
U=$B/hs-tpl-ours; rm -rf "$U"; git clone -q "$SRC" "$U"; cd "$U"
git checkout -q -b main 9164a53; git config user.name Fixture; git config user.email fixture@example.invalid
git remote remove origin
rm -f $T/implement.md
for d in .claude .agents .codex .grok; do
  rsync -a --delete --exclude __pycache__ "$HOME/trellis/$d/" "$U/$d/"
done
cp "$HOME/trellis/skills-lock.json" .
printf '__pycache__/\n' > .gitignore
git add -A; git commit -qm "overlay ~/trellis working-tree platform files; drop Matt implement.md from seeded task"
bash "$HOME/trellis/scripts/grok-fixes/apply-grok-fixes.sh" --dry-run "$U" > "$HS/ours-apply-dryrun.log" 2>&1 || true

echo built
