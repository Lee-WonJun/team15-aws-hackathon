# Senshilabs : 큐베 (Qube) - AI-Powered Entry Coding Platform

블록코딩과 AI의 결합으로 어린이들이 더 쉽게 코딩을 배울 수 있는 플랫폼  
*큐베(Qube): 인큐베이터(Incubator)의 줄임말로, 어린이들의 코딩 꿈을 키워주는 플랫폼*

## 어플리케이션 개요

**큐베(Qube)** 는 한국의 스크래치인 엔트리(Entry)를 기반으로 AI 기술을 결합한 교육용 블록코딩 플랫폼입니다. 최근 AI와 LLM 기술의 발전을 활용하여 어린이들이 더 직관적이고 쉽게 코딩을 학습할 수 있도록 지원합니다.

<img width="1175" height="704" alt="image" src="https://github.com/user-attachments/assets/5a589d80-242a-4efd-8abe-738b4d8e95ba" />
엔트리는 블록 코딩을 지원하는 프로그래밍 교육 플랫폼입니다. 특히 엔트리 파이썬은 블록 코딩을 Python 텍스트 코딩으로 변환하여 사용할 수 있는 기능을 제공합니다.

- 블록 코딩으로 작성한 프로그램을 Python 코드로 자동 변환
- 시각적 블록 코딩에서 텍스트 코딩으로 자연스러운 전환 가능

## 문제 정의

현재 교육 시장에는 수많은 노코드/블록코딩 플랫폼이 존재하지만, 대 AI 시대에 접어들면서 모든 것이 텍스트 토큰화되는 패러다
임 변화가 일어나고 있습니다. 

팬데믹 이후 코딩 교육 열풍과 AI 시대의 자연어 기반 프로그래밍이라는 두 가지 메가트렌드를 동시에 활용할 수 있는 혁신적인 
교육 플랫폼의 필요성이 대두되었습니다.

## 핵심 목표

### 🤖 진정한 AI 기반 코딩 교육
LLM을 활용하여 자연어 명령을 블록코딩으로 자동 변환하는 차세대 교육 경험 제공

### 🎯 직관적 학습 경험 
복잡한 프로그래밍 개념을 시각적 블록으로 단순화하여 누구나 쉽게 접근 가능한 코딩 교육

### 🔄 실시간 코드 변환
자연어 → Python → 블록코딩의 3단계 자동 변환 파이프라인으로 seamless한 학습 경험

### 📚 지능형 도움말
엔트리 API 정보를 기반으로 한 맞춤형 AI 가이드로 개인화된 학습 지원

## 주요 기능

### 1. 🤖 AI 챗봇 (Entry Knowledge Assistant)
- **엔트리 API 질의응답**: 사용 가능한 모든 블록과 함수 정보 제공
- **카테고리별 블록 검색**: 움직임, 소리, 화면 등 카테고리별 블록 탐색
- **Python 문법 가이드**: 각 블록의 Python 코드 변환 방법 안내
- **실시간 도움말**: AWS Bedrock 기반 지능형 응답 시스템

### 2. 🔧 MCP 서버 (Model Context Protocol)
- **API 정보 제공**: 엔트리의 모든 블록 및 함수 정보 구조화
- **Amazon Q 연동**: CLI를 통한 자연어 명령어 처리

### 3. 🎨 Entry Studio 연동
- **자동 코드 생성**: 자연어 명령을 Python 코드로 변환
- **블록코딩 변환**: Python 코드를 엔트리 블록으로 자동 변환
- **실시간 에디터 조작**: 웹 자동화를 통한 코드 삽입 및 수정

### 4. 📊 AWS 기반 인프라
- **S3 문서 저장소**: 엔트리 API 문서 및 가이드 저장
- **Bedrock Knowledge Base**: Claude 3.5 Sonnet 기반 RAG 시스템
- **EC2 서비스 배포**: 챗봇 및 MCP 서버 호스팅

## 동영상 데모

### 챗봇
https://github.com/user-attachments/assets/04d6c4ca-6e7c-4857-ab67-83168dc20e3d

### MCP with Studio
https://github.com/user-attachments/assets/ef28c2cd-c1b8-42e0-ab2d-6d2168cfcb9e



## 리소스 배포하기

### 시스템 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Amazon Q CLI  │───▶│   MCP Server     │───▶│  Entry Studio   │
│  (자연어 입력)    │    │  (API 정보 제공)   │    │  (블록코딩 변환)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   사용자 질문     │───▶│   AI 챗봇        │◀───│  Bedrock KB     │
│                │    │  (Streamlit)     │    │  (Claude 3)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        ▲
                                ▼                        │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   EC2 Instance   │    │   S3 Bucket     │
                       │  (서비스 호스팅)   │    │  (문서 저장소)   │
                       └──────────────────┘    └─────────────────┘
```

### 배포 단계
- IaC 의 경우 cloud 배포가 필요한 서비스들은 각 프로젝트 내에 cdk 배포/삭제가 구성되어 있습니다.

#### 1. 챗봇 서비스 배포
```bash
# Streamlit 챗봇 배포
cd deploy-ec2
./deploy.sh

# 배포 완료 후 접속
# URL: http://[EC2-PUBLIC-IP]:8000
```

#### 2. MCP 서버 배포
```bash
# MCP 서버 배포 (Python 3.11 환경)
cd deploy-mcp
./deploy.sh

# 수동 시작 (필요시)
ssh -i entry-mcp-key.pem ec2-user@[EC2-PUBLIC-IP]
cd /home/ec2-user/mcp-project/entry-mcp
source mcp-env/bin/activate
python entry_api_server.py
```

#### 3. Entry Studio 로컬 실행
```bash
# Entry Studio API 서버 실행
cd entry-studio
./run.sh

# API 접속: http://localhost:8000
```

### AWS 리소스 구성
<img width="1284" height="819" alt="image" src="https://github.com/user-attachments/assets/63fbf83a-bc92-4828-9856-373b52b5055d" />

- **EC2 Instance**: t3.medium (챗봇 및 MCP 서버)
- **S3 Bucket**: 엔트리 API 문서 저장소
- **Bedrock Knowledge Base**: Claude 3 Sonnet 기반 RAG
- **OpenSearch Serverless**: 벡터 데이터베이스
- **IAM Roles**: Bedrock 및 S3 접근 권한


### Public
 - 챗봇 : http://3.235.42.232:8000/
 - mcp : http://44.204.113.69:8000/ 

### 리소스 삭제
```bash
# CDK 스택 삭제
cd deploy-ec2/cdk && cdk destroy
cd deploy-mcp/cdk && cdk destroy

# 수동 생성된 리소스 확인 및 삭제
# - S3 버킷 내용물
# - Bedrock Knowledge Base
# - OpenSearch Serverless 컬렉션
```

## 프로젝트 기대 효과 및 예상 사용 사례

### 🎯 기대 효과

1. **코딩 교육의 접근성 향상**
   - 자연어로 코딩 의도를 표현하면 자동으로 블록코딩 생성
   - 복잡한 프로그래밍 개념을 직관적인 블록으로 학습

2. **학습 효율성 증대**
   - AI 기반 실시간 도움말로 학습 속도 향상
   - 개인화된 학습 경험 제공

3. **교육자 지원 강화**
   - 교사들이 더 효과적으로 코딩 교육 진행 가능
   - 학생 개별 질문에 대한 즉시 응답 시스템

### 💡 예상 사용 사례

#### 사례 1: 초보자 코딩 학습
```
학생: "캐릭터를 오른쪽으로 움직이게 하고 싶어요"
→ AI가 move_to_direction 블록을 추천하고 사용법 안내
→ 자동으로 해당 블록코딩 생성
```

#### 사례 2: API 탐색 및 학습
```
학생: "소리와 관련된 블록들이 뭐가 있나요?"
→ 챗봇이 sound 카테고리의 모든 블록 목록 제공
→ 각 블록의 사용법과 예제 코드 설명
```

#### 사례 3: 자연어 기반 프로그래밍
```
Amazon Q CLI: "공을 화면 가장자리에서 튕기게 만들어줘"
→ MCP 서버가 bounce_on_edge API 정보 제공
→ Python 코드 자동 생성 및 블록코딩 변환
```

#### 사례 4: 교실 수업 지원
```
교사: 학생들이 게임 만들기 수업 중 막힐 때
→ 실시간 AI 도우미가 개별 질문 해결
→ 수업 진행 속도 향상 및 학습 만족도 증대
```

### 🌟 장기적 비전

- **글로벌 확장**: 다국어 지원으로 전 세계 어린이 코딩 교육 지원
- **커리큘럼 통합**: 학교 정규 교육과정과의 연계
- **AI 튜터 발전**: 개인별 학습 패턴 분석 및 맞춤형 교육 제공
- **오픈소스 생태계**: 교육 커뮤니티와 함께 발전하는 플랫폼

---

**개발팀 Senshilabs**  
*Amazon Q Developer Hackathon 2025*
