# 🖥️ MLOps 교육 사전 설치 가이드 (Windows)

> **대상**: Windows 10/11 사용자  
> **완료 기한**: 2025년 12월 15일 (일)까지  
> **예상 소요시간**: 30~45분

---

## 📋 설치 순서

1. [Git 설치](#1-git-설치)
2. [Python 3.9+ 설치](#2-python-39-설치)
3. [Docker Desktop 설치](#3-docker-desktop-설치)
4. [AWS CLI v2 설치](#4-aws-cli-v2-설치)
5. [kubectl 설치](#5-kubectl-설치)
6. [설치 검증](#6-설치-검증)

---

## 1. Git 설치

### Step 1-1: 다운로드
1. https://git-scm.com/download/windows 접속
2. **"Click here to download"** 클릭하여 최신 버전 다운로드

### Step 1-2: 설치
1. 다운로드된 `Git-x.xx.x-64-bit.exe` 실행
2. 설치 옵션은 **모두 기본값**으로 진행 (Next 클릭)
3. 특히 아래 옵션 확인:
   - ✅ **Git Bash Here** (우클릭 메뉴에 추가)
   - ✅ **Use Git from Git Bash only** 또는 **Git from the command line...**

### Step 1-3: 설치 확인
**PowerShell** 또는 **명령 프롬프트**를 **새로 열고** 실행:
```powershell
git --version
```
**예상 출력**: `git version 2.43.0.windows.1` (버전은 다를 수 있음)

---

## 2. Python 3.9+ 설치

### Step 2-1: 다운로드
1. https://www.python.org/downloads/ 접속
2. **"Download Python 3.12.x"** (또는 3.9 이상) 클릭

### Step 2-2: 설치
1. 다운로드된 `python-3.xx.x-amd64.exe` 실행
2. ⚠️ **매우 중요**: 설치 첫 화면에서 **"Add python.exe to PATH"** 체크 ✅
3. **"Install Now"** 클릭

### Step 2-3: 설치 확인
**PowerShell**을 **새로 열고** 실행:
```powershell
python --version
```
**예상 출력**: `Python 3.12.x`

```powershell
pip --version
```
**예상 출력**: `pip 24.x.x from ...`

### Step 2-4: 필수 패키지 설치
```powershell
pip install kfp==1.8.22 mlflow==2.9.2 scikit-learn pandas numpy requests
```

---

## 3. Docker Desktop 설치

### Step 3-1: WSL2 활성화 (필수)
**PowerShell을 관리자 권한으로 실행** 후:
```powershell
wsl --install
```
설치 후 **컴퓨터 재시작** 필요

### Step 3-2: Docker Desktop 다운로드
1. https://www.docker.com/products/docker-desktop/ 접속
2. **"Download for Windows"** 클릭

### Step 3-3: 설치
1. 다운로드된 `Docker Desktop Installer.exe` 실행
2. 설치 옵션:
   - ✅ **Use WSL 2 instead of Hyper-V** (권장)
3. 설치 완료 후 **컴퓨터 재시작**

### Step 3-4: Docker Desktop 실행
1. 시작 메뉴에서 **Docker Desktop** 실행
2. 첫 실행 시 라이선스 동의 후 대기 (1-2분)
3. 좌측 하단에 **"Docker Desktop is running"** 확인 (녹색 아이콘)

### Step 3-5: 설치 확인
```powershell
docker --version
```
**예상 출력**: `Docker version 24.x.x, build xxxxx`

```powershell
docker run hello-world
```
**예상 출력**: `Hello from Docker!` 메시지

---

## 4. AWS CLI v2 설치

### Step 4-1: 다운로드
1. https://aws.amazon.com/cli/ 접속
2. **"Download and run the 64-bit Windows installer"** 클릭
3. 또는 직접 다운로드: https://awscli.amazonaws.com/AWSCLIV2.msi

### Step 4-2: 설치
1. 다운로드된 `AWSCLIV2.msi` 실행
2. 모든 옵션 **기본값**으로 진행

### Step 4-3: 설치 확인
**PowerShell을 새로 열고** 실행:
```powershell
aws --version
```
**예상 출력**: `aws-cli/2.15.x Python/3.11.x Windows/10 ...`

### Step 4-4: AWS 자격 증명 설정 (교육 당일 진행)
```powershell
aws configure
```
입력 값 (강사가 제공):
```
AWS Access Key ID: [교육 당일 제공]
AWS Secret Access Key: [교육 당일 제공]
Default region name: ap-northeast-2
Default output format: json
```

---

## 5. kubectl 설치

### Step 5-1: 다운로드
**PowerShell**에서 실행:
```powershell
# kubectl 다운로드
curl.exe -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"
```

### Step 5-2: 설치
```powershell
# kubectl을 PATH가 포함된 디렉토리로 이동
# 방법 1: 사용자 디렉토리에 bin 폴더 생성
mkdir -Force $HOME\bin
Move-Item -Force kubectl.exe $HOME\bin\kubectl.exe

# 환경 변수 PATH에 추가 (영구 설정)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$HOME\bin", "User")
```

### Step 5-3: PowerShell 재시작 후 확인
**PowerShell을 새로 열고** 실행:
```powershell
kubectl version --client
```
**예상 출력**: `Client Version: v1.28.x`

---

## 6. 설치 검증

### 전체 검증 스크립트
아래 내용을 `verify_setup.ps1` 파일로 저장 후 실행:

```powershell
# MLOps 교육 환경 검증 스크립트 (Windows)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  MLOps 교육 환경 검증" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0

# 1. Git 확인
Write-Host -NoNewline "1. Git: "
try {
    $gitVersion = git --version 2>&1
    Write-Host "✅ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 설치 필요" -ForegroundColor Red
    $errors++
}

# 2. Python 확인
Write-Host -NoNewline "2. Python: "
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 설치 필요" -ForegroundColor Red
    $errors++
}

# 3. pip 확인
Write-Host -NoNewline "3. pip: "
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ 설치됨" -ForegroundColor Green
} catch {
    Write-Host "❌ 설치 필요" -ForegroundColor Red
    $errors++
}

# 4. Docker 확인
Write-Host -NoNewline "4. Docker: "
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 설치 필요" -ForegroundColor Red
    $errors++
}

# 5. AWS CLI 확인
Write-Host -NoNewline "5. AWS CLI: "
try {
    $awsVersion = aws --version 2>&1
    Write-Host "✅ 설치됨" -ForegroundColor Green
} catch {
    Write-Host "❌ 설치 필요" -ForegroundColor Red
    $errors++
}

# 6. kubectl 확인
Write-Host -NoNewline "6. kubectl: "
try {
    $kubectlVersion = kubectl version --client 2>&1
    Write-Host "✅ 설치됨" -ForegroundColor Green
} catch {
    Write-Host "❌ 설치 필요" -ForegroundColor Red
    $errors++
}

# 7. Python 패키지 확인
Write-Host -NoNewline "7. kfp 패키지: "
try {
    python -c "import kfp; print(kfp.__version__)" 2>&1 | Out-Null
    Write-Host "✅ 설치됨" -ForegroundColor Green
} catch {
    Write-Host "❌ pip install kfp 필요" -ForegroundColor Yellow
}

Write-Host -NoNewline "8. mlflow 패키지: "
try {
    python -c "import mlflow; print(mlflow.__version__)" 2>&1 | Out-Null
    Write-Host "✅ 설치됨" -ForegroundColor Green
} catch {
    Write-Host "❌ pip install mlflow 필요" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

if ($errors -eq 0) {
    Write-Host "🎉 모든 필수 도구가 설치되었습니다!" -ForegroundColor Green
} else {
    Write-Host "⚠️  $errors 개 도구 설치가 필요합니다." -ForegroundColor Yellow
}

Write-Host "============================================" -ForegroundColor Cyan
```

### 실행 방법
```powershell
# 스크립트 실행 정책 변경 (최초 1회)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 스크립트 실행
.\verify_setup.ps1
```

---

## ⚠️ 자주 발생하는 문제 및 해결

### 문제 1: "python을 찾을 수 없습니다"
**원인**: PATH 환경변수에 Python이 추가되지 않음

**해결**:
1. Windows 검색에서 "환경 변수" 검색
2. "시스템 환경 변수 편집" 클릭
3. "환경 변수" 버튼 클릭
4. "Path" 선택 후 "편집"
5. "새로 만들기"로 Python 경로 추가:
   - `C:\Users\[사용자명]\AppData\Local\Programs\Python\Python312`
   - `C:\Users\[사용자명]\AppData\Local\Programs\Python\Python312\Scripts`

### 문제 2: Docker Desktop이 시작되지 않음
**원인**: WSL2가 제대로 설치되지 않음

**해결**:
```powershell
# WSL 상태 확인
wsl --status

# WSL 업데이트
wsl --update

# 재시작 후 Docker Desktop 실행
```

### 문제 3: "kubectl을 찾을 수 없습니다"
**원인**: PATH에 추가되지 않음

**해결**:
1. kubectl.exe 파일 위치 확인
2. 해당 경로를 환경 변수 Path에 추가

---

## 📞 문의

설치 중 해결되지 않는 문제가 있으시면 아래로 연락해 주세요:
- 이메일: [강사 이메일]
- Slack: [채널명]

---

*최종 업데이트: 2025년 12월 11일*
