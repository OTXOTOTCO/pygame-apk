import pygame
import socket
import threading
import json
import time
import os

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("A7 Remote")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# Renkler
DGRAY = (50, 50, 50)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Mouse pad
mouse_pad = pygame.Rect(20, 300, 450, 400)
status_rect = pygame.Rect(20, 20, 300, 60)

# Klavye
keys = ["1234567890", "QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM", "BACK", "SPACE", "ENTER"]
key_rects = []
ky = 20
for row in keys:
    if row == "SPACE":
        key_rects.append(("SPACE", pygame.Rect(20, ky, 1240, 80)))
    elif row == "ENTER":
        key_rects.append(("ENTER", pygame.Rect(20, ky, 300, 80)))
    elif row == "BACK":
        key_rects.append(("BACK", pygame.Rect(340, ky, 200, 80)))
    else:
        x = 20
        for char in row:
            key_rects.append((char, pygame.Rect(x, ky, 90, 80)))
            x += 95
    ky += 90

# Network
sock = None
connected = False
tablet_ip = input("Tablet IP girin (örn: 192.168.1.105): ")
port = 12345

def connect_tablet():
    global sock, connected
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((tablet_ip, port))
            connected = True
            print(f"✅ Bağlandı: {tablet_ip}:{port}")
            break
        except:
            connected = False
            print("🔄 Bağlanıyor...")
        time.sleep(1)

def send_command(cmd):
    global sock, connected
    if connected and sock:
        try:
            sock.send((json.dumps(cmd) + '\n').encode())
        except:
            connected = False
            threading.Thread(target=connect_tablet, daemon=True).start()

threading.Thread(target=connect_tablet, daemon=True).start()

mouse_x, mouse_y = 0, 0
last_touch = None
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            x = int(event.x * 1280) if hasattr(event, 'x') else int(event.x * 1280)
            y = int(event.y * 720) if hasattr(event, 'y') else int(event.y * 720)
            
            # Klavye kontrol
            for key, rect in key_rects:
                if rect.collidepoint(x, y):
                    print(f"Key: {key}")
                    send_command({"type": "key", "key": key})
                    break
            
            # Mouse pad
            if mouse_pad.collidepoint(x, y):
                mouse_x, mouse_y = x - mouse_pad.x, y - mouse_pad.y
                send_command({"type": "click", "x": mouse_x, "y": mouse_y})
            
            last_touch = (x, y)
        
        if event.type == pygame.FINGERMOTION or event.type == pygame.MOUSEMOTION:
            if last_touch:
                x = int(event.x * 1280) if hasattr(event, 'x') else int(event.x * 1280)
                y = int(event.y * 720) if hasattr(event, 'y') else int(event.y * 720)
                dx = x - last_touch[0]
                dy = y - last_touch[1]
                
                if mouse_pad.collidepoint(x, y):
                    send_command({"type": "move", "dx": dx*2, "dy": dy*2})
                
                last_touch = (x, y)
    
    # Çizim
    screen.fill(BLACK)
    
    # Status
    pygame.draw.rect(screen, GREEN if connected else RED, status_rect)
    status_text = font.render("BAĞLI" if connected else "BEKLE", True, WHITE)
    screen.blit(status_text, (30, 35))
    ip_text = font.render(tablet_ip[:15], True, WHITE)
    screen.blit(ip_text, (30, 70))
    
    # Mouse pad
    pygame.draw.rect(screen, BLUE, mouse_pad)
    pygame.draw.rect(screen, WHITE, mouse_pad, 3)
    mouse_pos = pygame.Rect(mouse_pad.x + mouse_x, mouse_pad.y + mouse_y, 20, 20)
    pygame.draw.circle(screen, WHITE, mouse_pos.center, 8)
    
    # Klavye
    for key, rect in key_rects:
        color = DGRAY if rect.collidepoint(pygame.mouse.get_pos()) else (70,70,70)
        pygame.draw.rect(screen, color, rect, border_radius=15)
        text = font.render(key, True, WHITE)
        screen.blit(text, text.get_rect(center=rect.center))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()