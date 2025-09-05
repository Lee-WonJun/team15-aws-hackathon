#!/bin/bash

echo "=== 단계별 배포 (간단 버전) ==="

# 환경변수 직접 설정
export AWS_ACCESS_KEY_ID=$(grep AWS_ACCESS_KEY_ID .env | cut -d'=' -f2)
export AWS_SECRET_ACCESS_KEY=$(grep AWS_SECRET_ACCESS_KEY .env | cut -d'=' -f2)
export AWS_ACCOUNT_ID=$(grep AWS_ACCOUNT_ID .env | cut -d'=' -f2)
export AWS_REGION=$(grep AWS_REGION .env | cut -d'=' -f2)

echo "Step 1: 인프라만 배포..."
cd cdk

# 간단한 앱 파일 생성
cat > simple_app.py << 'EOF'
#!/usr/bin/env python3
import aws_cdk as cdk
import sys, os
sys.path.append('..')
from step1_infrastructure import Step1InfrastructureStack

app = cdk.App()
Step1InfrastructureStack(app, "Step1Infrastructure",
    env=cdk.Environment(account=os.environ['AWS_ACCOUNT_ID'], region=os.environ['AWS_REGION'])
)
app.synth()
EOF

cdk deploy Step1Infrastructure --require-approval never --app "python3 simple_app.py"

echo "✅ Step 1 완료. 이제 수동으로:"
echo "1. 데이터 접근 정책 생성"
echo "2. 인덱스 생성" 
echo "3. Step 2 배포"