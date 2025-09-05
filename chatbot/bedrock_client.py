import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aws_config.config import get_bedrock_client, get_bedrock_agent_runtime_client

class BedrockChatbot:
    def __init__(self):
        self.bedrock_client = get_bedrock_client()
        self.agent_runtime_client = get_bedrock_agent_runtime_client()
        self.knowledge_base_id = "9R38KN62YH"
        self.model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    def retrieve_from_kb(self, query, max_results=5):
        """Knowledge Base에서 관련 문서 검색"""
        try:
            response = self.agent_runtime_client.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={
                    'text': query
                },
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            
            contexts = []
            print(f"KB 검색 결과: {len(response['retrievalResults'])}개 문서 발견")
            for result in response['retrievalResults']:
                contexts.append(result['content']['text'])
            
            return contexts
        except Exception as e:
            print(f"KB 검색 오류: {str(e)}")
            return []
    
    def chat(self, message, max_tokens=1000):
        """Knowledge Base를 활용한 RAG 채팅 응답 생성"""
        try:
            # 1. Knowledge Base에서 관련 문서 검색
            contexts = self.retrieve_from_kb(message)
            
            # 2. 컨텍스트와 함께 프롬프트 구성
            if contexts:
                context_text = "\n\n".join(contexts)
                enhanced_message = f"""다음 문서들을 참고하여 질문에 답변해주세요:

<참고문서>
{context_text}
</참고문서>

질문: {message}

엔트리 파이썬 관련 질문이라면 위 문서의 정보를 바탕으로 정확하고 구체적인 답변을 해주세요. 코드 예시가 있다면 포함해주세요."""
            else:
                enhanced_message = message
            
            # 3. Bedrock으로 응답 생성
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": enhanced_message
                    }
                ],
                "temperature": 0.7
            })
            
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            return f"오류가 발생했습니다: {str(e)}"

if __name__ == "__main__":
    chatbot = BedrockChatbot()
    print("Bedrock 챗봇이 준비되었습니다!")
    
    while True:
        user_input = input("\n사용자: ")
        if user_input.lower() in ['quit', 'exit', '종료']:
            break
        
        response = chatbot.chat(user_input)
        print(f"챗봇: {response}")