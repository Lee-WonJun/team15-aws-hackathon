import os
import boto3
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# AWS 설정 정보
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
AWS_REGION = os.getenv('AWS_REGION')
AWS_PROFILE = os.getenv('AWS_PROFILE')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

def get_bedrock_client():
    """Bedrock 클라이언트 생성"""
    # 환경변수 설정
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_DEFAULT_REGION'] = AWS_REGION
    
    # 프로필 관련 환경변수 제거
    if 'AWS_PROFILE' in os.environ:
        del os.environ['AWS_PROFILE']
    
    # 세션을 먼저 생성하고 클라이언트 생성
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    return session.client('bedrock-runtime')

def get_bedrock_agent_runtime_client():
    """Bedrock Agent Runtime 클라이언트 생성"""
    # 환경변수 설정
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_DEFAULT_REGION'] = AWS_REGION
    
    # 프로필 관련 환경변수 제거
    if 'AWS_PROFILE' in os.environ:
        del os.environ['AWS_PROFILE']
    
    # 세션을 먼저 생성하고 클라이언트 생성
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    return session.client('bedrock-agent-runtime')

def get_boto3_session():
    """boto3 세션 생성"""
    # 환경변수 설정
    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_DEFAULT_REGION'] = AWS_REGION
    
    # 프로필 관련 환경변수 제거
    if 'AWS_PROFILE' in os.environ:
        del os.environ['AWS_PROFILE']
    
    return boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

if __name__ == "__main__":
    print(f"AWS Account ID: {AWS_ACCOUNT_ID}")
    print(f"AWS Region: {AWS_REGION}")
    print(f"AWS Profile: {AWS_PROFILE}")
    print("AWS 설정이 로드되었습니다.")