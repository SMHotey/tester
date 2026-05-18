@echo off
REM Build the application into a single exe file
REM Requires PyInstaller installed in the virtual environment

set SCRIPT_DIR=%~dp0
set ENTRY_POINT=%SCRIPT_DIR%main.py
set ICON_PATH=%SCRIPT_DIR%app_icon.ico

REM Data files to bundle (format: source;destination for Windows)
set DATA_FILES=questions.json;.%SCRIPT_DIR%reglament.json;.%SCRIPT_DIR%test_scenarios.json;.%SCRIPT_DIR%app_icon.png;.%SCRIPT_DIR%style_config.py;.%SCRIPT_DIR%_utils.py;.%SCRIPT_DIR%pdf_generator.py;.

echo Building single exe...

"%SCRIPT_DIR%.venv\Scripts\pyinstaller.exe" ^
  --onefile ^
  --icon="%ICON_PATH%" ^
  --add-data="%SCRIPT_DIR%questions.json;." ^
  --add-data="%SCRIPT_DIR%reglament.json;." ^
  --add-data="%SCRIPT_DIR%test_scenarios.json;." ^
  --add-data="%SCRIPT_DIR%app_icon.png;." ^
  --add-data="%SCRIPT_DIR%style_config.py;." ^
  --add-data="%SCRIPT_DIR%_utils.py;." ^
  --add-data="%SCRIPT_DIR%pdf_generator.py;." ^
  --name="tester 1.1" ^
  --clean ^
  "%ENTRY_POINT%"

echo.
if exist "%SCRIPT_DIR%dist\tester 1.1.exe" (
  echo Build successful! Exe location: "%SCRIPT_DIR%dist\tester 1.1.exe"
) else (
  echo Build failed! Check the output above.
)

pause
