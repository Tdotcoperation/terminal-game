# Terminal Arcade

A terminal-only arcade for Windows and macOS. It never opens a browser, webview, or GUI window: the menu, animation, controls, scores, and all games are rendered directly inside the terminal with ANSI escape sequences.

## Included games (30)

1. Snake
2. Tetris
3. Breakout
4. Pong
5. Rolling Sky 500
6. Space Shooter
7. Asteroids
8. Neon Racer
9. Dodge
10. Flappy Terminal
11. 2048
12. Minesweeper
13. Maze Escape
14. 15 Puzzle
15. Lights Out
16. Reaction Test
17. Typing Speed
18. Aim Trainer
19. Simon
20. Memory Cards
21. Blackjack
22. Slot Machine
23. Dice Poker
24. Rock Paper Scissors
25. Tic Tac Toe
26. Connect Four
27. Hangman
28. Number Guess
29. Tower Stack
30. Falling Blocks

### Rolling Sky 500

Rolling Sky contains stages 001-500. Stages are generated deterministically from the stage number, so the repository does not need 500 separate map files. Difficulty, obstacle density, moving hazards, speed, and stage length scale upward as the stage number increases. Clearing a stage unlocks the next one and progress is saved locally.

## Requirements

- Python 3.10 or newer recommended
- No pip packages are required
- Interactive terminal with ANSI support

### Windows

Recommended: Windows Terminal or modern PowerShell/CMD.

Run `windows/run.bat`, or from the repository root:

```bat
py -3 terminal_arcade.py
```

The Windows launcher switches the console to UTF-8 and uses Python's built-in `msvcrt` for immediate key input.

### macOS

In Terminal.app or iTerm2:

```bash
chmod +x macos/run.command
./macos/run.command
```

Or from the repository root:

```bash
python3 terminal_arcade.py
```

macOS input uses the standard-library `termios`, `tty`, and `select` modules.

## Controls

The main menu uses arrow keys and Enter. Most action games support both arrow keys and WASD. `ESC` returns to the menu from every game.

The program uses the terminal alternate-screen buffer and hides the cursor while running. On normal exit it restores the previous terminal screen and cursor.

## Save data

Best scores and Rolling Sky progress are stored outside the repository:

- Windows: `%APPDATA%\\TerminalArcade\\save.json`
- macOS: `~/Library/Application Support/TerminalArcade/save.json`

## Useful commands

List game IDs:

```bash
python3 terminal_arcade.py --list
```

Launch a game directly:

```bash
python3 terminal_arcade.py --game rolling
python3 terminal_arcade.py --game snake
```
