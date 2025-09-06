#!/bin/bash

# 기존 스택 삭제 스크립트
set -e

echo "=== 기존 스택 삭제 중 ==="

source aws_env.sh
cd cdk
source venv/bin/activate

cdk destroy --force

echo "기존 스택이 삭제되었습니다."