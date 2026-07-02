# Danyria 1.1.0 开发者文档 / Developer Documentation

作者 / Author：B站 千早ですわ  
版本 / Version：1.1.0  
适用游戏 / Target Game：Left 4 Dead 2

---

## 1. 项目结构 / Project Structure

### 中文

Danyria 由主程序、外置 HUD、游戏内 VScript 插件和语言资源组成。

- `Danyria.pyw`：主程序入口，负责主题界面、MOD 管理、武器数值、插件安装状态、HUD 参数保存与外置 HUD 启动。
- `assets/i18n.json`：外部语言包，是 UI 文本的主要来源。程序内置语言文本只作为缺失时的兜底。
- `payload/danyria_hud/DanyriaHUD.pyw`：外置 HUD 程序，读取游戏侧遥测文件并绘制速度表、敌人血量、评分系统 HUD。
- `payload/danyria_hud_plugin/`：HUD 遥测插件，提供基础速度、血量、敌人血量数据。
- `payload/danyria_penalty_plugin/`：评分系统插件，当前标记为测试项目，负责个人行为统计与评分事件输出。
- `server_dedicated_plugin/`：独立服务器用插件副本，逻辑与 HUD 插件保持同步。

### English

Danyria is composed of the main application, the external HUD, in-game VScript plugins, and localization resources.

- `Danyria.pyw`: Main application entry point for themed UI, MOD management, weapon values, plugin install status, HUD settings, and launching the external HUD.
- `assets/i18n.json`: External localization pack and the primary UI text source. Embedded strings are only fallback text.
- `payload/danyria_hud/DanyriaHUD.pyw`: External HUD process. It reads game-side telemetry files and draws the speedometer, enemy health panel, and score HUD.
- `payload/danyria_hud_plugin/`: HUD telemetry plugin for speed, health, and enemy health data.
- `payload/danyria_penalty_plugin/`: Score system plugin. It is marked as a test item and outputs personal behavior statistics and scoring events.
- `server_dedicated_plugin/`: Dedicated-server plugin copy, kept synchronized with the HUD plugin logic.

---


## 2. 评分系统修复说明 / Score System Fix Notes

### 中文

本版本重点修复普通战役或非指定 mutation 环境下评分事件不稳定的问题。

已增强的事件路径：

- 增加并导出更多特感击杀事件回调：`hunter_killed`、`smoker_killed`、`boomer_killed`、`spider_killed`，同时保留 Charger、Spitter、Jockey、Witch、Tank 的原事件路径。
- 修正官方特感击杀事件中 `userid` 被误当成受害者实体的问题；现在 `userid` 优先作为击杀者归因，受害者只从实体字段读取，避免击杀事件被“受害者是幸存者”过滤掉。
- `infected_death` 现在会优先按攻击者、受害者实体和感染者类型判定；如果识别到特感、Witch 或 Tank，会进入特感评分逻辑，否则才进入普感评分逻辑。
- 特感、Witch、Tank 增加轮询兜底：当事件回调未触发，但敌人血量归零或实体短时间内从追踪表消失时，会结合最近伤害、准星朝向和攻击状态尝试补记击杀。
- `player_hurt` 现在会记录被追踪玩家受到的自伤、世界伤害和爆炸伤害；油桶自爆等没有有效特感攻击者的伤害也会进入扣血记录。
- 特感伤害记录会标记最近被玩家伤害过的敌人实体，为后续击杀兜底提供归因依据。


### English

This version focuses on improving score-event reliability in normal campaigns and non-mutation environments.

Enhanced event paths:

- Added and exported more special-infected kill callbacks: `hunter_killed`, `smoker_killed`, `boomer_killed`, and `spider_killed`, while keeping the original Charger, Spitter, Jockey, Witch, and Tank paths.
- Fixed official special-kill events where `userid` could be treated as the victim entity. `userid` is now used primarily for killer attribution, while victim resolution only uses entity fields, preventing valid kills from being filtered as survivor victims.
- `infected_death` now resolves attacker, victim entity, and infected type first. Special infected, Witch, and Tank enter the special-kill score path; only normal infected fall back to common-kill scoring.
- Special infected, Witch, and Tank now have a polling fallback. If event callbacks do not fire but the enemy reaches zero HP or disappears from the tracked table shortly after being aimed at or damaged, the script attempts to record the kill.
- `player_hurt` now records self-damage, world damage, and explosion damage taken by the tracked player. Oil-barrel self-damage can now be recorded even when no infected attacker exists.
- Special-infected damage records now mark recently damaged enemy entities, which gives the polling fallback a safer attribution source.


---

## 3. 遥测文件 / Telemetry Files

### 中文

游戏侧 VScript 会写入紧凑的 `DHUD2` 遥测数据，外置 HUD 读取后显示。

常见文件：

- `ems/danyria_hud_telemetry.txt`
- `danyria_hud_telemetry.txt`
- `ems/danyria_hud_score_state.txt`
- `danyria_hud_score_state.txt`
- `ems/danyria_hud_target.txt`
- `danyria_hud_target.txt`

目标绑定文件用于专用服务器或多玩家环境，帮助脚本锁定要追踪的本地玩家或指定玩家。

### English

The game-side VScript writes compact `DHUD2` telemetry data, which is then read by the external HUD.

Common files:

- `ems/danyria_hud_telemetry.txt`
- `danyria_hud_telemetry.txt`
- `ems/danyria_hud_score_state.txt`
- `danyria_hud_score_state.txt`
- `ems/danyria_hud_target.txt`
- `danyria_hud_target.txt`

The target-binding files are used in dedicated-server or multiplayer environments to help the script lock onto the local or designated tracked player.

---

## 4. 发布前检查 / Pre-release Checklist

### 中文

执行：

```bat
python -m py_compile Danyria.pyw payload\danyria_hud\DanyriaHUD.pyw
```

同时检查：

- 外部语言包是否与内置兜底文本同步。
- 插件卡片是否仍不显示运行方式提示。

### English

run:

```bat
python -m py_compile Danyria.pyw payload\danyria_hud\DanyriaHUD.pyw
```

Also verify:

- External localization pack stays synchronized with embedded fallback text.
- Plugin cards do not show launch/run descriptions.

---

## 5. 1.0.0 Hotfix: Score attribution and HUD persistence / 1.0.0 热修复：评分归因与 HUD 记忆

### 中文

- 特感击杀兜底改为“事件归因 + 个人击杀统计轮询 + 近期本人伤害贡献”三层方案。
- 修复特殊击杀轮询变量被固定为 0 的问题。
- 受伤扣分改为优先读取被追踪玩家自己的实际血量变化，避免油桶、爆炸、环境伤害因事件攻击者字段缺失而漏记。
- 修复评分 HUD 勾选状态在主程序启动时被默认未勾选状态覆盖的问题。
- 外置 HUD 新增屏幕边界校正，避免速度表因保存坐标异常而启动后出现在屏幕外。

### English

- Special infected kill fallback now uses event attribution, personal kill-stat polling, and recent tracked-player damage contribution.
- Fixed the special-kill polling delta that had been hardcoded to zero.
- Damage taken now prefers the tracked player's actual HP delta, so explosive and environmental damage can be counted even when attacker fields are missing.
- Fixed score HUD checkbox persistence being overwritten by the default unchecked state during main-app startup.
- Added screen-boundary clamping for external HUD windows to prevent the speedometer from reopening off-screen.

## 1.0.0 hotfix - score false positives and speed HUD

### 中文

- 关闭特感与 Tank 的统计属性轮询，避免 BOT、团队统计、旧章节状态在开局被误算为玩家击杀。
- 过图保存状态加入 `state_ver=2`，旧版本遗留状态文件不会继续导入，仍保留新版过图继承。
- 修复速度表 `paintEvent` 缩进错误，窗口现在能正常绘制。

### English

- Disabled special infected and Tank stat polling to avoid bot, team-stat, or stale chapter carry-over being counted as player kills at round start.
- Added `state_ver=2` to transition state; stale legacy state files will no longer be loaded while new transition carry-over remains supported.
- Fixed the SpeedWindow `paintEvent` indentation so the speedometer window can render normally.

## 2026-06-08 Score enemy bridge hotfix / 计分敌人桥接热修复

### 中文

- 计分板现在复用血量 HUD 的实体扫描结果。当被追踪玩家正在攻击，并且准星方向上的特感、Witch 或 Tank 血量下降时，先标记该实体为“本人贡献目标”，后续死亡或实体消失才允许计分。
- 保留关闭统计属性轮询的策略，避免开局 BOT 或旧章节团队统计继续误加特感 / Tank。

### English

- The score board now reuses the health HUD entity scan. When the tracked player is attacking and an aimed special infected, Witch, or Tank loses HP, that entity is marked as a personal contribution target before a later death or disappearance can score.
- Stat-property polling remains disabled for special infected and Tank kills to avoid bot or stale chapter team-stat false positives.

---

## 6. 多人 / 三方服内存桥 / Multiplayer & 3rd-party-server memory bridge

### 中文

**背景**：VScript 只在服务器端运行。你作为客户端加入第三方/专用服时，本机不跑脚本、也读不到服务器硬盘，所以 `ems/*.txt` 遥测拿不到。`server_payload` 里的 `DHUD_SendTelemetryToClient` 当前是空函数，客户端 console 通道也已移除，所以装不了插件的三方服上 HUD 没有数据。

**方案**：在外置 HUD 里加了一个**只读外部内存**数据源（不是 DLL 注入，封号风险更低），直接读《求生之路2》进程内存来画速度表、血量、敌人血量；评分沿用已有的 `_apply_client_score_fallback()` 按状态变化推算（尽力而为）。

- 代码：`payload/danyria_hud/DanyriaHUD.pyw` 内嵌 `L4D2Memory` / `_ProcMem` / `_Netvars`（纯 ctypes，无第三方依赖，打包安全）。
- 数据源优先级：内存开启时优先用内存；读不到时自动回落到本地 `ems` 文件（本地房主照常可用）。
- 开关：主程序 HUD 板块与评分板块各有“启用 多人/三方服 内存读取（后果自负）”勾选框，开启时弹**风险确认框**；状态存在 hud 配置的 `memory.enabled`。
- 偏移：与版本相关的 3 个锚点（local_player / entity_list / class_list）和 netvar 都在 `payload/danyria_hud/danyria_mem_offsets.json`，**默认留空**，需要按你当前 L4D2 版本校准一次。netvar 走 RecvTable 按名自动解析；也支持 `manual_offsets` 手填。
- 打包后该 json 会落到 `%APPDATA%/Danyria/danyria_hud/`（可写、可改），首次从打包资源播种。
- 自检：源码 `pythonw DanyriaHUD.pyw --mem-diagnose`，或打包后 `Danyria.exe --danyria-hud --mem-diagnose`；结果写到 `danyria_mem_diagnostic.txt`，含解析到的地址与一次 hp/speed 采样。

**校准（任选一条）**：A) 从公开 L4D2 偏移 dump 把 `dwLocalPlayer/dwEntityList/dwGetAllClasses` 填进 `signatures.*.static`，netvar 自动解析；B) 只填 local_player+entity_list 两个锚点，netvar 偏移粘进 `manual_offsets`；C) 用字节签名 `signatures.*.pattern`（最抗更新）。

**风险**：第三方读取游戏内存，受 VAC 保护的服务器可能判为作弊并封号。仅在可接受后果的服上使用。

### English

VScript runs server-side only, so a joining client on a 3rd-party/dedicated server cannot get `ems/*.txt` telemetry (its scripts don't run and it can't read the server disk; the dedicated→client bridge `DHUD_SendTelemetryToClient` is an empty stub). Added a **read-only external memory** data source (not DLL injection) embedded in `DanyriaHUD.pyw` (`L4D2Memory`, pure ctypes) that reads the L4D2 process directly for speed/HP/enemy-HP; score reuses the existing `_apply_client_score_fallback()` (best effort).

- Memory is the primary source when enabled and falls back to local `ems` files automatically (local host still works).
- Toggle lives in the HUD panel and the penalty panel ("Enable multiplayer / 3rd-party memory read"), with a mandatory risk-confirmation dialog; persisted as `memory.enabled` in the hud config.
- Version-specific anchors + netvars live in `danyria_mem_offsets.json` (ships empty, calibrate once per build). Netvars auto-resolve via the RecvTable walk; `manual_offsets` overrides are supported. Frozen builds seed a writable copy under `%APPDATA%/Danyria/danyria_hud/`.
- Self-check: `--mem-diagnose` (writes `danyria_mem_diagnostic.txt`).
- Packaging unchanged: only stdlib (`ctypes`/`struct`) added, new json is auto-bundled with `payload`.
- Risk: reading game memory can be flagged by VAC-secured servers. Use only where you accept the consequences.

### 更新 / Update — 自动化与弹窗修复

- **弹窗修复**：项目里 `QMessageBox` 被替换成自带的 `DanyriaMessageBox`，其 `.warning()` 只有 OK 按钮、永不返回 Yes，导致确认后开关又被取消。改用 `QMessageBox.question()`（是/否，返回 `StandardButton`）。
- **netvar 全自动**：新增 `find_recvtables_by_string()`——按 RecvTable 名字字符串（`DT_BasePlayer` 等，跨版本不变）+ xref 反查表地址，零配置解析所有 netvar 偏移，**不再需要 class_list 签名，也不需要手填**。
- 因此终端用户最多只需 **2 个基址**：`local_player`、`entity_list`。只给 `local_player` 也能出速度+血量（优雅降级）。锚点支持**候选数组**，依次尝试。
- 分发建议：作者在自己机器上校准一次这 2 个 static 偏移，连同 `danyria_mem_offsets.json` 一起发布，**其他人无需任何操作**；L4D2 更新后只需有人重校这 2 个数。
- English: fixed the confirm dialog (use `question`, not the OK-only `warning`); netvars now auto-resolve by RecvTable name-string xref (no class_list, no manual offsets); end users need at most 2 base pointers; `local_player` alone still yields speed+HP; anchors accept candidate lists. Calibrate the 2 statics once and ship the json so others need nothing.

### 更新 2 / Update 2 — 基址也运行时全自动（真正零配置）

- 进一步去掉手动步骤：`entity_list` 和 `local_player` 现在**运行时自动检测**，`danyria_mem_offsets.json` 可以全空。
- `entity_list`：扫描 client.dll 的 `.data` 节（`_pe_data_sections` 解析 PE 节表），找到一段步长 0x10 的指针数组，用「指向对象的 vtable 落在 client.dll 范围内」+「实体的 m_iTeamNum/m_iHealth 合理」双重校验确认（`_auto_find_entitylist`/`_validate_entitylist`）。
- `local_player`：在 `.data` 里找一个值等于某个队伍2幸存者实体指针、且不在实体数组内的独立静态槽——即 dwLocalPlayer（`_auto_find_localplayer`），每帧解引用得到当前本地玩家。
- 全程不依赖任何字节签名或手填数字，只依赖 Source 引擎固定的结构布局 + 已自动解析的 netvar。扫描限速 3s，进游戏加载地图后自动就绪；`--mem-diagnose` 会强制立刻扫一次并打印结果。
- 配置里若手填了 static/manual，则优先用手填值（作为大更新后失效时的兜底）。
- English: base pointers are now auto-detected at runtime too — the json can be entirely empty. entity_list is found by scanning client.dll .data for a stride-0x10 pointer array validated by client.dll-range vtables + sane team/HP netvars; local_player is the standalone .data slot pointing at a team-2 survivor (dwLocalPlayer). No signatures, no numbers. Throttled 3s; ready after loading a map; manual config still wins if provided.

### 更新 3 / Update 3 — 反馈修复（卡死/不触发/评分/翻译）

- **进游戏不触发**：`_static_done` 以前即使 client.dll 还没加载也被置真，导致提前开 HUD 后进游戏永远卡在未就绪。改为只有真正解析出关键 netvar 才算完成；attach 后若缺 client.dll 会限速重扫模块表。现在先开 HUD 再进游戏会自动接上，无需再开关一次。
- **进游戏偶发把 HUD 卡没**：后台自动扫描是纯 Python 遍历 .data，长时间占着 GIL 把 Qt 绘制线程饿死。修复：① 每次扫描只读一次 client.dll 映像（之前一趟读 3 次，各几十 MB）；② 扫描循环周期性 `time.sleep(0)` 让出 GIL；③ 静态解析/存活检测都加了限速（1.5s / 1s），不再每帧读 30MB 或枚举进程。
- **第三方服评分错乱**：内存拿不到服务器的击杀/道具/造成伤害等事件归因。改为在内存层算一个【诚实的个人评分】——只用本地玩家可靠状态（受伤/被击倒/死亡，按 default_score_rules 扣分），作为权威值喂入，绕开会被 BOT/团队/敌人列表噪声污染的 `_apply_client_score_fallback` 启发式；拿不到的击杀/道具/造成伤害一律显示 0（诚实，而非错乱）。
- **翻译**：新加的 UI 文案补齐 8 种语言，集中在 `DanyriaWindow.MEM_TEXT`（key -> {lang: text}）。这也是比旧 i18n「逐条对照」更省事的写法，以后新增文本建议照此集中写。
- English: fixed (1) pre-start HUD not engaging after the game launches (`_static_done` no longer latches before client.dll/netvars resolve; modules re-enumerated when client.dll is missing); (2) HUD freezing on map load (single image read per scan + periodic `time.sleep(0)` GIL yields + throttled static-resolve/alive checks); (3) scrambled score on 3rd-party servers (see Update 4); (4) added all 8 languages for the new UI strings, centralized in `DanyriaWindow.MEM_TEXT` (the convenient key→{lang:text} pattern).

### 更新 4 / Update 4 — 内存评分用「用户规则」并真正抓取战斗数据

- 之前内存模式把击杀/造成伤害置 0、规则写死，用户反馈在第三方服拿不到正确数据。现重做评分：
- 新增 `_ScoreEngine`：单次世界扫描 `_scan_world` 收集所有感染者(team3)原始记录（idx/ptr/hp/zombieClass/origin/dist）；逐帧跟踪每个感染者血量；当其掉血且本地玩家「正在开火(m_nButtons&IN_ATTACK，带 0.4s 记忆) + 准星指向它(由 m_angEyeAngles 求前向量，~28° 锥)」时，把这段伤害归因给本人，累加 `damage_done`；该感染者死亡(血量→0 或从表中消失)且 2.5s 内有本人贡献则按 `m_zombieClass` 记为 普感/特感/Witch/Tank 击杀。
- 评分用**用户在前端配置的规则值**：`load_score_rules()` 读 `danyria_hud_score_rules.txt`（与 hud 配置同目录或 ems），每 ~2s 重载，所以你在软件里改数值即时生效。`penalty_score = 60 + 各项计数 × 你的规则值`。
- 新增 netvar：`m_nButtons`/`m_angEyeAngles`/`m_vecViewOffset`（同样字符串反查自动解析）。世界扫描限到 ~30Hz。
- 诚实说明：客户端没有服务器的伤害归因，这是**启发式估算**——团队混战（你和队友/BOT 同时打一个目标）会偏高；救人/吃药/挂边等纯事件仍置 0（内存无法可靠判定）。
- English: reworked memory-mode scoring to use the **user's configurable rule values** (`load_score_rules()` reads `danyria_hud_score_rules.txt`, reloaded ~2s so front-end edits take effect live) and to actually capture combat. New `_ScoreEngine` + single-pass `_scan_world`: tracks every infected's HP; attributes HP drops to the local player when firing (`m_nButtons & IN_ATTACK`, 0.4s memory) and aiming at it (forward vector from `m_angEyeAngles`, ~28° cone); counts kills by `m_zombieClass` (common/special/witch/tank) and accumulates `damage_done`. Added netvars `m_nButtons`/`m_angEyeAngles`/`m_vecViewOffset`. Honest caveat: client has no server-side damage attribution, so this is a heuristic that over-counts in team play; pure item/revive/ledge events stay 0.

### 更新 5 / Update 5 — UI 精简与可靠性

- 评分板块的「多人/第三方」开关移除；只在 HUD 板块保留**一个**开关，文案就叫「多人/第三方模式」。之前两个开关共用 `memory.enabled`、`_sync_memory_checks` 会联动（开一个另一个跟着开）——移除后不再联动。
- 删除所有第三方运作说明文案（板块提示标签 `mem_*_hint`、开启后的 `enabled_tip` 弹窗）；风险确认弹窗 `warn_body` 改为只有「后果自负，是否开启？」，不含任何运作方式描述。
- 开关文案接入 `update_language()`（`mem_enable_check_hud.setText(mem_tr("enable"))`），切换语言时即时刷新——修复"新加文本不翻译"。`MEM_TEXT` 精简为 enable/warn_title/warn_body，仍各含 8 语言。
- 修复"先开 HUD 再进游戏要再开一遍"：worker 在内存模式下、若一直没出数据，每 8s 自动**重建 L4D2Memory**（等价于手动重开开关），这样后启动的游戏会被自动接上。
- English: removed the penalty-panel memory toggle (one toggle only, in the HUD panel, labelled "Multiplayer / 3rd-party mode"); the two were synced via `_sync_memory_checks`, now only one exists. Deleted all 3rd-party how-it-works text (hint labels + `enabled_tip` popup); the confirm dialog body is now just "Use at your own risk. Enable?". Hooked the checkbox into `update_language()` so it retranslates on language switch (fixes the "untranslated" report). Fixed "HUD started before the game needs re-toggling": the worker auto-rebuilds `L4D2Memory` every 8s while it has produced no data, so a later-launched game is picked up automatically.

## 7. 服务器面板 / Server panel

### 中文

- **第四个板块「服务器」**：导航加按钮、`main_stack` 加 `servers_page`。后端 `ServerBrowser`（`Danyria.pyw` 顶部，纯 Python UDP）：`a2s_query_master`(Valve 主服务器) + `a2s_info`/`a2s_players`(A2S 查询) + `a2s_lan_scan`(局域网广播)；后台线程每 3s 刷新，UI 用 1s QTimer 拉 `snapshot()` 实时更新。分类（互联网/局域网/好友）、文本筛选、详情、一键进入（`steam://connect/ip:port` 或好友 `steam://joinlobby`，会自动启动游戏并等加载/创意工坊完成）。
- **好友**：`steam_friends_servers` 用 ctypes flat API 读 Steam 好友（用 appid **480** 初始化，避免把自己标记成在玩 L4D2），列出正在玩 550 的好友及其可加入地址/lobby。实验性、需 Steam 运行；任何失败都安全返回空。
- 协议解析做了离线单元测试；Qt 控件/枚举已验证；只用标准库（socket/struct/threading/ctypes），打包无新依赖。**联网/主服务器可达性与 Steam 好友需在你机器上实测**——主服务器协议 Valve 有限速，可能返回有限或为空。

### English

- New 4th "Servers" panel: nav button + `servers_page`. Backend `ServerBrowser` (pure-Python UDP): `a2s_query_master` (Valve master) + `a2s_info`/`a2s_players` + `a2s_lan_scan`; background thread refreshes every 3s, UI polls `snapshot()` via a 1s QTimer. Source categories (internet/LAN/friends), text filter, detail, one-click join (`steam://connect` or friends `steam://joinlobby`, which auto-launches the game and waits for addons). Friends via `steam_friends_servers` (ctypes flat API, inits with appid 480 so it never marks you in-game; experimental, needs Steam running, fails safe to empty). A2S parsing unit-tested; Qt widgets verified; stdlib-only (no new packaging deps). Live behaviour (master-server reachability, Steam) needs on-machine testing — Valve rate-limits the master protocol so the internet list may be limited/empty.

### 更新 / Update — 服务器黑名单 / Server blacklist

**中文**

- 可按**名字关键字**（子串、忽略大小写）和 **IP**（精确或前缀）屏蔽服务器。国内 RPG 服会频繁改显示名来绕过名字过滤，所以 IP 屏蔽更可靠。
- 存储：`danyria_server_blacklist.json`（与 hud 配置同目录），结构 `{"enabled": bool, "names": [...], "ips": [...]}`（读写 `_srv_load_blacklist` / `_srv_save_blacklist`）。
- UI：服务器板块加「启用黑名单」勾选框 +「编辑黑名单」按钮（`create_themed_dialog` 统一风格弹窗，关键字/IP 空格分隔）+「拉黑所选」按钮；开启后 `_srv_refresh_table` 用 `_srv_blacklisted` 过滤命中行。

**English**

- Blocks servers by **name keyword** (case-insensitive substring) and by **IP** (exact or prefix). CN "RPG" servers rename their display name constantly to dodge name filters, so IP blocking is the reliable path.
- Stored in `danyria_server_blacklist.json` next to the hud config, shape `{"enabled": bool, "names": [...], "ips": [...]}` (`_srv_load_blacklist` / `_srv_save_blacklist`).
- UI: an "enable blacklist" checkbox + an "Edit blacklist" button (themed via `create_themed_dialog`, keywords/IPs space-separated) + a "Block selected" button; when enabled, `_srv_refresh_table` filters matching rows via `_srv_blacklisted`.

---

## 8. HUD 皮肤系统 / HUD skin system

### 中文

- **三套皮肤**，配置键 `hud_style`，在**设置**里用数字下拉选择：`1 经典 classic` / `2 霓虹赛博 acg` / `3 薄荷薰衣草 mint`。`apply_settings` 把选择写进 HUD 配置，HUD 端每帧按 `hud_style` 分流绘制；配色字典 `ACG` / `ACG_MINT` 与经典完全隔离。
- 三个窗口（`SpeedWindow` / `EnemyWindow` / `PenaltyWindow`）的 `paintEvent` 顶部按皮肤分支，经典逻辑原样保留：
  - **经典 classic**：原圆角边框（`draw_hud_frame`）+ 圆形表盘 / 指针。
  - **霓虹赛博 acg**：斜切矩形面板（`draw_angular_panel`：切左上 + 右下两角、直边、单描边、无辉光）、斜体数字、双色斜切进度条（`draw_angular_bar`）、斜切 chip（`draw_angular_chip`）；配色电光青 `#45E0FF` + 品红 `#FF57C7`。敌人为逐个斜切卡片。
  - **薄荷薰衣草 mint**：圆润极简（`draw_soft_panel` 圆角 + 发丝描边）、◇ 菱形标（`draw_acg_glyph`）、圆点 chip（`draw_soft_chip`，无底框）、细胶囊血条（`draw_soft_bar`）；配色薄荷 `#7CE0D4` + 薰衣草 `#B79CFF` + 天蓝 `#7FC7FF`。
- **敌人血条排布（仅薄荷）**：每个敌人一张**独立卡片**（自己出现 / 自己消失，和霓虹一致）；单卡内「名字 + 当前/最大血量」一行、胶囊血条、底部「百分比(左) / 距离(右)」。
- **拖动**：取消整窗拖拽，改为右上角 `DragGrip` 拖拽点（18×18 圆点子控件）。
- **缩放**：取消鼠标拖拽放大，改为每个插件板块的 `scale` 数值（0.3–4.0）；`sync_window` 按 `scale × 逻辑尺寸` 建窗。
- 修复敌人窗口建窗高度（`76+n×58`）与绘制逻辑高度（`60+n×58`）不一致导致的纵向拉伸，现已一致。

### English

- **Three skins**, config key `hud_style`, chosen in **Settings** via a numeric combo: `1 classic` / `2 acg (neon cyber)` / `3 mint (mint lavender)`. `apply_settings` writes the choice to the HUD config; the HUD dispatches per `hud_style` each frame. Palette dicts `ACG` / `ACG_MINT` are fully isolated from the classic skin.
- Each window (`SpeedWindow` / `EnemyWindow` / `PenaltyWindow`) branches at the top of `paintEvent`, classic path untouched:
  - **classic**: original rounded frame (`draw_hud_frame`) + circular gauge / needle.
  - **acg (neon)**: chamfered-rectangle panels (`draw_angular_panel` — top-left + bottom-right corners cut, straight edges, single border, no glow), italic numbers, two-tone slanted bars (`draw_angular_bar`), slanted chips (`draw_angular_chip`); electric cyan `#45E0FF` + magenta `#FF57C7`. Enemies are per-enemy angular cards.
  - **mint**: soft / minimal (`draw_soft_panel` rounded + hairline border), ◇ diamond glyph (`draw_acg_glyph`), dot chips (`draw_soft_chip`, no box), thin pill bars (`draw_soft_bar`); mint `#7CE0D4` + lavender `#B79CFF` + sky `#7FC7FF`.
- **Enemy HP row (mint only)**: each enemy is an **independent card** (appears / disappears on its own, like neon); inside, "name + current/max HP" on the top line, a pill bar, then "percent (left) / distance (right)".
- **Drag**: whole-window drag removed in favour of a top-right `DragGrip` handle (18×18 dot child widget).
- **Scale**: mouse drag-resize removed; each plugin panel has a `scale` value (0.3–4.0); `sync_window` builds the window at `scale × logical size`.
- Fixed the enemy window being created at `76+n*58` while painting at `60+n*58`, which stretched it vertically; the two now match.
