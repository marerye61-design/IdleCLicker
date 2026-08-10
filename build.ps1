Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Force IdleClicker.spec -ErrorAction SilentlyContinue
Remove-Item -Force IdleClickerLauncher.spec -ErrorAction SilentlyContinue
Remove-Item -Force IdleClicker_0.14_pre-alpha.zip -ErrorAction SilentlyContinue
Remove-Item -Force IdleClicker_0.15.zip -ErrorAction SilentlyContinue

C:\Users\Qonara\AppData\Local\Python\pythoncore-3.14-64\python.exe -m PyInstaller --noconsole --onefile --name "IdleClicker" --add-data "assets;assets" --add-data "version.txt;." main.py
C:\Users\Qonara\AppData\Local\Python\pythoncore-3.14-64\python.exe -m PyInstaller --noconsole --onefile --name "IdleClickerLauncher" IdleClickerLauncher.py

if (Test-Path "dist\IdleClicker.exe") {
    Compress-Archive -Path "dist\IdleClicker.exe", "dist\IdleClickerLauncher.exe", "assets" -DestinationPath "IdleClicker_0.15.zip" -Force
}
