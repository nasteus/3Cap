#!/system/bin/sh
# Dumpsys wrapper to inject DEBUGGABLE flag for RenderDoc compatibility checks

REAL_DUMPSYS="/system/bin/dumpsys.real"
if [ ! -f "$REAL_DUMPSYS" ]; then
    REAL_DUMPSYS="/system/bin/dumpsys"
fi

if [ "$1" = "package" ]; then
    "$REAL_DUMPSYS" "$@" | sed 's/pkgFlags=\[/pkgFlags=\[ DEBUGGABLE /g'
else
    exec "$REAL_DUMPSYS" "$@"
fi
