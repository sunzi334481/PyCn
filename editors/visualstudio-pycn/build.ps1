# build.ps1 - 构建 PyCn Visual Studio 扩展（官方 VSSDK targets 方案）
# 用法：powershell -ExecutionPolicy Bypass -File .\build.ps1
# 依赖：Visual Studio（MSBuild）、sdktools\bt（VSSDK.BuildTools，缺失时从 NuGet 下载解压）
# 产物：PycnVsPackage\bin\Release\PycnVsPackage.vsix（或直接使用根目录已构建好的 pycn-vs.vsix）
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$msbuild = 'F:\VS\MSBuild\Current\Bin\MSBuild.exe'
if (-not (Test-Path $msbuild)) {
    # 尝试从注册表 / 常见路径查找 MSBuild
    $candidates = @(
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2026\Community\MSBuild\Current\Bin\MSBuild.exe",
        'F:\VS\MSBuild\Current\Bin\MSBuild.exe'
    )
    $msbuild = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $msbuild) { throw "未找到 MSBuild.exe，请检查 Visual Studio 安装路径" }

$proj = Join-Path $root 'PycnVsPackage\PycnVsPackage.csproj'
$fw = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319'

Write-Output '==> MSBuild Rebuild (Release) ...'
& $msbuild $proj /t:Rebuild /p:Configuration=Release "/p:FrameworkPathOverride=$fw" /nologo /v:minimal
if ($LASTEXITCODE -ne 0) { throw '构建失败' }

$vsix = Join-Path $root 'PycnVsPackage\bin\Release\PycnVsPackage.vsix'
if (Test-Path $vsix) {
    Write-Output ("==> 构建成功：" + $vsix)
    Get-Item $vsix | Select-Object Name, Length
} else {
    Write-Output '==> 构建成功，但未找到 .vsix（可能已配置不打包）'
}
