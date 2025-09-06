# EC2 Streamlit 챗봇 배포 가이드

## 사용 방법

### 1. EC2 인스턴스 생성 및 초기 설정
```bash
cd deploy-ec2
python3 ec2_deploy.py
```

### 2. 파일 업로드 및 서비스 시작
```bash
chmod +x upload_files.sh
./upload_files.sh <EC2_PUBLIC_IP>
```

## 생성되는 리소스

- **EC2 인스턴스**: t3.medium (Amazon Linux 2023)
- **보안 그룹**: 포트 22(SSH), 8000(Streamlit) 오픈
- **키페어**: hackathon-key.pem

## 접속 정보

- **웹 접속**: http://EC2_PUBLIC_IP:8000
- **SSH 접속**: `ssh -i hackathon-key.pem ec2-user@EC2_PUBLIC_IP`

## 서비스 관리

```bash
# 서비스 상태 확인
sudo systemctl status streamlit-chatbot

# 서비스 재시작
sudo systemctl restart streamlit-chatbot

# 로그 확인
sudo journalctl -u streamlit-chatbot -f
```

## 주의사항

- 키페어 파일(hackathon-key.pem)을 안전하게 보관하세요
- EC2 인스턴스 사용 후 종료하여 비용을 절약하세요
- 보안 그룹에서 필요한 IP만 허용하도록 설정하세요