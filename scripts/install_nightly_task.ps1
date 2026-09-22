# TBlocks 本机定时回归 - 注册/卸载 Windows 任务计划
#
# 作用：每天指定时间在本机自动执行 run_regression.ps1（默认凌晨 02:00 全量 91 条）。
# 与 GitHub 夜间流水线的区别：本机零 Actions 分钟数成本，复用已验证的 Chrome 环境；
# 代价是执行时段本机必须开机、联网并保持登录（UI 用例需要桌面会话）。
#
# 用法（普通 PowerShell 即可，注册当前用户的任务无需管理员）：
#   .\scripts\install_nightly_task.ps1                      # 注册，每天 02:00 跑全量
#   .\scripts\install_nightly_task.ps1 -Time 23:30         # 自定义时间
#   .\scripts\install_nightly_task.ps1 -Suite quick         # 只跑快速套件
#   .\scripts\install_nightly_task.ps1 -Unregister          # 卸载定时任务
#   Get-ScheduledTask -TaskName 'TBlocks Nightly Regression' # 查看任务状态
param(
    [string]$Time = "02:00",
    [ValidateSet("all", "quick", "smoke", "api", "portal", "functional", "member",
                 "finance", "invest", "ui", "backend", "business", "demo",
                 "performance", "load", "security")]
    [string]$Suite = "all",
    [switch]$Unregister
)

$taskName = "TBlocks Nightly Regression"
$root = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $root "scripts\run_regression.ps1"

if ($Unregister) {
    $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existing) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "Scheduled task removed: $taskName"
    } else {
        Write-Host "Task not found, nothing to remove: $taskName"
    }
    exit 0
}

if (-not (Test-Path $runner)) {
    Write-Error "runner not found: $runner"
    exit 2
}

# 校验时间格式
try {
    $triggerAt = [datetime]::Today.Add([timespan]::Parse($Time))
} catch {
    Write-Error "Invalid -Time '$Time' (expected HH:mm, e.g. 02:00)"
    exit 2
}

# 幂等：已存在同名任务先删除再注册
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`" -Suite $Suite" `
    -WorkingDirectory $root

$trigger = New-ScheduledTaskTrigger -Daily -At $triggerAt

# 错过触发（如当时关机）开机后尽快补跑；用电池也运行；单次最长 5 小时；
# 失败后 10 分钟重试 1 次。
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 5) `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 10)

# InteractiveToken：仅在当前用户已登录时运行。UI 用例（即使无头）需要桌面会话，
# 因此不使用 S4U/后台凭据模式。
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "TBlocks 每日定时回归（$Time 跑 $Suite 套件，报告输出到 output\reports）" | Out-Null

Write-Host "Registered scheduled task: $taskName"
Write-Host "  Next runs : daily $Time (suite=$Suite)"
Write-Host "  Runner    : powershell -File $runner -Suite $Suite"
Write-Host "  Reports   : $root\output\reports\"
Write-Host "  Note      : PC must stay powered, networked and logged on at run time."
Write-Host "  Test now  : Start-ScheduledTask -TaskName '$taskName'"
Write-Host "  Remove    : .\scripts\install_nightly_task.ps1 -Unregister"
