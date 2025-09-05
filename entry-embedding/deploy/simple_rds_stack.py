from aws_cdk import (
    Stack, aws_s3 as s3, aws_bedrock as bedrock, aws_rds as rds,
    aws_iam as iam, aws_s3_deployment as s3deploy, aws_ec2 as ec2,
    CfnOutput, RemovalPolicy
)
from constructs import Construct

class SimpleRdsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # S3 버킷
        source_bucket = s3.Bucket(
            self, "EntryDocsSourceBucket",
            bucket_name=f"entry-python-docs-rds-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # RDS PostgreSQL 인스턴스
        db_instance = rds.DatabaseInstance(
            self, "EntryRagDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            credentials=rds.Credentials.from_generated_secret("postgres"),
            database_name="entryrag",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[
                ec2.SecurityGroup(
                    self, "RdsSecurityGroup",
                    vpc=vpc,
                    allow_all_outbound=True
                )
            ],
            publicly_accessible=True,
            removal_policy=RemovalPolicy.DESTROY,
            delete_automated_backups=True
        )

        # Bedrock 역할
        bedrock_role = iam.Role(
            self, "BedrockKnowledgeBaseRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "BedrockKnowledgeBasePolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["bedrock:InvokeModel", "bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            actions=["rds-data:*"],
                            resources=[f"arn:aws:rds:{self.region}:{self.account}:db:{db_instance.instance_identifier}"]
                        ),
                        iam.PolicyStatement(
                            actions=["secretsmanager:GetSecretValue"],
                            resources=[db_instance.secret.secret_arn]
                        )
                    ]
                )
            }
        )

        source_bucket.grant_read(bedrock_role)

        # Knowledge Base
        knowledge_base = bedrock.CfnKnowledgeBase(
            self, "EntryPythonKnowledgeBase",
            name="entry-python-knowledge-base",
            role_arn=bedrock_role.role_arn,
            knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn=f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v2:0"
                )
            ),
            storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
                type="RDS",
                rds_configuration=bedrock.CfnKnowledgeBase.RdsConfigurationProperty(
                    resource_arn=f"arn:aws:rds:{self.region}:{self.account}:db:{db_instance.instance_identifier}",
                    credentials_secret_arn=db_instance.secret.secret_arn,
                    database_name="entryrag",
                    table_name="bedrock_integration",
                    field_mapping=bedrock.CfnKnowledgeBase.RdsFieldMappingProperty(
                        primary_key_field="id",
                        vector_field="embedding",
                        text_field="chunks",
                        metadata_field="metadata"
                    )
                )
            )
        )

        # Data Source
        bedrock.CfnDataSource(
            self, "EntryPythonDataSource",
            knowledge_base_id=knowledge_base.attr_knowledge_base_id,
            name="entry-python-docs-rds",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                type="S3",
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=source_bucket.bucket_arn
                )
            )
        )

        # 문서 업로드
        s3deploy.BucketDeployment(
            self, "DeployDocs",
            sources=[s3deploy.Source.asset("../docs")],
            destination_bucket=source_bucket
        )

        # 출력
        CfnOutput(self, "BucketName", value=source_bucket.bucket_name)
        CfnOutput(self, "KnowledgeBaseId", value=knowledge_base.attr_knowledge_base_id)
        CfnOutput(self, "DBEndpoint", value=db_instance.instance_endpoint.hostname)
        CfnOutput(self, "SecretArn", value=db_instance.secret.secret_arn)