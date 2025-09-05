---
id: entry_python_guide
title: 엔트리 파이썬 기본 가이드
type: general_guide
category: unknown
---

# 엔트리 파이썬 기본 가이드

## 개요
엔트리 파이썬은 블록 코딩을 Python 텍스트 코딩으로 변환하여 사용할 수 있는 기능입니다.

## 기본 구조

### 이벤트 함수
```python
def when_start():
    # 시작하기 블록의 Python 코드
    pass

def when_press_key(key):
    # 키를 눌렀을 때 블록의 Python 코드
    pass

def when_click_mouse_on():
    # 마우스를 클릭했을 때 블록의 Python 코드
    pass
```

### 기본 명령어
- `Entry.move_to_direction(distance)`: 방향으로 이동
- `Entry.set_x(x)`: X 좌표 설정
- `Entry.set_y(y)`: Y 좌표 설정
- `Entry.show()`: 보이기
- `Entry.hide()`: 숨기기
- `Entry.print(text)`: 텍스트 출력

### 조건문과 반복문
```python
# 조건문
if Entry.is_mouse_clicked():
    Entry.show()

# 반복문
for i in range(10):
    Entry.move_to_direction(10)
```

## 매개변수 규칙
- `%1`, `%2`, `%3` 등은 블록의 입력값을 나타냅니다
- 블록에서 Python으로 변환할 때 실제 값으로 치환됩니다

## 주의사항
- 모든 Entry 함수는 `Entry.` 접두사를 사용합니다
- 이벤트 함수는 `def`로 시작하며 특정 이름 규칙을 따릅니다
- 들여쓰기는 Python 문법을 따라 4칸 공백을 사용합니다

