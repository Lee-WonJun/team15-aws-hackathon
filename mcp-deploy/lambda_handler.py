import json

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'MCP Server is running',
            'path': event.get('path', '/'),
            'method': event.get('httpMethod', 'GET')
        })
    }
