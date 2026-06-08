"""
NOVA STRIKE
A 2D top-down space shooter built with Pygame.
"""

import pygame
import math
import random
import sys

# ─── INIT ────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ─── IMPORTS (after pygame.init so entity surfaces can be created) ────────────
from entities import (
    W, H, FPS, TITLE,
    CYAN, YELLOW, RED, GREEN, ORANGE,
    DARK_BLUE, NEON_GREEN,
    Player, Bullet, Enemy, PowerUp, Particle,
    explosion,
)
import ui
from ui import (
    draw_hud, draw_star_field, scroll_stars, draw_stars,
    title_screen, story_screen, difficulty_selection_screen,
    pause_screen, game_over_screen, mission_complete_screen, wave_banner,
)

# ─── DISPLAY ─────────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# ─── FONTS ───────────────────────────────────────────────────────────────────
font_big   = pygame.font.SysFont("consolas", 48, bold=True)
font_med   = pygame.font.SysFont("consolas", 28, bold=True)
font_small = pygame.font.SysFont("consolas", 18)
font_tiny  = pygame.font.SysFont("consolas", 14)

# ─── SOUND GENERATOR ─────────────────────────────────────────────────────────

def make_sound(freq, duration_ms, wave="sine", volume=0.4, envelope=True):
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
    elif wave == "zap":
        f = np.linspace(freq, freq * 0.05, n)
        phase = np.cumsum(2 * np.pi * f / sample_rate)
        data = np.sign(np.sin(phase))
    elif wave == "noise_burst":
        data = np.random.uniform(-1, 1, n)
        data *= np.exp(-np.linspace(0, 6, n))
        envelope = False
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
    return pygame.sndarray.make_sound(stereo)


def make_arpeggio(freqs, dur_ms, wave="sine", volume=0.4):
    import numpy as np
    sample_rate = 44100
    chunks = []
    for freq in freqs:
        n = int(sample_rate * dur_ms / 1000)
        t = np.linspace(0, dur_ms / 1000, n, endpoint=False)
        if wave == "sine":
            d = np.sin(2 * np.pi * freq * t)
        elif wave == "square":
            d = np.sign(np.sin(2 * np.pi * freq * t))
        else:
            d = np.sin(2 * np.pi * freq * t)
        env = np.ones(n)
        env[:int(n * 0.08)] = np.linspace(0, 1, int(n * 0.08))
        release_start = int(n * 0.6)
        env[release_start:] = np.linspace(1, 0, n - release_start)
        d *= env
        chunks.append(d)
    combined = np.concatenate(chunks)
    combined = (combined * volume * 32767).astype(np.int16)
    stereo = np.column_stack([combined, combined])
    return pygame.sndarray.make_sound(stereo)


try:
    import numpy as np
    SFX = {
        "shoot":    make_sound(1400, 55,  "zap",         0.28),
        "explode":  make_sound(80,   350, "noise_burst",  0.55),
        "powerup":  make_arpeggio([330, 440, 550, 880], 65, "square", 0.28),
        "hit":      make_sound(200,  75,  "noise_burst",  0.38),
        "gameover": make_sound(200,  700, "sweep",        0.42),
        "level_up": make_arpeggio([523, 659, 784, 1047], 75, "sine", 0.38),
        "shield":   make_sound(1100, 120, "sweep",        0.22),
    }
    MUSIC_ENABLED = True
except ImportError:
    SFX = {}
    MUSIC_ENABLED = False


SOUND_ON = True


def play(name):
    if SOUND_ON and name in SFX:
        SFX[name].play()


def generate_music():
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
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


# ─── WIRE UP UI MODULE ───────────────────────────────────────────────────────
ui.init(screen, clock, font_big, font_med, font_small, font_tiny)


# ─── WAVE DEFINITIONS ────────────────────────────────────────────────────────

def build_wave(wave_num, speed_mult=1.0):
    enemies = []
    if wave_num % 5 == 0:
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


def get_required_kills(wave, wave_total):
    if wave % 5 == 0:
        return 1
    return max(1, math.ceil(wave_total * 0.7))


# ─── MAIN GAME LOOP ──────────────────────────────────────────────────────────

def run_game(difficulty=None):
    global SOUND_ON
    if difficulty is None:
        difficulty = {"label": "MEDIUM", "target_waves": 10, "speed_mult": 1.0, "powerup_mult": 1.0}
    target_waves = difficulty["target_waves"]
    speed_mult   = difficulty["speed_mult"]
    powerup_mult = difficulty["powerup_mult"]
    diff_label   = difficulty["label"]

    player   = Player()
    bullets  = []
    enemies  = []
    powerups = []
    particles = []
    stars    = draw_star_field(200)

    wave = 1
    wave_total = 0
    kills_this_wave = 0
    required_kills = 0
    bomb_available = False
    wave_clear_timer = 0
    showing_wave = False
    score_flash = []  # [(text, x, y, life)]

    music = generate_music()
    if music and SOUND_ON:
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
        clock.tick(FPS)

        # ── Events ──
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_p):
                    prev_sound = SOUND_ON
                    action, SOUND_ON = pause_screen(screen, SOUND_ON)
                    if SOUND_ON and not prev_sound and music:
                        music.play(loops=-1)
                    if action == "menu":
                        running = False; exit_reason = "menu"
                    elif action == "restart":
                        running = False; exit_reason = "retry"
                if ev.key == pygame.K_SPACE:
                    bomb_blast()
                if ev.key in (pygame.K_z, pygame.K_LCTRL, pygame.K_RCTRL):
                    if player.shoot(bullets):
                        play("shoot")

        keys = pygame.key.get_pressed()
        player.move(keys)
        if keys[pygame.K_z] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            if player.shoot(bullets):
                play("shoot")
        player.update()

        # Engine trail
        if pygame.time.get_ticks() % 60 < 30:
            cx = player.x + player.w // 2
            cy = player.y + player.h - 4
            particles.append(Particle(
                cx + random.randint(-4, 4), cy,
                random.choice([ORANGE, YELLOW, (255, 160, 0)]),
                (random.uniform(-0.5, 0.5), random.uniform(1, 3)),
                life=random.randint(10, 22), size=random.randint(2, 5)
            ))

        # ── Bullets ──
        for b in bullets[:]:
            b.update()
            if b.y < -20 or b.y > H + 20 or b.x < -20 or b.x > W + 20:
                bullets.remove(b)

        # ── Enemies ──
        for e in enemies[:]:
            e.update(bullets, player.x + player.w // 2, player.y + player.h // 2)
            if e.y > H + 50:
                enemies.remove(e)
                continue

            # Enemy bullets vs player
            for b in bullets[:]:
                if b.owner == "enemy" and b.rect().colliderect(player.rect()):
                    bullets.remove(b)
                    result = player.take_damage(e.dmg // 2)
                    if result == "hit":
                        play("hit")
                        explosion(particles, int(player.x + 18), int(player.y + 18), CYAN, 12, 3)
                    elif result == "shield":
                        play("shield")

            # Player bullets vs enemy
            for b in bullets[:]:
                if b.owner == "player" and b.rect().colliderect(e.rect()):
                    if b in bullets:
                        bullets.remove(b)
                    e.hp -= 15
                    explosion(particles, int(b.x), int(b.y), ORANGE, 6, 3)
                    if e.hp <= 0:
                        play("explode")
                        explosion(particles,
                                  int(e.x + e.w // 2), int(e.y + e.h // 2),
                                  RED if e.etype == "boss" else ORANGE,
                                  35 if e.etype == "boss" else 18, 6)
                        player.score += e.score_val
                        score_flash.append([f"+{e.score_val}", int(e.x + e.w // 2), int(e.y), 50])
                        if random.random() < (0.25 * powerup_mult) or e.etype in ("tank", "boss"):
                            powerups.append(PowerUp(e.x + e.w // 2 - 11, e.y))
                        if e in enemies:
                            enemies.remove(e)
                        kills_this_wave += 1
                        break

            # Enemy body vs player
            if e.rect().colliderect(player.rect()):
                result = player.take_damage(e.dmg)
                if result == "hit":
                    play("hit")
                    explosion(particles, int(player.x + 18), int(player.y + 18), RED, 15, 4)
                elif result == "shield":
                    play("shield")

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
                    if wave == target_waves:
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
            for _ in range(5):
                explosion(particles, int(player.x + 18), int(player.y + 18), CYAN, 20, 5)
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

        for e in enemies:    e.draw(screen)
        for p in powerups:   p.draw(screen)
        for b in bullets:    b.draw(screen)
        for pt in particles: pt.draw(screen)
        player.draw(screen)

        for sf in score_flash:
            alpha = min(255, sf[3] * 6)
            col = YELLOW if sf[0].startswith("+") else GREEN
            if "HP"     in sf[0]: col = GREEN
            if "SHIELD" in sf[0]: col = CYAN
            if "BOMB"   in sf[0]: col = ORANGE
            t = font_small.render(sf[0], True, col)
            tmp = pygame.Surface(t.get_size(), pygame.SRCALPHA)
            tmp.blit(t, (0, 0))
            tmp.set_alpha(alpha)
            screen.blit(tmp, (sf[1] - t.get_width() // 2, int(sf[2])))

        draw_hud(screen, player, wave, len(enemies), bomb_available,
                 wave_total, kills_this_wave, required_kills, diff_label)

        if not enemies and 0 < wave_clear_timer < FPS * 2:
            msg   = "BOSS  ELIMINATED!" if wave % 5 == 0 else "WAVE  CLEARED!"
            color = RED if wave % 5 == 0 else NEON_GREEN
            shd_color = (80, 0, 0) if wave % 5 == 0 else (0, 80, 60)
            wc  = font_big.render(msg, True, color)
            shd = font_big.render(msg, True, shd_color)
            wx  = W // 2 - wc.get_width() // 2
            screen.blit(shd, (wx + 2, H // 2 - 24 + 2))
            screen.blit(wc,  (wx,     H // 2 - 24))

        pygame.display.flip()

    if music:
        music.stop()
    return exit_reason


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def main():
    while True:
        title_screen()
        if story_screen() == "back":
            continue
        difficulty = difficulty_selection_screen()
        if difficulty is None:
            continue
        result = "retry"
        while result == "retry":
            result = run_game(difficulty)
        if result == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
