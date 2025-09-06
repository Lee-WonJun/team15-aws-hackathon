#!/usr/bin/env python3
"""
EC2에 Streamlit 챗봇 배포 스크립트
"""
import boto3
import os
import sys
import time
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv('../.env')

# AWS 설정
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# EC2 설정
INSTANCE_TYPE = 't3.medium'
AMI_ID = 'ami-0c02fb55956c7d316'  # Amazon Linux 2023
KEY_NAME = 'hackathon-key'  # 키페어 이름 (생성 필요)
SECURITY_GROUP_NAME = 'streamlit-chatbot-sg'

def create_ec2_client():
    """EC2 클라이언트 생성"""
    return boto3.client(
        'ec2',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

def create_security_group(ec2):
    """보안 그룹 생성"""
    try:
        # 기존 보안 그룹 확인
        response = ec2.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': [SECURITY_GROUP_NAME]}]
        )
        
        if response['SecurityGroups']:
            sg_id = response['SecurityGroups'][0]['GroupId']
            print(f"기존 보안 그룹 사용: {sg_id}")
            return sg_id
        
        # 새 보안 그룹 생성
        response = ec2.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description='Streamlit Chatbot Security Group'
        )
        sg_id = response['GroupId']
        
        # 인바운드 규칙 추가
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8000,
                    'ToPort': 8000,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        
        print(f"보안 그룹 생성됨: {sg_id}")
        return sg_id
        
    except Exception as e:
        print(f"보안 그룹 생성 오류: {e}")
        return None

def create_key_pair(ec2):
    """키페어 생성"""
    try:
        # 기존 키페어 확인
        response = ec2.describe_key_pairs(KeyNames=[KEY_NAME])
        print(f"기존 키페어 사용: {KEY_NAME}")
        return True
    except:
        try:
            # 새 키페어 생성
            response = ec2.create_key_pair(KeyName=KEY_NAME)
            
            # 키 파일 저장
            with open(f'{KEY_NAME}.pem', 'w') as f:
                f.write(response['KeyMaterial'])
            
            os.chmod(f'{KEY_NAME}.pem', 0o400)
            print(f"키페어 생성됨: {KEY_NAME}.pem")
            return True
        except Exception as e:
            print(f"키페어 생성 오류: {e}")
            return False

def launch_instance(ec2, sg_id):
    """EC2 인스턴스 시작"""
    user_data = f"""#!/bin/bash
yum update -y
yum install -y python3 python3-pip git

# 프로젝트 클론 (실제로는 파일 복사 사용)
mkdir -p /home/ec2-user/chatbot
cd /home/ec2-user

# Python 패키지 설치
pip3 install streamlit boto3 python-dotenv

# 환경변수 설정
cat > /home/ec2-user/.env << 'EOF'
AWS_ACCOUNT_ID={os.getenv('AWS_ACCOUNT_ID')}
AWS_REGION={AWS_REGION}
AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
EOF

# 서비스 파일 생성
cat > /etc/systemd/system/streamlit-chatbot.service << 'EOF'
[Unit]
Description=Streamlit Chatbot
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/chatbot
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/local/bin/streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable streamlit-chatbot
"""

    try:
        response = ec2.run_instances(
            ImageId=AMI_ID,
            MinCount=1,
            MaxCount=1,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            SecurityGroupIds=[sg_id],
            UserData=user_data,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'Streamlit-Chatbot'},
                        {'Key': 'Project', 'Value': 'Entry-Python-RAG'}
                    ]
                }
            ]
        )
        
        instance_id = response['Instances'][0]['InstanceId']
        print(f"EC2 인스턴스 시작됨: {instance_id}")
        
        # 인스턴스 실행 대기
        print("인스턴스 시작 대기 중...")
        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])
        
        # 퍼블릭 IP 가져오기
        response = ec2.describe_instances(InstanceIds=[instance_id])
        public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        
        print(f"인스턴스 퍼블릭 IP: {public_ip}")
        return instance_id, public_ip
        
    except Exception as e:
        print(f"인스턴스 시작 오류: {e}")
        return None, None

def main():
    """메인 함수"""
    print("=== EC2에 Streamlit 챗봇 배포 ===")
    
    # EC2 클라이언트 생성
    ec2 = create_ec2_client()
    
    # 키페어 생성
    if not create_key_pair(ec2):
        print("키페어 생성 실패")
        return
    
    # 보안 그룹 생성
    sg_id = create_security_group(ec2)
    if not sg_id:
        print("보안 그룹 생성 실패")
        return
    
    # EC2 인스턴스 시작
    instance_id, public_ip = launch_instance(ec2, sg_id)
    if not instance_id:
        print("인스턴스 시작 실패")
        return
    
    print("\n=== 배포 완료 ===")
    print(f"인스턴스 ID: {instance_id}")
    print(f"퍼블릭 IP: {public_ip}")
    print(f"SSH 접속: ssh -i {KEY_NAME}.pem ec2-user@{public_ip}")
    print(f"웹 접속: http://{public_ip}:8000")
    print("\n파일 업로드를 위해 upload_files.sh 스크립트를 실행하세요.")

if __name__ == "__main__":
    main()