import json
import os
from typing import List, Dict, Any

# 문서 파일 경로
DOCS_PATH = os.path.join(os.path.dirname(__file__), "entry_python_rag_docs.json")

def load_entry_docs() -> List[Dict[str, Any]]:
    """엔트리 파이썬 문서 데이터 로드"""
    try:
        with open(DOCS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def list_all_apis() -> str:
    """엔트리 파이썬 RAG 시스템의 모든 API 목록을 반환합니다"""
    docs = load_entry_docs()
    apis = []
    
    for doc in docs:
        if doc.get("type") == "block_reference":
            apis.append({
                "id": doc["id"],
                "title": doc["title"],
                "content": doc["content"]
            })
    
    result = {
        "total_apis": len(apis),
        "apis": apis
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)

def handler(event, context):
    """Lambda handler"""
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    if path == '/apis' and method == 'GET':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': list_all_apis()
        }
    
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'})
    }
