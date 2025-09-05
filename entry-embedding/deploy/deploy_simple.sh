#!/bin/bash

echo "=== Entry Python RAG 간단 배포 ==="

# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    set -a
    source .env
    set +a
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_ACCOUNT_ID
    export AWS_REGION
    echo "✅ .env 파일 로드됨"
else
    echo "❌ .env 파일이 없습니다"
    exit 1
fi

# 기존 Phase1 스택 삭제
echo "기존 Phase1 스택 삭제 중..."
cd cdk
cdk destroy EntryRagStackPhase1 --force --app "python3 app_phase1.py" || true

# 메인 스택 배포
echo "메인 스택 배포 중..."
cdk deploy EntryRagStack --require-approval never

if [ $? -eq 0 ]; then
    echo "✅ 배포 완료!"
    aws cloudformation describe-stacks --stack-name EntryRagStack --query 'Stacks[0].Outputs' 2>/dev/null || echo "null"
else
    echo "❌ 배포 실패!"
    exit 1
fi

echo ""
echo "다음 단계:"
echo "1. Bedrock 콘솔에서 Knowledge Base를 Sync하세요"
echo "   - AWS 콘솔 → Bedrock → Knowledge bases"
echo "   - Data source → Sync 버튼 클릭"