# Blue Prince Arabic - install (BepInEx 6 IL2CPP + Arabic plugin)
# usage:  powershell -ExecutionPolicy Bypass -File install.ps1 [-GameDir "D:\Games\Blue Prince"]
param(
    [string]$GameDir = "D:\Games\Blue Prince",
    [switch]$Force
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$payload = Join-Path $here "payload"
$manifestPath = Join-Path $here "manifest.json"

if (-not (Test-Path (Join-Path $GameDir "BLUE PRINCE.exe"))) { throw "BLUE PRINCE.exe not found in '$GameDir'. Pass -GameDir with the game folder." }
if (Get-Process -Name "BLUE PRINCE" -ErrorAction SilentlyContinue) { throw "Close the game first." }
if (Test-Path (Join-Path $GameDir "BluePrinceArabic_installed.json")) {
    if (-not $Force) { Write-Host "Already installed: updating files (use uninstall.ps1 to remove)." }
}

$manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
# verify the payload before touching the game folder
foreach ($m in $manifest) {
    $p = Join-Path $payload $m.path
    if (-not (Test-Path $p)) { throw "Payload file missing: $($m.path)" }
    $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower()
    if ($h -ne $m.sha256) { throw "Payload file damaged: $($m.path)" }
}

$backup = Join-Path $GameDir "BluePrinceArabic_backup"
$installed = @()
foreach ($m in $manifest) {
    $src = Join-Path $payload $m.path
    $dst = Join-Path $GameDir $m.path
    $dir = Split-Path -Parent $dst
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    if ((Test-Path $dst) -and -not (Test-Path (Join-Path $GameDir "BluePrinceArabic_installed.json"))) {
        # a file that existed before our first install: keep a copy so uninstall can restore it
        $bk = Join-Path $backup $m.path
        New-Item -ItemType Directory -Path (Split-Path -Parent $bk) -Force | Out-Null
        Copy-Item -LiteralPath $dst -Destination $bk -Force
    }
    Copy-Item -LiteralPath $src -Destination $dst -Force
    $installed += [pscustomobject]@{ path = $m.path; sha256 = $m.sha256 }
}
$installed | ConvertTo-Json -Depth 3 | Set-Content -Path (Join-Path $GameDir "BluePrinceArabic_installed.json") -Encoding UTF8
Write-Host ""
Write-Host "Installed $($installed.Count) files into $GameDir"
Write-Host "First launch builds BepInEx's interop cache (1-2 minutes, black window). Later launches are normal."
Write-Host "In game: F10 = English/Arabic, F11 = reload translations."
