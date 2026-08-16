#!/usr/bin/env python3
"""
Build script to create Arcanova AI EXE executable
Requires: pip install pyinstaller

Usage:
    python build_exe.py
    
Output:
    dist/arcanova.exe
"""

import sys
import subprocess
from pathlib import Path

def build_exe():
    """Build Arcanova AI as standalone EXE"""
    
    print("🔨 Building Arcanova AI EXE...")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Paths
    app_file = project_root / "app.py"
    icon_file = project_root / "assets" / "arcanova.ico"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    # Create assets directory if needed
    assets_dir = project_root / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Check if app.py exists
    if not app_file.exists():
        print(f"❌ Error: {app_file} not found!")
        sys.exit(1)
    
    print(f"✅ App file found: {app_file}")
    
    # PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--name", "arcanova",  # Output name
        "--distpath", str(dist_dir),  # Output directory
        "--buildpath", str(build_dir),  # Build cache
        "--specpath", str(project_root),  # Spec file location
        f"--icon={icon_file}",  # Icon file (if it exists)
        "--collect-submodules", "transformers",  # Include transformers
        "--collect-submodules", "torch",  # Include torch
        "--collect-submodules", "streamlit",  # Include streamlit
        "--hidden-import=pyttsx3",  # Hidden imports
        "--hidden-import=reportlab",
        "--hidden-import=numpy",
        app_file
    ]
    
    # Remove --icon if icon doesn't exist
    if not icon_file.exists():
        print("⚠️  Icon file not found, building without icon")
        pyinstaller_cmd = [cmd for cmd in pyinstaller_cmd if "--icon" not in cmd]
    
    # Run PyInstaller
    print("\n🚀 Running PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_cmd)}\n")
    
    try:
        result = subprocess.run(pyinstaller_cmd, check=True)
        
        if result.returncode == 0:
            exe_path = dist_dir / "arcanova.exe"
            
            if exe_path.exists():
                exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print("\n" + "=" * 50)
                print("✅ BUILD SUCCESSFUL!")
                print("=" * 50)
                print(f"📦 Executable: {exe_path}")
                print(f"📊 Size: {exe_size:.2f} MB")
                print("\n📝 IMPORTANT NOTES:")
                print("1. First run will download models (~7GB for Qwen + TTS)")
                print("2. Requires ~16GB RAM for optimal performance")
                print("3. GPU recommended for faster generation")
                print("4. Models are cached locally, subsequent runs are faster")
                print("\n✨ Ready to deploy!")
                
                return True
            else:
                print("❌ Build failed: EXE not created")
                return False
        else:
            print("❌ Build failed")
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller error: {str(e)}")
        print("\n💡 Make sure PyInstaller is installed:")
        print("   pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def create_launcher_script():
    """Create a batch launcher script"""
    launcher_content = """@echo off
REM Arcanova AI Launcher

echo.
echo ===================================
echo   Arcanova AI - Story Generator
echo ===================================
echo.
echo Starting application...
echo.

REM Check if models exist
if not exist "models\\" (
    echo Downloading models on first run...
    echo This may take 5-10 minutes depending on internet speed
    echo Please be patient...
    echo.
)

REM Run the application
cd /d "%~dp0"
python -m streamlit run app.py --logger.level=error

pause
"""
    
    launcher_file = Path(__file__).parent / "launch.bat"
    with open(launcher_file, 'w') as f:
        f.write(launcher_content)
    print(f"✅ Launcher script created: {launcher_file}")

if __name__ == "__main__":
    print("\n🎭 Arcanova AI - Build System")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not installed!")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Create launcher script
    create_launcher_script()
    
    # Build EXE
    success = build_exe()
    
    if success:
        print("\n🎉 All done! Your executable is ready.")
        print(f"📂 Location: ./dist/arcanova.exe")
    else:
        print("\n⚠️  Build encountered issues. Check the output above.")
        sys.exit(1)