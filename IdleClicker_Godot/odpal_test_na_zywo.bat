@echo off
chcp 65001 >nul
echo ===================================================================
echo   IDLECLICKER GODOT - AUTOMATYCZNY TEST NA ŻYWO (EKRAN 3 / DOWOLNY)
echo ===================================================================
echo Uruchamianie gry na żywo z Always-On-Top...
start "" "C:\Users\Qonara\AppData\Local\Microsoft\WinGet\Links\godot.exe" --path "C:\Users\Qonara\Documents\IdleClicker_Godot" "res://test/AutomatedLiveTester.tscn"
echo Okno gry zostało otwarte na pulpicie!
