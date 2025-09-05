#!/usr/bin/env python3
"""
OpenSearch Serverless 인덱스 생성 스크립트
"""
import boto3
import json
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def create_opensearch_index():
    # AWS 세션 설정
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    )
    
    # CloudFormation에서 컬렉션 엔드포인트 가져오기
    cf_client = session.client('cloudformation')
    
    try:
        # 먼저 Phase1 스택에서 시도
        try:
            response = cf_client.describe_stacks(StackName='EntryRagStackPhase1')
        except:
            # Phase1이 없으면 메인 스택에서 시도
            response = cf_client.describe_stacks(StackName='EntryRagStack')
        outputs = response['Stacks'][0]['Outputs']
        
        collection_endpoint = None
        for output in outputs:
            if output['OutputKey'] == 'CollectionEndpoint':
                collection_endpoint = output['OutputValue']
                break
        
        if not collection_endpoint:
            print("❌ 컬렉션 엔드포인트를 찾을 수 없습니다.")
            return False
            
        print(f"✅ 컬렉션 엔드포인트: {collection_endpoint}")
        
        # 인덱스 생성 요청
        index_name = "entry-python-index"
        url = f"{collection_endpoint}/{index_name}"
        
        # 인덱스 매핑 정의
        index_body = {
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
                    "metadata": {"type": "object"}
                }
            }
        }
        
        # AWS 서명된 요청 생성
        credentials = session.get_credentials()
        region = session.region_name
        
        request = AWSRequest(
            method='PUT',
            url=url,
            data=json.dumps(index_body),
            headers={'Content-Type': 'application/json'}
        )
        
        SigV4Auth(credentials, 'aoss', region).add_auth(request)
        
        # 요청 실행
        response = requests.put(
            url,
            data=request.body,
            headers=dict(request.headers)
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ 인덱스 '{index_name}' 생성 완료")
            return True
        else:
            print(f"❌ 인덱스 생성 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== OpenSearch 인덱스 생성 ===")
    success = create_opensearch_index()
    if success:
        print("\n다음 단계: CDK 스택을 다시 배포하세요")
        print("./deploy.sh")
    else:
        print("\n인덱스 생성에 실패했습니다.")