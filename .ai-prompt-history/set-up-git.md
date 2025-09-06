# Git 사용자 설정

## 문제
```
fatal: no email was given and auto-detection is disabled
```

## 해결 과정

1. **커밋 히스토리 확인**
   ```bash
   git log --oneline -10
   ```

2. **작성자 정보 추출**
   ```bash
   git show --format="%an <%ae>" e2264b8
   ```
   결과: `Lee-WonJun <dldnjs1013@gmail.com>`

3. **Git 사용자 정보 설정**
   ```bash
   git config user.name "Lee-WonJun"
   git config user.email "dldnjs1013@gmail.com"
   ```

## 결과
- Name: Lee-WonJun
- Email: dldnjs1013@gmail.com
- 커밋 시 이메일 오류 해결됨
