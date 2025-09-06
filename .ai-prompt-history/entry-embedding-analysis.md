# Entry-Embedding 분석 및 문서화 프롬프트

## 요청 내용
```
entry-embedding 이 임베딩이 어떻게 이루어 지는건지 확인하고, 이걸 entry-embedding 의 README.md 에 작성한뒤, 이 embedding 시퀀스를 다이어그램으로 그리고 산출물을 .ai 에 넣어줘
```

## 후속 요청
```
셋업 해달라는게 아니라, 코드 분석하고, readme 를 작성해줘, 예를들어서 entryjs 은 외부 오픈소스라 이 repo 에 포함이 안되서 돌리기전에 특정위치에 clone 받고 python 돌려야할텐데
```

## 작업 결과

### 1. 코드 분석 완료
- `entry-embedding/extraction/build_all.py` 분석
- `entry-embedding/deploy/cdk/bedrock_stack.py` 분석  
- `entry-embedding/deploy/create_index_simple.py` 분석
- EntryJS 외부 의존성 파악

### 2. README.md 업데이트
- EntryJS 클론 필요성 및 방법 설명
- 데이터 추출 프로세스 4단계 상세 분석
- JavaScript 정규식 파싱 로직 설명
- 실행 방법 및 주의사항 포함

### 3. 시퀀스 다이어그램 생성 (.ai/entry-embedding-sequence.md)
- 전체 임베딩 프로세스 시퀀스
- 데이터 추출 상세 시퀀스  
- AWS Bedrock 임베딩 내부 프로세스
- RAG 검색 시퀀스

## 핵심 발견사항
1. **외부 의존성**: EntryJS 오픈소스를 `.entryjs`에 클론 필요
2. **정규식 파싱**: `py: [...]` 패턴으로 JavaScript에서 Python 문법 추출
3. **상대경로 의존**: `../../.entryjs/entryjs/src/playground/blocks` 경로 사용
4. **자동화 파이프라인**: 추출→문서생성→S3업로드→Bedrock임베딩→OpenSearch저장

## 생성된 파일
- `entry-embedding/README.md` (업데이트)
- `.ai/entry-embedding-sequence.md` (신규)
