import pygame, sys, random, time, json, winsound
from math import floor
from threading import Thread
from data import icon_data
mode = "set mode"

class String:
    string : str
    is_red : bool
    def __init__(self, string : str, is_red=False) -> None:
        self.string = string
        self.is_red = is_red
    def clear(self):
        self.is_red = False
        return self

months = {
    "Jan" : "January",
    "Feb" : "February",
    "Mar" : "March",
    "Apr" : "April",
    "May" : "May",
    "Jun" : "June",
    "Jul" : "July",
    "Aug" : "August",
    "Sep" : "September",
    "Oct" : "October",
    "Nov" : "November",
    "Dec" : "December"
}

weeks = {
    "Sun" : "Sunday",
    "Mon" : "Monday",
    "Tue" : "Tuesday",
    "Wed" : "Wednesday",
    "Thu" : "Thursday",
    "Fri" : "Friday",
    "Sat" : "Saturday"
}

number_position = [0, 4, 8, 10, 14, 18, 20, 24]
chars = '''0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&"()*+,-./:;<=>?@[\\]^_`{|}~'''
pygame.init()
icon = pygame.image.fromstring(icon_data, (256, 256), "RGBA")
pygame.display.set_icon(icon)
window = pygame.display.set_mode(flags=pygame.FULLSCREEN)
pygame.display.set_caption("Hacker clock.")
window_width, window_height = pygame.display.get_window_size()
font_size = 16
default_settings = '''{\n\t"raindrop" : 3.0,\n\t"layout" : "%dx%d",\n\t"length" : 0.6,\n\t"fps" : 16\n}'''%(window_width//font_size, window_height//font_size)
try:
    with open("settings", "r", encoding="u8") as f:settings = json.load(f)
    font_size = window_width//int(settings["layout"].split("x")[0])
    layout = int(settings["layout"].split("x")[0])
    length = float(settings["length"])
    raindrop = float(settings["raindrop"])
    fps = int(settings["fps"])
except (FileNotFoundError, KeyError, ValueError):
    with open("settings", "w", encoding="u8") as f:f.write(default_settings)
    settings = json.loads(default_settings)
    font_size = window_width//int(settings["layout"].split("x")[0])
    layout = int(settings["layout"].split("x")[0])
    length = float(settings["length"])
    raindrop = float(settings["raindrop"])
    fps = int(settings["fps"])

font = pygame.font.Font("unifont-15.1.04.otf", font_size)
font.bold = True
data = [String(random.choice(chars)) for i in range(window_width*window_height//font_size**2)]
show = []
rain_is_display = True
clock_is_display = True
pixel_size = window_width//font_size//27
menu_is_display = False
clock_startX = (window_width//font_size-pixel_size*27)//2
clock_startY = (window_height//font_size-pixel_size*5)//2
clock_over = False
frame_continue = False
over_time = -1
beep = lambda winsound_frequency, winsound_duration: Thread(target=winsound.Beep, args=(winsound_frequency, winsound_duration)).start()
is_beeping = False
is_quiting = False
cursor = 0
alarm_clock_str = ""
is_in_alarm = False
display = 0
display_list = ["雨滴 & 时钟", "仅时钟", "仅雨滴"]

def number(num : str, x, y, color, is_chars=True):
    global pixel_size
    def rect(x1, y1, x2, y2, color, is_chars=True):
        global window
        if is_chars:
            for x in range(x1, x2):
                for y in range(y1,y2):
                    data[x*(window_height//font_size)+y].is_red = True
                    textSurface = font.render(data[x*(window_height//font_size)+y].string, False, color)
                    window.blit(textSurface, (x*font_size, y*font_size))
        else:
            pygame.draw.rect(window, color, (x1*font_size, y1*font_size, abs(x1-x2)*font_size, abs(y1-y2)*font_size))
    numbers = [
    "111 101 101 101 111",
    "010 110 010 010 010",
    "111 001 111 100 111",
    "111 001 011 001 111",
    "101 101 111 001 001",
    "111 100 111 001 111",
    "111 100 111 101 111",
    "111 001 001 001 001",
    "111 101 111 101 111",
    "111 101 111 001 111",
    "01010"
    ]
    if num in "0123456789":
        for i in range(5):
            for j in range(3):
                if numbers[int(num)].split()[i][j] == "1":
                    rect(x+j*pixel_size, y+i*pixel_size, x+j*pixel_size+pixel_size, y+i*pixel_size+pixel_size, color, is_chars)
    elif num == ":":
        for i in range(5):
            if numbers[10][i] == "1":
                rect(x, y+i*pixel_size, x+pixel_size, y+i*pixel_size+pixel_size, color, is_chars)

def reset(is_changing_layout=False):
    global show, data, window, pixel_size, clock_startX, clock_startY, raindrop, fps, time_start, clock_over, now_str, past_str, is_pausing, past_time, over_time, is_beeping
    window = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    pixel_size = window_width//font_size//27
    clock_startX = (window_width//font_size-pixel_size*27)//2
    clock_startY = (window_height//font_size-pixel_size*5)//2
    show = []
    data = [String(random.choice(chars)) for i in range(window_width*window_height//font_size**2)]
    if not is_changing_layout:
        is_beeping = False
        over_time = -1
        clock_over = False
        time_start = time.time()
    if mode == "positive timer":
        if not is_changing_layout:is_pausing = True
        past_str = "00:00:00"
        past_time = time.time()
    elif mode == "countdown timer":
        if not is_changing_layout:is_pausing = True
        past_str = str(floor(target)//3600).zfill(2) + ":" + str(floor(target) % 3600 // 60).zfill(2) + ":" + str(floor(target) % 60).zfill(2)
        past_time = time.time()

def inrange(number, min, max):
    return number >= min and number <= max

def menu():
    pygame.draw.rect(window, pygame.Color(0, 255, 0), (window_width*0.15, window_height*0.15, window_width*0.7, window_height*0.7), 10)
    settings_font = pygame.font.Font("unifont-15.1.04.otf", floor(window_height*0.05))
    settings_font.bold = False

    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.175, window_height*0.225):
        pygame.draw.rect(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.175, window_width*0.6, window_height*0.05))
        textSurface = settings_font.render("频率", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.2))))
        textSurface = settings_font.render(str(raindrop), False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.2))))
    else:
        textSurface = settings_font.render("频率", False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.2))))
        textSurface = settings_font.render(str(raindrop), False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.2))))

    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.275, window_height*0.325):
        pygame.draw.rect(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.275, window_width*0.6, window_height*0.05))
        textSurface = settings_font.render("布局", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.3))))
        textSurface = settings_font.render(str(layout) + "x" + str(floor(window_height/window_width*layout)), False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.3))))
    else:
        textSurface = settings_font.render("布局", False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.3))))
        textSurface = settings_font.render(str(layout) + "x" + str(floor(window_height/window_width*layout)), False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.3))))
    
    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.375, window_height*0.425):
        pygame.draw.rect(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.375, window_width*0.6, window_height*0.05))
        textSurface = settings_font.render("长度", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.4))))
        textSurface = settings_font.render(str(round(length*100)) +"%", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.4))))
    else:
        textSurface = settings_font.render("长度", False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.4))))
        textSurface = settings_font.render(str(round(length*100)) +"%", False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.4))))

    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.475, window_height*0.525):
        pygame.draw.rect(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.475, window_width*0.6, window_height*0.05))
        textSurface = settings_font.render("显示", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.5))))
        textSurface = settings_font.render(display_list[display%3], False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.5))))
    else:
        textSurface = settings_font.render("显示", False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.325, window_height*0.5))))
        textSurface = settings_font.render(display_list[display%3], False, pygame.Color(0, 255, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.675, window_height*0.5))))

    pygame.draw.line(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.55), (window_width*0.8, window_height*0.55), 5)
    
    if mode != "set mode":
        if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.575, window_height*0.625):
            pygame.draw.rect(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.575, window_width*0.6, window_height*0.05))
            textSurface = settings_font.render("设置模式", False, pygame.Color(0, 0, 0))
            window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.5, window_height*0.6))))
        else:
            textSurface = settings_font.render("设置模式", False, pygame.Color(0, 255, 0))
            window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.5, window_height*0.6))))

    if mode not in ["set mode", "set alarm clock", "set countdown timer", "positive timer"]:
        if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.675, window_height*0.725):
            pygame.draw.rect(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.675, window_width*0.6, window_height*0.05))
            textSurface = settings_font.render("设置闹钟" if mode == "clock" else "设置倒计时", False, pygame.Color(0, 0, 0))
            window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.5, window_height*0.7))))
        else:
            textSurface = settings_font.render("设置闹钟" if mode == "clock" else "设置倒计时", False, pygame.Color(0, 255, 0))
            window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.5, window_height*0.7))))
            
    pygame.draw.line(window, pygame.Color(0, 255, 0), (window_width*0.2, window_height*0.75), (window_width*0.8, window_height*0.75), 5)

    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.775, window_height*0.825):
        pygame.draw.rect(window, pygame.Color(255, 0, 0), (window_width*0.2, window_height*0.775, window_width*0.6, window_height*0.05))
        textSurface = settings_font.render("退出", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.5, window_height*0.8))))
    else:
        textSurface = settings_font.render("退出", False, pygame.Color(255, 0, 0))
        window.blit(textSurface, (textSurface.get_rect(center=(window_width*0.5, window_height*0.8))))

def quit():
    settings_font = pygame.font.Font("unifont-15.1.04.otf", window_width//50)
    settings_font.bold = False
    pygame.draw.rect(window, pygame.Color(0, 0, 0), (window_width//3, window_height//3, window_width//3, window_height//3))
    pygame.draw.rect(window, pygame.Color(255, 0, 0), (window_width//3, window_height//3, window_width//3, window_height//3), 5)
    textSurface = settings_font.render("你确定要退出吗？", False, pygame.Color(255, 0, 0))
    window.blit(textSurface, (textSurface.get_rect(center=window.get_rect().center)[0], textSurface.get_rect(center=window.get_rect().center)[1]*0.85))

    if inrange(pygame.mouse.get_pos()[0], window_width*(3/8), window_width*(11/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.55, window_height*0.65):
        pygame.draw.rect(window, pygame.Color(255, 0, 0), (window_width*(3/8), window_height*0.55, window_width*1/12, window_height*0.1))
        textSurface = settings_font.render("确定", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, textSurface.get_rect(center=(window_width*5/12, window_height*0.6)))
    else:
        textSurface = settings_font.render("确定", False, pygame.Color(255, 0, 0))
        window.blit(textSurface, textSurface.get_rect(center=(window_width*5/12, window_height*0.6)))

    if inrange(pygame.mouse.get_pos()[0], window_width*(13/24), window_width*(5/8)) and inrange(pygame.mouse.get_pos()[1], window_height*0.55, window_height*0.65):
        pygame.draw.rect(window, pygame.Color(255, 0, 0), (window_width*(13/24), window_height*0.55, window_width*1/12, window_height*0.1))
        textSurface = settings_font.render("取消", False, pygame.Color(0, 0, 0))
        window.blit(textSurface, textSurface.get_rect(center=(window_width*7/12, window_height*0.6)))
    else:
        textSurface = settings_font.render("取消", False, pygame.Color(255, 0, 0))
        window.blit(textSurface, textSurface.get_rect(center=(window_width*7/12, window_height*0.6)))

now = time.time()
time_difference = 0
past_time = time.time()
while True:
    pygame.time.Clock().tick(fps)
    window.fill(pygame.Color(0, 0, 0))
    data = [data[i].clear() for i in range(window_width*window_height//font_size**2)]
    if mode in ["set mode", "set countdown timer", "set alarm clock"] or menu_is_display or is_quiting:pygame.mouse.set_visible(True)
    else:pygame.mouse.set_visible(False)

    if display == 0:rain_is_display, clock_is_display = True, True
    elif display == 1:rain_is_display, clock_is_display = False, True
    else:rain_is_display, clock_is_display = True, False

    if menu_is_display and not is_quiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:is_quiting = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    menu_is_display = not menu_is_display
                elif e.key in [pygame.K_UP, pygame.K_w]:
                    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.175, window_height*0.225):
                        raindrop += 0.1
                        raindrop = round(raindrop, 1)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.275, window_height*0.325):
                        layout += 1
                        font_size = window_width // layout
                        font = pygame.font.Font("unifont-15.1.04.otf", font_size)
                        reset(True)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.375, window_height*0.425):
                        length += 0.1
                        length = round(length, 1)
                elif e.key in [pygame.K_DOWN, pygame.K_s]:
                    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.175, window_height*0.225):
                        raindrop -= 0.1
                        raindrop = round(raindrop, 1)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.275, window_height*0.325):
                        layout -= 1
                        font_size = window_width // layout
                        font = pygame.font.Font("unifont-15.1.04.otf", font_size)
                        reset(True)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.375, window_height*0.425):
                        length -= 0.1
                        length = round(length, 1)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.575, window_height*0.625) and mode != "set mode":
                        mode = "set mode"
                        time_difference = 0
                        menu_is_display = False
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.675, window_height*0.725) and mode not in ["set mode", "set alarm clock", "set countdown timer", "positive timer"]:
                        if mode == "clock":mode = "set alarm clock"
                        elif mode == "countdown timer":mode = "set countdown timer"
                        time_difference = 0
                        menu_is_display = False
                        if mode == "set alarm clock" and alarm_clock_str != "":now_str = alarm_clock_str
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.775, window_height*0.825):
                        is_quiting = True
                    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.175, window_height*0.225):
                        raindrop = 3.0
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.275, window_height*0.325):
                        font_size = 16
                        layout = window_width//font_size
                        font = pygame.font.Font("unifont-15.1.04.otf", font_size)
                        reset(True)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.375, window_height*0.425):
                        length = 0.6
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.475, window_height*0.525):
                        display += 1
                        display %= 3
                if e.button == 4:
                    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.175, window_height*0.225):
                        raindrop += 0.1
                        raindrop = round(raindrop, 1)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.275, window_height*0.325):
                        layout += 1
                        font_size = window_width // layout
                        font = pygame.font.Font("unifont-15.1.04.otf", font_size)
                        reset(True)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.375, window_height*0.425):
                        length += 0.1
                        length = round(length, 1)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.475, window_height*0.525):
                        display -= 1
                        display %= 3
                elif e.button == 5:
                    if inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.175, window_height*0.225):
                        raindrop -= 0.1
                        raindrop = round(raindrop, 1)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.275, window_height*0.325):
                        layout -= 1
                        font_size = window_width // layout
                        font = pygame.font.Font("unifont-15.1.04.otf", font_size)
                        reset(True)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.375, window_height*0.425):
                        length -= 0.1
                        length = round(length, 1)
                    elif inrange(pygame.mouse.get_pos()[0], window_width*0.25, window_width*0.75) and inrange(pygame.mouse.get_pos()[1], window_height*0.475, window_height*0.525):
                        display += 1
                        display %= 3

    if is_quiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                settings = '''{\n\t"raindrop" : %.1f,\n\t"layout" : "%dx%d",\n\t"length" : %.1f,\n\t"fps" : %d\n}'''%(raindrop, layout, floor(window_height/window_width*layout), length, fps)
                with open("settings", "w", encoding="u8") as f:f.write(settings)
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:is_quiting = False
                elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    settings = '''{\n\t"raindrop" : %.1f,\n\t"layout" : "%dx%d",\n\t"length" : %.1f,\n\t"fps" : %d\n}'''%(raindrop, layout, floor(window_height/window_width*layout), length, fps)
                    with open("settings", "w", encoding="u8") as f:f.write(settings)
                    sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if inrange(pygame.mouse.get_pos()[0], window_width*(3/8), window_width*(11/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.55, window_height*0.65):
                        settings = '''{\n\t"raindrop" : %.1f,\n\t"layout" : "%dx%d",\n\t"length" : %.1f,\n\t"fps" : %d\n}'''%(raindrop, layout, floor(window_height/window_width*layout), length, fps)
                        with open("settings", "w", encoding="u8") as f:f.write(settings)
                        sys.exit()
                    elif inrange(pygame.mouse.get_pos()[0], window_width*(13/24), window_width*(5/8)) and inrange(pygame.mouse.get_pos()[1], window_height*0.55, window_height*0.65):
                        is_quiting = False

    if mode == "set mode":
        if not menu_is_display:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:menu_is_display = not menu_is_display
                elif e.type == pygame.QUIT:is_quiting = True
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        if inrange(pygame.mouse.get_pos()[0], window_width*0.2, window_width*0.8) and inrange(pygame.mouse.get_pos()[1], window_height*0.25, window_height*0.35):
                            mode = "clock"
                            is_pausing = False
                        elif inrange(pygame.mouse.get_pos()[0], window_width*0.2, window_width*0.8) and inrange(pygame.mouse.get_pos()[1], window_height*0.45, window_height*0.55):
                            mode = "positive timer"
                            is_pausing = True
                            past_str = "00:00:00"
                            past_time = time.time()
                            time_start = time.time()
                        elif inrange(pygame.mouse.get_pos()[0], window_width*0.2, window_width*0.8) and inrange(pygame.mouse.get_pos()[1], window_height*0.65, window_height*0.75):
                            reset()
                            mode = "set countdown timer"
                            now_str = "00:00:00"
                            is_pausing = False
        pygame.draw.rect(window, pygame.Color(255 if not menu_is_display else 127, 0, 0), (window_width*0.2, window_height*0.2, window_width*0.6, window_height*0.6), 10)
        settings_font = pygame.font.Font("unifont-15.1.04.otf", floor(window_height*0.03))
        settings_font.bold = False
        textSurface = settings_font.render("使用鼠标单击以选择一个模式", False, pygame.Color(0, 255 if not menu_is_display else 127, 0))
        window.blit(textSurface, (window_width*0.1, window_height*0.1))
        author_font = pygame.font.Font("unifont-15.1.04.otf", floor(window_height*0.05))
        author_font.bold = True
        textSurface = author_font.render("By Jack Peng", False, pygame.Color(255 if not menu_is_display else 127, 0, 0))
        text_rect = textSurface.get_rect(center=window.get_rect().center)
        text_rect[1] = floor(text_rect[1] * 1.8)
        window.blit(textSurface, text_rect)
        settings_font = pygame.font.Font("unifont-15.1.04.otf", floor(window_height*0.1))
        settings_font.bold = False
        if not inrange(pygame.mouse.get_pos()[0], window_width*0.2, window_width*0.8) or not inrange(pygame.mouse.get_pos()[1], window_height*0.25, window_height*0.35):
            textSurface = settings_font.render("时钟", False, pygame.Color(255 if not menu_is_display else 127, 0, 0))
            window.blit(textSurface, (textSurface.get_rect(center=window.get_rect().center)[0], window_height*0.25))
        else:
            pygame.draw.rect(window, pygame.Color(255 if not menu_is_display else 127, 0, 0), (window_width*0.2, window_height*0.25, window_width*0.6, window_height*0.1))
            textSurface = settings_font.render("时钟", False, pygame.Color(0, 0, 0))
            window.blit(textSurface, (textSurface.get_rect(center=window.get_rect().center)[0], window_height*0.25))    
        if not inrange(pygame.mouse.get_pos()[0], window_width*0.2, window_width*0.8) or not inrange(pygame.mouse.get_pos()[1], window_height*0.45, window_height*0.55):
            textSurface = settings_font.render("正计时", False, pygame.Color(255 if not menu_is_display else 127, 0, 0))
            window.blit(textSurface, textSurface.get_rect(center=window.get_rect().center))
        else:
            pygame.draw.rect(window, pygame.Color(255 if not menu_is_display else 127, 0, 0), (window_width*0.2, window_height*0.45, window_width*0.6, window_height*0.1))
            textSurface = settings_font.render("正计时", False, pygame.Color(0, 0, 0))
            window.blit(textSurface, (textSurface.get_rect(center=window.get_rect().center)[0], window_height*0.45))    
        if not inrange(pygame.mouse.get_pos()[0], window_width*0.2, window_width*0.8) or not inrange(pygame.mouse.get_pos()[1], window_height*0.65, window_height*0.75):
            textSurface = settings_font.render("倒计时", False, pygame.Color(255 if not menu_is_display else 127, 0, 0))
            window.blit(textSurface, (textSurface.get_rect(center=window.get_rect().center)[0], window_height*0.65))
        else:
            pygame.draw.rect(window, pygame.Color(255 if not menu_is_display else 127, 0, 0), (window_width*0.2, window_height*0.65, window_width*0.6, window_height*0.1))
            textSurface = settings_font.render("倒计时", False, pygame.Color(0, 0, 0))
            window.blit(textSurface, (textSurface.get_rect(center=window.get_rect().center)[0], window_height*0.65))  

        if menu_is_display:menu()
        if is_quiting:quit()

        pygame.display.update()
        continue
    elif mode == "set countdown timer":
        if not menu_is_display:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        menu_is_display = not menu_is_display
                        continue
                    if e.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_KP_0, pygame.K_KP_1, pygame.K_KP_2, pygame.K_KP_3, pygame.K_KP_4, pygame.K_KP_5, pygame.K_KP_6, pygame.K_KP_7, pygame.K_KP_8, pygame.K_KP_0, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s]:
                        now_str = list(now_str)
                        if e.key in [pygame.K_0, pygame.K_KP_0]:now_str[cursor] = "0"
                        elif e.key in [pygame.K_1, pygame.K_KP_1]:now_str[cursor] = "1"
                        elif e.key in [pygame.K_2, pygame.K_KP_2]:now_str[cursor] = "2"
                        elif e.key in [pygame.K_3, pygame.K_KP_3]:now_str[cursor] = "3"
                        elif e.key in [pygame.K_4, pygame.K_KP_4]:now_str[cursor] = "4"
                        elif e.key in [pygame.K_5, pygame.K_KP_5]:now_str[cursor] = "5"
                        elif e.key in [pygame.K_6, pygame.K_KP_6]:now_str[cursor] = "6"
                        elif e.key in [pygame.K_7, pygame.K_KP_7]:now_str[cursor] = "7"
                        elif e.key in [pygame.K_8, pygame.K_KP_8]:now_str[cursor] = "8"
                        elif e.key in [pygame.K_9, pygame.K_KP_9]:now_str[cursor] = "9"
                        elif e.key in [pygame.K_UP, pygame.K_w] and int(now_str[cursor]) >= 0 and int(now_str[cursor]) < 9:now_str[cursor] = str(int(now_str[cursor])+1)
                        elif e.key in [pygame.K_DOWN, pygame.K_s] and int(now_str[cursor]) > 0 and int(now_str[cursor]) <= 9:now_str[cursor] = str(int(now_str[cursor])-1)
                        now_str = "".join(now_str)
                    
                    if e.key in [pygame.K_LEFT, pygame.K_a]:
                        cursor -= 1
                        if cursor == 2 or cursor == 5:cursor -= 1
                        cursor %= 8
                        continue
                    elif e.key in [pygame.K_RIGHT, pygame.K_d]: 
                        cursor += 1
                        cursor %= 8
                    elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                        target = sum([int(now_str.split(":")[::-1][i]) * 60**i for i in range(len(now_str.split(":")))])
                        mode = "countdown timer"
                        is_pausing = True
                        past_str = str(floor(target - time_difference)//3600).zfill(2) + ":" + str(floor(target - time_difference) % 3600 // 60).zfill(2) + ":" + str(floor(target - time_difference) % 60).zfill(2)
                        time_start = time.time()
                        past_time = time.time()
                        break
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        if inrange(pygame.mouse.get_pos()[0], window_width*(20/24), window_width*(22/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.75, window_height*0.85):
                            target = sum([int(now_str.split(":")[::-1][i]) * 60**i for i in range(len(now_str.split(":")))])
                            mode = "countdown timer"
                            is_pausing = True
                            past_str = str(floor(target - time_difference)//3600).zfill(2) + ":" + str(floor(target - time_difference) % 3600 // 60).zfill(2) + ":" + str(floor(target - time_difference) % 60).zfill(2)
                            time_start = time.time() 
                            past_time = time.time()
                            break
                        elif inrange(pygame.mouse.get_pos()[1], clock_startY*font_size, clock_startY*font_size + pixel_size*5*font_size):
                            if inrange(pygame.mouse.get_pos()[0], clock_startX*font_size, (clock_startX + pixel_size*3)*font_size):cursor = 0
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*4)*font_size, (clock_startX + pixel_size*7)*font_size):cursor = 1
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*10)*font_size, (clock_startX + pixel_size*13)*font_size):cursor = 3
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*14)*font_size, (clock_startX + pixel_size*17)*font_size):cursor = 4
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*20)*font_size, (clock_startX + pixel_size*23)*font_size):cursor = 6
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*24)*font_size, (clock_startX + pixel_size*27)*font_size):cursor = 7
                    elif e.button in [4, 5]:
                        if inrange(pygame.mouse.get_pos()[1], clock_startY*font_size, clock_startY*font_size + pixel_size*5*font_size):
                            if inrange(pygame.mouse.get_pos()[0], clock_startX*font_size, (clock_startX + pixel_size*3)*font_size):cursor = 0
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*4)*font_size, (clock_startX + pixel_size*7)*font_size):cursor = 1
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*10)*font_size, (clock_startX + pixel_size*13)*font_size):cursor = 3
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*14)*font_size, (clock_startX + pixel_size*17)*font_size):cursor = 4
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*20)*font_size, (clock_startX + pixel_size*23)*font_size):cursor = 6
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*24)*font_size, (clock_startX + pixel_size*27)*font_size):cursor = 7
                        now_str = list(now_str)
                        if e.button == 4 and int(now_str[cursor]) >= 0 and int(now_str[cursor]) < 9:now_str[cursor] = str(int(now_str[cursor])+1)
                        elif e.button == 5 and int(now_str[cursor]) > 0 and int(now_str[cursor]) <= 9:now_str[cursor] = str(int(now_str[cursor])-1)
                        now_str = "".join(now_str)

                if e.type == pygame.QUIT:is_quiting = True
        if int(now_str[0:2]) >= 24:
            now_str = list(now_str)
            now_str[0], now_str[1] = "2", "3"
            now_str = "".join(now_str)
        if int(now_str[3:5]) >= 60:
            now_str = list(now_str)
            now_str[3], now_str[4] = "5", "9"
            now_str = "".join(now_str)
        if int(now_str[6:8]) >= 60:
            now_str = list(now_str)
            now_str[6], now_str[7] = "5", "9"
            now_str = "".join(now_str)
        for i in range(8):
            if cursor == 2 or cursor == 5:cursor += 1
            if i != cursor:number(now_str[i], clock_startX+number_position[i]*pixel_size, clock_startY, pygame.Color(255 if not menu_is_display else 127, 0, 0))
            else:
                number(now_str[i], clock_startX+number_position[i]*pixel_size, clock_startY, pygame.Color(255 if not menu_is_display else 127, 0, 0), False)

        if menu_is_display:menu()
        if is_quiting:quit()

        settings_font = pygame.font.Font("unifont-15.1.04.otf", floor(window_height*0.03))
        settings_font.bold = False
        textSurface = settings_font.render("请使用鼠标单击或键盘键入以设置倒计时", False, pygame.Color(0, 255 if not menu_is_display else 127, 0))
        window.blit(textSurface, (window_width*0.1, window_height*0.1))
        if inrange(pygame.mouse.get_pos()[0], window_width*(20/24), window_width*(22/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.75, window_height*0.85):
            pygame.draw.rect(window, pygame.Color(0, 255 if not menu_is_display else 127, 0), (window_width*(20/24), window_height*0.75, window_width*1/12, window_height*0.1))
            textSurface = textSurface = settings_font.render("确定", False, pygame.Color(0, 0, 0))
        else:textSurface = textSurface = settings_font.render("确定", False, pygame.Color(0, 255 if not menu_is_display else 127, 0))
        window.blit(textSurface, textSurface.get_rect(center=(window_width*(21/24), window_height*0.8)))
        pygame.display.update()
        continue
    elif mode == "set alarm clock":
        if not menu_is_display:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        menu_is_display = not menu_is_display
                        continue
                    if e.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_KP_0, pygame.K_KP_1, pygame.K_KP_2, pygame.K_KP_3, pygame.K_KP_4, pygame.K_KP_5, pygame.K_KP_6, pygame.K_KP_7, pygame.K_KP_8, pygame.K_KP_0, pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s]:
                        now_str = list(now_str)
                        if e.key in [pygame.K_0, pygame.K_KP_0]:now_str[cursor] = "0"
                        elif e.key in [pygame.K_1, pygame.K_KP_1]:now_str[cursor] = "1"
                        elif e.key in [pygame.K_2, pygame.K_KP_2]:now_str[cursor] = "2"
                        elif e.key in [pygame.K_3, pygame.K_KP_3]:now_str[cursor] = "3"
                        elif e.key in [pygame.K_4, pygame.K_KP_4]:now_str[cursor] = "4"
                        elif e.key in [pygame.K_5, pygame.K_KP_5]:now_str[cursor] = "5"
                        elif e.key in [pygame.K_6, pygame.K_KP_6]:now_str[cursor] = "6"
                        elif e.key in [pygame.K_7, pygame.K_KP_7]:now_str[cursor] = "7"
                        elif e.key in [pygame.K_8, pygame.K_KP_8]:now_str[cursor] = "8"
                        elif e.key in [pygame.K_9, pygame.K_KP_9]:now_str[cursor] = "9"
                        elif e.key in [pygame.K_UP, pygame.K_w] and int(now_str[cursor]) >= 0 and int(now_str[cursor]) < 9:now_str[cursor] = str(int(now_str[cursor])+1)
                        elif e.key in [pygame.K_DOWN, pygame.K_s] and int(now_str[cursor]) > 0 and int(now_str[cursor]) <= 9:now_str[cursor] = str(int(now_str[cursor])-1)
                        now_str = "".join(now_str)
                    
                    if e.key in [pygame.K_LEFT, pygame.K_a]:
                        cursor -= 1
                        if cursor == 2 or cursor == 5:cursor -= 1
                        cursor %= 8
                        continue
                    elif e.key in [pygame.K_RIGHT, pygame.K_d]: 
                        cursor += 1
                        cursor %= 8
                    elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                        mode = "clock"
                        alarm_clock_str = now_str
                        break
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        if inrange(pygame.mouse.get_pos()[0], window_width*(20/24), window_width*(22/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.75, window_height*0.85):
                            mode = "clock"
                            alarm_clock_str = now_str
                            break
                        elif inrange(pygame.mouse.get_pos()[0], window_width*(17/24), window_width*(19/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.75, window_height*0.85):
                            mode = "clock"
                            alarm_clock_str = ""
                            break
                        elif inrange(pygame.mouse.get_pos()[1], clock_startY*font_size, clock_startY*font_size + pixel_size*5*font_size):
                            if inrange(pygame.mouse.get_pos()[0], clock_startX*font_size, (clock_startX + pixel_size*3)*font_size):cursor = 0
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*4)*font_size, (clock_startX + pixel_size*7)*font_size):cursor = 1
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*10)*font_size, (clock_startX + pixel_size*13)*font_size):cursor = 3
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*14)*font_size, (clock_startX + pixel_size*17)*font_size):cursor = 4
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*20)*font_size, (clock_startX + pixel_size*23)*font_size):cursor = 6
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*24)*font_size, (clock_startX + pixel_size*27)*font_size):cursor = 7
                    elif e.button in [4, 5]:
                        if inrange(pygame.mouse.get_pos()[1], clock_startY*font_size, clock_startY*font_size + pixel_size*5*font_size):
                            if inrange(pygame.mouse.get_pos()[0], clock_startX*font_size, (clock_startX + pixel_size*3)*font_size):cursor = 0
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*4)*font_size, (clock_startX + pixel_size*7)*font_size):cursor = 1
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*10)*font_size, (clock_startX + pixel_size*13)*font_size):cursor = 3
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*14)*font_size, (clock_startX + pixel_size*17)*font_size):cursor = 4
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*20)*font_size, (clock_startX + pixel_size*23)*font_size):cursor = 6
                            elif inrange(pygame.mouse.get_pos()[0], (clock_startX + pixel_size*24)*font_size, (clock_startX + pixel_size*27)*font_size):cursor = 7
                        now_str = list(now_str)
                        if e.button == 4 and int(now_str[cursor]) >= 0 and int(now_str[cursor]) < 9:now_str[cursor] = str(int(now_str[cursor])+1)
                        elif e.button == 5 and int(now_str[cursor]) > 0 and int(now_str[cursor]) <= 9:now_str[cursor] = str(int(now_str[cursor])-1)
                        now_str = "".join(now_str)

                if e.type == pygame.QUIT:is_quiting = True
        if int(now_str[0:2]) >= 24:
            now_str = list(now_str)
            now_str[0], now_str[1] = "2", "3"
            now_str = "".join(now_str)
        if int(now_str[3:5]) >= 60:
            now_str = list(now_str)
            now_str[3], now_str[4] = "5", "9"
            now_str = "".join(now_str)
        if int(now_str[6:8]) >= 60:
            now_str = list(now_str)
            now_str[6], now_str[7] = "5", "9"
            now_str = "".join(now_str)
        if cursor == 2 or cursor == 5:cursor += 1
        for i in range(8):
            if i != cursor:number(now_str[i], clock_startX+number_position[i]*pixel_size, clock_startY, pygame.Color(255 if not menu_is_display else 127, 0, 0))
            else:
                number(now_str[i], clock_startX+number_position[i]*pixel_size, clock_startY, pygame.Color(255 if not menu_is_display else 127, 0, 0), False)

        if menu_is_display:menu()
        if is_quiting:quit()

        settings_font = pygame.font.Font("unifont-15.1.04.otf", window_width//50)
        settings_font.bold = False
        textSurface = settings_font.render("请使用鼠标单击或键盘键入以设置闹钟", False, pygame.Color(0, 255 if not menu_is_display else 127, 0))
        window.blit(textSurface, (window_width*0.1, window_height*0.1))
        if inrange(pygame.mouse.get_pos()[0], window_width*(17/24), window_width*(19/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.75, window_height*0.85):
            pygame.draw.rect(window, pygame.Color(0, 255 if not menu_is_display else 127, 0), (window_width*(17/24), window_height*0.75, window_width*1/12, window_height*0.1))
            textSurface = textSurface = settings_font.render("取消", False, pygame.Color(0, 0, 0))
        else:textSurface = textSurface = settings_font.render("取消", False, pygame.Color(0, 255 if not menu_is_display else 127, 0))
        window.blit(textSurface, textSurface.get_rect(center=(window_width*0.75, window_height*0.8)))
        if inrange(pygame.mouse.get_pos()[0], window_width*(20/24), window_width*(22/24)) and inrange(pygame.mouse.get_pos()[1], window_height*0.75, window_height*0.85):
            pygame.draw.rect(window, pygame.Color(0, 255 if not menu_is_display else 127, 0), (window_width*(20/24), window_height*0.75, window_width*1/12, window_height*0.1))
            textSurface = textSurface = settings_font.render("确定", False, pygame.Color(0, 0, 0))
        else:textSurface = textSurface = settings_font.render("确定", False, pygame.Color(0, 255 if not menu_is_display else 127, 0))
        window.blit(textSurface, textSurface.get_rect(center=(window_width*(21/24), window_height*0.8)))
        pygame.display.update()
        continue
    elif mode == "clock":now_str = time.ctime().split()[3]
    elif mode == "positive timer":
        time_difference = time.time() - time_start
        now_str = str(floor(time_difference)//3600).zfill(2) + ":" + str(floor(time_difference) % 3600 // 60).zfill(2) + ":" + str(floor(time_difference) % 60).zfill(2)
    elif mode == "countdown timer":
        time_difference = time.time() - time_start
        if time_difference >= target:
            clock_over = True
            now_str = "00:00:00"
        else:
            now_str = str(floor(target - time_difference)//3600).zfill(2) + ":" + str(floor(target - time_difference) % 3600 // 60).zfill(2) + ":" + str(floor(target - time_difference) % 60).zfill(2)
    if is_pausing:
        if not clock_over:
            now_str = past_str
            if mode == "positive timer" or mode == "countdown timer":time_start += time.time() - past_time
        else:
            is_beeping = False
            is_pausing = True
            clock_over = False
            over_time = -1
            now_str = str(floor(target)//3600).zfill(2) + ":" + str(floor(target) % 3600 // 60).zfill(2) + ":" + str(floor(target) % 60).zfill(2)
            past_str = str(floor(target)//3600).zfill(2) + ":" + str(floor(target) % 3600 // 60).zfill(2) + ":" + str(floor(target) % 60).zfill(2)
            past_time = time.time()
            time_start = time.time()
    past_time = time.time()
    if not menu_is_display:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:is_quiting = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:menu_is_display = not menu_is_display
                elif e.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE] and mode != "clock":is_pausing = not is_pausing
                elif e.key == pygame.K_SPACE and mode == "clock" and is_in_alarm:is_in_alarm = False
                elif e.key == pygame.K_TAB:
                    reset()
                    frame_continue = True
    if frame_continue:
        frame_continue = False
        continue
    if raindrop < 0:raindrop = 0.0
    elif raindrop > fps:raindrop = float(fps)
    if layout < 27:layout = 27
    if length < 0:length = 0
    if (clock_over or is_in_alarm) and over_time == -1:over_time = time.time() - 2/fps
    elif not (clock_over or is_in_alarm) and over_time != -1:over_time = -1
    
    if mode == "clock" and alarm_clock_str != "":
        if now_str == alarm_clock_str:
            is_in_alarm = True

    if clock_is_display:
        if (not clock_over and not is_in_alarm) or is_pausing:
            for i in range(8):number(now_str[i], clock_startX+number_position[i]*pixel_size, clock_startY, pygame.Color(255 if not menu_is_display else 127, 0, 0))
        elif (clock_over or is_in_alarm) and (time.time() - over_time) % 1 >= 0.5 and not is_pausing:
            if not is_beeping:
                is_beeping = True
                beep(763, 500)
            for i in range(8):number(now_str[i], clock_startX+number_position[i]*pixel_size, clock_startY, pygame.Color(255 if not menu_is_display else 127, 0, 0))
        elif (time.time() - over_time) % 1 < 0.5:
            is_beeping = False

    for s in range(len(show)):
        if rain_is_display:
            for i in range(floor(window_height/window_width*layout*length)):
                try:
                    if not data[show[s][0]*(window_height//font_size)+show[s][1]-i].is_red and not menu_is_display:
                        textSurface = font.render(data[show[s][0]*(window_height//font_size)+show[s][1]-i].string, False, pygame.Color(0, 255 - floor(256/(window_height/window_width*layout*length)*i), 0))
                    elif not data[show[s][0]*(window_height//font_size)+show[s][1]-i].is_red and menu_is_display:
                        textSurface = font.render(data[show[s][0]*(window_height//font_size)+show[s][1]-i].string, False, pygame.Color(0, (255 - floor(256/(window_height/window_width*layout*length)*i))//2, 0))
                    elif data[show[s][0]*(window_height//font_size)+show[s][1]-i].is_red and not menu_is_display:
                        textSurface = font.render(data[show[s][0]*(window_height//font_size)+show[s][1]-i].string, False, pygame.Color(255, 255 - floor(256/(window_height/window_width*layout*length)*i), 0))
                    elif data[show[s][0]*(window_height//font_size)+show[s][1]-i].is_red and menu_is_display:
                        textSurface = font.render(data[show[s][0]*(window_height//font_size)+show[s][1]-i].string, False, pygame.Color(127, (255 - floor(256/(window_height/window_width*layout*length)*i))//2, 0))
                    window.blit(textSurface, (show[s][0]*font_size, show[s][1]*font_size-font_size*i))
                except IndexError:pass
        show[s][1] += 1
    
    date_font = pygame.font.Font("unifont-15.1.04.otf", window_width//16)
    date_font.bold = True
    if clock_is_display:
        now_list = time.ctime().split()
        date_str = weeks[now_list[0]] + ", " + months[now_list[1]] + " " + now_list[2] + ", " + now_list[4]
        textSurface = date_font.render(date_str, False, pygame.Color(255 if not menu_is_display else 127, 0, 0))
        text_rect = textSurface.get_rect(center=window.get_rect().center)
        text_rect[1] = floor(text_rect[1] * 5/12)
        window.blit(textSurface, text_rect)

    if is_pausing and clock_is_display:
        textSurface = date_font.render("PAUSE", False, pygame.Color(255 if not menu_is_display else 127, 0, 0))
        text_rect = textSurface.get_rect(center=window.get_rect().center)
        text_rect[1] = floor(text_rect[1] * 1.8)
        window.blit(textSurface, text_rect)

    for s in range(len(show)):
        try:
            if show[s][1] > window_height//font_size+floor(window_height/window_width*layout*length):del show[s]
            data[show[s][0]*(window_height//font_size)+show[s][1]].string = random.choice(chars)
        except IndexError:pass
    
    if raindrop != 0 and time.time() >= now+1/raindrop:
        show.append([random.randint(0, window_width//font_size)-1, 0])
        now = time.time()

    if menu_is_display:menu()
    if is_quiting:quit()

    past_str = now_str
    pygame.display.update()
