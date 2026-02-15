import pygame
import random
import sys

pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Midnight Chamber")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 56)

BLACK = (20, 20, 20)
WHITE = (230, 230, 230)
GREEN = (60, 190, 100)
RED = (190, 60, 60)
TABLE = (45, 30, 20)

MAX_HEALTH = 3
TOTAL_SHELLS = 8

# ---------------- GAME VARIABLES ----------------
player_health = MAX_HEALTH
enemy_health = MAX_HEALTH
shells = []

round_live_total = 0
round_live_used = 0

game_state = "START"
message = ""
turn_timer = 0
player_result = None
player_target = None

# ---------------- ROUND SETUP ----------------
def load_round():
    global shells, round_live_total, round_live_used, message

    live_count = random.randint(3, TOTAL_SHELLS - 1)
    blank_count = TOTAL_SHELLS - live_count

    shells = ["live"] * live_count + ["blank"] * blank_count
    random.shuffle(shells)

    round_live_total = live_count
    round_live_used = 0

    message = f"{live_count} live / {blank_count} blanks"

# ---------------- SHOOT ----------------
def shoot(target):
    global player_health, enemy_health, round_live_used, message

    if not shells:
        return None

    shell = shells.pop()

    if shell == "live":
        round_live_used += 1
        if target == "player":
            player_health -= 1
            message = "LIVE! Player hit!"
        else:
            enemy_health -= 1
            message = "LIVE! Enemy hit!"
        return "live"
    else:
        message = "Blank..."
        return "blank"

# ---------------- ENEMY ACTION ----------------
def enemy_action():
    global game_state, turn_timer

    if not shells:
        game_state = "GAME_OVER"
        return

    live = shells.count("live")
    total = len(shells)

    if live / total > 0.5:
        target = "player"
    else:
        target = "enemy"

    result = shoot(target)

    # Extra turn rule
    if result == "blank" and target == "enemy":
        game_state = "ENEMY_THINKING"
        turn_timer = 0
    else:
        game_state = "PLAYER_TURN"

# ---------------- FACE (ALWAYS NEUTRAL) ----------------
def draw_face(cx, cy, color):
    pygame.draw.circle(screen, color, (cx, cy), 70)

    pygame.draw.circle(screen, WHITE, (cx - 20, cy - 15), 12)
    pygame.draw.circle(screen, WHITE, (cx + 20, cy - 15), 12)
    pygame.draw.circle(screen, BLACK, (cx - 20, cy - 12), 5)
    pygame.draw.circle(screen, BLACK, (cx + 20, cy - 12), 5)

    pygame.draw.line(screen, BLACK,
                     (cx - 20, cy + 20),
                     (cx + 20, cy + 20), 3)

# ---------------- BUTTONS ----------------
shoot_enemy_btn = pygame.Rect(200, 520, 260, 60)
shoot_self_btn = pygame.Rect(540, 520, 260, 60)
start_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 50, 300, 70)

running = True

# ---------------- MAIN LOOP ----------------
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # START SCREEN
        if game_state == "START":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    player_health = MAX_HEALTH
                    enemy_health = MAX_HEALTH
                    load_round()
                    game_state = "PLAYER_TURN"

        # PLAYER TURN
        elif game_state == "PLAYER_TURN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if shoot_enemy_btn.collidepoint(event.pos):
                    player_target = "enemy"
                    player_result = shoot("enemy")
                    game_state = "PLAYER_REVEAL"
                    turn_timer = 0

                elif shoot_self_btn.collidepoint(event.pos):
                    player_target = "player"
                    player_result = shoot("player")
                    game_state = "PLAYER_REVEAL"
                    turn_timer = 0

        # RESET
        elif game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game_state = "START"

    # ---------------- PLAYER REVEAL ----------------
    if game_state == "PLAYER_REVEAL":
        turn_timer += dt

        if turn_timer > 1.2:
            # Extra chance rule
            if player_result == "blank" and player_target == "player":
                game_state = "PLAYER_TURN"
            else:
                game_state = "ENEMY_THINKING"

            turn_timer = 0

    # ---------------- ENEMY THINKING ----------------
    if game_state == "ENEMY_THINKING":
        turn_timer += dt
        message = "Enemy is thinking..."

        if turn_timer > 2:
            enemy_action()
            turn_timer = 0

    # ---------------- END CHECK ----------------
    if game_state in ["PLAYER_TURN", "ENEMY_THINKING"]:
        if (player_health <= 0 or
            enemy_health <= 0 or
            round_live_used >= round_live_total):
            game_state = "GAME_OVER"

    # ---------------- DRAW ----------------
    screen.fill(BLACK)

    if game_state == "START":
        title = BIG_FONT.render("Midnight Chamber", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))

        pygame.draw.rect(screen, WHITE, start_button, 2)
        txt = FONT.render("ENTER THE GAME", True, WHITE)
        screen.blit(txt,
                    (start_button.centerx - txt.get_width()//2,
                     start_button.centery - txt.get_height()//2))

        pygame.display.flip()
        continue

    pygame.draw.rect(screen, TABLE, (0, 350, WIDTH, 300))

    draw_face(250, 300, GREEN)
    draw_face(750, 300, RED)

    # Health bars
    pygame.draw.rect(screen, WHITE, (150,80,250,25),2)
    pygame.draw.rect(screen, GREEN,(150,80,250*(player_health/MAX_HEALTH),25))

    pygame.draw.rect(screen, WHITE, (600,80,250,25),2)
    pygame.draw.rect(screen, RED,(600,80,250*(enemy_health/MAX_HEALTH),25))

    # Buttons
    if game_state == "PLAYER_TURN":
        pygame.draw.rect(screen, WHITE, shoot_enemy_btn, 2)
        pygame.draw.rect(screen, WHITE, shoot_self_btn, 2)

        t1 = FONT.render("Shoot Enemy", True, WHITE)
        t2 = FONT.render("Shoot Yourself", True, WHITE)

        screen.blit(t1, (shoot_enemy_btn.centerx - t1.get_width()//2,
                         shoot_enemy_btn.centery - t1.get_height()//2))
        screen.blit(t2, (shoot_self_btn.centerx - t2.get_width()//2,
                         shoot_self_btn.centery - t2.get_height()//2))

    # Game Over Text
    if game_state == "GAME_OVER":
        if player_health > enemy_health:
            text = BIG_FONT.render("YOU WIN - Press R", True, GREEN)
        elif enemy_health > player_health:
            text = BIG_FONT.render("YOU LOST - Press R", True, RED)
        else:
            text = BIG_FONT.render("DRAW - Press R", True, WHITE)

        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))

    # Message display
    msg = FONT.render(message, True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 430))

    pygame.display.flip()

pygame.quit()
sys.exit()
