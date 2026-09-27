import json
import os
import sys
import pygame  # type: ignore[import-not-found]
# if it aint broke dont fix it :/

pygame.init()
pygame.mixer.init()

# Resolve the script's directory robustly — __file__ can point to the Python
# install dir when running from an interactive shell or IDLE.
_script = os.path.abspath(__file__) if "__file__" in dir() else os.path.abspath(sys.argv[0])
base_dir = os.path.dirname(_script)
# Final safety net: if assets aren't here, fall back to the script's real location
if not os.path.isdir(os.path.join(base_dir, "assets")):
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
settings_file = os.path.join(base_dir, "settings.json")
settings_data = {}
if os.path.exists(settings_file):
    with open(settings_file, "r", encoding="utf-8-sig") as f:
        settings_data = json.load(f)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Clicker")

music_path = os.path.join(base_dir, "assets", "Stringed Disco.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
else:
    print(f"Music not found: {music_path}")

BACKGROUND_COLOR = (255, 255, 197)

score = 0
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)

cookie_path = os.path.join(base_dir, "assets", "Cookie.png")     
if not os.path.exists(cookie_path):
    raise FileNotFoundError(f"Cookie image not found: {cookie_path}")

click_sound_name = settings_data.get("settings-click", {}).get("sound", "button-click.mp3")
click_sound_path = os.path.join(base_dir, "assets", click_sound_name)
if os.path.exists(click_sound_path):
    click_sound = pygame.mixer.Sound(click_sound_path)
else:
    click_sound = None
    print(f"Click sound not found: {click_sound_path}")

settings_path = os.path.join(base_dir, "assets", "Settings.png")
if os.path.exists(settings_path):
    settings_image = pygame.image.load(settings_path).convert_alpha()
    settings_image = pygame.transform.smoothscale(settings_image, (42, 42))
else:
    settings_image = None

cookie_image = pygame.image.load(cookie_path).convert_alpha()
cookie_rect = cookie_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
settings_button = pygame.Rect(WIDTH - 70, 20, 50, 50)
settings_menu = pygame.Rect(WIDTH - 240, 80, 220, 120)
settings_open = False
muted = False
click_multiplier = 1

gray_box_timer = 0.0
gray_box_visible = False

spin_angle = 0
click_timer = 0.0
click_delay = 0.2
clicking = False

SHRINK_SCALE = 0.85

clock = pygame.time.Clock()
running = True


def get_settings_menu_rects():
    rects = []
    for index, _ in enumerate(["Click Multiplier", "Mute Sound"]):
        y = settings_menu.y + 12 + index * 48
        rects.append(pygame.Rect(settings_menu.x + 12, y, settings_menu.width - 24, 35))
    return rects


def play_click_sound():
    if muted or click_sound is None:
        return
    click_sound.play()


def draw_settings_menu():
    if not settings_open:
        return []

    pygame.draw.rect(screen, (120, 120, 120), settings_menu, border_radius=12)
    pygame.draw.rect(screen, (200, 200, 200), settings_menu.inflate(-10, -10), border_radius=10)

    item_rects = get_settings_menu_rects()
    for index, rect in enumerate(item_rects):
        pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=6)

        if index == 0:
            label = "Click Multiplier"
            value_text = f"x{click_multiplier}"
        else:
            label = "Mute Sound (On)" if muted else "Mute Sound (Off)"
            value_text = ""

        label_surface = small_font.render(label, True, (0, 0, 0))
        label_rect = label_surface.get_rect(left=rect.x + 10, centery=rect.centery)
        screen.blit(label_surface, label_rect)

        if value_text:
            value_surface = small_font.render(value_text, True, (0, 0, 0))
            value_rect = value_surface.get_rect(midright=(rect.right - 12, rect.centery))
            screen.blit(value_surface, value_rect)

    return item_rects


def start_gray_box_timer():
    global gray_box_timer, gray_box_visible
    gray_box_timer = 0.0
    gray_box_visible = True


while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            score += click_multiplier
            play_click_sound()
            click_timer = 0.0
            clicking = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if settings_button.collidepoint(event.pos):
                play_click_sound()
                settings_open = not settings_open
                if settings_open:
                    start_gray_box_timer()
            elif settings_open:
                for index, rect in enumerate(get_settings_menu_rects()):
                    if rect.collidepoint(event.pos):
                        if index == 0:
                            if click_multiplier == 1:
                                click_multiplier = 2
                            elif click_multiplier == 2:
                                click_multiplier = 5
                            else:
                                click_multiplier = 1
                        elif index == 1:
                            muted = not muted
                            if muted:
                                pygame.mixer.music.set_volume(0.0)
                            elif os.path.exists(music_path):
                                pygame.mixer.music.set_volume(0.5)
                        settings_open = False
                        break
            elif cookie_rect.collidepoint(event.pos):
                score += click_multiplier
                play_click_sound()
                click_timer = 0.0
                clicking = True

    if clicking:
        click_timer += dt
        if click_timer >= click_delay:
            clicking = False

    if gray_box_visible:
        gray_box_timer += dt
        if gray_box_timer >= 2.0:
            settings_open = False
            gray_box_visible = False

    spin_angle = (spin_angle + 200 * dt) % 360

    screen.fill(BACKGROUND_COLOR)

    if clicking:
        scale = SHRINK_SCALE
    else:
        scale = 1.0

    scaled_cookie = pygame.transform.rotozoom(cookie_image, spin_angle, scale)
    draw_rect = scaled_cookie.get_rect(center=cookie_rect.center)
    screen.blit(scaled_cookie, draw_rect)

    if settings_image is not None:
        screen.blit(settings_image, settings_button)
    else:
        pygame.draw.rect(screen, (80, 80, 80), settings_button, border_radius=10)
        pygame.draw.line(screen, (255, 255, 255), (settings_button.centerx, settings_button.top + 14), (settings_button.centerx, settings_button.bottom - 14), 3)
        pygame.draw.line(screen, (255, 255, 255), (settings_button.left + 14, settings_button.centery), (settings_button.right - 14, settings_button.centery), 3)

    draw_settings_menu()

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))

    pygame.display.flip()

pygame.quit() 
