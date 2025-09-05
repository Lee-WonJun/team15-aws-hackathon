#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

def extract_blocks_from_entryjs():
    blocks = []
    blocks_dir = Path("../../.entryjs/entryjs/src/playground/blocks")
    
    if not blocks_dir.exists():
        return []
    
    for js_file in blocks_dir.glob("block_*.js"):
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            py_patterns = re.findall(r"py:\s*\[(.*?)\]", content, re.DOTALL)
            
            for py_content in py_patterns:
                entry_funcs = re.findall(r"'(Entry\.[^']*)'", py_content)
                entry_funcs.extend(re.findall(r'"(Entry\.[^"]*)"', py_content))
                
                for func in entry_funcs:
                    blocks.append({
                        "block_id": func.replace("Entry.", "").replace("()", "").replace("(%1)", "").replace("(%2)", "").replace("(%3)", ""),
                        "category": js_file.stem.replace('block_', ''),
                        "python_syntax": [func],
                        "file": js_file.name
                    })
        except:
            continue
    
    return blocks

def generate_rag_docs(blocks):
    docs = []
    
    # Category docs
    categories = {}
    for block in blocks:
        cat = block['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(block)
    
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
    
    # Individual block docs
    for block in blocks:
        content = f"# {block['block_id']} 블록\n\n**Python 문법:**\n```python\n{block['python_syntax'][0]}\n```\n\n"
        
        docs.append({
            "id": f"block_{block['block_id']}",
            "title": f"{block['block_id']} 블록",
            "content": content,
            "type": "block_reference"
        })
    
    return docs

def main():
    print("=== Entry Python RAG 문서 빌드 ===")
    
    blocks = extract_blocks_from_entryjs()
    print(f"추출된 블록: {len(blocks)}개")
    
    docs = generate_rag_docs(blocks)
    
    with open("../entry_python_rag_docs.json", 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    os.makedirs("../deploy/docs", exist_ok=True)
    for doc in docs:
        with open(f"../deploy/docs/{doc['id']}.md", 'w', encoding='utf-8') as f:
            f.write(f"---\nid: {doc['id']}\ntitle: {doc['title']}\ntype: {doc['type']}\n---\n\n{doc['content']}")
    
    print(f"완료: {len(docs)}개 문서 생성")

if __name__ == "__main__":
    main()