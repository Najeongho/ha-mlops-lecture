# 🍎 MLOps 교육 사전 설치 가이드 (macOS)

> **대상**: macOS 사용자 (Intel/Apple Silicon 모두 지원)  
> **완료 기한**: 2025년 12월 15일 (일)까지  
> **예상 소요시간**: 20~30분

---

## 📋 설치 순서

1. [Homebrew 설치](#1-homebrew-설치)
2. [Git 설치](#2-git-설치)
3. [Python 3.9+ 설치](#3-python-39-설치)
4. [Docker Desktop 설치](#4-docker-desktop-설치)
5. [AWS CLI v2 설치](#5-aws-cli-v2-설치)
6. [kubectl 설치](#6-kubectl-설치)
7. [설치 검증](#7-설치-검증)

---

## 1. Homebrew 설치

> Homebrew는 macOS의 패키지 관리자입니다. 이후 설치가 매우 간편해집니다.

### Step 1-1: Homebrew 설치
**터미널**을 열고 실행:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 1-2: PATH 설정 (Apple Silicon Mac만 해당)
Apple Silicon(M1/M2/M3) Mac인 경우 추가 설정 필요:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

### Step 1-3: 설치 확인
```bash
brew --version
```
**예상 출력**: `Homebrew 4.x.x`

---

## 2. Git 설치

### Step 2-1: 설치
```bash
brew install git
```

### Step 2-2: 설치 확인
```bash
git --version
```
**예상 출력**: `git version 2.43.x`

### Step 2-3: Git 설정 (선택)
```bash
git config --global user.name "본인 이름"
git config --global user.email "본인 이메일"
```

---

## 3. Python 3.9+ 설치

### Step 3-1: 설치
```bash
brew install python@3.12
```

### Step 3-2: 설치 확인
```bash
python3 --version
```
**예상 출력**: `Python 3.12.x`

```bash
pip3 --version
```
**예상 출력**: `pip 24.x.x from ...`

### Step 3-3: 필수 패키지 설치
```bash
pip3 install kfp==1.8.22 mlflow==2.9.2 scikit-learn pandas numpy requests
```

### Step 3-4: python 명령어 설정 (선택)
```bash
# python3 대신 python으로 사용하고 싶은 경우
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc
```

---

## 4. Docker Desktop 설치

### Step 4-1: 다운로드 및 설치

**방법 1: Homebrew 사용 (권장)**
```bash
brew install --cask docker
```

**방법 2: 직접 다운로드**
1. https://www.docker.com/products/docker-desktop/ 접속
2. **"Download for Mac"** 클릭
   - Apple Silicon (M1/M2/M3): **"Mac with Apple chip"**
   - Intel Mac: **"Mac with Intel chip"**
3. 다운로드된 `Docker.dmg` 실행
4. Docker 아이콘을 Applications 폴더로 드래그

### Step 4-2: Docker Desktop 실행
1. **Applications** → **Docker** 실행
2. 첫 실행 시 시스템 권한 허용
3. 메뉴바에 🐳 아이콘이 나타나고 **"Docker Desktop is running"** 확인

### Step 4-3: 설치 확인
```bash
docker --version
```
**예상 출력**: `Docker version 24.x.x, build xxxxx`

```bash
docker run hello-world
```
**예상 출력**: `Hello from Docker!` 메시지

---

## 5. AWS CLI v2 설치

### Step 5-1: 설치
```bash
brew install awscli
```

### Step 5-2: 설치 확인
```bash
aws --version
```
**예상 출력**: `aws-cli/2.15.x Python/3.11.x Darwin/23.x.x ...`

### Step 5-3: AWS 자격 증명 설정 (교육 당일 진행)
```bash
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

## 6. kubectl 설치

### Step 6-1: 설치
```bash
brew install kubectl
```

### Step 6-2: 설치 확인
```bash
kubectl version --client
```
**예상 출력**: `Client Version: v1.28.x`

---

## 7. 설치 검증

### 전체 검증 스크립트
아래 내용을 `verify_setup.sh` 파일로 저장 후 실행:

```bash
#!/bin/bash

# MLOps 교육 환경 검증 스크립트 (macOS)

echo "============================================"
echo "  MLOps 교육 환경 검증"
echo "============================================"
echo ""

errors=0

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Git 확인
echo -n "1. Git: "
if command -v git &> /dev/null; then
    echo -e "${GREEN}✅ $(git --version)${NC}"
else
    echo -e "${RED}❌ 설치 필요${NC}"
    ((errors++))
fi

# 2. Python 확인
echo -n "2. Python: "
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ $(python3 --version)${NC}"
else
    echo -e "${RED}❌ 설치 필요${NC}"
    ((errors++))
fi

# 3. pip 확인
echo -n "3. pip: "
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✅ 설치됨${NC}"
else
    echo -e "${RED}❌ 설치 필요${NC}"
    ((errors++))
fi

# 4. Docker 확인
echo -n "4. Docker: "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ $(docker --version)${NC}"
else
    echo -e "${RED}❌ 설치 필요${NC}"
    ((errors++))
fi

# 5. AWS CLI 확인
echo -n "5. AWS CLI: "
if command -v aws &> /dev/null; then
    echo -e "${GREEN}✅ 설치됨${NC}"
else
    echo -e "${RED}❌ 설치 필요${NC}"
    ((errors++))
fi

# 6. kubectl 확인
echo -n "6. kubectl: "
if command -v kubectl &> /dev/null; then
    echo -e "${GREEN}✅ 설치됨${NC}"
else
    echo -e "${RED}❌ 설치 필요${NC}"
    ((errors++))
fi

# 7. Python 패키지 확인
echo -n "7. kfp 패키지: "
if python3 -c "import kfp" 2>/dev/null; then
    echo -e "${GREEN}✅ 설치됨${NC}"
else
    echo -e "${YELLOW}❌ pip3 install kfp 필요${NC}"
fi

echo -n "8. mlflow 패키지: "
if python3 -c "import mlflow" 2>/dev/null; then
    echo -e "${GREEN}✅ 설치됨${NC}"
else
    echo -e "${YELLOW}❌ pip3 install mlflow 필요${NC}"
fi

echo ""
echo "============================================"

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}🎉 모든 필수 도구가 설치되었습니다!${NC}"
else
    echo -e "${YELLOW}⚠️  $errors 개 도구 설치가 필요합니다.${NC}"
fi

echo "============================================"
```

### 실행 방법
```bash
# 실행 권한 부여
chmod +x verify_setup.sh

# 스크립트 실행
./verify_setup.sh
```

### 빠른 검증 (한 줄 명령)
```bash
echo "Git: $(git --version 2>/dev/null || echo '❌')" && \
echo "Python: $(python3 --version 2>/dev/null || echo '❌')" && \
echo "Docker: $(docker --version 2>/dev/null || echo '❌')" && \
echo "AWS CLI: $(aws --version 2>/dev/null || echo '❌')" && \
echo "kubectl: $(kubectl version --client --short 2>/dev/null || echo '❌')"
```

---

## ⚠️ 자주 발생하는 문제 및 해결

### 문제 1: "brew: command not found"
**원인**: Homebrew PATH 미설정 (특히 Apple Silicon Mac)

**해결**:
```bash
# Apple Silicon Mac
eval "$(/opt/homebrew/bin/brew shellenv)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc

# Intel Mac
eval "$(/usr/local/bin/brew shellenv)"
```

### 문제 2: Docker Desktop이 시작되지 않음
**원인**: 권한 문제 또는 리소스 부족

**해결**:
1. **시스템 환경설정** → **보안 및 개인 정보 보호** → **일반** 탭
2. "Docker" 관련 항목 **허용** 클릭
3. Docker Desktop 재시작

### 문제 3: "python3: command not found"
**원인**: Python이 제대로 설치되지 않음

**해결**:
```bash
# Homebrew로 재설치
brew reinstall python@3.12

# 쉘 재시작
exec zsh
```

### 문제 4: pip 패키지 설치 시 권한 오류
**원인**: 시스템 Python에 설치 시도

**해결**:
```bash
# --user 옵션 사용
pip3 install --user kfp mlflow scikit-learn pandas numpy
```

### 문제 5: Apple Silicon에서 일부 패키지 호환성 문제
**원인**: arm64 아키텍처 미지원 패키지

**해결**:
```bash
# Rosetta 2 설치 (필요한 경우)
softwareupdate --install-rosetta

# x86_64 모드로 터미널 실행
arch -x86_64 /bin/bash
```

---

## 🔧 추가 유용한 설정

### VS Code 설치 (권장)
```bash
brew install --cask visual-studio-code
```

### Jupyter Notebook 설치 (선택)
```bash
pip3 install jupyter
```

### 터미널 꾸미기 (선택)
```bash
# Oh My Zsh 설치
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

---

## 📞 문의

설치 중 해결되지 않는 문제가 있으시면 아래로 연락해 주세요:
- 이메일: [강사 이메일]
- Slack: [채널명]

---

*최종 업데이트: 2025년 12월 11일*
