#!/bin/bash

echo "=== Entry Python RAG 배포 스크립트 ==="

# .env 파일에서 환경변수 로드
if [ -f .env ]; then
    set -a  # 자동으로 export
    source .env
    set +a
    # 명시적으로 export
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_ACCOUNT_ID
    export AWS_REGION
    echo "✅ .env 파일 로드됨"
    echo "AWS 계정: $AWS_ACCOUNT_ID"
    echo "AWS 리전: $AWS_REGION"
else
    echo "❌ .env 파일이 없습니다"
    exit 1
fi


# 문서 빌드 (JSON + 마크다운)
echo "문서 빌드 중..."
cd ../extraction
python build_all.py
cd ../deploy

# CDK 디렉토리로 이동
cd cdk

# 의존성 설치 (시스템 전역)
pip3 install --user -r requirements.txt

# CDK CLI 설치 (npm)
if ! command -v cdk &> /dev/null; then
    echo "CDK CLI 설치 중..."
    npm install -g aws-cdk
fi

# 임시 AWS 자격증명 파일 생성
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
EOF

cat > ~/.aws/config << EOF
[default]
region = $AWS_REGION
EOF

# CDK 부트스트랩 (최초 1회만)
echo "CDK 부트스트랩 실행..."
cdk bootstrap aws://$AWS_ACCOUNT_ID/$AWS_REGION

# CDK 배포
echo "CDK 스택 배포 중..."
cdk deploy --require-approval never

# 출력값 저장
echo "배포 완료! 출력값을 확인하세요:"
aws cloudformation describe-stacks --stack-name EntryRagStack --query 'Stacks[0].Outputs'

echo ""
echo "다음 단계:"
echo "1. Bedrock 콘솔에서 Knowledge Base를 Sync하세요"
echo "   - AWS 콘솔 → Bedrock → Knowledge bases"
echo "   - Data source → Sync 버튼 클릭"