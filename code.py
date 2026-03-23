import displayio
import time
import board
from adafruit_clue import clue
from components import Ball, Paddle, Listener
from ai_paddle import AIPaddle, BALL_SPEED_INC, BALL_SPEED_MAX

S=240;R=5;PW=60;HW=30
DT=1/60

aBtn=Listener()
bBtn=Listener()

ai=AIPaddle(side="top")
time.sleep(1)
ai.load()

bspeed=1.0

def mk():
    global bspeed
    bspeed=1.0
    b=Ball(20,20,R,colour=0xFF0000)
    p1=Paddle(90,228,PW,2,colour=0xFFFFFF)
    p2=Paddle(90,12,PW,2,colour=0xFFFFFF)
    g=displayio.Group()
    g.append(b.circle);g.append(p1.rect);g.append(p2.rect)
    board.DISPLAY.root_group=g
    return b,p1,p2

def step_ball(ball, p1, p2):
    global bspeed
    ball._last_vy=ball.y_vel
    ball.posx += ball.x_vel * R * bspeed
    ball.posy += ball.y_vel * R * bspeed

    if ball.posx < R: ball.posx=R; ball.x_vel=-ball.x_vel
    if ball.posx > S-R: ball.posx=S-R; ball.x_vel=-ball.x_vel

    if ball.posy < R: return "WIN"
    if ball.posy > S-R: return "LOSE"

    if (ball.y_vel > 0 and ball.posy+R >= 228 and ball.posy+R <= 233
            and p1.posx <= ball.posx <= p1.posx+PW):
        ball.y_vel=-ball.y_vel; ball.posy=228-R
        o=(ball.posx-(p1.posx+HW))/HW
        if o<-1: o=-1.0
        elif o>1: o=1.0
        ball.x_vel=o*0.8
        if bspeed<BALL_SPEED_MAX: bspeed+=BALL_SPEED_INC
        ball.circle.x0=int(ball.posx); ball.circle.y0=int(ball.posy)
        return "HB"

    if (ball.y_vel < 0 and ball.posy-R <= 14 and ball.posy-R >= 7
            and p2.posx <= ball.posx <= p2.posx+PW):
        ball.y_vel=-ball.y_vel; ball.posy=14+R
        o=(ball.posx-(p2.posx+HW))/HW
        if o<-1: o=-1.0
        elif o>1: o=1.0
        ball.x_vel=o*0.8
        if bspeed<BALL_SPEED_MAX: bspeed+=BALL_SPEED_INC
        ball.circle.x0=int(ball.posx); ball.circle.y0=int(ball.posy)
        return "HT"

    ball.circle.x0=int(ball.posx)
    ball.circle.y0=int(ball.posy)
    return None

def miss_dist(ball, paddle):
    pc=paddle.posx+HW
    d=abs(ball.posx-pc)-HW
    if d<0: d=0.0
    return d

def train_mode():
    ball,p1,p2=mk()
    rnd=0;hits=0;best=0
    print("=== TRAIN === B=stop")
    while True:
        if clue.button_b:
            ai.save()
            print("Saved R:{} best:{}".format(rnd,best))
            while clue.button_b:pass
            return
        p1.draw(clue.acceleration)
        ai.update(ball,p2,opp_paddle=p1)
        r=step_ball(ball,p1,p2)
        if r=="HB" or r=="HT":
            ai.on_hit()
            hits+=1
            print("HIT",hits,"spd:{:.2f}".format(bspeed))
        elif r=="WIN":
            d=miss_dist(ball,p2)
            ai.on_miss(dist=d)
            if hits>best:best=hits
            rnd+=1
            print("MISS ai r:{} hits:{} best:{} dist:{:.0f}".format(rnd,hits,best,d))
            hits=0
            ball,p1,p2=mk()
        elif r=="LOSE":
            d=miss_dist(ball,p1)
            ai.on_opponent_miss(dist=d)
            if hits>best:best=hits
            rnd+=1
            print("MISS you r:{} hits:{} best:{} dist:{:.0f}".format(rnd,hits,best,d))
            hits=0
            ball,p1,p2=mk()
        time.sleep(DT)

def play_mode():
    ball,p1,p2=mk()
    p_score=0;a_score=0;hits=0;best=0
    print("=== PLAY === A=stop")
    while True:
        if clue.button_a:
            while clue.button_a:pass
            return
        p1.draw(clue.acceleration)
        ai.update(ball,p2,opp_paddle=p1)
        r=step_ball(ball,p1,p2)
        if r=="HB" or r=="HT":
            hits+=1
        elif r=="WIN":
            p_score+=1
            if hits>best:best=hits
            hits=0
            print("YOU {}-{} spd:{:.2f}".format(p_score,a_score,bspeed))
            time.sleep(1)
            ball,p1,p2=mk()
        elif r=="LOSE":
            a_score+=1
            if hits>best:best=hits
            hits=0
            print("AI {}-{} spd:{:.2f}".format(p_score,a_score,bspeed))
            time.sleep(1)
            ball,p1,p2=mk()
        time.sleep(DT)

print("A=train B=play")
mode=None
while True:
    if mode is None:
        if aBtn.pressed(clue.button_a): mode="TRAIN"
        if bBtn.pressed(clue.button_b): mode="PLAY"
        time.sleep(DT)
    elif mode=="TRAIN":
        ai.learning=True
        train_mode()
        mode="PLAY"
    elif mode=="PLAY":
        ai.learning=False
        play_mode()
        mode="TRAIN"
