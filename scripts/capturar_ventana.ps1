param(
    [string]$Title = 'A4-CIS-2024-2388 - GNS3',
    [string]$Output = "$PSScriptRoot\..\docs\evidencias\01-topologia-real.png"
)
# Actual window capture. No generated or composited lab results.
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class A4Window {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int command);
}
'@
$process = Get-Process | Where-Object { $_.MainWindowTitle -eq $Title } | Select-Object -First 1
if (-not $process) { throw "Window not found: $Title" }
$handle = $process.MainWindowHandle
[void][A4Window]::ShowWindow($handle, 3)
[void][A4Window]::SetForegroundWindow($handle)
Start-Sleep -Milliseconds 800
$rect = New-Object A4Window+RECT
[void][A4Window]::GetWindowRect($handle, [ref]$rect)
$image = New-Object System.Drawing.Bitmap(($rect.Right - $rect.Left), ($rect.Bottom - $rect.Top))
$graphics = [System.Drawing.Graphics]::FromImage($image)
try {
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $image.Size)
    $image.Save([System.IO.Path]::GetFullPath($Output), [System.Drawing.Imaging.ImageFormat]::Png)
} finally {
    $graphics.Dispose()
    $image.Dispose()
}
Write-Output $Output
