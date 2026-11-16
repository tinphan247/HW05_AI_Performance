# Collect hardware evidence for HW05.
# Run from the hw5 directory AFTER load runs (dxdiag is relatively heavy):
#   powershell -ExecutionPolicy Bypass -File scripts/collect_hardware.ps1

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root "hardware"
New-Item -ItemType Directory -Force -Path $out | Out-Null

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"

# 1. dxdiag
$dx = Join-Path $out "dxdiag.txt"
& dxdiag.exe /t $dx /whql:off | Out-Null
Start-Sleep -Seconds 5

# 2. systeminfo
& systeminfo.exe | Out-File -FilePath (Join-Path $out "systeminfo.txt") -Encoding utf8

# 3. Structured markdown report
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$ramModules = Get-CimInstance Win32_PhysicalMemory
$ramTotal = [math]::Round(($ramModules | Measure-Object -Property Capacity -Sum).Sum / 1GB, 1)
$gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1
$os = Get-CimInstance Win32_OperatingSystem
$disks = Get-CimInstance Win32_DiskDrive
$computer = Get-CimInstance Win32_ComputerSystem

$lines = @(
    "# Hardware report - HW05",
    "",
    "Collected: $stamp",
    "",
    "| Item | Value |",
    "|---|---|",
    "| Hostname | $($computer.Name) |",
    "| Manufacturer / model | $($computer.Manufacturer) / $($computer.Model) |",
    "| CPU | $($cpu.Name) |",
    "| Cores / logical processors | $($cpu.NumberOfCores) / $($cpu.NumberOfLogicalProcessors) |",
    "| Max clock | $($cpu.MaxClockSpeed) MHz |",
    "| RAM total | $ramTotal GB |",
    "| RAM modules | $($ramModules.Count) x $([math]::Round($ramModules[0].Capacity / 1GB, 1)) GB @ $($ramModules[0].Speed) MT/s |",
    "| GPU | $($gpu.Name) |",
    "| OS | $($os.Caption) $($os.Version) ($($os.OSArchitecture)) |",
    "| Installed RAM (OS) | $([math]::Round($os.TotalVisibleMemorySize / 1MB, 1)) GB |",
    "| Disks | $((($disks | ForEach-Object { "$($_.Model) $([math]::Round($_.Size / 1GB, 1)) GB" }) -join '; ')) |",
    "",
    "Raw evidence: ``dxdiag.txt``, ``systeminfo.txt``.",
    "",
    "Note: JMeter and the SUT backend run on this same host; there is no second load-generator machine."
)
$lines | Out-File -FilePath (Join-Path $out "hardware_report.md") -Encoding utf8

Write-Output "Wrote hardware evidence to $out"
Get-Content (Join-Path $out "hardware_report.md")
