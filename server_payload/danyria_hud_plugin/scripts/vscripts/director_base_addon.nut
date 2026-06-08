try { IncludeScript("danyria_autoload"); } catch(e) { printl("[DHUD] addon hook failed: " + e); }

function DHUD_ForwardEvent(name, params)
{
    try
    {
        if (!("DHUD_DispatchGameEvent" in getroottable())) IncludeScript("danyria_autoload");
    }
    catch(e) {}
    try
    {
        if ("DHUD_DispatchGameEvent" in getroottable()) ::DHUD_DispatchGameEvent(name, params);
    }
    catch(e2)
    {
        try { printl("[DHUD] event forward failed: " + name + " / " + e2); } catch(e3) {}
    }
}

function OnGameEvent_round_start(params) { DHUD_ForwardEvent("round_start", params); }
function OnGameEvent_player_hurt(params) { DHUD_ForwardEvent("player_hurt", params); }
function OnGameEvent_player_hurt_concise(params) { DHUD_ForwardEvent("player_hurt_concise", params); }
function OnGameEvent_player_incapacitated(params) { DHUD_ForwardEvent("player_incapacitated", params); }
function OnGameEvent_player_ledge_grab(params) { DHUD_ForwardEvent("player_ledge_grab", params); }
function OnGameEvent_player_death(params) { DHUD_ForwardEvent("player_death", params); }
function OnGameEvent_infected_death(params) { DHUD_ForwardEvent("infected_death", params); }
function OnGameEvent_infected_hurt(params) { DHUD_ForwardEvent("infected_hurt", params); }
function OnGameEvent_entity_hurt(params) { DHUD_ForwardEvent("entity_hurt", params); }
function OnGameEvent_witch_hurt(params) { DHUD_ForwardEvent("witch_hurt", params); }
function OnGameEvent_tank_hurt(params) { DHUD_ForwardEvent("tank_hurt", params); }
function OnGameEvent_weapon_fire(params) { DHUD_ForwardEvent("weapon_fire", params); }
function OnGameEvent_non_pistol_fired(params) { DHUD_ForwardEvent("non_pistol_fired", params); }
function OnGameEvent_non_melee_fired(params) { DHUD_ForwardEvent("non_melee_fired", params); }
function OnGameEvent_weapon_fire_at_40(params) { DHUD_ForwardEvent("weapon_fire_at_40", params); }
function OnGameEvent_player_used_first_aid(params) { DHUD_ForwardEvent("player_used_first_aid", params); }
function OnGameEvent_player_use_item(params) { DHUD_ForwardEvent("player_use_item", params); }
function OnGameEvent_player_give_item(params) { DHUD_ForwardEvent("player_give_item", params); }
function OnGameEvent_witch_killed(params) { DHUD_ForwardEvent("witch_killed", params); }
function OnGameEvent_tank_killed(params) { DHUD_ForwardEvent("tank_killed", params); }
function OnGameEvent_charger_killed(params) { DHUD_ForwardEvent("charger_killed", params); }
function OnGameEvent_spitter_killed(params) { DHUD_ForwardEvent("spitter_killed", params); }
function OnGameEvent_jockey_killed(params) { DHUD_ForwardEvent("jockey_killed", params); }
function OnGameEvent_boomer_exploded(params) { DHUD_ForwardEvent("boomer_exploded", params); }
function OnGameEvent_ammo_pack_used(params) { DHUD_ForwardEvent("ammo_pack_used", params); }
function OnGameEvent_give_weapon(params) { DHUD_ForwardEvent("give_weapon", params); }
function OnGameEvent_weapon_drop(params) { DHUD_ForwardEvent("weapon_drop", params); }
function OnGameEvent_receive_upgrade(params) { DHUD_ForwardEvent("receive_upgrade", params); }
function OnGameEvent_upgrade_incendiary_ammo(params) { DHUD_ForwardEvent("upgrade_incendiary_ammo", params); }
function OnGameEvent_upgrade_explosive_ammo(params) { DHUD_ForwardEvent("upgrade_explosive_ammo", params); }
function OnGameEvent_player_incapacitated_start(params) { DHUD_ForwardEvent("player_incapacitated_start", params); }
function OnGameEvent_rescue_survivor(params) { DHUD_ForwardEvent("rescue_survivor", params); }
function OnGameEvent_survivor_rescued(params) { DHUD_ForwardEvent("survivor_rescued", params); }
function OnGameEvent_revive_success(params) { DHUD_ForwardEvent("revive_success", params); }
function OnGameEvent_heal_success(params) { DHUD_ForwardEvent("heal_success", params); }
function OnGameEvent_pills_used(params) { DHUD_ForwardEvent("pills_used", params); }
function OnGameEvent_adrenaline_used(params) { DHUD_ForwardEvent("adrenaline_used", params); }
function OnGameEvent_melee_kill(params) { DHUD_ForwardEvent("melee_kill", params); }
function OnGameEvent_infected_decapitated(params) { DHUD_ForwardEvent("infected_decapitated", params); }
function OnGameEvent_item_pickup(params) { DHUD_ForwardEvent("item_pickup", params); }
function OnGameEvent_weapon_pickup(params) { DHUD_ForwardEvent("weapon_pickup", params); }
function OnGameEvent_weapon_given(params) { DHUD_ForwardEvent("weapon_given", params); }
function OnGameEvent_item_given(params) { DHUD_ForwardEvent("item_given", params); }
function OnGameEvent_ammo_pickup(params) { DHUD_ForwardEvent("ammo_pickup", params); }
function OnGameEvent_upgrade_pack_added(params) { DHUD_ForwardEvent("upgrade_pack_added", params); }
function OnGameEvent_upgrade_pack_used(params) { DHUD_ForwardEvent("upgrade_pack_used", params); }
function OnGameEvent_player_use(params) { DHUD_ForwardEvent("player_use", params); }
function OnGameEvent_zombie_death(params) { DHUD_ForwardEvent("zombie_death", params); }
function OnGameEvent_special_killed(params) { DHUD_ForwardEvent("special_killed", params); }
function OnGameEvent_revive_begin(params) { DHUD_ForwardEvent("revive_begin", params); }
function OnGameEvent_heal_begin(params) { DHUD_ForwardEvent("heal_begin", params); }
function OnGameEvent_player_spawn(params) { DHUD_ForwardEvent("player_spawn", params); }
function OnGameEvent_tank_spawn(params) { DHUD_ForwardEvent("tank_spawn", params); }
function OnGameEvent_witch_spawn(params) { DHUD_ForwardEvent("witch_spawn", params); }
function OnGameEvent_mission_lost(params) { DHUD_ForwardEvent("mission_lost", params); }
function OnGameEvent_map_transition(params) { DHUD_ForwardEvent("map_transition", params); }
function OnGameEvent_finale_win(params) { DHUD_ForwardEvent("finale_win", params); }

try
{
    __CollectEventCallbacks(this, "OnGameEvent_", "DanyriaAddonGameEventCallbacks_director_base", RegisterScriptGameEventListener);
    printl("[DHUD] addon direct event callbacks registered: director_base");
}
catch(e)
{
    try { printl("[DHUD] addon direct event registration failed: " + e); } catch(e2) {}
}

try
{
    local evs = [
        "round_start",
        "player_hurt",
        "player_hurt_concise",
        "player_incapacitated",
        "player_ledge_grab",
        "player_death",
        "infected_death",
        "infected_hurt",
        "entity_hurt",
        "witch_hurt",
        "tank_hurt",
        "weapon_fire",
        "non_pistol_fired",
        "non_melee_fired",
        "weapon_fire_at_40",
        "player_used_first_aid",
        "player_use_item",
        "player_give_item",
        "witch_killed",
        "tank_killed",
        "charger_killed",
        "spitter_killed",
        "jockey_killed",
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
        "finale_win",
    ];
    foreach (evname in evs)
    {
        try { RegisterScriptGameEventListener(evname); } catch(e3) {}
    }
}
catch(e4) {}

try { if (("DHUD_RegisterEvents" in getroottable())) ::DHUD_RegisterEvents(); } catch(e_reg_final) {}
try { if (("DHUD_Write" in getroottable())) ::DHUD_Write(true); } catch(e_write_final) {}
