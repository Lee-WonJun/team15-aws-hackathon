#!/bin/bash

echo "=== Entry Python RAG 단계별 배포 ==="

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
    echo "AWS 계정: $AWS_ACCOUNT_ID"
    echo "AWS 리전: $AWS_REGION"
else
    echo "❌ .env 파일이 없습니다"
    exit 1
fi

# 문서 빌드
echo "문서 빌드 중..."
cd ../extraction
python3 build_all.py
cd ../deploy/cdk

# 의존성 설치
pip3 install --user -r requirements.txt

# 1단계: OpenSearch 컬렉션만 배포
echo "1단계: OpenSearch 컬렉션 배포 중..."
PYTHONPATH=/home/dldnjs1013/.local/lib/python3.8/site-packages:/usr/lib/python3/dist-packages python3 app_phase1.py > /tmp/cdk_synth.json
cdk deploy EntryRagStackPhase1 --require-approval never --app "python3 app_phase1.py"

if [ $? -ne 0 ]; then
    echo "❌ 1단계 배포 실패!"
    exit 1
fi

echo "✅ 1단계 완료"

# 2단계: 인덱스 생성
echo "2단계: OpenSearch 인덱스 생성 중..."
cd ..
python3 create_index.py

if [ $? -ne 0 ]; then
    echo "❌ 인덱스 생성 실패!"
    exit 1
fi

echo "✅ 2단계 완료"

# 3단계: Knowledge Base 배포
echo "3단계: Knowledge Base 배포 중..."
cd cdk
cdk deploy EntryRagStack --require-approval never

if [ $? -eq 0 ]; then
    echo "✅ 배포 완료!"
    aws cloudformation describe-stacks --stack-name EntryRagStack --query 'Stacks[0].Outputs' 2>/dev/null || echo "null"
else
    echo "❌ 3단계 배포 실패!"
    exit 1
fi

echo ""
echo "다음 단계:"
echo "1. Bedrock 콘솔에서 Knowledge Base를 Sync하세요"
echo "   - AWS 콘솔 → Bedrock → Knowledge bases"
echo "   - Data source → Sync 버튼 클릭"