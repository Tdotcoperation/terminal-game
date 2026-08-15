from __future__ import annotations

import random
import time

from engine import CYAN, GREEN, RED, YELLOW, SaveData, box, color, frame, wait_key


def result(key, title: str, lines: list[str]) -> None:
    frame(box(title, ["", *lines, "", "ENTER / ESC : menu"], 66))
    wait_key(key)


def draw_grid(grid: list[list[str]], title: str = "", footer: list[str] | None = None) -> None:
    body = ["  " + "".join(row) for row in grid]
    if footer:
        body += ["", *footer]
    frame(box(title, body, max(66, len(grid[0]) + 6 if grid else 66)))


def blackjack(key, save: SaveData):
    deck=[min(v,10) for _ in range(4) for v in range(1,14)];random.shuffle(deck);you=[deck.pop(),deck.pop()];dealer=[deck.pop(),deck.pop()]
    def val(hand):
        total=sum(11 if x==1 else x for x in hand);aces=hand.count(1)
        while total>21 and aces:total-=10;aces-=1
        return total
    while True:
        frame(box("BLACKJACK",["",f" Dealer: {dealer[0]}  [?]",f" You   : {' '.join(map(str,you))}   = {val(you)}",""," H Hit   S Stand   ESC menu"],62))
        k=key.read(None)
        if k=="ESC":return
        if k in ("h","H"):
            you.append(deck.pop())
            if val(you)>21:result(key,"BLACKJACK",[f"BUST {val(you)} · Dealer wins"]);return
        if k in ("s","S"):
            while val(dealer)<17:dealer.append(deck.pop())
            y,d=val(you),val(dealer);win=d>21 or y>d;draw=y==d
            if win:save.set_best("blackjack",save.best("blackjack")+1)
            result(key,"BLACKJACK",[f"Dealer {' '.join(map(str,dealer))} = {d}",f"You    {' '.join(map(str,you))} = {y}","PUSH" if draw else "YOU WIN!" if win else "DEALER WINS"]);return


def slots(key, save: SaveData):
    symbols=["7","★","◆","●","BAR"];coins=100
    while coins>=10:
        frame(box("SLOT MACHINE",["",f" COINS {coins}",""," ENTER spin (10) · ESC cash out"],62));k=key.read(None)
        if k=="ESC":save.set_best("slots",coins);return
        if k!="ENTER":continue
        coins-=10;r=[random.choice(symbols) for _ in range(3)]
        if len(set(r))==1:coins+=100 if r[0]=="7" else 60
        elif len(set(r))==2:coins+=20
        frame(box("SLOT MACHINE",["",f"          [ {r[0]:^3} ] [ {r[1]:^3} ] [ {r[2]:^3} ]","",f" COINS {coins}"," ENTER continue"],62));time.sleep(.35)
    result(key,"SLOT MACHINE",["Out of coins!"])


def dice_poker(key, save: SaveData):
    dice=[random.randint(1,6) for _ in range(5)];hold=[False]*5;rolls=1;cx=0
    def rank():
        counts=sorted([dice.count(v) for v in set(dice)],reverse=True)
        if counts==[5]:return "FIVE OF A KIND",60
        if counts==[4,1]:return "FOUR OF A KIND",40
        if counts==[3,2]:return "FULL HOUSE",30
        if counts==[3,1,1]:return "THREE OF A KIND",20
        if counts==[2,2,1]:return "TWO PAIR",15
        if counts==[2,1,1,1]:return "PAIR",8
        return "HIGH DICE",max(dice)
    while True:
        body=["", "      "+"  ".join(("[" if i==cx else " ")+f"{v}"+("*]" if hold[i] else "]" if i==cx else " ") for i,v in enumerate(dice)),"",f" Roll {rolls}/3 · ←→ select · SPACE hold · ENTER reroll"]
        frame(box("DICE POKER",body,66));k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":cx=max(0,cx-1)
        if k=="RIGHT":cx=min(4,cx+1)
        if k==" ":hold[cx]=not hold[cx]
        if k=="ENTER":
            if rolls>=3:
                name,pts=rank();save.set_best("dicepoker",pts);result(key,"DICE POKER",[name,f"Score {pts} · Best {save.best('dicepoker')}"]);return
            for i in range(5):
                if not hold[i]:dice[i]=random.randint(1,6)
            rolls+=1


def rps(key, save: SaveData):
    names=["ROCK","PAPER","SCISSORS"];you=cpu=rounds=0;sel=0
    while rounds<10:
        frame(box("ROCK PAPER SCISSORS",["",f" YOU {you} : {cpu} CPU   ROUND {rounds+1}/10","", "   "+"   ".join((">" if i==sel else " ")+n for i,n in enumerate(names)),""," ←→ choose · ENTER throw · ESC menu"],70));k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":sel=(sel-1)%3
        if k=="RIGHT":sel=(sel+1)%3
        if k=="ENTER":
            c=random.randrange(3);d=(sel-c)%3
            if d==1:you+=1
            elif d==2:cpu+=1
            rounds+=1
    if you>cpu:save.set_best("rps",save.best("rps")+1)
    result(key,"RPS",[f"FINAL {you}:{cpu}","YOU WIN!" if you>cpu else "DRAW" if you==cpu else "CPU WINS"])


def tic_tac_toe(key, save: SaveData):
    b=[" "]*9;cx=cy=0
    wins=[(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    def winner(p):return any(all(b[i]==p for i in q) for q in wins)
    while True:
        body=[]
        for y in range(3):body.append("                "+" | ".join((f"[{b[y*3+x]}]" if (x,y)==(cx,cy) else f" {b[y*3+x]} ") for x in range(3)))
        frame(box("TIC TAC TOE",body+[""," Arrows move · ENTER place X · ESC menu"],62));k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":cx=max(0,cx-1)
        if k=="RIGHT":cx=min(2,cx+1)
        if k=="UP":cy=max(0,cy-1)
        if k=="DOWN":cy=min(2,cy+1)
        if k=="ENTER" and b[cy*3+cx]==" ":
            b[cy*3+cx]="X"
            if winner("X"):save.set_best("ttt",save.best("ttt")+1);result(key,"TIC TAC TOE",["YOU WIN!"]);return
            empty=[i for i,v in enumerate(b) if v==" "]
            if not empty:result(key,"TIC TAC TOE",["DRAW"]);return
            choice=None
            for p in ("O","X"):
                for i in empty:
                    b[i]=p
                    if winner(p):choice=i
                    b[i]=" "
                    if choice is not None:break
                if choice is not None:break
            if choice is None and 4 in empty:choice=4
            if choice is None:choice=random.choice(empty)
            b[choice]="O"
            if winner("O"):result(key,"TIC TAC TOE",["CPU WINS"]);return


def connect4(key, save: SaveData):
    w,h=7,6;b=[[" "]*w for _ in range(h)];col=3
    def win(p):
        for y in range(h):
            for x in range(w):
                for dx,dy in ((1,0),(0,1),(1,1),(1,-1)):
                    if all(0<=x+dx*i<w and 0<=y+dy*i<h and b[y+dy*i][x+dx*i]==p for i in range(4)):return True
        return False
    def drop(c,p):
        for y in range(h-1,-1,-1):
            if b[y][c]==" ":b[y][c]=p;return True
        return False
    while True:
        body=["        "+" ".join(f" {i+1} " if i!=col else f"[{i+1}]" for i in range(w))]
        body += ["        "+" ".join(color("●",YELLOW) if v=="X" else color("●",RED) if v=="O" else "·" for v in row) for row in b]
        frame(box("CONNECT FOUR",body+[""," ←→ column · ENTER drop · ESC menu"],62));k=key.read(None)
        if k=="ESC":return
        if k=="LEFT":col=max(0,col-1)
        if k=="RIGHT":col=min(w-1,col+1)
        if k=="ENTER" and drop(col,"X"):
            if win("X"):save.set_best("connect4",save.best("connect4")+1);result(key,"CONNECT FOUR",["YOU WIN!"]);return
            valid=[c for c in range(w) if b[0][c]==" "]
            if not valid:result(key,"CONNECT FOUR",["DRAW"]);return
            choice=None
            for p in ("O","X"):
                for c in valid:
                    y=next(y for y in range(h-1,-1,-1) if b[y][c]==" ");b[y][c]=p
                    if win(p):choice=c
                    b[y][c]=" "
                    if choice is not None:break
                if choice is not None:break
            drop(choice if choice is not None else random.choice(valid),"O")
            if win("O"):result(key,"CONNECT FOUR",["CPU WINS"]);return


def hangman(key, save: SaveData):
    words=["python","terminal","keyboard","arcade","galaxy","network","pixel","rocket","window","memory"]
    word=random.choice(words);guessed=set();wrong=[]
    stages=["", " O ", " O\n | ", " O\n/| ", " O\n/|\\", " O\n/|\\\n/  ", " O\n/|\\\n/ \\"]
    while True:
        shown=" ".join(c if c in guessed else "_" for c in word)
        art=stages[min(len(wrong),len(stages)-1)].split("\n")
        frame(box("HANGMAN",["",*[("                  "+a) for a in art],"",f" WORD  {shown}",f" WRONG {' '.join(wrong)}","", " Type a letter · ESC menu"],66));k=key.read(None)
        if k=="ESC":return
        if isinstance(k,str) and len(k)==1 and k.isalpha():
            k=k.lower()
            if k in guessed or k in wrong:continue
            if k in word:guessed.add(k)
            else:wrong.append(k)
            if all(c in guessed for c in word):save.set_best("hangman",max(1,10-len(wrong)));result(key,"HANGMAN",[f"YOU GOT IT: {word.upper()}"]);return
            if len(wrong)>=6:result(key,"HANGMAN",[f"HANGED · WORD WAS {word.upper()}"]);return


def number_guess(key, save: SaveData):
    num=random.randint(1,100);typed="";tries=0;hint="1 ~ 100"
    while True:
        frame(box("NUMBER GUESS",["",f" Hint: {hint}","",f" > {typed}_","",f" Tries {tries}"," Digits · ENTER submit · BACKSPACE · ESC menu"],62));k=key.read(None)
        if k=="ESC":return
        if k=="BACKSPACE":typed=typed[:-1]
        elif isinstance(k,str) and len(k)==1 and k.isdigit() and len(typed)<3:typed+=k
        elif k=="ENTER" and typed:
            v=int(typed);typed="";tries+=1
            if v==num:save.set_best("guess",max(1,101-tries));result(key,"NUMBER GUESS",[f"CORRECT! {num}",f"TRIES {tries}"]);return
            hint=f"Higher than {v}" if v<num else f"Lower than {v}"


def tower_stack(key, save: SaveData):
    w=36;base_x=10;base_w=16;blocks=[(base_x,16,base_w)];x=0;dir=1;level=1
    while True:
        k=key.read(max(.035,.09-level*.002))
        if k=="ESC":return
        x+=dir
        if x<=0 or x+base_w>=w:dir*=-1;x=max(0,min(w-base_w,x))
        if k in (" ","ENTER"):
            px,_,pw=blocks[-1];left=max(x,px);right=min(x+base_w,px+pw)
            if right<=left:save.set_best("stack",level-1);result(key,"TOWER STACK",[f"MISSED · HEIGHT {level-1}"]);return
            base_x=left;base_w=right-left;level+=1;blocks.append((base_x,max(2,17-level),base_w));x=0;dir=1
            if level>=16:save.set_best("stack",level);result(key,"TOWER STACK",["PERFECT TOWER! 15 levels"]);return
        g=[[" " for _ in range(w)] for _ in range(18)]
        for bx,by,bw in blocks[-15:]:
            yy=max(1,by)
            for xx in range(bx,bx+bw):g[yy][xx]=color("█",GREEN)
        current_y=max(1,17-level)
        for xx in range(x,min(w,x+base_w)):g[current_y][xx]=color("█",CYAN)
        draw_grid(g,"TOWER STACK",[f" LEVEL {level}   BEST {save.best('stack')}"," SPACE/ENTER drop · ESC menu"])


def falling_blocks(key, save: SaveData):
    w,h=36,18;px=w//2;items=[];score=0;miss=0;tick=0
    while miss<5:
        k=key.read(.075)
        if k=="ESC":return
        if k in ("LEFT","a"):px=max(2,px-2)
        if k in ("RIGHT","d"):px=min(w-3,px+2)
        tick+=1;items=[[x,y+1,t] for x,y,t in items if y+1<h]
        if tick%4==0:items.append([random.randrange(1,w-1),0,"star" if random.random()<.78 else "bomb"])
        kept=[]
        for x,y,t in items:
            if y>=h-2 and abs(x-px)<=2:
                if t=="star":score+=10;save.set_best("falling",score)
                else:miss+=2
            elif y>=h-1:
                if t=="star":miss+=1
            else:kept.append([x,y,t])
        items=kept
        g=[[" " for _ in range(w)] for _ in range(h)]
        for x,y,t in items:g[y][x]=color("★",YELLOW) if t=="star" else color("●",RED)
        for x in range(px-2,px+3):g[h-1][x]=color("═",CYAN)
        draw_grid(g,"FALLING BLOCKS",[f" SCORE {score:04d}   MISS {miss}/5   BEST {save.best('falling'):04d}"," ←→ catch stars · avoid bombs · ESC menu"])
    result(key,"FALLING BLOCKS",[f"GAME OVER · SCORE {score}"])
