"""
Description: 配置tavus虚拟人认知能力。
Notes: 
虚拟人认知能力创建一次即可，不必多次创建。
"""
import requests

headers = {
    "x-api-key": "your-api-key",
    "Content-Type": "application/json"
}

#################
# 配置虚拟人认知能力
#################
data = {
    "persona_name": "tour_assistant",
    "default_replica_id": "r79e1c033f",
    "system_prompt": "你将扮演一个智能的旅游咨询助手，你将会使用context内的信息热情的回答用户的问题，请保持使用中文.",
    "layers": {
        "vqa": {
            "enable_vision": False # 表示是否开启视频问答，通过摄像头会对用户所处环境进行描述，然后解答。例如用户穿着白色夹克，带着AirPods等等。
        },
        "llm": {
            "model": "tavus-gpt-4o"
        },
        "stt": {
            "stt_engine": "tavus-advanced"
        },
        # "tts": {
        #     "api_key": "your-api-key",
        #     "tts_engine": "cartesia",
        #     "external_voice_id": "external-voice-id",
        #     "voice_settings": {
        #         "speed": "normal",
        #         "emotion": ["positivity:high", "curiosity"]
        #     },
        #     "playht_user_id": "your-playht-user-id"
        # },
    },
    "context": "世界旅游指南: 法国巴黎：著名的埃菲尔铁塔、卢浮宫和凯旋门，浪漫之都吸引了来自世界各地的游客。巴黎也以美食和时尚著称。中国北京：长城、故宫和天坛是北京的代表性景点，传统文化与现代化城市的结合让北京成为热门旅游城市。美国纽约：自由女神像、中央公园和时代广场是纽约的标志性景点。纽约还以百老汇和多元文化闻名，是一座永不眠的城市。"
}

# 创建虚拟人
response = requests.post('https://tavusapi.com/v2/personas', headers=headers, json=data)
# 获取虚拟人id
psn_id = response.json()["persona_id"]
print(psn_id)