#!/bin/bash

echo "=== 단계별 CDK 배포 ==="

# 환경변수 로드
source .env
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_ACCOUNT_ID AWS_REGION

# Step 1: 인프라 배포 (S3 + OpenSearch)
echo "Step 1: 인프라 배포 중..."
cd cdk
cat > app_step1.py << 'EOF'
#!/usr/bin/env python3
import aws_cdk as cdk
import sys
sys.path.append('..')
from step1_infrastructure import Step1InfrastructureStack
import os

app = cdk.App()
Step1InfrastructureStack(app, "Step1Infrastructure",
    env=cdk.Environment(
        account=os.environ.get('AWS_ACCOUNT_ID'),
        region=os.environ.get('AWS_REGION', 'us-east-1')
    )
)
app.synth()
EOF

cdk deploy Step1Infrastructure --require-approval never --app "python3 app_step1.py"

if [ $? -ne 0 ]; then
    echo "❌ Step 1 실패"
    exit 1
fi

echo "✅ Step 1 완료"
echo "⏳ 5분 대기 (OpenSearch 컬렉션 안정화)..."
sleep 300

# Step 2: 데이터 접근 정책 생성
echo "Step 2: 데이터 접근 정책 생성..."
cd ..
python3 -c "
import boto3, json, os
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)
client = session.client('opensearchserverless')
try:
    client.create_access_policy(
        name='entry-rag-data-access-policy',
        type='data',
        policy=json.dumps([{
            'Rules': [
                {'ResourceType': 'collection', 'Resource': ['collection/entry-rag-collection'], 'Permission': ['aoss:*']},
                {'ResourceType': 'index', 'Resource': ['index/entry-rag-collection/*'], 'Permission': ['aoss:*']}
            ],
            'Principal': ['arn:aws:iam::339712825274:user/Hackathon']
        }])
    )
    print('✅ 데이터 접근 정책 생성 완료')
except Exception as e:
    if 'already exists' in str(e):
        print('✅ 데이터 접근 정책 이미 존재')
    else:
        print(f'❌ 정책 생성 실패: {e}')
"

echo "⏳ 2분 대기 (정책 적용)..."
sleep 120

# Step 3: 인덱스 생성
echo "Step 3: OpenSearch 인덱스 생성..."
python3 -c "
import boto3, json, requests, os
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

# 컬렉션 엔드포인트 가져오기
cf = session.client('cloudformation')
outputs = cf.describe_stacks(StackName='Step1Infrastructure')['Stacks'][0]['Outputs']
endpoint = next(o['OutputValue'] for o in outputs if o['OutputKey'] == 'CollectionEndpoint')

# 인덱스 생성
url = f'{endpoint}/bedrock-knowledge-base-default-index'
body = {
    'mappings': {
        'properties': {
            'vector': {'type': 'knn_vector', 'dimension': 1024},
            'text': {'type': 'text'},
            'metadata': {'type': 'object'}
        }
    }
}

request = AWSRequest(method='PUT', url=url, data=json.dumps(body), headers={'Content-Type': 'application/json'})
SigV4Auth(session.get_credentials(), 'aoss', session.region_name).add_auth(request)

response = requests.put(url, data=request.body, headers=dict(request.headers))
if response.status_code in [200, 201]:
    print('✅ 인덱스 생성 완료')
else:
    print(f'❌ 인덱스 생성 실패: {response.status_code} - {response.text}')
"

echo "⏳ 1분 대기 (인덱스 안정화)..."
sleep 60

# Step 4: Bedrock Knowledge Base 배포
echo "Step 4: Bedrock Knowledge Base 배포..."
cd cdk

# 이전 스택 출력값 가져오기
COLLECTION_ARN=$(aws cloudformation describe-stacks --stack-name Step1Infrastructure --query 'Stacks[0].Outputs[?OutputKey==`CollectionArn`].OutputValue' --output text)
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name Step1Infrastructure --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)
BUCKET_ARN="arn:aws:s3:::$BUCKET_NAME"

cat > app_step2.py << EOF
#!/usr/bin/env python3
import aws_cdk as cdk
import sys
sys.path.append('..')
from step2_bedrock import Step2BedrockStack
import os

app = cdk.App()
Step2BedrockStack(app, "Step2Bedrock",
    collection_arn="$COLLECTION_ARN",
    bucket_arn="$BUCKET_ARN",
    env=cdk.Environment(
        account=os.environ.get('AWS_ACCOUNT_ID'),
        region=os.environ.get('AWS_REGION', 'us-east-1')
    )
)
app.synth()
EOF

cdk deploy Step2Bedrock --require-approval never --app "python3 app_step2.py"

if [ $? -eq 0 ]; then
    echo "✅ 전체 배포 완료!"
    aws cloudformation describe-stacks --stack-name Step2Bedrock --query 'Stacks[0].Outputs'
else
    echo "❌ Step 4 실패"
    exit 1
fi