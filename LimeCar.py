"""import pygame
import random
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("bg_pixel_sound.wav")
pygame.mixer.music.set_volume(0.5)  # 0.0 - 1.0 között, ez 50% hangerő
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LimeCar")

BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)

font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 60)
button_font = pygame.font.Font(None, 40)
instruction_font = pygame.font.Font(None, 28)
win_font = pygame.font.Font(None, 50)

# --- Gomb rajzolása ---
def draw_button(text, x, y, width, height, color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    current_color = hover_color if rect.collidepoint(mouse_pos) else color
    pygame.draw.rect(SCREEN, current_color, rect)
    label = button_font.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    SCREEN.blit(label, label_rect)
    return rect

# --- Menü logika ---
def show_main_menu():
    while True:
        SCREEN.fill(DARK_GREEN)
        title = menu_font.render("🍋 LimeCar 🍋", True, WHITE)
        SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        mouse_pos = pygame.mouse.get_pos()
        start_button = draw_button("Játék indítása", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, GRAY, YELLOW, mouse_pos)
        quit_button = draw_button("Kilépés", WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, GRAY, YELLOW, mouse_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return  # kilép a menüből, indul a játék
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# --- Játék logika ---
def run_game():
    # Autó beállítások
    car_width, car_height = 50, 80
    car_x = WIDTH // 2 - car_width // 2
    car_y = HEIGHT - car_height - 30
    car_lateral_speed = 5
    game_speed = 5

    try:
        car_image = pygame.image.load(resource_path("car.png")).convert_alpha()
        car_image = pygame.transform.scale(car_image, (car_width, car_height))
    except pygame.error as e:
        print(f"Hiba a 'car.png' betöltésekor: {e}")
        pygame.quit()
        exit()

    road_width = WIDTH // 2
    road_x = (WIDTH - road_width) // 2
    road_y = 0
    road_height = HEIGHT * 2

    stripe_width = 10
    stripe_height = 40
    stripe_gap = 60
    num_stripes = int(HEIGHT / (stripe_height + stripe_gap)) + 2
    stripe_y_offsets = [i * (stripe_height + stripe_gap) for i in range(num_stripes)]

    lime_width, lime_height = 30, 30
    limes = []
    score = 0
    lime_spawn_timer = 0
    lime_spawn_interval = 100

    try:
        lime_image = pygame.image.load(resource_path("lime.png")).convert_alpha()
        lime_image = pygame.transform.scale(lime_image, (50, 50))
    except pygame.error as e:
        print(f"Hiba a 'lime.png' betöltésekor: {e}")
        pygame.quit()
        exit()

    show_initial_message = True
    show_win_message = False

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            car_x -= car_lateral_speed
        if keys[pygame.K_d]:
            car_x += car_lateral_speed

        car_x = max(road_x, min(car_x, road_x + road_width - car_width))

        if keys[pygame.K_w]:
            game_speed = min(game_speed + 0.1, 15)
        if keys[pygame.K_s]:
            game_speed = max(game_speed - 0.1, 2)

        road_y += game_speed
        if road_y >= HEIGHT:
            road_y = 0

        for i in range(len(stripe_y_offsets)):
            stripe_y_offsets[i] += game_speed
            if stripe_y_offsets[i] > HEIGHT:
                stripe_y_offsets[i] -= (stripe_height + stripe_gap) * num_stripes

        lime_spawn_timer += 1
        if lime_spawn_timer >= lime_spawn_interval:
            new_lime_x = random.randint(road_x, road_x + road_width - lime_width)
            limes.append([new_lime_x, -lime_height])
            lime_spawn_timer = 0

        limes_to_remove = []
        for i, lime in enumerate(limes):
            lime[1] += game_speed
            car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
            lime_rect = pygame.Rect(lime[0], lime[1], lime_width, lime_height)

            if car_rect.colliderect(lime_rect):
                score += 1
                limes_to_remove.append(i)
                if score >= 10:
                    show_initial_message = False
                    show_win_message = True

            if lime[1] > HEIGHT:
                limes_to_remove.append(i)

        for i in sorted(limes_to_remove, reverse=True):
            del limes[i]

        SCREEN.fill(GREEN)
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y, road_width, road_height))
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y - road_height, road_width, road_height))

        for offset in stripe_y_offsets:
            pygame.draw.rect(SCREEN, YELLOW, (WIDTH // 2 - stripe_width // 2, offset, stripe_width, stripe_height))

        for lime in limes:
            SCREEN.blit(lime_image, (lime[0], lime[1]))

        SCREEN.blit(car_image, (car_x, car_y))

        score_text = font.render(f"Pontok: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        if show_initial_message:
            instruction_text = instruction_font.render("Gyűjts össze 10 lime-ot!", True, WHITE)
            instruction_text_rect = instruction_text.get_rect(center=(WIDTH // 2, 50))
            SCREEN.blit(instruction_text, instruction_text_rect)

        if show_win_message:
            win_text = win_font.render("Gratulálok! Lyme kóros lettél.", True, WHITE)
            win_text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            SCREEN.blit(win_text, win_text_rect)

        pygame.display.flip()
        clock.tick(60)

# --- Fő programindítás ---
show_main_menu()
run_game()
pygame.quit()
"""

"""

import pygame
import random
import sys

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("bg_pixel_sound.wav")
pygame.mixer.music.set_volume(0.5)  # 0.0 - 1.0 között, ez 50% hangerő
pygame.mixer.music.play(-1)

font = pygame.font.Font(None, 36)
instruction_font = pygame.font.Font(None, 28)
win_font = pygame.font.Font(None, 50)
menu_font = pygame.font.Font(None, 60)
button_font = pygame.font.Font(None, 40)

# --- Képernyő beállítások ---
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LimeCar")

# --- Színek ---
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# --- Autó beállítások ---
car_width, car_height = 50, 80
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 30
car_lateral_speed = 5
game_speed = 5

# --- Betöltések ---
try:
    car_image = pygame.image.load("car.png").convert_alpha()
    car_image = pygame.transform.scale(car_image, (car_width, car_height))
    lime_image = pygame.image.load("lime.png").convert_alpha()
    lime_image = pygame.transform.scale(lime_image, (50, 50))
    tequila_image = pygame.image.load("tequila.png").convert_alpha()
    tequila_image = pygame.transform.scale(tequila_image, (50, 50))
    baileys_image = pygame.image.load("baileys.png").convert_alpha()
    baileys_image = pygame.transform.scale(baileys_image, (50, 50))
    margherita_image = pygame.image.load("margherita.png").convert_alpha()
    margherita_image = pygame.transform.scale(margherita_image, (100, 100))
except pygame.error as e:
    print("Hiba a képek betöltésekor:", e)
    pygame.quit()
    sys.exit()

# --- Út ---
road_width = WIDTH // 2
road_x = (WIDTH - road_width) // 2
road_y = 0
road_height = HEIGHT * 2
stripe_width, stripe_height, stripe_gap = 10, 40, 60
num_stripes = int(HEIGHT / (stripe_height + stripe_gap)) + 2
stripe_y_offsets = [i * (stripe_height + stripe_gap) for i in range(num_stripes)]

# --- Lime/Tequila/Baileys ---
lime_width, lime_height = 30, 30
limes, tequilas, baileys = [], [], []
lime_count, tequila_count, baileys_count = 0, 0, 0
spawn_timer = 0
spawn_interval = 60

# --- Betűtípusok ---
font = pygame.font.Font(None, 36)
instruction_font = pygame.font.Font(None, 28)
win_font = pygame.font.Font(None, 50)
menu_font = pygame.font.Font(None, 72)
menu_option_font = pygame.font.Font(None, 48)

# --- Menü ---
def draw_button(text, x, y, width, height, color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    current_color = hover_color if rect.collidepoint(mouse_pos) else color
    pygame.draw.rect(SCREEN, current_color, rect)
    label = button_font.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    SCREEN.blit(label, label_rect)
    return rect

# --- Menü logika ---
def show_main_menu():
    while True:
        SCREEN.fill(GREEN)
        title = menu_font.render("🍋 LimeCar 🍋", True, WHITE)
        SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        mouse_pos = pygame.mouse.get_pos()
        start_button = draw_button("Játék indítása", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, GRAY, YELLOW, mouse_pos)
        quit_button = draw_button("Kilépés", WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, GRAY, YELLOW, mouse_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return  # kilép a menüből, indul a játék
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


# --- Játék ---
def game_loop():
    global lime_count, tequila_count, baileys_count
    global limes, tequilas, baileys
    global spawn_timer, game_speed
    global car_x, car_y, car_width, car_height, road_y, road_x, road_y

    show_win_message = False
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: car_x -= car_lateral_speed
        if keys[pygame.K_d]: car_x += car_lateral_speed
        if keys[pygame.K_w]: game_speed = min(game_speed + 0.1, 15)
        if keys[pygame.K_s]: game_speed = max(game_speed - 0.1, 2)

        if car_x < road_x: car_x = road_x
        if car_x + car_width > road_x + road_width:
            car_x = road_x + road_width - car_width

        road_y += game_speed
        if road_y >= HEIGHT:
            road_y = 0
        for i in range(len(stripe_y_offsets)):
            stripe_y_offsets[i] += game_speed
            if stripe_y_offsets[i] > HEIGHT:
                stripe_y_offsets[i] -= (stripe_height + stripe_gap) * num_stripes

        # --- Generálás ---
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            x = random.randint(road_x, road_x + road_width - lime_width)
            item_type = random.choice(["lime", "tequila", "baileys"])
            if item_type == "lime":
                limes.append([x, -lime_height])
            elif item_type == "tequila":
                tequilas.append([x, -lime_height])
            else:
                baileys.append([x, -lime_height])
            spawn_timer = 0

        # --- Mozgatás, ütközés ---
        car_rect = pygame.Rect(car_x, car_y, car_width, car_height)

        
        def handle_items(items, image, counter_name):
            global lime_count, tequila_count, baileys_count
            to_remove = []
            for i, item in enumerate(items):
                item[1] += game_speed
                item_rect = pygame.Rect(item[0], item[1], lime_width, lime_height)
                if car_rect.colliderect(item_rect):
                    if counter_name == 'lime':
                        lime_count += 1
                    elif counter_name == 'tequila':
                        tequila_count += 1
                    elif counter_name == 'baileys':
                        baileys_count += 1
                    to_remove.append(i)
                elif item[1] > HEIGHT:
                    to_remove.append(i)
            for i in sorted(to_remove, reverse=True):
                del items[i]


        handle_items(limes, lime_image, 'lime')
        handle_items(tequilas, tequila_image, 'tequila')
        handle_items(baileys, baileys_image, 'baileys')

        if lime_count >= 4 and tequila_count >= 8 and baileys_count >= 4:
            show_win_message = True

        # --- Rajzolás ---
        SCREEN.fill(GREEN)
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y, road_width, road_height))
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y - road_height, road_width, road_height))

        for offset in stripe_y_offsets:
            pygame.draw.rect(SCREEN, YELLOW, (WIDTH // 2 - stripe_width // 2, offset, stripe_width, stripe_height))

        for lime in limes:
            SCREEN.blit(lime_image, (lime[0], lime[1]))
        for tequila in tequilas:
            SCREEN.blit(tequila_image, (tequila[0], tequila[1]))
        for b in baileys:
            SCREEN.blit(baileys_image, (b[0], b[1]))

        SCREEN.blit(car_image, (car_x, car_y))

        # --- Szövegek ---
        score_text = font.render(f"Pontok: {lime_count + tequila_count + baileys_count}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        lime_text = font.render(f"Lime: {lime_count}/4", True, WHITE)
        SCREEN.blit(lime_text, (10, 50))
        tequila_text = font.render(f"Tequila: {tequila_count}/8", True, WHITE)
        SCREEN.blit(tequila_text, (10, 80))
        baileys_text = font.render(f"Baileys: {baileys_count}/4", True, WHITE)
        SCREEN.blit(baileys_text, (10, 110))

        # if lime_count < 10:
        #     instruction_text = instruction_font.render("Gyűjts össze 10 lime-ot!", True, WHITE)
        #     instruction_text_rect = instruction_text.get_rect(center=(WIDTH // 2, 50))
        #     SCREEN.blit(instruction_text, instruction_text_rect)

        if show_win_message:
            SCREEN.blit(margherita_image, (10, 150))
            win_text = win_font.render("Készen van a Margherita!", True, WHITE)
            SCREEN.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))



        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# --- Indítás ---
show_main_menu()
game_loop()
"""

"""
import pygame
import random
import sys
import os
import math

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("bg_pixel_sound.wav")
pygame.mixer.music.set_volume(0.5)  # 0.0 - 1.0 között, ez 50% hangerő
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LimeCar")

BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)

font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 60)
button_font = pygame.font.Font(None, 40)
instruction_font = pygame.font.Font(None, 28)
win_font = pygame.font.Font(None, 50)

# --- Gomb rajzolása ---
def draw_button(text, x, y, width, height, color, hover_color, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    current_color = hover_color if rect.collidepoint(mouse_pos) else color
    pygame.draw.rect(SCREEN, current_color, rect)
    label = button_font.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    SCREEN.blit(label, label_rect)
    return rect

# --- Menü logika ---
def show_main_menu():
    while True:
        SCREEN.fill(DARK_GREEN)
        title = menu_font.render("🍋 LimeCar 🍋", True, WHITE)
        SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        mouse_pos = pygame.mouse.get_pos()
        start_button = draw_button("Játék indítása", WIDTH // 2 - 150, HEIGHT // 2, 300, 60, GRAY, YELLOW, mouse_pos)
        quit_button = draw_button("Kilépés", WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, GRAY, YELLOW, mouse_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return  # kilép a menüből, indul a játék
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# --- Speedometer rajzolása ---
def draw_speedometer(speed, max_speed):
    radius = 60
    center_x = WIDTH - radius - 20
    center_y = HEIGHT - radius - 20

    pygame.draw.circle(SCREEN, GRAY, (center_x, center_y), radius)
    pygame.draw.circle(SCREEN, BLACK, (center_x, center_y), radius, 4)  # keret

    start_angle = -90
    end_angle = 90
    speed_ratio = min(speed / max_speed, 1.0)
    angle = start_angle + (end_angle - start_angle) * speed_ratio
    angle_rad = math.radians(angle)
    needle_length = radius - 10
    needle_x = center_x + needle_length * math.cos(angle_rad)
    needle_y = center_y + needle_length * math.sin(angle_rad)

    pygame.draw.line(SCREEN, (255, 0, 0), (center_x, center_y), (needle_x, needle_y), 4)
    pygame.draw.circle(SCREEN, BLACK, (center_x, center_y), 8)

    speed_text = font.render(f"{speed:.1f}", True, WHITE)
    text_rect = speed_text.get_rect(center=(center_x, center_y + radius + 15))
    SCREEN.blit(speed_text, text_rect)

# --- Játék logika ---
def run_game():
    car_width, car_height = 50, 80
    car_x = WIDTH // 2 - car_width // 2
    car_y = HEIGHT - car_height - 30
    car_lateral_speed = 5
    game_speed = 5

    try:
        car_image = pygame.image.load(resource_path("car.png")).convert_alpha()
        car_image = pygame.transform.scale(car_image, (car_width, car_height))
    except pygame.error as e:
        print(f"Hiba a 'car.png' betöltésekor: {e}")
        pygame.quit()
        exit()

    road_width = WIDTH // 2
    road_x = (WIDTH - road_width) // 2
    road_y = 0
    road_height = HEIGHT * 2

    stripe_width = 10
    stripe_height = 40
    stripe_gap = 60
    num_stripes = int(HEIGHT / (stripe_height + stripe_gap)) + 2
    stripe_y_offsets = [i * (stripe_height + stripe_gap) for i in range(num_stripes)]

    lime_width, lime_height = 30, 30
    limes = []
    score = 0
    lime_spawn_timer = 0
    lime_spawn_interval = 100

    try:
        lime_image = pygame.image.load(resource_path("lime.png")).convert_alpha()
        lime_image = pygame.transform.scale(lime_image, (50, 50))
    except pygame.error as e:
        print(f"Hiba a 'lime.png' betöltésekor: {e}")
        pygame.quit()
        exit()

    show_initial_message = True
    show_win_message = False

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            car_x -= car_lateral_speed
        if keys[pygame.K_d]:
            car_x += car_lateral_speed

        car_x = max(road_x, min(car_x, road_x + road_width - car_width))

        if keys[pygame.K_w]:
            game_speed = min(game_speed + 0.1, 15)
        if keys[pygame.K_s]:
            game_speed = max(game_speed - 0.1, 2)

        road_y += game_speed
        if road_y >= HEIGHT:
            road_y = 0

        for i in range(len(stripe_y_offsets)):
            stripe_y_offsets[i] += game_speed
            if stripe_y_offsets[i] > HEIGHT:
                stripe_y_offsets[i] -= (stripe_height + stripe_gap) * num_stripes

        lime_spawn_timer += 1
        if lime_spawn_timer >= lime_spawn_interval:
            new_lime_x = random.randint(road_x, road_x + road_width - lime_width)
            limes.append([new_lime_x, -lime_height])
            lime_spawn_timer = 0

        limes_to_remove = []
        for i, lime in enumerate(limes):
            lime[1] += game_speed
            car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
            lime_rect = pygame.Rect(lime[0], lime[1], lime_width, lime_height)

            if car_rect.colliderect(lime_rect):
                score += 1
                limes_to_remove.append(i)
                if score >= 10:
                    show_initial_message = False
                    show_win_message = True

            if lime[1] > HEIGHT:
                limes_to_remove.append(i)

        for i in sorted(limes_to_remove, reverse=True):
            del limes[i]

        SCREEN.fill(GREEN)
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y, road_width, road_height))
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y - road_height, road_width, road_height))

        for offset in stripe_y_offsets:
            pygame.draw.rect(SCREEN, YELLOW, (WIDTH // 2 - stripe_width // 2, offset, stripe_width, stripe_height))

        for lime in limes:
            SCREEN.blit(lime_image, (lime[0], lime[1]))

        SCREEN.blit(car_image, (car_x, car_y))

        score_text = font.render(f"Pontok: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

        if show_initial_message:
            instruction_text = instruction_font.render("Gyűjts össze 10 lime-ot!", True, WHITE)
            instruction_text_rect = instruction_text.get_rect(center=(WIDTH // 2, 50))
            SCREEN.blit(instruction_text, instruction_text_rect)

        if show_win_message:
            win_text = win_font.render("Gratulálok! Lyme kóros lettél.", True, WHITE)
            win_text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            SCREEN.blit(win_text, win_text_rect)

        # Sebességmérő kirajzolása
        draw_speedometer(game_speed, 15)

        pygame.display.flip()
        clock.tick(60)

# --- Fő programindítás ---
show_main_menu()
run_game()
pygame.quit()
"""

import pygame
import random
import sys


from pygments.console import dark_colors
from pygments.styles.gh_dark import BLUE_1, BLUE_2, PURPLE_2
from ursina.color import black


pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("bg_pixel_sound.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LimeCar")

BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

car_width, car_height = 50, 100
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 30
car_lateral_speed = 5
game_speed = 5

try:
    car_image = pygame.image.load("car.png").convert_alpha()
    car_image = pygame.transform.scale(car_image, (car_width, car_height))      ## új surface-t ad vissza, képméret-átalakító függvény a Pygame-ben
    lime_image = pygame.image.load("lime.png").convert_alpha()
    lime_image = pygame.transform.scale(lime_image, (50, 50))
    tequila_image = pygame.image.load("tequila.png").convert_alpha()
    tequila_image = pygame.transform.scale(tequila_image, (50, 50))
    baileys_image = pygame.image.load("baileys.png").convert_alpha()
    baileys_image = pygame.transform.scale(baileys_image, (50, 50))
    margherita_image = pygame.image.load("margherita.png").convert_alpha()
    margherita_image = pygame.transform.scale(margherita_image, (100, 100))
except pygame.error as e:
    print("Hiba a képek betöltésekor:", e)
    pygame.quit()
    sys.exit()

road_width = WIDTH // 2
road_x = (WIDTH - road_width) // 2
road_y = 0
road_height = HEIGHT * 2



stripe_width, stripe_height, stripe_gap = 10, 70, 60
num_stripes = int(HEIGHT / (stripe_height + stripe_gap)) + 2
# stripe_y_offsets = [i * (stripe_height + stripe_gap) for i in range(num_stripes)]
#________________________________________________________________________
# ez lényegében a stripe_y_offset sor érthetően

stripe_y_offsets = []  # lista, ami minden csík függőleges pozícióját tartalmazza

for i in range(num_stripes):
    y = i * (stripe_height + stripe_gap)  # minden csík lejjebb kerül egy egységgel
    stripe_y_offsets.append(y)            # hozzáadjuk a pozíciót a listához

#________________________________________________________________________

lime_width, lime_height = 30, 30
limes, tequilas, baileys = [], [], []
lime_count, tequila_count, baileys_count = 0, 0, 0
spawn_timer = 0
spawn_interval = 60

font = pygame.font.Font(None, 36)
instruction_font = pygame.font.Font(None, 28)
win_font = pygame.font.Font(None, 50)

def draw_speedometer(surface, x, y, radius, speed, max_speed):
    # Kör alap
    pygame.draw.circle(surface, WHITE, (x, y), radius, 4)
    pygame.draw.circle(surface, black, (x, y), radius - 4)

    # Skálák rajzolása (pl. 10 osztás)
    for i in range(11):
        angle = (315 + i * 27) * (3.14159 / 180) #(3.14159 / 180)  # 135° -tól 405°-ig (270 fok)
        inner = (int(x + (radius - 10) * -pygame.math.Vector2(1, 0).rotate_rad(angle).x),
                 int(y + (radius - 10) * -pygame.math.Vector2(1, 0).rotate_rad(angle).y)
                 )
        outer = (int(x + radius * -pygame.math.Vector2(1, 0).rotate_rad(angle).x),
                 int(y + radius * -pygame.math.Vector2(1, 0).rotate_rad(angle).y)
                 )
        pygame.draw.line(surface, WHITE, inner, outer, 3)  # speedometer vonal vastagsaga

        #print(f"{outer}\n{inner}\n{angle}")
        


    # Mutató szöge (135° + speed arányban)
    speed_ratio = min(speed / max_speed, 1.0)
    pointer_angle_deg = 300 + 270 * speed_ratio
    pointer_angle_rad = pointer_angle_deg * 3.14159 / 180
    pointer_length = radius - 15

    pointer_x = int(x + pointer_length * -pygame.math.Vector2(1, 0).rotate_rad(pointer_angle_rad).x)
    pointer_y = int(y + pointer_length * -pygame.math.Vector2(1, 0).rotate_rad(pointer_angle_rad).y)

    pygame.draw.line(surface, YELLOW, (x, y), (pointer_x, pointer_y), 5)

    # Középpont kör
    pygame.draw.circle(surface, YELLOW, (x, y), 8)

    # Sebesség szöveg középen
    speed_text = font.render(f"{int(speed)}", True, WHITE)
    text_rect = speed_text.get_rect(center=(x, y + radius // 2))
    surface.blit(speed_text, text_rect)


def game_loop():
    global lime_count, tequila_count, baileys_count
    global limes, tequilas, baileys
    global spawn_timer, game_speed
    global car_x, car_y, car_width, car_height, road_y, road_x

    show_win_message = False
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: car_x -= car_lateral_speed
        if keys[pygame.K_d]: car_x += car_lateral_speed
        if keys[pygame.K_w]: game_speed = min(game_speed + 0.1, 15)
        if keys[pygame.K_s]: game_speed = max(game_speed - 0.1, 2)

        if car_x < road_x: car_x = road_x
        if car_x + car_width > road_x + road_width:
            car_x = road_x + road_width - car_width

        road_y += game_speed
        if road_y >= HEIGHT:
            road_y = 0
        for i in range(len(stripe_y_offsets)):
            stripe_y_offsets[i] += game_speed
            if stripe_y_offsets[i] > HEIGHT:
                stripe_y_offsets[i] -= (stripe_height + stripe_gap) * num_stripes

        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            x = random.randint(road_x, road_x + road_width - lime_width)
            item_type = random.choice(["lime", "tequila", "baileys"])
            if item_type == "lime":
                limes.append([x, -lime_height])
            elif item_type == "tequila":
                tequilas.append([x, -lime_height])
            else:
                baileys.append([x, -lime_height])
            spawn_timer = 0

        car_rect = pygame.Rect(car_x, car_y, car_width, car_height)

        def handle_items(items, counter_name):
            global lime_count, tequila_count, baileys_count
            to_remove = []
            for i, item in enumerate(items):
                item[1] += game_speed
                item_rect = pygame.Rect(item[0], item[1], lime_width, lime_height)
                if car_rect.colliderect(item_rect):
                    if counter_name == 'lime':
                        lime_count += 1
                    elif counter_name == 'tequila':
                        tequila_count += 1
                    elif counter_name == 'baileys':
                        baileys_count += 1
                    to_remove.append(i)
                elif item[1] > HEIGHT:
                    to_remove.append(i)
            for i in sorted(to_remove, reverse=True):
                del items[i]

        handle_items(limes, 'lime')
        handle_items(tequilas, 'tequila')
        handle_items(baileys, 'baileys')

        if lime_count >= 4 and tequila_count >= 8 and baileys_count >= 4:
            show_win_message = True

        SCREEN.fill(GREEN)
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y, road_width, road_height))
        pygame.draw.rect(SCREEN, GRAY, (road_x, road_y - road_height, road_width, road_height))

        for offset in stripe_y_offsets:
            pygame.draw.rect(SCREEN, YELLOW, (WIDTH // 2 - stripe_width // 2, offset, stripe_width, stripe_height))

        for lime in limes:
            SCREEN.blit(lime_image, (lime[0], lime[1]))
        for tequila in tequilas:
            SCREEN.blit(tequila_image, (tequila[0], tequila[1]))
        for b in baileys:
            SCREEN.blit(baileys_image, (b[0], b[1]))

        SCREEN.blit(car_image, (car_x, car_y))

        lime_text = font.render(f"Lime: {lime_count}/4", True, WHITE)
        tequila_text = font.render(f"Tequila: {tequila_count}/8", True, WHITE)
        baileys_text = font.render(f"Baileys: {baileys_count}/4", True, WHITE)

        SCREEN.blit(lime_text, (10, 10))
        SCREEN.blit(tequila_text, (10, 40))  # 30 pixellel lejjebb
        SCREEN.blit(baileys_text, (10, 70))

        # Itt hívjuk meg a speedometer-t a jobb alsó sarokba
        speedometer_radius = 70
        speedometer_x = WIDTH - speedometer_radius - 20
        speedometer_y = HEIGHT - speedometer_radius - 20
        draw_speedometer(SCREEN, speedometer_x, speedometer_y, speedometer_radius, game_speed, 15)

        pygame.display.flip()
        clock.tick(60)

game_loop()
pygame.quit()
