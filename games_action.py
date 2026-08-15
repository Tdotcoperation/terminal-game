from __future__ import annotations

import math
import random
import time
from collections import deque

from engine import (
    BOLD, BLUE, CYAN, DIM, GRAY, GREEN, MAGENTA, RED, RESET, WHITE, YELLOW,
    SaveData, box, color, frame, sleep_countdown, wait_key,
)


def result(key, title: str, lines: list[str]) -> None:
    frame(box(title, ["", *lines, "", "ENTER / ESC : menu"], 66))
    wait_key(key)


def draw_grid(grid: list[list[str]], title: str = "", footer: list[str] | None = None) -> None:
    body = ["  " + "".join(row) for row in grid]
    if footer:
        body += ["", *footer]
    frame(box(title, body, max(66, len(grid[0]) + 6 if grid else 66)))


def snake(key, save: SaveData):
    w, h = 38, 18
    snake_body = deque([(w // 2, h // 2), (w // 2 - 1, h // 2), (w // 2 - 2, h // 2)])
    direction = (1, 0)
    food = (random.randrange(w), random.randrange(h))
    score = 0
    delay = 0.105
    while True:
        k = key.read(delay)
        nd = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0),
              "w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}.get(k)
        if k == "ESC": return
        if nd and (nd[0] != -direction[0] or nd[1] != -direction[1]): direction = nd
        hx, hy = snake_body[0]
        nx, ny = hx + direction[0], hy + direction[1]
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in snake_body:
            save.set_best("snake", score)
            result(key, "SNAKE", [f"Game Over · SCORE {score}", f"BEST {save.best('snake')}"])
            return
        snake_body.appendleft((nx, ny))
        if (nx, ny) == food:
            score += 10
            delay = max(0.045, delay - 0.002)
            empty = [(x, y) for y in range(h) for x in range(w) if (x, y) not in snake_body]
            food = random.choice(empty) if empty else (-1, -1)
        else:
            snake_body.pop()
        g = [[" " for _ in range(w)] for _ in range(h)]
        fx, fy = food
        if 0 <= fx < w: g[fy][fx] = color("◆", YELLOW)
        for i, (x, y) in enumerate(snake_body): g[y][x] = color("●" if i == 0 else "█", GREEN)
        draw_grid(g, "SNAKE", [f" SCORE {score:05d}   BEST {save.best('snake'):05d}", " Arrows/WASD · ESC menu"])


TETROMINOES = [
    [(0,0),(1,0),(2,0),(3,0)], [(0,0),(1,0),(0,1),(1,1)], [(1,0),(0,1),(1,1),(2,1)],
    [(1,0),(2,0),(0,1),(1,1)], [(0,0),(1,0),(1,1),(2,1)], [(0,0),(0,1),(1,1),(2,1)], [(2,0),(0,1),(1,1),(2,1)]
]


def _rot(shape): return [(-y, x) for x, y in shape]


def tetris(key, save: SaveData):
    w, h = 10, 20; board = [[0]*w for _ in range(h)]; score = lines = 0
    def new_piece(): return random.choice(TETROMINOES), 4, 0
    shape, px, py = new_piece(); last = time.monotonic(); drop = .55
    def valid(s, x, y):
        return all(0 <= x+dx < w and y+dy < h and (y+dy < 0 or not board[y+dy][x+dx]) for dx,dy in s)
    while True:
        timeout = max(0, drop - (time.monotonic()-last)); k = key.read(timeout)
        if k == "ESC": return
        if k in ("LEFT","a") and valid(shape,px-1,py): px -= 1
        if k in ("RIGHT","d") and valid(shape,px+1,py): px += 1
        if k in ("UP","w"):
            r = _rot(shape)
            if valid(r,px,py): shape = r
        if k in ("DOWN","s"): last = 0
        if k == " ":
            while valid(shape,px,py+1): py += 1
            last = 0
        if time.monotonic()-last >= drop:
            last = time.monotonic()
            if valid(shape,px,py+1): py += 1
            else:
                for dx,dy in shape:
                    if py+dy < 0:
                        save.set_best("tetris", score); result(key,"TETRIS",[f"Game Over · SCORE {score}",f"LINES {lines}"]); return
                    board[py+dy][px+dx] = 1
                kept = [r for r in board if not all(r)]; cleared = h-len(kept)
                if cleared:
                    board = [[0]*w for _ in range(cleared)] + kept; lines += cleared; score += [0,100,300,500,800][cleared]
                    save.set_best("tetris", score); drop = max(.12,.55-lines*.008)
                shape,px,py = new_piece()
        g = [[color("██", CYAN) if board[y][x] else "  " for x in range(w)] for y in range(h)]
        for dx,dy in shape:
            x,y=px+dx,py+dy
            if 0<=y<h and 0<=x<w:g[y][x]=color("██",MAGENTA)
        frame(box("TETRIS", ["  "+"".join(r) for r in g]+["",f" SCORE {score:06d}  LINES {lines:03d}  BEST {save.best('tetris'):06d}"," ←→ move  ↑ rotate  SPACE drop  ESC menu"], 56))


def breakout(key, save: SaveData):
    w,h=46,20; paddle_x=w//2-4; paddle_w=9; bx,by=w/2,h-5; vx,vy=.72,-.55; score=0;lives=3
    bricks={(x,y) for y in range(2,7) for x in range(2,w-2,4)}
    while True:
        k=key.read(.035)
        if k=="ESC":return
        if k in ("LEFT","a"):paddle_x=max(1,paddle_x-2)
        if k in ("RIGHT","d"):paddle_x=min(w-paddle_w-1,paddle_x+2)
        nx,ny=bx+vx,by+vy
        if nx<1 or nx>w-2:vx*=-1;nx=bx+vx
        if ny<1:vy=abs(vy);ny=by+vy
        hit_brick=None
        iy=int(round(ny))
        for brick in bricks:
            rx,ry=brick
            if ry==iy and rx<=nx<=rx+2:
                hit_brick=brick;break
        if hit_brick is not None:
            bricks.remove(hit_brick);vy*=-1;score+=10;save.set_best("breakout",score)
        if h-2<=ny<=h-1 and paddle_x<=nx<=paddle_x+paddle_w:
            vy=-abs(vy);vx += (nx-(paddle_x+paddle_w/2))*.025
        bx,by=nx,ny
        if by>=h:
            lives-=1
            if lives<=0:result(key,"BREAKOUT",[f"Game Over · SCORE {score}"]);return
            bx,by=w/2,h-5;vx,vy=random.choice([-.72,.72]),-.55
        if not bricks:result(key,"BREAKOUT",[f"CLEAR! SCORE {score}"]);return
        g=[[" " for _ in range(w)] for _ in range(h)]
        for x,y in bricks:
            for i in range(3):
                if x+i<w:g[y][x+i]=color("█",CYAN if y%2 else MAGENTA)
        if 0<=int(by)<h and 0<=int(bx)<w:g[int(by)][int(bx)]=color("●",YELLOW)
        for x in range(paddle_x,paddle_x+paddle_w):g[h-1][x]=color("═",GREEN)
        draw_grid(g,"BREAKOUT",[f" SCORE {score:05d}   LIFE {'♥'*lives}   BEST {save.best('breakout'):05d}"," ← → / A D · ESC menu"])


def pong(key, save: SaveData):
    w,h=52,18; py=h//2-2; ai=h//2-2; ph=5; bx,by=w/2,h/2;vx,vy=.85,.45;you=cpu=0
    while you<7 and cpu<7:
        k=key.read(.045)
        if k=="ESC":return
        if k in ("UP","w"):py=max(0,py-1)
        if k in ("DOWN","s"):py=min(h-ph,py+1)
        ai += 0.55 if by>ai+ph/2 else -0.55; ai=max(0,min(h-ph,ai))
        nx,ny=bx+vx,by+vy
        if ny<0 or ny>=h-1:vy*=-1;ny=by+vy
        if nx<=2 and py-1<=ny<=py+ph:vx=abs(vx);nx=bx+vx
        if nx>=w-3 and ai-1<=ny<=ai+ph:vx=-abs(vx);nx=bx+vx
        bx,by=nx,ny
        if bx<0:cpu+=1;bx,by=w/2,h/2;vx=.85
        if bx>w:you+=1;bx,by=w/2,h/2;vx=-.85
        g=[[" " for _ in range(w)] for _ in range(h)]
        for y in range(h):g[y][w//2]=color("│",GRAY)
        for y in range(int(py),int(py)+ph):g[y][1]=color("█",GREEN)
        for y in range(int(ai),int(ai)+ph):g[y][w-2]=color("█",RED)
        if 0<=int(by)<h and 0<=int(bx)<w:g[int(by)][int(bx)]=color("●",YELLOW)
        draw_grid(g,"PONG",[f" YOU {you} : {cpu} CPU   First to 7"," ↑↓ / W S · ESC menu"])
    if you>cpu:save.set_best("pong",save.best("pong")+1)
    result(key,"PONG",["YOU WIN!" if you>cpu else "CPU WIN!",f"Final {you}:{cpu}"])


def rolling_sky(key, save: SaveData):
    selected=save.rolling_unlocked
    while True:
        unlocked=save.rolling_unlocked
        start=((selected-1)//20)*20+1
        body=[f" Unlocked {unlocked:03d} / 500",""]
        for row in range(4):
            line="  "
            for col in range(5):
                n=start+row*5+col
                if n>500:continue
                mark="▶" if n==selected else " "
                state="✓" if n<unlocked else (" " if n==unlocked else "×")
                txt=f"{mark}{n:03d}{state}"
                line += (color(txt,GREEN) if n<=unlocked else color(txt,GRAY))+"  "
            body.append(line)
        body += ["", " ←→ select  ↑↓ ±5  ENTER play  ESC menu"]
        frame(box("ROLLING SKY 500 · STAGE SELECT",body,68))
        k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":selected=max(1,selected-1)
        if k=="RIGHT":selected=min(500,selected+1)
        if k=="UP":selected=max(1,selected-5)
        if k=="DOWN":selected=min(500,selected+5)
        if selected>unlocked:selected=unlocked
        if k=="ENTER":
            if _rolling_stage(key,save,selected) and selected<500:
                selected+=1


def _rolling_stage(key, save, stage):
    lanes=7; rows=20; player=lanes//2; tick=0; progress=0
    seed=random.Random(stage*9973+17); obstacles=[]
    speed=max(.035,.125-stage*.00017); length=170+stage//2
    density=min(.72,.18+stage*.00105)
    while tick<length:
        k=key.read(speed)
        if k=="ESC":return False
        if k in ("LEFT","a"):player=max(0,player-1)
        if k in ("RIGHT","d"):player=min(lanes-1,player+1)
        obstacles=[(lane,y+1,typ) for lane,y,typ in obstacles if y+1<rows]
        if tick%2==0 and seed.random()<density:
            blocked=set()
            count=1+(stage>100 and seed.random()<.35)+(stage>300 and seed.random()<.25)
            count=min(lanes-2,int(count))
            while len(blocked)<count:blocked.add(seed.randrange(lanes))
            for lane in blocked:obstacles.append((lane,0,"M" if stage>180 and seed.random()<.13 else "X"))
        moved=[]
        for lane,y,typ in obstacles:
            if typ=="M" and tick%3==0:
                lane=max(0,min(lanes-1,lane+seed.choice([-1,1])))
            moved.append((lane,y,typ))
        obstacles=moved
        if any(lane==player and y>=rows-2 for lane,y,_ in obstacles):
            result(key,f"ROLLING SKY · STAGE {stage:03d}",[f"CRASH · {int(tick/length*100)}%",f"Unlocked {save.rolling_unlocked:03d}/500"])
            return False
        tick+=1;progress=int(tick/length*100)
        track=[]
        for y in range(rows):
            row=[]
            for lane in range(lanes):
                ch="  "
                for ol,oy,typ in obstacles:
                    if ol==lane and oy==y:ch=color("▓▓",RED if typ=="X" else MAGENTA);break
                if y==rows-1 and lane==player:ch=color("◆◆",CYAN)
                row.append(ch)
            track.append("      │"+"".join(track_ch for track_ch in row)+"│")
        bar="█"*(progress//5)+"░"*(20-progress//5)
        frame(box(f"ROLLING SKY · STAGE {stage:03d}",[f" Progress [{bar}] {progress:3d}%  Speed {1/speed:4.1f}","",*track,"", " ← / → or A / D · ESC abort"], 72))
    save.unlock_rolling(min(500,stage+1));save.set_best("rolling",stage)
    result(key,f"STAGE {stage:03d} CLEAR!",[f"Progress 100%",f"Unlocked {save.rolling_unlocked:03d}/500"])
    return True


def space_shooter(key, save: SaveData):
    w,h=42,19;px=w//2; bullets=[];enemies=[];tick=0;score=0
    while True:
        k=key.read(.055)
        if k=="ESC":return
        if k in ("LEFT","a"):px=max(1,px-1)
        if k in ("RIGHT","d"):px=min(w-2,px+1)
        if k in (" ","UP","w"):bullets.append([px,h-2])
        tick+=1
        if tick%4==0:enemies.append([random.randrange(1,w-1),0])
        for b in bullets:b[1]-=1
        for e in enemies:e[1]+=1
        for b in bullets:
            for e in enemies:
                if b==e:e[1]=99;b[1]=-9;score+=10;save.set_best("shooter",score)
        bullets=[b for b in bullets if b[1]>=0];enemies=[e for e in enemies if e[1]<h]
        if any(e[1]>=h-2 and abs(e[0]-px)<=1 for e in enemies):result(key,"SPACE SHOOTER",[f"Destroyed · SCORE {score}"]);return
        g=[[" " for _ in range(w)] for _ in range(h)]
        for x,y in enemies:
            if 0<=y<h:g[y][x]=color("▼",RED)
        for x,y in bullets:
            if 0<=y<h:g[y][x]=color("│",YELLOW)
        g[h-1][px]=color("▲",CYAN)
        draw_grid(g,"SPACE SHOOTER",[f" SCORE {score:05d}  BEST {save.best('shooter'):05d}"," ←→ move · SPACE fire · ESC menu"])


def asteroids(key, save: SaveData):
    w,h=44,19;px,py=w//2,h//2;rocks=[];score=0;tick=0
    while True:
        k=key.read(.07)
        if k=="ESC":return
        dx=dy=0
        if k in ("LEFT","a"):dx=-1
        if k in ("RIGHT","d"):dx=1
        if k in ("UP","w"):dy=-1
        if k in ("DOWN","s"):dy=1
        px=max(1,min(w-2,px+dx));py=max(1,min(h-2,py+dy));tick+=1
        if tick%3==0:
            side=random.randrange(4)
            if side==0:rocks.append([random.randrange(w),0,random.choice([-1,0,1]),1])
            elif side==1:rocks.append([random.randrange(w),h-1,random.choice([-1,0,1]),-1])
            elif side==2:rocks.append([0,random.randrange(h),1,random.choice([-1,0,1])])
            else:rocks.append([w-1,random.randrange(h),-1,random.choice([-1,0,1])])
        for r in rocks:r[0]+=r[2];r[1]+=r[3]
        if k==" ":
            before=len(rocks);rocks=[r for r in rocks if abs(r[0]-px)>2 or abs(r[1]-py)>2];score+=(before-len(rocks))*10
        rocks=[r for r in rocks if 0<=r[0]<w and 0<=r[1]<h]
        if any(r[0]==px and r[1]==py for r in rocks):save.set_best("asteroids",score);result(key,"ASTEROIDS",[f"Impact · SCORE {score}"]);return
        g=[[" " for _ in range(w)] for _ in range(h)]
        for x,y,_,_ in rocks:g[y][x]=color("●",RED)
        g[py][px]=color("◆",CYAN)
        draw_grid(g,"ASTEROIDS",[f" SCORE {score:05d}  BEST {save.best('asteroids'):05d}"," Move WASD/arrows · SPACE pulse-shot"])


def racer(key, save: SaveData):
    lanes=[12,22,32]; lane=1;cars=[];score=0;tick=0;h=20;speed=.10
    while True:
        k=key.read(speed)
        if k=="ESC":return
        if k in ("LEFT","a"):lane=max(0,lane-1)
        if k in ("RIGHT","d"):lane=min(2,lane+1)
        tick+=1;score+=1
        cars=[[ln,y+1] for ln,y in cars if y+1<h]
        if tick%5==0:cars.append([random.randrange(3),0])
        if any(ln==lane and y>=h-2 for ln,y in cars):save.set_best("racer",score);result(key,"NEON RACER",[f"CRASH · DISTANCE {score}m"]);return
        g=[[" " for _ in range(45)] for _ in range(h)]
        for y in range(h):
            for x in (7,17,27,37):g[y][x]=color("│",GRAY)
        for ln,y in cars:g[y][lanes[ln]]=color("▣",RED)
        g[h-1][lanes[lane]]=color("▲",CYAN)
        draw_grid(g,"NEON RACER",[f" DIST {score:05d}m   BEST {save.best('racer'):05d}m"," ← → lane · ESC menu"])
        if score%100==0:speed=max(.045,speed-.005)


def dodge(key, save: SaveData):
    w,h=42,19;px,py=w//2,h-2;haz=[];tick=0;score=0
    while True:
        k=key.read(.06)
        if k=="ESC":return
        if k in ("LEFT","a"):px=max(0,px-1)
        if k in ("RIGHT","d"):px=min(w-1,px+1)
        if k in ("UP","w"):py=max(0,py-1)
        if k in ("DOWN","s"):py=min(h-1,py+1)
        tick+=1;score+=1;haz=[[x,y+1] for x,y in haz if y+1<h]
        if tick%2==0:haz.append([random.randrange(w),0])
        if [px,py] in haz:save.set_best("dodge",score);result(key,"DODGE",[f"Hit · SURVIVED {score} ticks"]);return
        g=[[" " for _ in range(w)] for _ in range(h)]
        for x,y in haz:g[y][x]=color("▼",RED)
        g[py][px]=color("◆",GREEN)
        draw_grid(g,"DODGE",[f" SURVIVAL {score:05d}  BEST {save.best('dodge'):05d}"," WASD/arrows · ESC menu"])


def flappy(key, save: SaveData):
    w,h=46,18;x=9;y=h/2;vy=0.;pipes=[];tick=0;score=0
    while True:
        k=key.read(.055)
        if k=="ESC":return
        if k in (" ","UP","w"):vy=-1.25
        vy+=.18;y+=vy;tick+=1
        pipes=[[px-1,gap] for px,gap in pipes if px-1>=0]
        if tick%22==0:pipes.append([w-1,random.randrange(4,h-5)])
        for px,gap in pipes:
            if px==x-1:score+=1;save.set_best("flappy",score)
            if px==x and not gap<=int(y)<=gap+4:result(key,"FLAPPY TERMINAL",[f"PIPE HIT · SCORE {score}"]);return
        if y<0 or y>=h:result(key,"FLAPPY TERMINAL",[f"OUT OF BOUNDS · SCORE {score}"]);return
        g=[[" " for _ in range(w)] for _ in range(h)]
        for px,gap in pipes:
            if 0<=px<w:
                for yy in range(h):
                    if not gap<=yy<=gap+4:g[yy][px]=color("█",GREEN)
        g[int(y)][x]=color("▶",YELLOW)
        draw_grid(g,"FLAPPY TERMINAL",[f" SCORE {score:03d}  BEST {save.best('flappy'):03d}"," SPACE / ↑ flap · ESC menu"])
