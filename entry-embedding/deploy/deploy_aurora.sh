#!/bin/bash

echo "=== Aurora Serverless RAG 배포 ==="

# 환경변수 설정
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export AWS_ACCOUNT_ID=339712825274
export AWS_REGION=us-east-1

# 기존 스택들 정리
echo "기존 스택 정리 중..."
cd cdk
cdk destroy Step1Infrastructure --force || true

# Aurora 스택 배포
echo "Aurora RAG 스택 배포 중..."
cat > app_aurora.py << 'EOF'
#!/usr/bin/env python3
import aws_cdk as cdk
import sys, os
sys.path.append('..')
from aurora_stack import AuroraRagStack

app = cdk.App()
AuroraRagStack(app, "AuroraRagStack",
    env=cdk.Environment(account="339712825274", region="us-east-1")
)
app.synth()
EOF

cdk deploy AuroraRagStack --require-approval never --app "python3 app_aurora.py"

if [ $? -eq 0 ]; then
    echo "✅ Aurora RAG 배포 완료!"
    echo ""
    echo "다음 단계:"
    echo "1. Aurora 클러스터에 pgvector 확장 설치"
    echo "2. Bedrock 콘솔에서 Knowledge Base Sync"
else
    echo "❌ 배포 실패"
    exit 1
fi