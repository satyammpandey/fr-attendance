<# install_dlib.ps1
   Usage: open "x64 Native Tools PowerShell" (or Developer Command Prompt) as Administrator
   then: Set-ExecutionPolicy Bypass -Scope Process -Force; .\install_dlib.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "1) Locating Python..."
$python = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $python) { Write-Error "Python not found in PATH. Open the Python-enabled terminal and retry."; exit 1 }

Write-Host "2) Checking CMake..."
$cmake = (Get-Command cmake -ErrorAction SilentlyContinue).Path
if (-not $cmake) {
  Write-Error "CMake not found. Install official CMake and add it to PATH: https://cmake.org/download/"; exit 1
}
Write-Host "CMake found at: $cmake"
if ($cmake -match "\\Python") {
  Write-Host "CMake appears to be a Python-installed wrapper. Attempting to remove Python cmake package..."
  & $python -m pip uninstall cmake -y
  Start-Sleep -Seconds 1
  $cmake = (Get-Command cmake -ErrorAction SilentlyContinue).Path
  if (-not $cmake -or $cmake -match "\\Python") {
    Write-Error "A broken Python-installed cmake remains. Manually remove it or ensure 'C:\Program Files\CMake\bin' is earlier in PATH."; exit 1
  }
  Write-Host "Now using CMake at: $cmake"
}

Write-Host "3) Checking Visual C++ build tools (cl.exe)..."
$cl = (Get-Command cl -ErrorAction SilentlyContinue).Path
if (-not $cl) {
  Write-Error "cl.exe not found. Install 'Build Tools for Visual Studio' -> 'Desktop development with C++' and open the 'x64 Native Tools' prompt."; exit 1
}
Write-Host "cl.exe found at: $cl"

Write-Host "4) Upgrading pip, setuptools, wheel..."
& $python -m pip install --upgrade pip setuptools wheel

Write-Host "5) Installing dlib (this may take several minutes)..."
& $python -m pip install --no-cache-dir dlib

if ($LASTEXITCODE -ne 0) {
  Write-Error "dlib build failed. See output above. Next options: use conda, or install a prebuilt wheel (see README)."; exit 1
}

Write-Host "6) Installing face-recognition..."
& $python -m pip install --no-cache-dir face-recognition

if ($LASTEXITCODE -ne 0) {
  Write-Error "face-recognition install failed."; exit 1
}

Write-Host "SUCCESS: dlib and face-recognition installed."