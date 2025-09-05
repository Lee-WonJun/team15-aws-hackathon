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

class SimpleCompleteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 버킷
        source_bucket = s3.Bucket(
            self, "EntryDocsSourceBucket",
            bucket_name=f"entry-python-docs-simple-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # OpenSearch Serverless 보안 정책들
        encryption_policy = opensearch.CfnSecurityPolicy(
            self, "EntryRagEncryptionPolicy",
            name="entry-encrypt-policy-v2",
            type="encryption",
            policy=json.dumps({
                "Rules": [{
                    "ResourceType": "collection",
                    "Resource": ["collection/entry-collection-v2"]
                }],
                "AWSOwnedKey": True
            })
        )

        network_policy = opensearch.CfnSecurityPolicy(
            self, "EntryRagNetworkPolicy", 
            name="entry-network-policy-v2",
            type="network",
            policy=json.dumps([{
                "Rules": [{
                    "ResourceType": "collection",
                    "Resource": ["collection/entry-collection-v2"]
                }, {
                    "ResourceType": "dashboard",
                    "Resource": ["collection/entry-collection-v2"]
                }],
                "AllowFromPublic": True
            }])
        )

        # 데이터 접근 정책
        data_access_policy = opensearch.CfnAccessPolicy(
            self, "EntryRagDataAccessPolicy",
            name="entry-data-policy-v2",
            type="data",
            policy=json.dumps([{
                "Rules": [{
                    "ResourceType": "collection",
                    "Resource": ["collection/entry-collection-v2"],
                    "Permission": ["aoss:*"]
                }, {
                    "ResourceType": "index",
                    "Resource": ["index/entry-collection-v2/*"],
                    "Permission": ["aoss:*"]
                }],
                "Principal": [f"arn:aws:iam::{self.account}:root"]
            }])
        )

        # OpenSearch Serverless 컬렉션
        collection = opensearch.CfnCollection(
            self, "EntryRagCollection",
            name="entry-collection-v2",
            type="VECTORSEARCH"
        )
        collection.add_dependency(encryption_policy)
        collection.add_dependency(network_policy)
        collection.add_dependency(data_access_policy)

        # 문서 업로드
        s3deploy.BucketDeployment(
            self, "DeployDocs",
            sources=[s3deploy.Source.asset("../docs")],
            destination_bucket=source_bucket
        )

        # 출력
        CfnOutput(self, "SourceBucketName", value=source_bucket.bucket_name)
        CfnOutput(self, "CollectionEndpoint", value=collection.attr_collection_endpoint)
        CfnOutput(self, "CollectionArn", value=collection.attr_arn)