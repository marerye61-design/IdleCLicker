$version = Get-Content "version.txt" -ErrorAction SilentlyContinue
if (-not $version) { $version = "0.18" }
$version = $version.Trim().TrimStart("v")

Write-Host "=== Budowanie wersji v$version ==="

Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Force IdleClicker.spec -ErrorAction SilentlyContinue
Remove-Item -Force IdleClickerLauncher.spec -ErrorAction SilentlyContinue
Remove-Item -Force IdleClicker_*.zip -ErrorAction SilentlyContinue

$PYTHON = "C:\Users\Qonara\AppData\Local\Python\pythoncore-3.14-64\python.exe"

# Budowanie głownej gry z odchudzonymi assets i wykluczeniem zbędnych modułów
& $PYTHON -m PyInstaller --noconsole --onefile --name "IdleClicker" `
    --add-data "assets;assets" `
    --add-data "version.txt;." `
    --exclude-module unittest `
    --exclude-module test `
    --exclude-module pydoc `
    --exclude-module doctest `
    --exclude-module tkinter.test `
    main.py

# Budowanie Launchera
& $PYTHON -m PyInstaller --noconsole --onefile --name "IdleClickerLauncher" `
    --exclude-module unittest `
    --exclude-module test `
    IdleClickerLauncher.py

if (Test-Path "dist\IdleClicker.exe") {
    Copy-Item "version.txt" "dist\version.txt"
    $zipName = "IdleClicker_$version.zip"
    Compress-Archive -Path "dist\IdleClicker.exe", "dist\IdleClickerLauncher.exe", "dist\version.txt" -DestinationPath $zipName -Force
    Write-Host "=== Pomyślnie zbudowano paczkę: $zipName ==="
}
