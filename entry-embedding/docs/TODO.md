# 엔트리 파이썬 RAG 데이터 추출 TODO

## 1단계: 엔트리 구조 분석 및 이해
- [ ] **블록 정의 파일 분석**
  - [ ] `/src/playground/blocks/` 폴더의 모든 블록 정의 파일 분석
  - [ ] 각 블록의 Python 문법 매핑 (`syntax.py`) 추출
  - [ ] 블록 카테고리별 분류 (움직임, 생김새, 소리, 판단, 반복, 함수 등)

- [ ] **Python 파서 구조 분석**
  - [ ] `/src/textcoding/parser.js` - 블록↔Python 변환 로직 분석
  - [ ] `/src/textcoding/hint/python.js` - Python 자동완성 힌트 시스템 분석
  - [ ] `/src/textcoding/ast/pyAstGenerator.js` - Python AST 생성 로직 분석

- [ ] **블록-Python 매핑 관계 파악**
  - [ ] 각 블록의 `syntax.py` 속성에서 Python 코드 템플릿 추출
  - [ ] 매개변수 치환 규칙 분석 (`%1`, `%2` 등)
  - [ ] 조건문, 반복문 등 제어구조 블록의 Python 변환 규칙

## 2단계: 데이터 추출 스크립트 개발
- [ ] **블록 메타데이터 추출기**
  - [ ] 블록 타입, 카테고리, 설명 추출
  - [ ] Python 문법 템플릿 추출
  - [ ] 매개변수 정보 (타입, 기본값, 옵션) 추출

- [ ] **Python 코드 예제 생성기**
  - [ ] 각 블록의 기본 사용 예제 생성
  - [ ] 블록 조합 패턴 예제 생성
  - [ ] 실제 프로젝트에서 사용되는 코드 패턴 추출

- [ ] **문서화 데이터 추출**
  - [ ] 블록 설명, 도움말 텍스트 추출
  - [ ] 매개변수 설명 추출
  - [ ] 사용 예시 및 주의사항 추출

## 3단계: RAG용 데이터 구조화
- [ ] **블록 참조 문서 생성**
  - [ ] 각 블록별 상세 문서 (이름, 기능, Python 문법, 예제)
  - [ ] 카테고리별 블록 목록 및 사용법
  - [ ] 블록 간 연관관계 및 조합 패턴

- [ ] **Python 문법 가이드 생성**
  - [ ] 엔트리 Python 기본 문법 설명
  - [ ] 블록 코딩과 Python 코딩 비교
  - [ ] 자주 사용되는 패턴 및 베스트 프랙티스

- [ ] **FAQ 및 문제해결 가이드**
  - [ ] 자주 묻는 질문 및 답변
  - [ ] 일반적인 오류 및 해결방법
  - [ ] 블록에서 Python으로 변환 시 주의사항

## 4단계: 데이터 검증 및 정제
- [ ] **추출된 데이터 검증**
  - [ ] Python 문법 정확성 검증
  - [ ] 예제 코드 실행 가능성 확인
  - [ ] 문서 내용 일관성 검토

- [ ] **RAG 최적화**
  - [ ] 검색 친화적 키워드 추가
  - [ ] 문서 청킹 전략 수립
  - [ ] 임베딩 품질 향상을 위한 텍스트 정제

## 5단계: RAG 시스템 통합
- [ ] **벡터 데이터베이스 구축**
  - [ ] 추출된 문서들의 임베딩 생성
  - [ ] OpenSearch/Pinecone 등에 인덱싱
  - [ ] 검색 성능 최적화

- [ ] **RAG 파이프라인 구현**
  - [ ] 질문 분석 및 의도 파악
  - [ ] 관련 문서 검색 및 랭킹
  - [ ] 컨텍스트 기반 답변 생성

## 주요 추출 대상 파일들
```
.entryjs/entryjs/src/playground/blocks/
├── block_*.js (모든 블록 정의 파일)
├── hardware/ (하드웨어 블록들)
└── index.js (블록 인덱스)

.entryjs/entryjs/src/textcoding/
├── parser.js (Python 파서)
├── hint/python.js (자동완성)
└── ast/pyAstGenerator.js (AST 생성)
```

## 예상 RAG 데이터 구조
```json
{
  "block_id": "move_direction",
  "category": "moving",
  "name": "방향으로 이동하기",
  "description": "스프라이트를 지정한 방향으로 이동시킵니다",
  "python_syntax": "Entry.move_direction(%1, %2)",
  "parameters": [
    {"name": "direction", "type": "angle", "description": "이동할 방향"},
    {"name": "distance", "type": "number", "description": "이동할 거리"}
  ],
  "examples": [
    "Entry.move_direction(90, 100)  # 오른쪽으로 100만큼 이동",
    "Entry.move_direction(0, 50)   # 위쪽으로 50만큼 이동"
  ],
  "related_blocks": ["move_x", "move_y", "move_xy"],
  "common_patterns": ["반복문과 함께 사용", "조건문으로 방향 제어"]
}
```