from __future__ import annotations

import argparse
import os
import platform
import sys

from engine import BOLD, CYAN, GREEN, SaveData, box, color, frame, term_size, terminal_session
from games import GAMES

VERSION = "1.0.0"

LOGO = [
    "████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     ",
    "╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║     ",
    "   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║     ",
    "   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     ",
    "   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗",
    "   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝",
    "                         A R C A D E",
]


def ensure_terminal_size():
    cols, rows = term_size()
    if cols < 72 or rows < 24:
        frame(box("TERMINAL TOO SMALL", [
            "",
            f" Current terminal: {cols} x {rows}",
            " Recommended minimum: 72 x 24",
            "",
            " Resize the terminal window, then press ENTER.",
        ], 68))


def records_screen(key, save: SaveData):
    while True:
        body = [f" Games played: {save.data.get('games_played', 0)}", f" Rolling Sky unlocked: {save.rolling_unlocked}/500", ""]
        for gid, name, _, _ in GAMES:
            if gid == "rolling":
                value = save.best(gid)
                text = f"Stage {value:03d}" if value else "-"
            elif gid == "reaction":
                value = save.data.get("best", {}).get(gid)
                text = f"{value} ms" if value is not None else "-"
            else:
                value = save.data.get("best", {}).get(gid)
                text = str(value) if value is not None else "-"
            body.append(f" {name:<22} {text:>12}")
        body += ["", " ESC / ENTER : back"]
        frame(box("RECORDS", body, 64))
        k = key.read(None)
        if k in ("ESC", "ENTER", "q", "Q"):
            return


def about_screen(key):
    body = [
        "",
        f" Terminal Arcade v{VERSION}",
        " Pure terminal games. No browser, no GUI, no external packages.",
        "",
        f" OS      : {platform.system()} {platform.release()}",
        f" Python  : {platform.python_version()}",
        f" Terminal: {os.getenv('TERM_PROGRAM') or os.getenv('WT_SESSION') or 'console'}",
        "",
        " Controls are game-specific, but ESC always returns to the menu.",
        " Windows input: msvcrt",
        " macOS/Linux input: termios + select",
        "",
        " ENTER / ESC : back",
    ]
    frame(box("ABOUT", body, 72))
    while key.read(None) not in ("ENTER", "ESC", "q", "Q"):
        pass


def main_menu(key, save: SaveData):
    selected = 0
    page_size = 10
    items = [(gid, name, desc, fn) for gid, name, desc, fn in GAMES]
    utility = [("records", "Records", "View saved best scores", None), ("about", "About", "Runtime and control information", None), ("exit", "Exit", "Return to your shell", None)]
    all_items = items + utility
    while True:
        page = selected // page_size
        start = page * page_size
        visible = all_items[start:start + page_size]
        body = [color(line, CYAN + BOLD) for line in LOGO]
        body += ["", f"  30 games · Rolling Sky 500 stages · page {page + 1}/{(len(all_items)+page_size-1)//page_size}", ""]
        for idx, item in enumerate(visible, start=start):
            _, name, desc, _ = item
            marker = "▶" if idx == selected else " "
            number = f"{idx+1:02d}" if idx < len(items) else "  "
            line = f" {marker} {number}  {name:<22} {desc}"
            body.append(color(line, GREEN + BOLD) if idx == selected else line)
        body += ["", " ↑↓ select   ←→ page   ENTER play   R records   Q exit"]
        frame(box("TERMINAL ARCADE", body, 92))
        k = key.read(None)
        if k in ("q", "Q"):
            return
        if k in ("r", "R"):
            records_screen(key, save); continue
        if k == "UP": selected = (selected - 1) % len(all_items)
        elif k == "DOWN": selected = (selected + 1) % len(all_items)
        elif k == "LEFT": selected = max(0, selected - page_size)
        elif k == "RIGHT": selected = min(len(all_items) - 1, selected + page_size)
        elif k == "ENTER":
            gid, name, _, fn = all_items[selected]
            if gid == "exit":
                return
            if gid == "records":
                records_screen(key, save); continue
            if gid == "about":
                about_screen(key); continue
            save.increment_played()
            try:
                fn(key, save)
            except KeyboardInterrupt:
                pass
            except Exception as exc:
                frame(box("GAME ERROR", ["", f" {name} stopped unexpectedly.", f" {type(exc).__name__}: {exc}", "", " Press ENTER / ESC to return."], 78))
                while key.read(None) not in ("ENTER", "ESC"):
                    pass


def direct_game(key, save: SaveData, query: str) -> bool:
    query = query.strip().lower()
    for gid, name, _, fn in GAMES:
        if query in (gid.lower(), name.lower()):
            save.increment_played(); fn(key, save); return True
    return False


def parse_args():
    p = argparse.ArgumentParser(description="Terminal Arcade - 30 terminal-only games")
    p.add_argument("--game", help="Launch a game directly by id/name")
    p.add_argument("--list", action="store_true", help="List game ids")
    p.add_argument("--version", action="version", version=VERSION)
    return p.parse_args()


def main():
    args = parse_args()
    if args.list:
        for gid, name, desc, _ in GAMES:
            print(f"{gid:<12} {name:<22} {desc}")
        return 0
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Terminal Arcade needs an interactive terminal (TTY).")
        return 2
    save = SaveData()
    with terminal_session() as key:
        ensure_terminal_size()
        if term_size()[0] < 72 or term_size()[1] < 24:
            while True:
                k = key.read(None)
                if k == "ENTER" and term_size()[0] >= 72 and term_size()[1] >= 24:
                    break
                ensure_terminal_size()
        if args.game and not direct_game(key, save, args.game):
            frame(box("GAME NOT FOUND", ["", f" No game matches: {args.game}", "", " Press ENTER to open the main menu."], 70))
            while key.read(None) != "ENTER":
                pass
        main_menu(key, save)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
