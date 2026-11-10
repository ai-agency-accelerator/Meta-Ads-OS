<#
Brief diario sin nadie delante (Windows). Lo lanza la tarea del Programador de tareas que crea instalar-windows.ps1.

  brief.ps1                  ejecuta el brief ahora (prueba manual)
  brief.ps1 -SiFalta HH:MM   solo si ya es esa hora y hoy aún no se ha intentado (lo usa la tarea, que también se
                             lanza al iniciar sesión para recuperar el brief si el ordenador estaba apagado)

Hace lo mismo que brief.sh: claude -p "/brief-diario todos" en modo dontAsk con herramientas-permitidas.txt (más las
variantes `python` y `py -3` de cada orden con python3) y herramientas-denegadas.txt; si el resumen de hoy no consta
como enviado en logs\notificaciones.jsonl, manda un aviso corto con notificar.py.
Registro: logs\brief-diario-AAAA-MM.log. Opcional en .env: CLAUDE_CODE_OAUTH_TOKEN (de `claude setup-token`); nunca
se imprime.
#>
param([string]$SiFalta = "", [string]$ClaudeBin = "", [string]$Modelo = "sonnet")

$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Raiz = (Resolve-Path (Join-Path $Dir "..\..\..\..")).Path
Set-Location -LiteralPath $Raiz
New-Item -ItemType Directory -Force -Path (Join-Path $Raiz "logs"), (Join-Path $Raiz "informes\diario") | Out-Null

$Hoy = Get-Date -Format "yyyy-MM-dd"
$Mes = Get-Date -Format "yyyy-MM"
$Log = Join-Path $Raiz "logs\brief-diario-$Mes.log"
$Marca = Join-Path $Raiz "logs\brief-diario.ultimo"
$Utf8 = New-Object System.Text.UTF8Encoding $false
function Anotar([string]$Texto) {
  [System.IO.File]::AppendAllText($Log, ("{0} {1}`n" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Texto), $Utf8)
}

if ($SiFalta) {
  if ($SiFalta -notmatch '^([01]\d|2[0-3]):[0-5]\d$') { Anotar "hora no válida: $SiFalta (usa HH:MM)"; exit 1 }
  $Ultimo = ""
  if (Test-Path -LiteralPath $Marca) { $Ultimo = ([System.IO.File]::ReadAllText($Marca)).Trim() }
  if ($Ultimo -ne "forzar") {
    if ($Ultimo -eq $Hoy) { exit 0 }                                           # hoy ya se intentó
    if ((Get-Date -Format "HHmm") -lt ($SiFalta -replace ":", "")) { exit 0 }  # aún no es la hora
  }
}
[System.IO.File]::WriteAllText($Marca, "$Hoy`n", $Utf8)

# claude y python (el python3 de la Microsoft Store es un acceso directo a la tienda: no sirve)
$Claude = $ClaudeBin
if (-not $Claude) { $c = Get-Command claude -ErrorAction SilentlyContinue; if ($c) { $Claude = $c.Source } }
if (-not $Claude) {
  $c = Join-Path $env:USERPROFILE ".local\bin\claude.exe"
  if (Test-Path -LiteralPath $c) { $Claude = $c }
}
$Python = $null
$PythonArgs = @()
foreach ($Nombre in @("python3", "python", "py")) {
  $c = Get-Command $Nombre -ErrorAction SilentlyContinue
  if ($c -and $c.Source -notlike "*\WindowsApps\*") {
    $Python = $c.Source
    if ($Nombre -eq "py") { $PythonArgs = @("-3") }
    break
  }
}

# Token de larga duración (opcional): solo la línea CLAUDE_CODE_OAUTH_TOKEN de .env, sin mostrarla
if (-not $env:CLAUDE_CODE_OAUTH_TOKEN -and (Test-Path -LiteralPath ".env")) {
  $Linea = Select-String -LiteralPath ".env" -Pattern '^\s*CLAUDE_CODE_OAUTH_TOKEN\s*=' | Select-Object -Last 1
  if ($Linea) {
    $Valor = ($Linea.Line -split "=", 2)[1].Trim().Trim('"').Trim("'")
    if ($Valor) {
      $env:CLAUDE_CODE_OAUTH_TOKEN = $Valor
      $env:ANTHROPIC_API_KEY = $null   # en -p, una clave de API presente tendría prioridad sobre el token
    }
  }
  $Linea = $null
  $Valor = $null
}

function Leer-Lista([string]$Archivo) {
  [System.IO.File]::ReadAllLines($Archivo, $Utf8) | ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") }
}
function Con-Variantes([string[]]$Reglas) {
  $Salida = @($Reglas)
  foreach ($r in $Reglas) {
    if ($r.StartsWith("Bash(python3 ")) {
      $Salida += $r.Replace("Bash(python3 ", "Bash(python ")
      $Salida += $r.Replace("Bash(python3 ", "Bash(py -3 ")
    }
  }
  return $Salida
}
$Permitidas = Con-Variantes @(Leer-Lista (Join-Path $Dir "herramientas-permitidas.txt"))
$Denegadas = Con-Variantes @(Leer-Lista (Join-Path $Dir "herramientas-denegadas.txt"))

Anotar "inicio del brief · claude: $Claude · python: $Python"
$Codigo = 0
if (-not $Claude) {
  Anotar "No encuentro claude. Vuelve a ejecutar instalar-windows.ps1 desde una terminal donde claude funcione."
  $Codigo = 127
} else {
  # El encargo va antes de --allowedTools: ese parámetro admite varios valores seguidos.
  $Argumentos = @("-p", "/brief-diario todos", "--permission-mode", "dontAsk", "--model", $Modelo, "--allowedTools") +
                $Permitidas + @("--disallowedTools") + $Denegadas
  $null | & $Claude @Argumentos 2>&1 | ForEach-Object { Anotar "$_" }
  $Codigo = $LASTEXITCODE
}
Anotar "fin de claude · código $Codigo"

# ¿Se envió el resumen de hoy? (notificar.py escribe las claves en este orden)
$Notificaciones = Join-Path $Raiz "logs\notificaciones.jsonl"
$Buscado = '"archivo": "informes/diario/' + $Hoy + '.md", "ok": true'
if ((Test-Path -LiteralPath $Notificaciones) -and
    (Select-String -LiteralPath $Notificaciones -SimpleMatch -Pattern $Buscado -Quiet)) {
  Anotar "brief enviado"
  exit 0
}

$Aviso = "informes/diario/$Hoy-aviso.md"
$Lineas = @(
  ('# ⚠️ Brief diario · {0} · no se ha generado' -f $Hoy),
  '',
  ('La ejecución programada de las {0} terminó sin enviar el brief (código {1}).' -f (Get-Date -Format 'HH:mm'), $Codigo),
  '',
  ('- Mira el final de `logs/brief-diario-{0}.log`.' -f $Mes),
  '- En Claude Code, `/brief-diario probar` lo lanza y enseña qué falla.',
  '- Guía: `docs/guias/brief-diario.md`, apartado «Solución de problemas».'
)
[System.IO.File]::WriteAllText((Join-Path $Raiz $Aviso), (($Lineas -join "`n") + "`n"), $Utf8)
if ($Python) {
  & $Python @PythonArgs -I herramientas/notificar.py enviar --archivo $Aviso --canal auto 2>&1 | ForEach-Object { Anotar "$_" }
  Anotar "aviso de fallo enviado · código $LASTEXITCODE"
} else {
  Anotar "no hay python para enviar el aviso de fallo"
}
exit 1
