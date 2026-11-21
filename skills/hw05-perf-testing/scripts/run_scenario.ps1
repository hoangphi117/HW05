# run_scenario.ps1 - HW05 Agent Skill
# Chay JMeter non-GUI cho mot scenario va sinh HTML report
#
# Usage:
#   .\run_scenario.ps1 -Scenario load   -StudentID 22127001 -Date 20261116
#   .\run_scenario.ps1 -Scenario stress -StudentID 22127001 -Date 20261116 -JMeterHome "C:\jmeter"
#
# Prerequisites:
#   - JMeter cai dat va JMETER_HOME duoc set, hoac truyen -JMeterHome
#   - Backend EShop dang chay tai http://localhost:3000

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("load", "stress", "spike", "soak")]
    [string]$Scenario,

    [Parameter(Mandatory=$true)]
    [string]$StudentID,

    [string]$Date = (Get-Date -Format "yyyyMMdd"),

    [string]$JMeterHome = $env:JMETER_HOME,

    [string]$BaseDir = (Resolve-Path "$PSScriptRoot\..\..\..").Path
)

#    Resolve paths                                                              
$ScenarioCapitalized = (Get-Culture).TextInfo.ToTitleCase($Scenario)
$PlanName  = "${StudentID}_${ScenarioCapitalized}_${Date}"
$JmxFile   = "$BaseDir\test-plans\$PlanName.jmx"
$JtlFile   = "$BaseDir\results\$Scenario\$PlanName.jtl"
$HtmlDir   = "$BaseDir\results\$Scenario\html-report"
$LogFile   = "$BaseDir\results\$Scenario\jmeter_${PlanName}.log"

#    Kiem tra JMeter                                                            
if (-not $JMeterHome) {
    if (Test-Path "D:\Downloads\apache-jmeter-5.6.3\bin\jmeter.bat") {
        $JMeterHome = "D:\Downloads\apache-jmeter-5.6.3"
        $JMeterBin  = "$JMeterHome\bin\jmeter.bat"
    } else {
        # Thu tim jmeter trong PATH
        $jmeterCmd = Get-Command jmeter -ErrorAction SilentlyContinue
        if ($jmeterCmd) {
            $JMeterBin = "jmeter"
        } else {
            Write-Error "[ERR] JMeter not found. Set JMETER_HOME env var hoac truyen -JMeterHome"
            exit 1
        }
    }
} else {
    $JMeterBin = "$JMeterHome\bin\jmeter.bat"
    if (-not (Test-Path $JMeterBin)) {
        Write-Error "[ERR] JMeter not found at: $JMeterBin"
        exit 1
    }
}

#    Kiem tra JMX file                                                          
if (-not (Test-Path $JmxFile)) {
    Write-Error "[ERR] Test plan not found: $JmxFile"
    Write-Host "   Chay generate_jmx.py truoc:"
    Write-Host "   python scripts\generate_jmx.py --scenario $Scenario --student-id $StudentID --date $Date"
    exit 1
}

#    Kiem tra SUT dang chay                                                     
Write-Host "`n[*] Checking SUT availability at http://localhost:3000 ..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/products" `
                                  -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] SUT is running (HTTP $($response.StatusCode))"
} catch {
    Write-Warning "[!]  Cannot reach http://localhost:3000/api/products"
    Write-Warning "   Hay chac chan backend EShop dang chay truoc khi test!"
    $confirm = Read-Host "Tiep tuc anyway? (y/N)"
    if ($confirm -ne "y") { exit 1 }
}

#    Tao output directories                                                     
New-Item -ItemType Directory -Path "$BaseDir\results\$Scenario" -Force | Out-Null
New-Item -ItemType Directory -Path $HtmlDir -Force | Out-Null

#    Clean HTML report cu                                                      
if (Test-Path "$HtmlDir\index.html") {
    Remove-Item "$HtmlDir\*" -Recurse -Force
    Write-Host "[DEL]  Cleaned old HTML report at $HtmlDir"
}

#    Banner                                                                     
Write-Host ""
Write-Host "=" * 60
Write-Host "  [RUN] Running JMeter - $($Scenario.ToUpper()) Scenario"
Write-Host "  Plan    : $PlanName"
Write-Host "  JMX     : $JmxFile"
Write-Host "  JTL     : $JtlFile"
Write-Host "  Report  : $HtmlDir"
Write-Host "=" * 60
Write-Host ""
Write-Host "  [!]  NHAC NHO:"
Write-Host "  [ ] Mo Task Manager NGAY BAY de quan sat CPU/RAM"
Write-Host "  [ ] Chuan bi chup man hinh: tool + Task Manager cung frame"
Write-Host "  [ ] Voi Stress/Spike: chuan bi reset lockout neu can"
Write-Host ""

$startTime = Get-Date
Write-Host "[TIME]  Started at: $($startTime.ToString('HH:mm:ss'))"
Write-Host ""

#    Chay JMeter                                                                
$jmeterArgs = @(
    "-n",                        # Non-GUI mode
    "-t", $JmxFile,              # Test plan
    "-l", $JtlFile,              # Log file (.jtl)
    "-e",                        # Generate HTML report after test
    "-o", $HtmlDir,              # HTML report output dir
    "-j", $LogFile,              # JMeter log
    "-Jjmeter.save.saveservice.output_format=csv",
    "-Jjmeter.save.saveservice.print_field_names=true",
    "-Jjmeter.save.saveservice.timestamp_format=ms",
    "-Jjmeter.save.saveservice.elapsed=true",
    "-Jjmeter.save.saveservice.latency=true",
    "-Jjmeter.save.saveservice.connect_time=true",
    "-Jjmeter.save.saveservice.successful=true",
    "-Jjmeter.save.saveservice.label=true",
    "-Jjmeter.save.saveservice.code=true",
    "-Jjmeter.save.saveservice.message=true",
    "-Jjmeter.save.saveservice.thread_name=true",
    "-Jjmeter.save.saveservice.bytes=true",
    "-Jjmeter.save.saveservice.sent_bytes=true",
    "-Jjmeter.save.saveservice.url=true",
    "-Jjmeter.save.saveservice.thread_counts=true"
)

& $JMeterBin $jmeterArgs

$exitCode = $LASTEXITCODE
$endTime  = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "=" * 60
if ($exitCode -eq 0) {
    Write-Host "  [OK] JMeter finished successfully"
} else {
    Write-Host "  [!]  JMeter exited with code $exitCode (check $LogFile)"
}
Write-Host "  [TIME]  Duration: $([math]::Round($duration, 1)) seconds"
Write-Host "  [JTL] JTL log : $JtlFile"
Write-Host "  [HTML] Report  : $HtmlDir\index.html"
Write-Host "=" * 60
Write-Host ""

#    Quick analysis                                                             
if (Test-Path $JtlFile) {
    Write-Host "[*] Running quick JTL analysis..."
    $analyzePy = "$PSScriptRoot\analyze_jtl.py"
    if (Test-Path $analyzePy) {
        python $analyzePy --file $JtlFile
    }
    Write-Host ""
    Write-Host "[TODO] Next steps:"
    Write-Host "   1. Chup man hinh Task Manager + JMeter cung frame"
    Write-Host "   2. Mo HTML report: $HtmlDir\index.html"
    Write-Host "   3. Git commit:"
    Write-Host "      git add test-plans\ results\$Scenario\ screenshots\"
    Write-Host "      git commit -m 'test($Scenario): run $ScenarioCapitalized scenario - $PlanName'"
}

