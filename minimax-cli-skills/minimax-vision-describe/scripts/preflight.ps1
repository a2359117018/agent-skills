# .opencode/skills/minimax-vision-describe/preflight.ps1
# Exit codes: 0=ok, 1=CLI_NOT_FOUND, 2=AUTH_NOT_CONFIGURED, 3=CLI_ERROR

$ErrorActionPreference = "Stop"

if (-not (Get-Command mmx -ErrorAction SilentlyContinue)) {
    Write-Output '{"error":"CLI_NOT_FOUND","message":"mmx is not installed"}'
    exit 1
}

try {
    $authOutput = mmx --non-interactive --output json auth status 2>&1
    $auth = $authOutput | ConvertFrom-Json
    if ($auth.method -and $auth.key) {
        @{ error = $null; message = "OK"; method = $auth.method } | ConvertTo-Json -Compress | Write-Output
        exit 0
    }
    Write-Output '{"error":"AUTH_NOT_CONFIGURED","message":"No API key configured"}'
    exit 2
}
catch {
    $msg = $_.Exception.Message
    if ($msg -match "No API key found") {
        Write-Output '{"error":"AUTH_NOT_CONFIGURED","message":"Run mmx auth or set MINIMAX_API_KEY"}'
        exit 2
    }
    $escaped = $msg -replace '"', '\"' -replace '\r?\n', ' '
    Write-Output "{`"error`":`"CLI_ERROR`",`"message`":`"$escaped`"}"
    exit 3
}
