from astrbot.api.event import filter, AstrMessageEvent, MessageChain
from astrbot.api.platform import MessageType
from astrbot.api.star import Context, Star
from astrbot.core.platform.message_session import MessageSession


class EchoPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("echo")
    async def echo(self, event: AstrMessageEvent):
        """/echo <内容> - 将内容私发给发送者"""
        content = event.message_str.removeprefix("/echo").strip()
        if not content:
            yield event.plain_result("用法: /echo <要私发的内容>")
            return

        session = MessageSession(
            event.get_platform_id(),
            MessageType.FRIEND_MESSAGE,
            event.get_sender_id(),
        )
        await self.context.send_message(session, MessageChain().message(content))
