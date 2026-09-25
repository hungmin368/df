$exe = "C:\MY_AI_JOBS\dragonfinder\unity_workspace\DragonFinder\Builds\Windows\DragonFinder.exe"
$shotPath = "C:\MY_AI_JOBS\dragonfinder\unity_workspace\release-save-read.png"

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class ReleaseCapture {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, int nFlags);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@

function Capture([System.Diagnostics.Process]$process) {
    $rect = New-Object ReleaseCapture+RECT
    [ReleaseCapture]::GetWindowRect($process.MainWindowHandle, [ref]$rect) | Out-Null
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $hdc = $graphics.GetHdc()
    [ReleaseCapture]::PrintWindow($process.MainWindowHandle, $hdc, 2) | Out-Null
    $graphics.ReleaseHdc($hdc)
    $graphics.Dispose()
    return $bitmap
}

function BrightCount([System.Drawing.Bitmap]$bitmap) {
    $count = 0
    for ($y = 0; $y -lt $bitmap.Height; $y += 4) {
        for ($x = 0; $x -lt $bitmap.Width; $x += 4) {
            $pixel = $bitmap.GetPixel($x, $y)
            if ($pixel.R -gt 200 -and $pixel.G -gt 200 -and $pixel.B -gt 200) { $count++ }
        }
    }
    return $count
}

$process = Start-Process -FilePath $exe -PassThru
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    Start-Sleep -Milliseconds 500
    $process.Refresh()
    if ($process.MainWindowHandle -ne 0) { break }
}
Start-Sleep -Seconds 5

$best = -1
for ($attempt = 0; $attempt -lt 12; $attempt++) {
    $bitmap = Capture $process
    $score = BrightCount $bitmap
    if ($score -gt $best) {
        $best = $score
        $bitmap.Save($shotPath, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    $bitmap.Dispose()
    Start-Sleep -Milliseconds 300
}

"BEST_BRIGHT=$best"
Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
