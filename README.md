# Entry Python RAG with AWS Bedrock

엔트리 파이썬 문서를 AWS Bedrock Knowledge Base로 구축하는 프로젝트

## 구성 요소

- **S3 버킷**: 엔트리 파이썬 문서 저장소
- **Bedrock Knowledge Base**: 고급 파싱 기능을 활용한 RAG
- **OpenSearch Serverless**: 벡터 데이터베이스
- **Claude 3 Sonnet**: 파싱 및 응답 생성 모델

## 배포 방법

```bash
# 1. 배포 스크립트 실행
./deploy.sh

# 2. 문서 준비 및 업로드
cd scripts
python prepare_docs.py

# 3. Bedrock 콘솔에서 Knowledge Base Sync
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