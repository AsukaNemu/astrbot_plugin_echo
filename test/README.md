# Echo 插件本地测试环境

## 概述
这是一个完全模拟AstrBot运行环境的本地测试脚本，不需要完整安装AstrBot即可测试插件功能。

## 目录结构
```
test/
├── test_echo.py      # 主测试脚本，包含所有测试用例
├── run_test.sh       # 一键运行测试的脚本
└── README.md         # 本说明文档
```

## 快速开始
### 方式1：使用一键脚本
```bash
cd test
./run_test.sh
```

### 方式2：直接运行Python脚本
```bash
cd test
python test_echo.py
```

## 测试用例说明
当前测试脚本覆盖了以下场景：

1. **空输入测试**：测试用户只输入`/echo`不带参数的情况，验证是否正确返回用法提示。
2. **正常输入测试**：测试用户输入`/echo 内容`的情况，验证是否正确私发消息给用户。
3. **特殊字符测试**：测试包含各种特殊字符的输入，验证是否能正确处理和传递。
4. **前后空格测试**：测试内容前后包含空格的情况，验证是否能正确处理。

## 扩展测试
你可以修改`test_echo.py`文件，添加更多测试用例：

```python
async def test_your_custom_case():
    """自定义测试用例"""
    context = Context()
    plugin = EchoPlugin(context)
    
    event = AstrMessageEvent("/echo 你的测试内容")
    async for res in plugin.echo(event):
        # 处理返回结果
        pass
    
    # 验证发送的消息
    assert len(context.sent_messages) == 1
    # ... 更多验证逻辑
```

## 测试输出说明
- 每个测试用例会显示测试结果（✅ 通过 / ❌ 失败）
- 发送的消息会被打印出来，方便调试：`[发送消息] 类型: friend, 目标: test_user_123, 内容: xxx`
- 所有测试通过后会显示：`🎉 所有测试通过！插件功能正常。`

## 注意事项
- 测试环境完全模拟AstrBot的API，不需要安装任何额外依赖
- 测试不会发送真实的消息，所有消息都会被捕获并记录在`context.sent_messages`中
- 支持Python 3.7+版本
