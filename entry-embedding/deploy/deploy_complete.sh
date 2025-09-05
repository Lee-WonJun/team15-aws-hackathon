#!/bin/bash

echo "=== 완전 자동화 Entry Python RAG 배포 ===" 

# .env 파일 로드
if [ -f .env ]; then
    set -a
    source .env
    set +a
    export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_ACCOUNT_ID AWS_REGION
    echo "✅ .env 파일 로드됨 (계정: $AWS_ACCOUNT_ID, 리전: $AWS_REGION)"
else
    echo "❌ .env 파일이 없습니다"
    exit 1
fi

# 문서 빌드
echo "📄 문서 빌드 중..."
cd ../extraction && python build_all.py && cd ../deploy

# CDK 준비
cd cdk
pip3 install -r requirements.txt

if ! command -v cdk &> /dev/null; then
    echo "📦 CDK CLI 설치 중..."
    npm install -g aws-cdk
fi

# 부트스트랩
echo "🚀 CDK 부트스트랩..."
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION

# 완전 자동화 배포 (Knowledge Base 동기화 포함)
echo "🔄 완전 자동화 배포 시작..."
cdk deploy CompleteEntryRagStack --app "python3 app_complete.py" --require-approval never

if [ $? -eq 0 ]; then
    echo "✅ 배포 완료! Knowledge Base 동기화도 자동으로 완료되었습니다."
    echo ""
    echo "📊 배포된 리소스:"
    aws cloudformation describe-stacks --stack-name CompleteEntryRagStack --query 'Stacks[0].Outputs' 2>/dev/null || echo "스택 정보 조회 실패"
    echo ""
    echo "🎉 이제 Bedrock 콘솔에서 바로 테스트할 수 있습니다!"
else
    echo "❌ 배포 실패"
    exit 1
fi