# 审计：grill「通过」结论如何得出，以及与 LHZHSQ 01a17d2d 的差异

日期：2026-10-27（Asia/Singapore）。依据 `docs/validation/2026-10-26-grok/` 与
`~/.grok/sessions/.../01a17d2d-3d94-7f33-86cd-d7ca9ae0abf1` 的保留证据，未改写会话本身。

## 1) 「validation passed」对 grill-with-docs / grill-alone 是怎么定的？

### INDEX 原文（判定标准）

`INDEX.md` Timeline 对 20:50–21:06 场景批的表述：

> `/grill-with-docs` made 1 task with `--no-start`. `/implement` OK.

同文件对 recheck：

> `/grill-me` stayed open once (33333333) and passed on the second run (66666666).

**通过标准 = 结果物判定，不是「会话一开始就有任务 + 已 load context」。**

| 场景 | 被记为 pass 的依据 | 证据 |
|---|---|---|
| `grill-docs` / `01a17842-eb1b-…` | 访谈结束后出现 **1 个** `planning` 任务，且创建带 `--no-start` | `evidence/fixtures-final-state.txt`：`10-26-textstats-top planning`；transcript `20261026-2050_grill-docs_01a17842.md` 在 **USER PROMPT #4 之后** 才 `task.py create … --no-start` |
| `grill-me` / 初跑 `01a1784c` | 有 6 轮访谈（未要求落盘任务） | `fixtures-final-state`：`grill-me` **只有** `00-bootstrap-guidelines`，无业务任务 |
| `recheck-grill-me` / `66666666` | 以「确认理解后给出 `/implement <scope>` 并 pause」为 pass（stateless 设计） | transcript 末尾 settled contract + `/implement Add textstats --top N:…`；fixture 仍无业务任务 |

session summary（grill-docs）：

```text
id: 01a17842-eb1b-74c1-b9c9-8f2218136197
cwd: …/grill-docs
session_kind: headless
session_summary: Add --top N option to textstats
```

### 实际时序（grill-with-docs）

1. PROMPT #1：`/grill-with-docs Add a --top N…` → 直接读 `.grok/skills/grill-with-docs`（Matt 技能体），**未**先 `get_context`、**未**建任务。
2. PROMPT #2–#4：问答 + 写 `GLOSSARY.md` / ADR。
3. 边界处才按 `matt-flow`「handoff 时 create」：`task.py create … --no-start`，填 `prd.md` / `implement.md`。

因此 INDEX 的「通过」= **晚建任务 + `--no-start` 落盘成功**，与用户期望的
「先建任务 → load context → 再 grill → 写入任务」**不是同一成功标准**。

## 2) 那些 run 里 hooks 到底有没有开火？

### hook-study 总表（`hook-study/INDEX.md`）

| hook | 事件 / matcher | 在 Grok 上 | stdout 是否进模型 |
|---|---|---|---|
| `session-start.py` | SessionStart `startup`/`clear`/`compact` | **从不**：Grok 发 `new`/`load` | 无 |
| `inject-workflow-state.py` | UserPromptSubmit | **会开火**（每条 prompt） | **否**：Grok 丢弃 allowing UPS 的 stdout；chat 中无 `<workflow-state>` |
| `inject-subagent-context.py` | PreToolUse `Task`→`spawn_subagent` | 会调到，但 tool_name 不匹配，stdout 0 B | 否 |
| `inject-spec-context.py` | PostToolUse Read/Edit/Write→`read_file`/… | 会调到，过滤器不认 Grok 工具名/字段，stdout 0 B | 否 |

结论原文：

> Net: on Grok, zero bytes of Trellis hook context reach the model… "hooks on" vs "off" is a null treatment.

### 轨迹计数（`hook-study/runs/*/hook-trace.log`，全部 hooks-on）

跨 12 个 on-run 聚合：

- `SessionStart/*`：**0**
- `UserPromptSubmit/inject-workflow-state.py`：**34**（全部 `stdout_len>0`，合计 ~14 KB，但未进模型）
- `PostToolUse/inject-spec-context.py`：**545**（`stdout_len` 全 0）
- `PreToolUse/inject-subagent-context.py`：**4**（仅 orig 跑，stdout 0；tool=`spawn_subagent`）

### grill-docs / LHZHSQ 会话 events

两会话 `events.jsonl` 均无 hook 事件类型（仅有 `turn_*` / `tool_*` / `phase_changed` / MCP）。
hooks 走 Claude-compat 侧信道，**不会**出现在 Grok session events 里；要以 hook-trace 为准。

**SessionStart 已知在 Grok 上跳过（matcher 不匹配）。实际会开火的是 UPS / PostToolUse /（偶发）PreToolUse，但对模型上下文等价于未注入。**

## 3) 与 LHZHSQ 练习会话 `01a17d2d` 为何看起来不同？

会话：`~/.grok/sessions/%2Fhome%2Fsamiya%2Fsrd%2FLHZHSQ%2FLHZHSQ-backend/01a17d2d-3d94-7f33-86cd-d7ca9ae0abf1`  
（interactive TUI，`grok-4.7`，cwd=`LHZHSQ-backend`）

| 维度 | 验证 fixture `grill-docs` | LHZHSQ `01a17d2d` |
|---|---|---|
| 入口 | 立刻 `/grill-with-docs …` | 同样以 `/grill-with-docs @…` 开场 |
| 前几轮有无任务 | 无（至 PROMPT #4 后才建） | **无**（Q1–Q14 整段 grill 无业务任务） |
| 任务何时出现 | 访谈收尾 handoff：`--no-start` | 用户随后打 **`/trellis-start 按此实现…`** → 先 `get_context`，再 `create … --no-start` 得到 `10-27-sp-archive-complete` |
| `/trellis-start` 语义 | 验证里单独测过：只 load context，**不建任务** | 同：命令本身只 `get_context`；建任务是模型读 matt-flow 后的 handoff |
| 成功标准 | harness：出现 1 个 `--no-start` 任务即 pass | 用户体感：grill 阶段「没有任务」→ 与 harness pass **错位** |
| headless vs TUI | headless，代理代答 | 交互 TUI，用户自答 |
| fixture trust | `grok --trust` 写入 trusted_folders | 真实项目，已信任 |
| hooks | 同上：SessionStart 0；UPS 开火但丢弃 | 同（events 无 hook；无理由认为不同） |

**纠正先前误读**：`01a17d2d` **并非「整段无任务」**——任务在同一会话后半段、`/trellis-start` 之后才创建；与 validation grill-docs 同属 **「晚建 + `--no-start`」**，差异主要在：

1. **成功标准**：INDEX 认「最终有任务」；用户认「grill 开始前就应有任务并 load context」。
2. **谁触发 handoff**：fixture 靠访谈结束自动 handoff；LHZHSQ 靠用户补 `/trellis-start` / `/implement`。
3. **grill-me**：文档写明 **stateless**（不建任务）；把它当「无 trellis-start 的 grill」对比会得到「无任务」，但这是设计而非 fixture 失败。

## 4) 根因（承接修复）

1. `docs/agents/matt-flow.md` 把 stateful 的 `grill-with-docs` 任务创建放在 **user-only 边界 handoff**，不是入口。
2. Grok 上 Trellis hooks **对模型无效**（SessionStart matcher 错；UPS stdout 丢弃；工具名不匹配）→ 无法靠 hook 在开场注入「先建任务」。
3. `.grok/commands/grill-with-docs.md` **不能**盖过 `.grok/skills/grill-with-docs`（symlink→`.agents/skills`，同名时 skill 胜出；且不可改 Matt 技能体）。
4. 验证 pass 标准过宽，掩盖了与用户期望路径的偏差。

修复方向（不改 Matt 技能体）：在 **AGENTS.md / matt-flow / workflow Phase Index** 把
`grill-with-docs` 改为 **入口即 bootstrap（create `--no-start` + get_context）**，再访谈并写入任务；
可选为 SessionStart 增加 `new|load` matcher（仍保留命令内显式 `get_context`）。
## 5) 修复后复验（2026-10-27）

Fixture: `~/tmp/trellis-grok-reval-grill-boot-20261027`（从旧 grill-docs 复制并覆盖 AGENTS/matt-flow/workflow/settings/trellis-start）。
Session: `01a17de6-10a5-7e22-aeb7-f2fca476518f`（headless, `grok-4.7-build-fast`, xhigh）。

Prompt 含「accept every recommended answer… do not implement」，以便单轮跑完。

工具序（节选）：

1. 读 `grill-with-docs` / `grilling` / `domain-modeling` / **`docs/agents/matt-flow.md`**
2. **`get_context.py` + `--mode phase`**
3. 探代码与 tracker
4. **`task.py create "Add textstats --top N" … --no-start`** → `.trellis/tasks/10-27-textstats-top-n`（`planning`）
5. 其后才写 GLOSSARY / ADR / 填 `prd.md`；**全程无 `ask_user_question`**（按提示接受推荐答案）

对照旧 `grill-docs`/`01a17842`：create 在 **USER PROMPT #4 收尾 handoff**；本次 create 在 **第一轮、写 ADR/glossary 之前**。

通过标准（新）：入口 bootstrap = get_context + `--no-start` create 早于访谈落盘；非「最终有任务即可」。
