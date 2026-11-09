<#
Uso (PowerShell):
  .\scripts\backup-local.ps1 -KeyFile C:\Secure\ecopredict-backup.key

La clave debe ser un archivo externo al repositorio con Base64 de 32 bytes aleatorios.
Ejemplo de creación (una vez):
  $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create(); $b = New-Object byte[] 32; $rng.GetBytes($b); [IO.File]::WriteAllText('C:\Secure\ecopredict-backup.key',[Convert]::ToBase64String($b))

El script nunca imprime secretos. Produce backups/*.zip.enc y su SHA-256.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })][string]$KeyFile,
  [string]$BackupDirectory
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$scriptDirectory = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($scriptDirectory)) {
  $invocationPath = $MyInvocation.MyCommand.Path
  if ([string]::IsNullOrWhiteSpace($invocationPath)) { throw 'Unable to determine the script path.' }
  $scriptDirectory = Split-Path -Parent $invocationPath
}
$scriptDirectory = (Resolve-Path -LiteralPath $scriptDirectory).Path
$repositoryRoot = Split-Path -Parent $scriptDirectory
if ([string]::IsNullOrWhiteSpace($repositoryRoot)) { throw 'Unable to determine the repository root.' }
if ([string]::IsNullOrWhiteSpace($BackupDirectory)) { $BackupDirectory = Join-Path $repositoryRoot 'backups' }

function Assert-DockerSuccess { param([string]$Operation) if ($LASTEXITCODE -ne 0) { throw "Docker failed during: $Operation" } }
function Get-ContainerEnv([string]$Name) {
  $lines = & docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' $Name; Assert-DockerSuccess "inspect $Name"
  $map = @{}; foreach ($line in $lines) { $i = $line.IndexOf('='); if ($i -gt 0) { $map[$line.Substring(0,$i)] = $line.Substring($i + 1) } }; return $map
}
function Get-Base64Key([string]$Path) {
  $key = [Convert]::FromBase64String(([IO.File]::ReadAllText((Resolve-Path -LiteralPath $Path)).Trim()))
  if ($key.Length -ne 32) { throw 'The local backup key must decode to exactly 32 bytes.' }; return $key
}
function Fill-Random([byte[]]$Bytes) { $rng = [Security.Cryptography.RandomNumberGenerator]::Create(); try { $rng.GetBytes($Bytes) } finally { $rng.Dispose() } }
function Get-Sha256Hex([string]$Value) { $sha = [Security.Cryptography.SHA256]::Create(); try { return (($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value)) | ForEach-Object { $_.ToString('x2') }) -join '') } finally { $sha.Dispose() } }
function Get-DerivedKey([byte[]]$Master,[byte[]]$Salt,[string]$Label) {
  $labelBytes = [Text.Encoding]::UTF8.GetBytes($Label); $data = New-Object byte[] ($Salt.Length + $labelBytes.Length)
  [Array]::Copy($Salt,0,$data,0,$Salt.Length); [Array]::Copy($labelBytes,0,$data,$Salt.Length,$labelBytes.Length)
  $h = [Security.Cryptography.HMACSHA256]::new($Master); try { return $h.ComputeHash($data) } finally { $h.Dispose() }
}
function Write-EncryptedFile([string]$InputPath,[string]$OutputPath,[byte[]]$Master) {
  $magic = [Text.Encoding]::ASCII.GetBytes('ECOLOCAL1'); $salt = New-Object byte[] 16; $iv = New-Object byte[] 16
  Fill-Random $salt; Fill-Random $iv
  $encKey = Get-DerivedKey $Master $salt 'enc'; $macKey = Get-DerivedKey $Master $salt 'mac'
  $out = [IO.File]::Open($OutputPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  $aes = [Security.Cryptography.Aes]::Create(); $aes.KeySize = 256; $aes.Mode = [Security.Cryptography.CipherMode]::CBC; $aes.Padding = [Security.Cryptography.PaddingMode]::PKCS7; $aes.Key = $encKey; $aes.IV = $iv
  try {
    $out.Write($magic,0,$magic.Length); $out.Write($salt,0,$salt.Length); $out.Write($iv,0,$iv.Length)
    $crypto = [Security.Cryptography.CryptoStream]::new($out,$aes.CreateEncryptor(),[Security.Cryptography.CryptoStreamMode]::Write)
    $input = [IO.File]::OpenRead($InputPath); try { $input.CopyTo($crypto); $crypto.FlushFinalBlock() } finally { $input.Dispose(); $crypto.Dispose() }
  } finally { $aes.Dispose(); $out.Dispose() }
  $hmac = [Security.Cryptography.HMACSHA256]::new($macKey); $stream = [IO.File]::OpenRead($OutputPath)
  try { $buffer = New-Object byte[] 1048576; while (($read = $stream.Read($buffer,0,$buffer.Length)) -gt 0) { [void]$hmac.TransformBlock($buffer,0,$read,$buffer,0) }; [void]$hmac.TransformFinalBlock([byte[]]::new(0),0,0); $tag = $hmac.Hash } finally { $stream.Dispose(); $hmac.Dispose() }
  $append = [IO.File]::Open($OutputPath,[IO.FileMode]::Append,[IO.FileAccess]::Write,[IO.FileShare]::None); try { $append.Write($tag,0,$tag.Length) } finally { $append.Dispose() }
}

& docker info *> $null; Assert-DockerSuccess 'Docker availability'
foreach ($container in 'aire_postgres','aire_n8n') { $running = & docker inspect -f '{{.State.Running}}' $container; Assert-DockerSuccess "inspect $container"; if ($running.Trim() -ne 'true') { throw "$container is not running." } }
& docker volume inspect aire_n8n_data *> $null; Assert-DockerSuccess 'inspect aire_n8n_data'
& docker image inspect alpine:3.20 *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host 'Descargando imagen auxiliar alpine:3.20 requerida para empaquetado...'
  & docker pull alpine:3.20; Assert-DockerSuccess 'docker pull alpine:3.20'
}
$pgEnv = Get-ContainerEnv 'aire_postgres'; $n8nEnv = Get-ContainerEnv 'aire_n8n'
foreach ($name in 'POSTGRES_USER','POSTGRES_PASSWORD','POSTGRES_DB') { if ([string]::IsNullOrWhiteSpace($pgEnv[$name])) { throw "Missing required PostgreSQL configuration: $name" } }
if ([string]::IsNullOrWhiteSpace($n8nEnv['N8N_ENCRYPTION_KEY'])) { throw 'N8N_ENCRYPTION_KEY is not configured in aire_n8n.' }
$pgUser = $pgEnv['POSTGRES_USER']; if ($pgUser -ne 'n8n_user') { throw 'The local backup expects PostgreSQL user n8n_user; refusing an unexpected target.' }
$timestamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'); $name = "ecopredict-local-$timestamp"
[string]$workflowsDirectory = Join-Path $repositoryRoot 'src/n8n-workflows'
if (-not (Test-Path -LiteralPath $workflowsDirectory -PathType Container)) { throw 'The n8n workflows bind-mount source directory is missing.' }
if (-not (Get-ChildItem -LiteralPath $workflowsDirectory -Force | Select-Object -First 1)) { throw 'The n8n workflows bind-mount source directory is empty.' }
[IO.Directory]::CreateDirectory($BackupDirectory) *> $null; $work = Join-Path ([IO.Path]::GetTempPath()) ("ecopredict-local-backup-" + [Guid]::NewGuid().ToString('N')); $payload = Join-Path $work 'payload'; $remote = "/tmp/ecopredict-local-backup-$PID"
$n8nStopped = $false
try {
  [IO.Directory]::CreateDirectory((Join-Path $payload 'postgres')) *> $null
  # Capture the encrypted-key-compatible runtime values only inside the encrypted payload.
  $appDb = $pgEnv['APP_DB']; if ([string]::IsNullOrWhiteSpace($appDb)) { $appDb = 'calidad_aire' }
  $timezone = $n8nEnv['GENERIC_TIMEZONE']; if ([string]::IsNullOrWhiteSpace($timezone)) { $timezone = 'America/Lima' }
  $runtime = @(
    "POSTGRES_USER=$($pgEnv['POSTGRES_USER'])", "POSTGRES_PASSWORD=$($pgEnv['POSTGRES_PASSWORD'])", "POSTGRES_DB=$($pgEnv['POSTGRES_DB'])",
    "APP_DB=$appDb", "N8N_ENCRYPTION_KEY=$($n8nEnv['N8N_ENCRYPTION_KEY'])", "GENERIC_TIMEZONE=$timezone"
  )
  [IO.File]::WriteAllLines((Join-Path $payload 'restore.env'),$runtime,[Text.UTF8Encoding]::new($false))
  $meta = [ordered]@{ format='ecopredict-local-backup-v1'; created_utc=[DateTime]::UtcNow.ToString('o'); postgres_container='aire_postgres'; n8n_container='aire_n8n'; n8n_volume='aire_n8n_data'; workflows_archive='workflows.tar.gz'; databases=@('n8n','calidad_aire'); n8n_encryption_key_sha256=(Get-Sha256Hex $n8nEnv['N8N_ENCRYPTION_KEY']) }
  [IO.File]::WriteAllText((Join-Path $payload 'metadata.json'),($meta | ConvertTo-Json -Depth 3),[Text.UTF8Encoding]::new($false))
  & docker stop aire_n8n *> $null; Assert-DockerSuccess 'stop aire_n8n'; $n8nStopped = $true
  & docker exec aire_postgres sh -ec "mkdir -p '$remote'; pg_dump -U n8n_user -Fc -d n8n -f '$remote/n8n.dump'; pg_dump -U n8n_user -Fc -d calidad_aire -f '$remote/calidad_aire.dump'; pg_dumpall -U n8n_user --globals-only --no-role-passwords -f '$remote/globals.sql'; pg_restore -l '$remote/n8n.dump' >/dev/null; pg_restore -l '$remote/calidad_aire.dump' >/dev/null"; Assert-DockerSuccess 'PostgreSQL dumps and validation'
  & docker cp "aire_postgres:$remote/n8n.dump" (Join-Path $payload 'postgres/n8n.dump'); Assert-DockerSuccess 'copy n8n dump'
  & docker cp "aire_postgres:$remote/calidad_aire.dump" (Join-Path $payload 'postgres/calidad_aire.dump'); Assert-DockerSuccess 'copy calidad_aire dump'
  & docker cp "aire_postgres:$remote/globals.sql" (Join-Path $payload 'postgres/globals.sql'); Assert-DockerSuccess 'copy global roles dump'
  # Write into payload (not its parent) so the archive is included in the encrypted ZIP.
  & docker run --pull never --rm --mount 'type=volume,src=aire_n8n_data,dst=/source,readonly' --mount "type=bind,src=$payload,dst=/backup" alpine:3.20 sh -ec 'tar -C /source -czf /backup/n8n-volume.tar.gz --numeric-owner .; tar -tzf /backup/n8n-volume.tar.gz | grep -q .'; Assert-DockerSuccess 'archive n8n volume'
  if (-not (Test-Path -LiteralPath (Join-Path $payload 'n8n-volume.tar.gz') -PathType Leaf)) { throw 'n8n volume archive was not created in the backup payload.' }
  # /workflows is an independent bind mount in the original Compose; archive it separately.
  & docker run --pull never --rm --mount "type=bind,src=$workflowsDirectory,dst=/source,readonly" --mount "type=bind,src=$payload,dst=/backup" alpine:3.20 sh -ec 'tar -C /source -czf /backup/workflows.tar.gz --numeric-owner .; tar -tzf /backup/workflows.tar.gz | grep -q .'; Assert-DockerSuccess 'archive n8n workflows bind mount'
  if (-not (Test-Path -LiteralPath (Join-Path $payload 'workflows.tar.gz') -PathType Leaf)) { throw 'n8n workflows archive was not created in the backup payload.' }
  $zip = Join-Path $work "$name.zip"; Add-Type -AssemblyName System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::CreateFromDirectory($payload,$zip,[IO.Compression.CompressionLevel]::Optimal,$false)
  $archive = [IO.Compression.ZipFile]::OpenRead($zip)
  try {
    $entries = @($archive.Entries | ForEach-Object { $_.FullName.Replace('\','/') })
    foreach ($entry in 'metadata.json','restore.env','postgres/n8n.dump','postgres/calidad_aire.dump','postgres/globals.sql','n8n-volume.tar.gz','workflows.tar.gz') {
      if ($entries -notcontains $entry) { throw "Backup ZIP validation failed: missing $entry" }
      if ((Get-Item -LiteralPath (Join-Path $payload $entry)).Length -le 0) { throw "Backup ZIP validation failed: empty $entry" }
    }
  } finally { $archive.Dispose() }
  $encrypted = Join-Path $BackupDirectory "$name.zip.enc"; Write-EncryptedFile $zip $encrypted (Get-Base64Key $KeyFile)
  $hash = (Get-FileHash -LiteralPath $encrypted -Algorithm SHA256).Hash.ToLowerInvariant(); [IO.File]::WriteAllText("$encrypted.sha256","$hash  $(Split-Path -Leaf $encrypted)`n",[Text.UTF8Encoding]::new($false))
  Write-Host "Backup encrypted and verified: $(Split-Path -Leaf $encrypted)"
} finally {
  if ($n8nStopped) { & docker start aire_n8n *> $null; if ($LASTEXITCODE -ne 0) { Write-Error 'Failed to restart aire_n8n; start it manually.' } }
  & docker exec aire_postgres sh -c "rm -rf '$remote'" *> $null
  if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
}
