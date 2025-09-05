from aws_cdk import (
    Stack, aws_s3 as s3, aws_opensearchserverless as opensearch,
    aws_s3_deployment as s3deploy, CfnOutput, RemovalPolicy
)
import json
from constructs import Construct

class Step1InfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 버킷
        self.source_bucket = s3.Bucket(
            self, "EntryDocsSourceBucket",
            bucket_name=f"entry-python-docs-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # OpenSearch 보안 정책
        encryption_policy = opensearch.CfnSecurityPolicy(
            self, "EntryRagEncryptionPolicy",
            name="entry-rag-encryption-policy",
            type="encryption",
            policy=json.dumps({
                "Rules": [{"ResourceType": "collection", "Resource": ["collection/entry-rag-collection"]}],
                "AWSOwnedKey": True
            })
        )

        network_policy = opensearch.CfnSecurityPolicy(
            self, "EntryRagNetworkPolicy", 
            name="entry-rag-network-policy",
            type="network",
            policy=json.dumps([{
                "Rules": [{"ResourceType": "collection", "Resource": ["collection/entry-rag-collection"]}],
                "AllowFromPublic": True
            }])
        )

        # OpenSearch 컬렉션
        self.collection = opensearch.CfnCollection(
            self, "EntryRagCollection",
            name="entry-rag-collection",
            type="VECTORSEARCH"
        )
        self.collection.add_dependency(encryption_policy)
        self.collection.add_dependency(network_policy)

        # 문서 업로드
        s3deploy.BucketDeployment(
            self, "DeployDocs",
            sources=[s3deploy.Source.asset("../docs")],
            destination_bucket=self.source_bucket
        )

        # 출력
        CfnOutput(self, "BucketName", value=self.source_bucket.bucket_name)
        CfnOutput(self, "CollectionEndpoint", value=self.collection.attr_collection_endpoint)
        CfnOutput(self, "CollectionArn", value=self.collection.attr_arn)