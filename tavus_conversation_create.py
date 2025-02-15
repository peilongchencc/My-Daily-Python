"""
Description: tavus对话创建。
Notes: 
"""
import requests

headers = {
    "x-api-key": "your-api-key",
    "Content-Type": "application/json"
}

#################
# 配置人物上下文
#################

generated_prompt = (
    "你将扮演一个智能的旅游咨询助手，基于已有的旅游路线和景点信息，为用户提供简洁、精准的建议。无论用户的问题是详细或宽泛，如‘去哪玩’，你都应通过逐步引导式提问，让用户提供具体的兴趣和偏好、餐饮和住宿需求。"
    )

# 会话参数
payload = {
    "replica_id": "r79e1c033f", # 虚拟人的形象
    "persona_id": "p74f1ca8",   # 虚拟人认知能力
    # "callback_url": "https://yourwebsite.com/webhook",
    "conversation_name": "世界旅游问答",
    # "conversational_context": "You are about to talk to people who are interested in traveling in Fangshan district of Beijing.",
    "conversational_context": generated_prompt,
    "custom_greeting": "你好,我是您的智能的旅游咨询助手，有什么我可以帮您的?",
    "properties": {
        "max_call_duration": 3600,
        "participant_left_timeout": 180,
        "participant_absent_timeout": 300,
        # "enable_recording": True,
        "enable_transcription": True,
        # "apply_greenscreen": True,
        "language": "chinese", #english
        # "recording_s3_bucket_name": "conversation-recordings",
        # "recording_s3_bucket_region": "us-east-1",
        # "aws_assume_role_arn": ""
    }
}

# 生成会话 create conversation 
response = requests.request("POST", "https://tavusapi.com/v2/conversations", json=payload, headers=headers)

# 查看会话url、conversation_id
print(response.text)