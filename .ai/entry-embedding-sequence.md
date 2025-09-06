# Entry Python RAG 임베딩 시퀀스 다이어그램

## 전체 임베딩 프로세스 시퀀스

```mermaid
sequenceDiagram
    participant Dev as 개발자
    participant EntryJS as EntryJS 소스
    participant Extract as build_all.py
    participant CDK as AWS CDK
    participant AWS as AWS 서비스

    Note over Dev,AWS: 1단계: 데이터 준비
    Dev->>EntryJS: git clone entryjs.git .entryjs
    Dev->>Extract: python3 build_all.py
    Extract->>EntryJS: JavaScript 블록 파일 파싱
    Extract->>Extract: RAG 문서 생성 (39개)
    
    Note over Dev,AWS: 2단계: AWS 배포
    Dev->>CDK: ./deploy_final.sh
    CDK->>AWS: S3 + Bedrock + OpenSearch 생성
    CDK->>AWS: 문서 업로드 및 임베딩
    AWS-->>Dev: RAG 시스템 완료
```

## 데이터 추출 상세 시퀀스

```mermaid
sequenceDiagram
    participant Script as build_all.py
    participant EntryJS as .entryjs/blocks/*.js
    participant Output as JSON 파일

    Script->>EntryJS: block_*.js 파일 스캔
    EntryJS-->>Script: JavaScript 코드

    loop 각 블록 파일
        Script->>Script: 정규식으로 py: [...] 추출
        Script->>Script: Entry.function() 파싱
        Script->>Script: 블록 메타데이터 구성
    end
    
    Script->>Script: RAG 문서 생성 (39개)
    Script->>Output: entry_python_rag_docs.json 저장
```

## AWS Bedrock 임베딩 내부 프로세스

```mermaid
sequenceDiagram
    participant S3 as S3 문서
    participant DataSource as Bedrock Data Source
    participant Parser as Claude 3 Sonnet
    participant Chunker as 계층적 청킹
    participant Embedder as Titan Embed
    participant Vector as OpenSearch Vector

    Note over S3,Vector: Bedrock Knowledge Base 내부 처리
    
    DataSource->>S3: 문서 스캔 및 읽기
    S3-->>DataSource: 텍스트 문서 (39개)
    
    loop 각 문서
        DataSource->>Parser: 고급 파싱 요청
        Parser->>Parser: 마크다운 구조 분석
        Parser->>Parser: 코드 블록 식별
        Parser->>Parser: 메타데이터 추출
        Parser-->>DataSource: 구조화된 콘텐츠
        
        DataSource->>Chunker: 계층적 청킹 실행
        Chunker->>Chunker: Level 1: 1500 토큰 청크
        Chunker->>Chunker: Level 2: 300 토큰 청크
        Chunker->>Chunker: 60 토큰 오버랩 적용
        Chunker-->>DataSource: 청크 배열
        
        loop 각 청크
            DataSource->>Embedder: 임베딩 생성 요청
            Embedder->>Embedder: 1024차원 벡터 생성
            Embedder-->>DataSource: 임베딩 벡터
            
            DataSource->>Vector: 벡터 + 메타데이터 저장
            Vector-->>DataSource: 저장 완료
        end
    end
    
    DataSource-->>DataSource: 인덱싱 완료
```

## RAG 검색 시퀀스

```mermaid
sequenceDiagram
    participant User as 사용자
    participant Chatbot as Streamlit 챗봇
    participant BedrockRT as Bedrock Runtime
    participant KB as Knowledge Base
    participant Vector as Vector Search
    participant Claude as Claude 3.5 Sonnet

    User->>Chatbot: "Entry.is_mouse_clicked() 사용법?"
    Chatbot->>BedrockRT: retrieve_and_generate() 호출
    
    BedrockRT->>KB: 질문 분석 및 검색 요청
    KB->>Vector: 의미적 유사도 검색
    Vector->>Vector: 코사인 유사도 계산
    Vector-->>KB: 관련 문서 청크 반환
    
    KB->>KB: 컨텍스트 구성 및 랭킹
    KB-->>BedrockRT: 검색된 컨텍스트
    
    BedrockRT->>Claude: 컨텍스트 + 질문으로 답변 생성
    Claude->>Claude: Entry Python 전문 답변 생성
    Claude-->>BedrockRT: 구조화된 답변
    
    BedrockRT-->>Chatbot: 최종 답변
    Chatbot-->>User: "Entry.is_mouse_clicked()는..."
```

## 핵심 특징

### 1. 외부 의존성 관리
- EntryJS 오픈소스 저장소를 `.entryjs`에 클론
- 상대경로 `../../.entryjs`로 접근
- JavaScript 파일에서 Python 문법 추출

### 2. 정규식 기반 파싱
- `py: [...]` 패턴으로 Python 문법 블록 식별
- `'Entry.function()'` 형태의 함수 추출
- 파일명에서 카테고리 자동 추출

### 3. 계층적 문서 구조
- 카테고리별 가이드 문서 (14개)
- 개별 블록 참조 문서 (23개)
- 일반 가이드 및 FAQ (2개)

### 4. AWS 완전 관리형 RAG
- Bedrock Knowledge Base로 임베딩 자동화
- Claude 3 Sonnet 기반 고급 파싱
- OpenSearch Serverless 벡터 저장
- 통합 검색+생성 API 제공
