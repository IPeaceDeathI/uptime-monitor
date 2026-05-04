# Скачивает PlantUML (если нет) и рендерит PNG из practice1/diagrams/*.puml
$ErrorActionPreference = "Stop"
$jar = Join-Path $PSScriptRoot "plantuml.jar"
if (-not (Test-Path $jar)) {
  Write-Host "Downloading plantuml.jar ..."
  Invoke-WebRequest -Uri "https://github.com/plantuml/plantuml/releases/download/v1.2024.7/plantuml-1.2024.7.jar" -OutFile $jar
}
$diag = Join-Path $PSScriptRoot "diagrams"
Get-ChildItem $diag -Filter "*.puml" | ForEach-Object {
  java -jar $jar -tpng -Sdpi=120 $_.FullName
}
# Переименование выходных файлов к коротким именам (опционально)
if (Test-Path (Join-Path $diag "UptimeMonitor_Context.png")) {
  Move-Item -Force (Join-Path $diag "UptimeMonitor_Context.png") (Join-Path $diag "context.png")
}
if (Test-Path (Join-Path $diag "UptimeMonitor_Containers.png")) {
  Move-Item -Force (Join-Path $diag "UptimeMonitor_Containers.png") (Join-Path $diag "container.png")
}
if (Test-Path (Join-Path $diag "UptimeMonitor_API_Components.png")) {
  Move-Item -Force (Join-Path $diag "UptimeMonitor_API_Components.png") (Join-Path $diag "component.png")
}
Write-Host "Done."
