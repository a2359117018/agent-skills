# scripts/describe.ps1
# Wraps `mmx vision describe` — runs preflight, executes command, normalizes output.
# Exit codes: 0=success, 1=CLI_NOT_FOUND, 2=AUTH_NOT_CONFIGURED, 3=CLI_ERROR, 4=API_ERROR

param(
    [Parameter(Mandatory = $true)]
    [string]$Image,

    [string]$Prompt,

    [int]$TimeoutSeconds = 120
)

$ErrorActionPreference = "Stop"

# --- Preflight: installation ---
if (-not (Get-Command mmx -ErrorAction SilentlyContinue)) {
    Write-Output '{"error":"CLI_NOT_FOUND","message":"mmx is not installed"}'
    exit 1
}

# --- Preflight: auth ---
try {
    $authOutput = mmx --non-interactive --output json auth status 2>&1
    $auth = $authOutput | ConvertFrom-Json
    if (-not ($auth.method -and $auth.key)) {
        Write-Output '{"error":"AUTH_NOT_CONFIGURED","message":"Run mmx auth or set MINIMAX_API_KEY"}'
        exit 2
    }
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

# --- Build args ---
$cmdArgs = @("--non-interactive", "--output", "json")
if ($Prompt) {
    $cmdArgs += @("--prompt", $Prompt)
}
$cmdArgs += @("vision", "describe", "--image", $Image)

# --- Execute ---
try {
    $raw = & mmx @cmdArgs 2>&1 | Out-String
}
catch {
    $msg = $_.Exception.Message
    $escaped = $msg -replace '"', '\"' -replace '\r?\n', ' '
    Write-Output "{`"error`":`"CLI_ERROR`",`"message`":`"$escaped`"}"
    exit 3
}

# --- Parse response ---
try {
    $resp = $raw | ConvertFrom-Json
}
catch {
    $escaped = ($raw -replace '"', '\"' -replace '\r?\n', ' ').Trim()
    Write-Output "{`"error`":`"CLI_ERROR`",`"message`":`"Failed to parse response: $escaped`"}"
    exit 3
}

if ($resp.base_resp.status_code -ne 0) {
    $code = $resp.base_resp.status_code
    $smsg = $resp.base_resp.status_msg -replace '"', '\"'
    Write-Output "{`"error`":`"API_ERROR`",`"status_code`":$code,`"message`":`"$smsg`"}"
    exit 4
}

# --- Success: output clean content ---
Write-Output $resp.content
exit 0
