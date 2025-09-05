# Entry Python RAG 배포

## 필수 파일
- `.env` - AWS 자격증명
- `docs/` - 마크다운 문서들
- `cdk/` - CDK 스택 정의

## 배포 방법
```bash
./deploy_final.sh
```

## 구성 요소
1. **SimpleCompleteStack**: S3 + OpenSearch Serverless
2. **BedrockStack**: Knowledge Base + 자동 동기화
