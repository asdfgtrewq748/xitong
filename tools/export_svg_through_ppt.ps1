param(
  [Parameter(Mandatory = $true)]
  [string]$SvgPath,

  [Parameter(Mandatory = $true)]
  [string]$OutputPng,

  [switch]$ConvertToShape
)

$ErrorActionPreference = "Stop"

function Stop-NewPowerPointProcesses {
  param([int[]]$ExistingIds)
  Start-Sleep -Seconds 1
  Get-Process POWERPNT -ErrorAction SilentlyContinue |
    Where-Object { $ExistingIds -notcontains $_.Id } |
    Stop-Process -Force -ErrorAction SilentlyContinue
}

$existingIds = @(Get-Process POWERPNT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$tmpDir = Join-Path ([System.IO.Path]::GetDirectoryName($OutputPng)) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

$ppt = $null
try {
  $ppt = New-Object -ComObject PowerPoint.Application
  $appType = $ppt.GetType()
  $appType.InvokeMember('Visible', 'SetProperty', $null, $ppt, @(1)) | Out-Null

  $presentations = $appType.InvokeMember('Presentations', 'GetProperty', $null, $ppt, @())
  $pres = $presentations.GetType().InvokeMember('Add', 'InvokeMethod', $null, $presentations, @())
  $slides = $pres.GetType().InvokeMember('Slides', 'GetProperty', $null, $pres, @())
  $slide = $slides.GetType().InvokeMember('Add', 'InvokeMethod', $null, $slides, @(1, 12))
  $shapes = $slide.GetType().InvokeMember('Shapes', 'GetProperty', $null, $slide, @())
  $shape = $shapes.GetType().InvokeMember('AddPicture', 'InvokeMethod', $null, $shapes, @($SvgPath, 0, -1, 40, 40, 1000, 395))

  if ($ConvertToShape) {
    $shape.GetType().InvokeMember('Select', 'InvokeMethod', $null, $shape, @()) | Out-Null
    Start-Sleep -Milliseconds 500

    $wshell = New-Object -ComObject WScript.Shell
    $wshell.AppActivate('PowerPoint') | Out-Null
    Start-Sleep -Milliseconds 500

    $job = Start-Job -ScriptBlock {
      $ws = New-Object -ComObject WScript.Shell
      1..30 | ForEach-Object {
        Start-Sleep -Seconds 1
        $ws.SendKeys('{ENTER}')
      }
    }

    try {
      $cmdBars = $appType.InvokeMember('CommandBars', 'GetProperty', $null, $ppt, @())
      $cmdBars.GetType().InvokeMember('ExecuteMso', 'InvokeMethod', $null, $cmdBars, @('SVGEdit')) | Out-Null
      Receive-Job $job -Wait | Out-Null
      Start-Sleep -Seconds 2
    }
    finally {
      Remove-Job $job -Force -ErrorAction SilentlyContinue
    }
  }

  $exportArgs = New-Object object[] 4
  $exportArgs[0] = [string]$tmpDir
  $exportArgs[1] = [string]'PNG'
  $exportArgs[2] = [int]1600
  $exportArgs[3] = [int]900
  $pres.GetType().InvokeMember('Export', 'InvokeMethod', $null, $pres, $exportArgs) | Out-Null

  Start-Sleep -Seconds 1
  $png = Get-ChildItem $tmpDir -Filter '*.PNG' | Select-Object -First 1
  if (-not $png) {
    $png = Get-ChildItem $tmpDir -Filter '*.png' | Select-Object -First 1
  }
  if (-not $png) {
    throw "No PNG exported for $SvgPath"
  }

  Copy-Item $png.FullName $OutputPng -Force
}
finally {
  if ($ppt) {
    try {
      $ppt.GetType().InvokeMember('Quit', 'InvokeMethod', $null, $ppt, @()) | Out-Null
    }
    catch {
    }
  }
  Stop-NewPowerPointProcesses -ExistingIds $existingIds
}
