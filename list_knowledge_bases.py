#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from aws_config.config import get_boto3_session

def list_knowledge_bases():
    """현재 계정의 모든 Knowledge Base 목록 조회"""
    try:
        session = get_boto3_session()
        bedrock_agent = session.client('bedrock-agent')
        
        response = bedrock_agent.list_knowledge_bases()
        
        print("=== 사용 가능한 Knowledge Base 목록 ===")
        print()
        
        if not response['knowledgeBaseSummaries']:
            print("Knowledge Base가 없습니다.")
            return
        
        for kb in response['knowledgeBaseSummaries']:
            print(f"ID: {kb['knowledgeBaseId']}")
            print(f"이름: {kb['name']}")
            print(f"상태: {kb['status']}")
            print(f"설명: {kb.get('description', 'N/A')}")
            print(f"생성일: {kb.get('createdAt', 'N/A')}")
            print("-" * 50)
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    list_knowledge_bases()