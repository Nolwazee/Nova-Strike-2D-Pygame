import pygame
import math
import random

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
W, H = 800, 700
FPS  = 60
TITLE = "NOVA STRIKE"

# Colours
BLACK     = (0, 0, 0)
WHITE     = (255, 255, 255)
CYAN      = (0, 220, 255)
YELLOW    = (255, 220, 0)
RED       = (255, 50, 50)
GREEN     = (50, 255, 120)
ORANGE    = (255, 140, 0)
PURPLE    = (160, 60, 255)
DARK_BLUE = (5, 5, 30)
NEON_BLUE  = (0, 170, 255)
NEON_GREEN = (0, 255, 160)
GREY      = (120, 120, 140)
PINK      = (255, 80, 180)


# ─── ASSET DRAWING (procedural sprites) ─────────────────────────────────────

def draw_player_ship(color=CYAN, size=36):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    pts = [(cx, 2), (cx + 14, size - 8), (cx, size - 14), (cx - 14, size - 8)]
    pygame.draw.polygon(s, color, pts)
    pygame.draw.polygon(s, WHITE, pts, 1)
    pygame.draw.ellipse(s, (180, 240, 255), (cx - 5, cy - 4, 10, 8))
    pygame.draw.rect(s, ORANGE, (cx - 4, size - 10, 8, 6))
    return s


def draw_enemy(etype, size=30):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    if etype == "basic":
        pts = [(cx, size - 2), (cx - 12, 4), (cx, 10), (cx + 12, 4)]
        pygame.draw.polygon(s, RED, pts)
        pygame.draw.polygon(s, PINK, pts, 1)
        pygame.draw.circle(s, YELLOW, (cx, cy), 5)
    elif etype == "fast":
        pts = [(cx, size - 2), (cx - 8, 4), (cx + 8, 4)]
        pygame.draw.polygon(s, PURPLE, pts)
        pygame.draw.polygon(s, WHITE, pts, 1)
        pygame.draw.circle(s, CYAN, (cx, cy - 2), 4)
    elif etype == "tank":
        pygame.draw.rect(s, (200, 60, 0), (4, 4, size - 8, size - 8), border_radius=4)
        pygame.draw.rect(s, ORANGE, (4, 4, size - 8, size - 8), 2, border_radius=4)
        pygame.draw.circle(s, RED, (cx, cy), 7)
        pygame.draw.circle(s, YELLOW, (cx, cy), 4)
    elif etype == "boss":
        pts = [
            (cx, 2), (cx + 20, 10), (cx + 24, cy), (cx + 16, size - 4),
            (cx, size - 10), (cx - 16, size - 4), (cx - 24, cy), (cx - 20, 10)
        ]
        pygame.draw.polygon(s, (220, 30, 30), pts)
        pygame.draw.polygon(s, ORANGE, pts, 2)
        pygame.draw.circle(s, YELLOW, (cx, cy), 10)
        pygame.draw.circle(s, WHITE, (cx, cy), 5)
    return s


def draw_bullet(color=NEON_GREEN, length=12, width=4):
    s = pygame.Surface((width, length), pygame.SRCALPHA)
    pygame.draw.rect(s, color, (0, 0, width, length), border_radius=2)
    pygame.draw.rect(s, WHITE, (1, 0, width - 2, 3), border_radius=1)
    return s


def draw_powerup(ptype, size=22):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    if ptype == "health":
        pygame.draw.circle(s, GREEN, (cx, cy), cx - 2)
        pygame.draw.line(s, WHITE, (cx, 4), (cx, size - 4), 3)
        pygame.draw.line(s, WHITE, (4, cy), (size - 4, cy), 3)
    elif ptype == "rapid":
        pygame.draw.circle(s, YELLOW, (cx, cy), cx - 2)
        for i in range(3):
            x = cx - 6 + i * 6
            pygame.draw.rect(s, WHITE, (x, 4, 3, 14), border_radius=1)
    elif ptype == "shield":
        pygame.draw.circle(s, CYAN, (cx, cy), cx - 2)
        pygame.draw.circle(s, WHITE, (cx, cy), cx - 4, 2)
    elif ptype == "bomb":
        pygame.draw.circle(s, ORANGE, (cx, cy), cx - 2)
        for a in range(0, 360, 45):
            r = math.radians(a)
            x2 = cx + math.cos(r) * (cx - 4)
            y2 = cy + math.sin(r) * (cy - 4)
            pygame.draw.line(s, WHITE, (cx, cy), (int(x2), int(y2)), 2)
    return s


# ─── PARTICLE SYSTEM ────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color, vel=None, life=40, size=4, grav=0):
        self.x, self.y = x, y
        self.color = color
        self.vx = vel[0] if vel else random.uniform(-3, 3)
        self.vy = vel[1] if vel else random.uniform(-3, 3)
        self.life = life
        self.max_life = life
        self.size = size
        self.grav = grav

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.grav
        self.vx *= 0.97
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = max(0, min(255, int(255 * (self.life / self.max_life))))
        r = max(1, int(self.size * (self.life / self.max_life)))
        color = (*self.color[:3], alpha)
        tmp = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, color, (r, r), r)
        surf.blit(tmp, (int(self.x) - r, int(self.y) - r))


def explosion(particles, x, y, color=ORANGE, count=30, speed=5):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        spd = random.uniform(1, speed)
        vx, vy = math.cos(angle) * spd, math.sin(angle) * spd
        c = random.choice([color, YELLOW, WHITE, RED])
        size = random.randint(2, 6)
        particles.append(Particle(x, y, c, (vx, vy), random.randint(25, 55), size))


# ─── GAME OBJECTS ────────────────────────────────────────────────────────────

class Player:
    def __init__(self):
        self.w, self.h = 36, 36
        self.x = W // 2 - self.w // 2
        self.y = H - 100
        self.speed = 5
        self.hp = 100
        self.max_hp = 100
        self.score = 0
        self.rapid_timer = 0
        self.shield_timer = 0
        self.shoot_cooldown = 0
        self.base_cooldown = 18
        self.invincible = 0
        self.sprite = draw_player_ship()
        self.engine_frame = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def move(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += self.speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.y += self.speed
        self.x = max(0, min(W - self.w, self.x))
        self.y = max(0, min(H - self.h, self.y))

    def shoot(self, bullets):
        """Returns True if a shot was fired (caller handles the shoot sound)."""
        if self.shoot_cooldown <= 0:
            cd = 8 if self.rapid_timer > 0 else self.base_cooldown
            if self.shoot_cooldown <= 0:
                cx = self.x + self.w // 2
                bullets.append(Bullet(cx - 2, self.y, -14, NEON_GREEN, "player"))
                if self.rapid_timer > 0:
                    bullets.append(Bullet(cx - 10, self.y + 6, -13, NEON_GREEN, "player"))
                    bullets.append(Bullet(cx + 6,  self.y + 6, -13, NEON_GREEN, "player"))
                self.shoot_cooldown = cd
                return True
        return False

    def update(self):
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.rapid_timer  > 0:  self.rapid_timer  -= 1
        if self.shield_timer > 0:  self.shield_timer -= 1
        if self.invincible   > 0:  self.invincible   -= 1
        self.engine_frame += 1

    def take_damage(self, dmg):
        """Returns 'hit', 'shield', or None. Caller handles sounds and explosion particles."""
        if self.invincible > 0: return None
        if self.shield_timer > 0:
            self.shield_timer = 0
            self.invincible = 60
            return "shield"
        self.hp -= dmg
        self.invincible = 45
        return "hit"

    def draw(self, surf):
        if self.engine_frame % 3 == 0:
            pass  # engine trail handled via particles in run_game
        if self.invincible > 0 and self.invincible % 8 < 4:
            return
        surf.blit(self.sprite, (self.x, self.y))
        if self.shield_timer > 0:
            cx = self.x + self.w // 2
            cy = self.y + self.h // 2
            alpha = min(180, self.shield_timer * 3)
            tmp = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (*CYAN, alpha), (30, 30), 28, 3)
            surf.blit(tmp, (cx - 30, cy - 30))


class Bullet:
    def __init__(self, x, y, vy, color, owner, vx=0):
        self.x, self.y = x, y
        self.vy = vy
        self.vx = vx
        self.color = color
        self.owner = owner
        self.w, self.h = 4, 12
        self.sprite = draw_bullet(color)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surf):
        surf.blit(self.sprite, (int(self.x), int(self.y)))


class Enemy:
    TYPES = {
        "basic": {"hp": 20, "speed": 2.0, "score": 100, "shoot_rate": 90,  "bullet_spd": 5, "dmg": 10, "size": 30},
        "fast":  {"hp": 10, "speed": 4.0, "score": 150, "shoot_rate": 120, "bullet_spd": 7, "dmg": 8,  "size": 24},
        "tank":  {"hp": 60, "speed": 1.2, "score": 250, "shoot_rate": 60,  "bullet_spd": 4, "dmg": 20, "size": 36},
        "boss":  {"hp": 300,"speed": 1.5, "score": 1000,"shoot_rate": 40,  "bullet_spd": 6, "dmg": 25, "size": 64},
    }

    def __init__(self, etype, x, y, wave=1):
        self.etype = etype
        stats = self.TYPES[etype].copy()
        scale = 1 + (wave - 1) * 0.15
        self.hp = int(stats["hp"] * scale)
        self.max_hp = self.hp
        self.speed = stats["speed"]
        self.score_val = stats["score"]
        self.shoot_timer = random.randint(0, stats["shoot_rate"])
        self.shoot_rate = stats["shoot_rate"]
        self.bullet_spd = stats["bullet_spd"]
        self.dmg = stats["dmg"]
        self.size = stats["size"] if etype != "boss" else 64
        self.x, self.y = x, y
        self.w = self.h = self.size
        self.sprite = draw_enemy(etype, self.size)
        self.angle = 0
        self.move_timer = 0
        self.dir = 1
        self.entry_y = -self.h
        self.entered = False

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, bullets, player_x, player_y):
        if not self.entered:
            self.y += self.speed * 2
            if self.y >= self.entry_y + self.h + 20:
                self.entered = True
            return

        if self.etype == "basic":
            self.y += self.speed
        elif self.etype == "fast":
            self.move_timer += 0.07
            self.x += math.sin(self.move_timer) * 3
            self.y += self.speed
        elif self.etype == "tank":
            self.y += self.speed
        elif self.etype == "boss":
            self.move_timer += 1
            self.y = min(self.y + 0.5, 60)
            self.x += self.speed * self.dir
            if self.x < 0 or self.x > W - self.w:
                self.dir *= -1

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_rate
            cx = int(self.x + self.w // 2)
            cy = int(self.y + self.h)
            if self.etype == "boss":
                for angle in [-20, 0, 20]:
                    rad = math.radians(90 + angle)
                    vx = math.cos(rad) * self.bullet_spd
                    vy = math.sin(rad) * self.bullet_spd
                    bullets.append(Bullet(cx, cy, vy, RED, "enemy", vx))
            else:
                bullets.append(Bullet(cx, cy, self.bullet_spd, ORANGE, "enemy"))

    def draw(self, surf):
        surf.blit(self.sprite, (int(self.x), int(self.y)))
        if self.etype in ("tank", "boss"):
            bw = self.w
            bh = 5 if self.etype == "tank" else 8
            ratio = self.hp / self.max_hp
            pygame.draw.rect(surf, (80, 0, 0), (int(self.x), int(self.y) - bh - 2, bw, bh), border_radius=2)
            pygame.draw.rect(surf, RED, (int(self.x), int(self.y) - bh - 2, int(bw * ratio), bh), border_radius=2)


class PowerUp:
    TYPES = ["health", "rapid", "shield", "bomb"]

    def __init__(self, x, y, ptype=None):
        self.ptype = ptype or random.choice(self.TYPES)
        self.x, self.y = x, y
        self.w = self.h = 22
        self.speed = 1.8
        self.sprite = draw_powerup(self.ptype)
        self.bob = 0
        self.age = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y + math.sin(self.bob) * 4), self.w, self.h)

    def update(self):
        self.y += self.speed
        self.bob += 0.12
        self.age += 1

    def draw(self, surf):
        y = int(self.y + math.sin(self.bob) * 4)
        glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*YELLOW, 40), (20, 20), 18)
        surf.blit(glow, (int(self.x) - 9, y - 9))
        surf.blit(self.sprite, (int(self.x), y))
