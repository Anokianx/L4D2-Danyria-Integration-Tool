function DHUD_AutoloadCore()
{
    try
    {
        IncludeScript("danyria_hud", getroottable());
        if (("DHUD_RegisterEvents" in getroottable())) ::DHUD_RegisterEvents();
        if (("DHUD_Register" in getroottable())) ::DHUD_Register();
        if (("DHUD_Write" in getroottable())) ::DHUD_Write(true);
        printl("[DHUD] Autoloaded Danyria HUD telemetry from addon hook.");
    }
    catch(e)
    {
        printl("[DHUD] Autoload failed: " + e);
    }
}

if (!("DHUD_AUTOLOAD_DONE" in getroottable()))
{
    ::DHUD_AUTOLOAD_DONE <- true;
    DHUD_AutoloadCore();
}
else
{
    try
    {
        if (!("DHUD_DispatchGameEvent" in getroottable()) || !("DHUD_Write" in getroottable())) DHUD_AutoloadCore();
        else
        {
            if (("DHUD_RegisterEvents" in getroottable())) ::DHUD_RegisterEvents();
            if (("DHUD_Register" in getroottable())) ::DHUD_Register();
            ::DHUD_Write(true);
        }
    }
    catch(e2) { DHUD_AutoloadCore(); }
}
