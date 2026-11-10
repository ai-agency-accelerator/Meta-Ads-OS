<#
Programa el brief diario en Windows con el Programador de tareas. Lo usa /brief-diario programar (método «sistema»).

  instalar-windows.ps1 -Hora 08:00   instala o actualiza la tarea (hora local)
  instalar-windows.ps1 -Probar       la lanza ahora, igual que cada mañana (tarda de 2 a 6 minutos)
  instalar-windows.ps1 -Estado       último resultado y próxima ejecución
  instalar-windows.ps1 -Quitar       quita la tarea del Programador de tareas (confírmalo antes)

Desde Git Bash o PowerShell:
  powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/brief-diario/programacion/instalar-windows.ps1 -Hora 08:00

La tarea se ejecuta con tu usuario y solo con tu sesión iniciada (ahí están tu login de Claude y tus claves). Tiene dos
disparadores: cada día a la hora elegida y al iniciar sesión; con «Ejecutar lo antes posible si se pierde una
ejecución» y «Activar el equipo para ejecutar la tarea». brief.ps1 -SiFalta evita que se ejecute dos veces el mismo día.
#>
param([string]$Hora = "", [switch]$Probar, [switch]$Estado, [switch]$Quitar)
$ErrorActionPreference = "Stop"

$Nombre = "Meta Ads OS - brief diario"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Raiz = (Resolve-Path (Join-Path $Dir "..\..\..\..")).Path
$Marca = Join-Path $Raiz "logs\brief-diario.ultimo"
$Utf8 = New-Object System.Text.UTF8Encoding $false
New-Item -ItemType Directory -Force -Path (Join-Path $Raiz "logs") | Out-Null
$Tarea = Get-ScheduledTask -TaskName $Nombre -ErrorAction SilentlyContinue

if ($Quitar) {
  if ($Tarea) {
    Unregister-ScheduledTask -TaskName $Nombre -Confirm:$false
    Write-Output "Tarea «$Nombre» quitada del Programador de tareas."
  } else {
    Write-Output "No había tarea instalada."
  }
  exit 0
}

if ($Estado) {
  if ($Tarea) {
    $Tarea | Get-ScheduledTaskInfo | Format-List LastRunTime, LastTaskResult, NextRunTime
  } else {
    Write-Output "La tarea no está instalada."
  }
  $Ultimo = "ninguno"
  if (Test-Path -LiteralPath $Marca) { $Ultimo = ([System.IO.File]::ReadAllText($Marca)).Trim() }
  Write-Output "Último intento: $Ultimo"
  exit 0
}

if ($Probar) {
  if (-not $Tarea) { Write-Output "La tarea no está instalada: ejecuta primero instalar-windows.ps1 -Hora HH:MM"; exit 2 }
  [System.IO.File]::WriteAllText($Marca, "forzar`n", $Utf8)
  Start-ScheduledTask -TaskName $Nombre
  Write-Output "Lanzado. En 2-6 minutos debería llegarte el brief. Si no, mira el final de logs\brief-diario-$(Get-Date -Format 'yyyy-MM').log"
  exit 0
}

if ($Hora -notmatch '^([01]\d|2[0-3]):[0-5]\d$') {
  Write-Output "Uso: instalar-windows.ps1 -Hora HH:MM | -Probar | -Estado | -Quitar   (p. ej. -Hora 08:00)"
  exit 1
}

$Claude = $null
$c = Get-Command claude -ErrorAction SilentlyContinue
if ($c) { $Claude = $c.Source }
if (-not $Claude) {
  $c = Join-Path $env:USERPROFILE ".local\bin\claude.exe"
  if (Test-Path -LiteralPath $c) { $Claude = $c }
}
if (-not $Claude) {
  Write-Output 'No encuentro claude. Instala Claude Code o abre una terminal donde "claude" funcione y repite.'
  exit 2
}

$Script = Join-Path $Dir "brief.ps1"
$Argumento = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}" -SiFalta {1} -ClaudeBin "{2}"' -f $Script, $Hora, $Claude
$Accion = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Argumento -WorkingDirectory $Raiz
$Disparadores = @(
  (New-ScheduledTaskTrigger -Daily -At $Hora),
  (New-ScheduledTaskTrigger -AtLogOn -User ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME))
)
$Ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 1) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $Nombre -Action $Accion -Trigger $Disparadores -Settings $Ajustes -Force `
  -Description "Brief diario de Meta Ads OS (solo lectura). Lo gestiona /brief-diario programar." | Out-Null

# Si hoy ya pasó la hora, no se lanza un brief ahora al iniciar sesión: el primero será mañana o con -Probar
if ((Get-Date -Format "HHmm") -ge ($Hora -replace ":", "")) {
  [System.IO.File]::WriteAllText($Marca, ((Get-Date -Format "yyyy-MM-dd") + "`n"), $Utf8)
}
Write-Output "Brief programado cada día a las $Hora con el Programador de tareas («$Nombre»)."
Write-Output "Pruébalo ahora: powershell -NoProfile -ExecutionPolicy Bypass -File `"$Dir\instalar-windows.ps1`" -Probar"
