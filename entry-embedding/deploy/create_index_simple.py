#!/usr/bin/env python3
import boto3
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# AWS 클라이언트 설정
session = boto3.Session(
    aws_access_key_id=os.getenv('ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

aoss_client = session.client('opensearchserverless')

def create_vector_index():
    collection_endpoint = "https://htnuv49jy3dpgekonzrf.us-east-1.aoss.amazonaws.com"
    
    # OpenSearch 클라이언트 설정
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from aws_requests_auth.aws_auth import AWSRequestsAuth
    
    host = collection_endpoint.replace('https://', '')
    auth = AWSRequestsAuth(
        aws_access_key=os.getenv('ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
        aws_host=host,
        aws_region=os.getenv('AWS_REGION', 'us-east-1'),
        aws_service='aoss'
    )
    
    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    # 인덱스 생성
    index_name = "bedrock-knowledge-base-default-index"
    
    index_body = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                "vector": {
                    "type": "knn_vector",
                    "dimension": 1024,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "faiss"
                    }
                },
                "text": {"type": "text"},
                "metadata": {"type": "text"}
            }
        }
    }
    
    try:
        response = client.indices.create(index=index_name, body=index_body)
        print(f"✅ 인덱스 생성 성공: {index_name}")
        return True
    except Exception as e:
        if "already exists" in str(e):
            print(f"✅ 인덱스가 이미 존재합니다: {index_name}")
            return True
        else:
            print(f"❌ 인덱스 생성 실패: {e}")
            return False

if __name__ == "__main__":
    print("OpenSearch 인덱스 생성 중...")
    if create_vector_index():
        print("✅ 인덱스 생성 완료")
    else:
        print("❌ 인덱스 생성 실패")
        exit(1)
