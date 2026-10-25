#!/usr/bin/env python3
"""Smoke test PTY; usa soltanto la libreria standard Python."""
from __future__ import annotations

import fcntl
import os
import pathlib
import pty
import struct
import tempfile
import termios
import time

SCRIPT = str(pathlib.Path(__file__).resolve().parents[1] / "ai-bar-fm")
F3 = b"\x1bOR"
F4 = b"\x1bOS"
F5 = b"\x1b[15~"
F6 = b"\x1b[17~"
F7 = b"\x1b[18~"
F8 = b"\x1b[19~"
DOWN = b"\x1b[B"
UP = b"\x1b[A"
END = b"\x1b[F"
BACK = b"\x7f"
ENTER = b"\r"


class Session:
    def __init__(self, cwd: pathlib.Path):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execl(SCRIPT, SCRIPT, str(cwd))
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", 28, 96, 0, 0))
        os.set_blocking(self.fd, False)
        self.output = bytearray()
        self.drain(0.3)

    def drain(self, pause: float = 0.07):
        deadline = time.monotonic() + pause
        while time.monotonic() < deadline:
            try:
                data = os.read(self.fd, 65536)
                if data:
                    self.output.extend(data)
                    deadline = min(deadline + 0.005, time.monotonic() + 0.025)
                else:
                    break
            except BlockingIOError:
                time.sleep(0.005)
            except OSError:
                break

    def key(self, value: bytes):
        os.write(self.fd, value)
        self.drain()

    def type(self, text: str):
        for ch in text.encode("utf-8"):
            self.key(bytes([ch]))

    def close(self):
        self.key(b"q")
        for _ in range(50):
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid:
                os.close(self.fd)
                assert os.waitstatus_to_exitcode(status) == 0, f"Programma terminato con {status}"
                return
            time.sleep(0.02)
        os.kill(self.pid, 15)
        os.waitpid(self.pid, 0)
        os.close(self.fd)
        raise AssertionError("Il file manager non termina")


def fixture(root: pathlib.Path):
    source = root / "src"
    dest = root / "dest"
    source.mkdir()
    dest.mkdir()
    (source / "tree").mkdir()
    (source / "tree" / "deep.txt").write_text("profondo")
    (source / "alpha.txt").write_text("alpha")
    (source / "delete.txt").write_text("cancella")
    (source / "file space.txt").write_text("spazi")
    return source, dest


def test_copy_multiple():
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = fixture(pathlib.Path(tmp))
        s = Session(src)
        s.key(F3)        # tree/ (prima directory)
        s.key(DOWN)      # alpha.txt
        s.key(F3)
        s.key(F4)        # copia entrambi
        s.key(BACK)      # parent
        s.key(ENTER)     # dest (prima directory del parent)
        s.key(F6)
        s.close()
        assert (dst / "tree" / "deep.txt").read_text() == "profondo"
        assert (dst / "alpha.txt").read_text() == "alpha"
        assert (src / "alpha.txt").exists(), "Copia non deve spostare"


def test_cut_move():
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = fixture(pathlib.Path(tmp))
        s = Session(src)
        s.key(DOWN)      # alpha.txt
        s.key(F5)
        s.key(BACK)
        s.key(ENTER)
        s.key(F6)
        s.close()
        assert not (src / "alpha.txt").exists()
        assert (dst / "alpha.txt").read_text() == "alpha"


def test_mkdir_and_delete():
    with tempfile.TemporaryDirectory() as tmp:
        target = pathlib.Path(tmp)
        s = Session(target)
        s.key(F7)
        s.type("nuova")
        s.key(ENTER)
        assert (target / "nuova").is_dir(), "F7 non ha creato la directory"
        s.key(END)
        s.key(F8)
        s.type("s")
        s.key(ENTER)
        s.close()
        assert not (target / "nuova").exists(), "F8 non ha rimosso la directory"


def test_no_overwrite():
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = fixture(pathlib.Path(tmp))
        (dst / "alpha.txt").write_text("preesistente")
        s = Session(src)
        s.key(DOWN)
        s.key(F4)
        s.key(BACK)
        s.key(ENTER)
        s.key(F6)
        s.close()
        assert (dst / "alpha.txt").read_text() == "preesistente", "File sovrascritto!"


def test_filename_with_spaces():
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = fixture(pathlib.Path(tmp))
        s = Session(src)
        s.key(END)       # file space.txt
        s.key(F4)
        s.key(BACK)
        s.key(ENTER)
        s.key(F6)
        s.close()
        assert (dst / "file space.txt").read_text() == "spazi"


def test_delete_cancelled():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "keep.txt").write_text("intatto")
        s = Session(root)
        s.key(F8)
        s.type("n")
        s.key(ENTER)
        s.close()
        assert (root / "keep.txt").read_text() == "intatto"


def test_no_copy_into_self():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "folder").mkdir()
        s = Session(root)
        s.key(F4)        # copia folder
        s.key(ENTER)     # entra in folder
        s.key(F6)        # non deve fare folder/folder
        s.close()
        assert not (root / "folder" / "folder").exists()


if __name__ == "__main__":
    tests = [test_copy_multiple, test_cut_move, test_mkdir_and_delete, test_no_overwrite,
             test_filename_with_spaces, test_delete_cancelled, test_no_copy_into_self]
    for test in tests:
        test()
        print(f"OK {test.__name__}")
    print(f"{len(tests)} test superati")
