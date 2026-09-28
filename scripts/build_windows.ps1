param(
    [string]$Python = "python",
    [string]$OutputDirectory = "dist"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$distRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot $OutputDirectory))
if (-not $distRoot.StartsWith(
    ($repoRoot + [IO.Path]::DirectorySeparatorChar),
    [StringComparison]::OrdinalIgnoreCase
)) {
    throw "OutputDirectory must be inside the project."
}
$bundlePath = Join-Path $distRoot "LocalCP"
$archivePath = Join-Path $distRoot "LocalCP-windows-x64.zip"
$pythonPath = (& $Python -c "import sys; print(sys.executable)").Trim()
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $pythonPath)) {
    throw "Could not resolve the selected Python interpreter."
}
$originalPath = $env:PATH
$originalPythonPath = $env:PYTHONPATH

if (-not [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows
)) {
    throw "This build script requires Windows."
}
if ((Test-Path -LiteralPath $bundlePath) -or (Test-Path -LiteralPath $archivePath)) {
    throw "Existing package found in dist. Move or remove the previous LocalCP folder and ZIP before rebuilding."
}

Push-Location $repoRoot
try {
    # Ignore unrelated development tools on PATH: they can contribute incompatible
    # DLLs (for example, a different ICU build) to the frozen application.
    $env:PATH = @(
        (Split-Path -Parent $pythonPath),
        (Join-Path $env:SystemRoot "System32"),
        $env:SystemRoot
    ) -join ";"
    $env:PYTHONPATH = $null
    & $pythonPath -m PyInstaller --clean --onedir --windowed --name LocalCP `
        --paths (Join-Path $repoRoot "src") `
        --distpath $distRoot --workpath (Join-Path $repoRoot "build") `
        --specpath (Join-Path $repoRoot "build") `
        (Join-Path $repoRoot "src\local_cp\__main__.py")
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $bundlePath "LocalCP.exe"))) {
        throw "Build completed without LocalCP.exe."
    }

    Compress-Archive -LiteralPath $bundlePath -DestinationPath $archivePath
    & (Join-Path $PSScriptRoot "smoke_portable.ps1") -Archive $archivePath
    Write-Host "Package ready: $archivePath"
}
finally {
    $env:PATH = $originalPath
    $env:PYTHONPATH = $originalPythonPath
    Pop-Location
}
