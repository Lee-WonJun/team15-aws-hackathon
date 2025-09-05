# Deploy Scripts

AWS Bedrock Knowledge Base 배포를 위한 스크립트들

## 파일 설명

- `deploy.sh`: 메인 배포 스크립트
- `.env`: AWS 계정 정보 (git에서 제외됨)
- `cdk/`: CDK 인프라 코드
- `scripts/`: 문서 처리 스크립트

## 사용법

cdk 배포를 위해 `.env` 파일을 생성하고, AWS 자격 증명을 설정합니다:
```
[Hackathon]
aws_access_key_id = <YOUR_AWS_ACCESS>
aws_secret_access_key = <YOUR_AWS_SECRET>

```


```bash
# 환경 설정
cp .env.example .env
# .env 편집

# 배포
./deploy.sh
```