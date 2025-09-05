---
id: block_check_weather
title: 엔트리 파이썬 블록: check_weather
type: block_reference
category: weather_legacy
---

# check_weather 블록

**카테고리:** weather_legacy

**Python 문법:**
```python
Legacy.Weather.is_condition_sunny(%1, %2)
```

## 매개변수

- **DATE** (위치 0): 블록의 1번째 입력값
- **LOCATION** (위치 1): 블록의 2번째 입력값

## 사용 예시

```python
result = Legacy.Weather.is_condition_sunny(%1, %2)
Entry.print(result)
```

## 관련 정보

- 이 블록은 weather_legacy 카테고리에 속합니다
- 원본 파일: block_expansion_weather.js

