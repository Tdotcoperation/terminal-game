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


def game2048(key, save: SaveData):
    b=[[0]*4 for _ in range(4)]; score=0
    def add():
        z=[(r,c) for r in range(4) for c in range(4) if not b[r][c]]
        if z:
            r,c=random.choice(z);b[r][c]=4 if random.random()<.1 else 2
    def compress(row):
        non=[x for x in row if x];out=[];gain=0;i=0
        while i<len(non):
            if i+1<len(non) and non[i]==non[i+1]:out.append(non[i]*2);gain+=non[i]*2;i+=2
            else:out.append(non[i]);i+=1
        return out+[0]*(4-len(out)),gain
    def move(dir):
        nonlocal score,b
        old=[r[:] for r in b];gain=0
        if dir in ("LEFT","RIGHT"):
            for r in range(4):
                row=b[r][::-1] if dir=="RIGHT" else b[r][:];row,g=compress(row);gain+=g;b[r]=row[::-1] if dir=="RIGHT" else row
        else:
            for c in range(4):
                col=[b[r][c] for r in range(4)];col=col[::-1] if dir=="DOWN" else col;col,g=compress(col);gain+=g;col=col[::-1] if dir=="DOWN" else col
                for r in range(4):b[r][c]=col[r]
        if b!=old:score+=gain;add();save.set_best("2048",max(max(r) for r in b));return True
        return False
    add();add()
    while True:
        body=[]
        for r in b:body.append("   "+" ".join(f"{n:^7}" if n else "   ·   " for n in r))
        frame(box("2048",body+["",f" SCORE {score}   MAX {max(max(r) for r in b)}   BEST TILE {save.best('2048')}"," Arrows move · ESC menu"],58))
        k=key.read(None)
        if k=="ESC":return
        if k in ("LEFT","RIGHT","UP","DOWN"):move(k)
        if all(b[r][c] and not any(0<=rr<4 and 0<=cc<4 and b[rr][cc]==b[r][c] for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1))) for r in range(4) for c in range(4)):
            result(key,"2048",["No more moves",f"MAX TILE {max(max(r) for r in b)}"]);return


def minesweeper(key, save: SaveData):
    w,h=9,9;mines=set(random.sample([(x,y) for y in range(h) for x in range(w)],10));open_=set();flags=set();cx=cy=0
    def around(x,y):return [(xx,yy) for yy in range(max(0,y-1),min(h,y+2)) for xx in range(max(0,x-1),min(w,x+2)) if (xx,yy)!=(x,y)]
    def reveal(x,y):
        q=[(x,y)]
        while q:
            p=q.pop()
            if p in open_ or p in flags:continue
            open_.add(p)
            if sum(n in mines for n in around(*p))==0:
                q += [n for n in around(*p) if n not in open_]
    while True:
        rows=[]
        for y in range(h):
            line="   "
            for x in range(w):
                p=(x,y);sel=p==(cx,cy)
                if p in open_:
                    if p in mines:ch=color("*",RED)
                    else:
                        n=sum(q in mines for q in around(x,y));ch=str(n) if n else "·"
                elif p in flags:ch=color("F",YELLOW)
                else:ch="■"
                line += (color(f"[{ch}]",CYAN) if sel else f" {ch} ")
            rows.append(line)
        frame(box("MINESWEEPER",rows+["",f" Open {len(open_):02d}/71   Flags {len(flags):02d}/10"," Arrows move · ENTER open · F flag · ESC menu"],58))
        k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":cx=max(0,cx-1)
        if k=="RIGHT":cx=min(w-1,cx+1)
        if k=="UP":cy=max(0,cy-1)
        if k=="DOWN":cy=min(h-1,cy+1)
        if k in ("f","F"):
            p=(cx,cy)
            if p not in open_:
                if p in flags:flags.remove(p)
                else:flags.add(p)
        if k=="ENTER":
            if (cx,cy) in mines:
                result(key,"MINESWEEPER",["BOOM! You hit a mine."]);return
            reveal(cx,cy)
            if len(open_)==w*h-len(mines):save.set_best("mines",1);result(key,"MINESWEEPER",["CLEAR! All safe cells opened."]);return


def maze(key, save: SaveData):
    n=15;vis={(0,0)};stack=[(0,0)];links=set()
    while stack:
        x,y=stack[-1];opts=[(nx,ny) for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)) if 0<=nx<n and 0<=ny<n and (nx,ny) not in vis]
        if not opts:stack.pop();continue
        p=random.choice(opts);vis.add(p);links.add(((x,y),p));links.add((p,(x,y)));stack.append(p)
    px=py=0;moves=0
    while True:
        canvas=[list("#"*(n*2+1)) for _ in range(n*2+1)]
        for y in range(n):
            for x in range(n):
                canvas[y*2+1][x*2+1]=" "
                for nx,ny in ((x+1,y),(x,y+1)):
                    if ((x,y),(nx,ny)) in links:canvas[y+ny+1][x+nx+1]=" "
        canvas[1][1]=color("S",GREEN);canvas[n*2-1][n*2-1]=color("E",YELLOW);canvas[py*2+1][px*2+1]=color("◆",CYAN)
        frame(box("MAZE ESCAPE",["  "+"".join(r) for r in canvas]+["",f" MOVES {moves}"," Arrows/WASD · ESC menu"],40))
        k=key.read(None)
        if k=="ESC":return
        d={"LEFT":(-1,0),"a":(-1,0),"RIGHT":(1,0),"d":(1,0),"UP":(0,-1),"w":(0,-1),"DOWN":(0,1),"s":(0,1)}.get(k)
        if d and ((px,py),(px+d[0],py+d[1])) in links:px+=d[0];py+=d[1];moves+=1
        if (px,py)==(n-1,n-1):
            score=max(1,1000-moves);save.set_best("maze",score);result(key,"MAZE ESCAPE",[f"ESCAPED in {moves} moves",f"Score {score}"]);return


def puzzle15(key, save: SaveData):
    arr=list(range(1,16))+[0]
    z=15
    for _ in range(250):
        x,y=z%4,z//4;opts=[]
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<4 and 0<=ny<4:opts.append(ny*4+nx)
        q=random.choice(opts);arr[z],arr[q]=arr[q],arr[z];z=q
    moves=0
    while True:
        body=[]
        for r in range(4):body.append("       "+" ".join("    " if not v else f"{v:>3} " for v in arr[r*4:r*4+4]))
        frame(box("15 PUZZLE",body+["",f" MOVES {moves}"," Move blank with arrows · ESC menu"],56))
        k=key.read(None)
        if k=="ESC":return
        x,y=z%4,z//4;target=None
        if k=="LEFT" and x>0:target=z-1
        if k=="RIGHT" and x<3:target=z+1
        if k=="UP" and y>0:target=z-4
        if k=="DOWN" and y<3:target=z+4
        if target is not None:arr[z],arr[target]=arr[target],arr[z];z=target;moves+=1
        if arr==list(range(1,16))+[0]:save.set_best("puzzle15",max(1,1000-moves));result(key,"15 PUZZLE",[f"SOLVED in {moves} moves"]);return


def lights_out(key, save: SaveData):
    n=5;b=[[random.randrange(2) for _ in range(n)] for _ in range(n)];cx=cy=0;moves=0
    def press(x,y):
        nonlocal moves
        for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<n and 0<=ny<n:b[ny][nx]^=1
        moves+=1
    while True:
        body=[]
        for y in range(n):
            line="          "
            for x in range(n):
                ch=color("●",YELLOW) if b[y][x] else color("○",GRAY);line+=(color("[",CYAN)+ch+color("]",CYAN) if (x,y)==(cx,cy) else f" {ch} ")+" "
            body.append(line)
        frame(box("LIGHTS OUT",body+["",f" MOVES {moves}"," Arrows move · ENTER toggle · ESC menu"],60))
        k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":cx=max(0,cx-1)
        if k=="RIGHT":cx=min(n-1,cx+1)
        if k=="UP":cy=max(0,cy-1)
        if k=="DOWN":cy=min(n-1,cy+1)
        if k=="ENTER":press(cx,cy)
        if not any(map(any,b)):save.set_best("lights",max(1,100-moves));result(key,"LIGHTS OUT",[f"ALL LIGHTS OFF · {moves} moves"]);return


def reaction(key, save: SaveData):
    frame(box("REACTION TEST",[""," Wait for GREEN."," Do NOT press early.",""," ESC menu"],62))
    start=time.monotonic();wait=random.uniform(1.5,4.0)
    while time.monotonic()-start<wait:
        k=key.read(.03)
        if k=="ESC":return
        if k is not None:result(key,"REACTION TEST",["Too early! False start."]);return
    frame(box("REACTION TEST",["",color("                  GREEN! PRESS ANY KEY",GREEN+BOLD),"",""],62))
    t=time.perf_counter()
    while True:
        k=key.read(None)
        if k:
            ms=int((time.perf_counter()-t)*1000);save.set_best("reaction",ms,lower_is_better=True)
            result(key,"REACTION TEST",[f"{ms} ms",f"BEST {save.best('reaction')} ms"]);return


def typing_test(key, save: SaveData):
    samples=["the quick brown fox jumps over the lazy dog","terminal games are surprisingly fun to play","speed comes from accuracy before everything else"]
    target=random.choice(samples);typed="";start=None
    while True:
        good=sum(1 for a,b in zip(typed,target) if a==b);acc=int(good/max(1,len(typed))*100)
        display="".join(color(c,GREEN) if i<len(typed) and typed[i]==c else color(c,RED) if i<len(typed) else c for i,c in enumerate(target))
        frame(box("TYPING SPEED",["",f" {display}","",f" > {typed}_","",f" Accuracy {acc}%"," Type exactly · BACKSPACE edit · ESC menu"],78))
        k=key.read(None)
        if k=="ESC":return
        if k=="BACKSPACE":typed=typed[:-1];continue
        if isinstance(k,str) and len(k)==1 and k.isprintable():
            if start is None:start=time.perf_counter()
            typed+=k
        if typed==target:
            sec=time.perf_counter()-start;wpm=int((len(target)/5)/(sec/60));save.set_best("typing",wpm)
            result(key,"TYPING SPEED",[f"{wpm} WPM · {sec:.2f}s",f"BEST {save.best('typing')} WPM"]);return
        if len(typed)>len(target)+10:typed=typed[:len(target)+10]


def aim_trainer(key, save: SaveData):
    w,h=28,12;cx=cy=0;tx,ty=random.randrange(w),random.randrange(h);hits=0;start=time.monotonic();duration=20
    while True:
        left=max(0,duration-(time.monotonic()-start))
        if left<=0:save.set_best("aim",hits);result(key,"AIM TRAINER",[f"HITS {hits}",f"BEST {save.best('aim')}"]);return
        g=[["·" for _ in range(w)] for _ in range(h)];g[ty][tx]=color("◎",RED);g[cy][cx]=color("+",CYAN)
        draw_grid(g,"AIM TRAINER",[f" HITS {hits:02d}   TIME {left:04.1f}s"," Arrows aim · ENTER fire · ESC menu"])
        k=key.read(.05)
        if k=="ESC":return
        if k=="LEFT":cx=max(0,cx-1)
        if k=="RIGHT":cx=min(w-1,cx+1)
        if k=="UP":cy=max(0,cy-1)
        if k=="DOWN":cy=min(h-1,cy+1)
        if k=="ENTER" and (cx,cy)==(tx,ty):hits+=1;tx,ty=random.randrange(w),random.randrange(h)


def simon(key, save: SaveData):
    seq=[];level=0;labels=[("1",RED),("2",GREEN),("3",YELLOW),("4",BLUE)]
    while True:
        seq.append(random.randrange(4));level+=1
        for idx in seq:
            body=["", "        "+"   ".join(color(f" {n} ",c+BOLD if i==idx else GRAY) for i,(n,c) in enumerate(labels)),"",f" LEVEL {level} · Watch..."]
            frame(box("SIMON",body,62));time.sleep(.42);frame(box("SIMON",["","        1     2     3     4","",f" LEVEL {level}"],62));time.sleep(.16)
        for pos,ans in enumerate(seq):
            frame(box("SIMON",["","        1     2     3     4","",f" Repeat {pos+1}/{len(seq)} · keys 1-4 · ESC menu"],62))
            k=key.read(None)
            if k=="ESC":return
            if k not in "1234" or int(k)-1!=ans:
                save.set_best("simon",level-1);result(key,"SIMON",[f"Wrong sequence · LEVEL {level-1}",f"BEST {save.best('simon')}"]);return


def memory_cards(key, save: SaveData):
    vals=list("AABBCCDDEEFFGGHH");random.shuffle(vals);open_=set();matched=set();cx=cy=0;moves=0;first=None
    while True:
        body=[]
        for y in range(4):
            line="       "
            for x in range(4):
                i=y*4+x;show=i in open_ or i in matched;ch=vals[i] if show else "■";cell=f"[{ch}]" if (x,y)==(cx,cy) else f" {ch} ";line+=cell+" "
            body.append(line)
        frame(box("MEMORY CARDS",body+["",f" PAIRS {len(matched)//2}/8   MOVES {moves}"," Arrows move · ENTER flip · ESC menu"],56))
        k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":cx=max(0,cx-1)
        if k=="RIGHT":cx=min(3,cx+1)
        if k=="UP":cy=max(0,cy-1)
        if k=="DOWN":cy=min(3,cy+1)
        if k=="ENTER":
            i=cy*4+cx
            if i in matched or i in open_:continue
            open_.add(i)
            if first is None:first=i
            else:
                moves+=1
                shown=[]
                for yy in range(4):
                    line="       "
                    for xx in range(4):
                        j=yy*4+xx;visible=j in open_ or j in matched;ch=vals[j] if visible else "■";line+=f" {ch}  "
                    shown.append(line)
                frame(box("MEMORY CARDS",shown+[""," Checking pair..."],56));time.sleep(.45)
                if vals[first]==vals[i]:matched|={first,i}
                open_.clear();first=None
                if len(matched)==16:save.set_best("memory",max(1,100-moves));result(key,"MEMORY CARDS",[f"ALL PAIRS · {moves} moves"]);return
