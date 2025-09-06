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

class StreamlitChatbotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, aws_credentials: dict = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 버킷 생성
        assets_bucket = s3.Bucket(
            self, "StreamlitAssetsBucket",
            bucket_name=f"streamlit-chatbot-assets-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # 기존 파일들을 S3에 업로드
        s3deploy.BucketDeployment(
            self, "DeployFiles",
            sources=[
                s3deploy.Source.asset("../../chatbot"),
                s3deploy.Source.asset("../../aws_config")
            ],
            destination_bucket=assets_bucket
        )
        
        s3deploy.BucketDeployment(
            self, "DeployEnv",
            sources=[
                s3deploy.Source.asset("../../", exclude=["**/*", "!.env"])
            ],
            destination_bucket=assets_bucket
        )

        # VPC
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # 보안 그룹
        security_group = ec2.SecurityGroup(
            self, "StreamlitSecurityGroup",
            vpc=vpc,
            description="Security group for Streamlit chatbot",
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
            "Streamlit access"
        )

        # IAM 역할
        ec2_role = iam.Role(
            self, "StreamlitEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ],
            inline_policies={
                "BedrockAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:Retrieve",
                                "bedrock:RetrieveAndGenerate"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "bedrock-agent-runtime:Retrieve"
                            ],
                            resources=["*"]
                        ),
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
            self, "StreamlitKeyPair",
            key_name="streamlit-chatbot-key"
        )

        # User Data 스크립트
        user_data_script = f"""#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1

# 패키지 업데이트 및 설치
yum update -y
yum install -y python3 python3-pip git aws-cli

# 프로젝트 디렉토리 생성
mkdir -p /home/ec2-user/project
cd /home/ec2-user/project

# S3에서 파일 다운로드
aws s3 sync s3://{assets_bucket.bucket_name}/ ./ --region {self.region}

# 파일 구조 정리
mkdir -p chatbot/aws_config
mv streamlit_app.py chatbot/
mv bedrock_client.py chatbot/
mv requirements.txt chatbot/
mv config.py chatbot/aws_config/
mv __init__.py chatbot/aws_config/
mv .env chatbot/

# .env 파일이 이미 S3에서 다운로드됨 - 추가 설정 불필요

# 가상환경 생성 및 패키지 설치
cd chatbot
python3 -m venv streamlit-env
source streamlit-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 소유권 변경
chown -R ec2-user:ec2-user /home/ec2-user/project

# nohup으로 Streamlit 시작
sudo -u ec2-user bash -c 'cd /home/ec2-user/project/chatbot && source streamlit-env/bin/activate && nohup streamlit run streamlit_app.py --server.port=8000 --server.address=0.0.0.0 > streamlit.log 2>&1 &'

# 시작 대기
sleep 15

# 상태 확인
echo "=== Streamlit 프로세스 상태 ===" >> /var/log/user-data.log
ps aux | grep streamlit >> /var/log/user-data.log 2>&1
echo "=== 포트 상태 ===" >> /var/log/user-data.log
ss -tlnp | grep :8000 >> /var/log/user-data.log 2>&1
"""

        # EC2 인스턴스 생성
        instance = ec2.Instance(
            self, "StreamlitInstance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MEDIUM
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
        CfnOutput(self, "StreamlitURL", value=f"http://{instance.instance_public_ip}:8000")
        CfnOutput(self, "SSHCommand", value=f"ssh -i streamlit-chatbot-key.pem ec2-user@{instance.instance_public_ip}")
        CfnOutput(self, "AssetsBucket", value=assets_bucket.bucket_name)