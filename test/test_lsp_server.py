import pytest
code_text = """
x = 1 + 1
print(x)
"""


def test_hover(client):
    """测试 Hover 功能"""
    # 打开一个测试文档
    client.did_open(
        uri="file:///test.sage",
        language_id="sagemath",
        text=code_text
    )

if __name__ == "__main__":
    pytest.main([__file__])