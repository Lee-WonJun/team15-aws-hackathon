#!/bin/bash

# Entry MCP CDK 배포 스크립트
set -e

echo "=== Entry MCP CDK 배포 시작 ==="

# AWS 환경변수 설정
source aws_env.sh

echo "AWS 환경변수 설정 완료:"
echo "- Region: $AWS_DEFAULT_REGION"
echo "- Access Key: ${AWS_ACCESS_KEY_ID:0:10}..."

# CDK 디렉토리로 이동
cd cdk

# 가상환경 생성 (없는 경우)
if [ ! -d "venv" ]; then
    echo "Python 3.11 가상환경 생성 중..."
    python3.11 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
echo "의존성 설치 중..."
pip install -r requirements.txt

# CDK 부트스트랩 (처음 한 번만 필요)
echo "CDK 부트스트랩 확인 중..."
cdk bootstrap

# CDK 배포
echo "CDK 배포 시작..."
cdk deploy --require-approval never

echo "=== Entry MCP 배포 완료 ==="