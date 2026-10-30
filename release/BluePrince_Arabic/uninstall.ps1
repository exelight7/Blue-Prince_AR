# Blue Prince Arabic - uninstall: removes only what install.ps1 added (and BepInEx's generated cache), restores backed-up files
# usage:  powershell -ExecutionPolicy Bypass -File uninstall.ps1 [-GameDir "D:\Games\Blue Prince"] [-WhatIf]
param(
    [string]$GameDir = "D:\Games\Blue Prince",
    [switch]$WhatIf
)
$ErrorActionPreference = "Stop"
$listPath = Join-Path $GameDir "BluePrinceArabic_installed.json"
if (-not (Test-Path $listPath)) { throw "Nothing to uninstall: $listPath not found." }
if (Get-Process -Name "BLUE PRINCE" -ErrorAction SilentlyContinue) { throw "Close the game first." }

$files = Get-Content $listPath -Raw -Encoding UTF8 | ConvertFrom-Json
$dirs = New-Object System.Collections.Generic.HashSet[string]
foreach ($f in $files) {
    $p = Join-Path $GameDir $f.path
    if (Test-Path $p) {
        if ($WhatIf) { Write-Host "would remove $($f.path)" } else { Remove-Item -LiteralPath $p -Force }
    }
    [void]$dirs.Add((Split-Path -Parent $p))
}
# files BepInEx itself generates on first launch (none of them exist in the original game)
foreach ($g in @("BepInEx\cache", "BepInEx\interop", "BepInEx\unity-libs", "BepInEx\bpar", "BepInEx\LogOutput.log", "BepInEx\ErrorLog.log", "changelog.txt")) {
    $p = Join-Path $GameDir $g
    if ($g -eq "changelog.txt") { if (-not (Test-Path (Join-Path $GameDir "BluePrinceArabic_backup\changelog.txt"))) { continue } }
    if (Test-Path $p) { if ($WhatIf) { Write-Host "would remove $g" } else { Remove-Item -LiteralPath $p -Recurse -Force } }
}
# restore files that existed before the install
$backup = Join-Path $GameDir "BluePrinceArabic_backup"
if (Test-Path $backup) {
    Get-ChildItem -LiteralPath $backup -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($backup.Length + 1)
        if ($WhatIf) { Write-Host "would restore $rel" } else { Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $GameDir $rel) -Force }
    }
    if (-not $WhatIf) { Remove-Item -LiteralPath $backup -Recurse -Force }
}
if (-not $WhatIf) {
    # remove directories that became empty (deepest first)
    foreach ($d in ($dirs | Sort-Object { $_.Length } -Descending)) {
        $cur = $d
        while ($cur -and $cur.Length -gt $GameDir.Length -and (Test-Path $cur) -and -not (Get-ChildItem -LiteralPath $cur -Force | Select-Object -First 1)) {
            Remove-Item -LiteralPath $cur -Force
            $cur = Split-Path -Parent $cur
        }
    }
    Remove-Item -LiteralPath $listPath -Force
    Write-Host "Uninstalled."
}
