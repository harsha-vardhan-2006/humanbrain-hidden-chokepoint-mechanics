# Build humanbrain_hidden_chokepoint_mechanics_v2.0.1.zip from the
# standalone repo's tracked files (git ls-files manifest).
$ErrorActionPreference = "Stop"

$root    = "D:\humanbrain\hbm_standalone"
$list    = "D:\humanbrain\dist_build\ziplist.txt"
$stage   = "D:\humanbrain\dist_build\_stage"
$dest    = "D:\humanbrain\dist_build\humanbrain_hidden_chokepoint_mechanics_v2.0.1.zip"

if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $dest -Parent) -Force | Out-Null

$files = Get-Content $list | Where-Object { $_.Trim() -ne '' }
foreach ($f in $files) {
    $src  = Join-Path $root $f
    $destF = Join-Path $stage $f
    $dir  = Split-Path $destF -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Copy-Item $src $destF -Force
}

if (Test-Path $dest) { Remove-Item $dest -Force }
Compress-Archive -Path ($stage + "\*") -DestinationPath $dest -Force
Remove-Item $stage -Recurse -Force
Write-Output ("zip entries: " + $files.Count)
Write-Output ("zip built: " + $dest)
