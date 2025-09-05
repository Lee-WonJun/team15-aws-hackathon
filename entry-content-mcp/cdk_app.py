#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_iam as iam,
)
from constructs import Construct

class McpServerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "McpVpc", max_azs=2)

        # ECS Cluster
        cluster = ecs.Cluster(self, "McpCluster", vpc=vpc)

        # Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self, "McpTaskDef",
            memory_limit_mib=512,
            cpu=256
        )

        # Container
        container = task_definition.add_container(
            "mcp-server",
            image=ecs.ContainerImage.from_asset("."),
            port_mappings=[ecs.PortMapping(container_port=8000)],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="mcp-server",
                log_retention=logs.RetentionDays.ONE_WEEK
            )
        )

        # Service
        service = ecs.FargateService(
            self, "McpService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            assign_public_ip=True
        )

app = cdk.App()
McpServerStack(app, "McpServerStack")
app.synth()
