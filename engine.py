from __future__ import annotations

import json
import os
import random
import select
import shutil
import sys
import time
from contextlib import contextmanager
from pathlib import Path

IS_WINDOWS = os.name == "nt"

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
GRAY = "\033[90m"


def ansi(code: str) -> str:
    return f"\033[{code}m"


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def clear() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def home() -> None:
    sys.stdout.write("\033[H")


def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def enter_alt_screen() -> None:
    sys.stdout.write("\033[?1049h\033[2J\033[H")
    sys.stdout.flush()


def leave_alt_screen() -> None:
    sys.stdout.write("\033[?1049l")
    sys.stdout.flush()


def term_size() -> tuple[int, int]:
    s = shutil.get_terminal_size((100, 30))
    return s.columns, s.lines


def centered(lines: list[str], min_width: int = 0) -> str:
    cols, rows = term_size()
    width = max(min_width, max((visible_len(x) for x in lines), default=0))
    top = max(0, (rows - len(lines)) // 2)
    out = [""] * top
    for line in lines:
        pad = max(0, (cols - width) // 2)
        out.append(" " * pad + line)
    return "\n".join(out)


def visible_len(text: str) -> int:
    # Good enough for our own ANSI sequences and mostly single-width characters.
    import re
    return len(re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text))


def frame(lines: list[str]) -> None:
    sys.stdout.write("\033[H" + "\n".join(lines) + "\033[J")
    sys.stdout.flush()


def box(title: str, body: list[str], width: int = 64) -> list[str]:
    inner = width - 2
    top = "╭" + "─" * inner + "╮"
    bottom = "╰" + "─" * inner + "╯"
    title_text = f" {title} "
    if len(title_text) < inner:
        left = (inner - len(title_text)) // 2
        top = "╭" + "─" * left + title_text + "─" * (inner - left - len(title_text)) + "╮"
    lines = [top]
    for raw in body:
        plain = visible_len(raw)
        lines.append("│" + raw + " " * max(0, inner - plain) + "│")
    lines.append(bottom)
    return lines


class KeyReader:
    def __init__(self) -> None:
        self._old_settings = None

    def start(self) -> None:
        if IS_WINDOWS:
            return
        if not sys.stdin.isatty():
            return
        import termios
        import tty
        self._old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    def stop(self) -> None:
        if IS_WINDOWS or self._old_settings is None:
            return
        import termios
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
        self._old_settings = None

    def read(self, timeout: float | None = None) -> str | None:
        if IS_WINDOWS:
            import msvcrt
            start = time.monotonic()
            while True:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ("\x00", "\xe0"):
                        code = msvcrt.getwch()
                        return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT"}.get(code, "")
                    if ch == "\r":
                        return "ENTER"
                    if ch == "\x1b":
                        return "ESC"
                    if ch == "\x08":
                        return "BACKSPACE"
                    return ch
                if timeout is not None and time.monotonic() - start >= timeout:
                    return None
                time.sleep(0.004)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return None
        ch = sys.stdin.read(1)
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x7f":
            return "BACKSPACE"
        if ch == "\x1b":
            # ANSI arrow sequences. Tiny non-blocking grace period for the rest.
            seq = ""
            end = time.monotonic() + 0.015
            while time.monotonic() < end:
                r, _, _ = select.select([sys.stdin], [], [], 0)
                if not r:
                    time.sleep(0.001)
                    continue
                seq += sys.stdin.read(1)
                if len(seq) >= 2:
                    break
            if seq.startswith("[") and len(seq) >= 2:
                return {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT"}.get(seq[1], "ESC")
            return "ESC"
        return ch


@contextmanager
def terminal_session():
    key = KeyReader()
    try:
        if IS_WINDOWS:
            # Enable ANSI on supported Windows consoles.
            os.system("")
        enter_alt_screen()
        hide_cursor()
        key.start()
        yield key
    finally:
        key.stop()
        show_cursor()
        leave_alt_screen()


def data_dir() -> Path:
    if IS_WINDOWS:
        base = Path(os.getenv("APPDATA") or Path.home())
        p = base / "TerminalArcade"
    elif sys.platform == "darwin":
        p = Path.home() / "Library" / "Application Support" / "TerminalArcade"
    else:
        p = Path.home() / ".terminal_arcade"
    p.mkdir(parents=True, exist_ok=True)
    return p


class SaveData:
    def __init__(self) -> None:
        self.path = data_dir() / "save.json"
        self.data = {"best": {}, "rolling_unlocked": 1, "games_played": 0}
        self.load()

    def load(self) -> None:
        try:
            loaded = json.loads(self.path.read_text("utf-8"))
            if isinstance(loaded, dict):
                self.data.update(loaded)
        except Exception:
            pass

    def save(self) -> None:
        try:
            self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), "utf-8")
        except Exception:
            pass

    def best(self, game: str, default: int = 0) -> int:
        try:
            return int(self.data.get("best", {}).get(game, default))
        except Exception:
            return default

    def set_best(self, game: str, score: int, lower_is_better: bool = False) -> bool:
        scores = self.data.setdefault("best", {})
        old = scores.get(game)
        improved = old is None or (score < old if lower_is_better else score > old)
        if improved:
            scores[game] = int(score)
            self.save()
        return improved

    def increment_played(self) -> None:
        self.data["games_played"] = int(self.data.get("games_played", 0)) + 1
        self.save()

    @property
    def rolling_unlocked(self) -> int:
        return max(1, min(500, int(self.data.get("rolling_unlocked", 1))))

    def unlock_rolling(self, stage: int) -> None:
        self.data["rolling_unlocked"] = max(self.rolling_unlocked, min(500, stage))
        self.save()


def sleep_countdown(key: KeyReader, seconds: int = 3, title: str = "READY") -> bool:
    for n in range(seconds, 0, -1):
        frame(box(title, ["", f"{' ' * 27}{BOLD}{n}{RESET}", "", "ESC : cancel"], 62))
        end = time.monotonic() + 1
        while time.monotonic() < end:
            k = key.read(0.05)
            if k == "ESC":
                return False
    return True


def wait_key(key: KeyReader, message: str = "Press ENTER to return") -> None:
    while True:
        k = key.read(None)
        if k in ("ENTER", "ESC", "q", "Q"):
            return


def rand_choice(seq):
    return seq[random.randrange(len(seq))]
