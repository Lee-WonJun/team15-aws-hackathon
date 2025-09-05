#!/usr/bin/env python3
"""
Entry Python RAG API Server using FastMCP
"""

import json
import os
from typing import List, Dict, Any
from fastmcp import FastMCP

# 프로젝트 루트 경로 (현재 스크립트 기준 상대 경로)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_PATH = os.path.join(PROJECT_ROOT, "entry-embedding", "entry_python_rag_docs.json")

# FastMCP 서버 생성
mcp = FastMCP("Entry Python API")

def load_entry_docs() -> List[Dict[str, Any]]:
    """엔트리 파이썬 문서 데이터 로드"""
    try:
        with open(DOCS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@mcp.tool()
def list_all_apis() -> str:
    """엔트리 파이썬 RAG 시스템의 모든 API 목록을 반환합니다"""
    docs = load_entry_docs()
    apis = []
    
    for doc in docs:
        if doc.get("type") == "block_reference":
            apis.append({
                "block_id": doc["block_id"],
                "category": doc["category"],
                "python_syntax": doc["python_syntax"],
                "parameters": doc.get("parameters", [])
            })
    
    result = {
        "total_apis": len(apis),
        "apis": apis
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
def list_categories() -> str:
    """사용 가능한 블록 카테고리 목록을 반환합니다"""
    docs = load_entry_docs()
    categories = set()
    
    for doc in docs:
        if "category" in doc:
            categories.add(doc["category"])
    
    return json.dumps(sorted(list(categories)), ensure_ascii=False, indent=2)

@mcp.tool()
def list_blocks_by_category(category: str) -> str:
    """특정 카테고리의 블록 목록을 반환합니다"""
    docs = load_entry_docs()
    blocks = []
    
    for doc in docs:
        if doc.get("category") == category and doc.get("type") == "block_reference":
            blocks.append({
                "block_id": doc["block_id"],
                "python_syntax": doc["python_syntax"],
                "parameters": doc.get("parameters", [])
            })
    
    return json.dumps(blocks, ensure_ascii=False, indent=2)

@mcp.tool()
def get_block_details(block_id: str) -> str:
    """특정 블록의 상세 정보를 반환합니다"""
    docs = load_entry_docs()
    
    for doc in docs:
        if doc.get("block_id") == block_id and doc.get("type") == "block_reference":
            return json.dumps(doc, ensure_ascii=False, indent=2)
    
    return f"블록 '{block_id}'를 찾을 수 없습니다."

@mcp.tool()
def search_python_syntax(syntax: str) -> str:
    """Python 문법으로 블록을 검색합니다"""
    docs = load_entry_docs()
    matches = []
    
    for doc in docs:
        if doc.get("type") == "block_reference":
            for py_syntax in doc.get("python_syntax", []):
                if syntax.lower() in py_syntax.lower():
                    matches.append({
                        "block_id": doc["block_id"],
                        "category": doc["category"],
                        "python_syntax": py_syntax,
                        "parameters": doc.get("parameters", [])
                    })
    
    return json.dumps(matches, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)