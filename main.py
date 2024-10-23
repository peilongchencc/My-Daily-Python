import asyncio
import json
from daily import *
from fastapi import FastAPI, WebSocket
# FastAPI 是基于 Starlette 构建的，而 Starlette 是 FastAPI 背后的异步 Web 框架
from starlette.websockets import WebSocketState

# 初始化 Daily 环境
Daily.init()

# 创建 FastAPI 应用实例
app = FastAPI()

# 定义事件处理器类
class RoomHandler(EventHandler):
    def __init__(self):
        """初始化 RoomHandler 类，继承自 EventHandler 父类"""
        super().__init__()
        self.message_queue = None  # 初始化消息队列为空

    def set_queue(self, queue):
        """设置消息队列
        
        Args:
            queue (asyncio.Queue): 用于存放消息的队列
        """
        self.message_queue = queue

    def on_app_message(self, message, sender: str) -> None:
        """当收到应用消息时自动触发的事件处理方法
        
        Args:
            message (str): 收到的消息
            sender (str): 消息发送者
        """
        if self.message_queue:
            # 将消息放入队列，不阻塞当前任务
            self.message_queue.put_nowait(message)

def daily_call_init(conversation_id, handler=None):
    """初始化 Daily 会议
    
    Args:
        conversation_id (str): 会议室 ID
        handler (RoomHandler): 事件处理器实例
        
    Returns:
        CallClient: Daily 通话客户端实例
    """
    # 使用事件处理器创建通话客户端
    call_client = CallClient(event_handler=handler)
    # 设置用户名称
    call_client.set_user_name("listener")
    # 生成 Tavus 房间会议链接
    room_url = "https://tavus.daily.co/" + conversation_id
    print(f"完整的入会链接为:{room_url}")
    # 加入会议
    call_client.join(room_url)
    
    return call_client

# 定义 WebSocket 端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """处理 WebSocket 连接
    
    Args:
        websocket (WebSocket): WebSocket 连接对象
    """
    await websocket.accept()  # 接受 WebSocket 连接
    
    # 创建用于存放消息的异步队列
    message_queue = asyncio.Queue()
    
    # 创建 RoomHandler 实例，并将队列绑定到处理器
    room_handler = RoomHandler()
    room_handler.set_queue(message_queue)

    call_client = None  # 初始化为空，后续根据情况加入会议

    # 定义后台任务，用于从队列中发送消息
    async def send_messages():
        """后台任务，从消息队列中提取消息并发送到 WebSocket 客户端"""
        try:
            while True:
                # 从队列中获取消息
                message = await message_queue.get()
                # 终端输出内容，方便查询
                print(f"output:{message}, type:{type(message)}\n")
                # 将消息转换为 JSON 格式并保持中文字符
                message_str = json.dumps(message, ensure_ascii=False)
                # 通过 WebSocket 发送消息
                await websocket.send_text(message_str)
        except Exception as e:
            # 处理发送消息时的异常
            print(f"send_messages时出错: {e}")

    # 创建异步任务执行消息发送操作
    send_task = asyncio.create_task(send_messages())

    try:
        while True:
            # 等待 WebSocket 接收消息
            data = await websocket.receive_text()
            print(f"传入ws的数据为:{data},类型:{type(data)}")
            # 数据格式 conversation_id:c70ed8f4
            if data.startswith("conversation_id:"):
                # 从数据中提取 conversation_id
                conversation_id = data.split("conversation_id:")[1]
                # print(f"对话id为:{conversation_id}")
                # 如果已经存在会议客户端，先离开当前会议
                if call_client:
                    call_client.leave()
                # 创建新的会议客户端
                call_client = daily_call_init(conversation_id=conversation_id, handler=room_handler)
            elif data == "disconnect":
                # 离开会议
                if call_client:
                    call_client.leave()
                break
    except Exception as e:
        print(f"WebSocket 连接中的错误: {e}")
        if call_client:
            call_client.leave()
    finally:
        # 取消发送消息的后台任务
        send_task.cancel()
        # 检查 WebSocket 是否处于打开状态，避免重复关闭
        # 这一步是为了避免调用方手动关闭ws连接，导致重复关闭ws引发错误。
        if not websocket.client_state == WebSocketState.DISCONNECTED:
            try:
                # 关闭ws连接
                await websocket.close()
            except Exception as e:
                print(f"WebSocket关闭时出错: {e}")

# 主程序入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # 如果是IPv6方式，可以启用下列代码
    # uvicorn.run(app, host="::", port=8000)