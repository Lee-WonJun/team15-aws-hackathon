#!/bin/bash

echo "=== AWS 설정 수정 ==="

# 현재 계정 확인
CURRENT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
echo "현재 AWS 계정: $CURRENT_ACCOUNT"

# .env 파일 수정
echo "AWS_ACCOUNT_ID=$CURRENT_ACCOUNT" > .env
echo "AWS_REGION=us-west-2" >> .env
echo "AWS_PROFILE=default" >> .env

echo "✅ .env 파일 업데이트 완료:"
cat .env

echo ""
echo "이제 ./deploy.sh 를 다시 실행하세요"