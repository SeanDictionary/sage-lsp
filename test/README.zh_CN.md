## LSP 测试指南 (pytest)

**中文 | [English](README.md)**

### 文件结构

- [lspclient.py](lspclient.py) - LSP 客户端封装（请求/通知，响应读取）
- [lspclientbase.py](lspclientbase.py) - LSP 客户端基类实现
- [conftest.py](conftest.py) - Pytest 配置与 fixture 定义
- [examples.py](examples.py) - 测试用例代码示例
- [color.py](color.py) - 终端颜色工具

#### 测试文件

- [test_lsp_server.py](test_lsp_server.py) - LSP 服务器初始化和基本功能测试
- [test_hover.py](test_hover.py) - Hover 悬停信息测试
- [test_definition.py](test_definition.py) - 跳转到定义测试
- [test_autopep8.py](test_autopep8.py) - 代码格式化测试 (autopep8)
- [test_pycodestyle.py](test_pycodestyle.py) - 代码风格检查测试 (pycodestyle)
- [test_pyflakes.py](test_pyflakes.py) - 代码检查测试 (pyflakes)
- [test_cython_utils.py](test_cython_utils.py) - Cython 工具测试

### 运行测试

```bash
pytest test/                                   # 运行全部测试
pytest test/ -v                                # 详细输出模式
pytest test/test_hover.py                      # 运行指定测试文件
pytest test/test_hover.py::test_hover          # 运行指定测试用例
pytest test/ -k "hover"                        # 运行匹配模式的测试
```

### 添加新测试

创建新的测试函数，使用 `client` fixture（自动启动/初始化/清理）：

```python
import pytest

code_text = """\
R = PolynomialRing(ZZ)
"""

def test_my_feature(client):
    uri = "file:///test.sage"

    # 打开文档
    client.did_open(
        uri=uri,
        text=code_text,
        language_id="sagemath",
        version=1,
    )

    # 测试你的功能
    response = client.hover(
        uri=uri,
        line=0,
        character=4,
    )

    assert response is not None
    print("\n响应:", response)

if __name__ == "__main__":
    pytest.main([__file__])
```

### LSPClient 快速参考

#### LSPClientBase 方法（低级）

- `initialize()` – 执行初始化握手
- `shutdown()` – 优雅关闭
- `send_request(method, params=None)` – 发送请求，返回请求 ID
- `send_notification(method, params=None)` – 发送通知
- `read_response(expected_id=None)` – 读取一条响应，自动跳过通知
- `start()` – 启动 LSP 服务器进程
- `stop()` – 停止 LSP 服务器进程

#### LSPClient 方法（高级）

- `did_open(uri, language_id, text, version=1)` – 通知服务器文档已打开
- `did_change(uri, text, version)` – 通知服务器文档已更改
- `hover(uri, line, character)` – 请求指定位置的 hover 信息
- `definition(uri, line, character)` – 请求定义位置
- `formatting(uri)` – 请求文档格式化编辑

**注意**：`client` fixture 会自动调用 `initialize()` 并处理 `shutdown()/stop()` 清理工作。
