
from image_annotation_gui.main import hello_world


def test_hello_world():
    result = hello_world()
    assert result is not None
    assert "hello" in result.lower()
    assert "world" in result.lower()