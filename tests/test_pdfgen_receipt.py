import os
import types
import pytest
import subprocess
import sys

import pdfgen_receipt as pr


def test_get_jpg_files_missing_dir():
    with pytest.raises(pr.ImageNotFoundError):
        pr.get_jpg_files("nonexistent_dir_for_tests")


def test_get_jpg_files_wrong_count(tmp_path):
    d = tmp_path / "images"
    d.mkdir()
    # create 3 jpg files (should be 4)
    for i in range(3):
        (d / f"img{i}.jpg").write_text("x")

    with pytest.raises(pr.ImageNotFoundError):
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


def test_main_creates_pdf_with_canvas(tmp_path, monkeypatch):
    """Test main() function creates PDF with canvas operations."""
    # Setup: create 4 dummy JPG images
    img_dir = tmp_path / "image_resources"
    img_dir.mkdir()
    for i in range(4):
        (img_dir / f"img{i}.jpg").write_text("x")

    # Setup: mock canvas.Canvas to track calls
    canvas_calls = []

    class MockCanvas:
        def __init__(self, filename, pagesize):
            self.filename = filename
            self.pagesize = pagesize
            canvas_calls.append(("Canvas.__init__", filename, pagesize))

        def showPage(self):
            canvas_calls.append(("showPage",))

        def save(self):
            canvas_calls.append(("save",))

        def line(self, x1, y1, x2, y2):
            canvas_calls.append(("line", x1, y1, x2, y2))

        def drawImage(self, path, x, y, width, height):
            canvas_calls.append(("drawImage", path))

        def setLineWidth(self, w):
            pass

        def setStrokeColor(self, c):
            pass

        def rect(self, x, y, w, h):
            pass

    # Patch canvas.Canvas
    monkeypatch.setattr(pr.canvas, "Canvas", MockCanvas)
    # Patch get_jpg_files to return our test images
    monkeypatch.setattr(
        pr,
        "get_jpg_files",
        lambda d: [f"img{i}.jpg" for i in range(4)],
    )
    # Patch current directory to use temp directory
    monkeypatch.chdir(tmp_path)

    # Execute: call main()
    pr.main()

    # Verify: Canvas was created, pages added, and saved
    assert any("Canvas.__init__" in str(c) for c in canvas_calls)
    assert any("showPage" in str(c) for c in canvas_calls)
    assert any("save" in str(c) for c in canvas_calls)
    assert canvas_calls.count(("showPage",)) == 1, "showPage should be called once"


def test_main_calls_create_page_twice(tmp_path, monkeypatch):
    """Test main() function calls create_page() twice for two pages."""
    # Setup: create 4 dummy JPG images
    img_dir = tmp_path / "image_resources"
    img_dir.mkdir()
    for i in range(4):
        (img_dir / f"img{i}.jpg").write_text("x")

    # Track create_page calls
    create_page_calls = []

    def fake_create_page(c, img1, img2):
        create_page_calls.append((img1, img2))

    class MockCanvas:
        def __init__(self, filename, pagesize):
            pass

        def showPage(self):
            pass

        def save(self):
            pass

    # Mock create_page
    monkeypatch.setattr(pr, "create_page", fake_create_page)
    # Mock canvas.Canvas
    monkeypatch.setattr(pr.canvas, "Canvas", MockCanvas)
    # Patch get_jpg_files
    monkeypatch.setattr(
        pr,
        "get_jpg_files",
        lambda d: ["img0.jpg", "img1.jpg", "img2.jpg", "img3.jpg"],
    )
    # Patch current directory
    monkeypatch.chdir(tmp_path)

    # Execute
    pr.main()

    # Verify: create_page called twice with correct images
    assert len(create_page_calls) == 2
    # First call: images 0 and 1
    assert "img0.jpg" in create_page_calls[0][0]
    assert "img1.jpg" in create_page_calls[0][1]
    # Second call: images 2 and 3
    assert "img2.jpg" in create_page_calls[1][0]
    assert "img3.jpg" in create_page_calls[1][1]


def test_main_logging_info_calls(tmp_path, monkeypatch, caplog):
    """Test main() function logs appropriate info messages."""
    import logging

    # Setup
    img_dir = tmp_path / "image_resources"
    img_dir.mkdir()
    for i in range(4):
        (img_dir / f"img{i}.jpg").write_text("x")

    class MockCanvas:
        def __init__(self, filename, pagesize):
            pass

        def showPage(self):
            pass

        def save(self):
            pass

    # Mock the expensive operations
    monkeypatch.setattr(pr, "create_page", lambda c, i1, i2: None)
    monkeypatch.setattr(pr.canvas, "Canvas", MockCanvas)
    monkeypatch.setattr(
        pr,
        "get_jpg_files",
        lambda d: ["img0.jpg", "img1.jpg", "img2.jpg", "img3.jpg"],
    )
    monkeypatch.chdir(tmp_path)

    # Execute with captured logs
    with caplog.at_level(logging.INFO):
        pr.main()

    # Verify: Check that expected log messages were written
    log_text = caplog.text
    assert "Dir name" in log_text or "image_resources" in log_text
    assert "PDF file name" in log_text or "2026_q_receipt.pdf" in log_text
    assert "creating page 1" in log_text or "creating page 2" in log_text or "new page added" in log_text


def test_script_entry_point(tmp_path, monkeypatch):
    """Test the run_pdf_generator() entry point function."""
    import logging

    # Setup: create 4 dummy JPG images
    img_dir = tmp_path / "image_resources"
    img_dir.mkdir()
    for i in range(4):
        (img_dir / f"img{i}.jpg").write_text("x")

    # Mock input() to prevent blocking
    monkeypatch.setattr("builtins.input", lambda: "")

    # Mock write_custom_log
    log_writes = []

    def fake_write_custom_log(msg):
        log_writes.append(msg)

    monkeypatch.setattr(pr, "write_custom_log", fake_write_custom_log)

    # Mock main() to verify it's called
    main_called = []

    def fake_main():
        main_called.append(True)

    monkeypatch.setattr(pr, "main", fake_main)

    # Change to temp directory
    monkeypatch.chdir(tmp_path)

    # Call the entry point function
    pr.run_pdf_generator()

    # Verify: entry point function executed
    assert len(main_called) == 1, "main() should be called once"
    assert len(log_writes) == 2, "write_custom_log should be called twice (start and end)"
    assert "Starting" in log_writes[0]
    assert "Completed" in log_writes[1]

