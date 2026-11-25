@echo off
chcp 65001 >nul
cd /d "%~dp0"
set REPO=https://github.com/papamac69/3-_-_2026.git
where git >nul 2>&1
if errorlevel 1 (
  echo git을 찾지 못했습니다. https://git-scm.com 에서 설치한 뒤 다시 실행하세요.
  pause
  exit /b 1
)
if not exist ".git" (
  echo [준비] 이 폴더를 GitHub 저장소와 처음 연결합니다.
  git init -b main
  git remote add origin %REPO%
  git fetch origin
  git reset --soft origin/main 2>nul
  git config http.postBuffer 524288000
)
echo.
echo [1/2] 작품 목록 만들기
set PY=
py --version >nul 2>&1 && set PY=py
if not defined PY python --version >nul 2>&1 && set PY=python
if not defined PY (
  echo 파이썬을 찾지 못했습니다. https://www.python.org 에서 설치한 뒤 다시 실행하세요.
  pause
  exit /b 1
)
%PY% build_manifest.py
if errorlevel 1 (
  echo 목록 만들기 실패 - 위 오류를 확인하세요.
  pause
  exit /b 1
)
echo.
echo [2/2] GitHub에 올리기 - 파일이 많으면 몇 분 걸립니다.
git add -A
git commit -m "작품 업데이트 %date% %time:~0,5%"
git push -u origin main
echo.
echo 완료. 1~2분 뒤 사이트에 반영됩니다: https://papamac69.github.io/3-_-_2026/
pause
