from aws_cdk import (
    Stack, aws_bedrock as bedrock, aws_iam as iam, CfnOutput
)
from constructs import Construct

class Step2BedrockStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 collection_arn: str, bucket_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
                            actions=["aoss:APIAccessAll"],
                            resources=[collection_arn]
                        ),
                        iam.PolicyStatement(
                            actions=["s3:GetObject", "s3:ListBucket"],
                            resources=[bucket_arn, f"{bucket_arn}/*"]
                        )
                    ]
                )
            }
        )

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

        # Data Source
        bedrock.CfnDataSource(
            self, "EntryPythonDataSource",
            knowledge_base_id=knowledge_base.attr_knowledge_base_id,
            name="entry-python-docs",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                type="S3",
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=bucket_arn
                )
            )
        )

        CfnOutput(self, "KnowledgeBaseId", value=knowledge_base.attr_knowledge_base_id)