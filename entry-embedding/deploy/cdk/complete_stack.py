from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_bedrock as bedrock,
    aws_opensearchserverless as opensearch,
    aws_iam as iam,
    aws_s3_deployment as s3deploy,
    aws_lambda as lambda_,
    aws_logs as logs,
    custom_resources as cr,
    CfnOutput,
    RemovalPolicy,
    Duration,
    CustomResource
)
import json
from constructs import Construct

class CompleteEntryRagStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 버킷
        source_bucket = s3.Bucket(
            self, "EntryDocsSourceBucket",
            bucket_name=f"entry-python-docs-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # OpenSearch Serverless 보안 정책들
        encryption_policy = opensearch.CfnSecurityPolicy(
            self, "EntryRagEncryptionPolicy",
            name="entry-rag-encryption-policy",
            type="encryption",
            policy=json.dumps({
                "Rules": [{
                    "ResourceType": "collection",
                    "Resource": ["collection/entry-rag-collection"]
                }],
                "AWSOwnedKey": True
            })
        )

        network_policy = opensearch.CfnSecurityPolicy(
            self, "EntryRagNetworkPolicy", 
            name="entry-rag-network-policy",
            type="network",
            policy=json.dumps([{
                "Rules": [{
                    "ResourceType": "collection",
                    "Resource": ["collection/entry-rag-collection"]
                }, {
                    "ResourceType": "dashboard",
                    "Resource": ["collection/entry-rag-collection"]
                }],
                "AllowFromPublic": True
            }])
        )

        # 데이터 접근 정책
        data_access_policy = opensearch.CfnAccessPolicy(
            self, "EntryRagDataAccessPolicy",
            name="entry-rag-data-access-policy",
            type="data",
            policy=json.dumps([{
                "Rules": [{
                    "ResourceType": "collection",
                    "Resource": ["collection/entry-rag-collection"],
                    "Permission": ["aoss:*"]
                }, {
                    "ResourceType": "index",
                    "Resource": ["index/entry-rag-collection/*"],
                    "Permission": ["aoss:*"]
                }],
                "Principal": [f"arn:aws:iam::{self.account}:root"]
            }])
        )

        # OpenSearch Serverless 컬렉션
        collection = opensearch.CfnCollection(
            self, "EntryRagCollection",
            name="entry-rag-collection",
            type="VECTORSEARCH"
        )
        collection.add_dependency(encryption_policy)
        collection.add_dependency(network_policy)
        collection.add_dependency(data_access_policy)

        # Bedrock 서비스 역할
        bedrock_role = iam.Role(
            self, "BedrockKnowledgeBaseRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "BedrockKnowledgeBasePolicy": iam.PolicyDocument(
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
                            actions=["aoss:*"],
                            resources=[collection.attr_arn]
                        )
                    ]
                )
            }
        )
        source_bucket.grant_read(bedrock_role)

        # Lambda 실행 역할
        lambda_role = iam.Role(
            self, "KnowledgeBaseLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            inline_policies={
                "KnowledgeBasePolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "bedrock:*",
                                "aoss:*",
                                "s3:GetObject",
                                "s3:ListBucket"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

        # Knowledge Base 생성
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
                type="OPENSEARCH_SERVERLESS",
                opensearch_serverless_configuration=bedrock.CfnKnowledgeBase.OpenSearchServerlessConfigurationProperty(
                    collection_arn=collection.attr_arn,
                    vector_index_name="bedrock-knowledge-base-default-index",
                    field_mapping=bedrock.CfnKnowledgeBase.OpenSearchServerlessFieldMappingProperty(
                        vector_field="vector",
                        text_field="text",
                        metadata_field="metadata"
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

        # Data Source 생성
        data_source = bedrock.CfnDataSource(
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
                            bedrock.CfnDataSource.HierarchicalChunkingLevelConfigurationProperty(
                                max_tokens=1500
                            ),
                            bedrock.CfnDataSource.HierarchicalChunkingLevelConfigurationProperty(
                                max_tokens=300
                            )
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

        # 자동 동기화 Lambda
        sync_lambda = lambda_.Function(
            self, "KnowledgeBaseSyncLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            role=lambda_role,
            timeout=Duration.minutes(15),
            code=lambda_.Code.from_inline("""
import boto3
import json
import time

def handler(event, context):
    bedrock = boto3.client('bedrock-agent')
    
    kb_id = event['ResourceProperties']['KnowledgeBaseId']
    ds_id = event['ResourceProperties']['DataSourceId']
    
    if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
        try:
            # 동기화 시작
            response = bedrock.start_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=ds_id
            )
            
            job_id = response['ingestionJob']['ingestionJobId']
            
            # 완료 대기
            while True:
                job_status = bedrock.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds_id,
                    ingestionJobId=job_id
                )
                
                status = job_status['ingestionJob']['status']
                if status in ['COMPLETE', 'FAILED']:
                    break
                    
                time.sleep(30)
            
            return {
                'Status': 'SUCCESS',
                'PhysicalResourceId': job_id,
                'Data': {'JobId': job_id, 'Status': status}
            }
            
        except Exception as e:
            return {
                'Status': 'FAILED',
                'Reason': str(e),
                'PhysicalResourceId': 'failed'
            }
    
    return {'Status': 'SUCCESS', 'PhysicalResourceId': 'deleted'}
"""),
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        # 커스텀 리소스로 자동 동기화 실행
        sync_cr = CustomResource(
            self, "KnowledgeBaseSyncCustomResource",
            service_token=sync_lambda.function_arn,
            properties={
                "KnowledgeBaseId": knowledge_base.attr_knowledge_base_id,
                "DataSourceId": data_source.attr_data_source_id
            }
        )
        sync_cr.node.add_dependency(data_source)

        # 출력
        CfnOutput(self, "SourceBucketName", value=source_bucket.bucket_name)
        CfnOutput(self, "KnowledgeBaseId", value=knowledge_base.attr_knowledge_base_id)
        CfnOutput(self, "CollectionEndpoint", value=collection.attr_collection_endpoint)
        CfnOutput(self, "DataSourceId", value=data_source.attr_data_source_id)