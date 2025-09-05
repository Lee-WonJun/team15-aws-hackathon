#!/usr/bin/env python3
"""
OpenSearch Serverless 데이터 접근 정책 추가
"""
import boto3
import json
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def add_data_access_policy():
    # AWS 세션 설정
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    )
    
    client = session.client('opensearchserverless')
    account_id = os.getenv('AWS_ACCOUNT_ID')
    
    # 데이터 접근 정책 생성
    policy_document = [{
        "Rules": [{
            "ResourceType": "collection",
            "Resource": ["collection/entry-rag-collection"],
            "Permission": ["aoss:*"]
        }, {
            "ResourceType": "index",
            "Resource": ["index/entry-rag-collection/*"],
            "Permission": ["aoss:*"]
        }],
        "Principal": [f"arn:aws:iam::{account_id}:root"]
    }]
    
    try:
        response = client.create_access_policy(
            name='entry-rag-data-access-policy',
            type='data',
            policy=json.dumps(policy_document)
        )
        print("✅ 데이터 접근 정책 생성 완료")
        print(f"정책 ARN: {response.get('securityPolicyDetail', {}).get('name')}")
        return True
    except Exception as e:
        if "already exists" in str(e):
            print("✅ 데이터 접근 정책이 이미 존재합니다")
            return True
        else:
            print(f"❌ 데이터 접근 정책 생성 실패: {str(e)}")
            return False

if __name__ == "__main__":
    print("=== OpenSearch 데이터 접근 정책 추가 ===")
    success = add_data_access_policy()
    if success:
        print("\n다음 단계: 인덱스를 생성하세요")
        print("python3 create_index.py")
    else:
        print("\n정책 생성에 실패했습니다.")