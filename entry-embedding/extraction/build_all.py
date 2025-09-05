#!/usr/bin/env python3
"""
Entry Python RAG 문서 빌드 스크립트
블록 추출 → JSON 생성 → 마크다운 변환을 한번에 처리
"""
import json
import os
import re
from pathlib import Path

def extract_blocks_from_js(js_file_path):
    """JavaScript 파일에서 블록 정보 추출"""
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = []
    
    # Entry.block 패턴 찾기
    block_pattern = r'Entry\.block\s*=\s*\{(.*?)\};'
    matches = re.findall(block_pattern, content, re.DOTALL)
    
    for match in matches:
        # 블록 ID 추출
        id_match = re.search(r'["\']([^"\']+)["\']', match)
        if not id_match:
            continue
            
        block_id = id_match.group(1)
        
        # Python 문법 추출
        python_syntax = []
        syntax_patterns = [
            r'Entry\.([a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)',
            r'Legacy\.([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\)',
            r'\b(break|continue|name)\b'
        ]
        
        for pattern in syntax_patterns:
            syntax_matches = re.findall(pattern, match)
            for syntax in syntax_matches:
                if isinstance(syntax, tuple):
                    syntax = syntax[0] if syntax[0] else syntax[1]
                python_syntax.append(f"Entry.{syntax}()" if not syntax.startswith(('Legacy', 'break', 'continue', 'name')) else syntax)
        
        if not python_syntax:
            python_syntax = ["Entry.unknown()"]
        
        # 카테고리 추정
        category = "unknown"
        if "mouse" in block_id or "key" in block_id or "boost" in block_id:
            category = "boolean_input"
        elif "weather" in block_id:
            category = "weather_legacy"
        elif "show" in block_id or "hide" in block_id:
            category = "visibility"
        elif "sound" in block_id:
            category = "sound_volume" if "volume" in block_id else "bgm"
        elif "repeat" in block_id:
            category = "repeat"
        elif "effect" in block_id:
            category = "effect"
        elif "flip" in block_id:
            category = "flip"
        elif "stamp" in block_id:
            category = "stamp"
        elif "brush" in block_id:
            category = "brush_clear"
        elif "user" in block_id or "nickname" in block_id:
            category = "calc_user"
        elif "touch" in block_id:
            category = "boolean_device"
        
        blocks.append({
            "block_id": block_id,
            "category": category,
            "python_syntax": python_syntax,
            "parameters": [],
            "file": os.path.basename(js_file_path)
        })
    
    return blocks

def generate_rag_docs(blocks):
    """블록 데이터로부터 RAG 문서 생성"""
    docs = []
    
    # 카테고리별 그룹화
    categories = {}
    for block in blocks:
        cat = block['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(block)
    
    # 카테고리별 가이드 생성
    for category, cat_blocks in categories.items():
        content = f"# {category} 카테고리 블록들\n\n"
        
        for block in cat_blocks:
            content += f"## {block['block_id']}\n"
            content += f"**Python 문법:** `{block['python_syntax'][0]}`\n\n"
            
            if block['parameters']:
                content += "**매개변수:**\n"
                for param in block['parameters']:
                    content += f"- {param['name']}: 위치 {param['index']}\n"
                content += "\n"
            
            content += "**사용 예시:**\n"
            content += f"```python\n{block['python_syntax'][0]}\n```\n\n"
        
        docs.append({
            "id": f"category_{category}",
            "title": f"엔트리 파이썬 - {category} 카테고리",
            "content": content,
            "type": "category_guide",
            "category": category,
            "blocks": cat_blocks
        })
    
    # 개별 블록 문서 생성
    for block in blocks:
        content = f"# {block['block_id']} 블록\n\n"
        content += f"**카테고리:** {block['category']}\n\n"
        content += f"**Python 문법:**\n```python\n{block['python_syntax'][0]}\n```\n\n"
        
        if block['parameters']:
            content += "## 매개변수\n\n"
            for param in block['parameters']:
                content += f"- **{param['name']}** (위치 {param['index']}): 블록의 {param['index']+1}번째 입력값\n"
            content += "\n"
        
        content += "## 사용 예시\n\n"
        if block['category'] == 'boolean_input':
            content += f"```python\nif {block['python_syntax'][0]}:\n    Entry.print('조건이 참입니다')\n```\n\n"
        elif block['category'] in ['visibility', 'effect', 'flip']:
            content += f"```python\n{block['python_syntax'][0]}\n```\n\n"
        else:
            content += f"```python\nresult = {block['python_syntax'][0]}\nEntry.print(result)\n```\n\n"
        
        content += "## 관련 정보\n\n"
        content += f"- 이 블록은 {block['category']} 카테고리에 속합니다\n"
        content += f"- 원본 파일: {block['file']}\n"
        
        docs.append({
            "id": f"block_{block['block_id']}",
            "title": f"엔트리 파이썬 블록: {block['block_id']}",
            "content": content,
            "type": "block_reference",
            "block_id": block['block_id'],
            "category": block['category'],
            "python_syntax": block['python_syntax'],
            "parameters": block['parameters']
        })
    
    # 기본 가이드 추가
    docs.extend([
        {
            "id": "entry_python_guide",
            "title": "엔트리 파이썬 기본 가이드",
            "content": """# 엔트리 파이썬 기본 가이드

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
""",
            "type": "general_guide"
        },
        {
            "id": "entry_python_faq",
            "title": "엔트리 파이썬 자주 묻는 질문",
            "content": """# 엔트리 파이썬 FAQ

## Q: 블록 코딩과 Python 코딩의 차이점은 무엇인가요?
A: 블록 코딩은 시각적인 블록을 조합하여 프로그래밍하는 방식이고, Python 코딩은 텍스트로 직접 코드를 작성하는 방식입니다. 엔트리에서는 블록을 Python 코드로 자동 변환할 수 있습니다.

## Q: Entry.move_to_direction()과 같은 함수는 어디서 확인할 수 있나요?
A: 엔트리 워크스페이스에서 블록을 Python 모드로 전환하면 해당하는 Python 함수를 확인할 수 있습니다.

## Q: 매개변수 %1, %2는 무엇을 의미하나요?
A: 블록의 입력 필드 순서를 나타냅니다. %1은 첫 번째 입력값, %2는 두 번째 입력값을 의미합니다.

## Q: Python 코드에서 오류가 발생했을 때 어떻게 해결하나요?
A: 
1. 문법 오류: 들여쓰기, 괄호, 따옴표 등을 확인하세요
2. 함수 오류: Entry. 접두사가 올바른지 확인하세요
3. 매개변수 오류: 함수에 필요한 매개변수가 모두 제공되었는지 확인하세요

## Q: 어떤 블록들이 Python으로 변환 가능한가요?
A: 대부분의 엔트리 블록이 Python으로 변환 가능합니다. 움직임, 생김새, 소리, 판단, 반복, 변수 등 모든 카테고리의 블록을 지원합니다.

## Q: Python 코드를 직접 작성할 때 주의할 점은?
A: 
- Entry 함수는 반드시 `Entry.` 접두사를 사용하세요
- 이벤트 함수는 정확한 이름을 사용하세요 (예: `def when_start():`)
- Python 문법 규칙을 준수하세요 (들여쓰기, 콜론 등)
""",
            "type": "faq"
        }
    ])
    
    return docs

def convert_to_markdown(docs, output_dir):
    """JSON 문서를 마크다운 파일로 변환"""
    os.makedirs(output_dir, exist_ok=True)
    
    for doc in docs:
        filename = f"{doc['id']}.md"
        filepath = os.path.join(output_dir, filename)
        
        content = f"""---
id: {doc['id']}
title: {doc['title']}
type: {doc['type']}
category: {doc.get('category', 'unknown')}
---

{doc['content']}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    """메인 실행 함수"""
    print("=== Entry Python RAG 문서 빌드 ===")
    
    # 1. 블록 추출 (샘플 데이터 생성)
    print("1. 블록 데이터 생성 중...")
    sample_blocks = [
        {"block_id": "is_clicked", "category": "boolean_input", "python_syntax": ["Entry.is_mouse_clicked()"], "parameters": [], "file": "block_judgement.js"},
        {"block_id": "is_press_some_key", "category": "boolean_input", "python_syntax": ["Entry.is_key_pressed(%1)"], "parameters": [{"name": "VALUE", "index": 0}], "file": "block_judgement.js"},
        {"block_id": "show", "category": "visibility", "python_syntax": ["Entry.show()"], "parameters": [], "file": "block_looks.js"},
        {"block_id": "hide", "category": "visibility", "python_syntax": ["Entry.hide()"], "parameters": [], "file": "block_looks.js"},
        {"block_id": "check_weather", "category": "weather_legacy", "python_syntax": ["Legacy.Weather.is_condition_sunny(%1, %2)"], "parameters": [{"name": "DATE", "index": 0}, {"name": "LOCATION", "index": 1}], "file": "block_expansion_weather.js"}
    ]
    
    # 2. RAG 문서 생성
    print("2. RAG 문서 생성 중...")
    docs = generate_rag_docs(sample_blocks)
    
    # 3. JSON 저장
    json_output = "../entry_python_rag_docs.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"   → {json_output} 생성 완료")
    
    # 4. 마크다운 변환
    print("3. 마크다운 파일 생성 중...")
    md_output_dir = "../deploy/docs"
    convert_to_markdown(docs, md_output_dir)
    print(f"   → {md_output_dir}/ 에 {len(docs)}개 파일 생성 완료")
    
    print("\n=== 빌드 완료 ===")
    print(f"- JSON: {json_output}")
    print(f"- 마크다운: {md_output_dir}/")
    print(f"- 총 {len(docs)}개 문서 생성")

if __name__ == "__main__":
    main()