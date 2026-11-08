<#
Uso (PowerShell):
  .\scripts\restore-local.ps1 -BackupFile .\backups\ecopredict-local-...zip.enc -KeyFile C:\Secure\ecopredict-backup.key
  .\scripts\restore-local.ps1 -BackupFile .\backups\ecopredict-local-...zip.enc -KeyFile C:\Secure\ecopredict-backup.key -ExtractEnvOnly

Restaura exclusivamente en contenedores ecopredict_restore_* y puertos locales
15432, 15678 y 18080. Nunca sustituye aire_* ni sus volúmenes.
ExtractEnvOnly verifica y descifra sólo restore.env en $env:TEMP; no usa Docker.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })][string]$BackupFile,
  [Parameter(Mandatory = $true)][ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })][string]$KeyFile,
  [string]$ComposeFile,
  [switch]$ExtractEnvOnly
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
if ([string]::IsNullOrWhiteSpace($ComposeFile)) { $ComposeFile = Join-Path $repositoryRoot 'infrastructure/docker-compose.restore-local.yml' }

function Assert-DockerSuccess { param([string]$Operation) if ($LASTEXITCODE -ne 0) { throw "Docker failed during: $Operation" } }
function Get-Base64Key([string]$Path) { $key=[Convert]::FromBase64String(([IO.File]::ReadAllText((Resolve-Path -LiteralPath $Path)).Trim())); if($key.Length -ne 32){throw 'The local backup key must decode to exactly 32 bytes.'}; return $key }
function Get-DerivedKey([byte[]]$Master,[byte[]]$Salt,[string]$Label) { $b=[Text.Encoding]::UTF8.GetBytes($Label); $d=New-Object byte[] ($Salt.Length+$b.Length); [Array]::Copy($Salt,0,$d,0,$Salt.Length); [Array]::Copy($b,0,$d,$Salt.Length,$b.Length); $h=[Security.Cryptography.HMACSHA256]::new($Master); try{return $h.ComputeHash($d)}finally{$h.Dispose()} }
function Read-Exact([IO.Stream]$Stream,[byte[]]$Buffer) { $offset=0; while($offset -lt $Buffer.Length){$n=$Stream.Read($Buffer,$offset,$Buffer.Length-$offset); if($n -le 0){throw 'Unexpected end of encrypted backup.'}; $offset+=$n} }
function Test-FixedTime([byte[]]$A,[byte[]]$B) { if($A.Length -ne $B.Length){return $false}; $diff=0; for($i=0;$i -lt $A.Length;$i++){$diff=$diff -bor ($A[$i] -bxor $B[$i])}; return $diff -eq 0 }
function Set-OwnerOnlyAcl([string]$Path) {
  $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name
  & icacls $Path /inheritance:r /grant:r "${currentUser}:(R,W)" /c *> $null
  if ($LASTEXITCODE -ne 0) { throw 'Unable to apply restrictive permissions to the temporary restore environment file.' }
}
function Read-EncryptedFile([string]$InputPath,[string]$OutputPath,[byte[]]$Master) {
  $magic=[Text.Encoding]::ASCII.GetBytes('ECOLOCAL1'); $length=(Get-Item -LiteralPath $InputPath).Length; if($length -le 73){throw 'Encrypted backup is too small.'}; $cipherLength=$length-32
  $cipherTemp="$OutputPath.cipher"; $s=[IO.File]::OpenRead($InputPath)
  try { $header=New-Object byte[] 9; Read-Exact $s $header; if(-not (Test-FixedTime $header $magic)){throw 'Unexpected encrypted backup format.'}; $salt=New-Object byte[] 16; $iv=New-Object byte[] 16; Read-Exact $s $salt; Read-Exact $s $iv; $macKey=Get-DerivedKey $Master $salt 'mac'; $hmac=[Security.Cryptography.HMACSHA256]::new($macKey); $s.Position=0; $buffer=New-Object byte[] 1048576; $remaining=$cipherLength; while($remaining -gt 0){$take=[Math]::Min($buffer.Length,$remaining); $read=$s.Read($buffer,0,$take); if($read -le 0){throw 'Unexpected end of encrypted backup.'}; [void]$hmac.TransformBlock($buffer,0,$read,$buffer,0); $remaining-=$read}; [void]$hmac.TransformFinalBlock([byte[]]::new(0),0,0); $tag=New-Object byte[] 32; Read-Exact $s $tag; if(-not (Test-FixedTime $hmac.Hash $tag)){throw 'Encrypted backup authentication failed.'}; $hmac.Dispose(); $s.Position=41; $remaining=$cipherLength-41; $cipher=[IO.File]::Open($cipherTemp,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None); try{while($remaining -gt 0){$take=[Math]::Min($buffer.Length,$remaining);$read=$s.Read($buffer,0,$take);if($read -le 0){throw 'Unexpected encrypted backup.'};$cipher.Write($buffer,0,$read);$remaining-=$read}}finally{$cipher.Dispose()} } finally { $s.Dispose() }
  try { $input=[IO.File]::OpenRead($cipherTemp); $aes=[Security.Cryptography.Aes]::Create(); $aes.KeySize=256; $aes.Mode=[Security.Cryptography.CipherMode]::CBC; $aes.Padding=[Security.Cryptography.PaddingMode]::PKCS7; $aes.Key=(Get-DerivedKey $Master $salt 'enc'); $aes.IV=$iv; $crypto=[Security.Cryptography.CryptoStream]::new($input,$aes.CreateDecryptor(),[Security.Cryptography.CryptoStreamMode]::Read); $out=[IO.File]::Open($OutputPath,[IO.FileMode]::CreateNew); try{$crypto.CopyTo($out)}finally{$out.Dispose();$crypto.Dispose();$aes.Dispose();$input.Dispose()} } finally { if(Test-Path -LiteralPath $cipherTemp){Remove-Item -LiteralPath $cipherTemp -Force} }
}

if ((Get-Item -LiteralPath $BackupFile).Name -notmatch '^ecopredict-local-[A-Za-z0-9TZ-]+\.zip\.enc$') { throw 'Unexpected backup filename.' }
$sidecar = "$BackupFile.sha256"; if (-not (Test-Path -LiteralPath $sidecar)) { throw 'Missing SHA-256 sidecar file.' }
$expected = ((Get-Content -LiteralPath $sidecar -Raw).Trim() -split '\s+')[0].ToLowerInvariant(); $actual=(Get-FileHash -LiteralPath $BackupFile -Algorithm SHA256).Hash.ToLowerInvariant(); if($expected -ne $actual){throw 'SHA-256 validation failed.'}
if ($ExtractEnvOnly) {
  $work = Join-Path ([IO.Path]::GetTempPath()) ("ecopredict-restore-env-" + [Guid]::NewGuid().ToString('N'))
  $destination = Join-Path $env:TEMP 'ecopredict-restore.env'
  $temporaryOutput = Join-Path $work 'restore.env.tmp'
  $archive = $null
  try {
    [IO.Directory]::CreateDirectory($work) *> $null
    $zip = Join-Path $work 'backup.zip'
    Read-EncryptedFile $BackupFile $zip (Get-Base64Key $KeyFile)
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($zip)
    $entry = $archive.GetEntry('restore.env')
    if ($null -eq $entry -or $entry.Length -le 0) { throw 'Backup component missing: restore.env' }
    $input = $entry.Open(); $output = [IO.File]::Open($temporaryOutput,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $input.CopyTo($output) } finally { $output.Dispose(); $input.Dispose() }
    if (Test-Path -LiteralPath $destination) { Remove-Item -LiteralPath $destination -Force }
    Move-Item -LiteralPath $temporaryOutput -Destination $destination -Force
    Set-OwnerOnlyAcl $destination
    Write-Host 'Encrypted backup verified; restore.env extracted to the protected temporary location.'
  } finally {
    if ($null -ne $archive) { $archive.Dispose() }
    if (Test-Path -LiteralPath $temporaryOutput) { Remove-Item -LiteralPath $temporaryOutput -Force }
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
  }
  exit 0
}

& docker info *> $null; Assert-DockerSuccess 'Docker availability'
if (-not (Test-Path -LiteralPath $ComposeFile -PathType Leaf)) { throw 'Isolated restore Compose file was not found.' }
foreach($name in 'aire_postgres','aire_n8n','aire_n8n_data','aire_postgres_data'){ if($name -like 'ecopredict_restore_*'){throw 'Safety guard failed.'} }
foreach($name in 'ecopredict_restore_postgres','ecopredict_restore_n8n','ecopredict_restore_nginx') {
  $existing = @(& docker container ls -aq --filter "name=^/$name$"); Assert-DockerSuccess "list container $name"
  if ($existing | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) { throw "Isolated restore container already exists: $name" }
}
foreach($volume in 'ecopredict_restore_postgres_data','ecopredict_restore_n8n_data','ecopredict_restore_workflows') {
  $existing = @(& docker volume ls -q --filter "name=^$volume$"); Assert-DockerSuccess "list volume $volume"
  if ($existing | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) { throw "Isolated restore volume already exists: $volume" }
}
$work=Join-Path ([IO.Path]::GetTempPath()) ("ecopredict-local-restore-"+[Guid]::NewGuid().ToString('N')); $payload=Join-Path $work 'payload'
try {
  [IO.Directory]::CreateDirectory($payload) *> $null; $zip=Join-Path $work 'backup.zip'; Read-EncryptedFile $BackupFile $zip (Get-Base64Key $KeyFile)
  Add-Type -AssemblyName System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::ExtractToDirectory($zip,$payload)
  foreach($file in 'metadata.json','restore.env','postgres/n8n.dump','postgres/calidad_aire.dump','postgres/globals.sql','n8n-volume.tar.gz','workflows.tar.gz'){ if(-not (Test-Path -LiteralPath (Join-Path $payload $file) -PathType Leaf)){throw "Backup component missing: $file"} }
  $runtime=Get-Content -LiteralPath (Join-Path $payload 'restore.env'); if(-not ($runtime | Where-Object { $_ -match '^N8N_ENCRYPTION_KEY=.' })){throw 'Backup has no n8n encryption key.'}
  foreach($volume in 'ecopredict_restore_n8n_data','ecopredict_restore_workflows') { & docker volume create $volume *> $null; Assert-DockerSuccess "create isolated volume $volume" }
  & docker compose --project-name ecopredict_restore --env-file (Join-Path $payload 'restore.env') -f $ComposeFile up -d --pull never postgres; Assert-DockerSuccess 'start isolated PostgreSQL'
  for($i=0;$i -lt 30;$i++){ $health=& docker inspect -f '{{.State.Health.Status}}' ecopredict_restore_postgres; if($LASTEXITCODE -eq 0 -and $health.Trim() -eq 'healthy'){break}; Start-Sleep -Seconds 2 }
  if($health.Trim() -ne 'healthy'){throw 'Isolated PostgreSQL did not become healthy.'}
  & docker cp (Join-Path $payload 'postgres/n8n.dump') 'ecopredict_restore_postgres:/tmp/n8n.dump'; Assert-DockerSuccess 'copy n8n dump'
  & docker cp (Join-Path $payload 'postgres/calidad_aire.dump') 'ecopredict_restore_postgres:/tmp/calidad_aire.dump'; Assert-DockerSuccess 'copy calidad_aire dump'
  # Restore global roles only when absent. Existing bootstrap roles are retained, so their passwords are never overwritten.
  $existingRoles = @(& docker exec ecopredict_restore_postgres psql -U n8n_user -d postgres -Atqc 'SELECT rolname FROM pg_roles'); Assert-DockerSuccess 'list isolated PostgreSQL roles'
  $filteredGlobals = New-Object 'System.Collections.Generic.List[string]'
  foreach($line in (Get-Content -LiteralPath (Join-Path $payload 'postgres/globals.sql'))) {
    if($line -match '^(CREATE ROLE|ALTER ROLE)\s+"?([^"\s;]+)"?') { if($existingRoles -contains $Matches[2]) { continue } }
    $filteredGlobals.Add($line)
  }
  $globalsPath = Join-Path $work 'globals-restore.sql'; [IO.File]::WriteAllLines($globalsPath,$filteredGlobals,[Text.UTF8Encoding]::new($false))
  & docker cp $globalsPath 'ecopredict_restore_postgres:/tmp/globals-restore.sql'; Assert-DockerSuccess 'copy global roles dump'
  & docker exec ecopredict_restore_postgres psql -U n8n_user -d postgres -v ON_ERROR_STOP=1 -f /tmp/globals-restore.sql; Assert-DockerSuccess 'restore compatible global roles'
  & docker exec ecopredict_restore_postgres createdb -U n8n_user calidad_aire; Assert-DockerSuccess 'create isolated calidad_aire database'
  & docker exec ecopredict_restore_postgres pg_restore -U n8n_user --exit-on-error -d n8n /tmp/n8n.dump; Assert-DockerSuccess 'restore n8n database'
  & docker exec ecopredict_restore_postgres pg_restore -U n8n_user --exit-on-error -d calidad_aire /tmp/calidad_aire.dump; Assert-DockerSuccess 'restore calidad_aire database'
  & docker run --pull never --rm --mount 'type=volume,src=ecopredict_restore_n8n_data,dst=/target' --mount "type=bind,src=$payload,dst=/backup,readonly" alpine:3.20 sh -ec 'tar -C /target -xzf /backup/n8n-volume.tar.gz --numeric-owner'; Assert-DockerSuccess 'restore isolated n8n volume'
  & docker run --pull never --rm --mount 'type=volume,src=ecopredict_restore_workflows,dst=/target' --mount "type=bind,src=$payload,dst=/backup,readonly" alpine:3.20 sh -ec 'tar -C /target -xzf /backup/workflows.tar.gz --numeric-owner'; Assert-DockerSuccess 'restore isolated workflows volume'
  & docker run --pull never --rm --mount 'type=volume,src=ecopredict_restore_n8n_data,dst=/target,readonly' alpine:3.20 sh -ec 'find /target -mindepth 1 -print -quit | grep -q .'; Assert-DockerSuccess 'validate restored n8n persistent data'
  & docker run --pull never --rm --mount 'type=volume,src=ecopredict_restore_workflows,dst=/target,readonly' alpine:3.20 sh -ec 'find /target -mindepth 1 -print -quit | grep -q .'; Assert-DockerSuccess 'validate restored workflow data'
  & docker compose --project-name ecopredict_restore --env-file (Join-Path $payload 'restore.env') -f $ComposeFile up -d --pull never n8n nginx; Assert-DockerSuccess 'start isolated n8n and nginx'
  & docker exec ecopredict_restore_n8n sh -ec 'test -d /workflows && find /workflows -mindepth 1 -print -quit | grep -q .'; Assert-DockerSuccess 'validate /workflows mount in isolated n8n'
  for($i=0;$i -lt 30;$i++){ try{$null=Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://127.0.0.1:15678/healthz/readiness; break}catch{Start-Sleep -Seconds 2} }
  $null=Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 http://127.0.0.1:15678/healthz/readiness
  $null=Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 http://127.0.0.1:18080/
  Write-Host 'Isolated restore completed: PostgreSQL=15432, n8n=15678, Nginx=18080.'
} finally { if(Test-Path -LiteralPath $work){Remove-Item -LiteralPath $work -Recurse -Force} }
