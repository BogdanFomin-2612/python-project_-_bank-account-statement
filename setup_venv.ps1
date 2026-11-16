# Tworzy .venv, a jeśli jest uszkodzone (np. po aktualizacji/usunięciu wersji Pythona
# w C:\Users\<user>\AppData\Local\Python\), usuwa je i tworzy od nowa.
$ErrorActionPreference = "Stop"

function Test-Venv {
    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        return $false
    }
    & ".venv\Scripts\python.exe" --version *> $null
    return ($LASTEXITCODE -eq 0)
}

if (-not (Test-Venv)) {
    if (Test-Path ".venv") {
        Write-Host "Uszkodzone .venv (brakuje wersji Pythona, na którą wskazuje) - usuwam i tworzę od nowa."
        Remove-Item -Recurse -Force ".venv"
    }
    py -m venv .venv
}

& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "Gotowe. Uruchom program: .venv\Scripts\python.exe main.py"
