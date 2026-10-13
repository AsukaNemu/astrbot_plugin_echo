#!/usr/bin/env python3
"""
AstrBot Echo 插件本地测试脚本
不需要完整安装AstrBot即可测试插件功能
"""
import asyncio
import sys
from pathlib import Path
from typing import Any, List, Callable
from dataclasses import dataclass

# 首先模拟astrbot模块，这样不需要安装真实的astrbot
class MockAstrbotModule:
    class api:
        class event:
            class _Filter:
                @staticmethod
                def command(command: str) -> Callable:
                    """模拟命令过滤器装饰器"""
                    def decorator(func: Callable) -> Callable:
                        func._command = command
                        return func
                    return decorator

            filter = _Filter()

            @dataclass
            class AstrMessageEvent:
                """模拟消息事件"""
                message_str: str
                _sender_id: str = "test_user_123"
                _platform_id: str = "test_platform"
                message_type: str = "group"

                def get_sender_id(self) -> str:
                    """获取发送者ID"""
                    return self._sender_id

                def get_platform_id(self) -> str:
                    """获取平台ID"""
                    return self._platform_id

                def plain_result(self, content: str):
                    """返回普通文本结果"""
                    return {"type": "plain", "content": content}

            @dataclass
            class MessageChain:
                """模拟消息链"""
                messages: List[Any] = None

                def __post_init__(self):
                    if self.messages is None:
                        self.messages = []

                def message(self, content: str):
                    """添加文本消息"""
                    self.messages.append({"type": "text", "content": content})
                    return self

        class platform:
            class MessageType:
                """模拟消息类型"""
                FRIEND_MESSAGE = "friend"
                GROUP_MESSAGE = "group"

        class star:
            @dataclass
            class Context:
                """模拟插件上下文"""
                config: dict = None
                sent_messages: List[dict] = None

                def __post_init__(self):
                    if self.config is None:
                        self.config = {}
                    if self.sent_messages is None:
                        self.sent_messages = []

                async def send_message(self, session, message):
                    """模拟发送消息"""
                    self.sent_messages.append({
                        "session": session,
                        "message": message
                    })
                    # 打印发送的消息，方便调试
                    content = "".join([m["content"] for m in message.messages if m["type"] == "text"])
                    print(f"[发送消息] 类型: {session.message_type}, 目标: {session.target_id}, 内容: {content}")

            class Star:
                """模拟插件基类"""
                def __init__(self, context: 'api.star.Context'):
                    self.context = context

    class core:
        class platform:
            @dataclass
            class message_session:
                @dataclass
                class MessageSession:
                    """模拟消息会话"""
                    platform_id: str
                    message_type: str
                    target_id: str
                    group_id: str = None

# 注入模拟的astrbot模块到sys.modules
sys.modules['astrbot'] = MockAstrbotModule()
sys.modules['astrbot.api'] = MockAstrbotModule.api
sys.modules['astrbot.api.event'] = MockAstrbotModule.api.event
sys.modules['astrbot.api.platform'] = MockAstrbotModule.api.platform
sys.modules['astrbot.api.star'] = MockAstrbotModule.api.star
sys.modules['astrbot.core'] = MockAstrbotModule.core
sys.modules['astrbot.core.platform'] = MockAstrbotModule.core.platform
sys.modules['astrbot.core.platform.message_session'] = MockAstrbotModule.core.platform.message_session

# 现在可以导入我们的插件了
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import EchoPlugin

# 导入模拟的类，方便测试使用
from astrbot.api.platform import MessageType
from astrbot.api.event import AstrMessageEvent, MessageChain
from astrbot.api.star import Context
from astrbot.core.platform.message_session import MessageSession

async def test_echo_empty():
    """测试空输入情况"""
    print("\n=== 测试1: 空输入 ===")
    context = Context()
    plugin = EchoPlugin(context)

    event = AstrMessageEvent("/echo")
    result = plugin.echo(event)

    # 获取异步生成器的返回值
    response = None
    async for res in result:
        response = res
        break

    assert response is not None, "应该返回用法提示"
    assert response["content"] == "用法: /echo <要私发的内容>", "用法提示不正确"
    assert len(context.sent_messages) == 0, "空输入不应该发送私发消息"
    print("✅ 空输入测试通过")

async def test_echo_normal():
    """测试正常输入情况"""
    print("\n=== 测试2: 正常输入 ===")
    context = Context()
    plugin = EchoPlugin(context)

    test_content = "这是测试内容"
    event = AstrMessageEvent(f"/echo {test_content}")
    result = plugin.echo(event)

    # 执行生成器
    async for res in result:
        pass

    # 等待异步操作完成
    await asyncio.sleep(0.1)

    assert len(context.sent_messages) == 1, "应该发送一条私发消息"
    sent_msg = context.sent_messages[0]
    assert sent_msg["session"].message_type == MessageType.FRIEND_MESSAGE, "应该是私发消息"
    assert sent_msg["session"].target_id == event.get_sender_id(), "应该发送给消息发送者"

    msg_content = "".join([m["content"] for m in sent_msg["message"].messages if m["type"] == "text"])
    assert msg_content == test_content, "消息内容不匹配"
    print(f"✅ 正常输入测试通过，发送内容: {msg_content}")

async def test_echo_special_chars():
    """测试特殊字符输入"""
    print("\n=== 测试3: 特殊字符输入 ===")
    context = Context()
    plugin = EchoPlugin(context)

    test_content = "测试特殊字符!@#$%^&*()_+-=[]{}|;:'\",.<>?/~`"
    event = AstrMessageEvent(f"/echo {test_content}")
    result = plugin.echo(event)

    async for res in result:
        pass

    await asyncio.sleep(0.1)

    assert len(context.sent_messages) == 1
    msg_content = "".join([m["content"] for m in context.sent_messages[0]["message"].messages if m["type"] == "text"])
    assert msg_content == test_content, "特殊字符处理不正确"
    print(f"✅ 特殊字符测试通过，发送内容: {msg_content}")

async def test_echo_with_extra_spaces():
    """测试前后有空格的输入"""
    print("\n=== 测试4: 前后空格输入 ===")
    context = Context()
    plugin = EchoPlugin(context)

    test_content = "  前后有空格的内容  "
    event = AstrMessageEvent(f"/echo {test_content}")
    result = plugin.echo(event)

    async for res in result:
        pass

    await asyncio.sleep(0.1)

    assert len(context.sent_messages) == 1
    msg_content = "".join([m["content"] for m in context.sent_messages[0]["message"].messages if m["type"] == "text"])
    assert msg_content == test_content.strip(), "前后空格应该被保留？"  # 原代码中strip()只作用于整个参数，内容中的空格会保留
    print(f"✅ 前后空格测试通过，发送内容: '{msg_content}'")

async def main():
    """运行所有测试"""
    print("开始测试 Echo 插件...")

    try:
        await test_echo_empty()
        await test_echo_normal()
        await test_echo_special_chars()
        await test_echo_with_extra_spaces()

        print("\n🎉 所有测试通过！插件功能正常。")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
