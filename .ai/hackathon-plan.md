# 하루 해커톤 MVP 계획

## 🎯 핵심 전략: "Entry 챗봇 + 간단한 RAG"

### 시간 배분 (8시간 기준)
- **1-2시간**: 환경 설정 + Entry 데이터 수집
- **3-4시간**: RAG 시스템 구축 (AWS Bedrock + S3)
- **2-3시간**: 챗봇 웹 인터페이스 개발
- **1시간**: 데모 준비 + 발표 자료

## 🚀 MVP 범위

### 구현할 것
1. **Entry 지식 베이스 RAG**
   - Entry 공식 문서 크롤링/수집
   - S3에 텍스트 저장
   - Bedrock으로 임베딩 생성
   
2. **Entry 학습 챗봇**
   - Streamlit 기반 웹 인터페이스
   - Bedrock Claude 모델 활용
   - RAG 연동으로 Entry 관련 질답

3. **데모용 기능**
   - "Entry 블록 설명해줘"
   - "Entry로 게임 만드는 방법"
   - "Entry Python 변환 방법"

### 제외할 것
- MCP 서버 (시간 부족)
- Entry Studio 조작 (복잡도 높음)
- 복잡한 UI/UX
- 사용자 인증

## 🛠 기술 스택 (최소화)

### AWS 서비스 (3개만)
1. **Amazon Bedrock**: Claude 3.5 Sonnet
2. **Amazon S3**: Entry 문서 저장
3. **AWS Lambda**: API 엔드포인트 (선택사항)

### 개발 도구
- **Python**: 백엔드 로직
- **Streamlit**: 빠른 웹 인터페이스
- **boto3**: AWS SDK
- **requests**: 데이터 수집

## ⏰ 시간별 실행 계획

### 1시간: 환경 설정
```bash
# AWS 설정
aws configure
pip install streamlit boto3 requests beautifulsoup4

# 프로젝트 구조
mkdir -p src/{data,rag,chatbot}
```

### 2시간: Entry 데이터 수집
- Entry 공식 사이트 크롤링
- 튜토리얼, 블록 설명 수집
- S3 업로드 스크립트

### 3-4시간: RAG 구축
- Bedrock 임베딩 생성
- 벡터 검색 로직
- 컨텍스트 생성 함수

### 2-3시간: 챗봇 개발
- Streamlit 인터페이스
- Bedrock 연동
- RAG 통합

### 1시간: 데모 준비
- 테스트 시나리오
- 발표 자료 (3-5슬라이드)

## 📁 프로젝트 구조
```
qhack/
├── src/
│   ├── data_collector.py    # Entry 데이터 수집
│   ├── rag_system.py       # RAG 로직
│   ├── chatbot.py          # Streamlit 앱
│   └── config.py           # 설정
├── data/                   # 수집된 Entry 데이터
├── requirements.txt
└── README.md
```

## 🎪 데모 시나리오
1. **Entry 기초 질문**: "Entry에서 스프라이트란 무엇인가요?"
2. **실습 가이드**: "Entry로 간단한 게임을 만들고 싶어요"
3. **Python 연동**: "Entry 코드를 Python으로 어떻게 바꾸나요?"

## 🏆 성공 기준
- Entry 관련 질문에 정확한 답변 (RAG 기반)
- 3분 내 매끄러운 데모 진행
- AWS 서비스 활용 어필
- 교육적 가치 강조

## 🚨 리스크 대응
- **AWS 계정 이슈**: 로컬 임베딩 모델 대체
- **데이터 수집 실패**: 수동으로 샘플 데이터 준비
- **Bedrock 접근 불가**: OpenAI API 대체
- **시간 부족**: 하드코딩된 FAQ 시스템으로 축소