#!/usr/bin/env python3
"""
AWS 환경변수 설정 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aws_config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

def setup_aws_env():
    """AWS 환경변수를 쉘 스크립트로 생성"""
    
    env_script = f"""#!/bin/bash
export AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
export AWS_DEFAULT_REGION={AWS_REGION}
export AWS_REGION={AWS_REGION}
"""
    
    with open('aws_env.sh', 'w') as f:
        f.write(env_script)
    
    os.chmod('aws_env.sh', 0o755)
    
    print(f"AWS 환경변수 설정 완료:")
    print(f"- Region: {AWS_REGION}")
    print(f"- Access Key: {AWS_ACCESS_KEY_ID[:10]}...")

if __name__ == "__main__":
    setup_aws_env()