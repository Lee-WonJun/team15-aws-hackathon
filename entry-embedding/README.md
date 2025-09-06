# Entry Python RAG Embedding

엔트리 파이썬 문서를 AWS Bedrock Knowledge Base로 임베딩하는 프로젝트

## 🔧 사전 준비사항 (중요!)

### EntryJS 소스코드 설정
이 프로젝트는 **EntryJS 오픈소스 저장소**에 의존합니다. 데이터 추출 전에 반드시 EntryJS를 클론해야 합니다.

```bash
# 프로젝트 루트에서 EntryJS 클론 (필수!)
cd /home/dldnjs1013/projects/team15-aws-hackathon
git clone https://github.com/entrylabs/entryjs.git .entryjs

# 예상 디렉토리 구조
team15-aws-hackathon/
├── .entryjs/                    # EntryJS 소스코드 (외부 의존성)
│   └── entryjs/
│       └── src/
│           └── playground/
│               └── blocks/      # 블록 정의 JavaScript 파일들
│                   ├── block_boolean_input.js
│                   ├── block_moving.js
│                   ├── block_sound.js
│                   └── ... (기타 블록 파일들)
└── entry-embedding/
    └── extraction/
        └── build_all.py         # 이 스크립트가 .entryjs를 참조
```

## 📊 데이터 추출 프로세스 상세

### 1단계: EntryJS 블록 파일 분석
```python
# extraction/build_all.py의 핵심 로직
def extract_blocks_from_entryjs():
    # EntryJS 블록 정의 파일들이 있는 디렉토리
    blocks_dir = Path("../../.entryjs/entryjs/src/playground/blocks")
    
    # block_*.js 패턴의 모든 파일 스캔
    for js_file in blocks_dir.glob("block_*.js"):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # JavaScript 파일에서 Python 문법 추출
        # 패턴: py: ['Entry.function_name()', 'break', ...]
        py_patterns = re.findall(r"py:\s*\[(.*?)\]", content, re.DOTALL)
```

### 2단계: Python 문법 패턴 추출
```python
# JavaScript 블록 정의 예시:
# block_boolean_input.js 내부
"""
Entry.block = {
    is_mouse_clicked: {
        color: EntryStatic.colorSet.block.default.JUDGEMENT,
        outerLine: EntryStatic.colorSet.block.darken.JUDGEMENT,
        skeleton: 'basic_boolean_field',
        statements: [],
        params: [],
        events: {},
        def: {
            params: [],
            type: 'is_mouse_clicked'
        },
        pyHelpDef: {
            params: [],
            type: 'is_mouse_clicked'
        },
        syntax: {
            js: [],
            py: ['Entry.is_mouse_clicked()']  # ← 이 부분을 추출!
        }
    }
}
"""

# 정규식으로 추출하는 부분
for py_content in py_patterns:
    # 'Entry.함수명()' 패턴 찾기
    entry_funcs = re.findall(r"'(Entry\.[^']*)'", py_content)
    entry_funcs.extend(re.findall(r'"(Entry\.[^"]*)"', py_content))
```

### 3단계: 블록 메타데이터 구성
```python
# 추출된 데이터를 구조화
for func in entry_funcs:
    blocks.append({
        "block_id": func.replace("Entry.", "").replace("()", ""),
        "category": js_file.stem.replace('block_', ''),  # 파일명에서 카테고리 추출
        "python_syntax": [func],
        "file": js_file.name
    })
```

### 4단계: RAG 문서 생성
```python
def generate_rag_docs(blocks):
    docs = []
    
    # 카테고리별 문서 생성
    categories = {}
    for block in blocks:
        cat = block['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(block)
    
    # 각 카테고리마다 가이드 문서 생성
    for category, cat_blocks in categories.items():
        content = f"# {category} 카테고리 블록들\n\n"
        for block in cat_blocks:
            content += f"## {block['block_id']}\n**Python 문법:** `{block['python_syntax'][0]}`\n\n"
        
        docs.append({
            "id": f"category_{category}",
            "title": f"엔트리 파이썬 - {category} 카테고리",
            "content": content,
            "type": "category_guide",
            "category": category
        })
```

## 🔍 추출되는 데이터 예시

### JavaScript 원본 (EntryJS)
```javascript
// .entryjs/entryjs/src/playground/blocks/block_boolean_input.js
syntax: {
    js: [],
    py: [
        'Entry.is_mouse_clicked()',
        'Entry.is_key_pressed(%1)',
        'Entry.is_clicked()'
    ]
}
```

### 추출된 Python 문법
```python
# 최종 생성되는 RAG 문서
{
    "id": "block_is_mouse_clicked",
    "title": "is_mouse_clicked 블록",
    "content": "# is_mouse_clicked 블록\n\n**Python 문법:**\n```python\nEntry.is_mouse_clicked()\n```",
    "type": "block_reference",
    "python_syntax": ["Entry.is_mouse_clicked()"]
}
```

## 📁 폴더 구조

```
entry-embedding/
├── entry_python_rag_docs.json    # 최종 RAG 문서 데이터 (39개)
├── extraction/                   # 데이터 추출 관련
│   ├── build_all.py             # 메인 추출 스크립트
│   └── extracted_blocks.json    # 중간 추출 결과 (23개 블록)
├── deploy/                       # AWS 배포 관련
│   ├── cdk/                     # CDK 인프라 코드
│   ├── create_index_simple.py   # OpenSearch 인덱스 생성
│   ├── deploy_final.sh         # 전체 배포 스크립트
│   └── .env.example            # 환경 변수 템플릿
└── docs/                        # 문서 및 설명
    ├── bedrock_kb_architecture.md
    ├── EXTRACTION_SUMMARY.md
    └── TODO.md
```

## 🚀 실행 방법

### 1. EntryJS 소스코드 준비
```bash
# 프로젝트 루트에서 실행
cd /home/dldnjs1013/projects/team15-aws-hackathon
git clone https://github.com/entrylabs/entryjs.git .entryjs
```

### 2. 데이터 추출 실행
```bash
cd entry-embedding/extraction
python3 build_all.py
```

### 3. 배포 실행
```bash
cd ../deploy
cp .env.example .env
# .env 파일 편집 후
./deploy_final.sh
```

## 📊 추출 결과

- **EntryJS 블록 파일**: `block_*.js` 패턴으로 스캔
- **추출된 블록**: 23개 (boolean_input, moving, sound 등)
- **생성된 RAG 문서**: 39개 (카테고리 14개 + 블록 23개 + 가이드 2개)
- **Python 문법 예시**: `Entry.is_mouse_clicked()`, `Entry.show()`, `Entry.hide()` 등

## ⚠️ 주의사항

1. **EntryJS 의존성**: 반드시 `.entryjs` 디렉토리에 EntryJS 소스코드가 있어야 함
2. **경로 의존성**: `build_all.py`는 상대경로 `../../.entryjs`를 사용
3. **파일 인코딩**: JavaScript 파일은 UTF-8로 읽어야 함
4. **정규식 패턴**: `py: [...]` 패턴이 없는 블록은 추출되지 않음

## 🔍 사용 예시

```
Q: Entry.is_mouse_clicked() 함수 사용법을 알려줘
Q: boolean_input 카테고리에 어떤 블록들이 있나요?
Q: 날씨 관련 블록의 Python 문법을 보여줘
```
