# Entry.js 텍스트 에디터 조작 가이드

## CodeMirror 에디터 접근

```javascript
// 메인 워크스페이스의 CodeMirror 에디터 접근
Entry.getMainWS().vimBoard.codeMirror
```

## 텍스트 가져오기

```javascript
// 전체 텍스트 가져오기
Entry.getMainWS().vimBoard.codeMirror.getValue()

// 특정 라인 텍스트 가져오기 (0부터 시작)
Entry.getMainWS().vimBoard.codeMirror.getLine(0)

// 선택된 텍스트 가져오기
Entry.getMainWS().vimBoard.codeMirror.getSelection()
```

## 텍스트 설정/수정

```javascript
// 전체 텍스트 교체
Entry.getMainWS().vimBoard.codeMirror.setValue("새로운 코드 내용")

// 현재 커서 위치에 텍스트 삽입
Entry.getMainWS().vimBoard.codeMirror.replaceSelection("삽입할 텍스트")

// 특정 라인 교체
Entry.getMainWS().vimBoard.codeMirror.replaceRange("새 텍스트", {line: 0, ch: 0}, {line: 0})

// 선택된 텍스트 교체
Entry.getMainWS().vimBoard.codeMirror.replaceSelection("교체할 텍스트")
```

## 커서 조작

```javascript
// 커서 위치 가져오기
Entry.getMainWS().vimBoard.codeMirror.getCursor()

// 커서 위치 설정
Entry.getMainWS().vimBoard.codeMirror.setCursor({line: 0, ch: 0})
```

## 유용한 메서드들

```javascript
// 라인 수 가져오기
Entry.getMainWS().vimBoard.codeMirror.lineCount()

// 특정 위치의 문자 가져오기
Entry.getMainWS().vimBoard.codeMirror.getRange({line: 0, ch: 0}, {line: 0, ch: 5})

// 에디터 포커스
Entry.getMainWS().vimBoard.codeMirror.focus()
```
