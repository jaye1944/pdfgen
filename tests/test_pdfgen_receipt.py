import os
import types
import pytest

import pdfgen_receipt as pr


def test_get_jpg_files_missing_dir():
    with pytest.raises(SystemExit):
        pr.get_jpg_files("nonexistent_dir_for_tests")


def test_get_jpg_files_wrong_count(tmp_path):
    d = tmp_path / "images"
    d.mkdir()
    # create 3 jpg files (should be 4)
    for i in range(3):
        (d / f"img{i}.jpg").write_text("x")

    with pytest.raises(SystemExit):
        pr.get_jpg_files(str(d))


def test_get_jpg_files_success(tmp_path):
    d = tmp_path / "images"
    d.mkdir()
    names = [f"img{i}.jpg" for i in range(4)]
    for n in names:
        (d / n).write_text("x")

    result = pr.get_jpg_files(str(d))
    assert isinstance(result, list)
    assert set(result) == set(names)
    assert len(result) == 4


def test_add_image_with_border_calls_canvas_methods():
    class MockCanvas:
        def __init__(self):
            self.calls = []

        def drawImage(self, path, x, y, width, height):
            self.calls.append(("drawImage", path, x, y, width, height))

        def setLineWidth(self, w):
            self.calls.append(("setLineWidth", w))

        def setStrokeColor(self, c):
            self.calls.append(("setStrokeColor", c))

        def rect(self, x, y, w, h):
            self.calls.append(("rect", x, y, w, h))

    mc = MockCanvas()
    pr.add_image_with_border(mc, "some_image.jpg", 1, 2, 3, 4)

    names = [c[0] for c in mc.calls]
    assert "drawImage" in names
    assert "rect" in names


def test_create_page_calls_line_and_add_image_with_border(monkeypatch):
    recorded = []

    def fake_add(c, path, x, y, w, h):
        recorded.append((path, x, y, w, h))

    monkeypatch.setattr(pr, "add_image_with_border", fake_add)

    class MockCanvas:
        def __init__(self):
            self.line_calls = []

        def line(self, x1, y1, x2, y2):
            self.line_calls.append((x1, y1, x2, y2))

    mc = MockCanvas()
    pr.create_page(mc, "a.jpg", "b.jpg")

    assert mc.line_calls, "line was not called"
    width, height = pr.A4
    assert mc.line_calls[0] == (0, height / 2, width, height / 2)

    margin = 15 * pr.mm
    # first image placed at top half, second in bottom half
    assert recorded[0][0] == "a.jpg"
    assert recorded[1][0] == "b.jpg"
    assert recorded[0][1] == margin
    assert recorded[1][1] == margin
    assert recorded[0][2] == (height / 2) + margin
    assert recorded[1][2] == margin


def test_custom_formatter_formats_time():
    fmt = pr.CustomFormatter()

    class R:
        pass

    r = R()
    # 2021-01-01 00:00:00 with .123 seconds
    r.created = 1609459200.123
    r.msecs = 123

    s = fmt.formatTime(r, datefmt="%Y-%m-%d %H:%M:%S")
    assert s.endswith(".123")

    s2 = fmt.formatTime(r)
    assert s2.endswith(".123")


def test_write_custom_log_writes_file(tmp_path, monkeypatch):
    f = tmp_path / "mylog.log"
    monkeypatch.setattr(pr, "log_file_name", str(f))
    pr.write_custom_log("hello world")
    assert f.read_text().strip() == "hello world"
