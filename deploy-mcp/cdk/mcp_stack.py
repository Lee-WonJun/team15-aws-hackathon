from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct

class EntryMcpStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 버킷 생성
        assets_bucket = s3.Bucket(
            self, "McpAssetsBucket",
            bucket_name=f"entry-mcp-assets-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # 기존 파일들을 S3에 업로드
        s3deploy.BucketDeployment(
            self, "DeployMcpFiles",
            sources=[
                s3deploy.Source.asset("../../entry-content-mcp"),
                s3deploy.Source.asset("../../entry-embedding")
            ],
            destination_bucket=assets_bucket
        )

        # VPC
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # 보안 그룹
        security_group = ec2.SecurityGroup(
            self, "McpSecurityGroup",
            vpc=vpc,
            description="Security group for Entry MCP server",
            allow_all_outbound=True
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "SSH access"
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8000),
            "MCP API access"
        )

        # IAM 역할
        ec2_role = iam.Role(
            self, "McpEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ],
            inline_policies={
                "S3Access": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "s3:GetObject",
                                "s3:ListBucket"
                            ],
                            resources=[
                                assets_bucket.bucket_arn,
                                f"{assets_bucket.bucket_arn}/*"
                            ]
                        )
                    ]
                )
            }
        )

        # 키페어
        key_pair = ec2.CfnKeyPair(
            self, "McpKeyPair",
            key_name="entry-mcp-key"
        )

        # User Data 스크립트
        user_data_script = f"""#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1

# 패키지 업데이트 및 설치
yum update -y
yum install -y git aws-cli gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make

# Python 3.11 소스에서 설치
cd /tmp
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar xzf Python-3.11.9.tgz
cd Python-3.11.9
./configure --enable-optimizations
make altinstall
ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3
ln -sf /usr/local/bin/pip3.11 /usr/local/bin/pip3

# 프로젝트 디렉토리 생성
mkdir -p /home/ec2-user/mcp-project
cd /home/ec2-user/mcp-project

# S3에서 파일 다운로드
aws s3 sync s3://{assets_bucket.bucket_name}/ ./ --region {self.region}

# 파일 구조 정리
mkdir -p entry-mcp
mv entry_api_server.py entry-mcp/
mv requirements.txt entry-mcp/
mkdir -p entry-mcp/entry-embedding
mv entry_python_rag_docs.json entry-mcp/entry-embedding/

# 가상환경 생성 및 패키지 설치
cd entry-mcp
/usr/local/bin/python3.11 -m venv mcp-env
source mcp-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 소유권 변경
chown -R ec2-user:ec2-user /home/ec2-user/mcp-project

# nohup으로 MCP 서버 시작
sudo -u ec2-user bash -c 'cd /home/ec2-user/mcp-project/entry-mcp && source mcp-env/bin/activate && nohup python entry_api_server.py > mcp.log 2>&1 &'

# 시작 대기
sleep 15

# 상태 확인
echo "=== MCP 프로세스 상태 ===" >> /var/log/user-data.log
ps aux | grep entry_api_server >> /var/log/user-data.log 2>&1
echo "=== 포트 상태 ===" >> /var/log/user-data.log
ss -tlnp | grep :8000 >> /var/log/user-data.log 2>&1
"""

        # EC2 인스턴스 생성
        instance = ec2.Instance(
            self, "McpInstance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.SMALL
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023
            ),
            vpc=vpc,
            security_group=security_group,
            role=ec2_role,
            key_name=key_pair.key_name,
            user_data=ec2.UserData.custom(user_data_script)
        )

        # 출력
        CfnOutput(self, "InstanceId", value=instance.instance_id)
        CfnOutput(self, "PublicIP", value=instance.instance_public_ip)
        CfnOutput(self, "McpURL", value=f"http://{instance.instance_public_ip}:8000")
        CfnOutput(self, "SSHCommand", value=f"ssh -i entry-mcp-key.pem ec2-user@{instance.instance_public_ip}")
        CfnOutput(self, "AssetsBucket", value=assets_bucket.bucket_name)