# 핵심 학습 사항 및 베스트 프랙티스

## 🔑 핵심 원칙

### AWS 자격 증명 관리
```
❗ 중요: AWS 관련 정보는 aws_config/config.py 코드를 이용해 가져오기
- 하드코딩 절대 금지
- 환경변수 직접 사용 대신 기존 설정 모듈 재사용
- get_bedrock_client(), get_bedrock_agent_runtime_client() 등 활용
```

## 🛠️ 기술적 해결책

### 1. EC2 User Data 최적화
```bash
#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1  # 로깅 활성화

# 가상환경 사용으로 패키지 충돌 방지
python3 -m venv streamlit-env
source streamlit-env/bin/activate
pip install streamlit boto3 python-dotenv

# 소유권 설정
chown -R ec2-user:ec2-user /home/ec2-user/chatbot

# nohup으로 백그라운드 실행
sudo -u ec2-user bash -c 'cd /home/ec2-user/chatbot && source streamlit-env/bin/activate && nohup streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0 > streamlit.log 2>&1 &'
```

### 2. CDK 구조 단순화
- S3 업로드 대신 User Data에서 직접 파일 생성
- 복잡한 의존성 제거
- 매개변수를 통한 설정 전달

### 3. Knowledge Base 연동
```python
class BedrockChatbot:
    def __init__(self):
        self.knowledge_base_id = "9R38KN62YH"  # 정확한 ID 사용
        self.bedrock_client = get_bedrock_client()
        self.agent_runtime_client = get_bedrock_agent_runtime_client()
```

## 🐛 주요 트러블슈팅

### 문제 1: pip 패키지 충돌
**증상**: `ERROR: Cannot uninstall requests 2.25.1, RECORD file not found`
**해결**: 가상환경 사용으로 시스템 패키지와 격리

### 문제 2: 파일 누락
**증상**: `streamlit_app.py` 파일이 EC2에 업로드되지 않음
**해결**: S3 업로드 대신 User Data에서 직접 파일 생성

### 문제 3: User Data 실행 실패
**증상**: 새로운 User Data가 실행되지 않음
**해결**: 인스턴스 재생성 또는 재부팅 필요

### 문제 4: 권한 문제
**증상**: ec2-user 권한으로 실행되지 않음
**해결**: `chown -R ec2-user:ec2-user` + `sudo -u ec2-user` 사용

## 📋 체크리스트

### 배포 전 확인사항
- [ ] Knowledge Base ID 정확성 확인
- [ ] aws_config 모듈에서 자격 증명 가져오는지 확인
- [ ] 모든 필요 파일이 User Data에 포함되었는지 확인
- [ ] 가상환경 설정이 올바른지 확인

### 배포 후 확인사항
- [ ] `sudo cat /var/log/user-data.log` 로그 확인
- [ ] `ps aux | grep streamlit` 프로세스 확인
- [ ] `ss -tlnp | grep :8000` 포트 확인
- [ ] `curl localhost:8000` 로컬 접속 확인

## 🚀 성공 요인

1. **단계별 접근**: 문제를 작은 단위로 나누어 해결
2. **로깅 활용**: User Data 로그를 통한 디버깅
3. **단순한 구조**: 복잡한 의존성 제거
4. **기존 모듈 재사용**: aws_config 활용
5. **가상환경 격리**: 패키지 충돌 방지

## 🔄 개선 가능한 부분

1. **Health Check**: Streamlit 서비스 상태 모니터링
2. **Auto Scaling**: 트래픽에 따른 자동 확장
3. **HTTPS**: SSL 인증서 적용
4. **도메인**: Route 53을 통한 도메인 연결
5. **로그 관리**: CloudWatch Logs 연동

## 📚 참고 명령어

### 디버깅
```bash
# User Data 로그 확인
sudo cat /var/log/user-data.log

# 실시간 로그 확인
sudo tail -f /var/log/user-data.log

# Streamlit 로그 확인
tail -f /home/ec2-user/chatbot/streamlit.log

# 프로세스 상태 확인
ps aux | grep streamlit
ss -tlnp | grep :8000
```

### 수동 실행
```bash
cd /home/ec2-user/chatbot
python3 -m venv streamlit-env
source streamlit-env/bin/activate
pip install streamlit boto3 python-dotenv
nohup streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```