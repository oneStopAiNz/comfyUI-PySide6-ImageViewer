---
description: How to build the ComfyUI Image Viewer as a Windows EXE
---

To build the application as a standalone Windows executable (`.exe`), follow these steps:

1. **Activate Virtual Environment**:
   Ensure you are in the project root and your virtual environment is active.
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install PyInstaller** (if not already installed):
   ```powershell
   pip install pyinstaller
   ```

3. **Run the Build**:
   Use the existing `.spec` file to ensure all configurations (icon, hidden imports, etc.) are applied.
   // turbo
   ```powershell
   pyinstaller comfy_viewer.spec
   ```

4. **Locate the Executable**:
   The resulting `.exe` will be located in the `dist/` directory:
   `dist\comfy_viewer.exe`

> [!NOTE]
> The build process may take 1-2 minutes. The resulting file is a "one-file" bundle, meaning it contains all necessary DLLs and the Python interpreter itself.
