<#
check_env.ps1 — Cowork + capability gate for the create-slide-deck skill.

This skill builds a real PowerPoint file on the user's machine, so it only works
in Cowork (local agent mode). This script confirms we're in a local environment
and that the tools it needs are present. It prints a block of KEY=VALUE lines and
a final verdict line.

  COWORK_READY=yes   -> safe to build decks
  COWORK_READY=no    -> stop; tell the user to switch on Cowork (see SKILL.md)

Note: if the skill is running in plain chat (NOT Cowork), Claude will have no way
to run this script at all — that absence is itself the signal to stop.
#>
$ErrorActionPreference = "SilentlyContinue"

$entrypoint = $env:CLAUDE_CODE_ENTRYPOINT
$isDesktop  = ($entrypoint -eq "claude-desktop")

Write-Output "ENTRYPOINT=$entrypoint"
Write-Output ("OS=" + [System.Environment]::OSVersion.Platform)

# Python + python-pptx (deck engine)
$py = (Get-Command python -ErrorAction SilentlyContinue)
Write-Output ("PYTHON=" + $(if ($py) { $py.Source } else { "MISSING" }))
$pptxOk = $false
if ($py) {
  & $py.Source -c "import pptx" 2>$null
  $pptxOk = ($LASTEXITCODE -eq 0)
}
Write-Output ("PYTHON_PPTX=" + $(if ($pptxOk) { "ok" } else { "MISSING" }))

# Renderer for QA (nice-to-have, not fatal)
$ppOk = $false
try { $pp = New-Object -ComObject PowerPoint.Application; $ppOk = $true; $pp.Quit();
      [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null } catch {}
$soffice = (Test-Path "C:\Program Files\LibreOffice\program\soffice.exe") -or `
           (Test-Path "C:\Program Files (x86)\LibreOffice\program\soffice.exe")
Write-Output ("POWERPOINT=" + $(if ($ppOk) { "ok" } else { "no" }))
Write-Output ("LIBREOFFICE=" + $(if ($soffice) { "ok" } else { "no" }))
$renderer = $ppOk -or $soffice
Write-Output ("RENDERER=" + $(if ($renderer) { "ok" } else { "none" }))

# Verdict: we can BUILD a deck as long as python-pptx is present and we can run
# code locally (the fact this script ran proves local execution). A renderer is
# recommended for QA but not required to produce the .pptx.
if ($pptxOk) {
  Write-Output "COWORK_READY=yes"
} else {
  Write-Output "COWORK_READY=no"
}
