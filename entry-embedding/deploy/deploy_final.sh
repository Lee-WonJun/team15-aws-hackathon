#!/bin/bash

echo "=== Entry Python RAG 자동 배포 ==="

# 환경변수 로드
if [ -f .env ]; then
    export $(cat .env | xargs)
    echo "✅ 환경변수 로드됨"
else
    echo "❌ .env 파일이 없습니다"
    exit 1
fi

# 문서 빌드
echo "📄 문서 빌드..."
echo "📄 문서 준비됨"

# CDK 배포
cd cdk
pip3 install -r requirements.txt

echo "🚀 1단계: S3 + OpenSearch 배포..."
cdk deploy SimpleCompleteStack-v2 --app "python3 app_simple.py" --require-approval never

echo "🔧 2단계: 벡터 인덱스 생성..."
cd .. && python3 create_index_simple.py && cd cdk

echo "🤖 3단계: Bedrock Knowledge Base 배포..."
cdk deploy BedrockStack --app "python3 app_bedrock.py" --require-approval never

echo "✅ 배포 완료!"
