#!/bin/bash

# 파일 업로드 스크립트
set -e

# 설정
KEY_FILE="hackathon-key.pem"
EC2_USER="ec2-user"

# EC2 IP 입력 받기
if [ -z "$1" ]; then
    echo "사용법: $0 <EC2_PUBLIC_IP>"
    echo "예시: $0 3.34.123.456"
    exit 1
fi

EC2_HOST=$1

echo "=== 파일 업로드 시작 ==="
echo "EC2 Host: $EC2_HOST"

# 키 파일 권한 설정
chmod 400 $KEY_FILE

# 필요한 디렉토리 생성
ssh -i $KEY_FILE $EC2_USER@$EC2_HOST "mkdir -p /home/ec2-user/chatbot/aws_config"

# 챗봇 파일들 업로드
echo "챗봇 파일 업로드 중..."
scp -i $KEY_FILE ../chatbot/streamlit_app.py $EC2_USER@$EC2_HOST:/home/ec2-user/chatbot/
scp -i $KEY_FILE ../chatbot/bedrock_client.py $EC2_USER@$EC2_HOST:/home/ec2-user/chatbot/

# AWS 설정 파일 업로드
echo "AWS 설정 파일 업로드 중..."
scp -i $KEY_FILE ../aws_config/config.py $EC2_USER@$EC2_HOST:/home/ec2-user/chatbot/aws_config/
scp -i $KEY_FILE ../aws_config/__init__.py $EC2_USER@$EC2_HOST:/home/ec2-user/chatbot/aws_config/

# 환경 파일 업로드
echo "환경 파일 업로드 중..."
scp -i $KEY_FILE ../.env $EC2_USER@$EC2_HOST:/home/ec2-user/chatbot/

# 서비스 시작
echo "Streamlit 서비스 시작 중..."
ssh -i $KEY_FILE $EC2_USER@$EC2_HOST "
    cd /home/ec2-user/chatbot
    sudo systemctl start streamlit-chatbot
    sudo systemctl status streamlit-chatbot
"

echo ""
echo "=== 배포 완료 ==="
echo "웹 브라우저에서 http://$EC2_HOST:8000 접속하세요"
echo ""
echo "서비스 상태 확인: ssh -i $KEY_FILE $EC2_USER@$EC2_HOST 'sudo systemctl status streamlit-chatbot'"
echo "로그 확인: ssh -i $KEY_FILE $EC2_USER@$EC2_HOST 'sudo journalctl -u streamlit-chatbot -f'"