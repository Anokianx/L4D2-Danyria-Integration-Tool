printl("[DHUD] Danyria unified HUD personal score script loaded.");

try
{
    if (!("MutationOptions" in this)) MutationOptions <- {};
    MutationOptions.ActiveChallenge <- 1;
}
catch(e) {}

if (!("DHUD_VERSION" in getroottable())) ::DHUD_VERSION <- "score-system-v100-2026-06";
if (!("DHUD_FILE" in getroottable())) ::DHUD_FILE <- "danyria_hud_telemetry.txt";
if (!("DHUD_FILE2" in getroottable())) ::DHUD_FILE2 <- "ems/danyria_hud_telemetry.txt";
if (!("DHUD_STATE_FILE" in getroottable())) ::DHUD_STATE_FILE <- "danyria_hud_score_state.txt";
if (!("DHUD_STATE_FILE2" in getroottable())) ::DHUD_STATE_FILE2 <- "ems/danyria_hud_score_state.txt";
if (!("DHUD_TARGET_FILE" in getroottable())) ::DHUD_TARGET_FILE <- "danyria_hud_target.txt";
if (!("DHUD_TARGET_FILE2" in getroottable())) ::DHUD_TARGET_FILE2 <- "ems/danyria_hud_target.txt";
if (!("DHUD_RULE_FILE" in getroottable())) ::DHUD_RULE_FILE <- "danyria_hud_score_rules.txt";
if (!("DHUD_RULE_FILE2" in getroottable())) ::DHUD_RULE_FILE2 <- "ems/danyria_hud_score_rules.txt";
if (!("DHUD_SCORE_RULES" in getroottable())) ::DHUD_SCORE_RULES <- {};
if (!("DHUD_SCORE_RULES_LAST_LOAD" in getroottable())) ::DHUD_SCORE_RULES_LAST_LOAD <- -100.0;
if (!("DHUD_LAST_WRITE" in getroottable())) ::DHUD_LAST_WRITE <- 0.0;
if (!("DHUD_LAST_CONSOLE" in getroottable())) ::DHUD_LAST_CONSOLE <- 0.0;
if (!("DHUD_WRITE_INTERVAL" in getroottable())) ::DHUD_WRITE_INTERVAL <- 0.033;
if (!("DHUD_CONSOLE_INTERVAL" in getroottable())) ::DHUD_CONSOLE_INTERVAL <- 0.70;
if (!("DHUD_POLL_REGISTERED" in getroottable())) ::DHUD_POLL_REGISTERED <- false;
if (!("DHUD_EVENTS_REGISTERED" in getroottable())) ::DHUD_EVENTS_REGISTERED <- false;
if (!("DHUD_TIMER_ACTIVE" in getroottable())) ::DHUD_TIMER_ACTIVE <- false;
if (!("DHUD_MAX_DIST" in getroottable())) ::DHUD_MAX_DIST <- 1800.0;

if (!("DHUD_SCORE" in getroottable())) ::DHUD_SCORE <- 60.0;
if (!("DHUD_FF" in getroottable())) ::DHUD_FF <- 0;
if (!("DHUD_FF_DAMAGE" in getroottable())) ::DHUD_FF_DAMAGE <- 0;
if (!("DHUD_INCAPPED" in getroottable())) ::DHUD_INCAPPED <- 0;
if (!("DHUD_DEATHS" in getroottable())) ::DHUD_DEATHS <- 0;
if (!("DHUD_REVIVES" in getroottable())) ::DHUD_REVIVES <- 0;
if (!("DHUD_RESCUED_BY_TEAM" in getroottable())) ::DHUD_RESCUED_BY_TEAM <- 0;
if (!("DHUD_HEALS" in getroottable())) ::DHUD_HEALS <- 0;
if (!("DHUD_HEAL_HP_SELF" in getroottable())) ::DHUD_HEAL_HP_SELF <- 0;
if (!("DHUD_HEAL_HP_TEAM" in getroottable())) ::DHUD_HEAL_HP_TEAM <- 0;
if (!("DHUD_LAST_HEAL_HP_TIME" in getroottable())) ::DHUD_LAST_HEAL_HP_TIME <- -100.0;
if (!("DHUD_HEALED_BY_TEAM" in getroottable())) ::DHUD_HEALED_BY_TEAM <- 0;
if (!("DHUD_DEFIBS" in getroottable())) ::DHUD_DEFIBS <- 0;
if (!("DHUD_PILLS" in getroottable())) ::DHUD_PILLS <- 0;
if (!("DHUD_ADRENALINE" in getroottable())) ::DHUD_ADRENALINE <- 0;
if (!("DHUD_SUPPLIES" in getroottable())) ::DHUD_SUPPLIES <- 0;
if (!("DHUD_COMMON_KILLS" in getroottable())) ::DHUD_COMMON_KILLS <- 0;
if (!("DHUD_SPECIAL_KILLS" in getroottable())) ::DHUD_SPECIAL_KILLS <- 0;
if (!("DHUD_WITCH_KILLS" in getroottable())) ::DHUD_WITCH_KILLS <- 0;
if (!("DHUD_TANK_KILLS" in getroottable())) ::DHUD_TANK_KILLS <- 0;
if (!("DHUD_PROTECTS" in getroottable())) ::DHUD_PROTECTS <- 0;
if (!("DHUD_DAMAGE_TAKEN" in getroottable())) ::DHUD_DAMAGE_TAKEN <- 0;
if (!("DHUD_DAMAGE_DONE" in getroottable())) ::DHUD_DAMAGE_DONE <- 0;
if (!("DHUD_LEDGE_GRABS" in getroottable())) ::DHUD_LEDGE_GRABS <- 0;
if (!("DHUD_LAST" in getroottable())) ::DHUD_LAST <- "Round started";
if (!("DHUD_EVENTS_SEEN" in getroottable())) ::DHUD_EVENTS_SEEN <- 0;
if (!("DHUD_ACTION_SEEN" in getroottable())) ::DHUD_ACTION_SEEN <- {};
if (!("DHUD_LAST_HEAL_TIME" in getroottable())) ::DHUD_LAST_HEAL_TIME <- -100.0;
if (!("DHUD_LAST_SUPPLY_TIME" in getroottable())) ::DHUD_LAST_SUPPLY_TIME <- -100.0;
if (!("DHUD_LAST_INCAP_TIME" in getroottable())) ::DHUD_LAST_INCAP_TIME <- -100.0;
if (!("DHUD_LAST_DEATH_TIME" in getroottable())) ::DHUD_LAST_DEATH_TIME <- -100.0;
if (!("DHUD_LAST_LEDGE_TIME" in getroottable())) ::DHUD_LAST_LEDGE_TIME <- -100.0;
if (!("DHUD_DAMAGE_SCORE_STEP" in getroottable())) ::DHUD_DAMAGE_SCORE_STEP <- 200;
if (!("DHUD_DAMAGE_SCORE_BANK" in getroottable())) ::DHUD_DAMAGE_SCORE_BANK <- 0;
if (!("DHUD_PENDING_SPECIAL_COMMON_SUPPRESS" in getroottable())) ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS <- 0;
if (!("DHUD_LAST_DAMAGE_DONE_TIME" in getroottable())) ::DHUD_LAST_DAMAGE_DONE_TIME <- -100.0;
if (!("DHUD_LAST_DAMAGE_TAKEN_TIME" in getroottable())) ::DHUD_LAST_DAMAGE_TAKEN_TIME <- -100.0;
if (!("DHUD_POLL_ENEMY_HP" in getroottable())) ::DHUD_POLL_ENEMY_HP <- {};
if (!("DHUD_POLL_KILL_PROPS_ONLY" in getroottable())) ::DHUD_POLL_KILL_PROPS_ONLY <- {};
if (!("DHUD_DEBUG_LAST_EVENT" in getroottable())) ::DHUD_DEBUG_LAST_EVENT <- "";
if (!("DHUD_DEBUG_LAST_SCORE_EVENT" in getroottable())) ::DHUD_DEBUG_LAST_SCORE_EVENT <- "";
if (!("DHUD_LAST_LOCAL_ATTACK_TIME" in getroottable())) ::DHUD_LAST_LOCAL_ATTACK_TIME <- -100.0;
if (!("DHUD_LAST_GIVEN_TO_TRACKED_TIME" in getroottable())) ::DHUD_LAST_GIVEN_TO_TRACKED_TIME <- -100.0;
if (!("DHUD_ATTACK_FALLBACK_SUPPRESS_UNTIL" in getroottable())) ::DHUD_ATTACK_FALLBACK_SUPPRESS_UNTIL <- -100.0;
if (!("DHUD_HEALING_SUPPRESS_UNTIL" in getroottable())) ::DHUD_HEALING_SUPPRESS_UNTIL <- -100.0;
if (!("DHUD_TRACKED_DAMAGE_TARGETS" in getroottable())) ::DHUD_TRACKED_DAMAGE_TARGETS <- {};
if (!("DHUD_TRACKED_DAMAGE_KINDS" in getroottable())) ::DHUD_TRACKED_DAMAGE_KINDS <- {};
if (!("DHUD_TRACKED_DAMAGE_AMOUNTS" in getroottable())) ::DHUD_TRACKED_DAMAGE_AMOUNTS <- {};
if (!("DHUD_LAST_PROTECT_TIME" in getroottable())) ::DHUD_LAST_PROTECT_TIME <- -100.0;
if (!("DHUD_POLL_KILL_SEEN" in getroottable())) ::DHUD_POLL_KILL_SEEN <- {};

if (!("DHUD_EVENT_REAL_SEEN" in getroottable())) ::DHUD_EVENT_REAL_SEEN <- 0;
if (!("DHUD_LAST_REAL_EVENT_TIME" in getroottable())) ::DHUD_LAST_REAL_EVENT_TIME <- 0.0;
if (!("DHUD_LAST_SCORE_CHANGE_TIME" in getroottable())) ::DHUD_LAST_SCORE_CHANGE_TIME <- 0.0;
if (!("DHUD_SCORE_ACTIVITY_COUNT" in getroottable())) ::DHUD_SCORE_ACTIVITY_COUNT <- 0;
if (!("DHUD_SCORE_POLL_INIT" in getroottable())) ::DHUD_SCORE_POLL_INIT <- false;
if (!("DHUD_SCORE_POLL_LAST" in getroottable())) ::DHUD_SCORE_POLL_LAST <- 0.0;
if (!("DHUD_SCORE_POLL_BASE_TIME" in getroottable())) ::DHUD_SCORE_POLL_BASE_TIME <- 0.0;
if (!("DHUD_POLL_HP" in getroottable())) ::DHUD_POLL_HP <- -1;
if (!("DHUD_POLL_INCAP" in getroottable())) ::DHUD_POLL_INCAP <- false;
if (!("DHUD_POLL_LEDGE" in getroottable())) ::DHUD_POLL_LEDGE <- false;
if (!("DHUD_POLL_DEAD" in getroottable())) ::DHUD_POLL_DEAD <- false;
if (!("DHUD_POLL_INV_SIG" in getroottable())) ::DHUD_POLL_INV_SIG <- "";
if (!("DHUD_POLL_INV_SLOTS" in getroottable())) ::DHUD_POLL_INV_SLOTS <- {};
if (!("DHUD_LAST_INV_SCORE_TIME" in getroottable())) ::DHUD_LAST_INV_SCORE_TIME <- -100.0;
if (!("DHUD_LAST_SLOT_SCORE_TIME" in getroottable())) ::DHUD_LAST_SLOT_SCORE_TIME <- {};
if (!("DHUD_POLL_STATS" in getroottable())) ::DHUD_POLL_STATS <- {};
if (!("DHUD_POLL_TEAM_ALIVE" in getroottable())) ::DHUD_POLL_TEAM_ALIVE <- -1;
if (!("DHUD_POLL_TEAM_INCAP" in getroottable())) ::DHUD_POLL_TEAM_INCAP <- -1;
if (!("DHUD_POLL_TEAM_DEAD" in getroottable())) ::DHUD_POLL_TEAM_DEAD <- -1;
if (!("DHUD_POLL_TEAM_HP" in getroottable())) ::DHUD_POLL_TEAM_HP <- -1;
if (!("DHUD_POLL_STAT_MANAGER" in getroottable())) ::DHUD_POLL_STAT_MANAGER <- null;
if (!("DHUD_LISTEN_EVENTS_REGISTERED" in getroottable())) ::DHUD_LISTEN_EVENTS_REGISTERED <- false;
if (!("DHUD_LISTEN_CALLBACKS" in getroottable())) ::DHUD_LISTEN_CALLBACKS <- [];
if (!("DHUD_TRACK_USERID" in getroottable())) ::DHUD_TRACK_USERID <- -1;
if (!("DHUD_TRACK_INDEX" in getroottable())) ::DHUD_TRACK_INDEX <- -1;
if (!("DHUD_TRACK_NAME" in getroottable())) ::DHUD_TRACK_NAME <- "";
if (!("DHUD_TRACK_LOCKED" in getroottable())) ::DHUD_TRACK_LOCKED <- false;
if (!("DHUD_TRACK_DEAD_LOCK" in getroottable())) ::DHUD_TRACK_DEAD_LOCK <- false;
if (!("DHUD_RECENT_INV_SIGS" in getroottable())) ::DHUD_RECENT_INV_SIGS <- {};
if (!("DHUD_SKIP_STAT_COMMON" in getroottable())) ::DHUD_SKIP_STAT_COMMON <- 0;
if (!("DHUD_SKIP_STAT_SPECIAL" in getroottable())) ::DHUD_SKIP_STAT_SPECIAL <- 0;
if (!("DHUD_SKIP_STAT_REVIVE" in getroottable())) ::DHUD_SKIP_STAT_REVIVE <- 0;
if (!("DHUD_SKIP_STAT_HEAL" in getroottable())) ::DHUD_SKIP_STAT_HEAL <- 0;
if (!("DHUD_SKIP_STAT_PILLS" in getroottable())) ::DHUD_SKIP_STAT_PILLS <- 0;
if (!("DHUD_SKIP_STAT_ADRENALINE" in getroottable())) ::DHUD_SKIP_STAT_ADRENALINE <- 0;
if (!("DHUD_LAST_USE_BUTTON_TIME" in getroottable())) ::DHUD_LAST_USE_BUTTON_TIME <- -100.0;
if (!("DHUD_LAST_SUPPLY_BLOCK_TIME" in getroottable())) ::DHUD_LAST_SUPPLY_BLOCK_TIME <- -100.0;
if (!("DHUD_PRESERVE_NEXT_ROUND" in getroottable())) ::DHUD_PRESERVE_NEXT_ROUND <- false;
if (!("DHUD_SCORE_SESSION_STARTED" in getroottable())) ::DHUD_SCORE_SESSION_STARTED <- false;
if (!("DHUD_SCORE_STATE_LOADED" in getroottable())) ::DHUD_SCORE_STATE_LOADED <- false;
if (!("DHUD_LAST_BOSS_KILL_TIME" in getroottable())) ::DHUD_LAST_BOSS_KILL_TIME <- -100.0;
if (!("DHUD_LAST_WITCH_KILL_TIME" in getroottable())) ::DHUD_LAST_WITCH_KILL_TIME <- -100.0;
if (!("DHUD_LAST_TANK_KILL_TIME" in getroottable())) ::DHUD_LAST_TANK_KILL_TIME <- -100.0;
if (!("DHUD_LAST_WITCH_HURT_TIME" in getroottable())) ::DHUD_LAST_WITCH_HURT_TIME <- -100.0;
if (!("DHUD_LAST_TANK_HURT_TIME" in getroottable())) ::DHUD_LAST_TANK_HURT_TIME <- -100.0;
if (!("DHUD_LAST_WITCH_HURT_ACTOR" in getroottable())) ::DHUD_LAST_WITCH_HURT_ACTOR <- -1;
if (!("DHUD_LAST_TANK_HURT_ACTOR" in getroottable())) ::DHUD_LAST_TANK_HURT_ACTOR <- -1;
if (!("DHUD_LAST_DEFIB_BEGIN_TIME" in getroottable())) ::DHUD_LAST_DEFIB_BEGIN_TIME <- -100.0;
if (!("DHUD_LAST_DEFIB_BEGIN_ACTOR" in getroottable())) ::DHUD_LAST_DEFIB_BEGIN_ACTOR <- -1;
::DHUD_DAMAGE_SCORE_STEP = 200;

function DHUD_Now() { return Time(); }

function DHUD_DefaultScoreRule(key, fallback)
{
    if (key == "common") return 0.1;
    if (key == "special") return 1.5;
    if (key == "witch") return 3.0;
    if (key == "tank") return 5.0;
    if (key == "damage_done_step") return 200.0;
    if (key == "damage_done_score") return 0.1;
    if (key == "damage_taken_per10") return -1.0;
    if (key == "incap") return -10.0;
    if (key == "death") return -18.0;
    if (key == "ledge") return -6.0;
    if (key == "revive") return 5.0;
    if (key == "heal") return -3.0;
    if (key == "pills") return -1.5;
    if (key == "adrenaline") return -1.5;
    if (key == "supply_small") return -1.0;
    if (key == "supply_weapon") return -2.0;
    return fallback;
}

function DHUD_ParseScoreRulesLine(line)
{
    local parsed = {};
    if (line == null || line == "") return parsed;
    try
    {
        local parts = split(line, "|");
        foreach (part in parts)
        {
            local eq = part.find("=");
            if (eq == null) continue;
            local key = part.slice(0, eq);
            local val = part.slice(eq + 1);
            if (key == "" || key == "DHUD_SCORE_RULES") continue;
            try { parsed[key] <- val.tofloat(); } catch(e_val) {}
        }
    }
    catch(e) {}
    return parsed;
}

function DHUD_LoadScoreRules(force = false)
{
    local now = DHUD_Now();
    if (!force && now - ::DHUD_SCORE_RULES_LAST_LOAD < 0.90) return;
    ::DHUD_SCORE_RULES_LAST_LOAD = now;
    local line = null;
    try { line = FileToString(::DHUD_RULE_FILE2); } catch(e) { line = null; }
    if (line == null || line == "") { try { line = FileToString(::DHUD_RULE_FILE); } catch(e2) { line = null; } }
    if (line != null && line != "") ::DHUD_SCORE_RULES = DHUD_ParseScoreRulesLine(line);
}

function DHUD_Rule(key, fallback)
{
    try { DHUD_LoadScoreRules(false); } catch(e_load_rule) {}
    try { if (key in ::DHUD_SCORE_RULES) return ::DHUD_SCORE_RULES[key].tofloat(); } catch(e_rule) {}
    return DHUD_DefaultScoreRule(key, fallback);
}

function DHUD_RuleInt(key, fallback)
{
    local v = fallback;
    try { v = DHUD_Rule(key, fallback).tointeger(); } catch(e_int_rule) { v = fallback; }
    if (v < 1) v = fallback;
    return v;
}

function DHUD_Escape(s)
{
    if (s == null) return "";
    local out = s.tostring();
    try { out = out.gsub("|", "/"); } catch(e) {}
    try { out = out.gsub(";", ","); } catch(e) {}
    try { out = out.gsub("=", ":"); } catch(e) {}
    return out;
}

function DHUD_Fmt1(v)
{
    try { return format("%.1f", v.tofloat()); } catch(e) {}
    try { return v.tostring(); } catch(e2) {}
    return "0.0";
}

function DHUD_Length2D(v)
{
    try { return sqrt(v.x * v.x + v.y * v.y); } catch(e) {}
    return 0.0;
}

function DHUD_Velocity(ent)
{
    try { return ent.GetVelocity(); } catch(e) {}
    try { return NetProps.GetPropVector(ent, "m_vecVelocity"); } catch(e) {}
    try { return NetProps.GetPropVector(ent, "m_vecAbsVelocity"); } catch(e2) {}
    return Vector(0, 0, 0);
}

function DHUD_Health(ent)
{
    local hp = 0;
    try { hp = NetProps.GetPropInt(ent, "m_iHealth"); } catch(e) {}
    if (hp <= 0) { try { hp = ent.GetHealth(); } catch(e2) {} }
    return hp;
}

function DHUD_SurvivorHealth(ent)
{
    local hp = DHUD_Health(ent);
    if (hp < 0) hp = 0;
    local temp = 0.0;
    try
    {
        local buffer = NetProps.GetPropFloat(ent, "m_healthBuffer");
        local bufferTime = NetProps.GetPropFloat(ent, "m_healthBufferTime");
        local decay = 0.27;
        try { decay = Convars.GetFloat("pain_pills_decay_rate"); } catch(e2) {}
        temp = buffer - ((DHUD_Now() - bufferTime) * decay);
        if (temp < 0.0) temp = 0.0;
    }
    catch(e) {}
    return (hp + temp).tointeger();
}

function DHUD_MaxHealth(ent, fallback)
{
    try
    {
        local mx = NetProps.GetPropInt(ent, "m_iMaxHealth");
        if (mx > 0) return mx;
    }
    catch(e) {}
    return fallback;
}

function DHUD_UserPlayer(uid)
{
    try { return GetPlayerFromUserID(uid); } catch(e) {}
    return null;
}

function DHUD_EntityIndex(ent)
{
    try { return ent.GetEntityIndex(); } catch(e) {}
    return -1;
}

function DHUD_EntityByIndex(idx)
{
    try
    {
        if (idx == null) return null;
        local n = idx.tointeger();
        if (n < 0) return null;
        try
        {
            local e = EntIndexToHScript(n);
            if (e != null) return e;
        }
        catch(e0) {}
        try
        {
            local e2 = Entities.GetByIndex(n);
            if (e2 != null) return e2;
        }
        catch(e1) {}
    }
    catch(e2) {}
    return null;
}

function DHUD_SameEntity(a, b)
{
    if (a == null || b == null) return false;
    try { if (a == b) return true; } catch(e) {}
    local ia = DHUD_EntityIndex(a);
    local ib = DHUD_EntityIndex(b);
    return ia >= 0 && ia == ib;
}

function DHUD_IsSurvivor(ent)
{
    if (ent == null) return false;
    try { return ent.IsValid() && ent.IsSurvivor(); } catch(e) {}
    return false;
}

function DHUD_IsAliveSurvivor(ent)
{
    if (!DHUD_IsSurvivor(ent)) return false;
    try { if (ent.IsDead()) return false; } catch(e) {}
    return true;
}

function DHUD_IsIncap(ent)
{
    try { return NetProps.GetPropInt(ent, "m_isIncapacitated") > 0; } catch(e) {}
    return false;
}

function DHUD_IsHuman(ent)
{
    if (ent == null) return false;
    try { if (ent.IsBot()) return false; } catch(e) {}
    return true;
}


function DHUD_HostPlayer()
{
    local h = null;
    try { h = GetListenServerHost(); } catch(e0) { h = null; }
    if (h != null)
    {
        try
        {
            if (h.IsValid() && h.IsSurvivor() && DHUD_IsHuman(h)) return h;
        }
        catch(e1) {}
    }
    return null;
}

function DHUD_LockTrackedPlayer(ent)
{
    if (ent == null) return null;
    try { if (!ent.IsValid()) return null; } catch(e0) { return null; }
    try { if (!ent.IsSurvivor()) return null; } catch(e1) { return null; }
    if (!DHUD_IsHuman(ent)) return null;

    ::DHUD_TRACK_LOCKED = true;
    ::DHUD_TRACK_INDEX = DHUD_EntityIndex(ent);
    try { ::DHUD_TRACK_USERID = ent.GetPlayerUserId(); } catch(e2) { ::DHUD_TRACK_USERID = -1; }
    try { ::DHUD_TRACK_NAME = ent.GetPlayerName(); } catch(e3) { ::DHUD_TRACK_NAME = ""; }
    return ent;
}

function DHUD_FindHumanSurvivor(includeDead = true)
{
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try
        {
            if (!ent.IsValid()) continue;
            if (!ent.IsSurvivor()) continue;
            if (!includeDead && ent.IsDead()) continue;
            if (!DHUD_IsHuman(ent)) continue;
            return ent;
        }
        catch(e) {}
    }
    return null;
}

function DHUD_TrimString(s)
{
    if (s == null) return "";
    local out = s.tostring();
    try
    {
        while (out.len() > 0)
        {
            local c = out.slice(0, 1);
            if (c == " " || c == "\n" || c == "\r" || c == "\t") out = out.slice(1);
            else break;
        }
        while (out.len() > 0)
        {
            local c2 = out.slice(out.len() - 1, out.len());
            if (c2 == " " || c2 == "\n" || c2 == "\r" || c2 == "\t") out = out.slice(0, out.len() - 1);
            else break;
        }
    }
    catch(e) {}
    return out;
}

function DHUD_TargetSpec()
{
    local s = null;
    try { s = FileToString(::DHUD_TARGET_FILE2); } catch(e) { s = null; }
    if (s == null || s == "") { try { s = FileToString(::DHUD_TARGET_FILE); } catch(e2) { s = null; } }
    return DHUD_TrimString(s);
}

function DHUD_TargetMatches(ent, spec)
{
    if (ent == null || spec == null || spec == "") return false;
    local low = spec.tolower();
    try
    {
        local uid = ent.GetPlayerUserId();
        if (uid.tostring() == spec) return true;
    }
    catch(e_uid) {}
    try
    {
        local nm = ent.GetPlayerName();
        if (nm != null)
        {
            local nml = nm.tolower();
            if (nml == low) return true;
            if (nml.find(low) != null) return true;
        }
    }
    catch(e_name) {}
    return false;
}

function DHUD_FindTargetHumanSurvivor(includeDead = true)
{
    local spec = DHUD_TargetSpec();
    if (spec == null || spec == "") return null;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try
        {
            if (!ent.IsValid()) continue;
            if (!ent.IsSurvivor()) continue;
            if (!includeDead && ent.IsDead()) continue;
            if (!DHUD_IsHuman(ent)) continue;
            if (DHUD_TargetMatches(ent, spec)) return ent;
        }
        catch(e) {}
    }
    return null;
}

function DHUD_TrackedPlayer(create = true)
{
    local target = DHUD_FindTargetHumanSurvivor(true);
    local host = DHUD_HostPlayer();
    local preferred = (target != null) ? target : host;
    if (preferred != null)
    {
        if (!::DHUD_TRACK_LOCKED || !DHUD_SameEntity(preferred, DHUD_ResolveTrackedEntityRaw()))
        {
            if (!::DHUD_TRACK_DEAD_LOCK) return DHUD_LockTrackedPlayer(preferred);
        }
    }

    local ent = null;
    if (::DHUD_TRACK_LOCKED)
    {
        ent = DHUD_ResolveTrackedEntityRaw();
        if (ent != null) return ent;
        if (!create || ::DHUD_TRACK_DEAD_LOCK) return null;
        ::DHUD_TRACK_LOCKED = false;
    }

    if (!create) return null;
    ent = preferred;
    if (ent == null) ent = DHUD_FindHumanSurvivor(false);
    if (ent == null) ent = DHUD_FindHumanSurvivor(true);
    if (ent != null) return DHUD_LockTrackedPlayer(ent);
    return null;
}

function DHUD_ResolveTrackedEntityRaw()
{
    local ent = null;
    if (::DHUD_TRACK_USERID >= 0)
    {
        ent = DHUD_UserPlayer(::DHUD_TRACK_USERID);
        try { if (ent != null && ent.IsValid()) return ent; } catch(e_uid) {}
    }
    if (::DHUD_TRACK_INDEX >= 0)
    {
        try { ent = EntIndexToHScript(::DHUD_TRACK_INDEX); if (ent != null && ent.IsValid()) return ent; } catch(e_idx) {}
        try { ent = Entities.GetByIndex(::DHUD_TRACK_INDEX); if (ent != null && ent.IsValid()) return ent; } catch(e_idx2) {}
    }
    return null;
}
function DHUD_Player()
{
    local ent = DHUD_TrackedPlayer(true);
    if (ent != null && DHUD_IsAliveSurvivor(ent)) return ent;
    return null;
}

function DHUD_IsTracked(ent)
{
    if (ent == null) return false;
    return DHUD_SameEntity(ent, DHUD_TrackedPlayer(true));
}

function DHUD_ScorePlayer()
{
    return DHUD_TrackedPlayer(true);
}

function DHUD_ScoringActive()
{
    local ent = DHUD_TrackedPlayer(false);
    if (ent == null) ent = DHUD_TrackedPlayer(true);
    if (ent == null) return false;
    if (!DHUD_IsAliveSurvivor(ent)) return false;
    return true;
}

function DHUD_IsDeadSafe(ent)
{
    if (ent == null) return false;
    try { return ent.IsDead(); } catch(e) {}
    return false;
}

function DHUD_IsLedge(ent)
{
    if (ent == null) return false;
    try { return NetProps.GetPropInt(ent, "m_isHangingFromLedge") > 0; } catch(e) {}
    try { return NetProps.GetPropInt(ent, "m_isHangingFromLedge") == 1; } catch(e2) {}
    return false;
}

function DHUD_UsePollScoring()
{
    try
    {
        if (::DHUD_SCORE_ACTIVITY_COUNT <= 0) return true;
        return (DHUD_Now() - ::DHUD_LAST_SCORE_CHANGE_TIME) > 0.80;
    }
    catch(e) {}
    return true;
}

function DHUD_InventorySignature(ent)
{
    if (ent == null) return "";
    local inv = {};
    try { GetInvTable(ent, inv); } catch(e) { return ""; }
    local sig = "";
    for (local i = 0; i < 8; i++)
    {
        local k = "slot" + i;
        try
        {
            if (k in inv && inv[k] != null)
            {
                local w = inv[k];
                local cn = "";
                try { cn = w.GetClassname(); } catch(e2) { cn = "weapon"; }
                sig += k + ":" + cn + ";";
            }
        }
        catch(e3) {}
    }
    return sig;
}

function DHUD_InventorySlots(ent)
{
    local slots = {};
    if (ent == null) return slots;
    local inv = {};
    try { GetInvTable(ent, inv); } catch(e) { return slots; }
    for (local i = 0; i < 8; i++)
    {
        local k = "slot" + i;
        local cn = "";
        try
        {
            if (k in inv && inv[k] != null)
            {
                try { cn = inv[k].GetClassname(); } catch(e2) { cn = "weapon"; }
            }
        }
        catch(e3) { cn = ""; }
        slots[k] <- cn;
    }
    return slots;
}

function DHUD_InventoryChangedItem(oldSlots, newSlots)
{
    local bestSlot = "";
    local bestItem = "";
    try
    {
        for (local i = 0; i < 8; i++)
        {
            local k = "slot" + i;
            local oldv = "";
            local newv = "";
            try { if (k in oldSlots) oldv = oldSlots[k]; } catch(e1) {}
            try { if (k in newSlots) newv = newSlots[k]; } catch(e2) {}
            if (oldv != newv && newv != "")
            {
                bestSlot = k;
                bestItem = newv;
                if (k == "slot3" || k == "slot4" || k == "slot2") return [bestSlot, bestItem];
            }
        }
    }
    catch(e) {}
    if (bestItem == "") return null;
    return [bestSlot, bestItem];
}

function DHUD_TeamHealthSum()
{
    local sum = 0;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try
        {
            if (!DHUD_IsAliveSurvivor(ent)) continue;
            sum += DHUD_SurvivorHealth(ent);
        }
        catch(e) {}
    }
    return sum;
}

function DHUD_FindStatManager()
{
    try
    {
        if (::DHUD_POLL_STAT_MANAGER != null && ::DHUD_POLL_STAT_MANAGER.IsValid()) return ::DHUD_POLL_STAT_MANAGER;
    }
    catch(e) {}

    local names = ["terror_player_manager", "cs_player_manager", "player_manager"];
    foreach (cn in names)
    {
        try
        {
            local m = Entities.FindByClassname(null, cn);
            if (m != null)
            {
                ::DHUD_POLL_STAT_MANAGER = m;
                return m;
            }
        }
        catch(e2) {}
    }
    return null;
}

function DHUD_ReadStatArray(ent, names)
{
    if (ent == null) return -1;
    local mgr = DHUD_FindStatManager();
    if (mgr == null) return -1;

    local idx = DHUD_EntityIndex(ent);
    local candidates = [];
    if (idx >= 0)
    {
        candidates.push(idx);
        if (idx > 0) candidates.push(idx - 1);
    }
    try
    {
        local uid = ent.GetPlayerUserId();
        if (uid >= 0) candidates.push(uid);
    }
    catch(e_uid) {}
    try
    {
        local ch = NetProps.GetPropInt(ent, "m_survivorCharacter");
        if (ch >= 0) candidates.push(ch);
    }
    catch(e_ch) {}
    foreach (prop in names)
    {
        foreach (i in candidates)
        {
            try
            {
                local v = NetProps.GetPropIntArray(mgr, prop, i);
                if (v >= 0) return v;
            }
            catch(e) {}
            try
            {
                local v2 = NetProps.GetPropFloatArray(mgr, prop, i).tointeger();
                if (v2 >= 0) return v2;
            }
            catch(e2) {}
        }
    }
    return -1;
}

function DHUD_ReadEntIntArray(ent, prop, idx)
{
    if (ent == null) return -1;
    try
    {
        local v = NetProps.GetPropIntArray(ent, prop, idx);
        if (v >= 0) return v;
    }
    catch(e) {}
    try
    {
        local vf = NetProps.GetPropFloatArray(ent, prop, idx).tointeger();
        if (vf >= 0) return vf;
    }
    catch(e2) {}
    return -1;
}

function DHUD_ReadZombieKillBucket(ent, bucket)
{
    local props = ["m_checkpointZombieKills", "m_missionZombieKills"];
    local best = -1;
    local seen = false;
    foreach (prop in props)
    {
        local sum = 0;
        local ok = false;
        if (bucket == "common")
        {
            local v = DHUD_ReadEntIntArray(ent, prop, 0);
            if (v >= 0) { sum += v; ok = true; }
        }
        else if (bucket == "special")
        {
            for (local i = 1; i <= 6; i++)
            {
                local v2 = DHUD_ReadEntIntArray(ent, prop, i);
                if (v2 >= 0) { sum += v2; ok = true; }
            }
        }
        else if (bucket == "tank")
        {
            local v3 = DHUD_ReadEntIntArray(ent, prop, 8);
            if (v3 >= 0) { sum += v3; ok = true; }
        }
        if (ok)
        {
            if (sum > best) best = sum;
            seen = true;
        }
    }
    if (!seen) return -1;
    return best;
}

function DHUD_PollZombieKillDelta(ent, bucket)
{
    local v = DHUD_ReadZombieKillBucket(ent, bucket);
    if (v < 0)
    {
        if (bucket == "common") return DHUD_PollStatDelta(ent, "common_legacy", ["m_checkpointZombieKills", "m_missionZombieKills", "m_iZombieKills", "m_zombieKills"]);
        if (bucket == "special") return DHUD_PollStatDelta(ent, "special_legacy", ["m_checkpointSpecialKills", "m_missionSpecialKills", "m_iSpecialKills", "m_specialKills", "m_specialKillsTotal"]);
        if (bucket == "tank") return DHUD_PollStatDelta(ent, "tank_legacy", ["m_checkpointTankKills", "m_missionTankKills", "m_tankKills"]);
        return 0;
    }
    local key = "zk_" + bucket;
    try
    {
        if (!(key in ::DHUD_POLL_STATS))
        {
            ::DHUD_POLL_STATS[key] <- v;
            return 0;
        }
        local old = ::DHUD_POLL_STATS[key];
        ::DHUD_POLL_STATS[key] = v;
        local d = v - old;
        if (d < 0) d = 0;
        return d;
    }
    catch(e) {}
    return 0;
}

function DHUD_CallStatMethod(ent, names)
{
    if (ent == null) return -1;
    foreach (name in names)
    {
        try
        {
            local fn = ent[name];
            local v = fn.call(ent);
            if (v != null && v.tointeger() >= 0) return v.tointeger();
        }
        catch(e) {}
    }
    return -1;
}

function DHUD_ReadStatAny(ent, names)
{
    if (ent == null) return -1;

    foreach (prop in names)
    {
        try
        {
            local v = NetProps.GetPropInt(ent, prop);
            if (v >= 0) return v;
        }
        catch(e) {}
        try
        {
            local vf = NetProps.GetPropFloat(ent, prop).tointeger();
            if (vf >= 0) return vf;
        }
        catch(e2) {}
    }

    local arr = DHUD_ReadStatArray(ent, names);
    if (arr >= 0) return arr;

    local methods = [];
    foreach (prop2 in names)
    {
        methods.push(prop2);
        try
        {
            if (prop2.len() > 2 && prop2.slice(0, 2) == "m_") methods.push("Get" + prop2.slice(2));
        }
        catch(e3) {}
    }
    return DHUD_CallStatMethod(ent, methods);
}

function DHUD_PollStatDelta(ent, key, names)
{
    local v = DHUD_ReadStatAny(ent, names);
    if (v < 0) return 0;
    try
    {
        if (!(key in ::DHUD_POLL_STATS))
        {
            ::DHUD_POLL_STATS[key] <- v;
            return 0;
        }
        local old = ::DHUD_POLL_STATS[key];
        ::DHUD_POLL_STATS[key] = v;
        local d = v - old;
        if (d < 0) d = 0;
        return d;
    }
    catch(e2) {}
    return 0;
}

function DHUD_ReadDamageStat(ent)
{
    local total = DHUD_ReadStatAny(ent, ["m_checkpointDamageDone", "m_missionDamageDone", "m_iDamageDone", "m_damageDone", "m_totalDamageDone", "m_checkpointDamage", "m_missionDamage"]);
    if (total >= 0) return total;

    local sum = 0;
    local seen = false;
    local parts = [
        ["m_checkpointDamageToTank", "m_missionDamageToTank", "m_iTankDamage", "m_tankDamage"],
        ["m_checkpointDamageToWitch", "m_missionDamageToWitch", "m_iWitchDamage", "m_witchDamage"],
        ["m_checkpointDamageToSpecial", "m_missionDamageToSpecial", "m_iSpecialDamage", "m_specialDamage"],
        ["m_checkpointMeleeDamage", "m_missionMeleeDamage"]
    ];
    foreach (arr in parts)
    {
        local v = DHUD_ReadStatAny(ent, arr);
        if (v >= 0)
        {
            sum += v;
            seen = true;
        }
    }
    if (seen) return sum;
    return -1;
}

function DHUD_PollDamageDelta(ent)
{
    local v = DHUD_ReadDamageStat(ent);
    if (v < 0) return 0;
    try
    {
        if (!("damage_done" in ::DHUD_POLL_STATS))
        {
            ::DHUD_POLL_STATS["damage_done"] <- v;
            return 0;
        }
        local old = ::DHUD_POLL_STATS["damage_done"];
        ::DHUD_POLL_STATS["damage_done"] = v;
        local d = v - old;
        if (d < 0) d = 0;
        return d;
    }
    catch(e) {}
    return 0;
}



function DHUD_ReadEntPropIntOnly(ent, names)
{
    if (ent == null) return -1;
    foreach (prop in names)
    {
        try
        {
            local v = NetProps.GetPropInt(ent, prop);
            if (v >= 0) return v;
        }
        catch(e) {}
        try
        {
            local vf = NetProps.GetPropFloat(ent, prop).tointeger();
            if (vf >= 0) return vf;
        }
        catch(e2) {}
    }
    return -1;
}

function DHUD_PollEntPropDelta(ent, key, names, cap = 8)
{
    local v = DHUD_ReadEntPropIntOnly(ent, names);
    if (v < 0) return 0;
    try
    {
        local k = "prop_" + key;
        if (!(k in ::DHUD_POLL_KILL_PROPS_ONLY))
        {
            ::DHUD_POLL_KILL_PROPS_ONLY[k] <- v;
            return 0;
        }
        local old = ::DHUD_POLL_KILL_PROPS_ONLY[k];
        ::DHUD_POLL_KILL_PROPS_ONLY[k] = v;
        local d = v - old;
        if (d < 0) d = 0;
        if (cap > 0 && d > cap) d = cap;
        return d;
    }
    catch(e) {}
    return 0;
}



function DHUD_AttackFallbackSuppressed()
{
    try { return DHUD_Now() < ::DHUD_ATTACK_FALLBACK_SUPPRESS_UNTIL; } catch(e) {}
    return false;
}

function DHUD_SuppressAttackFallback(seconds = 5.0, reason = "")
{
    local until = DHUD_Now() + seconds;
    try
    {
        if (until > ::DHUD_ATTACK_FALLBACK_SUPPRESS_UNTIL) ::DHUD_ATTACK_FALLBACK_SUPPRESS_UNTIL = until;
        if (until > ::DHUD_HEALING_SUPPRESS_UNTIL) ::DHUD_HEALING_SUPPRESS_UNTIL = until;
        ::DHUD_LAST_LOCAL_ATTACK_TIME = -100.0;
        if (reason != "") DHUD_Remember(reason);
    }
    catch(e) {}
}

function DHUD_IsLikelyTrackedTarget(tracked, ent, localAttacking)
{
    if (!localAttacking || tracked == null || ent == null) return false;
    if (DHUD_AttackFallbackSuppressed()) return false;
    local veryRecentFire = DHUD_RecentLocalAttack(0.24);
    local pressingAttack = DHUD_IsUseOrAttackPressed(tracked);
    if (!veryRecentFire && !pressingAttack) return false;

    try
    {
        local start = tracked.EyePosition();
        local target = ent.GetOrigin();
        try { target = ent.EyePosition(); } catch(e_eye_target) {}
        local delta = target - start;
        local dist = delta.Length();
        if (dist < 130.0) return true;
        if (dist > ::DHUD_MAX_DIST) return false;
        delta.Norm();
        local fwd = tracked.EyeAngles().Forward();
        local dot = delta.Dot(fwd);
        if (dist < 360.0 && dot > 0.70) return true;
        if (dist < 850.0 && dot > 0.84) return true;
        return dot > 0.91;
    }
    catch(e)
    {
        return veryRecentFire || pressingAttack;
    }
}


function DHUD_ScanEnemyForPoll(ent, defaultKind, tracked, origin, current, localAttacking, now)
{
    if (ent == null || DHUD_IsSurvivor(ent)) return;
    local idx = DHUD_EntityIndex(ent);
    if (idx < 0) return;
    local hp = DHUD_Health(ent);
    local maxhp = DHUD_MaxHealth(ent, hp);
    if (maxhp < hp) maxhp = hp;
    local kind = defaultKind;
    try
    {
        local cn = ent.GetClassname();
        if (cn == "witch") kind = "witch";
        else if (cn == "infected") kind = "common";
        else if (cn == "player" && !ent.IsSurvivor())
        {
            local zt = DHUD_ZombieType(ent);
            if (zt == 8) kind = "tank";
            else if (zt >= 1 && zt <= 6) kind = "special";
        }
    }
    catch(ek) {}

    local old = null;
    try { if (idx in ::DHUD_POLL_ENEMY_HP) old = ::DHUD_POLL_ENEMY_HP[idx]; } catch(e_old_lookup) {}
    local oldOwned = DHUD_RecentTrackedDamageIndex(idx, 4.00);
    try { if (old != null && ("owned" in old) && old.owned) oldOwned = true; } catch(e_old_owned) {}

    local likelyLocal = DHUD_IsLikelyTrackedTarget(tracked, ent, localAttacking);
    if (hp <= 0)
    {
        if (oldOwned)
        {
            local leftHp = 0;
            local maxLeft = maxhp;
            try { if (old != null) leftHp = old.hp; } catch(e_left_hp) {}
            try { if (old != null && ("maxhp" in old)) maxLeft = old.maxhp; } catch(e_left_max) {}
            if (leftHp > 0) DHUD_AddTrackedDamageForIndex(idx, kind, leftHp, "Damage dealt", maxLeft);
            DHUD_AddPolledEnemyKill(idx, kind, "Poll enemy dead");
        }
        return;
    }

    local ownedNow = oldOwned;
    if ((kind == "special" || kind == "witch" || kind == "tank") && likelyLocal && localAttacking)
    {
        ownedNow = true;
        DHUD_MarkTrackedDamageTarget(ent, kind);
    }
    current[idx] <- { hp = hp, maxhp = maxhp, kind = kind, seen = now, aimed = likelyLocal, owned = ownedNow };

    try
    {
        if (old != null)
        {
            local oldhp = old.hp;
            local drop = oldhp - hp;
            if (drop > 0 && likelyLocal)
            {
                // 计分板复用血量 HUD 的实体扫描，按真实血量下降累计伤害，避免秒杀 Tank / Witch 时只记录零碎事件伤害。
                // The score board reuses the health HUD entity scan and accumulates real HP drops, preventing one-shot Tank / Witch kills from being counted as only small event damage.
                if (kind == "special" || kind == "witch" || kind == "tank")
                {
                    DHUD_MarkTrackedDamageTarget(ent, kind);
                    current[idx].owned = true;
                    try { ::DHUD_DEBUG_LAST_SCORE_EVENT = "Tracked enemy HP drop " + kind + " -" + drop; } catch(e_dbg_drop) {}
                }

                if (!DHUD_UseStrictAttribution() || kind == "special" || kind == "witch" || kind == "tank" || DHUD_RecentTrackedDamageTo(ent, 1.20))
                {
                    DHUD_AddTrackedDamageForIndex(idx, kind, drop, "Damage dealt", maxhp);
                }
            }
        }
    }
    catch(eold) {}
}




function DHUD_TrackEnemyDamageAndDeaths()
{
    local p = DHUD_TrackedPlayer(false);
    if (p == null) return;
    local now = DHUD_Now();
    DHUD_CleanupTrackedDamageTargets();
    local origin = null;
    try { origin = p.GetOrigin(); } catch(e_origin) { origin = null; }
    local current = {};
    local localAttacking = DHUD_RecentLocalAttack(0.85) || DHUD_IsUseOrAttackPressed(p);
    local strict = DHUD_UseStrictAttribution();

    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null) DHUD_ScanEnemyForPoll(ent, "special", p, origin, current, localAttacking, now);
    ent = null;
    while ((ent = Entities.FindByClassname(ent, "witch")) != null) DHUD_ScanEnemyForPoll(ent, "witch", p, origin, current, localAttacking, now);
    ent = null;
    local commonScan = 0;
    while ((ent = Entities.FindByClassname(ent, "infected")) != null)
    {
        DHUD_ScanEnemyForPoll(ent, "common", p, origin, current, localAttacking, now);
        commonScan += 1;
        if (commonScan >= 96) break;
    }

    try
    {
        foreach (idx, old in ::DHUD_POLL_ENEMY_HP)
        {
            if (idx in current) continue;
            local kindGone = "";
            local seenGone = now;
            local ownedGone = DHUD_RecentTrackedDamageIndex(idx, 4.00);
            try { kindGone = old.kind; } catch(e_kind_gone) {}
            try { seenGone = old.seen; } catch(e_seen_gone) {}
            try { if (("owned" in old) && old.owned) ownedGone = true; } catch(e_owned_gone) {}
            if (kindGone == "common" || kindGone == "") continue;
            if (now - seenGone > 1.60) continue;
            if (ownedGone)
            {
                local leftHp = 0;
                local maxLeft = 0;
                try { leftHp = old.hp; } catch(e_left_gone) {}
                try { maxLeft = old.maxhp; } catch(e_max_gone) {}
                if (leftHp > 0) DHUD_AddTrackedDamageForIndex(idx, kindGone, leftHp, "Damage dealt", maxLeft);
                DHUD_AddPolledEnemyKill(idx, kindGone, "Poll enemy gone");
            }
        }
    }
    catch(e_gone_poll) {}

    ::DHUD_POLL_ENEMY_HP = current;
}




function DHUD_AddSelfHealHP(amount, reason)
{
    if (amount < 1) return;
    if (amount > 100) amount = 100;
    ::DHUD_HEAL_HP_SELF += amount;
    ::DHUD_LAST_HEAL_HP_TIME = DHUD_Now();
    DHUD_Remember(reason + " +" + amount + " HP");
}

function DHUD_ResetPollBaseline(ent)
{
    ::DHUD_SCORE_POLL_INIT = true;
    ::DHUD_SCORE_POLL_BASE_TIME = DHUD_Now();
    ::DHUD_POLL_HP = DHUD_SurvivorHealth(ent);
    ::DHUD_POLL_INCAP = DHUD_IsIncap(ent);
    ::DHUD_POLL_LEDGE = DHUD_IsLedge(ent);
    ::DHUD_POLL_DEAD = DHUD_IsDeadSafe(ent);
    ::DHUD_POLL_INV_SIG = DHUD_InventorySignature(ent);
    ::DHUD_POLL_INV_SLOTS = DHUD_InventorySlots(ent);
    ::DHUD_POLL_TEAM_ALIVE = DHUD_TeamAlive();
    ::DHUD_POLL_TEAM_INCAP = DHUD_TeamIncap();
    ::DHUD_POLL_TEAM_DEAD = DHUD_TeamDead();
    ::DHUD_POLL_TEAM_HP = DHUD_TeamHealthSum();
    ::DHUD_POLL_STATS = {};
    DHUD_PollStatDelta(ent, "revives", ["m_checkpointReviveOtherCount", "m_missionReviveOtherCount", "m_checkpointRevives", "m_iRevives", "m_reviveOtherCount"]);
    DHUD_PollStatDelta(ent, "heals", ["m_checkpointMedkitsUsed", "m_missionMedkitsUsed", "m_checkpointFirstAidShared", "m_missionFirstAidShared", "m_checkpointFirstAidUsed", "m_iFirstAidUsed", "m_firstAidUsed"]);
    DHUD_PollStatDelta(ent, "pills", ["m_checkpointPillsUsed", "m_missionPillsUsed", "m_iPillsUsed", "m_pillsUsed"]);
    DHUD_PollStatDelta(ent, "adr", ["m_checkpointAdrenalinesUsed", "m_missionAdrenalinesUsed", "m_iAdrenalineUsed", "m_adrenalinesUsed"]);
    DHUD_PollDamageDelta(ent);
    try { ::DHUD_POLL_ENEMY_HP = {}; ::DHUD_TRACKED_DAMAGE_AMOUNTS = {}; DHUD_TrackEnemyDamageAndDeaths(); } catch(e_enemy_base) {}
    try { ::DHUD_POLL_KILL_PROPS_ONLY = {}; DHUD_PollEntPropDelta(ent, "common_scalar", ["m_checkpointZombieKills", "m_missionZombieKills"], 8); } catch(e_prop_base) {}
}


function DHUD_ScorePoll()
{
    local now = DHUD_Now();
    if (now < ::DHUD_SCORE_POLL_LAST + 0.04) return;
    ::DHUD_SCORE_POLL_LAST = now;

    local p = DHUD_ScorePlayer();
    if (p == null)
    {
        ::DHUD_SCORE_POLL_INIT = false;
        return;
    }

    if (!DHUD_IsAliveSurvivor(p))
    {
        local deadNow = DHUD_IsDeadSafe(p);
        if (::DHUD_SCORE_POLL_INIT && deadNow && !::DHUD_POLL_DEAD) DHUD_RecordPersonalDeath("You died -18");
        ::DHUD_POLL_DEAD = deadNow;
        ::DHUD_TRACK_DEAD_LOCK = deadNow;
        ::DHUD_POLL_HP = 0;
        return;
    }

    if (!::DHUD_SCORE_POLL_INIT)
    {
        DHUD_ResetPollBaseline(p);
        return;
    }

    local hp = DHUD_SurvivorHealth(p);
    local incap = DHUD_IsIncap(p);
    local ledge = DHUD_IsLedge(p);
    local dead = DHUD_IsDeadSafe(p);
    local invSig = DHUD_InventorySignature(p);
    if (DHUD_IsUseOrAttackPressed(p)) { ::DHUD_LAST_USE_BUTTON_TIME = now; if (!DHUD_AttackFallbackSuppressed()) DHUD_MarkLocalAttack(); }
    local fallback = DHUD_UsePollScoring();
    local teamAlive = DHUD_TeamAlive();
    local teamIncap = DHUD_TeamIncap();
    local teamDead = DHUD_TeamDead();
    local teamHp = DHUD_TeamHealthSum();

    try { DHUD_TrackEnemyDamageAndDeaths(); } catch(e_enemy_poll) {}

    if (incap && !::DHUD_POLL_INCAP) DHUD_RecordPersonalIncap("Incapacitated " + DHUD_Fmt1(DHUD_Rule("incap", -10.0)));
    if (ledge && !::DHUD_POLL_LEDGE) DHUD_RecordPersonalLedge("Ledge grab -6");
    if (dead && !::DHUD_POLL_DEAD) DHUD_RecordPersonalDeath("You died -18");

    if (fallback)
    {
        if (::DHUD_POLL_TEAM_INCAP >= 0)
        {
            local dIncap = teamIncap - ::DHUD_POLL_TEAM_INCAP;
            if (dIncap > 0) DHUD_Remember("Team incapacitated");
            else if (dIncap < 0) DHUD_Remember("Team revived");
        }
        if (::DHUD_POLL_TEAM_DEAD >= 0)
        {
            local dDead = teamDead - ::DHUD_POLL_TEAM_DEAD;
            if (dDead > 0) DHUD_Remember("Team death");
            else if (dDead < 0)
            {
            }
        }
        if (::DHUD_POLL_TEAM_HP >= 0 && teamHp >= 0)
        {
            local dTeamHp = teamHp - ::DHUD_POLL_TEAM_HP;
            if (dTeamHp <= -15) DHUD_Remember("Team HP changed " + dTeamHp);
            else if (dTeamHp >= 20) DHUD_Remember("Team healed +" + dTeamHp);
        }
    }

    if (invSig != "" && invSig != ::DHUD_POLL_INV_SIG && now > ::DHUD_SCORE_POLL_BASE_TIME + 2.0)
    {
        local newSlots = DHUD_InventorySlots(p);
        local changed = DHUD_InventoryChangedItem(::DHUD_POLL_INV_SLOTS, newSlots);
        if (changed != null && DHUD_HasRecentManualSupplyAction(p) && now - ::DHUD_LAST_GIVEN_TO_TRACKED_TIME > 1.0)
        {
            local item = changed[1];
            if (now - ::DHUD_LAST_INV_SCORE_TIME > 0.20)
            {
                ::DHUD_LAST_INV_SCORE_TIME = now;
                DHUD_AddSupplyScore(item, "Inventory pickup", DHUD_SupplyScore(item, "Inventory pickup"));
            }
        }
        else
        {
            if (now - ::DHUD_LAST_SUPPLY_BLOCK_TIME > 1.2)
            {
                ::DHUD_LAST_SUPPLY_BLOCK_TIME = now;
                DHUD_Remember("Inventory changed");
            }
        }
        ::DHUD_POLL_INV_SLOTS = newSlots;
    }

    local justRevived = (!incap && ::DHUD_POLL_INCAP && !dead);
    if (justRevived)
    {
        ::DHUD_RESCUED_BY_TEAM += 1;
        DHUD_Remember("Revived by teammate");
        ::DHUD_POLL_HP = hp;
    }

    if (!incap && !::DHUD_POLL_INCAP && !dead && !justRevived && hp > 0 && ::DHUD_POLL_HP > 0)
    {
        local diff = hp - ::DHUD_POLL_HP;
        if (diff <= -2 && !dead)
        {
            DHUD_RecordSelfHealthDrop(p, "Damage taken");
        }
        else if (diff >= 8 && !dead)
        {
            if (DHUD_Now() - ::DHUD_LAST_HEAL_HP_TIME > 3.5) DHUD_AddSelfHealHP(diff, "Self restored");
            else DHUD_Remember("Healing +" + diff);
        }
    }

    local dc = DHUD_PollEntPropDelta(p, "common_scalar", ["m_checkpointZombieKills", "m_missionZombieKills"], 8);
    // 特感击杀不再读取统计属性，避免 BOT / 旧章节 / 团队统计被误算。
    // Special kills no longer use stat polling to avoid bot, stale chapter, or team-stat overcount.
    local ds = 0;
    // Tank 击杀只走明确事件或本人伤害兜底，不走统计属性。
    // Tank kills only use explicit events or tracked-damage fallback, not stat polling.
    local dtankpoll = 0;
    local dr = DHUD_PollStatDelta(p, "revives", ["m_checkpointReviveOtherCount", "m_missionReviveOtherCount", "m_checkpointRevives", "m_iRevives", "m_reviveOtherCount"]);
    local dh = DHUD_PollStatDelta(p, "heals", ["m_checkpointMedkitsUsed", "m_missionMedkitsUsed", "m_checkpointFirstAidShared", "m_missionFirstAidShared", "m_checkpointFirstAidUsed", "m_iFirstAidUsed", "m_firstAidUsed"]);
    local dp = DHUD_PollStatDelta(p, "pills", ["m_checkpointPillsUsed", "m_missionPillsUsed", "m_iPillsUsed", "m_pillsUsed"]);
    local da = DHUD_PollStatDelta(p, "adr", ["m_checkpointAdrenalinesUsed", "m_missionAdrenalinesUsed", "m_iAdrenalineUsed", "m_adrenalinesUsed"]);
    local dprot = 0;

    if (::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS > 0 && dc > 0)
    {
        local cut = dc;
        if (cut > ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS) cut = ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS;
        dc -= cut;
        ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS -= cut;
        if (::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS < 0) ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS = 0;
    }

    if (dc > 0 && ::DHUD_SKIP_STAT_COMMON > 0) { local cutc = dc; if (cutc > ::DHUD_SKIP_STAT_COMMON) cutc = ::DHUD_SKIP_STAT_COMMON; dc -= cutc; ::DHUD_SKIP_STAT_COMMON -= cutc; }
    if (ds > 0 && ::DHUD_SKIP_STAT_SPECIAL > 0) { local cuts = ds; if (cuts > ::DHUD_SKIP_STAT_SPECIAL) cuts = ::DHUD_SKIP_STAT_SPECIAL; ds -= cuts; ::DHUD_SKIP_STAT_SPECIAL -= cuts; }
    if (dr > 0 && ::DHUD_SKIP_STAT_REVIVE > 0) { local cutr = dr; if (cutr > ::DHUD_SKIP_STAT_REVIVE) cutr = ::DHUD_SKIP_STAT_REVIVE; dr -= cutr; ::DHUD_SKIP_STAT_REVIVE -= cutr; }
    if (dh > 0 && ::DHUD_SKIP_STAT_HEAL > 0) { local cuth = dh; if (cuth > ::DHUD_SKIP_STAT_HEAL) cuth = ::DHUD_SKIP_STAT_HEAL; dh -= cuth; ::DHUD_SKIP_STAT_HEAL -= cuth; }
    if (dp > 0 && ::DHUD_SKIP_STAT_PILLS > 0) { local cutp = dp; if (cutp > ::DHUD_SKIP_STAT_PILLS) cutp = ::DHUD_SKIP_STAT_PILLS; dp -= cutp; ::DHUD_SKIP_STAT_PILLS -= cutp; }
    if (da > 0 && ::DHUD_SKIP_STAT_ADRENALINE > 0) { local cuta = da; if (cuta > ::DHUD_SKIP_STAT_ADRENALINE) cuta = ::DHUD_SKIP_STAT_ADRENALINE; da -= cuta; ::DHUD_SKIP_STAT_ADRENALINE -= cuta; }

    if (dc > 0)
    {
        ::DHUD_COMMON_KILLS += dc;
        local cadd = DHUD_Rule("common", 0.1) * dc;
        DHUD_ScoreDelta(cadd, "Common infected +" + dc + " / score " + DHUD_Fmt1(cadd));
    }
    if (ds > 0)
    {
        ::DHUD_SPECIAL_KILLS += ds;
        local add = ds * DHUD_Rule("special", 1.5);
        DHUD_ScoreDelta(add, "Special infected +" + ds + " / score +" + DHUD_Fmt1(add));
    }
    if (dtankpoll > 0)
    {
        ::DHUD_TANK_KILLS += dtankpoll;
        local tadd = dtankpoll * DHUD_Rule("tank", 5.0);
        DHUD_ScoreDelta(tadd, "Tank killed +" + dtankpoll + " / score +" + DHUD_Fmt1(tadd));
    }
    if (dr > 0)
    {
        ::DHUD_REVIVES += dr;
        local radd = DHUD_Rule("revive", 5.0) * dr;
        DHUD_ScoreDelta(radd, "Revive success " + DHUD_Fmt1(radd));
    }
    if (dh > 0)
    {
        if (DHUD_Now() - ::DHUD_LAST_HEAL_TIME > 3.0)
        {
            ::DHUD_HEALS += dh;
            ::DHUD_LAST_HEAL_TIME = DHUD_Now();
            local healhp = 0;
            if (::DHUD_POLL_HP > 0 && hp > ::DHUD_POLL_HP) healhp = hp - ::DHUD_POLL_HP;
            else if (::DHUD_POLL_HP > 0)
            {
                local missing = DHUD_MaxHealth(p, 100) - ::DHUD_POLL_HP;
                if (missing < 0) missing = 0;
                healhp = missing;
            }
            if (healhp <= 0) healhp = 1;
            if (healhp > 100) healhp = 100;
            DHUD_AddSelfHealHP(healhp, "First aid restored");
            local hadd = DHUD_Rule("heal", -3.0) * dh;
            DHUD_ScoreDelta(hadd, "First aid used +" + healhp + " HP / score " + DHUD_Fmt1(hadd));
        }
        else DHUD_Remember("First aid already counted");
    }
    if (dp > 0)
    {
        ::DHUD_PILLS += dp;
        ::DHUD_HEALS += dp;
        DHUD_AddSelfHealHP(20 * dp, "Pills temp HP");
        local padd = DHUD_Rule("pills", -1.5) * dp;
        DHUD_ScoreDelta(padd, "Pills used " + dp + " / score " + DHUD_Fmt1(padd));
    }
    if (da > 0)
    {
        ::DHUD_ADRENALINE += da;
        ::DHUD_HEALS += da;
        DHUD_AddSelfHealHP(25 * da, "Adrenaline temp HP");
        local aadd = DHUD_Rule("adrenaline", -1.5) * da;
        DHUD_ScoreDelta(aadd, "Adrenaline used " + da + " / score " + DHUD_Fmt1(aadd));
    }

    ::DHUD_POLL_HP = hp;
    ::DHUD_POLL_INCAP = incap;
    ::DHUD_POLL_LEDGE = ledge;
    ::DHUD_POLL_DEAD = dead;
    ::DHUD_POLL_INV_SIG = invSig;
    try { ::DHUD_POLL_INV_SLOTS = DHUD_InventorySlots(p); } catch(e_slots_end) {}
    ::DHUD_POLL_TEAM_ALIVE = teamAlive;
    ::DHUD_POLL_TEAM_INCAP = teamIncap;
    ::DHUD_POLL_TEAM_DEAD = teamDead;
    ::DHUD_POLL_TEAM_HP = teamHp;
}


function DHUD_EventRaw(params, key)
{
    try { return params[key]; } catch(e) {}
    return null;
}

function DHUD_EventText(params, key, fallback = "")
{
    local v = DHUD_EventRaw(params, key);
    if (v == null) return fallback;
    try { return DHUD_Escape(v.tostring()); } catch(e) {}
    return fallback;
}

function DHUD_EntityFromParam(params, key)
{
    local v = DHUD_EventRaw(params, key);
    if (v == null) return null;
    local idx = -1;
    try { idx = v.tointeger(); } catch(e) { return null; }
    try
    {
        local ent = EntIndexToHScript(idx);
        if (ent != null) return ent;
    }
    catch(e2) {}
    try
    {
        local ent2 = Entities.GetByIndex(idx);
        if (ent2 != null) return ent2;
    }
    catch(e3) {}
    return null;
}

function DHUD_EventPlayer(params, key)
{
    local v = DHUD_EventRaw(params, key);
    if (v == null) return null;
    local n = -1;
    try { n = v.tointeger(); } catch(e) { return null; }

    local preferEntity = false;
    try
    {
        if (key == "entityid" || key == "entindex" || key == "attackerentid" || key == "attackerentindex" || key == "tankid" || key == "witchid") preferEntity = true;
    }
    catch(e_key) {}

    local ent = null;
    try { ent = DHUD_EntityFromParam(params, key); } catch(e_ent0) { ent = null; }

    if (preferEntity && ent != null)
    {
        try { if (ent.GetClassname() == "player") return ent; } catch(e_ent) {}
    }

    local p = DHUD_UserPlayer(n);

    if (ent != null)
    {
        try
        {
            if (ent.GetClassname() == "player" && DHUD_IsTracked(ent)) return ent;
        }
        catch(e_tracked_ent) {}
    }

    if (p != null) return p;

    if (ent != null)
    {
        try { if (ent.GetClassname() == "player") return ent; } catch(e2) {}
    }
    return null;
}

function DHUD_EventPlayerAny(params, keys)
{
    foreach (k in keys)
    {
        local p = DHUD_EventPlayer(params, k);
        if (p != null) return p;
    }
    return null;
}

function DHUD_ParamMatchesTracked(params, keys)
{
    local tracked = DHUD_TrackedPlayer(true);
    if (tracked == null) return false;
    local tidx = DHUD_EntityIndex(tracked);
    local tuid = -1;
    try { tuid = tracked.GetPlayerUserId(); } catch(e_uid) {}
    foreach (k in keys)
    {
        local raw = DHUD_EventRaw(params, k);
        if (raw == null) continue;
        local n = -999999;
        local hasInt = false;
        try { n = raw.tointeger(); hasInt = true; } catch(e_int) {}
        if (hasInt)
        {
            if (tuid >= 0 && n == tuid) return true;
            if (tidx >= 0 && n == tidx) return true;
        }
        local p = DHUD_EventPlayer(params, k);
        if (DHUD_SameEntity(p, tracked)) return true;
    }
    return false;
}

function DHUD_EventPlayerTrackedFirst(params, keys)
{
    if (DHUD_ParamMatchesTracked(params, keys)) return DHUD_TrackedPlayer(true);
    return DHUD_EventPlayerAny(params, keys);
}

function DHUD_TrackedEntityFromParams(params, keys)
{
    if (DHUD_ParamMatchesTracked(params, keys)) return DHUD_TrackedPlayer(true);
    return DHUD_EventEntityAny(params, keys);
}


function DHUD_EventEntityAny(params, keys)
{
    foreach (k in keys)
    {
        local p = DHUD_EventPlayer(params, k);
        if (p != null) return p;
        local ent = DHUD_EntityFromParam(params, k);
        if (ent != null) return ent;
    }
    return null;
}

function DHUD_EventHasKey(params, key)
{
    try { local v = params[key]; return true; } catch(e) {}
    return false;
}

function DHUD_ActionDedupe(tag, params, cooldown)
{
    if (!("DHUD_ACTION_SEEN" in getroottable())) ::DHUD_ACTION_SEEN <- {};
    local now = DHUD_Now();
    local key = tag;
    local keys = ["userid", "player", "player_userid", "attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "victim", "subject", "target", "entityid", "entindex", "infected_id", "weapon", "item", "type", "zombieclass"];
    foreach (k in keys)
    {
        try { key += "|" + k + "=" + params[k]; } catch(e) {}
    }
    try
    {
        if (key in ::DHUD_ACTION_SEEN && now - ::DHUD_ACTION_SEEN[key] < cooldown) return true;
        ::DHUD_ACTION_SEEN[key] <- now;
        foreach (oldk, oldt in ::DHUD_ACTION_SEEN)
        {
            if (now - oldt > 4.0) delete ::DHUD_ACTION_SEEN[oldk];
        }
    }
    catch(e2) {}
    return false;
}

function DHUD_IncScoreOnly(delta, statName, reason)
{
    DHUD_ScoreDelta(delta, reason);
}

function DHUD_EventInt(params, key, fallback)
{
    try { return params[key].tointeger(); } catch(e) {}
    return fallback;
}

function DHUD_ZombieType(ent)
{
    try { return ent.GetZombieType(); } catch(e) {}
    return -1;
}

function DHUD_Name(ent)
{
    local cn = "";
    try { cn = ent.GetClassname(); } catch(e) {}
    if (cn == "player")
    {
        try { if (ent.IsSurvivor()) return DHUD_Escape(ent.GetPlayerName()); } catch(e2) {}
        try { return DHUD_Escape(ent.GetZombieType().tostring()); } catch(e3) {}
        return "infected";
    }
    if (cn == "witch") return "Witch";
    if (cn == "infected") return "Common";
    return DHUD_Escape(cn);
}

function DHUD_AddEnemy(out, ent, origin, fallbackMax)
{
    if (ent == null) return;
    local hp = DHUD_Health(ent);
    if (hp <= 0) return;

    local maxhp = DHUD_MaxHealth(ent, fallbackMax);
    if (maxhp < hp) maxhp = hp;

    local dist = 0.0;
    try { dist = (ent.GetOrigin() - origin).Length(); } catch(e) {}
    if (dist > ::DHUD_MAX_DIST) return;

    out.push(DHUD_Name(ent) + "," + hp + "," + maxhp + "," + dist.tointeger());
}

function DHUD_EnemyList(player)
{
    local out = [];
    if (player == null) return "";
    local origin = player.GetOrigin();

    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try
        {
            if (!ent.IsValid()) continue;
            if (ent.IsSurvivor()) continue;
            if (ent.IsDead()) continue;
            DHUD_AddEnemy(out, ent, origin, 250);
        }
        catch(e) {}
        if (out.len() >= 8) break;
    }

    ent = null;
    while ((ent = Entities.FindByClassname(ent, "witch")) != null)
    {
        try
        {
            if (!ent.IsValid()) continue;
            DHUD_AddEnemy(out, ent, origin, 1000);
        }
        catch(e) {}
        if (out.len() >= 8) break;
    }

    if (out.len() <= 0) return "";
    local s = out[0];
    for (local i = 1; i < out.len(); i++) s += ";" + out[i];
    return s;
}


function DHUD_DebugEventLine(name, params)
{
    local keys = ["userid", "player", "player_userid", "attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "victim", "victim_userid", "subject", "target", "entityid", "entindex", "infected_id", "tankid", "witchid", "dmg_health", "damage", "amount", "dmg", "health", "type", "zombieclass", "zombie_class", "weapon", "item", "giver", "giver_userid", "giveruserid", "donor", "receiver", "recipient", "source"];
    local line = name;
    foreach (k in keys)
    {
        try
        {
            local v = params[k];
            if (v != null) line += " " + k + "=" + DHUD_Escape(v.tostring());
        }
        catch(e) {}
    }
    try
    {
        local p = DHUD_TrackedPlayer(false);
        if (p != null)
        {
            line += " tracked_idx=" + DHUD_EntityIndex(p);
            try { line += " tracked_uid=" + p.GetPlayerUserId(); } catch(e_uid) {}
            try { line += " tracked=" + DHUD_Escape(p.GetPlayerName()); } catch(e_nm) {}
        }
    }
    catch(e2) {}
    if (line.len() > 220) line = line.slice(0, 220);
    return line;
}

function DHUD_DebugEvent(name, params)
{
    try
    {
        ::DHUD_DEBUG_LAST_EVENT = DHUD_DebugEventLine(name, params);
        if (name != "round_start" && name != "player_spawn" && name != "revive_begin" && name != "heal_begin")
        {
            printl("[DHUD-EVENT] " + ::DHUD_DEBUG_LAST_EVENT);
        }
    }
    catch(e) {}
}

function DHUD_DebugScore(reason)
{
    try
    {
        ::DHUD_DEBUG_LAST_SCORE_EVENT = reason + " | " + ::DHUD_DEBUG_LAST_EVENT;
        if (::DHUD_DEBUG_LAST_SCORE_EVENT.len() > 240) ::DHUD_DEBUG_LAST_SCORE_EVENT = ::DHUD_DEBUG_LAST_SCORE_EVENT.slice(0, 240);
    }
    catch(e) {}
}

function DHUD_MarkLocalAttack()
{
    try { if (!DHUD_AttackFallbackSuppressed()) ::DHUD_LAST_LOCAL_ATTACK_TIME = DHUD_Now(); } catch(e) {}
}

function DHUD_RecentLocalAttack(window = 0.90)
{
    try { if (DHUD_AttackFallbackSuppressed()) return false; } catch(e0) {}
    try { return (DHUD_Now() - ::DHUD_LAST_LOCAL_ATTACK_TIME) <= window; } catch(e) {}
    return false;
}

function DHUD_MarkScoreActivity()
{
    try
    {
        ::DHUD_LAST_SCORE_CHANGE_TIME = DHUD_Now();
        ::DHUD_SCORE_ACTIVITY_COUNT += 1;
    }
    catch(e) {}
}

function DHUD_ScoreDelta(delta, reason)
{
    try { delta = delta.tofloat(); } catch(e_delta) {}
    ::DHUD_SCORE = ::DHUD_SCORE.tofloat() + delta;
    if (::DHUD_SCORE > 100.0) ::DHUD_SCORE = 100.0;
    if (::DHUD_SCORE < 0.0) ::DHUD_SCORE = 0.0;
    ::DHUD_LAST = reason;
    DHUD_DebugScore(reason);
    DHUD_MarkScoreActivity();
    try { DHUD_SaveScoreState(); } catch(e_save_score) {}
}

function DHUD_Remember(reason)
{
    ::DHUD_LAST = reason;
    DHUD_DebugScore(reason);
    DHUD_MarkScoreActivity();
    try { DHUD_SaveScoreState(); } catch(e_save_remember) {}
}

function DHUD_RecordPersonalIncap(reason)
{
    local now = DHUD_Now();
    if (now - ::DHUD_LAST_INCAP_TIME < 2.50) return;
    ::DHUD_LAST_INCAP_TIME = now;
    ::DHUD_INCAPPED += 1;
    DHUD_ScoreDelta(DHUD_Rule("incap", -10.0), reason);
}

function DHUD_RecordPersonalDeath(reason)
{
    local now = DHUD_Now();
    if (now - ::DHUD_LAST_DEATH_TIME < 2.50) return;
    ::DHUD_LAST_DEATH_TIME = now;
    ::DHUD_DEATHS += 1;
    DHUD_ScoreDelta(DHUD_Rule("death", -18.0), reason);
}

function DHUD_RecordPersonalLedge(reason)
{
    local now = DHUD_Now();
    if (now - ::DHUD_LAST_LEDGE_TIME < 2.00) return;
    ::DHUD_LAST_LEDGE_TIME = now;
    ::DHUD_LEDGE_GRABS += 1;
    DHUD_ScoreDelta(DHUD_Rule("ledge", -6.0), reason);
}

function DHUD_AddDamageDone(dmg, reason)
{
    if (dmg < 1) return;
    ::DHUD_DAMAGE_DONE += dmg;
    local step = DHUD_RuleInt("damage_done_step", 200);
    local stepScore = DHUD_Rule("damage_done_score", 0.1);
    ::DHUD_DAMAGE_SCORE_STEP = step;
    ::DHUD_DAMAGE_SCORE_BANK += dmg;
    ::DHUD_LAST_DAMAGE_DONE_TIME = DHUD_Now();

    local addScore = 0.0;
    while (::DHUD_DAMAGE_SCORE_BANK >= step)
    {
        ::DHUD_DAMAGE_SCORE_BANK -= step;
        addScore += stepScore;
    }

    if (addScore != 0.0) DHUD_ScoreDelta(addScore, reason + " +" + dmg + " / total " + ::DHUD_DAMAGE_DONE + " / " + DHUD_Fmt1(stepScore) + " per " + step + " dmg");
    else DHUD_Remember(reason + " +" + dmg + " / total " + ::DHUD_DAMAGE_DONE);
}

function DHUD_AddSupplyScore(item, reason, delta)
{
    local low = item;
    try { low = low.tolower(); } catch(e_low_supply) {}
    if (DHUD_TextContains(low, "first_aid")) delta = DHUD_Rule("heal", -3.0);
    else if (DHUD_TextContains(low, "weapon") || DHUD_TextContains(low, "ammo")) delta = DHUD_Rule("supply_weapon", -2.0);
    else delta = DHUD_Rule("supply_small", delta == 0 ? -1.0 : delta);
    ::DHUD_SUPPLIES += 1;
    ::DHUD_LAST_SUPPLY_TIME = DHUD_Now();
    if (delta > 0) DHUD_ScoreDelta(delta, reason + " " + item + " +" + delta);
    else DHUD_ScoreDelta(delta, reason + " " + item + " " + delta);
}

function DHUD_ScoreLevel()
{
    if (::DHUD_SCORE >= 95) return "EX";
    if (::DHUD_SCORE >= 81) return "S";
    if (::DHUD_SCORE >= 71) return "A";
    if (::DHUD_SCORE >= 60) return "B";
    if (::DHUD_SCORE >= 50) return "C";
    return "D";
}

function DHUD_ScoreDesc()
{
    local lv = DHUD_ScoreLevel();
    if (lv == "EX") return "Iridescent";
    if (lv == "S") return "Red";
    if (lv == "A") return "Purple";
    if (lv == "B") return "Blue";
    if (lv == "C") return "Green";
    return "White";
}

function DHUD_TeamAlive()
{
    local n = 0;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try { if (ent.IsValid() && ent.IsSurvivor() && !ent.IsDead()) n++; } catch(e) {}
    }
    return n;
}

function DHUD_TeamIncap()
{
    local n = 0;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try { if (DHUD_IsAliveSurvivor(ent) && DHUD_IsIncap(ent)) n++; } catch(e) {}
    }
    return n;
}

function DHUD_TeamDead()
{
    local n = 0;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try { if (ent.IsValid() && ent.IsSurvivor() && ent.IsDead()) n++; } catch(e) {}
    }
    return n;
}

function DHUD_TeamAvgHP()
{
    local sum = 0;
    local n = 0;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try
        {
            if (!DHUD_IsAliveSurvivor(ent)) continue;
            sum += DHUD_SurvivorHealth(ent);
            n++;
        }
        catch(e) {}
    }
    if (n <= 0) return 0;
    return (sum / n).tointeger();
}


function DHUD_StateValue(line, key, fallback)
{
    try
    {
        local parts = split(line, "|");
        foreach (part in parts)
        {
            local eq = part.find("=");
            if (eq == null) continue;
            local k = part.slice(0, eq);
            if (k == key) return part.slice(eq + 1);
        }
    }
    catch(e) {}
    return fallback;
}

function DHUD_StateInt(line, key, fallback)
{
    try { return DHUD_StateValue(line, key, fallback).tointeger(); } catch(e) {}
    return fallback;
}


function DHUD_AddTrackedDamageForIndex(idx, kind, dmg, reason, maxTotal = 0)
{
    if (idx < 0 || dmg < 1) return;
    if (dmg > 20000) dmg = 20000;
    local already = 0;
    try { if (idx in ::DHUD_TRACKED_DAMAGE_AMOUNTS) already = ::DHUD_TRACKED_DAMAGE_AMOUNTS[idx]; } catch(e_already) {}
    if (maxTotal > 0)
    {
        local room = maxTotal - already;
        if (room <= 0) return;
        if (dmg > room) dmg = room;
    }
    if (dmg < 1) return;
    try { ::DHUD_TRACKED_DAMAGE_AMOUNTS[idx] <- already + dmg; } catch(e_store) {}
    DHUD_AddDamageDone(dmg, reason);
}

function DHUD_StateFloat(line, key, fallback)
{
    try { return DHUD_StateValue(line, key, fallback).tofloat(); } catch(e) {}
    return fallback;
}

function DHUD_CurrentMapName()
{
    local m = "";
    try { m = GetMapName(); if (m != null && m != "") return m.tolower(); } catch(e0) {}
    try { m = Director.GetMapName(); if (m != null && m != "") return m.tolower(); } catch(e1) {}
    try { m = Convars.GetStr("mapname"); if (m != null && m != "") return m.tolower(); } catch(e2) {}
    try { m = Convars.GetStr("host_map"); if (m != null && m != "") return m.tolower(); } catch(e3) {}
    return "unknown";
}

function DHUD_MapCampaignKey(map)
{
    try
    {
        if (map == null || map == "") return "unknown";
        local idx = map.find("m");
        if (idx != null && idx > 0) return map.slice(0, idx);
        local us = map.find("_");
        if (us != null && us > 0) return map.slice(0, us);
        return map;
    }
    catch(e) {}
    return "unknown";
}

function DHUD_MapChapterNumber(map)
{
    try
    {
        if (map == null || map == "") return -1;
        local idx = map.find("m");
        if (idx == null) return -1;
        local j = idx + 1;
        local digits = "";
        while (j < map.len())
        {
            local ch = map.slice(j, j + 1);
            if (ch < "0" || ch > "9") break;
            digits += ch;
            j += 1;
        }
        if (digits == "") return -1;
        return digits.tointeger();
    }
    catch(e) {}
    return -1;
}

function DHUD_StateCanCarry(line)
{
    local curMap = DHUD_CurrentMapName();
    local curCampaign = DHUD_MapCampaignKey(curMap);
    local curChapter = DHUD_MapChapterNumber(curMap);
    local oldMap = DHUD_StateValue(line, "map", "");
    local oldCampaign = DHUD_StateValue(line, "campaign", "");
    local oldChapter = DHUD_StateInt(line, "chapter", -1);
    local transition = DHUD_StateInt(line, "transition", 0);
    local stateVer = DHUD_StateInt(line, "state_ver", 0);
    // 只继承新版主动保存的过图状态，避免旧状态文件在新战役开局误导入。
    // Only carry new transition states to prevent stale files from being loaded at a fresh campaign start.
    if (stateVer != 2) return false;
    if (transition != 1) return false;
    if (oldCampaign == "" || oldCampaign == "unknown" || curCampaign == "unknown") return false;
    if (oldCampaign != curCampaign) return false;
    if (oldMap == curMap) return false;
    if (oldChapter >= 0 && curChapter >= 0 && curChapter <= oldChapter) return false;
    return true;
}

function DHUD_ClearScoreState()
{
    try { StringToFile(::DHUD_STATE_FILE2, "DHUD_SCORE_STATE|cleared=1|map=" + DHUD_CurrentMapName() + "|transition=0"); } catch(e) {}
    try { StringToFile(::DHUD_STATE_FILE, "DHUD_SCORE_STATE|cleared=1|map=" + DHUD_CurrentMapName() + "|transition=0"); } catch(e2) {}
}

function DHUD_SaveScoreState()
{
    local curMap = DHUD_CurrentMapName();
    local line = "DHUD_SCORE_STATE"
        + "|map=" + curMap
        + "|campaign=" + DHUD_MapCampaignKey(curMap)
        + "|chapter=" + DHUD_MapChapterNumber(curMap)
        + "|state_ver=2"
        + "|transition=" + (::DHUD_PRESERVE_NEXT_ROUND ? 1 : 0)
        + "|score=" + DHUD_Fmt1(::DHUD_SCORE)
        + "|ff=" + ::DHUD_FF
        + "|ff_damage=" + ::DHUD_FF_DAMAGE
        + "|incap=" + ::DHUD_INCAPPED
        + "|death=" + ::DHUD_DEATHS
        + "|revive=" + ::DHUD_REVIVES
        + "|rescued_by_team=" + ::DHUD_RESCUED_BY_TEAM
        + "|heals=" + ::DHUD_HEALS
        + "|heal_self=" + ::DHUD_HEAL_HP_SELF
        + "|heal_team=" + ::DHUD_HEAL_HP_TEAM
        + "|healed_by_team=" + ::DHUD_HEALED_BY_TEAM
        + "|defib=" + ::DHUD_DEFIBS
        + "|pills=" + ::DHUD_PILLS
        + "|adrenaline=" + ::DHUD_ADRENALINE
        + "|supply=" + ::DHUD_SUPPLIES
        + "|common=" + ::DHUD_COMMON_KILLS
        + "|special=" + ::DHUD_SPECIAL_KILLS
        + "|witch=" + ::DHUD_WITCH_KILLS
        + "|tank=" + ::DHUD_TANK_KILLS
        + "|damage_taken=" + ::DHUD_DAMAGE_TAKEN
        + "|damage_done=" + ::DHUD_DAMAGE_DONE
        + "|damage_bank=" + DHUD_Fmt1(::DHUD_DAMAGE_SCORE_BANK)
        + "|ledge=" + ::DHUD_LEDGE_GRABS
        + "|last=" + DHUD_Escape(::DHUD_LAST);
    try { StringToFile(::DHUD_STATE_FILE2, line); } catch(e) {}
    try { StringToFile(::DHUD_STATE_FILE, line); } catch(e2) {}
}

function DHUD_LoadScoreState()
{
    local line = null;
    try { line = FileToString(::DHUD_STATE_FILE2); } catch(e) { line = null; }
    if (line == null || line == "") { try { line = FileToString(::DHUD_STATE_FILE); } catch(e2) { line = null; } }
    if (line == null || line == "") return false;
    try { if (line.find("DHUD_SCORE_STATE") == null) return false; } catch(e3) { return false; }
    if (DHUD_StateInt(line, "cleared", 0) == 1) return false;
    if (!DHUD_StateCanCarry(line)) return false;

    ::DHUD_SCORE = DHUD_StateFloat(line, "score", 60.0);
    ::DHUD_FF = DHUD_StateInt(line, "ff", 0);
    ::DHUD_FF_DAMAGE = DHUD_StateInt(line, "ff_damage", 0);
    ::DHUD_INCAPPED = DHUD_StateInt(line, "incap", 0);
    ::DHUD_DEATHS = DHUD_StateInt(line, "death", 0);
    ::DHUD_REVIVES = DHUD_StateInt(line, "revive", 0);
    ::DHUD_RESCUED_BY_TEAM = DHUD_StateInt(line, "rescued_by_team", 0);
    ::DHUD_HEALS = DHUD_StateInt(line, "heals", 0);
    ::DHUD_HEAL_HP_SELF = DHUD_StateInt(line, "heal_self", 0);
    ::DHUD_HEAL_HP_TEAM = DHUD_StateInt(line, "heal_team", 0);
    ::DHUD_HEALED_BY_TEAM = DHUD_StateInt(line, "healed_by_team", 0);
    ::DHUD_DEFIBS = DHUD_StateInt(line, "defib", 0);
    ::DHUD_PILLS = DHUD_StateInt(line, "pills", 0);
    ::DHUD_ADRENALINE = DHUD_StateInt(line, "adrenaline", 0);
    ::DHUD_SUPPLIES = DHUD_StateInt(line, "supply", 0);
    ::DHUD_COMMON_KILLS = DHUD_StateInt(line, "common", 0);
    ::DHUD_SPECIAL_KILLS = DHUD_StateInt(line, "special", 0);
    ::DHUD_WITCH_KILLS = DHUD_StateInt(line, "witch", 0);
    ::DHUD_TANK_KILLS = DHUD_StateInt(line, "tank", 0);
    ::DHUD_DAMAGE_TAKEN = DHUD_StateInt(line, "damage_taken", 0);
    ::DHUD_DAMAGE_DONE = DHUD_StateInt(line, "damage_done", 0);
    ::DHUD_DAMAGE_SCORE_BANK = DHUD_StateFloat(line, "damage_bank", 0.0);
    ::DHUD_LEDGE_GRABS = DHUD_StateInt(line, "ledge", 0);
    ::DHUD_LAST = "Chapter started: score kept";
    ::DHUD_SCORE_SESSION_STARTED = true;
    ::DHUD_SCORE_STATE_LOADED = true;
    return true;
}

function DHUD_ResetRuntimeForNextChapter()
{
    ::DHUD_SCORE_POLL_INIT = false;
    ::DHUD_ACTION_SEEN = {};
    ::DHUD_LAST_HEAL_TIME = -100.0;
    ::DHUD_LAST_SUPPLY_TIME = -100.0;
    ::DHUD_LAST_INCAP_TIME = -100.0;
    ::DHUD_LAST_DEATH_TIME = -100.0;
    ::DHUD_LAST_LEDGE_TIME = -100.0;
    ::DHUD_LAST_DAMAGE_DONE_TIME = -100.0;
    ::DHUD_LAST_DAMAGE_TAKEN_TIME = -100.0;
    ::DHUD_POLL_ENEMY_HP = {};
    ::DHUD_TRACKED_DAMAGE_AMOUNTS = {};
    ::DHUD_POLL_KILL_PROPS_ONLY = {};
    ::DHUD_DEBUG_LAST_EVENT = "";
    ::DHUD_DEBUG_LAST_SCORE_EVENT = "";
    ::DHUD_LAST_LOCAL_ATTACK_TIME = -100.0;
    ::DHUD_LAST_GIVEN_TO_TRACKED_TIME = -100.0;
    ::DHUD_ATTACK_FALLBACK_SUPPRESS_UNTIL = -100.0;
    ::DHUD_HEALING_SUPPRESS_UNTIL = -100.0;
    ::DHUD_POLL_TEAM_ALIVE = -1;
    ::DHUD_POLL_TEAM_INCAP = -1;
    ::DHUD_POLL_TEAM_DEAD = -1;
    ::DHUD_POLL_TEAM_HP = -1;
    ::DHUD_POLL_STATS = {};
    ::DHUD_POLL_INV_SLOTS = {};
    ::DHUD_LAST_INV_SCORE_TIME = -100.0;
    ::DHUD_LAST_SLOT_SCORE_TIME = {};
    ::DHUD_TRACK_USERID = -1;
    ::DHUD_TRACK_INDEX = -1;
    ::DHUD_TRACK_NAME = "";
    ::DHUD_TRACK_LOCKED = false;
    ::DHUD_TRACK_DEAD_LOCK = false;
    ::DHUD_RECENT_INV_SIGS = {};
    ::DHUD_SKIP_STAT_COMMON = 0;
    ::DHUD_SKIP_STAT_SPECIAL = 0;
    ::DHUD_SKIP_STAT_REVIVE = 0;
    ::DHUD_SKIP_STAT_HEAL = 0;
    ::DHUD_SKIP_STAT_PILLS = 0;
    ::DHUD_SKIP_STAT_ADRENALINE = 0;
    ::DHUD_LAST_USE_BUTTON_TIME = -100.0;
    ::DHUD_LAST_SUPPLY_BLOCK_TIME = -100.0;
    ::DHUD_LAST_BOSS_KILL_TIME = -100.0;
    ::DHUD_LAST_WITCH_KILL_TIME = -100.0;
    ::DHUD_LAST_TANK_KILL_TIME = -100.0;
    ::DHUD_LAST_WITCH_HURT_TIME = -100.0;
    ::DHUD_LAST_TANK_HURT_TIME = -100.0;
    ::DHUD_LAST_WITCH_HURT_ACTOR = -1;
    ::DHUD_LAST_TANK_HURT_ACTOR = -1;
    ::DHUD_LAST = "Chapter started: score kept";
}

function DHUD_ResetScore()
{
    ::DHUD_SCORE_SESSION_STARTED = true;
    ::DHUD_SCORE = 60.0;
    ::DHUD_FF = 0;
    ::DHUD_FF_DAMAGE = 0;
    ::DHUD_INCAPPED = 0;
    ::DHUD_DEATHS = 0;
    ::DHUD_REVIVES = 0;
    ::DHUD_RESCUED_BY_TEAM = 0;
    ::DHUD_HEALS = 0;
    ::DHUD_HEAL_HP_SELF = 0;
    ::DHUD_HEAL_HP_TEAM = 0;
    ::DHUD_LAST_HEAL_HP_TIME = -100.0;
    ::DHUD_HEALED_BY_TEAM = 0;
    ::DHUD_DEFIBS = 0;
    ::DHUD_PILLS = 0;
    ::DHUD_ADRENALINE = 0;
    ::DHUD_SUPPLIES = 0;
    ::DHUD_COMMON_KILLS = 0;
    ::DHUD_SPECIAL_KILLS = 0;
    ::DHUD_WITCH_KILLS = 0;
    ::DHUD_TANK_KILLS = 0;
    ::DHUD_PROTECTS = 0;
    ::DHUD_DAMAGE_TAKEN = 0;
    ::DHUD_DAMAGE_DONE = 0;
    ::DHUD_LEDGE_GRABS = 0;
    ::DHUD_LAST = "Round started";
    ::DHUD_EVENT_REAL_SEEN = 0;
    ::DHUD_LAST_REAL_EVENT_TIME = 0.0;
    ::DHUD_LAST_SCORE_CHANGE_TIME = 0.0;
    ::DHUD_SCORE_ACTIVITY_COUNT = 0;
    ::DHUD_SCORE_POLL_INIT = false;
    ::DHUD_ACTION_SEEN = {};
    ::DHUD_LAST_HEAL_TIME = -100.0;
    ::DHUD_LAST_SUPPLY_TIME = -100.0;
    ::DHUD_LAST_INCAP_TIME = -100.0;
    ::DHUD_LAST_DEATH_TIME = -100.0;
    ::DHUD_LAST_LEDGE_TIME = -100.0;
    ::DHUD_DAMAGE_SCORE_BANK = 0;
    ::DHUD_DAMAGE_SCORE_STEP = 200;
    ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS = 0;
    ::DHUD_LAST_DAMAGE_DONE_TIME = -100.0;
    ::DHUD_LAST_DAMAGE_TAKEN_TIME = -100.0;
    ::DHUD_POLL_ENEMY_HP = {};
    ::DHUD_TRACKED_DAMAGE_AMOUNTS = {};
    ::DHUD_POLL_KILL_PROPS_ONLY = {};
    ::DHUD_DEBUG_LAST_EVENT = "";
    ::DHUD_DEBUG_LAST_SCORE_EVENT = "";
    ::DHUD_LAST_LOCAL_ATTACK_TIME = -100.0;
    ::DHUD_LAST_GIVEN_TO_TRACKED_TIME = -100.0;
    ::DHUD_ATTACK_FALLBACK_SUPPRESS_UNTIL = -100.0;
    ::DHUD_HEALING_SUPPRESS_UNTIL = -100.0;
    ::DHUD_POLL_TEAM_ALIVE = -1;
    ::DHUD_POLL_TEAM_INCAP = -1;
    ::DHUD_POLL_TEAM_DEAD = -1;
    ::DHUD_POLL_TEAM_HP = -1;
    ::DHUD_POLL_STATS = {};
    ::DHUD_POLL_INV_SLOTS = {};
    ::DHUD_LAST_INV_SCORE_TIME = -100.0;
    ::DHUD_LAST_SLOT_SCORE_TIME = {};
    ::DHUD_TRACK_USERID = -1;
    ::DHUD_TRACK_INDEX = -1;
    ::DHUD_TRACK_NAME = "";
    ::DHUD_TRACK_LOCKED = false;
    ::DHUD_TRACK_DEAD_LOCK = false;
    ::DHUD_RECENT_INV_SIGS = {};
    ::DHUD_SKIP_STAT_COMMON = 0;
    ::DHUD_SKIP_STAT_SPECIAL = 0;
    ::DHUD_SKIP_STAT_REVIVE = 0;
    ::DHUD_SKIP_STAT_HEAL = 0;
    ::DHUD_SKIP_STAT_PILLS = 0;
    ::DHUD_SKIP_STAT_ADRENALINE = 0;
    ::DHUD_LAST_USE_BUTTON_TIME = -100.0;
    ::DHUD_LAST_SUPPLY_BLOCK_TIME = -100.0;
    ::DHUD_PRESERVE_NEXT_ROUND = false;
    ::DHUD_LAST_BOSS_KILL_TIME = -100.0;
    ::DHUD_LAST_WITCH_KILL_TIME = -100.0;
    ::DHUD_LAST_TANK_KILL_TIME = -100.0;
    ::DHUD_LAST_WITCH_HURT_TIME = -100.0;
    ::DHUD_LAST_TANK_HURT_TIME = -100.0;
    ::DHUD_LAST_WITCH_HURT_ACTOR = -1;
    ::DHUD_LAST_TANK_HURT_ACTOR = -1;
    ::DHUD_SCORE_STATE_LOADED = true;
    try { DHUD_SaveScoreState(); } catch(e_save_reset) {}
}

function DHUD_SendTelemetryToClient(player, line)
{
    return;
}

function DHUD_BuildTelemetryLine(player, now, scoreOwned = true)
{
    local speed = 0;
    local hp = 0;
    local playerName = "-";
    local enemies = "";

    if (player != null)
    {
        speed = DHUD_Length2D(DHUD_Velocity(player)).tointeger();
        hp = DHUD_SurvivorHealth(player);
        playerName = DHUD_Name(player);
        enemies = DHUD_EnemyList(player);
    }

    return "DHUD2"
        + "|version=" + ::DHUD_VERSION
        + "|time=" + now
        + "|player=" + DHUD_Escape(playerName)
        + "|speed=" + speed
        + "|hp=" + hp
        + "|enemies=" + enemies
        + "|penalty_score=" + (scoreOwned ? DHUD_Fmt1(::DHUD_SCORE) : "60.0")
        + "|penalty_level=" + (scoreOwned ? DHUD_ScoreLevel() : "GOOD")
        + "|penalty_desc=" + DHUD_Escape(scoreOwned ? DHUD_ScoreDesc() : "Dedicated bridge")
        + "|penalty_last=" + DHUD_Escape(scoreOwned ? ::DHUD_LAST : "Waiting for personal score")
        + "|penalty_ff=" + (scoreOwned ? ::DHUD_FF : 0)
        + "|penalty_incaps=" + (scoreOwned ? ::DHUD_INCAPPED : 0)
        + "|penalty_deaths=" + (scoreOwned ? ::DHUD_DEATHS : 0)
        + "|penalty_revives=" + (scoreOwned ? ::DHUD_REVIVES : 0)
        + "|score_ff_damage=0"
        + "|score_heals=" + (scoreOwned ? ::DHUD_HEALS : 0)
        + "|score_heal_actions=" + (scoreOwned ? ::DHUD_HEALS : 0)
        + "|score_heal_team_hp=" + (scoreOwned ? ::DHUD_HEAL_HP_TEAM : 0)
        + "|score_defibs=0"
        + "|score_pills=" + (scoreOwned ? ::DHUD_PILLS : 0)
        + "|score_adrenaline=" + (scoreOwned ? ::DHUD_ADRENALINE : 0)
        + "|score_supplies=" + (scoreOwned ? ::DHUD_SUPPLIES : 0)
        + "|score_common=" + (scoreOwned ? ::DHUD_COMMON_KILLS : 0)
        + "|score_special=" + (scoreOwned ? ::DHUD_SPECIAL_KILLS : 0)
        + "|score_witch=" + (scoreOwned ? ::DHUD_WITCH_KILLS : 0)
        + "|score_tank=" + (scoreOwned ? ::DHUD_TANK_KILLS : 0)
        + "|score_damage_taken=" + (scoreOwned ? ::DHUD_DAMAGE_TAKEN : 0)
        + "|score_damage_done=" + (scoreOwned ? ::DHUD_DAMAGE_DONE : 0)
        + "|score_damage_progress=" + (scoreOwned ? ::DHUD_DAMAGE_DONE : 0)
        + "|score_damage_step=" + DHUD_RuleInt("damage_done_step", 200)
        + "|score_rescued_by_team=" + (scoreOwned ? ::DHUD_RESCUED_BY_TEAM : 0)
        + "|score_healed_by_team=" + (scoreOwned ? ::DHUD_HEALED_BY_TEAM : 0)
        + "|score_ledge=" + (scoreOwned ? ::DHUD_LEDGE_GRABS : 0)
        + "|team_alive=" + DHUD_TeamAlive()
        + "|team_incap=" + DHUD_TeamIncap()
        + "|team_dead=" + DHUD_TeamDead()
        + "|team_avg_hp=" + DHUD_TeamAvgHP()
        + "|score_event_reg=" + (::DHUD_EVENTS_REGISTERED ? 1 : 0)
        + "|score_events_seen=" + (scoreOwned ? ::DHUD_EVENTS_SEEN : 0)
        + "|score_tracked=" + DHUD_Escape(scoreOwned ? ::DHUD_TRACK_NAME : playerName)
        + "|score_active=" + ((scoreOwned && DHUD_ScoringActive()) ? 1 : 0)
        + "|score_debug_event=" + DHUD_Escape(scoreOwned ? ::DHUD_DEBUG_LAST_EVENT : "dedicated_client_bridge")
        + "|score_debug_score=" + DHUD_Escape(scoreOwned ? ::DHUD_DEBUG_LAST_SCORE_EVENT : "basic_personal_telemetry");
}

function DHUD_SendDedicatedTelemetryToClients(now, trackedLine)
{
    if (DHUD_HostPlayer() != null) return;
    local tracked = DHUD_TrackedPlayer(false);
    local sentTracked = false;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try
        {
            if (!ent.IsValid()) continue;
            if (!ent.IsSurvivor()) continue;
            if (!DHUD_IsHuman(ent)) continue;
            local isTracked = DHUD_SameEntity(ent, tracked);
            local line = isTracked ? trackedLine : DHUD_BuildTelemetryLine(ent, now, false);
            DHUD_SendTelemetryToClient(ent, line);
            if (isTracked) sentTracked = true;
        }
        catch(e_send_all) {}
    }
    if (!sentTracked && tracked != null) DHUD_SendTelemetryToClient(tracked, trackedLine);
}

function DHUD_Write(force = false)
{
    local now = DHUD_Now();
    if (!force && now < ::DHUD_LAST_WRITE + ::DHUD_WRITE_INTERVAL) return;
    ::DHUD_LAST_WRITE = now;

    local player = DHUD_Player();

    try { DHUD_ScorePoll(); } catch(e_poll) { try { printl("[DHUD] score poll failed: " + e_poll); } catch(e_print) {} }

    local line = DHUD_BuildTelemetryLine(player, now, true);

    try { StringToFile(::DHUD_FILE2, line); } catch(e) {}
    try { StringToFile(::DHUD_FILE, line); } catch(e2) {}

    if (force || now >= ::DHUD_LAST_CONSOLE + ::DHUD_CONSOLE_INTERVAL)
    {
        ::DHUD_LAST_CONSOLE = now;
        printl(line);
        if (DHUD_HostPlayer() == null)
        {
            try { DHUD_SendDedicatedTelemetryToClients(now, line); } catch(e_dedicated_telemetry) {}
        }
        else
        {
            try { DHUD_SendTelemetryToClient(player, line); } catch(e_client_telemetry) {}
        }
    }
}

function DanyriaHUD_SlowPoll()
{
    DHUD_Write(false);
}

function DanyriaHUD_FastThink()
{
    DHUD_Write(false);
    return ::DHUD_WRITE_INTERVAL;
}


function DHUD_EventNames()
{
    return [
        "round_start",
        "player_hurt",
        "player_hurt_concise",
        "player_incapacitated",
        "player_ledge_grab",
        "player_death",
        "infected_death",
        "infected_hurt",
        "entity_hurt",
        "weapon_fire",
        "non_pistol_fired",
        "non_melee_fired",
        "weapon_fire_at_40",
        "player_used_first_aid",
        "player_use_item",
        "player_give_item",
        "witch_hurt",
        "tank_hurt",
        "witch_killed",
        "tank_killed",
        "charger_killed",
        "spitter_killed",
        "jockey_killed",
        "hunter_killed",
        "smoker_killed",
        "boomer_killed",
        "spider_killed",
        "boomer_exploded",
        "ammo_pack_used",
        "give_weapon",
        "weapon_drop",
        "receive_upgrade",
        "upgrade_incendiary_ammo",
        "upgrade_explosive_ammo",
        "player_incapacitated_start",
        "rescue_survivor",
        "survivor_rescued",
        "revive_success",
        "heal_success",
        "pills_used",
        "adrenaline_used",
        "melee_kill",
        "infected_decapitated",
        "item_pickup",
        "weapon_pickup",
        "weapon_given",
        "item_given",
        "ammo_pickup",
        "upgrade_pack_added",
        "upgrade_pack_used",
        "player_use",
        "zombie_death",
        "special_killed",
        "revive_begin",
        "heal_begin",
        "player_spawn",
        "tank_spawn",
        "witch_spawn",
        "mission_lost",
        "map_transition",
        "spawner_give_item",
        "player_ledge_release",
        "finale_win"
    ];
}

function DHUD_ExportRootEventCallbacks()
{
    local root = getroottable();
    root.OnGameEvent_round_start <- function(params) { ::DHUD_DispatchGameEvent("round_start", params); };
    root.OnGameEvent_player_hurt <- function(params) { ::DHUD_DispatchGameEvent("player_hurt", params); };
    root.OnGameEvent_player_hurt_concise <- function(params) { ::DHUD_DispatchGameEvent("player_hurt_concise", params); };
    root.OnGameEvent_player_incapacitated <- function(params) { ::DHUD_DispatchGameEvent("player_incapacitated", params); };
    root.OnGameEvent_player_ledge_grab <- function(params) { ::DHUD_DispatchGameEvent("player_ledge_grab", params); };
    root.OnGameEvent_player_death <- function(params) { ::DHUD_DispatchGameEvent("player_death", params); };
    root.OnGameEvent_infected_death <- function(params) { ::DHUD_DispatchGameEvent("infected_death", params); };
    root.OnGameEvent_infected_hurt <- function(params) { ::DHUD_DispatchGameEvent("infected_hurt", params); };
    root.OnGameEvent_entity_hurt <- function(params) { ::DHUD_DispatchGameEvent("entity_hurt", params); };
    root.OnGameEvent_weapon_fire <- function(params) { ::DHUD_DispatchGameEvent("weapon_fire", params); };
    root.OnGameEvent_non_pistol_fired <- function(params) { ::DHUD_DispatchGameEvent("non_pistol_fired", params); };
    root.OnGameEvent_non_melee_fired <- function(params) { ::DHUD_DispatchGameEvent("non_melee_fired", params); };
    root.OnGameEvent_weapon_fire_at_40 <- function(params) { ::DHUD_DispatchGameEvent("weapon_fire_at_40", params); };
    root.OnGameEvent_player_used_first_aid <- function(params) { ::DHUD_DispatchGameEvent("player_used_first_aid", params); };
    root.OnGameEvent_player_use_item <- function(params) { ::DHUD_DispatchGameEvent("player_use_item", params); };
    root.OnGameEvent_player_give_item <- function(params) { ::DHUD_DispatchGameEvent("player_give_item", params); };
    root.OnGameEvent_witch_hurt <- function(params) { ::DHUD_DispatchGameEvent("witch_hurt", params); };
    root.OnGameEvent_tank_hurt <- function(params) { ::DHUD_DispatchGameEvent("tank_hurt", params); };
    root.OnGameEvent_witch_killed <- function(params) { ::DHUD_DispatchGameEvent("witch_killed", params); };
    root.OnGameEvent_tank_killed <- function(params) { ::DHUD_DispatchGameEvent("tank_killed", params); };
    root.OnGameEvent_charger_killed <- function(params) { ::DHUD_DispatchGameEvent("charger_killed", params); };
    root.OnGameEvent_spitter_killed <- function(params) { ::DHUD_DispatchGameEvent("spitter_killed", params); };
    root.OnGameEvent_jockey_killed <- function(params) { ::DHUD_DispatchGameEvent("jockey_killed", params); };
    root.OnGameEvent_hunter_killed <- function(params) { ::DHUD_DispatchGameEvent("hunter_killed", params); };
    root.OnGameEvent_smoker_killed <- function(params) { ::DHUD_DispatchGameEvent("smoker_killed", params); };
    root.OnGameEvent_boomer_killed <- function(params) { ::DHUD_DispatchGameEvent("boomer_killed", params); };
    root.OnGameEvent_spider_killed <- function(params) { ::DHUD_DispatchGameEvent("spider_killed", params); };
    root.OnGameEvent_boomer_exploded <- function(params) { ::DHUD_DispatchGameEvent("boomer_exploded", params); };
    root.OnGameEvent_ammo_pack_used <- function(params) { ::DHUD_DispatchGameEvent("ammo_pack_used", params); };
    root.OnGameEvent_give_weapon <- function(params) { ::DHUD_DispatchGameEvent("give_weapon", params); };
    root.OnGameEvent_weapon_drop <- function(params) { ::DHUD_DispatchGameEvent("weapon_drop", params); };
    root.OnGameEvent_receive_upgrade <- function(params) { ::DHUD_DispatchGameEvent("receive_upgrade", params); };
    root.OnGameEvent_upgrade_incendiary_ammo <- function(params) { ::DHUD_DispatchGameEvent("upgrade_incendiary_ammo", params); };
    root.OnGameEvent_upgrade_explosive_ammo <- function(params) { ::DHUD_DispatchGameEvent("upgrade_explosive_ammo", params); };
    root.OnGameEvent_player_incapacitated_start <- function(params) { ::DHUD_DispatchGameEvent("player_incapacitated_start", params); };
    root.OnGameEvent_rescue_survivor <- function(params) { ::DHUD_DispatchGameEvent("rescue_survivor", params); };
    root.OnGameEvent_survivor_rescued <- function(params) { ::DHUD_DispatchGameEvent("survivor_rescued", params); };
    root.OnGameEvent_revive_success <- function(params) { ::DHUD_DispatchGameEvent("revive_success", params); };
    root.OnGameEvent_heal_success <- function(params) { ::DHUD_DispatchGameEvent("heal_success", params); };
    root.OnGameEvent_pills_used <- function(params) { ::DHUD_DispatchGameEvent("pills_used", params); };
    root.OnGameEvent_adrenaline_used <- function(params) { ::DHUD_DispatchGameEvent("adrenaline_used", params); };
    root.OnGameEvent_melee_kill <- function(params) { ::DHUD_DispatchGameEvent("melee_kill", params); };
    root.OnGameEvent_infected_decapitated <- function(params) { ::DHUD_DispatchGameEvent("infected_decapitated", params); };
    root.OnGameEvent_item_pickup <- function(params) { ::DHUD_DispatchGameEvent("item_pickup", params); };
    root.OnGameEvent_weapon_pickup <- function(params) { ::DHUD_DispatchGameEvent("weapon_pickup", params); };
    root.OnGameEvent_weapon_given <- function(params) { ::DHUD_DispatchGameEvent("weapon_given", params); };
    root.OnGameEvent_item_given <- function(params) { ::DHUD_DispatchGameEvent("item_given", params); };
    root.OnGameEvent_ammo_pickup <- function(params) { ::DHUD_DispatchGameEvent("ammo_pickup", params); };
    root.OnGameEvent_upgrade_pack_added <- function(params) { ::DHUD_DispatchGameEvent("upgrade_pack_added", params); };
    root.OnGameEvent_upgrade_pack_used <- function(params) { ::DHUD_DispatchGameEvent("upgrade_pack_used", params); };
    root.OnGameEvent_player_use <- function(params) { ::DHUD_DispatchGameEvent("player_use", params); };
    root.OnGameEvent_zombie_death <- function(params) { ::DHUD_DispatchGameEvent("zombie_death", params); };
    root.OnGameEvent_special_killed <- function(params) { ::DHUD_DispatchGameEvent("special_killed", params); };
    root.OnGameEvent_revive_begin <- function(params) { ::DHUD_DispatchGameEvent("revive_begin", params); };
    root.OnGameEvent_heal_begin <- function(params) { ::DHUD_DispatchGameEvent("heal_begin", params); };
    root.OnGameEvent_player_spawn <- function(params) { ::DHUD_DispatchGameEvent("player_spawn", params); };
    root.OnGameEvent_tank_spawn <- function(params) { ::DHUD_DispatchGameEvent("tank_spawn", params); };
    root.OnGameEvent_witch_spawn <- function(params) { ::DHUD_DispatchGameEvent("witch_spawn", params); };
    root.OnGameEvent_mission_lost <- function(params) { ::DHUD_DispatchGameEvent("mission_lost", params); };
    root.OnGameEvent_map_transition <- function(params) { ::DHUD_DispatchGameEvent("map_transition", params); };
    root.OnGameEvent_spawner_give_item <- function(params) { ::DHUD_DispatchGameEvent("spawner_give_item", params); };
    root.OnGameEvent_player_ledge_release <- function(params) { ::DHUD_DispatchGameEvent("player_ledge_release", params); };
    root.OnGameEvent_finale_win <- function(params) { ::DHUD_DispatchGameEvent("finale_win", params); };
}


function DHUD_MakeListenCallback(evname)
{
    return function(params)
    {
        try { ::DHUD_DispatchGameEvent(evname, params); } catch(e) {}
    };
}

function DHUD_RegisterListenEvents()
{
    if (::DHUD_LISTEN_EVENTS_REGISTERED) return true;
    local ok = false;
    try
    {
        foreach (evname in DHUD_EventNames())
        {
            try
            {
                local cb = DHUD_MakeListenCallback(evname);
                ::DHUD_LISTEN_CALLBACKS.push(cb);
                ListenToGameEvent(evname, cb, null);
                ok = true;
            }
            catch(e_one) {}
        }
    }
    catch(e) {}
    if (ok)
    {
        ::DHUD_LISTEN_EVENTS_REGISTERED = true;
        try { printl("[DHUD] ListenToGameEvent score callbacks registered."); } catch(e2) {}
    }
    return ok;
}

function DHUD_RegisterEvents()
{
    if (!("DHUD_ROOT_EVENTS_REGISTERED" in getroottable())) ::DHUD_ROOT_EVENTS_REGISTERED <- false;

    local rootOk = false;
    if (!::DHUD_ROOT_EVENTS_REGISTERED)
    {
        try
        {
            DHUD_ExportRootEventCallbacks();
            __CollectEventCallbacks(getroottable(), "OnGameEvent_", "DanyriaRootGameEventCallbacks", RegisterScriptGameEventListener);
            ::DHUD_ROOT_EVENTS_REGISTERED = true;
            rootOk = true;
            try { printl("[DHUD] root score event callbacks registered."); } catch(e_print_ok) {}
        }
        catch(e_root)
        {
            try { printl("[DHUD] root event callback registration failed: " + e_root); } catch(e_print_root) {}
        }
    }
    else
    {
        rootOk = true;
    }

    if (::DHUD_EVENTS_REGISTERED) return;

    local ok = rootOk;

    try { if (DHUD_RegisterListenEvents()) ok = true; } catch(e_listen) {}

    try
    {
        ::DHUD_EVENT_SCOPE <- DHUD_BuildEventScope();
        __CollectEventCallbacks(::DHUD_EVENT_SCOPE, "OnGameEvent_", "DanyriaExplicitGameEventCallbacks", RegisterScriptGameEventListener);
        ok = true;
    }
    catch(e)
    {
        try { printl("[DHUD] explicit event callback registration failed: " + e); } catch(e_print) {}
    }

    try { __CollectEventCallbacks(this, "OnGameEvent_", "DanyriaLocalGameEventCallbacks", RegisterScriptGameEventListener); ok = true; } catch(e2) {}
    try { __CollectGameEventCallbacks(this); ok = true; } catch(e3) {}

    try
    {
        foreach (evname in DHUD_EventNames())
        {
            try { RegisterScriptGameEventListener(evname); ok = true; } catch(e4) {}
        }
    }
    catch(e5) {}

    if (ok)
    {
        ::DHUD_EVENTS_REGISTERED = true;
        try { printl("[DHUD] score event callbacks registered."); } catch(e6) {}
    }
}

function DHUD_TimerTick()
{
    if (!::DHUD_TIMER_ACTIVE) return;
    DHUD_Write(false);
    try { DoEntFire("worldspawn", "RunScriptCode", "::DHUD_TimerTick()", ::DHUD_WRITE_INTERVAL, null, null); } catch(e) {}
}

function DHUD_Register()
{
    if (::DHUD_POLL_REGISTERED) return;
    ::DHUD_POLL_REGISTERED = true;

    try { ScriptedMode_AddSlowPoll(DanyriaHUD_SlowPoll); } catch(e) {}
    try
    {
        local world = Entities.FindByClassname(null, "worldspawn");
        if (world != null)
        {
            try { world.ValidateScriptScope(); } catch(e3) {}
            try
            {
                local scope = world.GetScriptScope();
                scope["DanyriaHUD_FastThink"] <- DanyriaHUD_FastThink;
            }
            catch(e4) {}
            try { AddThinkToEnt(world, "DanyriaHUD_FastThink"); } catch(e5) {}
        }
    }
    catch(e2) {}

    if (!::DHUD_TIMER_ACTIVE)
    {
        ::DHUD_TIMER_ACTIVE = true;
        try { DoEntFire("worldspawn", "RunScriptCode", "::DHUD_TimerTick()", ::DHUD_WRITE_INTERVAL, null, null); } catch(e6) {}
    }

    DHUD_Write(true);
}

function OnGameEvent_round_start(params)
{
    if (DHUD_LoadScoreState())
    {
        ::DHUD_PRESERVE_NEXT_ROUND = false;
        DHUD_ResetRuntimeForNextChapter();
        try { DHUD_SaveScoreState(); } catch(e_save_after_load) {}
    }
    else if (::DHUD_SCORE_SESSION_STARTED)
    {
        ::DHUD_PRESERVE_NEXT_ROUND = false;
        DHUD_ResetRuntimeForNextChapter();
    }
    else
    {
        DHUD_ResetScore();
    }
    DHUD_Register();
    DHUD_Write(true);
}

function DHUD_TextContains(text, needle)
{
    try { return text.tolower().find(needle) != null; } catch(e) {}
    return false;
}

function DHUD_EntityActionDedupe(tag, actor, subject, params, cooldown)
{
    if (!("DHUD_ACTION_SEEN" in getroottable())) ::DHUD_ACTION_SEEN <- {};
    local now = DHUD_Now();
    local key = tag + "|a=" + DHUD_EntityIndex(actor) + "|s=" + DHUD_EntityIndex(subject);
    if (DHUD_EntityIndex(actor) < 0 && DHUD_EntityIndex(subject) < 0)
    {
        local keys = ["userid", "attacker", "attacker_userid", "killer", "killer_userid", "victim", "subject", "target", "entityid", "entindex", "weapon", "item", "type"];
        foreach (k in keys)
        {
            try { key += "|" + k + "=" + params[k]; } catch(e) {}
        }
    }
    try
    {
        if (key in ::DHUD_ACTION_SEEN && now - ::DHUD_ACTION_SEEN[key] < cooldown) return true;
        ::DHUD_ACTION_SEEN[key] <- now;
        foreach (oldk, oldt in ::DHUD_ACTION_SEEN)
        {
            if (now - oldt > 4.0) delete ::DHUD_ACTION_SEEN[oldk];
        }
    }
    catch(e2) {}
    return false;
}

function DHUD_EventActor(params)
{
    return DHUD_EventPlayerAny(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "userid", "player", "player_userid", "rescuer", "reviver", "healer", "giver", "giver_userid", "donor"]);
}

function DHUD_EventSubject(params)
{
    return DHUD_EventPlayerAny(params, ["subject", "victim", "target", "userid"]);
}

function DHUD_InfectedKind(params, victim)
{
    if (DHUD_EventHasKey(params, "witchid")) return "witch";
    if (DHUD_EventHasKey(params, "tankid")) return "tank";

    try
    {
        local cn0 = victim.GetClassname();
        if (cn0 == "witch") return "witch";
    }
    catch(e0) {}

    local zt = -1;
    if (victim != null) zt = DHUD_ZombieType(victim);
    if (zt < 0) zt = DHUD_EventInt(params, "zombieclass", -1);
    if (zt < 0) zt = DHUD_EventInt(params, "zombie_class", -1);
    if (zt == 8) return "tank";
    if (zt >= 1 && zt <= 6) return "special";

    try
    {
        local cn = victim.GetClassname();
        if (cn == "witch") return "witch";
        if (cn == "player" && !victim.IsSurvivor()) return "special";
        if (cn == "infected") return "common";
    }
    catch(e) {}

    local text = DHUD_EventText(params, "victimname", "") + " " + DHUD_EventText(params, "classname", "") + " " + DHUD_EventText(params, "infected", "") + " " + DHUD_EventText(params, "name", "") + " " + DHUD_EventText(params, "type", "");
    if (DHUD_TextContains(text, "witch")) return "witch";
    if (DHUD_TextContains(text, "tank")) return "tank";
    if (DHUD_TextContains(text, "smoker") || DHUD_TextContains(text, "boomer") || DHUD_TextContains(text, "hunter") || DHUD_TextContains(text, "spitter") || DHUD_TextContains(text, "spider") || DHUD_TextContains(text, "jockey") || DHUD_TextContains(text, "charger")) return "special";
    return "";
}

function DHUD_BossKindFromRecentTrackedDamage(actor)
{
    if (!DHUD_IsTracked(actor)) return "";
    local now = DHUD_Now();
    local aidx = DHUD_EntityIndex(actor);
    try
    {
        if (aidx >= 0 && ::DHUD_LAST_WITCH_HURT_ACTOR == aidx && now - ::DHUD_LAST_WITCH_HURT_TIME < 4.00) return "witch";
        if (aidx >= 0 && ::DHUD_LAST_TANK_HURT_ACTOR == aidx && now - ::DHUD_LAST_TANK_HURT_TIME < 4.00) return "tank";
    }
    catch(e) {}
    return "";
}

function DHUD_RecentBossHurtActor(kind, window = 4.00)
{
    local now = DHUD_Now();
    local idx = -1;
    try
    {
        if (kind == "witch" && now - ::DHUD_LAST_WITCH_HURT_TIME <= window) idx = ::DHUD_LAST_WITCH_HURT_ACTOR;
        else if (kind == "tank" && now - ::DHUD_LAST_TANK_HURT_TIME <= window) idx = ::DHUD_LAST_TANK_HURT_ACTOR;
    }
    catch(e0) { idx = -1; }
    if (idx < 0) return null;
    local ent = DHUD_EntityByIndex(idx);
    if (DHUD_IsTracked(ent)) return ent;
    return null;
}





function DHUD_HumanSurvivorCount()
{
    local n = 0;
    local ent = null;
    while ((ent = Entities.FindByClassname(ent, "player")) != null)
    {
        try
        {
            if (ent.IsValid() && ent.IsSurvivor() && !ent.IsBot()) n += 1;
        }
        catch(e) {}
    }
    return n;
}

function DHUD_UseStrictAttribution()
{
    return true;
}

function DHUD_ExplicitActor(params, keys)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, keys);
    if (DHUD_IsTracked(actor)) return actor;
    return actor;
}

function DHUD_MarkTrackedDamageTarget(victim, kind = "")
{
    local idx = DHUD_EntityIndex(victim);
    if (idx < 0) return;
    try
    {
        ::DHUD_TRACKED_DAMAGE_TARGETS[idx] <- DHUD_Now();
        if (kind != "") ::DHUD_TRACKED_DAMAGE_KINDS[idx] <- kind;
    }
    catch(e) {}
}

function DHUD_RecentTrackedDamageTo(victim, window = 0.80)
{
    local idx = DHUD_EntityIndex(victim);
    if (idx < 0) return false;
    return DHUD_RecentTrackedDamageIndex(idx, window);
}

function DHUD_RecentTrackedDamageIndex(idx, window = 0.80)
{
    if (idx < 0) return false;
    try
    {
        if (idx in ::DHUD_TRACKED_DAMAGE_TARGETS) return (DHUD_Now() - ::DHUD_TRACKED_DAMAGE_TARGETS[idx]) <= window;
    }
    catch(e) {}
    return false;
}

function DHUD_TrackedDamageKindIndex(idx)
{
    if (idx < 0) return "";
    try
    {
        if (idx in ::DHUD_TRACKED_DAMAGE_KINDS) return ::DHUD_TRACKED_DAMAGE_KINDS[idx];
    }
    catch(e) {}
    return "";
}

function DHUD_TrackedDamageKind(victim)
{
    return DHUD_TrackedDamageKindIndex(DHUD_EntityIndex(victim));
}

function DHUD_CleanupTrackedDamageTargets()
{
    try
    {
        local now = DHUD_Now();
        foreach (idx, t in ::DHUD_TRACKED_DAMAGE_TARGETS)
        {
            if (now - t > 6.0)
            {
                delete ::DHUD_TRACKED_DAMAGE_TARGETS[idx];
                try { if (idx in ::DHUD_TRACKED_DAMAGE_KINDS) delete ::DHUD_TRACKED_DAMAGE_KINDS[idx]; } catch(e_kind) {}
                try { if (idx in ::DHUD_TRACKED_DAMAGE_AMOUNTS) delete ::DHUD_TRACKED_DAMAGE_AMOUNTS[idx]; } catch(e_amount) {}
            }
        }
    }
    catch(e) {}
}


function DHUD_ActorOrRecentTracked(params, keys, allowRecentAttack = true)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, keys);
    if (DHUD_IsTracked(actor)) return actor;

    if (actor != null)
    {
        try { if (actor.IsValid() && actor.IsSurvivor()) return actor; } catch(e_surv) {}
    }

    return actor;
}



function DHUD_KillActorOrRecentTracked(params, keys)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, keys);
    if (DHUD_IsTracked(actor)) return actor;

    if (actor != null)
    {
        try { if (actor.IsValid() && actor.IsSurvivor()) return actor; } catch(e_surv) {}
    }

    return actor;
}




function DHUD_RecordEnemyDamage(params, label)
{
    local actor = DHUD_ActorOrRecentTracked(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "userid", "player", "player_userid"], true);
    if (!DHUD_ScoringActive() || !DHUD_IsTracked(actor)) return;

    local victim = DHUD_EventEntityAny(params, ["victim", "victim_userid", "subject", "target", "entityid", "entindex", "infected_id", "tankid", "witchid", "userid"]);
    if (DHUD_IsSurvivor(victim)) return;

    local dmg = DHUD_EventDamageAmount(params);
    if (dmg > 0)
    {
        local kind = DHUD_InfectedKind(params, victim);
        DHUD_MarkTrackedDamageTarget(victim, kind);
        DHUD_AddTrackedDamageForIndex(DHUD_EntityIndex(victim), kind, dmg, label, DHUD_MaxHealth(victim, 0));
    }
}




function DHUD_AddPolledEnemyKill(idx, kind, label)
{
    if (!DHUD_ScoringActive()) return;
    if (kind == "common" || kind == "") return;
    local now = DHUD_Now();
    local key = "poll_kill|" + idx + "|" + kind;
    try
    {
        if (key in ::DHUD_POLL_KILL_SEEN && now - ::DHUD_POLL_KILL_SEEN[key] < 3.00) return;
        ::DHUD_POLL_KILL_SEEN[key] <- now;
    }
    catch(e_seen_poll) {}
    local actor = DHUD_TrackedPlayer(true);
    if (!DHUD_IsTracked(actor)) return;
    local victim = DHUD_EntityByIndex(idx);
    local fake = { entindex = idx, source = "poll" };
    DHUD_AddSpecialKill(fake, actor, victim, kind, label);
}

function DHUD_AddSpecialKill(params, actor, victim, kind, label)
{
    if (!DHUD_ScoringActive()) return;
    if (!DHUD_IsTracked(actor)) return;
    if (DHUD_IsSurvivor(victim)) return;
    if (kind == "") kind = DHUD_InfectedKind(params, victim);
    if (kind == "") kind = "special";

    local recentKey = "recent_kill_" + kind + "|a=" + DHUD_EntityIndex(actor);
    local nowKill = DHUD_Now();
    try
    {
        local bossKey = "recent_boss_any|a=" + DHUD_EntityIndex(actor);
        if (kind == "special" && bossKey in ::DHUD_ACTION_SEEN && nowKill - ::DHUD_ACTION_SEEN[bossKey] < 0.90) return;
        if (recentKey in ::DHUD_ACTION_SEEN && nowKill - ::DHUD_ACTION_SEEN[recentKey] < 0.35) return;
        ::DHUD_ACTION_SEEN[recentKey] <- nowKill;
        if (kind == "witch") { ::DHUD_LAST_WITCH_KILL_TIME = nowKill; ::DHUD_LAST_BOSS_KILL_TIME = nowKill; ::DHUD_ACTION_SEEN[bossKey] <- nowKill; }
        else if (kind == "tank") { ::DHUD_LAST_TANK_KILL_TIME = nowKill; ::DHUD_LAST_BOSS_KILL_TIME = nowKill; ::DHUD_ACTION_SEEN[bossKey] <- nowKill; }
        if (kind == "special")
        {
            ::DHUD_ACTION_SEEN["recent_special_any|a=" + DHUD_EntityIndex(actor)] <- nowKill;
            ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS += 1;
            if (::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS > 3) ::DHUD_PENDING_SPECIAL_COMMON_SUPPRESS = 3;
        }
    }
    catch(e_recent) {}

    if (DHUD_EntityActionDedupe("kill_" + kind, actor, victim, params, 0.45)) return;

    if (kind == "tank")
    {
        ::DHUD_TANK_KILLS += 1;
        ::DHUD_SKIP_STAT_SPECIAL += 1;
        DHUD_ScoreDelta(DHUD_Rule("tank", 5.0), "Tank killed " + DHUD_Fmt1(DHUD_Rule("tank", 5.0)));
    }
    else if (kind == "witch")
    {
        ::DHUD_WITCH_KILLS += 1;
        ::DHUD_SKIP_STAT_SPECIAL += 1;
        DHUD_ScoreDelta(DHUD_Rule("witch", 3.0), "Witch killed " + DHUD_Fmt1(DHUD_Rule("witch", 3.0)));
    }
    else
    {
        ::DHUD_SPECIAL_KILLS += 1;
        ::DHUD_SKIP_STAT_SPECIAL += 1;
        DHUD_ScoreDelta(DHUD_Rule("special", 1.5), label + " " + DHUD_Fmt1(DHUD_Rule("special", 1.5)));
    }
}

function DHUD_AddCommonKill(params, actor, reason)
{
    if (!DHUD_ScoringActive()) return;
    if (!DHUD_IsTracked(actor)) return;
    local now = DHUD_Now();
    try
    {
        local sk = "recent_special_any|a=" + DHUD_EntityIndex(actor);
        if (sk in ::DHUD_ACTION_SEEN && now - ::DHUD_ACTION_SEEN[sk] < 0.60) return;
    }
    catch(e_recent_common) {}
    local commonKey = "kill_common|a=" + DHUD_EntityIndex(actor);
    local hasIdentity = false;
    foreach (k in ["infected_id", "entityid", "entindex", "victim", "target"])
    {
        try { commonKey += "|" + k + "=" + params[k]; hasIdentity = true; } catch(e_key) {}
    }
    if (!hasIdentity)
    {
        try { commonKey += "|tb=" + ((now * 50.0).tointeger()); } catch(e_tb) {}
    }
    if (DHUD_CustomDedupe(commonKey, hasIdentity ? 0.16 : 0.04)) return;
    ::DHUD_COMMON_KILLS += 1;
    ::DHUD_SKIP_STAT_COMMON += 1;
    DHUD_ScoreDelta(0.1, reason + " +0.1");
}


function DHUD_IsUseOrAttackPressed(ent)
{
    if (ent == null) return false;
    local buttons = 0;
    try { buttons = NetProps.GetPropInt(ent, "m_nButtons"); } catch(e) { return false; }
    try { if ((buttons & 1) != 0) return true; } catch(e1) {}
    try { if ((buttons & 32) != 0) return true; } catch(e2) {}
    try { if ((buttons & 2048) != 0) return true; } catch(e3) {}
    return false;
}

function DHUD_HasRecentManualSupplyAction(ent)
{
    if (DHUD_IsUseOrAttackPressed(ent)) return true;
    try { if (DHUD_Now() - ::DHUD_LAST_USE_BUTTON_TIME < 1.25) return true; } catch(e) {}
    return false;
}

function DHUD_SupplyScore(name, reason)
{
    local n = name;
    try { n = n.tolower(); } catch(e) {}
    if (DHUD_TextContains(n, "first_aid")) return -4;
    if (DHUD_TextContains(n, "ammo") || DHUD_TextContains(n, "upgrade")) return -2;
    if (DHUD_TextContains(n, "weapon_") || DHUD_TextContains(n, "melee") || DHUD_TextContains(n, "pistol")) return -2;
    if (DHUD_TextContains(n, "pills") || DHUD_TextContains(n, "adrenaline")) return -2;
    if (DHUD_TextContains(n, "molotov") || DHUD_TextContains(n, "pipe_bomb") || DHUD_TextContains(n, "vomitjar")) return -2;
    return -2;
}

function DHUD_EventDamageAmount(params)
{
    local keys = ["dmg_health", "amount", "damage", "dmg", "damageamount", "damage_health", "damage_health_real", "dmgHealth", "dmg_done", "damage_done"];
    foreach (k in keys)
    {
        local v = DHUD_EventInt(params, k, -1);
        if (v > 0) return v;
    }
    return 0;
}


function DHUD_RecordDamageTaken(dmg, reason)
{
    if (dmg < 1) return;
    local now = DHUD_Now();
    if (now - ::DHUD_LAST_DAMAGE_TAKEN_TIME < 0.08) return;
    ::DHUD_LAST_DAMAGE_TAKEN_TIME = now;
    ::DHUD_DAMAGE_TAKEN += dmg;
    local per10 = DHUD_Rule("damage_taken_per10", -1.0);
    local pen = ((dmg + 9) / 10).tointeger() * per10;
    DHUD_ScoreDelta(pen, reason + " -" + dmg + " HP / score " + DHUD_Fmt1(pen));
}

function DHUD_RecordSelfHealthDrop(ent, reason)
{
    if (ent == null) return false;
    local cur = DHUD_SurvivorHealth(ent);
    if (cur < 0) cur = 0;
    if (::DHUD_POLL_HP > 0 && cur > 0 && cur < ::DHUD_POLL_HP && !DHUD_IsIncap(ent) && !DHUD_IsDeadSafe(ent))
    {
        local dmg = ::DHUD_POLL_HP - cur;
        if (dmg >= 2)
        {
            DHUD_RecordDamageTaken(dmg, reason);
            ::DHUD_POLL_HP = cur;
            return true;
        }
    }
    if (cur > 0) ::DHUD_POLL_HP = cur;
    return false;
}

function OnGameEvent_player_hurt(params)
{
    local victim = DHUD_EventPlayerAny(params, ["userid", "victim", "victim_userid", "subject", "target", "entityid", "entindex"]);
    local attacker = DHUD_EventPlayerTrackedFirst(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid"]);
    local dmg = DHUD_EventDamageAmount(params);

    if (DHUD_EntityActionDedupe("hurt", attacker, victim, params, 0.03))
    {
        DHUD_Write(true);
        return;
    }

    if (DHUD_IsTracked(victim))
    {
        local reason = DHUD_SameEntity(victim, attacker) ? "Self damage" : "Damage taken";
        if (!DHUD_RecordSelfHealthDrop(victim, reason))
        {
            if (dmg > 0) DHUD_Remember("Damage event pending -" + dmg);
        }
    }
    else if (DHUD_ScoringActive() && DHUD_IsTracked(attacker) && victim != null && !DHUD_IsSurvivor(victim))
    {
        if (dmg > 0)
        {
            local kind = DHUD_InfectedKind(params, victim);
            DHUD_MarkTrackedDamageTarget(victim, kind);
            DHUD_AddTrackedDamageForIndex(DHUD_EntityIndex(victim), kind, dmg, "Damage dealt", DHUD_MaxHealth(victim, 0));
        }
    }
    DHUD_Write(true);
}


function OnGameEvent_player_incapacitated(params)
{
    local victim = DHUD_EventPlayerTrackedFirst(params, ["userid", "victim", "victim_userid", "subject", "target", "entityid", "entindex"]);
    if (DHUD_IsTracked(victim) && !DHUD_EntityActionDedupe("incap", victim, null, params, 1.20))
    {
        DHUD_RecordPersonalIncap("You were incapacitated " + DHUD_Fmt1(DHUD_Rule("incap", -10.0)));
    }
    DHUD_Write(true);
}

function OnGameEvent_player_ledge_grab(params)
{
    local victim = DHUD_EventPlayerTrackedFirst(params, ["userid", "victim", "victim_userid", "subject", "target", "entityid", "entindex"]);
    if (DHUD_IsTracked(victim) && !DHUD_EntityActionDedupe("ledge", victim, null, params, 1.20))
    {
        DHUD_RecordPersonalLedge("Ledge grab -6");
    }
    DHUD_Write(true);
}



function OnGameEvent_player_death(params)
{
    local victim = DHUD_EventPlayerAny(params, ["userid", "victim", "subject", "target"]);
    if (victim == null) victim = DHUD_EventEntityAny(params, ["entityid", "entindex", "infected_id", "tankid", "witchid"]);
    if (DHUD_IsTracked(victim))
    {
        DHUD_RecordPersonalDeath("You died -18");
        DHUD_Write(true);
        return;
    }
    if (DHUD_IsSurvivor(victim)) { DHUD_Write(true); return; }

    local actor = DHUD_KillActorOrRecentTracked(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "player", "player_userid"]);
    if (!DHUD_IsTracked(actor) && DHUD_RecentTrackedDamageTo(victim, 4.00)) actor = DHUD_TrackedPlayer(true);
    local kind = DHUD_InfectedKind(params, victim);
    if (kind == "") kind = DHUD_TrackedDamageKind(victim);
    if (kind == "witch") DHUD_AddSpecialKill(params, actor, victim, "witch", "Witch killed");
    else if (kind == "tank") DHUD_AddSpecialKill(params, actor, victim, "tank", "Tank killed");
    else if (kind == "special") DHUD_AddSpecialKill(params, actor, victim, "special", "Special infected killed");
    DHUD_Write(true);
}





function OnGameEvent_infected_death(params)
{
    local attacker = DHUD_KillActorOrRecentTracked(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "player", "player_userid"]);
    local victim = DHUD_EventEntityAny(params, ["infected_id", "entityid", "entindex", "victim", "subject", "target", "tankid", "witchid"]);
    if (!DHUD_IsTracked(attacker) && DHUD_RecentTrackedDamageTo(victim, 4.00)) attacker = DHUD_TrackedPlayer(true);
    local kind = DHUD_InfectedKind(params, victim);
    if (kind == "") kind = DHUD_TrackedDamageKind(victim);
    if (kind == "special" || kind == "witch" || kind == "tank") DHUD_AddSpecialKill(params, attacker, victim, kind, "Special infected killed");
    else DHUD_AddCommonKill(params, attacker, "Common infected killed");
    DHUD_Write(true);
}




function OnGameEvent_witch_killed(params)
{
    local actor = DHUD_ExplicitActor(params, ["userid", "attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "killer", "killer_userid", "killeruserid", "killerid"]);
    local victim = DHUD_EventEntityAny(params, ["witchid", "entityid", "entindex", "victim", "subject", "target"]);
    if (!DHUD_IsTracked(actor))
    {
        local bossActor = DHUD_RecentBossHurtActor("witch", 4.00);
        if (DHUD_IsTracked(bossActor)) actor = bossActor;
        else if (DHUD_RecentTrackedDamageTo(victim, 4.00)) actor = DHUD_TrackedPlayer(true);
    }
    DHUD_AddSpecialKill(params, actor, victim, "witch", "Witch killed");
    DHUD_Write(true);
}



function OnGameEvent_tank_killed(params)
{
    local actor = DHUD_ExplicitActor(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "killer", "killer_userid", "killeruserid", "killerid"]);
    local victim = DHUD_EventEntityAny(params, ["userid", "tankid", "entityid", "entindex", "victim", "subject", "target"]);
    if (!DHUD_IsTracked(actor))
    {
        local bossActor = DHUD_RecentBossHurtActor("tank", 4.00);
        if (DHUD_IsTracked(bossActor)) actor = bossActor;
        else if (DHUD_RecentTrackedDamageTo(victim, 4.00)) actor = DHUD_TrackedPlayer(true);
    }
    DHUD_AddSpecialKill(params, actor, victim, "tank", "Tank killed");
    DHUD_Write(true);
}


function OnGameEvent_rescue_survivor(params) { DHUD_Write(true); }
function OnGameEvent_survivor_rescued(params) { DHUD_Write(true); }


function OnGameEvent_revive_success(params)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, ["userid", "rescuer", "reviver", "healer", "attacker", "attacker_userid"]);
    local subject = DHUD_EventPlayerTrackedFirst(params, ["subject", "victim", "target"]);

    if (DHUD_IsTracked(actor) && !DHUD_SameEntity(actor, subject))
    {
        if (!DHUD_EntityActionDedupe("revive", actor, subject, params, 1.00))
        {
            ::DHUD_REVIVES += 1;
            ::DHUD_SKIP_STAT_REVIVE += 1;
            DHUD_ScoreDelta(DHUD_Rule("revive", 5.0), "Revive success " + DHUD_Fmt1(DHUD_Rule("revive", 5.0)));
        }
    }
    else if (DHUD_IsTracked(subject) && !DHUD_IsTracked(actor))
    {
        ::DHUD_RESCUED_BY_TEAM += 1;
        DHUD_Remember("Revived by teammate");
    }
    DHUD_Write(true);
}


function OnGameEvent_heal_success(params)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, ["userid", "healer", "attacker", "attacker_userid"]);
    local subject = DHUD_EventPlayerTrackedFirst(params, ["subject", "victim", "target"]);
    if (DHUD_IsTracked(actor) || DHUD_IsTracked(subject) || actor == null) DHUD_SuppressAttackFallback(5.5, "");
    local restoredEvent = DHUD_EventInt(params, "health_restored", 0);

    if (DHUD_IsTracked(actor))
    {
        if (!DHUD_EntityActionDedupe("heal", actor, subject, params, 4.50) && DHUD_Now() - ::DHUD_LAST_HEAL_TIME > 4.50)
        {
            ::DHUD_HEALS += 1;
            ::DHUD_SKIP_STAT_HEAL += 1;
            ::DHUD_LAST_HEAL_TIME = DHUD_Now();
            if (DHUD_SameEntity(actor, subject) || subject == null)
            {
                local restored = restoredEvent;
                local oldHp = ::DHUD_POLL_HP;
                local curHp = DHUD_SurvivorHealth(actor);
                if (oldHp > 0 && curHp > oldHp) restored = curHp - oldHp;
                else if (oldHp > 0)
                {
                    local maxHp = DHUD_MaxHealth(actor, 100);
                    local missing = maxHp - oldHp;
                    if (missing < 0) missing = 0;
                    if (restored <= 0 || restored > missing) restored = missing;
                }
                if (restored <= 0) restored = 1;
                if (restored > 100) restored = 100;
                DHUD_AddSelfHealHP(restored, "Self heal");
                local hs = DHUD_Rule("heal", -3.0);
                DHUD_ScoreDelta(hs, "Self heal +" + restored + " HP / score " + DHUD_Fmt1(hs));
                if (curHp > 0) ::DHUD_POLL_HP = curHp;
            }
            else
            {
                if (restoredEvent > 0) ::DHUD_HEAL_HP_TEAM += restoredEvent;
                local ths = DHUD_Rule("heal", -3.0);
                DHUD_ScoreDelta(ths, "Teammate healed / score " + DHUD_Fmt1(ths));
            }
        }
    }
    else if (DHUD_IsTracked(subject))
    {
        if (!DHUD_EntityActionDedupe("healed_by_team", actor, subject, params, 4.50) && DHUD_Now() - ::DHUD_LAST_HEAL_TIME > 4.50)
        {
            ::DHUD_HEALED_BY_TEAM += 1;
            ::DHUD_LAST_HEAL_TIME = DHUD_Now();
            DHUD_Remember("Healed by teammate");
            local tracked = DHUD_TrackedPlayer(true);
            if (tracked != null) ::DHUD_POLL_HP = DHUD_SurvivorHealth(tracked);
        }
    }
    DHUD_Write(true);
}







function OnGameEvent_pills_used(params)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, ["userid", "subject", "player"]);
    if (DHUD_IsTracked(actor) && !DHUD_EntityActionDedupe("pills", actor, null, params, 0.80))
    {
        ::DHUD_PILLS += 1;
        ::DHUD_SKIP_STAT_PILLS += 1;
        ::DHUD_HEALS += 1;
        DHUD_AddSelfHealHP(20, "Pills temp HP");
        local ps = DHUD_Rule("pills", -1.5);
        DHUD_ScoreDelta(ps, "Pills used / score " + DHUD_Fmt1(ps));
    }
    DHUD_Write(true);
}



function OnGameEvent_adrenaline_used(params)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, ["userid", "subject", "player"]);
    if (DHUD_IsTracked(actor) && !DHUD_EntityActionDedupe("adrenaline", actor, null, params, 0.80))
    {
        ::DHUD_ADRENALINE += 1;
        ::DHUD_SKIP_STAT_ADRENALINE += 1;
        ::DHUD_HEALS += 1;
        DHUD_AddSelfHealHP(25, "Adrenaline temp HP");
        local adr = DHUD_Rule("adrenaline", -1.5);
        DHUD_ScoreDelta(adr, "Adrenaline used / score " + DHUD_Fmt1(adr));
    }
    DHUD_Write(true);
}



function OnGameEvent_melee_kill(params)
{
    local actor = DHUD_ExplicitActor(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "killer", "killer_userid", "killeruserid", "killerid", "userid", "player", "player_userid"]);
    DHUD_AddCommonKill(params, actor, "Melee kill");
    DHUD_Write(true);
}


function DHUD_ItemName(params)
{
    local name = "item";
    try { name = params["item"]; } catch(e) {}
    try { name = params["weapon"]; } catch(e2) {}
    return DHUD_Escape(name);
}

function DHUD_CustomDedupe(key, cooldown)
{
    if (!("DHUD_ACTION_SEEN" in getroottable())) ::DHUD_ACTION_SEEN <- {};
    local now = DHUD_Now();
    try
    {
        if (key in ::DHUD_ACTION_SEEN && now - ::DHUD_ACTION_SEEN[key] < cooldown) return true;
        ::DHUD_ACTION_SEEN[key] <- now;
    }
    catch(e) {}
    return false;
}

function DHUD_RecordSupplyPickup(params, reason)
{
    if (!DHUD_ScoringActive()) { DHUD_Write(true); return; }
    local actor = DHUD_ActorOrRecentTracked(params, ["userid", "player", "player_userid", "attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id"], true);
    local subjectIsTracked = DHUD_ParamMatchesTracked(params, ["subject", "victim", "target", "receiver", "recipient"]);
    local giver = DHUD_EventPlayerAny(params, ["giver", "giver_userid", "giveruserid", "donor", "donor_userid", "old_owner", "oldowner", "source"]);

    if (!DHUD_IsTracked(actor))
    {
        if (subjectIsTracked) DHUD_Remember("Supply received from teammate");
        DHUD_Write(true);
        return;
    }

    if (giver != null && !DHUD_IsTracked(giver))
    {
        DHUD_Remember("Supply received from teammate");
        DHUD_Write(true);
        return;
    }
    try
    {
        if (("block_supply_given" in ::DHUD_ACTION_SEEN && DHUD_Now() - ::DHUD_ACTION_SEEN["block_supply_given"] < 3.5) || (DHUD_Now() - ::DHUD_LAST_GIVEN_TO_TRACKED_TIME < 3.5))
        {
            DHUD_Remember("Supply received from teammate");
            DHUD_Write(true);
            return;
        }
    }
    catch(e_block_supply) {}


    local item = DHUD_ItemName(params);
    local key = "supply|a=" + DHUD_EntityIndex(actor) + "|i=" + item + "|t=" + ((DHUD_Now() * 4).tointeger());
    if (!DHUD_CustomDedupe(key, 0.25) && DHUD_Now() - ::DHUD_LAST_SUPPLY_TIME > 0.20)
    {
        local add = DHUD_SupplyScore(item, reason);
        DHUD_AddSupplyScore(item, reason, add);
    }
    else
    {
        DHUD_Remember("Supply duplicate ignored");
    }
    DHUD_Write(true);
}
function DHUD_RecordSupplyGiven(params)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, ["userid", "giver", "giver_userid", "donor", "attacker", "attacker_userid"]);
    local subject = DHUD_EventPlayerTrackedFirst(params, ["subject", "victim", "target", "receiver", "recipient", "player", "player_userid"]);
    if (DHUD_IsTracked(subject) && !DHUD_IsTracked(actor))
    {
        ::DHUD_LAST_SUPPLY_BLOCK_TIME = DHUD_Now();
        ::DHUD_LAST_GIVEN_TO_TRACKED_TIME = DHUD_Now();
        try { ::DHUD_ACTION_SEEN["block_supply_given"] <- DHUD_Now(); } catch(e) {}
        DHUD_Remember("Supply received from teammate");
    }
    DHUD_Write(true);
}

function OnGameEvent_weapon_given(params) { DHUD_RecordSupplyGiven(params); }
function OnGameEvent_item_given(params) { DHUD_RecordSupplyGiven(params); }
function OnGameEvent_player_give_item(params) { DHUD_RecordSupplyGiven(params); }
function OnGameEvent_spawner_give_item(params) { DHUD_RecordSupplyPickup(params, "Spawner item"); }

function OnGameEvent_item_pickup(params) { DHUD_RecordSupplyPickup(params, "Supply pickup"); }
function OnGameEvent_weapon_pickup(params) { DHUD_RecordSupplyPickup(params, "Weapon pickup"); }
function OnGameEvent_ammo_pickup(params) { DHUD_RecordSupplyPickup(params, "Ammo pickup"); }
function OnGameEvent_upgrade_pack_added(params) { DHUD_RecordSupplyPickup(params, "Ammo upgrade pickup"); }
function OnGameEvent_upgrade_pack_used(params) { DHUD_RecordSupplyPickup(params, "Ammo upgrade used"); }
function OnGameEvent_player_use(params)
{
    local useActor = DHUD_EventPlayerTrackedFirst(params, ["userid", "player", "player_userid", "attacker", "attacker_userid"]);
    if (DHUD_IsTracked(useActor)) ::DHUD_LAST_USE_BUTTON_TIME = DHUD_Now();
    local item = DHUD_ItemName(params);
    if (item == "item")
    {
        try
        {
            local t = DHUD_EntityFromParam(params, "targetid");
            if (t != null) item = t.GetClassname();
        }
        catch(e_target_item) {}
    }
    local low = item;
    try { low = low.tolower(); } catch(e_low) {}
    if (item == "item") { DHUD_Write(true); return; }
    if (!(DHUD_TextContains(low, "weapon") || DHUD_TextContains(low, "ammo") || DHUD_TextContains(low, "first_aid") || DHUD_TextContains(low, "pills") || DHUD_TextContains(low, "adrenaline") || DHUD_TextContains(low, "molotov") || DHUD_TextContains(low, "pipe_bomb") || DHUD_TextContains(low, "vomitjar") || DHUD_TextContains(low, "melee")))
    {
        DHUD_Write(true);
        return;
    }
    DHUD_RecordSupplyPickup(params, "Use item");
}
function OnGameEvent_infected_hurt(params)
{
    DHUD_RecordEnemyDamage(params, "Common damage");
    DHUD_Write(true);
}

function OnGameEvent_witch_hurt(params)
{
    local actor = DHUD_ActorOrRecentTracked(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "userid", "player", "player_userid"], true);
    if (DHUD_IsTracked(actor))
    {
        ::DHUD_LAST_WITCH_HURT_TIME = DHUD_Now();
        ::DHUD_LAST_WITCH_HURT_ACTOR = DHUD_EntityIndex(actor);
    }
    DHUD_RecordEnemyDamage(params, "Witch damage");
    DHUD_Write(true);
}

function OnGameEvent_tank_hurt(params)
{
    local actor = DHUD_ActorOrRecentTracked(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "userid", "player", "player_userid"], true);
    if (DHUD_IsTracked(actor))
    {
        ::DHUD_LAST_TANK_HURT_TIME = DHUD_Now();
        ::DHUD_LAST_TANK_HURT_ACTOR = DHUD_EntityIndex(actor);
    }
    DHUD_RecordEnemyDamage(params, "Tank damage");
    DHUD_Write(true);
}

function OnGameEvent_zombie_death(params) { OnGameEvent_infected_death(params); }


function OnGameEvent_special_killed(params)
{
    local actor = DHUD_KillActorOrRecentTracked(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "player", "player_userid"]);
    local victim = DHUD_EventEntityAny(params, ["victim", "subject", "target", "entityid", "entindex", "infected_id", "witchid", "tankid"]);
    if (!DHUD_IsTracked(actor) && DHUD_RecentTrackedDamageTo(victim, 4.00)) actor = DHUD_TrackedPlayer(true);
    local kind = DHUD_InfectedKind(params, victim);
    if (kind == "witch" || kind == "tank")
    {
        if (DHUD_Now() - ::DHUD_LAST_BOSS_KILL_TIME < 1.00) { DHUD_Write(true); return; }
    }
    if (kind == "") kind = "special";
    DHUD_AddSpecialKill(params, actor, victim, kind, "Special infected killed");
    DHUD_Write(true);
}





function DHUD_OfficialSpecialKill(params, label)
{
    local actor = DHUD_KillActorOrRecentTracked(params, ["userid", "attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "killer", "killer_userid", "killeruserid", "killerid", "player", "player_userid"]);
    local victim = DHUD_EventEntityAny(params, ["victim", "subject", "target", "entityid", "entindex", "infected_id"]);
    if (!DHUD_IsTracked(actor) && DHUD_RecentTrackedDamageTo(victim, 4.00)) actor = DHUD_TrackedPlayer(true);
    DHUD_AddSpecialKill(params, actor, victim, "special", label);
    DHUD_Write(true);
}




function OnGameEvent_charger_killed(params) { DHUD_OfficialSpecialKill(params, "Charger killed"); }
function OnGameEvent_spitter_killed(params) { DHUD_OfficialSpecialKill(params, "Spitter killed"); }
function OnGameEvent_jockey_killed(params) { DHUD_OfficialSpecialKill(params, "Jockey killed"); }
function OnGameEvent_hunter_killed(params) { DHUD_OfficialSpecialKill(params, "Hunter killed"); }
function OnGameEvent_smoker_killed(params) { DHUD_OfficialSpecialKill(params, "Smoker killed"); }
function OnGameEvent_boomer_killed(params) { DHUD_OfficialSpecialKill(params, "Boomer killed"); }
function OnGameEvent_spider_killed(params) { DHUD_OfficialSpecialKill(params, "Spider killed"); }


function OnGameEvent_boomer_exploded(params)
{
    local actor = DHUD_KillActorOrRecentTracked(params, ["userid", "attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "killer", "killer_userid", "killeruserid", "killerid", "player", "player_userid"]);
    local victim = DHUD_EventEntityAny(params, ["victim", "subject", "target", "entityid", "entindex", "infected_id"]);
    if (!DHUD_IsTracked(actor) && DHUD_RecentTrackedDamageTo(victim, 4.00)) actor = DHUD_TrackedPlayer(true);
    if (DHUD_IsTracked(actor)) DHUD_AddSpecialKill(params, actor, victim, "special", "Boomer killed");
    DHUD_Write(true);
}




function OnGameEvent_ammo_pack_used(params) { DHUD_RecordSupplyPickup(params, "Ammo pack used"); }
function OnGameEvent_give_weapon(params) { DHUD_RecordSupplyGiven(params); }
function OnGameEvent_weapon_drop(params) { DHUD_Write(true); }
function OnGameEvent_receive_upgrade(params) { DHUD_RecordSupplyPickup(params, "Ammo upgrade received"); }
function OnGameEvent_upgrade_incendiary_ammo(params) { DHUD_RecordSupplyPickup(params, "Incendiary ammo"); }
function OnGameEvent_upgrade_explosive_ammo(params) { DHUD_RecordSupplyPickup(params, "Explosive ammo"); }
function OnGameEvent_player_incapacitated_start(params) { OnGameEvent_player_incapacitated(params); }

function OnGameEvent_revive_begin(params) { DHUD_Write(true); }
function OnGameEvent_heal_begin(params)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, ["userid", "healer", "attacker", "attacker_userid"]);
    local subject = DHUD_EventPlayerTrackedFirst(params, ["subject", "victim", "target"]);
    if (DHUD_IsTracked(actor) || DHUD_IsTracked(subject) || actor == null) DHUD_SuppressAttackFallback(6.5, "");
    DHUD_Write(true);
}
function OnGameEvent_player_used_first_aid(params) { OnGameEvent_heal_success(params); }
function OnGameEvent_player_use_item(params) { DHUD_RecordSupplyPickup(params, "Use item"); }
function OnGameEvent_entity_hurt(params) { DHUD_RecordEnemyDamage(params, "Entity damage"); DHUD_Write(true); }

function OnGameEvent_weapon_fire(params)
{
    local actor = DHUD_EventPlayerTrackedFirst(params, ["userid", "player", "player_userid", "attacker", "attacker_userid"]);
    if (DHUD_IsTracked(actor)) DHUD_MarkLocalAttack();
    DHUD_Write(true);
}

function OnGameEvent_player_hurt_concise(params) { OnGameEvent_player_hurt(params); }
function OnGameEvent_non_pistol_fired(params) { OnGameEvent_weapon_fire(params); }
function OnGameEvent_non_melee_fired(params) { OnGameEvent_weapon_fire(params); }
function OnGameEvent_weapon_fire_at_40(params) { OnGameEvent_weapon_fire(params); }


function OnGameEvent_infected_decapitated(params)
{
    local actor = DHUD_ExplicitActor(params, ["attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "killer", "killer_userid", "killeruserid", "killerid", "userid", "player", "player_userid"]);
    DHUD_AddCommonKill(params, actor, "Infected decapitated");
    DHUD_Write(true);
}



function OnGameEvent_player_spawn(params) { DHUD_Register(); DHUD_Write(true); }
function OnGameEvent_tank_spawn(params) { DHUD_Write(true); }
function OnGameEvent_witch_spawn(params) { DHUD_Write(true); }
function OnGameEvent_mission_lost(params) { DHUD_ScoreDelta(-12, "Mission lost -12"); DHUD_Write(true); }
function OnGameEvent_map_transition(params) { ::DHUD_PRESERVE_NEXT_ROUND = true; DHUD_Remember("Map transition: score kept"); try { DHUD_SaveScoreState(); } catch(e_save_map) {} DHUD_Write(true); }
function OnGameEvent_finale_win(params) { DHUD_ScoreDelta(6, "Finale clear +6"); ::DHUD_PRESERVE_NEXT_ROUND = false; try { DHUD_ClearScoreState(); } catch(e_clear_finale) {} DHUD_Write(true); }



function DHUD_EventDedupeKey(name, params)
{
    local key = name;
    local keys = ["userid", "player", "player_userid", "attacker", "attacker_userid", "attackeruserid", "attackerid", "attacker_id", "attackerentid", "attackerentindex", "killer", "killer_userid", "killeruserid", "killerid", "victim", "victim_userid", "subject", "rescuer", "reviver", "healer", "target", "receiver", "recipient", "entityid", "entindex", "infected_id", "tankid", "witchid", "dmg_health", "damage", "amount", "dmg", "type", "zombieclass", "zombie_class", "victimname", "classname", "weapon", "item", "has_spit", "melee", "charging", "solo", "oneshot", "giver", "giver_userid", "giveruserid", "donor", "source"];
    foreach (k in keys)
    {
        try { key += "|" + k + "=" + params[k]; } catch(e) {}
    }
    try
    {
        local tbScale = 20.0;
        if (name == "infected_death" || name == "zombie_death" || name == "melee_kill" || name == "infected_decapitated") tbScale = 200.0;
        key += "|tb=" + ((Time() * tbScale).tointeger());
    }
    catch(e2) {}
    return key;
}

function DHUD_DispatchGameEvent(name, params)
{
    if (!("DHUD_EVENT_SEEN" in getroottable())) ::DHUD_EVENT_SEEN <- {};
    local k = DHUD_EventDedupeKey(name, params);
    try
    {
        if (k in ::DHUD_EVENT_SEEN) return;
        ::DHUD_EVENT_SEEN[k] <- DHUD_Now();
    }
    catch(e) {}

    try
    {
        local now = DHUD_Now();
        foreach (oldk, oldt in ::DHUD_EVENT_SEEN)
        {
            if (now - oldt > 2.0) delete ::DHUD_EVENT_SEEN[oldk];
        }
    }
    catch(e2) {}

    try { ::DHUD_EVENTS_SEEN += 1; } catch(e_seen) {}
    DHUD_DebugEvent(name, params);
    try
    {
        if (name != "round_start" && name != "player_spawn" && name != "revive_begin" && name != "heal_begin" && name != "tank_spawn" && name != "witch_spawn" && name != "map_transition")
        {
            ::DHUD_EVENT_REAL_SEEN += 1;
            ::DHUD_LAST_REAL_EVENT_TIME = DHUD_Now();
        }
    }
    catch(e_real) {}

    if (name == "round_start") OnGameEvent_round_start(params);
    else if (name == "player_hurt") OnGameEvent_player_hurt(params);
    else if (name == "player_hurt_concise") OnGameEvent_player_hurt_concise(params);
    else if (name == "player_incapacitated") OnGameEvent_player_incapacitated(params);
    else if (name == "player_ledge_grab") OnGameEvent_player_ledge_grab(params);
    else if (name == "player_ledge_release") DHUD_Write(true);
    else if (name == "player_death") OnGameEvent_player_death(params);
    else if (name == "infected_death") OnGameEvent_infected_death(params);
    else if (name == "infected_hurt") OnGameEvent_infected_hurt(params);
    else if (name == "entity_hurt") OnGameEvent_entity_hurt(params);
    else if (name == "weapon_fire") OnGameEvent_weapon_fire(params);
    else if (name == "non_pistol_fired") OnGameEvent_non_pistol_fired(params);
    else if (name == "non_melee_fired") OnGameEvent_non_melee_fired(params);
    else if (name == "weapon_fire_at_40") OnGameEvent_weapon_fire_at_40(params);
    else if (name == "player_used_first_aid") OnGameEvent_player_used_first_aid(params);
    else if (name == "player_use_item") OnGameEvent_player_use_item(params);
    else if (name == "player_give_item") OnGameEvent_player_give_item(params);
    else if (name == "witch_hurt") OnGameEvent_witch_hurt(params);
    else if (name == "tank_hurt") OnGameEvent_tank_hurt(params);
    else if (name == "witch_killed") OnGameEvent_witch_killed(params);
    else if (name == "tank_killed") OnGameEvent_tank_killed(params);
    else if (name == "charger_killed") OnGameEvent_charger_killed(params);
    else if (name == "spitter_killed") OnGameEvent_spitter_killed(params);
    else if (name == "jockey_killed") OnGameEvent_jockey_killed(params);
    else if (name == "hunter_killed") OnGameEvent_hunter_killed(params);
    else if (name == "smoker_killed") OnGameEvent_smoker_killed(params);
    else if (name == "boomer_killed") OnGameEvent_boomer_killed(params);
    else if (name == "spider_killed") OnGameEvent_spider_killed(params);
    else if (name == "boomer_exploded") OnGameEvent_boomer_exploded(params);
    else if (name == "ammo_pack_used") OnGameEvent_ammo_pack_used(params);
    else if (name == "give_weapon") OnGameEvent_give_weapon(params);
    else if (name == "weapon_drop") OnGameEvent_weapon_drop(params);
    else if (name == "receive_upgrade") OnGameEvent_receive_upgrade(params);
    else if (name == "upgrade_incendiary_ammo") OnGameEvent_upgrade_incendiary_ammo(params);
    else if (name == "upgrade_explosive_ammo") OnGameEvent_upgrade_explosive_ammo(params);
    else if (name == "player_incapacitated_start") OnGameEvent_player_incapacitated_start(params);
    else if (name == "rescue_survivor") OnGameEvent_rescue_survivor(params);
    else if (name == "survivor_rescued") OnGameEvent_survivor_rescued(params);
    else if (name == "revive_success") OnGameEvent_revive_success(params);
    else if (name == "heal_success") OnGameEvent_heal_success(params);
    else if (name == "pills_used") OnGameEvent_pills_used(params);
    else if (name == "adrenaline_used") OnGameEvent_adrenaline_used(params);
    else if (name == "melee_kill") OnGameEvent_melee_kill(params);
    else if (name == "infected_decapitated") OnGameEvent_infected_decapitated(params);
    else if (name == "spawner_give_item") OnGameEvent_spawner_give_item(params);
    else if (name == "item_pickup") OnGameEvent_item_pickup(params);
    else if (name == "weapon_pickup") OnGameEvent_weapon_pickup(params);
    else if (name == "weapon_given") OnGameEvent_weapon_given(params);
    else if (name == "item_given") OnGameEvent_item_given(params);
    else if (name == "ammo_pickup") OnGameEvent_ammo_pickup(params);
    else if (name == "upgrade_pack_added") OnGameEvent_upgrade_pack_added(params);
    else if (name == "upgrade_pack_used") OnGameEvent_upgrade_pack_used(params);
    else if (name == "player_use") OnGameEvent_player_use(params);
    else if (name == "zombie_death") OnGameEvent_zombie_death(params);
    else if (name == "special_killed") OnGameEvent_special_killed(params);
    else if (name == "revive_begin") OnGameEvent_revive_begin(params);
    else if (name == "heal_begin") OnGameEvent_heal_begin(params);
    else if (name == "player_spawn") OnGameEvent_player_spawn(params);
    else if (name == "tank_spawn") OnGameEvent_tank_spawn(params);
    else if (name == "witch_spawn") OnGameEvent_witch_spawn(params);
    else if (name == "mission_lost") OnGameEvent_mission_lost(params);
    else if (name == "map_transition") OnGameEvent_map_transition(params);
    else if (name == "finale_win") OnGameEvent_finale_win(params);
    else DHUD_Write(true);
}

::DHUD_DispatchGameEvent <- DHUD_DispatchGameEvent;

function DHUD_BuildEventScope()
{
    local ev = {};

    ev.OnGameEvent_round_start <- function(params) { ::DHUD_DispatchGameEvent("round_start", params); };
    ev.OnGameEvent_player_hurt <- function(params) { ::DHUD_DispatchGameEvent("player_hurt", params); };
    ev.OnGameEvent_player_hurt_concise <- function(params) { ::DHUD_DispatchGameEvent("player_hurt_concise", params); };
    ev.OnGameEvent_player_incapacitated <- function(params) { ::DHUD_DispatchGameEvent("player_incapacitated", params); };
    ev.OnGameEvent_player_ledge_grab <- function(params) { ::DHUD_DispatchGameEvent("player_ledge_grab", params); };
    ev.OnGameEvent_player_death <- function(params) { ::DHUD_DispatchGameEvent("player_death", params); };
    ev.OnGameEvent_infected_death <- function(params) { ::DHUD_DispatchGameEvent("infected_death", params); };
    ev.OnGameEvent_infected_hurt <- function(params) { ::DHUD_DispatchGameEvent("infected_hurt", params); };
    ev.OnGameEvent_entity_hurt <- function(params) { ::DHUD_DispatchGameEvent("entity_hurt", params); };
    ev.OnGameEvent_weapon_fire <- function(params) { ::DHUD_DispatchGameEvent("weapon_fire", params); };
    ev.OnGameEvent_non_pistol_fired <- function(params) { ::DHUD_DispatchGameEvent("non_pistol_fired", params); };
    ev.OnGameEvent_non_melee_fired <- function(params) { ::DHUD_DispatchGameEvent("non_melee_fired", params); };
    ev.OnGameEvent_weapon_fire_at_40 <- function(params) { ::DHUD_DispatchGameEvent("weapon_fire_at_40", params); };
    ev.OnGameEvent_player_used_first_aid <- function(params) { ::DHUD_DispatchGameEvent("player_used_first_aid", params); };
    ev.OnGameEvent_player_use_item <- function(params) { ::DHUD_DispatchGameEvent("player_use_item", params); };
    ev.OnGameEvent_player_give_item <- function(params) { ::DHUD_DispatchGameEvent("player_give_item", params); };
    ev.OnGameEvent_witch_hurt <- function(params) { ::DHUD_DispatchGameEvent("witch_hurt", params); };
    ev.OnGameEvent_tank_hurt <- function(params) { ::DHUD_DispatchGameEvent("tank_hurt", params); };
    ev.OnGameEvent_witch_killed <- function(params) { ::DHUD_DispatchGameEvent("witch_killed", params); };
    ev.OnGameEvent_tank_killed <- function(params) { ::DHUD_DispatchGameEvent("tank_killed", params); };
    ev.OnGameEvent_charger_killed <- function(params) { ::DHUD_DispatchGameEvent("charger_killed", params); };
    ev.OnGameEvent_spitter_killed <- function(params) { ::DHUD_DispatchGameEvent("spitter_killed", params); };
    ev.OnGameEvent_jockey_killed <- function(params) { ::DHUD_DispatchGameEvent("jockey_killed", params); };
    ev.OnGameEvent_hunter_killed <- function(params) { ::DHUD_DispatchGameEvent("hunter_killed", params); };
    ev.OnGameEvent_smoker_killed <- function(params) { ::DHUD_DispatchGameEvent("smoker_killed", params); };
    ev.OnGameEvent_boomer_killed <- function(params) { ::DHUD_DispatchGameEvent("boomer_killed", params); };
    ev.OnGameEvent_spider_killed <- function(params) { ::DHUD_DispatchGameEvent("spider_killed", params); };
    ev.OnGameEvent_boomer_exploded <- function(params) { ::DHUD_DispatchGameEvent("boomer_exploded", params); };
    ev.OnGameEvent_ammo_pack_used <- function(params) { ::DHUD_DispatchGameEvent("ammo_pack_used", params); };
    ev.OnGameEvent_give_weapon <- function(params) { ::DHUD_DispatchGameEvent("give_weapon", params); };
    ev.OnGameEvent_weapon_drop <- function(params) { ::DHUD_DispatchGameEvent("weapon_drop", params); };
    ev.OnGameEvent_receive_upgrade <- function(params) { ::DHUD_DispatchGameEvent("receive_upgrade", params); };
    ev.OnGameEvent_upgrade_incendiary_ammo <- function(params) { ::DHUD_DispatchGameEvent("upgrade_incendiary_ammo", params); };
    ev.OnGameEvent_upgrade_explosive_ammo <- function(params) { ::DHUD_DispatchGameEvent("upgrade_explosive_ammo", params); };
    ev.OnGameEvent_player_incapacitated_start <- function(params) { ::DHUD_DispatchGameEvent("player_incapacitated_start", params); };
    ev.OnGameEvent_rescue_survivor <- function(params) { ::DHUD_DispatchGameEvent("rescue_survivor", params); };
    ev.OnGameEvent_survivor_rescued <- function(params) { ::DHUD_DispatchGameEvent("survivor_rescued", params); };
    ev.OnGameEvent_revive_success <- function(params) { ::DHUD_DispatchGameEvent("revive_success", params); };
    ev.OnGameEvent_heal_success <- function(params) { ::DHUD_DispatchGameEvent("heal_success", params); };
    ev.OnGameEvent_pills_used <- function(params) { ::DHUD_DispatchGameEvent("pills_used", params); };
    ev.OnGameEvent_adrenaline_used <- function(params) { ::DHUD_DispatchGameEvent("adrenaline_used", params); };
    ev.OnGameEvent_melee_kill <- function(params) { ::DHUD_DispatchGameEvent("melee_kill", params); };
    ev.OnGameEvent_infected_decapitated <- function(params) { ::DHUD_DispatchGameEvent("infected_decapitated", params); };
    ev.OnGameEvent_item_pickup <- function(params) { ::DHUD_DispatchGameEvent("item_pickup", params); };
    ev.OnGameEvent_weapon_pickup <- function(params) { ::DHUD_DispatchGameEvent("weapon_pickup", params); };
    ev.OnGameEvent_weapon_given <- function(params) { ::DHUD_DispatchGameEvent("weapon_given", params); };
    ev.OnGameEvent_item_given <- function(params) { ::DHUD_DispatchGameEvent("item_given", params); };
    ev.OnGameEvent_ammo_pickup <- function(params) { ::DHUD_DispatchGameEvent("ammo_pickup", params); };
    ev.OnGameEvent_upgrade_pack_added <- function(params) { ::DHUD_DispatchGameEvent("upgrade_pack_added", params); };
    ev.OnGameEvent_upgrade_pack_used <- function(params) { ::DHUD_DispatchGameEvent("upgrade_pack_used", params); };
    ev.OnGameEvent_player_use <- function(params) { ::DHUD_DispatchGameEvent("player_use", params); };
    ev.OnGameEvent_zombie_death <- function(params) { ::DHUD_DispatchGameEvent("zombie_death", params); };
    ev.OnGameEvent_special_killed <- function(params) { ::DHUD_DispatchGameEvent("special_killed", params); };
    ev.OnGameEvent_revive_begin <- function(params) { ::DHUD_DispatchGameEvent("revive_begin", params); };
    ev.OnGameEvent_heal_begin <- function(params) { ::DHUD_DispatchGameEvent("heal_begin", params); };
    ev.OnGameEvent_player_spawn <- function(params) { ::DHUD_DispatchGameEvent("player_spawn", params); };
    ev.OnGameEvent_tank_spawn <- function(params) { ::DHUD_DispatchGameEvent("tank_spawn", params); };
    ev.OnGameEvent_witch_spawn <- function(params) { ::DHUD_DispatchGameEvent("witch_spawn", params); };
    ev.OnGameEvent_mission_lost <- function(params) { ::DHUD_DispatchGameEvent("mission_lost", params); };
    ev.OnGameEvent_map_transition <- function(params) { ::DHUD_DispatchGameEvent("map_transition", params); };
    ev.OnGameEvent_spawner_give_item <- function(params) { ::DHUD_DispatchGameEvent("spawner_give_item", params); };
    ev.OnGameEvent_player_ledge_release <- function(params) { ::DHUD_DispatchGameEvent("player_ledge_release", params); };
    ev.OnGameEvent_finale_win <- function(params) { ::DHUD_DispatchGameEvent("finale_win", params); };

    return ev;
}

try { DHUD_LoadScoreState(); } catch(e_autoload_state) {}
DHUD_RegisterEvents();
DHUD_Register();
DHUD_Write(true);
