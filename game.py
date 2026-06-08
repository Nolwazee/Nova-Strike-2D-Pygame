"""
NOVA STRIKE
A 2D top-down space shooter built with Pygame.
Genre: Space Shooter / Arcade
Storyline: Earth's last fighter pilot defends the solar system against an alien invasion fleet.
"""

import pygame
import math
import random
import sys
import os
import json
import socket
import threading
from datetime import datetime

# ─── INIT ───────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
W, H = 800, 700
FPS = 60
TITLE = "NOVA STRIKE"

# Colours
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
CYAN   = (0, 220, 255)
YELLOW = (255, 220, 0)
RED    = (255, 50, 50)
GREEN  = (50, 255, 120)
ORANGE = (255, 140, 0)
PURPLE = (160, 60, 255)
DARK_BLUE = (5, 5, 30)
NEON_BLUE  = (0, 170, 255)
NEON_GREEN = (0, 255, 160)
GREY   = (120, 120, 140)
PINK   = (255, 80, 180)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# ─── SAVE SYSTEM ─────────────────────────────────────────────────────────────
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
os.makedirs(SAVE_DIR, exist_ok=True)

def save_game(profile, wave, score, hp, difficulty_label):
    """Save game state to saves/<profile>.json"""
    data = {
        "profile":    profile,
        "wave":       wave,
        "score":      score,
        "hp":         hp,
        "difficulty": difficulty_label,
        "saved_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    path = os.path.join(SAVE_DIR, f"{profile}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def load_game(profile):
    """Load save data for profile. Returns dict or None."""
    path = os.path.join(SAVE_DIR, f"{profile}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None

def delete_save(profile):
    """Delete a save file."""
    path = os.path.join(SAVE_DIR, f"{profile}.json")
    if os.path.exists(path):
        os.remove(path)

def list_saves():
    """Return list of (profile_name, save_data) for all saves."""
    saves = []
    if not os.path.exists(SAVE_DIR):
        return saves
    for fname in os.listdir(SAVE_DIR):
        if fname.endswith(".json"):
            profile = fname[:-5]
            data = load_game(profile)
            if data:
                saves.append((profile, data))
    return sorted(saves, key=lambda x: x[1].get("saved_at", ""), reverse=True)

# Active profile for this session
_active_profile = "Player1"

def get_profile():
    return _active_profile

def set_profile(name):
    global _active_profile
    _active_profile = name.strip() or "Player1"


# ─── SOUND GENERATOR ─────────────────────────────────────────────────────────
def make_sound(freq, duration_ms, wave="sine", volume=0.4, envelope=True):
    """Procedurally generate a sound effect."""
    import numpy as np
    sample_rate = 44100
    n = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n, endpoint=False)

    if wave == "sine":
        data = np.sin(2 * np.pi * freq * t)
    elif wave == "square":
        data = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == "saw":
        data = 2 * (t * freq - np.floor(t * freq + 0.5))
    elif wave == "noise":
        data = np.random.uniform(-1, 1, n)
    elif wave == "sweep":
        f = np.linspace(freq, freq * 0.3, n)
        data = np.sin(2 * np.pi * np.cumsum(f) / sample_rate)
    else:
        data = np.sin(2 * np.pi * freq * t)

    if envelope:
        attack = int(n * 0.05)
        release = int(n * 0.4)
        env = np.ones(n)
        env[:attack] = np.linspace(0, 1, attack)
        env[n - release:] = np.linspace(1, 0, release)
        data *= env

    data = (data * volume * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])
    sound = pygame.sndarray.make_sound(stereo)
    return sound


try:
    import numpy as np
    SFX = {
        "shoot":    make_sound(880,  80,  "square", 0.25),
        "explode":  make_sound(120,  500, "sweep",  0.5),
        "powerup":  make_sound(660,  300, "sine",   0.4),
        "hit":      make_sound(300,  120, "noise",  0.35),
        "gameover": make_sound(80,   800, "saw",    0.4),
        "level_up": make_sound(1200, 400, "sine",   0.45),
        "shield":   make_sound(440,  200, "sine",   0.3),
    }
    MUSIC_ENABLED = True
except ImportError:
    SFX = {}
    MUSIC_ENABLED = False

def play(name):
    if name in SFX:
        SFX[name].play()


def generate_music():
    """Generate looping background music as a stream of notes."""
    if not MUSIC_ENABLED:
        return None
    try:
        import numpy as np
        sample_rate = 44100
        bpm = 130
        beat = 60 / bpm
        pattern = [
            (110, beat * 0.5), (0, beat * 0.5),
            (138, beat * 0.5), (0, beat * 0.25),
            (110, beat * 0.25),(165, beat * 0.5),
            (0, beat * 0.5),   (123, beat * 0.5),
            (0, beat * 0.5),   (110, beat * 1.0),
        ]
        chunks = []
        for freq, dur in pattern:
            n = int(sample_rate * dur)
            t = np.linspace(0, dur, n, endpoint=False)
            if freq > 0:
                d = (np.sin(2 * np.pi * freq * t) * 0.2 +
                     np.sin(2 * np.pi * freq * 2 * t) * 0.08)
                env = np.ones(n)
                r = int(n * 0.3)
                env[n - r:] = np.linspace(1, 0, r)
                d *= env
            else:
                d = np.zeros(n)
            chunks.append((d * 8000).astype(np.int16))
        loop = np.concatenate(chunks)
        stereo = np.column_stack([loop, loop])
        snd = pygame.sndarray.make_sound(stereo)
        return snd
    except Exception:
        return None


# ─── ASSET DRAWING (procedural sprites) ─────────────────────────────────────

def draw_player_ship(color=CYAN, size=36):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    # Body
    pts = [(cx, 2), (cx + 14, size - 8), (cx, size - 14), (cx - 14, size - 8)]
    pygame.draw.polygon(s, color, pts)
    pygame.draw.polygon(s, WHITE, pts, 1)
    # Cockpit
    pygame.draw.ellipse(s, (180, 240, 255), (cx - 5, cy - 4, 10, 8))
    # Engine glow
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
        # star burst
        for a in range(0, 360, 45):
            r = math.radians(a)
            x2 = cx + math.cos(r) * (cx - 4)
            y2 = cy + math.sin(r) * (cy - 4)
            pygame.draw.line(s, WHITE, (cx, cy), (int(x2), int(y2)), 2)
    return s


def draw_star_field(n=180):
    stars = []
    for _ in range(n):
        x = random.randint(0, W)
        y = random.randint(0, H)
        sp = random.uniform(0.5, 3.0)
        br = random.randint(100, 255)
        size = random.choice([1, 1, 1, 2])
        stars.append([x, y, sp, br, size])
    return stars


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
    def __init__(self, color=CYAN, bullet_color=NEON_GREEN):
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
        self.sprite = draw_player_ship(color=color)
        self.bullet_color = bullet_color
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

    def shoot(self, bullets, owner_id="player"):
        if self.shoot_cooldown <= 0:
            cd = 8 if self.rapid_timer > 0 else self.base_cooldown
            cx = self.x + self.w // 2
            bullets.append(Bullet(cx - 2, self.y, -14, self.bullet_color, owner_id))
            if self.rapid_timer > 0:
                bullets.append(Bullet(cx - 10, self.y + 6, -13, self.bullet_color, owner_id))
                bullets.append(Bullet(cx + 6,  self.y + 6, -13, self.bullet_color, owner_id))
            self.shoot_cooldown = cd
            play("shoot")

    def update(self):
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.rapid_timer  > 0:  self.rapid_timer  -= 1
        if self.shield_timer > 0:  self.shield_timer -= 1
        if self.invincible   > 0:  self.invincible   -= 1
        self.engine_frame += 1

    def take_damage(self, dmg):
        if self.invincible > 0: return False
        if self.shield_timer > 0:
            play("shield")
            self.shield_timer = 0
            self.invincible = 60
            return False
        self.hp -= dmg
        self.invincible = 45
        play("hit")
        return True

    def draw(self, surf):
        # Engine trail
        if self.engine_frame % 3 == 0:
            pass  # handled via particles outside
        # Blink when invincible
        if self.invincible > 0 and self.invincible % 8 < 4:
            return
        surf.blit(self.sprite, (self.x, self.y))
        # Shield ring
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
        self.dir = 1  # for boss side movement
        self.entry_y = -self.h  # start off-screen
        self.entered = False
        # Boss phase system
        self.boss_phase = 0      # 0, 1, 2
        self.boss_shot_count = 0 # shots fired in current phase
        self.boss_angle = 0      # for circular movement

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, bullets, player_x, player_y):
        # Entry phase
        if not self.entered:
            self.y += self.speed * 2
            if self.y >= self.entry_y + self.h + 20:
                self.entered = True
            return

        if self.etype == "basic":
            self.y += self.speed
        elif self.etype == "fast":
            # Sine wave movement
            self.move_timer += 0.07
            self.x += math.sin(self.move_timer) * 3
            self.y += self.speed
        elif self.etype == "tank":
            self.y += self.speed
        elif self.etype == "boss":
            self.move_timer += 1
            self.y = min(self.y + 0.5, 60)
            if self.boss_phase == 0:
                # Phase 1: slow horizontal hover
                self.x += self.speed * self.dir
                if self.x < 0 or self.x > W - self.w:
                    self.dir *= -1
            elif self.boss_phase == 1:
                # Phase 2: fast diagonal zigzag
                self.x += self.speed * 2.5 * self.dir
                if self.x < 0 or self.x > W - self.w:
                    self.dir *= -1
                    self.y = min(self.y + 8, 120)
            elif self.boss_phase == 2:
                # Phase 3: circular figure-8 hover
                self.boss_angle += 0.03
                self.x = W // 2 - self.w // 2 + math.sin(self.boss_angle) * 200
                self.y = 60 + math.sin(self.boss_angle * 2) * 30

        # Shooting
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = self.shoot_rate
            cx = int(self.x + self.w // 2)
            cy = int(self.y + self.h)
            if self.etype == "boss":
                if self.boss_phase == 0:
                    # Phase 1: 3-way spread
                    for angle in [-20, 0, 20]:
                        rad = math.radians(90 + angle)
                        vx = math.cos(rad) * self.bullet_spd
                        vy = math.sin(rad) * self.bullet_spd
                        bullets.append(Bullet(cx, cy, vy, RED, "enemy", vx))
                elif self.boss_phase == 1:
                    # Phase 2: 5-way wide fan
                    for angle in [-40, -20, 0, 20, 40]:
                        rad = math.radians(90 + angle)
                        vx = math.cos(rad) * self.bullet_spd
                        vy = math.sin(rad) * self.bullet_spd
                        bullets.append(Bullet(cx, cy, vy, ORANGE, "enemy", vx))
                elif self.boss_phase == 2:
                    # Phase 3: aimed shot at player + 2 flanking shots
                    dx = player_x - cx
                    dy = player_y - cy
                    dist = max(1, math.hypot(dx, dy))
                    vx_aim = (dx / dist) * self.bullet_spd
                    vy_aim = (dy / dist) * self.bullet_spd
                    bullets.append(Bullet(cx, cy, vy_aim, PURPLE, "enemy", vx_aim))
                    # Flanking
                    for angle_offset in [-30, 30]:
                        rad = math.atan2(dy, dx) + math.radians(angle_offset)
                        bullets.append(Bullet(cx, cy, math.sin(rad) * self.bullet_spd,
                                              PINK, "enemy", math.cos(rad) * self.bullet_spd))
                # Cycle phase after every 3 shots
                self.boss_shot_count += 1
                if self.boss_shot_count >= 3:
                    self.boss_shot_count = 0
                    self.boss_phase = (self.boss_phase + 1) % 3
            else:
                bullets.append(Bullet(cx, cy, self.bullet_spd, ORANGE, "enemy"))

    def draw(self, surf):
        surf.blit(self.sprite, (int(self.x), int(self.y)))
        # HP bar (for tank and boss)
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
        # Glow
        glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*YELLOW, 40), (20, 20), 18)
        surf.blit(glow, (int(self.x) - 9, y - 9))
        surf.blit(self.sprite, (int(self.x), y))


# ─── WAVE DEFINITIONS ────────────────────────────────────────────────────────

def build_wave(wave_num, speed_mult=1.0):
    enemies = []
    if wave_num % 5 == 0:  # Boss wave
        e = Enemy("boss", W // 2 - 32, -80, wave_num)
        e.entry_y = 40
        e.speed *= speed_mult
        enemies.append(e)
    else:
        count_basic = 4 + wave_num * 2
        count_fast  = wave_num
        count_tank  = max(0, wave_num - 1)
        cols = 8
        spacing_x = W // (cols + 1)

        all_types = (["basic"] * count_basic +
                     ["fast"]  * count_fast  +
                     ["tank"]  * count_tank)
        random.shuffle(all_types)

        for i, etype in enumerate(all_types):
            row = i // cols
            col = i % cols
            x = spacing_x * (col + 1) - 15
            y = -60 - row * 70
            e = Enemy(etype, x, y, wave_num)
            e.entry_y = 60 + row * 70
            e.speed *= speed_mult
            enemies.append(e)
    return enemies


# ─── WAVE RULES ──────────────────────────────────────────────────────────────

def get_required_kills(wave, wave_total):
    """Minimum player kills needed before a wave can be cleared."""
    if wave % 5 == 0:
        return 1  # boss must be defeated
    return max(1, math.ceil(wave_total * 0.7))


# ─── HUD DRAWING ─────────────────────────────────────────────────────────────

font_big   = pygame.font.SysFont("consolas", 48, bold=True)
font_med   = pygame.font.SysFont("consolas", 28, bold=True)
font_small = pygame.font.SysFont("consolas", 18)
font_tiny  = pygame.font.SysFont("consolas", 14)


def draw_hud(surf, player, wave, enemies_left, bomb_available,
             wave_total=0, kills_this_wave=0, required_kills=0, diff_label=""):
    # HP bar
    bar_w = 200
    ratio = player.hp / player.max_hp
    bar_color = GREEN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
    pygame.draw.rect(surf, (40, 40, 60), (10, 10, bar_w, 18), border_radius=4)
    pygame.draw.rect(surf, bar_color, (10, 10, int(bar_w * ratio), 18), border_radius=4)
    pygame.draw.rect(surf, WHITE, (10, 10, bar_w, 18), 1, border_radius=4)
    hp_txt = font_tiny.render(f"HP {player.hp}/{player.max_hp}", True, WHITE)
    surf.blit(hp_txt, (14, 13))

    # Score
    score_txt = font_med.render(f"SCORE  {player.score:07d}", True, CYAN)
    surf.blit(score_txt, (W // 2 - score_txt.get_width() // 2, 8))

    # Wave label — red on boss waves
    is_boss_wave = (wave % 5 == 0)
    wave_label = f"BOSS  WAVE  {wave}" if is_boss_wave else f"WAVE  {wave}"
    wave_txt = font_small.render(wave_label, True, RED if is_boss_wave else YELLOW)
    surf.blit(wave_txt, (W - wave_txt.get_width() - 10, 8))

    if is_boss_wave:
        # Boss wave: just remind the player what to do
        boss_txt = font_tiny.render("DEFEAT  THE  BOSS", True, RED)
        surf.blit(boss_txt, (W - boss_txt.get_width() - 10, 28))
    else:
        # Normal wave: kills progress (turns green when threshold met) + enemies remaining
        kills_color = NEON_GREEN if kills_this_wave >= required_kills else GREY
        kills_txt = font_tiny.render(f"KILLS: {kills_this_wave}/{required_kills}", True, kills_color)
        surf.blit(kills_txt, (W - kills_txt.get_width() - 10, 28))
        en_label = f"LEFT: {enemies_left}/{wave_total}" if wave_total else f"LEFT: {enemies_left}"
        en_txt = font_tiny.render(en_label, True, GREY)
        surf.blit(en_txt, (W - en_txt.get_width() - 10, 44))

    # Power-up timers
    y = 36
    if player.rapid_timer > 0:
        t = font_tiny.render(f"RAPID x2  {player.rapid_timer // FPS + 1}s", True, YELLOW)
        surf.blit(t, (10, y)); y += 16
    if player.shield_timer > 0:
        t = font_tiny.render(f"SHIELD  {player.shield_timer // FPS + 1}s", True, CYAN)
        surf.blit(t, (10, y)); y += 16

    # Bomb
    bomb_col = ORANGE if bomb_available else GREY
    bomb_txt = font_tiny.render("[ SPACE ] BOMB" if bomb_available else "NO BOMB", True, bomb_col)
    surf.blit(bomb_txt, (10, H - 22))

    # Difficulty label (bottom-right)
    if diff_label:
        diff_txt = font_tiny.render(f"DIFFICULTY: {diff_label}", True, GREY)
        surf.blit(diff_txt, (W - diff_txt.get_width() - 10, H - 22))


def draw_stars(surf, stars):
    for s in stars:
        c = int(s[3])
        col = (c, c, min(255, c + 60))
        if s[4] == 1:
            surf.set_at((int(s[0]), int(s[1])), col)
        else:
            pygame.draw.circle(surf, col, (int(s[0]), int(s[1])), s[4])


def scroll_stars(stars):
    for s in stars:
        s[1] += s[2]
        if s[1] > H:
            s[1] = 0
            s[0] = random.randint(0, W)


# ─── MULTIPLAYER NETWORK MANAGER ─────────────────────────────────────────────

MP_PORT = 55555
MP_BUFFER = 2048

class NetworkManager:
    """Handles socket communication for LAN/internet co-op."""
    def __init__(self):
        self.sock = None
        self.conn = None          # host: accepted connection
        self.connected = False
        self.is_host = False
        self.recv_data = {}       # latest received state
        self.send_lock = threading.Lock()
        self._recv_thread = None

    def host(self, port=MP_PORT):
        self.is_host = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", port))
        self.sock.listen(1)
        self.sock.settimeout(60)
        try:
            self.conn, addr = self.sock.accept()
            self.conn.settimeout(2)
            try:
                self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except Exception:
                pass
            self.connected = True
            self._start_recv(self.conn)
            return addr[0]
        except Exception:
            return None

    def join(self, host_ip, port=MP_PORT):
        self.is_host = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(8)
        try:
            self.sock.connect((host_ip, port))
            self.sock.settimeout(2)
            try:
                self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except Exception:
                pass
            self.connected = True
            self._start_recv(self.sock)
            return True
        except Exception:
            return False

    def _start_recv(self, sock):
        def recv_loop():
            buf = ""
            while self.connected:
                try:
                    chunk = sock.recv(MP_BUFFER).decode("utf-8", errors="ignore")
                    if not chunk:
                        break
                    buf += chunk
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        try:
                            self.recv_data = json.loads(line)
                        except Exception:
                            pass
                except Exception:
                    break
            self.connected = False
        self._recv_thread = threading.Thread(target=recv_loop, daemon=True)
        self._recv_thread.start()

    def send(self, data):
        if not self.connected:
            return
        sock = self.conn if self.is_host else self.sock
        try:
            with self.send_lock:
                sock.sendall((json.dumps(data) + "\n").encode("utf-8"))
        except Exception:
            self.connected = False

    def close(self):
        self.connected = False
        try:
            if self.conn: self.conn.close()
            if self.sock: self.sock.close()
        except Exception:
            pass

    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def text_input_box(prompt, default="", max_len=20):
    """Full-screen text input. Returns typed string or default on ESC."""
    stars = draw_star_field(180)
    text = default
    tick = 0
    pygame.key.start_text_input()
    try:
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                elif ev.type == pygame.TEXTINPUT:
                    if len(text) < max_len:
                        text += ev.text
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return text.strip() or "Player1"
                    elif ev.key == pygame.K_ESCAPE:
                        return default or "Player1"
                    elif ev.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif ev.unicode and len(text) < max_len and ev.unicode.isprintable() and ev.key not in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        text += ev.unicode
            
            screen.fill(DARK_BLUE)
            scroll_stars(stars)
            draw_stars(screen, stars)
            p = font_small.render(prompt, True, CYAN)
            screen.blit(p, (W//2 - p.get_width()//2, H//2 - 60))
            # Input box
            box = pygame.Rect(W//2 - 160, H//2 - 20, 320, 44)
            pygame.draw.rect(screen, (20, 20, 50), box, border_radius=6)
            pygame.draw.rect(screen, CYAN, box, 2, border_radius=6)
            cursor = "|" if tick % 60 < 30 else ""
            txt = font_med.render(text + cursor, True, WHITE)
            screen.blit(txt, (box.x + 12, box.y + 8))
            hint = font_tiny.render("ENTER to confirm   ESC to cancel", True, GREY)
            screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 40))
            pygame.display.flip()
            clock.tick(FPS)
            tick += 1
    finally:
        pygame.key.stop_text_input()


def profile_screen():
    """Profile selection / creation screen. Returns chosen profile name."""
    saves = list_saves()
    stars = draw_star_field(180)
    tick = 0
    selected = 0  # 0 = "New Profile", 1+ = existing saves

    options = ["[ NEW PROFILE ]"] + [f"{s[0]}  —  Wave {s[1]['wave']}  ({s[1]['saved_at']})" for s in saves]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    if selected == 0:
                        name = text_input_box("Enter your pilot name:", default="")
                        set_profile(name)
                    else:
                        set_profile(saves[selected - 1][0])
                    return get_profile()
                elif ev.key == pygame.K_ESCAPE:
                    return get_profile()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i in range(len(options)):
                    y = 110 + i * 44
                    rect = pygame.Rect(40, y - 4, W - 80, 36)
                    if rect.collidepoint(ev.pos):
                        if i == 0:
                            name = text_input_box("Enter your pilot name:", default="")
                            set_profile(name)
                        else:
                            set_profile(saves[i - 1][0])
                        return get_profile()

        # Update hovered selection using mouse position
        for i in range(len(options)):
            y = 110 + i * 44
            rect = pygame.Rect(40, y - 4, W - 80, 36)
            if rect.collidepoint(mouse_pos):
                selected = i

        screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(screen, stars)

        hdr = font_med.render("SELECT  PROFILE", True, CYAN)
        screen.blit(hdr, (W//2 - hdr.get_width()//2, 50))
        pygame.draw.line(screen, CYAN, (60, 88), (W-60, 88), 1)

        for i, opt in enumerate(options):
            y = 110 + i * 44
            is_sel = (i == selected)
            col = YELLOW if is_sel else GREY
            if i == 0: col = NEON_GREEN if is_sel else GREEN
            if is_sel:
                pygame.draw.rect(screen, (20, 20, 50), (40, y - 4, W - 80, 36), border_radius=4)
                pygame.draw.rect(screen, col, (40, y - 4, W - 80, 36), 1, border_radius=4)
            t = font_small.render(opt, True, col)
            screen.blit(t, (60, y))

        hint = font_tiny.render("↑ / ↓  Navigate   ENTER / CLICK  Select   ESC  Back", True, GREY)
        screen.blit(hint, (W//2 - hint.get_width()//2, H - 28))
        pygame.display.flip()
        clock.tick(FPS)
        tick += 1


# ─── SCREENS ─────────────────────────────────────────────────────────────────

def story_crawl():
    """Star Wars-style scrolling story intro for Wave 1."""
    stars = draw_star_field(200)
    crawl_lines = [
        "",
        "A long time ago, in a galaxy",
        "under siege...",
        "",
        "",
        "N O V A   S T R I K E",
        "",
        "",
        "Humanity is on the brink",
        "of extinction.",
        "",
        "An unstoppable alien race",
        "known as the VOID ARMADA",
        "has invaded Earth,",
        "destroying cities, countries",
        "and military defenses",
        "worldwide.",
        "",
        "As Earth's final fighter pilot,",
        "you are humanity's last hope.",
        "",
        "Wave after wave of enemy ships",
        "descend from deep space.",
        "",
        "Your mission:",
        "",
        "      Survive.",
        "      Defend Earth.",
        "      Destroy the alien fleet.",
        "      Defeat the invasion.",
        "",
        "",
        "",
    ]

    line_h = 32
    total_h = len(crawl_lines) * line_h
    scroll_y = float(H)          # starts below screen
    scroll_speed = 1.2
    font_crawl_title = pygame.font.SysFont("consolas", 32, bold=True)
    font_crawl = pygame.font.SysFont("consolas", 20)

    # Perspective gradient mask
    fade_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for fy in range(H):
        alpha = int(255 * (fy / H) ** 1.5)
        fade_surf.fill((5, 5, 30, 255 - alpha), (0, fy, W, 1))

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return

        screen.fill((0, 0, 0))
        scroll_stars(stars)
        draw_stars(screen, stars)

        # Draw crawl lines
        for i, line in enumerate(crawl_lines):
            y = int(scroll_y) + i * line_h
            if y < -line_h or y > H:
                continue
            is_title = (line.strip() == "N O V A   S T R I K E")
            font_use = font_crawl_title if is_title else font_crawl
            col = CYAN if is_title else YELLOW
            txt = font_use.render(line, True, col)
            # Fade out top
            fade = max(0, min(255, y * 3))
            txt.set_alpha(fade)
            screen.blit(txt, (W // 2 - txt.get_width() // 2, y))

        # Overlay perspective fade
        screen.blit(fade_surf, (0, 0))

        # Skip hint
        hint = font_tiny.render("PRESS SPACE / ENTER TO SKIP", True, GREY)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 30))

        pygame.display.flip()
        clock.tick(FPS)
        scroll_y -= scroll_speed

        # Auto-end when all text has scrolled off
        if scroll_y + total_h < 0:
            return


def tutorial_stage():
    """Level 0 — Interactive tutorial teaching all controls."""
    stars = draw_star_field(200)
    player = Player()
    bullets = []
    particles = []

    # Dummy target enemy (can't shoot, high HP)
    dummy = Enemy("basic", W // 2 - 15, 180, wave=1)
    dummy.entered = True
    dummy.hp = 9999
    dummy.shoot_rate = 99999  # never shoots
    dummy.shoot_timer = 99999

    # Tutorial steps: (description, completion_fn)
    steps = [
        ("Move your ship!  [ WASD / ARROW KEYS ]",   None),
        ("Shoot the target!  [ Z / LEFT CTRL ]",     None),
        ("Drop a BOMB!  [ SPACE ]",                  None),
        ("Pause and Resume!  [ ESC / P ]",           None),
    ]
    step = 0
    moved_dirs = set()   # track {left, right, up, down}
    shots_fired = 0
    bomb_used = False
    pause_done = False

    # Grant player a bomb for step 3
    bomb_available = True

    tick = 0
    clock_tut = pygame.time.Clock()

    while step < len(steps):
        dt = clock_tut.tick(FPS)

        # ── Events
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_z, pygame.K_LCTRL, pygame.K_RCTRL):
                    player.shoot(bullets)
                    shots_fired += 1
                if ev.key == pygame.K_SPACE and step == 2 and bomb_available:
                    bomb_available = False
                    bomb_used = True
                    # Bomb flash effect
                    for _ in range(30):
                        particles.append(Particle(
                            random.randint(0, W), random.randint(0, H // 2),
                            random.choice([ORANGE, YELLOW, RED]),
                            (random.uniform(-5, 5), random.uniform(-3, 3)),
                            random.randint(20, 45), random.randint(3, 7)
                        ))
                if ev.key in (pygame.K_ESCAPE, pygame.K_p) and step == 3:
                    # Show the pause screen as part of the tutorial
                    action = pause_screen(screen)
                    if action == "resume":
                        pause_done = True

        keys = pygame.key.get_pressed()
        old_x, old_y = player.x, player.y
        player.move(keys)
        player.update()
        # Track directions moved
        if player.x < old_x: moved_dirs.add("left")
        if player.x > old_x: moved_dirs.add("right")
        if player.y < old_y: moved_dirs.add("up")
        if player.y > old_y: moved_dirs.add("down")
        if keys[pygame.K_z] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            player.shoot(bullets)
            shots_fired += 1

        # Engine trail
        if tick % 4 == 0:
            cx = player.x + player.w // 2
            cy = player.y + player.h - 4
            particles.append(Particle(cx + random.randint(-3, 3), cy,
                                      random.choice([ORANGE, YELLOW]),
                                      (random.uniform(-0.3, 0.3), random.uniform(1, 2.5)),
                                      life=random.randint(8, 18), size=random.randint(2, 4)))

        # Update bullets
        for b in bullets[:]:
            b.update()
            if b.y < -20 or b.y > H + 20:
                bullets.remove(b)

        # Update particles
        for pt in particles[:]:
            pt.update()
            if pt.life <= 0:
                particles.remove(pt)

        # ── Step completion checks
        if step == 0 and len(moved_dirs) >= 4:
            step = 1
        elif step == 1 and shots_fired >= 5:
            step = 2
        elif step == 2 and bomb_used:
            step = 3
        elif step == 3 and pause_done:
            step = 4  # done
            break

        # ── Draw
        screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(screen, stars)
        for pt in particles: pt.draw(screen)
        for b in bullets: b.draw(screen)

        # Draw dummy target
        dummy.draw(screen)
        # Draw a subtle label above dummy
        lbl = font_tiny.render("[ TRAINING TARGET ]", True, GREY)
        screen.blit(lbl, (dummy.x + dummy.w // 2 - lbl.get_width() // 2, dummy.y - 20))

        player.draw(screen)

        # ── Tutorial panel
        panel_y = H - 130
        panel = pygame.Surface((W, 130), pygame.SRCALPHA)
        panel.fill((10, 10, 40, 200))
        screen.blit(panel, (0, panel_y))

        header = font_small.render("▶  TRAINING  MODE", True, CYAN)
        screen.blit(header, (W // 2 - header.get_width() // 2, panel_y + 6))

        # Steps list
        for i, (desc, _) in enumerate(steps):
            if i < step:
                col = GREEN
                prefix = "✓  "
            elif i == step:
                col = YELLOW if tick % 60 < 40 else WHITE
                prefix = "▶  "
            else:
                col = GREY
                prefix = "   "
            t = font_tiny.render(prefix + desc, True, col)
            screen.blit(t, (20, panel_y + 30 + i * 22))

        # Bomb indicator
        bomb_col = ORANGE if bomb_available else GREY
        bt = font_tiny.render("BOMB READY" if bomb_available else "BOMB USED", True, bomb_col)
        screen.blit(bt, (W - bt.get_width() - 14, panel_y + 30))

        pygame.display.flip()
        tick += 1

    # Flash "TRAINING COMPLETE!"
    for frame in range(100):
        screen.fill(DARK_BLUE)
        draw_stars(screen, stars)
        alpha = 255 if frame < 60 else max(0, 255 - (frame - 60) * 8)
        msg = font_big.render("TRAINING  COMPLETE!", True, NEON_GREEN)
        tmp = pygame.Surface(msg.get_size(), pygame.SRCALPHA)
        tmp.blit(msg, (0, 0))
        tmp.set_alpha(alpha)
        screen.blit(tmp, (W // 2 - msg.get_width() // 2, H // 2 - 30))
        pygame.display.flip()
        clock_tut.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()


def title_screen():
    """Main menu. Returns one of: 'new', 'continue', 'multiplayer', 'quit'."""
    stars = draw_star_field(200)
    ship_y = float(H + 50)
    target_y = H // 2 - 60
    ship_sprite = draw_player_ship(size=60)
    tick = 0
    selected = 0

    while True:
        save_data = load_game(get_profile())
        has_save = save_data is not None

        menu_items = []
        if has_save:
            menu_items.append(("CONTINUE",    NEON_GREEN,  "continue"))
        menu_items.append(    ("NEW GAME",     YELLOW,      "new"))
        menu_items.append(    ("MULTIPLAYER",  CYAN,        "multiplayer"))
        menu_items.append(    ("PROFILE",      PURPLE,      "profile"))
        menu_items.append(    ("QUIT",         RED,         "quit"))

        selected = max(0, min(selected, len(menu_items) - 1))
        start_y = H // 2 + 10
        mouse_pos = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(menu_items)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(menu_items)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    action = menu_items[selected][2]
                    if action == "profile":
                        profile_screen()
                    else:
                        return action
                elif ev.key == pygame.K_c and has_save:
                    return "continue"
                elif ev.key == pygame.K_n:
                    return "new"
                elif ev.key == pygame.K_m:
                    return "multiplayer"
                elif ev.key == pygame.K_p:
                    profile_screen()
                elif ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "quit"
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, (label, col, action) in enumerate(menu_items):
                    rect = pygame.Rect(W // 2 - 180, start_y + i * 44 - 4, 360, 36)
                    if rect.collidepoint(ev.pos):
                        if action == "profile":
                            profile_screen()
                        else:
                            return action

        # Update hovered selection using mouse position
        for i, (label, col, action) in enumerate(menu_items):
            rect = pygame.Rect(W // 2 - 180, start_y + i * 44 - 4, 360, 36)
            if rect.collidepoint(mouse_pos):
                selected = i

        screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(screen, stars)

        # Animate ship flying in
        if ship_y > target_y:
            ship_y -= 4
        # Engine trail
        if tick % 2 == 0:
            pass  # simplified

        # Title text
        title = font_big.render("NOVA  STRIKE", True, CYAN)
        shadow = font_big.render("NOVA  STRIKE", True, PURPLE)
        tx = W // 2 - title.get_width() // 2
        screen.blit(shadow, (tx + 3, 83))
        screen.blit(title, (tx, 80))

        sub = font_small.render("Earth's last fighter. The stars await.", True, GREY)
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 148))

        prof_lbl = font_small.render(f"Pilot Profile: {get_profile()}", True, YELLOW)
        screen.blit(prof_lbl, (W // 2 - prof_lbl.get_width() // 2, 180))

        screen.blit(ship_sprite, (W // 2 - 30, int(ship_y)))

        # Draw interactive menu items
        for i, (label, col, action) in enumerate(menu_items):
            is_sel = (i == selected)
            prefix = "▶ " if is_sel else "  "
            text_color = WHITE if is_sel and (tick % 30 < 15) else (WHITE if is_sel else col)
            if action == "continue" and has_save:
                lbl = font_med.render(f"{prefix}{label} (Wave {save_data['wave']})", True, text_color)
            else:
                lbl = font_med.render(f"{prefix}{label}", True, text_color)
            screen.blit(lbl, (W // 2 - lbl.get_width() // 2, start_y + i * 44))

        controls = [
            "WASD / ARROW KEYS : MOVE     Z / CTRL : SHOOT",
            "SPACE : BOMB (collect first!)     ESC / P : PAUSE",
        ]
        for i, line in enumerate(controls):
            t = font_tiny.render(line, True, GREY)
            screen.blit(t, (W // 2 - t.get_width() // 2, H - 54 + i * 17))

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1


def game_over_screen(score, wave):
    stars = draw_star_field(200)
    tick = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: return "retry"
                if ev.key == pygame.K_ESCAPE: return "quit"

        screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(screen, stars)

        over = font_big.render("GAME  OVER", True, RED)
        screen.blit(over, (W // 2 - over.get_width() // 2, 140))

        sc = font_med.render(f"SCORE: {score:07d}", True, YELLOW)
        screen.blit(sc, (W // 2 - sc.get_width() // 2, 220))

        wv = font_med.render(f"REACHED WAVE {wave}", True, CYAN)
        screen.blit(wv, (W // 2 - wv.get_width() // 2, 262))

        if tick % 80 < 55:
            r = font_med.render("[ R ] RETRY     [ ESC ] QUIT", True, WHITE)
            screen.blit(r, (W // 2 - r.get_width() // 2, H - 100))

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1


def wave_banner(wave_num):
    """Show a brief wave announcement."""
    is_boss = (wave_num % 5 == 0)
    msg = f"⚠  BOSS  WAVE  {wave_num}  ⚠" if is_boss else f"WAVE  {wave_num}"
    color = RED if is_boss else CYAN
    for frame in range(80):
        screen.fill(DARK_BLUE)
        alpha = 255 if frame < 50 else max(0, 255 - (frame - 50) * 12)
        txt = font_big.render(msg, True, color)
        tmp = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        tmp.blit(txt, (0, 0))
        tmp.set_alpha(alpha)
        screen.blit(tmp, (W // 2 - txt.get_width() // 2, H // 2 - 30))
        pygame.display.flip()
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()


def pause_screen(surf, wave=1, score=0, hp=100, diff_label="MEDIUM"):
    """Semi-transparent pause overlay. Returns 'resume','restart','save_quit', or 'menu'."""
    overlay = surf.copy()
    darken = pygame.Surface((W, H), pygame.SRCALPHA)
    darken.fill((10, 10, 30, 180))
    overlay.blit(darken, (0, 0))

    title  = font_big.render("GAME  PAUSED", True, CYAN)
    shadow = font_big.render("GAME  PAUSED", True, PURPLE)

    options = [
        ("[ R ]  RESUME GAME",     YELLOW),
        ("[ S ]  SAVE & QUIT",     NEON_GREEN),
        ("[ N ]  NEW GAME",        ORANGE),
        ("[ Q ]  RETURN TO MENU",  RED),
    ]

    pygame.mixer.pause()
    tick = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_r, pygame.K_ESCAPE):
                    pygame.mixer.unpause()
                    return "resume"
                if ev.key == pygame.K_s:
                    save_game(get_profile(), wave, score, hp, diff_label)
                    pygame.mixer.unpause()
                    return "save_quit"
                if ev.key == pygame.K_n:
                    pygame.mixer.unpause()
                    return "restart"
                if ev.key == pygame.K_q:
                    pygame.mixer.unpause()
                    return "menu"

        surf.blit(overlay, (0, 0))
        tx = W // 2 - title.get_width() // 2
        surf.blit(shadow, (tx + 3, H // 2 - 100 + 3))
        surf.blit(title,  (tx,     H // 2 - 100))

        for i, (label, col) in enumerate(options):
            if i == 0 and tick % 60 < 30: col = WHITE
            t = font_med.render(label, True, col)
            surf.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 20 + i * 48))

        # Profile + save info
        prof = font_tiny.render(f"Profile: {get_profile()}   Wave: {wave}   Score: {score:07d}", True, GREY)
        surf.blit(prof, (W // 2 - prof.get_width() // 2, H - 50))
        sub = font_tiny.render("R/ESC: Resume   S: Save & Quit   N: New Game   Q: Menu", True, GREY)
        surf.blit(sub, (W // 2 - sub.get_width() // 2, H - 28))

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1


def difficulty_selection_screen():
    """Let the player choose difficulty. Returns a difficulty dict, or None (ESC = back)."""
    stars = draw_star_field(200)
    tick = 0
    selected_index = 1  # default to MEDIUM

    DIFFICULTIES = [
        {
            "label": "EASY",
            "target_waves": 5,
            "speed_mult": 0.85,
            "powerup_mult": 1.25,
            "desc": ["5 Waves", "Slower enemies", "More power-ups"],
            "color": NEON_GREEN,
            "key": pygame.K_1,
        },
        {
            "label": "MEDIUM",
            "target_waves": 10,
            "speed_mult": 1.0,
            "powerup_mult": 1.0,
            "desc": ["10 Waves", "Standard gameplay", ""],
            "color": YELLOW,
            "key": pygame.K_2,
        },
        {
            "label": "HARD",
            "target_waves": 15,
            "speed_mult": 1.2,
            "powerup_mult": 0.75,
            "desc": ["15 Waves", "Faster enemies", "Fewer power-ups"],
            "color": RED,
            "key": pygame.K_3,
        },
    ]

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                if ev.key in (pygame.K_LEFT, pygame.K_a):
                    selected_index = (selected_index - 1) % len(DIFFICULTIES)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    selected_index = (selected_index + 1) % len(DIFFICULTIES)
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return DIFFICULTIES[selected_index]
                else:
                    for i, d in enumerate(DIFFICULTIES):
                        if ev.key == d["key"]:
                            return d

        screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(screen, stars)

        hdr = font_med.render("SELECT  DIFFICULTY", True, CYAN)
        shd = font_med.render("SELECT  DIFFICULTY", True, PURPLE)
        tx = W // 2 - hdr.get_width() // 2
        screen.blit(shd, (tx + 2, 62))
        screen.blit(hdr, (tx, 60))
        pygame.draw.line(screen, GREY, (80, 100), (W - 80, 100), 1)

        card_w = 190
        card_h = 160
        gap = 20
        total_w = card_w * 3 + gap * 2
        start_x = W // 2 - total_w // 2

        for i, d in enumerate(DIFFICULTIES):
            cx = start_x + i * (card_w + gap)
            cy = H // 2 - card_h // 2 - 40
            rect = pygame.Rect(cx, cy, card_w, card_h)
            is_sel = (i == selected_index)
            bg_col = (15, 20, 50) if is_sel else (5, 5, 25)
            brd_col = d["color"] if is_sel else GREY
            pygame.draw.rect(screen, bg_col, rect, border_radius=8)
            pygame.draw.rect(screen, brd_col, rect, 2 if is_sel else 1, border_radius=8)

            # Draw label
            lbl = font_med.render(d["label"], True, d["color"])
            screen.blit(lbl, (cx + card_w // 2 - lbl.get_width() // 2, cy + 16))

            # Draw desc lines
            for j, line in enumerate(d["desc"]):
                t = font_tiny.render(line, True, WHITE)
                screen.blit(t, (cx + card_w // 2 - t.get_width() // 2, cy + 54 + j * 22))

        # Instructions
        inst = font_small.render("← / →  Navigate     ENTER  Confirm     ESC  Cancel", True, GREY)
        screen.blit(inst, (W // 2 - inst.get_width() // 2, H - 120))

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1


# ─── MAIN GAME LOOP ──────────────────────────────────────────────────────────

def run_game(difficulty=None, continue_data=None):
    if difficulty is None:
        difficulty = {"label": "MEDIUM", "target_waves": 10, "speed_mult": 1.0, "powerup_mult": 1.0}
    target_waves = difficulty["target_waves"]
    speed_mult   = difficulty["speed_mult"]
    powerup_mult = difficulty["powerup_mult"]
    diff_label   = difficulty["label"]

    player = Player()
    # Restore from save if continuing
    wave = 1
    if continue_data:
        wave = continue_data.get("wave", 1)
        player.score = continue_data.get("score", 0)
        player.hp    = continue_data.get("hp", 100)
        # Map saved difficulty label back to difficulty dict
        saved_label  = continue_data.get("difficulty", "MEDIUM")
        label_to_diff = {
            "EASY":   {"label": "EASY",   "target_waves": 5,  "speed_mult": 0.85, "powerup_mult": 1.25},
            "MEDIUM": {"label": "MEDIUM", "target_waves": 10, "speed_mult": 1.0,  "powerup_mult": 1.0},
            "HARD":   {"label": "HARD",   "target_waves": 15, "speed_mult": 1.2,  "powerup_mult": 0.75},
        }
        difficulty   = label_to_diff.get(saved_label, difficulty)
        target_waves = difficulty["target_waves"]
        speed_mult   = difficulty["speed_mult"]
        powerup_mult = difficulty["powerup_mult"]
        diff_label   = difficulty["label"]
    bullets = []
    enemies = []
    powerups = []
    particles = []
    stars = draw_star_field(200)

    # Note: wave was already initialized above (possibly loaded from continue_data)
    wave_total = 0
    kills_this_wave = 0
    required_kills = 0
    bomb_available = False
    wave_clear_timer = 0
    showing_wave = False
    score_flash = []  # [(text, x, y, life)]

    # background music
    music = generate_music()
    if music:
        music.play(loops=-1)

    wave_banner(wave)
    enemies = build_wave(wave, speed_mult)
    wave_total = len(enemies)
    required_kills = get_required_kills(wave, wave_total)
    kills_this_wave = 0

    def bomb_blast():
        nonlocal bomb_available
        if not bomb_available: return
        bomb_available = False
        play("explode")
        for e in enemies[:]:
            explosion(particles, int(e.x + e.w // 2), int(e.y + e.h // 2), RED, 25, 6)
            player.score += e.score_val
        enemies.clear()
        for _ in range(80):
            particles.append(Particle(
                random.randint(0, W), random.randint(0, H // 2),
                random.choice([ORANGE, YELLOW, RED]),
                (random.uniform(-6, 6), random.uniform(-4, 4)),
                random.randint(30, 60), random.randint(3, 8)
            ))

    running = True
    exit_reason = "quit"
    while running:
        dt = clock.tick(FPS)

        # ── Events ──
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_p):
                    action = pause_screen(screen, wave=wave, score=player.score,
                                         hp=player.hp, diff_label=diff_label)
                    if action in ("menu", "save_quit"):
                        running = False
                        exit_reason = "menu"
                    elif action == "restart":
                        running = False
                        exit_reason = "retry"
                if ev.key in (pygame.K_SPACE,):
                    bomb_blast()
                if ev.key in (pygame.K_z, pygame.K_LCTRL, pygame.K_RCTRL):
                    player.shoot(bullets)

        keys = pygame.key.get_pressed()
        player.move(keys)
        if keys[pygame.K_z] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            player.shoot(bullets)
        player.update()

        # Engine trail
        if pygame.time.get_ticks() % 60 < 30:
            cx = player.x + player.w // 2
            cy = player.y + player.h - 4
            particles.append(Particle(cx + random.randint(-4, 4), cy,
                                       random.choice([ORANGE, YELLOW, (255, 160, 0)]),
                                       (random.uniform(-0.5, 0.5), random.uniform(1, 3)),
                                       life=random.randint(10, 22), size=random.randint(2, 5)))

        # ── Bullets ──
        for b in bullets[:]:
            b.update()
            if b.y < -20 or b.y > H + 20 or b.x < -20 or b.x > W + 20:
                bullets.remove(b)

        # ── Enemies ──
        for e in enemies[:]:
            e.update(bullets, player.x + player.w // 2, player.y + player.h // 2)
            if e.y > H + 50:
                # Wrap back to top — must be killed to clear the wave
                e.y = -e.h - random.randint(10, 80)
                e.x = random.randint(0, W - e.w)
                e.entered = False
                e.entry_y = random.randint(40, 150)
                continue

            # Enemy bullets vs player
            for b in bullets[:]:
                if b.owner == "enemy" and b.rect().colliderect(player.rect()):
                    bullets.remove(b)
                    dmg = player.take_damage(e.dmg // 2)
                    if dmg:
                        explosion(particles, int(player.x + 18), int(player.y + 18), CYAN, 12, 3)

            # Player bullets vs enemy
            for b in bullets[:]:
                if b.owner == "player" and b.rect().colliderect(e.rect()):
                    if b in bullets:
                        bullets.remove(b)
                    e.hp -= 15
                    explosion(particles, int(b.x), int(b.y), ORANGE, 6, 3)
                    if e.hp <= 0:
                        play("explode")
                        explosion(particles, int(e.x + e.w // 2), int(e.y + e.h // 2),
                                  RED if e.etype == "boss" else ORANGE, 35 if e.etype == "boss" else 18, 6)
                        player.score += e.score_val
                        score_flash.append([f"+{e.score_val}", int(e.x + e.w // 2), int(e.y), 50])
                        # Drop power-up
                        if random.random() < 0.25 * powerup_mult or e.etype in ("tank", "boss"):
                            powerups.append(PowerUp(e.x + e.w // 2 - 11, e.y))
                        if e in enemies:
                            enemies.remove(e)
                        kills_this_wave += 1
                        break

            # Enemy body vs player
            if e.rect().colliderect(player.rect()):
                dmg = player.take_damage(e.dmg)
                if dmg:
                    explosion(particles, int(player.x + 18), int(player.y + 18), RED, 15, 4)

        # ── Power-ups ──
        for p in powerups[:]:
            p.update()
            if p.y > H + 30 or p.age > 300:
                powerups.remove(p); continue
            if p.rect().colliderect(player.rect()):
                play("powerup")
                if p.ptype == "health":
                    player.hp = min(player.max_hp, player.hp + 35)
                    score_flash.append(["+35 HP", int(p.x), int(p.y), 60])
                elif p.ptype == "rapid":
                    player.rapid_timer = 10 * FPS
                    score_flash.append(["RAPID FIRE!", int(p.x), int(p.y), 60])
                elif p.ptype == "shield":
                    player.shield_timer = 8 * FPS
                    score_flash.append(["SHIELD!", int(p.x), int(p.y), 60])
                elif p.ptype == "bomb":
                    bomb_available = True
                    score_flash.append(["BOMB READY!", int(p.x), int(p.y), 60])
                powerups.remove(p)

        # ── Particles ──
        for pt in particles[:]:
            pt.update()
            if pt.life <= 0:
                particles.remove(pt)

        # ── Score flashes ──
        for sf in score_flash[:]:
            sf[3] -= 1
            sf[2] -= 0.8
            if sf[3] <= 0:
                score_flash.remove(sf)

        # ── Wave progression ──
        if not enemies and not showing_wave:
            if kills_this_wave < required_kills:
                # Enemies escaped without enough kills — spawn reinforcements
                deficit = required_kills - kills_this_wave
                for _ in range(deficit):
                    x = random.randint(60, W - 60)
                    reinf = Enemy("basic", x, -60, wave)
                    reinf.entry_y = 100
                    reinf.speed *= speed_mult
                    enemies.append(reinf)
            else:
                wave_clear_timer += 1
                if wave_clear_timer >= FPS * 2:
                    if wave == target_waves:  # final boss cleared — mission complete
                        if music: music.stop()
                        result = mission_complete_screen(player.score)
                        return result
                    wave += 1
                    wave_clear_timer = 0
                    play("level_up")
                    wave_banner(wave)
                    enemies = build_wave(wave, speed_mult)
                    wave_total = len(enemies)
                    required_kills = get_required_kills(wave, wave_total)
                    kills_this_wave = 0
        else:
            wave_clear_timer = 0

        # ── Death ──
        if player.hp <= 0:
            play("gameover")
            if music: music.stop()
            # Death explosion
            for _ in range(5):
                explosion(particles, int(player.x + 18), int(player.y + 18), CYAN, 20, 5)
            # Show death particles briefly
            for _ in range(60):
                screen.fill(DARK_BLUE)
                scroll_stars(stars)
                draw_stars(screen, stars)
                for pt in particles:
                    pt.update()
                    pt.draw(screen)
                pygame.display.flip()
                clock.tick(FPS)
            result = game_over_screen(player.score, wave)
            return result

        # ─── DRAW ──────────────────────────────────────────────
        screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(screen, stars)

        for e in enemies:     e.draw(screen)
        for p in powerups:    p.draw(screen)
        for b in bullets:     b.draw(screen)
        for pt in particles:  pt.draw(screen)
        player.draw(screen)

        # Score flashes
        for sf in score_flash:
            alpha = min(255, sf[3] * 6)
            col = YELLOW if sf[0].startswith("+") else GREEN
            if "HP" in sf[0]: col = GREEN
            if "SHIELD" in sf[0]: col = CYAN
            if "BOMB" in sf[0]: col = ORANGE
            t = font_small.render(sf[0], True, col)
            tmp = pygame.Surface(t.get_size(), pygame.SRCALPHA)
            tmp.blit(t, (0, 0))
            tmp.set_alpha(alpha)
            screen.blit(tmp, (sf[1] - t.get_width() // 2, int(sf[2])))

        draw_hud(screen, player, wave, len(enemies), bomb_available, wave_total, kills_this_wave, required_kills, diff_label)
        pygame.display.flip()

    if music:
        music.stop()
    return exit_reason


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def main():
    title_screen()
    # First run: show tutorial then story crawl
    tutorial_stage()
    story_crawl()
    first_run = True
    while True:
        result = run_game()
        if result == "quit":
            break
        # On retry, skip tutorial and story crawl — go straight back into the game

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
