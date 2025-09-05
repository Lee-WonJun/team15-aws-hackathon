# .env 파일 설정 방법

AWS 프로필 없이 .env 파일에 직접 자격증명을 설정하세요.

## .env 파일 예시

```bash
AWS_ACCOUNT_ID=339712825274
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

## 자격증명 얻는 방법

1. **AWS 콘솔** → IAM → Users → 본인 계정 → Security credentials
2. **Access keys** → Create access key
3. 생성된 Access Key ID와 Secret Access Key를 .env에 입력

## 배포

```bash
# .env 파일 편집 후
./deploy.sh
```