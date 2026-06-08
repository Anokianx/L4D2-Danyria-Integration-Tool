# Danyria 1.0.0 开发者文档 / Developer Documentation

作者 / Author：B站 千早ですわ  
版本 / Version：1.0.0  
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
