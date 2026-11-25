@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=
py --version >nul 2>&1 && set PY=py
if not defined PY python --version >nul 2>&1 && set PY=python
if not defined PY (
  echo 파이썬을 찾지 못했습니다. https://www.python.org 에서 설치한 뒤 다시 실행하세요.
  pause
  exit /b 1
)
echo [1/2] 작품 목록 만들기
%PY% build_manifest.py
echo.
echo [2/2] 미리보기 서버 시작 - 이 검은 창을 닫으면 뷰어도 멈춥니다.
start "" cmd /c "timeout /t 2 >nul & start http://localhost:8000/"
%PY% -m http.server 8000
