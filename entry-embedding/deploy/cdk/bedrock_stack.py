from aws_cdk import (
    Stack,
    aws_bedrock as bedrock,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    CfnOutput,
    Duration,
    CustomResource
)
import json
from constructs import Construct

class BedrockStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 기존 리소스 참조
        bucket_name = "entry-python-docs-simple-339712825274-us-east-1"
        collection_arn = "arn:aws:aoss:us-east-1:339712825274:collection/htnuv49jy3dpgekonzrf"

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
                            resources=[collection_arn]
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "s3:GetObject",
                                "s3:ListBucket"
                            ],
                            resources=[
                                f"arn:aws:s3:::{bucket_name}",
                                f"arn:aws:s3:::{bucket_name}/*"
                            ]
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
                    collection_arn=collection_arn,
                    vector_index_name="bedrock-knowledge-base-default-index",
                    field_mapping=bedrock.CfnKnowledgeBase.OpenSearchServerlessFieldMappingProperty(
                        vector_field="vector",
                        text_field="text",
                        metadata_field="metadata"
                    )
                )
            )
        )

        # Data Source 생성
        data_source = bedrock.CfnDataSource(
            self, "EntryPythonDataSource",
            knowledge_base_id=knowledge_base.attr_knowledge_base_id,
            name="entry-python-docs",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                type="S3",
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=f"arn:aws:s3:::{bucket_name}"
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
                            actions=["bedrock:*"],
                            resources=["*"]
                        )
                    ]
                )
            }
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
            
            # 완료 대기 (최대 10분)
            for i in range(60):
                job_status = bedrock.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds_id,
                    ingestionJobId=job_id
                )
                
                status = job_status['ingestionJob']['status']
                if status in ['COMPLETE', 'FAILED']:
                    break
                    
                time.sleep(10)
            
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
""")
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
        # sync_cr.node.add_dependency(data_source)  # Comment out problematic dependency

        # 출력
        CfnOutput(self, "KnowledgeBaseId", value=knowledge_base.attr_knowledge_base_id)
        CfnOutput(self, "DataSourceId", value=data_source.attr_data_source_id)