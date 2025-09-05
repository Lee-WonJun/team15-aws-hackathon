from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_opensearchserverless as opensearch,
    aws_iam as iam,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    RemovalPolicy
)
import json
from constructs import Construct

class EntryRagStackPhase1(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 버킷 생성
        source_bucket = s3.Bucket(
            self, "EntryDocsSourceBucket",
            bucket_name=f"entry-python-docs-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # OpenSearch Serverless 컬렉션
        collection = opensearch.CfnCollection(
            self, "EntryRagCollection",
            name="entry-rag-collection",
            type="VECTORSEARCH"
        )

        # OpenSearch Serverless 보안 정책
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

        # 컬렉션 의존성 설정
        collection.add_dependency(encryption_policy)
        collection.add_dependency(network_policy)

        # 마크다운 문서 자동 업로드
        s3deploy.BucketDeployment(
            self, "DeployDocs",
            sources=[s3deploy.Source.asset("../docs")],
            destination_bucket=source_bucket
        )

        # 출력
        CfnOutput(self, "SourceBucketName", value=source_bucket.bucket_name)
        CfnOutput(self, "CollectionEndpoint", value=collection.attr_collection_endpoint)
        CfnOutput(self, "CollectionArn", value=collection.attr_arn)