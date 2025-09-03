from turtle import Turtle
import pygame
import time
import math
from enum import Enum,auto#enumerate
from COLORS import Colors
pygame.init()
WIDTH=600
HEIGHT=WIDTH*1
MAX_LIFE=3
pygame.display.set_caption("打砖块")
screen=pygame.Surface((WIDTH,HEIGHT))
physical_screen=pygame.display.set_mode((600,600),pygame.RESIZABLE)
clock=pygame.time.Clock()

brick_imgs={
    "blue":pygame.image.load("kenney_puzzle-pack\png\element_blue_rectangle.png").convert_alpha(),
    "green":pygame.image.load("kenney_puzzle-pack\png\element_green_rectangle.png").convert_alpha(),
    "grey":pygame.image.load("kenney_puzzle-pack\png\element_grey_rectangle.png").convert_alpha(),
    "purple":pygame.image.load("kenney_puzzle-pack\png\element_purple_rectangle.png").convert_alpha(),
    "red":pygame.image.load("kenney_puzzle-pack\png\element_red_rectangle.png").convert_alpha(),
    "yellow":pygame.image.load("kenney_puzzle-pack\png\element_yellow_rectangle.png").convert_alpha(),
}
volume_on_img=pygame.image.load(r"kenney_puzzle-pack\volume-high.svg").convert_alpha()
volume_off_img=pygame.image.load(r"kenney_puzzle-pack\volume-off.svg").convert_alpha()
fullscreen_img=pygame.image.load(r"kenney_puzzle-pack\fullscreen.svg").convert_alpha()
fullscreen_exit_img=pygame.image.load(r"kenney_puzzle-pack\fullscreen-exit.svg").convert_alpha()
ball_img=pygame.image.load(r"kenney_puzzle-pack\png\ballBlue.png").convert_alpha()

brick_sound=pygame.mixer.Sound(r"sound\audio_593a2d86e9.mp3")


class GameState(Enum):
    GAMING=0
    PAUSE=1
    END=2

def squa_distance(p1,p2):
    return sum(pow(a-b,2) for a,b in zip(p1,p2))
def normalize_range(range):
    return range%360 if not 0<=range<360 else range
def angle_change(wall,angle):
    if not 0<=wall<180:
        raise ValueError(f"wall参数必须在[0,180)范围内，当前值: {wall}")
    return normalize_range(360+2*wall-angle)

class Paddle:
    __slots__=("width","height","pos_x","velocity","pos_y","rect","color")

    def __init__(self,width,height,velocity=10,pos_x=WIDTH//2,pos_y=0.92*HEIGHT,color=Colors.BLACK):
        self.width=width
        self.height=height
        self.pos_x=pos_x
        self.velocity=velocity
        self.pos_y=pos_y
        self.rect=pygame.Rect(self.pos_x,self.pos_y,self.width,self.height)
        self.color=color
    def draw(self):
        pygame.draw.rect(screen,self.color,self.rect)
    def move(self):
        if pygame.key.get_pressed()[pygame.K_LEFT] and self.rect.left>=0:
            self.rect.left-=self.velocity
        if pygame.key.get_pressed()[pygame.K_RIGHT] and self.rect.right<=WIDTH:
            self.rect.right+=self.velocity
brick_radius=pow(pow(brick_imgs["blue"].get_rect().width,2)+pow(brick_imgs["blue"].get_rect().height,2),0.5)/2  
class Brick:
    __slots__=("x","y","image","rect","btype","is_visible","radius")
    class BType(Enum):
        NORMAL=auto()
        BALL=auto()
        TNT=auto()

    def __init__(self,x,y,image:pygame.Surface,brick_type,is_visible=True) -> None:
        self.x=x
        self.y=y
        self.image=image
        self.rect=pygame.Rect(x,y,image.get_width(),image.get_height())
        self.btype=brick_type
        self.is_visible=is_visible
        self.radius=brick_radius
    def draw(self):
        if self.is_visible:
                screen.blit(self.image,(self.x,self.y))
                if self.btype==Brick.BType.NORMAL:
                    pass
                elif self.btype==Brick.BType.BALL:
                    pygame.draw.circle(screen,Colors.SNOW,self.rect.center,radius=self.rect.height/2-6,width=3)


                elif self.btype==Brick.BType.TNT:
                    text=pygame.font.SysFont('simhei',16).render("TNT",True,Colors.RED)
                    text_rect=text.get_rect(center=self.rect.center)
                    screen.blit(text,text_rect)

     
    @staticmethod       
    def creat_bricks():
        bricks=[]
        left_margin=(WIDTH-(67*8-64))//2
        brick_type=Brick.BType.NORMAL
        for i in range(4):
            for j in range(7):

                if i == 0:
                    brick_img=brick_imgs["blue"]
                elif i == 1:
                    brick_img=brick_imgs["red"]
                elif i == 2:
                    brick_img=brick_imgs["yellow"]
                elif i == 3:
                    brick_img=brick_imgs["green"]
                    brick_type=Brick.BType.NORMAL


                brick=Brick(67*j+left_margin,34*i+60,brick_img,brick_type=brick_type)
                bricks.append(brick)
        
        return bricks
    @staticmethod
    def draw_bricks(bricks:list[object]):
        for brick in bricks:
            if brick.is_visible==True:
                brick.draw()
class Ball:
    __slots__=("velocity","_angle","image","is_move","rect","x","y","radius")
    def __init__(self,position:tuple,velocity=0,angle=40.0,image=None,is_move=False):
        self.velocity=velocity
        self._angle=angle
        self.image=image
        self.is_move=is_move

        self.rect=self.image.get_rect()
        self.rect.center=position
        # 添加浮点位置属性以保持精度
        self.x = float(position[0])
        self.y = float(position[1])
        self.radius=self.rect.width/2#11    
    @property#监控角度方便调试
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self,new_val):
        print(f"angle从{self._angle:.2f}变为{new_val:.2f}")
        self._angle = new_val
    def move_to_paddle(self,paddle:Paddle):#重置小球位置
        self.is_move = False
        self.rect.center = (paddle.rect.centerx, paddle.rect.centery - 25)
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
    def draw(self):
        screen.blit(self.image,self.rect)
    def move(self):
        if self.is_move:
            # 使用浮点位置更新
            self.x += self.velocity*math.cos(math.radians(self.angle))
            self.y -= self.velocity*math.sin(math.radians(self.angle))
            # 四舍五入后更新rect位置
            self.rect.centerx = round(self.x)
            self.rect.centery = round(self.y)
    def collision(self,paddle:Paddle,bricks:list[Brick]=None):
        #边界碰撞
        if self.rect.right>=WIDTH and (self.angle<90 or self.angle>270):
            self.angle=angle_change(90,self.angle)
        elif self.rect.left<=0 and 90<self.angle<270:
            self.angle=angle_change(90,self.angle)
        elif self.rect.top<=0 and self.angle<180:
            self.angle=angle_change(0,self.angle)
        elif self.rect.bottom>=HEIGHT:
            life_change(-1,self)

        
        #挡板碰撞
        if self.rect.colliderect(paddle.rect):
            if self.angle>180:#防止重复判断
                print('碰撞挡板',end=':')
                return self.collision_paddle(paddle)
        #砖块碰撞
        for brick in bricks:
            #print(self.rect.center,brick.rect.center)
            if brick.is_visible and self.rect.colliderect(brick.rect) and squa_distance(self.rect.center,brick.rect.center)<=pow(self.radius+brick_radius,2):
                print("碰撞砖块",end=':')
                brick.is_visible=False#砖块消失
                self.collision_rect(brick)
                bricks.remove(brick)#必须带break，否则会吃掉下一个循环
                break#一次只处理一个砖块，可能处理不了同时碰撞两个砖块的情况
    def collision_paddle(self,obj):#挡板碰撞函数
        collision_pos=self.rect.centerx-obj.rect.centerx
        x=collision_pos
        MAX=self.radius+obj.rect.width/2
        print(f'碰撞点：{x}，最大距离：{MAX}')
        #y = 90 - 60 * (x / MAX)**2 * (1 if x >= 0 else -1)#二次函数
        #y = 90 - 45 * (2 ** (x / MAX) - 1) if x >= 0 else 90 + 45 * (2 ** (-x / MAX) - 1)#指数
        y=-0.95*x+90#线性
        
        self.angle=y
        print("碰撞挡板结束")
    def collision_rect(self,brick):#矩形碰撞小球函数
        if brick.rect.left<=self.rect.centerx<=brick.rect.left+brick.rect.width:#上下碰撞
            self.angle=angle_change(0,self.angle)
        elif brick.rect.top<=self.rect.centery<=brick.rect.top+brick.rect.height:#左右碰撞
            self.angle=angle_change(90,self.angle)
        else:
            vertex_index,vertex=min(enumerate([squa_distance(self.rect.center,(brick.rect.left,brick.rect.top)),#左上顶点
                                squa_distance(self.rect.center,(brick.rect.left+brick.rect.width,brick.rect.top)),#右上顶点
                                squa_distance(self.rect.center,(brick.rect.left,brick.rect.top+brick.rect.height)),#左下顶点
                                squa_distance(self.rect.center,(brick.rect.left+brick.rect.width,brick.rect.top+brick.rect.height))]),#右下顶点
                                key=lambda x:x[1])
            # print(vertex_index)
            if vertex_index==0 or vertex_index==2:
                wall=math.degrees(math.asin(abs(self.rect.centerx-brick.rect.left)/math.sqrt(vertex)))
            else:
                wall=math.degrees(math.asin(abs(self.rect.centerx-brick.rect.left-brick.rect.width)/math.sqrt(vertex)))
            if vertex_index==1 or vertex_index==2:
                wall=180-wall
            self.angle=angle_change(wall,self.angle)
        brick_sound.play()
        print("碰撞砖块结束")
            #k=-1/()
    def dead(self):
        return 

class LifeBall:
    class State(Enum):
        LIVE=auto()
        SHRINK=auto()
        EXPAND=auto()
        DEAD=auto()
    def __init__(self,position:tuple[int,int],radius:int,color,width:int):

        self.x,self.y=position
        self.radius=radius
        self.max_radius=radius
        self.color=color
        self.width=width
        self.is_shrinking=False
        self.shrink_time=0.8
        self.target_radius=0
        self.state=LifeBall.State.LIVE
    #收缩动画
    def start_ani_shrink(self):
        self.state=LifeBall.State.SHRINK
        self.radius-=self.width
        self.shrink_speed=(self.radius-self.target_radius)/self.shrink_time
    def update_ani_shrink(self,dt):
        shrink_frame_speed=self.shrink_speed*dt/1000
        self.radius-=shrink_frame_speed
        if self.radius<=self.target_radius:
            self.radius=self.target_radius
            self.state=LifeBall.State.DEAD

            return self.finish_animation()

    #充填动画
    def start_ani_expand(self):
        self.state=LifeBall.State.EXPAND
        self.expand_speed=(self.max_radius-self.radius)/self.shrink_time
    def update_ani_expand(self,dt):
        expand_frame_speed=self.expand_speed*dt/1000
        self.radius+=expand_frame_speed
        if self.radius>=self.max_radius:
            self.radius=self.max_radius
            self.state=LifeBall.State.LIVE
            return self.finish_animation()
    def finish_animation(self):
        pass       
        
    def draw(self,screen):
        if self.state==LifeBall.State.LIVE:
            pygame.draw.circle(screen,self.color,(self.x,self.y),self.radius)
        elif self.state==LifeBall.State.DEAD:
            pygame.draw.circle(screen,self.color,(self.x,self.y),self.max_radius,self.width)
        else:
            pygame.draw.circle(screen,self.color,(self.x,self.y),self.radius)
            pygame.draw.circle(screen,self.color,(self.x,self.y),self.max_radius,self.width)

    @staticmethod
    def create_life_balls(amount):
        top=13
        color=Colors.PINK
        width=2
        radius=10
        left_margin=19
        space=10 
        life_balls=[]
        for i in range(amount):
            life_ball=LifeBall((left_margin+i*(radius*2+space),top+radius),radius,color,width)
            life_balls.append(life_ball)
        return life_balls
    @staticmethod
    def draw_life_balls(screen,life_balls,dt):
        for life_ball in life_balls:
            if life_ball.state==LifeBall.State.EXPAND:
                life_ball.update_ani_expand(dt)
            elif life_ball.state==LifeBall.State.SHRINK:
                life_ball.update_ani_shrink(dt)
            life_ball.draw(screen)

class Button():
    def __init__(self,image:pygame.Surface,image_pressed:pygame.Surface,rect:pygame.Rect):
        self.image=image
        self.image_pressed=image_pressed
        self.rect=rect
        self.is_hover=False
        self.is_pressed=False
    def update(self,event:pygame.event.Event):
        pass
    def draw(self):
        pass
class FullscreenButton(Button):
    def __init__(self,image:pygame.Surface,image_pressed:pygame.Surface,rect:pygame.Rect):

        super().__init__(image,image_pressed,rect)
    def update(self,event:pygame.event.Event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(mouse_get_pos()):

                self.on_click()
                
    def on_click(self):
        self.is_pressed=True if self.is_pressed==False else False
        pygame.display.toggle_fullscreen()#切换显示模式
        print("切换显示模式")
    def draw(self,screen):
        if self.is_pressed:
            image=pygame.transform.scale(self.image_pressed,(self.rect.width,self.rect.height))
            screen.blit(image,self.rect)
        else:
            image=pygame.transform.scale(self.image,(self.rect.width,self.rect.height))
            screen.blit(image,self.rect)
class VolumeButton(Button):
    def __init__(self,image:pygame.Surface,image_pressed:pygame.Surface,rect:pygame.Rect):

        super().__init__(image,image_pressed,rect)
    def update(self,event:pygame.event.Event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(mouse_get_pos()):
                self.on_click()
                
    def on_click(self):
        
        self.is_pressed=True if self.is_pressed==False else False
        if self.is_pressed:
            pygame.mixer.pause
            print("暂停播放所有声道")
        else:
            pygame.mixer.unpause
            print("恢复播放所有声道")
    def draw(self,screen):
        if self.is_pressed:
            image=pygame.transform.scale(self.image_pressed,(self.rect.width,self.rect.height))
            screen.blit(image,self.rect)
        else:
            image=pygame.transform.scale(self.image,(self.rect.width,self.rect.height))
            screen.blit(image,self.rect)





def draw_top_ui(screen):
    fullscreen_button.draw(screen)
    volumebutton.draw(screen)
def life_change(change:int,ball:Ball):
    global life
    global pre_life
    global current_state
    life_is_change=True
    pre_life=life
    life+=change

    print(f"生命值变化{change}，剩余生命值: {life}")

    # 检查游戏是否结束
    if life <= 0:
        current_state = GameState.END
        print("游戏结束，生命值耗尽!")
    #生命球动画 
    if life<pre_life:
        life_balls[pre_life-1-1].start_ani_shrink()
    else:
            life_balls[life-1-1].start_ani_expand()
    ball.is_move=False

def draw_to_real_screen(physical_screen,virtual_canvas):
    global mouse_get_pos
    phys_h=physical_screen.get_height()
    phys_w=physical_screen.get_width()
    virt_h=virtual_canvas.get_height()
    virt_w=virtual_canvas.get_width()
    scale_ratio=min(phys_h/virt_h,phys_w/virt_w)
    scale_w=int(virt_w*scale_ratio)
    scale_h=int(virt_h*scale_ratio)
    canvas=pygame.transform.scale(virtual_canvas,(scale_w,scale_h))
    physical_screen.fill(Colors.BLACK)
    physical_screen.blit(canvas,((phys_w-scale_w)//2,(phys_h-scale_h)//2))
    mouse_get_pos=create_mouse_get_pos(scale_ratio,scale_w,scale_h,phys_w,phys_h)

def create_mouse_get_pos(scale_ratio=1,scale_w=0,scale_h=0,phys_w=0,phys_h=0):
    def mouse_get_pos():
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_x = (mouse_pos[0]-(phys_w-scale_w)/2)/ scale_ratio
        mouse_pos_y = (mouse_pos[1]-(phys_h-scale_h)/2 )/ scale_ratio
        return mouse_pos_x,mouse_pos_y
    return mouse_get_pos

mouse_get_pos=create_mouse_get_pos()
top=13
volumebutton=VolumeButton(volume_on_img,volume_off_img,pygame.Rect(560,top,21,21))
fullscreen_button=FullscreenButton(fullscreen_img,fullscreen_exit_img,pygame.Rect(510,top,21,21))
paddle0=Paddle(0.191*WIDTH,0.0193*HEIGHT,color=Colors.LIGHTGREEN)
ball0=Ball(position=(paddle0.rect.centerx, paddle0.rect.centery-30),angle=90,image=ball_img,is_move=False)
bricks=Brick.creat_bricks()
life_balls=LifeBall.create_life_balls(MAX_LIFE)
life=MAX_LIFE+1
life_change(-1,ball0)


current_state= GameState.GAMING
while current_state==GameState.GAMING:
    dt=clock.tick(100)
    #定义速度
    ball0.velocity=380*dt/1000
    paddle0.velocity=580*dt/1000
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            current_state=GameState.END
        if event.type==pygame.MOUSEBUTTONDOWN:
            fullscreen_button.update(event)
            volumebutton.update(event)
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:#空格控制球的移动
                if ball0.is_move==False:
                    ball0.angle=45
                    ball0.is_move=True
                else:
                    ball0.is_move=False

    if(len(bricks)==0):
        pass

    #背景渲染
    screen.fill(Colors.BLACK)    

    #碰撞检测+移动
    if ball0.is_move:
        ball0.collision(paddle0,bricks)
        ball0.move()
        paddle0.move()
    else:
        paddle0.move()
        ball0.move_to_paddle(paddle0)
    #调试碰撞
    # if ball0.is_move==0:
    #     mouse_pos = mouse_get_pos()
    #     ball0.x = float(mouse_pos[0])
    #     ball0.y = float(mouse_pos[1])
    #     ball0.rect.center = (round(ball0.x), round(ball0.y))

    #ui
    draw_top_ui(screen)
    LifeBall.draw_life_balls(screen,life_balls,dt)
    #绘制砖块
    Brick.draw_bricks(bricks)
    #绘制球
    ball0.draw()
    #绘制挡板
    paddle0.draw()
    
    draw_to_real_screen(physical_screen,screen)
    pygame.display.flip()