# Entry Python RAG Embedding

엔트리 파이썬 문서를 AWS Bedrock Knowledge Base로 임베딩하는 프로젝트

## 폴더 구조

```
entry-embedding/
├── entry_python_rag_docs.json    # 최종 RAG 문서 데이터
├── deploy/                       # AWS 배포 관련 파일들
│   ├── cdk/                     # CDK 인프라 코드
│   ├── scripts/                 # 배포 스크립트
│   ├── .env                     # 환경 변수
│   └── deploy.sh               # 메인 배포 스크립트
├── extraction/                   # 데이터 추출 관련 파일들
│   ├── extract_blocks.py        # 블록 추출 스크립트
│   ├── generate_rag_docs.py     # RAG 문서 생성
│   ├── extracted_blocks.json    # 추출된 블록 데이터
│   └── (기타 추출 관련 파일들)
├── docs/                        # 문서 및 설명
│   ├── bedrock_kb_architecture.md
│   ├── EXTRACTION_SUMMARY.md
│   └── TODO.md
└── README.md                    # 이 파일
```

## 배포 방법

```bash
cd entry-embedding/deploy

# 1. 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (AWS_ACCOUNT_ID, AWS_PROFILE 등)

# 2. 배포 실행
./deploy.sh

# 3. 문서 업로드
cd scripts
python prepare_docs.py

# 4. Bedrock 콘솔에서 Knowledge Base Sync
```

## 주요 기능

- **고급 파싱**: Claude 3 Sonnet을 활용한 문서 구조화
- **계층적 청킹**: 1500/300 토큰 단위 계층 구조  
- **메타데이터 활용**: 카테고리, 블록 ID 기반 정밀 검색

## 사용 예시

```
Q: Entry.is_mouse_clicked() 함수 사용법을 알려줘
Q: boolean_input 카테고리에 어떤 블록들이 있나요?
Q: 날씨 관련 블록의 Python 문법을 보여줘
```