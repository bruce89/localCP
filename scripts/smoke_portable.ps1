param(
    [Parameter(Mandatory = $true)]
    [string]$Archive
)

$ErrorActionPreference = "Stop"
$archivePath = (Resolve-Path -LiteralPath $Archive).Path
$smokeRoot = Join-Path ([IO.Path]::GetTempPath()) ("localcp-smoke-" + [guid]::NewGuid().ToString("N"))
$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$resolvedSmokeRoot = [IO.Path]::GetFullPath($smokeRoot)
if (-not $resolvedSmokeRoot.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to use a smoke-test directory outside the system temp folder."
}

try {
    New-Item -ItemType Directory -Path $smokeRoot | Out-Null
    Expand-Archive -LiteralPath $archivePath -DestinationPath $smokeRoot
    $exePath = Join-Path $smokeRoot "LocalCP\LocalCP.exe"
    if (-not (Test-Path -LiteralPath $exePath)) {
        throw "The ZIP does not contain LocalCP\LocalCP.exe."
    }

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $exePath
    $startInfo.Arguments = "--smoke-test"
    $startInfo.WorkingDirectory = Split-Path -Parent $exePath
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.EnvironmentVariables["QT_QPA_PLATFORM"] = "offscreen"
    $startInfo.EnvironmentVariables["PATH"] = Join-Path $env:SystemRoot "System32"
    $process = [System.Diagnostics.Process]::Start($startInfo)
    try {
        if (-not $process.WaitForExit(30000)) {
            $process.Kill()
            throw "Portable executable did not finish its smoke test within 30 seconds."
        }
        if ($process.ExitCode -ne 0) {
            throw "Portable executable smoke test failed with exit code $($process.ExitCode)."
        }
        $process.WaitForExit()
    }
    finally {
        $process.Dispose()
    }
    Write-Host "Portable smoke test passed from: $smokeRoot"
}
finally {
    for ($attempt = 1; $attempt -le 20; $attempt++) {
        if (-not (Test-Path -LiteralPath $smokeRoot)) {
            break
        }
        try {
            Remove-Item -LiteralPath $smokeRoot -Recurse -Force
            break
        }
        catch {
            if ($attempt -eq 20) {
                throw
            }
            Start-Sleep -Milliseconds 250
        }
    }
}
