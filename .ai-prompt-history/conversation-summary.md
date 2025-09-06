# Entry Python RAG 챗봇 개발 대화 기록

## 프로젝트 개요
- **목표**: 엔트리 파이썬 문서를 AWS Bedrock Knowledge Base로 구축하여 RAG 챗봇 개발
- **Knowledge Base ID**: `9R38KN62YH`
- **주요 기술**: AWS Bedrock, Claude 3 Sonnet, Streamlit, EC2 배포

## 주요 대화 내용

### 1. 초기 설정 및 Knowledge Base 확인
- Knowledge Base ID `9R38KN62YH` 확인
- 테스트 쿼리로 엔트리 파이썬 문서 검색 성공
- moving 카테고리, input 블록 등 문서 확인

### 2. 로컬 Streamlit 챗봇 개발
- `bedrock_client.py`: Bedrock 클라이언트 및 RAG 로직 구현
- `streamlit_app.py`: Streamlit 웹 인터페이스 구현
- Knowledge Base ID 오류 수정 (`entry-python-docs` → `9R38KN62YH`)

### 3. EC2 배포 자동화 (CDK)
- **첫 번째 시도**: Python 스크립트로 EC2 생성
- **두 번째 시도**: CDK로 완전 자동화
- **문제점들**:
  - pip 패키지 충돌 (requests 패키지)
  - User Data 실행 실패
  - 파일 업로드 구조 문제
  - streamlit_app.py 파일 누락

### 4. 배포 문제 해결 과정
- **S3 업로드 방식**: 복잡한 파일 구조로 인한 실패
- **가상환경 사용**: 시스템 패키지 충돌 해결
- **파일 직접 생성**: User Data에서 모든 파일을 직접 생성하는 방식으로 변경
- **aws_config 모듈 활용**: 하드코딩 제거, 기존 설정 모듈 재사용

### 5. 최종 해결책
- CDK에서 S3 업로드 제거
- User Data에서 모든 파일 직접 생성
- aws_config 모듈에서 AWS 자격 증명 가져오기
- 가상환경에서 패키지 설치 및 실행

## 핵심 학습 사항

### 1. AWS 자격 증명 관리
```
중요 원칙: AWS 관련 정보는 aws_config/config.py 코드를 이용해 가져오기
- 하드코딩 금지
- 기존 설정 모듈 재사용
- get_bedrock_client(), get_bedrock_agent_runtime_client() 등 활용
```

### 2. EC2 User Data 베스트 프랙티스
- 로깅 활성화: `exec > >(tee /var/log/user-data.log) 2>&1`
- 가상환경 사용으로 패키지 충돌 방지
- 파일 소유권 설정: `chown -R ec2-user:ec2-user`
- nohup으로 백그라운드 실행

### 3. CDK 구조화
- 단순한 구조가 더 안정적
- S3 업로드보다 직접 파일 생성이 확실
- 매개변수를 통한 설정 전달

## 최종 배포 결과
- **인스턴스 ID**: `i-07b98fb47f00f416a`
- **퍼블릭 IP**: `3.215.180.187`
- **Streamlit URL**: http://3.215.180.187:8000
- **SSH 접속**: `ssh -i streamlit-chatbot-key.pem ec2-user@3.215.180.187`

## 파일 구조
```
team15-aws-hackathon/
├── chatbot/
│   ├── streamlit_app.py
│   ├── bedrock_client.py
│   └── requirements.txt
├── aws_config/
│   ├── __init__.py
│   └── config.py
├── deploy-ec2/
│   ├── cdk/
│   │   ├── app.py
│   │   ├── streamlit_stack_simple.py
│   │   └── requirements.txt
│   └── deploy.sh
└── .env
```

## 주요 명령어

### 로컬 실행
```bash
cd chatbot
source streamlit-env/bin/activate
streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0
```

### CDK 배포
```bash
cd deploy-ec2
./deploy.sh
```

### EC2 수동 설정
```bash
cd /home/ec2-user/chatbot
python3 -m venv streamlit-env
source streamlit-env/bin/activate
pip install streamlit boto3 python-dotenv
nohup streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

## 트러블슈팅 경험
1. **Knowledge Base ID 오류**: 정확한 ID 확인 필요
2. **pip 충돌**: 가상환경 사용으로 해결
3. **파일 누락**: User Data에서 직접 생성으로 해결
4. **권한 문제**: chown으로 소유권 변경
5. **서비스 시작 실패**: nohup + 가상환경 절대 경로 사용

## 성공 요인
- 단계별 문제 해결 접근
- 로깅을 통한 디버깅
- 단순한 구조 선택
- 기존 설정 모듈 재사용
- 가상환경을 통한 격리