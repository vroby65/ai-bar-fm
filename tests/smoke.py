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
    def __init__(self, cwd: pathlib.Path, cols: int = 96, env: dict[str, str] | None = None):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.environ["TERM"] = "xterm-256color"
            os.environ["LC_ALL"] = "C.UTF-8"
            os.environ.pop("NO_COLOR", None)
            os.environ.pop("ABFM_NO_COLOR", None)
            os.environ.pop("ABFM_ASCII", None)
            if env:
                os.environ.update(env)
            os.execl(SCRIPT, SCRIPT, str(cwd))
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", 28, cols, 0, 0))
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

    def mouse(self, button: int, x: int, y: int, release: bool = False):
        suffix = 'm' if release else 'M'
        self.key(f"\x1b[<{button};{x};{y}{suffix}".encode())

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


def test_mouse_double_click_opens_folder():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "folder").mkdir()
        s = Session(root)
        try:
            assert b"\x1b[?1000h\x1b[?1006h" in s.output, "Mouse non attivato"
            assert "┌".encode() in s.output, "Cornici Unicode mancanti"
            assert b"\x1b[0;37;44m" in s.output, "Palette classica MC mancante"
            s.mouse(0, 10, 5)
            s.mouse(0, 10, 5)
            s.key(F7)
            s.type("mouse-created")
            s.key(ENTER)
            assert (root / "folder" / "mouse-created").is_dir(), "Doppio click non apre"
        finally:
            s.close()


def test_mouse_button_mkdir():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        s = Session(root)
        try:
            s.mouse(0, 60, 25)
            s.type("button-made")
            s.key(ENTER)
            assert (root / "button-made").is_dir(), "F7 via mouse non funziona"
        finally:
            s.close()


def test_mouse_prompt_ignores_click():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        s = Session(root)
        try:
            s.key(F7)
            s.mouse(0, 10, 8)
            s.type("clean-name")
            s.key(ENTER)
            assert (root / "clean-name").is_dir(), "Mouse ha corrotto il prompt"
        finally:
            s.close()


def test_mouse_mark_copy():
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = fixture(pathlib.Path(tmp))
        s = Session(src)
        try:
            s.mouse(0, 3, 6)
            s.key(F4)
            s.key(BACK)
            s.key(ENTER)
            s.key(F6)
            assert (dst / "alpha.txt").read_text() == "alpha", "Selezione mouse non funziona"
        finally:
            s.close()


def test_mouse_compact_bar_and_wheel():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        for i in range(30):
            (root / f"d{i:02d}").mkdir()
        s = Session(root, cols=40)
        try:
            s.mouse(0, 27, 25)
            s.type("small-window")
            s.key(ENTER)
            assert (root / "small-window").is_dir(), "F7 non cliccabile su finestra stretta"
            for _ in range(28):
                s.mouse(65, 10, 10)
            assert b"d25" in s.output[-2500:], "Rotella non porta ai file piu' in basso"
        finally:
            s.close()



def test_mc_palette_and_highlighting():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "dir").mkdir()
        (root / "regular.txt").write_text("text")
        exe = root / "executable.sh"
        exe.write_text("#!/bin/sh\nexit 0\n")
        exe.chmod(0o755)
        (root / "shortcut").symlink_to("regular.txt")
        (root / "broken").symlink_to("does-not-exist")
        s = Session(root)
        try:
            out = bytes(s.output)
            assert b"\x1b[0;37;44m" in out, "Sfondo blu / grigio mancante"
            assert b"\x1b[0;30;46m" in out, "Selezione nero / ciano mancante"
            assert b"\x1b[1;37;44m" in out, "Directory bianche mancanti"
            assert b"\x1b[1;32;44m" in out, "Eseguibili verdi mancanti"
            assert b"\x1b[0;36;44m" in out, "Link ciano mancanti"
            assert b"\x1b[1;31;44m" in out, "Link interrotti rossi mancanti"
            assert b"\x1b[0;37;40m" in out, "Barra nera comandi mancante"
            s.key(F3)
            assert b"\x1b[1;33;46m" in s.output, "Selezione marcata gialla mancante"
        finally:
            s.close()


def test_no_color_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        s = Session(pathlib.Path(tmp), env={"ABFM_NO_COLOR": "1"})
        try:
            assert b"\x1b[0;37;44m" not in s.output
            assert b"\x1b[0;30;46m" not in s.output
            assert b"\x1b[0;37;40m" not in s.output
            assert "┌".encode() in s.output
        finally:
            s.close()


def test_ascii_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        s = Session(pathlib.Path(tmp), env={"ABFM_ASCII": "1"})
        try:
            assert b"+" + b"-" * 94 + b"+" in s.output
            assert "┌".encode() not in s.output
        finally:
            s.close()

if __name__ == "__main__":
    tests = [test_copy_multiple, test_cut_move, test_mkdir_and_delete, test_no_overwrite,
             test_filename_with_spaces, test_delete_cancelled, test_no_copy_into_self,
             test_mouse_double_click_opens_folder, test_mouse_button_mkdir,
             test_mouse_prompt_ignores_click, test_mouse_mark_copy,
             test_mouse_compact_bar_and_wheel, test_mc_palette_and_highlighting,
             test_no_color_fallback, test_ascii_fallback]
    for test in tests:
        test()
        print(f"OK {test.__name__}")
    print(f"{len(tests)} test superati")
