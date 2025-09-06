# Entry Python RAG System Architecture

## System Overview Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Streamlit Web UI]
        CLI[Q CLI Interface]
    end
    
    subgraph "Application Layer"
        subgraph "MCP Services"
            EMCP[Entry Content MCP<br/>FastMCP Server]
            SMCP[Entry Studio MCP<br/>Selenium Automation]
        end
        
        subgraph "Core Services"
            CHAT[Bedrock Chatbot<br/>streamlit_app.py]
            API[Entry API Server<br/>entry_api_server.py]
        end
    end
    
    subgraph "AWS Cloud Services"
        subgraph "AI/ML Services"
            BEDROCK[Amazon Bedrock<br/>Claude 3.5 Sonnet]
            KB[Knowledge Base<br/>9R38KN62YH]
            OPENSEARCH[OpenSearch Serverless<br/>Vector Database]
        end
        
        subgraph "Storage & Compute"
            S3[Amazon S3<br/>Document Storage]
            LAMBDA[AWS Lambda<br/>API Endpoints]
            ECS[Amazon ECS/Fargate<br/>Container Services]
        end
        
        subgraph "Infrastructure"
            CDK[AWS CDK<br/>Infrastructure as Code]
            IAM[AWS IAM<br/>Access Control]
        end
    end
    
    subgraph "Data Sources"
        DOCS[Entry Python Docs<br/>JSON Format]
        BLOCKS[Entry Block Definitions<br/>Categories & APIs]
        STUDIO[Entry Studio<br/>Web Interface]
    end
    
    subgraph "Development Tools"
        DEPLOY[Deploy Scripts<br/>deploy.sh]
        EXTRACT[Data Extraction<br/>build_all.py]
    end
    
    %% Client connections
    UI --> CHAT
    CLI --> EMCP
    CLI --> SMCP
    
    %% Application layer connections
    CHAT --> BEDROCK
    EMCP --> API
    SMCP --> STUDIO
    API --> DOCS
    
    %% AWS service connections
    BEDROCK --> KB
    KB --> OPENSEARCH
    KB --> S3
    LAMBDA --> BEDROCK
    ECS --> SMCP
    
    %% Data flow
    DOCS --> S3
    BLOCKS --> DOCS
    EXTRACT --> DOCS
    DEPLOY --> CDK
    CDK --> ECS
    CDK --> LAMBDA
    CDK --> S3
    
    %% Security
    IAM --> BEDROCK
    IAM --> S3
    IAM --> OPENSEARCH
    
    classDef client fill:#e1f5fe
    classDef app fill:#f3e5f5
    classDef aws fill:#fff3e0
    classDef data fill:#e8f5e8
    classDef dev fill:#fce4ec
    
    class UI,CLI client
    class EMCP,SMCP,CHAT,API app
    class BEDROCK,KB,OPENSEARCH,S3,LAMBDA,ECS,CDK,IAM aws
    class DOCS,BLOCKS,STUDIO data
    class DEPLOY,EXTRACT dev
```

## Component Details

### MCP Services
- **Entry Content MCP**: FastMCP server providing Entry documentation APIs
- **Entry Studio MCP**: Selenium-based automation for Entry Studio web interface

### Core Services  
- **Bedrock Chatbot**: Streamlit-based chat interface using Claude 3.5 Sonnet
- **Entry API Server**: FastMCP server exposing Entry block and category information

### AWS Services
- **Amazon Bedrock**: Foundation model service with Claude 3.5 Sonnet
- **Knowledge Base**: RAG system with ID 9R38KN62YH
- **OpenSearch Serverless**: Vector database for document embeddings
- **S3**: Storage for Entry documentation and media files
- **Lambda**: Serverless API endpoints
- **ECS/Fargate**: Container orchestration for MCP services

### Data Pipeline
- **Extraction**: Automated data extraction from Entry documentation
- **Processing**: Document parsing and embedding generation
- **Storage**: Vector storage in OpenSearch with metadata
- **Retrieval**: Semantic search and context generation

## Deployment Architecture

```mermaid
graph LR
    subgraph "Development"
        DEV[Local Development]
        SCRIPTS[Deploy Scripts]
    end
    
    subgraph "CI/CD Pipeline"
        BUILD[Build & Test]
        DEPLOY[Deploy to AWS]
    end
    
    subgraph "Production Environment"
        subgraph "Container Services"
            ECS_CLUSTER[ECS Cluster]
            ENTRY_MCP[Entry Content MCP]
            STUDIO_MCP[Entry Studio MCP]
        end
        
        subgraph "Serverless Services"
            LAMBDA_API[Lambda APIs]
            BEDROCK_KB[Bedrock Knowledge Base]
        end
        
        subgraph "Web Interface"
            STREAMLIT[Streamlit App]
            ALB[Application Load Balancer]
        end
    end
    
    DEV --> SCRIPTS
    SCRIPTS --> BUILD
    BUILD --> DEPLOY
    DEPLOY --> ECS_CLUSTER
    DEPLOY --> LAMBDA_API
    DEPLOY --> BEDROCK_KB
    
    ECS_CLUSTER --> ENTRY_MCP
    ECS_CLUSTER --> STUDIO_MCP
    ALB --> STREAMLIT
    
    classDef dev fill:#e3f2fd
    classDef cicd fill:#f1f8e9
    classDef prod fill:#fff8e1
    
    class DEV,SCRIPTS dev
    class BUILD,DEPLOY cicd
    class ECS_CLUSTER,ENTRY_MCP,STUDIO_MCP,LAMBDA_API,BEDROCK_KB,STREAMLIT,ALB prod
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Chat as Bedrock Chatbot
    participant KB as Knowledge Base
    participant Bedrock as Claude 3.5 Sonnet
    participant MCP as Entry Content MCP
    participant Docs as Entry Docs
    
    User->>UI: Ask Entry Python question
    UI->>Chat: Process user query
    Chat->>KB: Retrieve relevant context
    KB->>KB: Vector similarity search
    KB-->>Chat: Return relevant documents
    Chat->>Bedrock: Generate response with context
    Bedrock-->>Chat: AI-generated answer
    Chat-->>UI: Display response
    UI-->>User: Show answer
    
    Note over User,Docs: Alternative: Direct API access
    User->>MCP: Query Entry block info
    MCP->>Docs: Load documentation
    Docs-->>MCP: Return block details
    MCP-->>User: Structured response
```
