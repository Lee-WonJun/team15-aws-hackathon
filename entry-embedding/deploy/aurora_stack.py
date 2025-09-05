from aws_cdk import (
    Stack, aws_s3 as s3, aws_bedrock as bedrock, aws_rds as rds,
    aws_iam as iam, aws_s3_deployment as s3deploy, aws_ec2 as ec2,
    CfnOutput, RemovalPolicy, SecretValue
)
from constructs import Construct

class AuroraRagStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC (기본 VPC 사용)
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # S3 버킷
        source_bucket = s3.Bucket(
            self, "EntryDocsSourceBucket",
            bucket_name=f"entry-python-docs-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Aurora Serverless v2 클러스터
        cluster = rds.DatabaseCluster(
            self, "EntryRagCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_15_4
            ),
            credentials=rds.Credentials.from_generated_secret("postgres"),
            default_database_name="entryrag",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[
                ec2.SecurityGroup(
                    self, "AuroraSecurityGroup",
                    vpc=vpc,
                    allow_all_outbound=True
                )
            ],
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Serverless v2 인스턴스 추가
        cluster.add_capacity("ServerlessInstance",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T4G, ec2.InstanceSize.MEDIUM),
            auto_minor_version_upgrade=False
        )

        # pgvector 확장 활성화를 위한 파라미터 그룹
        parameter_group = rds.ParameterGroup(
            self, "AuroraParameterGroup",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_15_4
            ),
            parameters={
                "shared_preload_libraries": "vector"
            }
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
                            resources=[cluster.cluster_arn]
                        ),
                        iam.PolicyStatement(
                            actions=["secretsmanager:GetSecretValue"],
                            resources=[cluster.secret.secret_arn]
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
                    resource_arn=cluster.cluster_arn,
                    credentials_secret_arn=cluster.secret.secret_arn,
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
            name="entry-python-docs",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                type="S3",
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=source_bucket.bucket_arn
                )
            ),
            vector_ingestion_configuration=bedrock.CfnDataSource.VectorIngestionConfigurationProperty(
                chunking_configuration=bedrock.CfnDataSource.ChunkingConfigurationProperty(
                    chunking_strategy="HIERARCHICAL",
                    hierarchical_chunking_configuration=bedrock.CfnDataSource.HierarchicalChunkingConfigurationProperty(
                        level_configurations=[
                            bedrock.CfnDataSource.HierarchicalChunkingLevelConfigurationProperty(max_tokens=1500),
                            bedrock.CfnDataSource.HierarchicalChunkingLevelConfigurationProperty(max_tokens=300)
                        ],
                        overlap_tokens=60
                    )
                ),
                parsing_configuration=bedrock.CfnDataSource.ParsingConfigurationProperty(
                    parsing_strategy="BEDROCK_FOUNDATION_MODEL",
                    bedrock_foundation_model_configuration=bedrock.CfnDataSource.BedrockFoundationModelConfigurationProperty(
                        model_arn=f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
                    )
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
        CfnOutput(self, "ClusterEndpoint", value=cluster.cluster_endpoint.hostname)
        CfnOutput(self, "SecretArn", value=cluster.secret.secret_arn)