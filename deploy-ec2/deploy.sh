#!/bin/bash

# CDK로 Streamlit 챗봇 배포 스크립트
set -e

echo "=== CDK Streamlit 챗봇 배포 시작 ==="

# AWS 자격 증명 설정
echo "AWS 자격 증명 설정 중..."
python3 setup_aws_env.py
source aws_env.sh

# CDK 디렉토리로 이동
cd cdk

# Python 가상환경 생성 및 활성화
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# CDK 패키지 설치
pip install -r requirements.txt

# CDK 부트스트랩 (처음 한 번만 필요)
echo "CDK 부트스트랩 확인 중..."
cdk bootstrap

# CDK 배포
echo "CDK 스택 배포 중..."
cdk deploy --require-approval never

echo ""
echo "=== 배포 완료 ==="
echo "몇 분 후 Streamlit 앱이 시작됩니다."
echo "배포 상태는 AWS 콘솔에서 확인하세요."