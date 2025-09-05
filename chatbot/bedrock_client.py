import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aws_config.config import get_bedrock_client

class BedrockChatbot:
    def __init__(self):
        self.client = get_bedrock_client()
        self.model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    
    def chat(self, message, max_tokens=1000):
        """Bedrock을 통해 채팅 응답 생성"""
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": 0.7
            })
            
            response = self.client.invoke_model(
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