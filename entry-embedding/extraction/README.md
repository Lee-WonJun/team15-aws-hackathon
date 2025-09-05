# Build Script

Entry Python RAG 문서 빌드 스크립트

## 파일 설명

- `build_all.py`: 블록 추출 → JSON 생성 → 마크다운 변환을 한번에 처리

## 사용법

```bash
# 모든 문서 빌드 (JSON + 마크다운)
python build_all.py
```

## 출력

- `../entry_python_rag_docs.json`: RAG용 JSON 문서
- `../deploy/docs/*.md`: 배포용 마크다운 파일들