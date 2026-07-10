<#
render_pptx.ps1 — rasterise a .pptx to one PNG per slide for visual QA.

Primary path: PowerPoint COM (Office). This renders with the user's REAL fonts
and the real template geometry, so QA matches what they'll open. Falls back to
LibreOffice (soffice) if PowerPoint isn't installed.

Usage:
  powershell -File render_pptx.ps1 -Pptx "out.pptx" -OutDir ".\qa" [-Width 1280] [-Height 720]

Prints one absolute PNG path per line on success, prefixed with "PNG: ".
#>
param(
  [Parameter(Mandatory = $true)][string]$Pptx,
  [Parameter(Mandatory = $true)][string]$OutDir,
  [int]$Width = 1280,
  [int]$Height = 720
)

$ErrorActionPreference = "Stop"
$Pptx = (Resolve-Path $Pptx).Path
if (Test-Path $OutDir) { Remove-Item (Join-Path $OutDir "slide-*.png") -Force -ErrorAction SilentlyContinue }
else { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$OutDir = (Resolve-Path $OutDir).Path

function Try-PowerPoint {
  try { $pp = New-Object -ComObject PowerPoint.Application } catch { return $false }
  try {
    $deck = $pp.Presentations.Open($Pptx, $true, $false, $false)  # ReadOnly, Untitled, no window
    $i = 0
    foreach ($slide in $deck.Slides) {
      $i++
      $name = "slide-{0:D2}.png" -f $i
      $slide.Export((Join-Path $OutDir $name), "PNG", $Width, $Height)
    }
    $deck.Close()
    $pp.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
    return $true
  } catch {
    try { $pp.Quit() } catch {}
    Write-Error "PowerPoint render failed: $($_.Exception.Message)"
    return $false
  }
}

function Try-LibreOffice {
  $soffice = $null
  foreach ($p in @("C:\Program Files\LibreOffice\program\soffice.exe",
                   "C:\Program Files (x86)\LibreOffice\program\soffice.exe")) {
    if (Test-Path $p) { $soffice = $p; break }
  }
  if (-not $soffice) { return $false }
  & $soffice --headless --convert-to pdf --outdir $OutDir $Pptx | Out-Null
  $pdf = Join-Path $OutDir ([System.IO.Path]::GetFileNameWithoutExtension($Pptx) + ".pdf")
  $pdftoppm = (Get-Command pdftoppm -ErrorAction SilentlyContinue)
  if (-not $pdftoppm -or -not (Test-Path $pdf)) { return $false }
  & $pdftoppm.Source -png -r 96 $pdf (Join-Path $OutDir "slide")
  return $true
}

$ok = Try-PowerPoint
if (-not $ok) { $ok = Try-LibreOffice }
if (-not $ok) {
  Write-Error "No renderer available (PowerPoint COM and LibreOffice both unavailable). The .pptx is still valid; open it in PowerPoint to view."
  exit 2
}

Get-ChildItem (Join-Path $OutDir "slide-*.png") | Sort-Object Name | ForEach-Object { "PNG: $($_.FullName)" }
