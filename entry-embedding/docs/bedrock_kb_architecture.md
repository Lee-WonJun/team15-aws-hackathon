# AWS Bedrock Knowledge Base 기반 엔트리 파이썬 RAG 아키텍처

## 🏗️ 전체 아키텍처

```
JSON 문서 → S3 텍스트 파일 → Bedrock KB → OpenSearch Serverless → RAG 답변
```

## 📋 구현 단계

### 1단계: 데이터 준비
```python
# JSON → 개별 텍스트 파일 변환
for doc in entry_python_docs:
    content = f"{doc['title']}\n{doc['content']}"
    s3.put_object(Bucket='entry-python-kb', Key=f"{doc['id']}.txt", Body=content)
```

### 2단계: Knowledge Base 생성
- **임베딩 모델**: Amazon Titan Embed Text v1
- **벡터 저장소**: OpenSearch Serverless
- **데이터 소스**: S3 버킷

### 3단계: 자동 임베딩 및 인덱싱
```python
# Bedrock이 자동으로 처리
bedrock_agent.start_ingestion_job(knowledgeBaseId=kb_id)
```

### 4단계: RAG 쿼리
```python
# 한 번의 API 호출로 검색 + 답변 생성
response = bedrock_agent_runtime.retrieve_and_generate(
    input={'text': '마우스 클릭 확인하는 코드는?'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': kb_id,
            'modelArn': 'claude-3-sonnet'
        }
    }
)
```

## 🎯 Bedrock KB vs 직접 구현 비교

| 항목 | Bedrock KB | 직접 구현 |
|------|------------|-----------|
| **임베딩** | 자동 처리 | 수동 API 호출 |
| **벡터 저장** | 관리형 OpenSearch | 직접 관리 |
| **검색 + 생성** | 통합 API | 별도 구현 |
| **확장성** | 자동 스케일링 | 수동 관리 |
| **비용** | 사용량 기반 | 인프라 비용 |

## 💡 엔트리 파이썬 RAG 최적화

### 메타데이터 활용
```python
# 문서에 구조화된 메타데이터 추가
metadata = {
    "category": "visibility",
    "block_id": "show", 
    "python_syntax": "Entry.show()",
    "difficulty": "beginner"
}
```

### 청킹 전략
```python
# 블록별로 개별 문서 생성
# 카테고리별 요약 문서 추가
# FAQ는 Q&A 단위로 분할
```

### 프롬프트 엔지니어링
```python
system_prompt = """
당신은 엔트리 파이썬 전문가입니다.
- 블록 코딩을 Python으로 변환하는 방법을 설명하세요
- 실제 사용 가능한 코드 예시를 제공하세요
- 초보자도 이해할 수 있게 단계별로 설명하세요
"""
```

## 🚀 배포 및 운영

### CloudFormation 템플릿
```yaml
Resources:
  EntryPythonKB:
    Type: AWS::Bedrock::KnowledgeBase
    Properties:
      Name: entry-python-kb
      RoleArn: !GetAtt BedrockKBRole.Arn
      KnowledgeBaseConfiguration:
        Type: VECTOR
        VectorKnowledgeBaseConfiguration:
          EmbeddingModelArn: !Sub 'arn:aws:bedrock:${AWS::Region}::foundation-model/amazon.titan-embed-text-v1'
```

### API Gateway + Lambda
```python
def lambda_handler(event, context):
    question = event['body']['question']
    answer = bedrock_agent_runtime.retrieve_and_generate(
        input={'text': question},
        retrieveAndGenerateConfiguration={...}
    )
    return {'answer': answer['output']['text']}
```

## 📊 예상 성능 및 비용

- **응답 시간**: 2-5초
- **정확도**: 85-95% (도메인 특화)
- **월 비용**: $50-200 (1000 쿼리 기준)
- **확장성**: 무제한

이 방식으로 구현하면 복잡한 벡터 DB 관리 없이도 고품질 RAG 시스템을 빠르게 구축할 수 있습니다!