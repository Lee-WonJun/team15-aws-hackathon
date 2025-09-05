# Entry Studio API

엔트리 스튜디오 웹 자동화를 위한 FastAPI 서버

## 실행 방법

```bash
./run.sh
```

## API 엔드포인트

### GET /editor/code
현재 에디터의 코드를 가져옵니다.

```bash
curl http://localhost:8000/editor/code
```

### PUT /editor/code
에디터의 코드를 설정합니다.

```bash
curl -X PUT http://localhost:8000/editor/code \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello Entry!\")"}'
```

### POST /editor/insert
현재 커서 위치에 코드를 삽입합니다.

```bash
curl -X POST http://localhost:8000/editor/insert \
  -H "Content-Type: application/json" \
  -d '{"code": "# 새로운 코드"}'
```

### GET /editor/cursor
현재 커서 위치를 가져옵니다.

```bash
curl http://localhost:8000/editor/cursor
```

### POST /editor/focus
에디터에 포커스를 설정합니다.

```bash
curl -X POST http://localhost:8000/editor/focus
```

## 주의사항

- Chrome 브라우저가 설치되어 있어야 합니다
- ChromeDriver가 PATH에 있어야 합니다
- 서버 실행 시 자동으로 Entry Studio가 열립니다