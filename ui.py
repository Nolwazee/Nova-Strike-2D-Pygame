import pygame
import sys
import math
import random

from entities import (
    W, H, FPS,
    WHITE, CYAN, YELLOW, RED, GREEN, ORANGE, PURPLE,
    DARK_BLUE, NEON_GREEN, GREY,
    draw_player_ship,
)

# ─── MODULE GLOBALS — set once by init() before any screen function is called ─
_screen    = None
_clock     = None
_font_big  = None
_font_med  = None
_font_small = None
_font_tiny  = None


def init(screen, clock, font_big, font_med, font_small, font_tiny):
    global _screen, _clock, _font_big, _font_med, _font_small, _font_tiny
    _screen    = screen
    _clock     = clock
    _font_big  = font_big
    _font_med  = font_med
    _font_small = font_small
    _font_tiny  = font_tiny


# ─── STAR FIELD ──────────────────────────────────────────────────────────────

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


def scroll_stars(stars):
    for s in stars:
        s[1] += s[2]
        if s[1] > H:
            s[1] = 0
            s[0] = random.randint(0, W)


def draw_stars(surf, stars):
    for s in stars:
        c = int(s[3])
        col = (c, c, min(255, c + 60))
        if s[4] == 1:
            surf.set_at((int(s[0]), int(s[1])), col)
        else:
            pygame.draw.circle(surf, col, (int(s[0]), int(s[1])), s[4])


# ─── HUD ─────────────────────────────────────────────────────────────────────

def draw_hud(surf, player, wave, enemies_left, bomb_available,
             wave_total=0, kills_this_wave=0, required_kills=0, diff_label=""):
    bar_w = 200
    ratio = player.hp / player.max_hp
    bar_color = GREEN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
    pygame.draw.rect(surf, (40, 40, 60), (10, 10, bar_w, 18), border_radius=4)
    pygame.draw.rect(surf, bar_color, (10, 10, int(bar_w * ratio), 18), border_radius=4)
    pygame.draw.rect(surf, WHITE, (10, 10, bar_w, 18), 1, border_radius=4)
    hp_txt = _font_tiny.render(f"HP {player.hp}/{player.max_hp}", True, WHITE)
    surf.blit(hp_txt, (14, 13))

    score_txt = _font_med.render(f"SCORE  {player.score:07d}", True, CYAN)
    surf.blit(score_txt, (W // 2 - score_txt.get_width() // 2, 8))

    is_boss_wave = (wave % 5 == 0)
    wave_label = f"BOSS  WAVE  {wave}" if is_boss_wave else f"WAVE  {wave}"
    wave_txt = _font_small.render(wave_label, True, RED if is_boss_wave else YELLOW)
    surf.blit(wave_txt, (W - wave_txt.get_width() - 10, 8))

    if is_boss_wave:
        boss_txt = _font_tiny.render("DEFEAT  THE  BOSS", True, RED)
        surf.blit(boss_txt, (W - boss_txt.get_width() - 10, 28))
    else:
        kills_color = NEON_GREEN if kills_this_wave >= required_kills else GREY
        kills_txt = _font_tiny.render(f"KILLS: {kills_this_wave}/{required_kills}", True, kills_color)
        surf.blit(kills_txt, (W - kills_txt.get_width() - 10, 28))
        en_label = f"LEFT: {enemies_left}/{wave_total}" if wave_total else f"LEFT: {enemies_left}"
        en_txt = _font_tiny.render(en_label, True, GREY)
        surf.blit(en_txt, (W - en_txt.get_width() - 10, 44))

    y = 36
    if player.rapid_timer > 0:
        t = _font_tiny.render(f"RAPID x2  {player.rapid_timer // FPS + 1}s", True, YELLOW)
        surf.blit(t, (10, y)); y += 16
    if player.shield_timer > 0:
        t = _font_tiny.render(f"SHIELD  {player.shield_timer // FPS + 1}s", True, CYAN)
        surf.blit(t, (10, y)); y += 16

    bomb_col = ORANGE if bomb_available else GREY
    bomb_txt = _font_tiny.render("[ SPACE ] BOMB" if bomb_available else "NO BOMB", True, bomb_col)
    surf.blit(bomb_txt, (10, H - 22))

    if diff_label:
        diff_colors = {"EASY": NEON_GREEN, "MEDIUM": YELLOW, "HARD": RED}
        dc = diff_colors.get(diff_label, GREY)
        dt = _font_tiny.render(diff_label, True, dc)
        surf.blit(dt, (W - dt.get_width() - 10, H - 22))


# ─── SCREENS ─────────────────────────────────────────────────────────────────

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
            
            _screen.fill(DARK_BLUE)
            scroll_stars(stars)
            draw_stars(_screen, stars)
            p = _font_small.render(prompt, True, CYAN)
            _screen.blit(p, (W//2 - p.get_width()//2, H//2 - 60))
            # Input box
            box = pygame.Rect(W//2 - 160, H//2 - 20, 320, 44)
            pygame.draw.rect(_screen, (20, 20, 50), box, border_radius=6)
            pygame.draw.rect(_screen, CYAN, box, 2, border_radius=6)
            cursor = "|" if tick % 60 < 30 else ""
            txt = _font_med.render(text + cursor, True, WHITE)
            _screen.blit(txt, (box.x + 12, box.y + 8))
            hint = _font_tiny.render("ENTER to confirm   ESC to cancel", True, GREY)
            _screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 40))
            pygame.display.flip()
            _clock.tick(FPS)
            tick += 1
    finally:
        pygame.key.stop_text_input()


def profile_screen(saves, get_profile_fn, set_profile_fn):
    """Profile selection / creation screen. Returns chosen profile name."""
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
                        set_profile_fn(name)
                    else:
                        set_profile_fn(saves[selected - 1][0])
                    return get_profile_fn()
                elif ev.key == pygame.K_ESCAPE:
                    return get_profile_fn()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i in range(len(options)):
                    y = 110 + i * 44
                    rect = pygame.Rect(40, y - 4, W - 80, 36)
                    if rect.collidepoint(ev.pos):
                        if i == 0:
                            name = text_input_box("Enter your pilot name:", default="")
                            set_profile_fn(name)
                        else:
                            set_profile_fn(saves[i - 1][0])
                        return get_profile_fn()

        # Update hovered selection using mouse position
        for i in range(len(options)):
            y = 110 + i * 44
            rect = pygame.Rect(40, y - 4, W - 80, 36)
            if rect.collidepoint(mouse_pos):
                selected = i

        _screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(_screen, stars)

        hdr = _font_med.render("SELECT  PROFILE", True, CYAN)
        _screen.blit(hdr, (W//2 - hdr.get_width()//2, 50))
        pygame.draw.line(_screen, CYAN, (60, 88), (W-60, 88), 1)

        for i, opt in enumerate(options):
            y = 110 + i * 44
            is_sel = (i == selected)
            col = YELLOW if is_sel else GREY
            if i == 0: col = NEON_GREEN if is_sel else GREEN
            if is_sel:
                pygame.draw.rect(_screen, (20, 20, 50), (40, y - 4, W - 80, 36), border_radius=4)
                pygame.draw.rect(_screen, col, (40, y - 4, W - 80, 36), 1, border_radius=4)
            t = _font_small.render(opt, True, col)
            _screen.blit(t, (60, y))

        hint = _font_tiny.render("↑ / ↓  Navigate   ENTER / CLICK  Select   ESC  Back", True, GREY)
        _screen.blit(hint, (W//2 - hint.get_width()//2, H - 28))
        pygame.display.flip()
        _clock.tick(FPS)
        tick += 1


def multiplayer_menu():
    """Multiplayer host / join menu. Returns ('host' | 'join' | 'back')."""
    stars = draw_star_field(180)
    selected = 0
    menu_items = [
        ("HOST CO-OP (Authority)", CYAN, "host"),
        ("JOIN CO-OP (Connect to IP)", NEON_GREEN, "join"),
        ("BACK TO MENU", RED, "back")
    ]
    tick = 0
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(menu_items)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(menu_items)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    return menu_items[selected][2]
                elif ev.key == pygame.K_ESCAPE:
                    return "back"
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, (label, col, action) in enumerate(menu_items):
                    rect = pygame.Rect(W // 2 - 220, H // 2 - 40 + i * 50 - 4, 440, 36)
                    if rect.collidepoint(ev.pos):
                        return action

        for i, (label, col, action) in enumerate(menu_items):
            rect = pygame.Rect(W // 2 - 220, H // 2 - 40 + i * 50 - 4, 440, 36)
            if rect.collidepoint(mouse_pos):
                selected = i

        _screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(_screen, stars)

        hdr = _font_med.render("CO-OP  MULTIPLAYER", True, CYAN)
        shd = _font_med.render("CO-OP  MULTIPLAYER", True, PURPLE)
        tx = W // 2 - hdr.get_width() // 2
        _screen.blit(shd, (tx + 2, H // 2 - 130 + 2))
        _screen.blit(hdr, (tx, H // 2 - 130))
        pygame.draw.line(_screen, GREY, (80, H // 2 - 95), (W - 80, H // 2 - 95), 1)

        for i, (label, col, action) in enumerate(menu_items):
            is_sel = (i == selected)
            prefix = "▶ " if is_sel else "  "
            text_color = WHITE if is_sel and (tick % 30 < 15) else (WHITE if is_sel else col)
            lbl = _font_med.render(f"{prefix}{label}", True, text_color)
            _screen.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 - 40 + i * 50))

        hint = _font_tiny.render("↑ / ↓  Navigate     ENTER / CLICK  Select     ESC  Back", True, GREY)
        _screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 35))

        pygame.display.flip()
        _clock.tick(FPS)
        tick += 1


def title_screen(get_profile_fn, has_save=False, save_data=None, profile_screen_callback=None):
    """Main menu. Returns one of: 'new', 'continue', 'multiplayer', 'quit'."""
    stars = draw_star_field(200)
    ship_y = H + 50
    target_y = H // 2 + 100
    ship_sprite = draw_player_ship(size=60)
    tick = 0
    selected = 0

    while True:
        menu_items = []
        if has_save and save_data:
            menu_items.append(("CONTINUE",     GREEN,       "continue"))
        menu_items.append(    ("NEW GAME",     YELLOW,      "new"))
        menu_items.append(    ("PROFILE",      PURPLE,      "profile"))
        menu_items.append(    ("MULTIPLAYER",  CYAN,        "multiplayer"))
        menu_items.append(    ("QUIT",         RED,         "quit"))

        if selected >= len(menu_items):
            selected = len(menu_items) - 1

        mouse_pos = pygame.mouse.get_pos()
        start_y = H // 2 - 40

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(menu_items)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(menu_items)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    action = menu_items[selected][2]
                    if action == "profile" and profile_screen_callback:
                        profile_screen_callback()
                    else:
                        return action
                elif ev.key == pygame.K_c and has_save:
                    return "continue"
                elif ev.key == pygame.K_n:
                    return "new"
                elif ev.key == pygame.K_m:
                    return "multiplayer"
                elif ev.key == pygame.K_p and profile_screen_callback:
                    profile_screen_callback()
                elif ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "quit"
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, (label, col, action) in enumerate(menu_items):
                    rect = pygame.Rect(W // 2 - 180, start_y + i * 44 - 4, 360, 36)
                    if rect.collidepoint(ev.pos):
                        if action == "profile" and profile_screen_callback:
                            profile_screen_callback()
                        else:
                            return action

        # Update hovered selection using mouse position
        for i, (label, col, action) in enumerate(menu_items):
            rect = pygame.Rect(W // 2 - 180, start_y + i * 44 - 4, 360, 36)
            if rect.collidepoint(mouse_pos):
                selected = i

        _screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(_screen, stars)

        if ship_y > target_y:
            ship_y -= 4

        # Title text
        title = _font_big.render("NOVA  STRIKE", True, CYAN)
        shadow = _font_big.render("NOVA  STRIKE", True, PURPLE)
        tx = W // 2 - title.get_width() // 2
        _screen.blit(shadow, (tx + 3, 83))
        _screen.blit(title, (tx, 80))

        sub = _font_small.render("Earth's last fighter. The stars await.", True, GREY)
        _screen.blit(sub, (W // 2 - sub.get_width() // 2, 148))

        prof_lbl = _font_small.render(f"Pilot Profile: {get_profile_fn()}", True, YELLOW)
        _screen.blit(prof_lbl, (W // 2 - prof_lbl.get_width() // 2, 180))

        _screen.blit(ship_sprite, (W // 2 - 30, int(ship_y)))

        # Draw interactive menu items
        for i, (label, col, action) in enumerate(menu_items):
            is_sel = (i == selected)
            prefix = "▶ " if is_sel else "  "
            text_color = WHITE if is_sel and (tick % 30 < 15) else (WHITE if is_sel else col)
            if action == "continue" and has_save and save_data:
                lbl = _font_med.render(f"{prefix}{label} (Wave {save_data['wave']})", True, text_color)
            else:
                lbl = _font_med.render(f"{prefix}{label}", True, text_color)
            _screen.blit(lbl, (W // 2 - lbl.get_width() // 2, start_y + i * 44))

        controls = [
            "WASD / ARROW KEYS : MOVE     Z / CTRL : SHOOT",
            "SPACE : BOMB (collect first!)     ESC / P : PAUSE",
        ]
        for i, line in enumerate(controls):
            t = _font_tiny.render(line, True, GREY)
            _screen.blit(t, (W // 2 - t.get_width() // 2, H - 54 + i * 17))

        pygame.display.flip()
        _clock.tick(FPS)
        tick += 1


def story_screen():
    """Returns 'start' or 'back'."""
    stars = draw_star_field(200)
    lines = [
        ("YEAR 2157  —  EARTH IS UNDER SIEGE.", RED),
        ("", WHITE),
        ("The Void Armada, an alien fleet of", WHITE),
        ("unimaginable scale, tore through every", WHITE),
        ("planetary defense in hours.", WHITE),
        ("", WHITE),
        ("Cities are burning. Governments have", WHITE),
        ("fallen. Humanity's military is gone.", WHITE),
        ("", WHITE),
        ("You are the last pilot standing.", YELLOW),
        ("One ship.  One chance.", YELLOW),
        ("", WHITE),
        ("Survive.  Defend Earth.  Destroy them.", CYAN),
    ]
    tick = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "start"
                if ev.key == pygame.K_ESCAPE:
                    return "back"

        _screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(_screen, stars)

        hdr = _font_med.render("MISSION  BRIEFING", True, CYAN)
        shd = _font_med.render("MISSION  BRIEFING", True, PURPLE)
        tx = W // 2 - hdr.get_width() // 2
        _screen.blit(shd, (tx + 2, 42))
        _screen.blit(hdr, (tx, 40))
        pygame.draw.line(_screen, GREY, (80, 78), (W - 80, 78), 1)

        for i, (text, col) in enumerate(lines):
            t = _font_small.render(text, True, col)
            _screen.blit(t, (W // 2 - t.get_width() // 2, 100 + i * 34))

        if tick % 60 < 30:
            go = _font_med.render("PRESS  ENTER  TO  LAUNCH", True, NEON_GREEN)
            _screen.blit(go, (W // 2 - go.get_width() // 2, H - 70))

        back_hint = _font_tiny.render("ESC : Back to Menu", True, GREY)
        _screen.blit(back_hint, (W // 2 - back_hint.get_width() // 2, H - 28))

        pygame.display.flip()
        _clock.tick(FPS)
        tick += 1


def difficulty_selection_screen():
    """Returns a difficulty dict, or None (ESC = back to title)."""
    stars = draw_star_field(200)
    tick = 0
    selected_index = 1  # default MEDIUM

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
                    for d in DIFFICULTIES:
                        if ev.key == d["key"]:
                            return d

        _screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(_screen, stars)

        hdr = _font_med.render("SELECT  DIFFICULTY", True, CYAN)
        shd = _font_med.render("SELECT  DIFFICULTY", True, PURPLE)
        tx = W // 2 - hdr.get_width() // 2
        _screen.blit(shd, (tx + 2, 62))
        _screen.blit(hdr, (tx, 60))
        pygame.draw.line(_screen, GREY, (80, 100), (W - 80, 100), 1)

        card_w = 190
        card_h = 160
        gap = 20
        total_w = card_w * 3 + gap * 2
        start_x = W // 2 - total_w // 2

        for i, d in enumerate(DIFFICULTIES):
            cx = start_x + i * (card_w + gap)
            cy = 140
            is_selected = (i == selected_index)

            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            pygame.draw.rect(_screen, (15, 15, 40), card_rect, border_radius=8)
            if is_selected:
                pygame.draw.rect(_screen, d["color"], card_rect, 4, border_radius=8)
                glow_rect = pygame.Rect(cx - 3, cy - 3, card_w + 6, card_h + 6)
                pygame.draw.rect(_screen, d["color"], glow_rect, 1, border_radius=10)
            else:
                pygame.draw.rect(_screen, d["color"], card_rect, 2, border_radius=8)

            key_hint = _font_tiny.render(f"[ {i + 1} ]", True, d["color"])
            _screen.blit(key_hint, (cx + card_w // 2 - key_hint.get_width() // 2, cy + 10))

            label_col = (255, 255, 255) if is_selected else d["color"]
            label_txt = _font_med.render(d["label"], True, label_col)
            _screen.blit(label_txt, (cx + card_w // 2 - label_txt.get_width() // 2, cy + 30))

            pygame.draw.line(_screen, d["color"], (cx + 16, cy + 62), (cx + card_w - 16, cy + 62), 1)

            for j, line in enumerate(d["desc"]):
                if line:
                    lt = _font_tiny.render(line, True, (255, 255, 255))
                    _screen.blit(lt, (cx + card_w // 2 - lt.get_width() // 2, cy + 74 + j * 22))

            if is_selected:
                sel_txt = _font_tiny.render("SELECTED", True, d["color"])
                _screen.blit(sel_txt, (cx + card_w // 2 - sel_txt.get_width() // 2, cy + card_h + 8))

        hint_line = _font_tiny.render(
            "← / →  or  A / D : Choose      ENTER : Confirm      ESC : Back",
            True, GREY
        )
        _screen.blit(hint_line, (W // 2 - hint_line.get_width() // 2, H - 28))

        pygame.display.flip()
        _clock.tick(FPS)
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

        _screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(_screen, stars)

        over = _font_big.render("GAME  OVER", True, RED)
        _screen.blit(over, (W // 2 - over.get_width() // 2, 140))

        sc = _font_med.render(f"SCORE: {score:07d}", True, YELLOW)
        _screen.blit(sc, (W // 2 - sc.get_width() // 2, 220))

        wv = _font_med.render(f"REACHED WAVE {wave}", True, CYAN)
        _screen.blit(wv, (W // 2 - wv.get_width() // 2, 262))

        if tick % 80 < 55:
            r = _font_med.render("[ R ] RETRY     [ ESC ] QUIT", True, (255, 255, 255))
            _screen.blit(r, (W // 2 - r.get_width() // 2, H - 100))

        pygame.display.flip()
        _clock.tick(FPS)
        tick += 1


def mission_complete_screen(score):
    """Returns 'retry' or 'menu'."""
    stars = draw_star_field(200)
    tick = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:                     return "retry"
                if ev.key in (pygame.K_ESCAPE, pygame.K_q): return "menu"

        _screen.fill(DARK_BLUE)
        scroll_stars(stars)
        draw_stars(_screen, stars)

        hdr = _font_big.render("MISSION  COMPLETE!", True, NEON_GREEN)
        shd = _font_big.render("MISSION  COMPLETE!", True, (0, 80, 40))
        tx  = W // 2 - hdr.get_width() // 2
        _screen.blit(shd, (tx + 3, 143))
        _screen.blit(hdr, (tx, 140))
        pygame.draw.line(_screen, NEON_GREEN, (80, 198), (W - 80, 198), 1)

        lines = [
            ("The Void Armada flagship has been destroyed.", (255, 255, 255)),
            ("Earth is saved. Humanity lives on.", YELLOW),
            ("", (255, 255, 255)),
            (f"FINAL  SCORE :  {score:07d}", CYAN),
        ]
        for i, (text, col) in enumerate(lines):
            t = _font_small.render(text, True, col)
            _screen.blit(t, (W // 2 - t.get_width() // 2, 226 + i * 36))

        if tick % 60 < 30:
            opts = _font_med.render("[ R ] PLAY AGAIN     [ ESC ] MENU", True, YELLOW)
            _screen.blit(opts, (W // 2 - opts.get_width() // 2, H - 100))

        hint = _font_tiny.render("R : Retry   ESC / Q : Return to Menu", True, GREY)
        _screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 28))

        pygame.display.flip()
        _clock.tick(FPS)
        tick += 1


def wave_banner(wave_num):
    """Brief full-screen wave announcement."""
    is_boss = (wave_num % 5 == 0)
    msg = f"⚠  BOSS  WAVE  {wave_num}  ⚠" if is_boss else f"WAVE  {wave_num}"
    color = RED if is_boss else CYAN
    for frame in range(80):
        _screen.fill(DARK_BLUE)
        alpha = 255 if frame < 50 else max(0, 255 - (frame - 50) * 12)
        txt = _font_big.render(msg, True, color)
        tmp = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        tmp.blit(txt, (0, 0))
        tmp.set_alpha(alpha)
        _screen.blit(tmp, (W // 2 - txt.get_width() // 2, H // 2 - 30))
        pygame.display.flip()
        _clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()


def pause_screen(surf, sound_on=True, wave=1, score=0, hp=100, diff_label="MEDIUM"):
    """Semi-transparent pause overlay. Returns ('resume'|'restart'|'menu'|'save_quit', sound_on)."""
    overlay = surf.copy()
    darken = pygame.Surface((W, H), pygame.SRCALPHA)
    darken.fill((10, 10, 30, 180))
    overlay.blit(darken, (0, 0))

    title  = _font_big.render("GAME  PAUSED", True, CYAN)
    shadow = _font_big.render("GAME  PAUSED", True, PURPLE)

    pygame.mixer.pause()
    tick = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_m:
                    sound_on = not sound_on
                elif ev.key in (pygame.K_r, pygame.K_ESCAPE):
                    if sound_on:
                        pygame.mixer.unpause()
                    else:
                        pygame.mixer.stop()
                    return "resume", sound_on
                elif ev.key == pygame.K_n:
                    if sound_on:
                        pygame.mixer.unpause()
                    else:
                        pygame.mixer.stop()
                    return "restart", sound_on
                elif ev.key == pygame.K_s:
                    pygame.mixer.stop()
                    return "save_quit", sound_on
                elif ev.key == pygame.K_q:
                    pygame.mixer.stop()
                    return "menu", sound_on

        sound_label = "[ M ]  SOUND: ON " if sound_on else "[ M ]  SOUND: OFF"
        sound_col   = NEON_GREEN if sound_on else GREY
        options = [
            ("[ R ]  RESUME GAME",    YELLOW),
            ("[ N ]  NEW GAME",       NEON_GREEN),
            ("[ S ]  SAVE & QUIT",     CYAN),
            (sound_label,             sound_col),
            ("[ Q ]  RETURN TO MENU", RED),
        ]

        surf.blit(overlay, (0, 0))

        tx = W // 2 - title.get_width() // 2
        surf.blit(shadow, (tx + 3, H // 2 - 120 + 3))
        surf.blit(title,  (tx,     H // 2 - 120))

        # Render stats box
        stats = _font_tiny.render(f"Wave: {wave}  |  Score: {score}  |  HP: {hp}  |  Difficulty: {diff_label}", True, WHITE)
        surf.blit(stats, (W // 2 - stats.get_width() // 2, H // 2 - 60))

        for i, (label, col) in enumerate(options):
            if i == 0 and tick % 60 < 30:
                col = (255, 255, 255)
            t = _font_med.render(label, True, col)
            surf.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 30 + i * 44))

        sub = _font_tiny.render("R/ESC : Resume   N : New   S : Save   M : Sound   Q : Menu", True, GREY)
        surf.blit(sub, (W // 2 - sub.get_width() // 2, H - 40))

        pygame.display.flip()
        _clock.tick(FPS)
        tick += 1
