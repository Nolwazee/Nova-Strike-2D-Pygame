# NOVA STRIKE 🚀
### A 2D Top-Down Space Shooter built with Pygame

---

## STORYLINE
Earth's final fighter pilot stands against an unstoppable alien invasion fleet.
Wave after wave of enemy ships descend. You must survive — or humanity falls.

---

## SETUP & RUNNING

### Requirements
- Python 3.8+
- Pygame 2.x
- NumPy (for procedural audio — optional but recommended)

### Install dependencies
```bash
pip install pygame numpy
```

### Run the game
```bash
python game.py
```

---

## CONTROLS

| Key               | Action         |
|-------------------|----------------|
| WASD / Arrow Keys | Move ship      |
| Z / Left Ctrl     | Shoot          |
| SPACE             | Drop BOMB      |
| ESC               | Quit / Menu    |
| R (Game Over)     | Retry          |

---

## GAME FEATURES

### Genre
Arcade Space Shooter (2D, top-down)

### Gameplay Mechanics (✅ meets requirements)

1. **Enemy AI** — Four enemy types with unique behaviours:
   - 🔴 Basic — Steady descent, single shots
   - 🟣 Fast — Sine-wave movement, rapid shots
   - 🟠 Tank — Slow but heavily armoured, HP bar visible
   - 👾 Boss — Appears every 5th wave; hovers, fires 3-way spread

2. **Power-up System** — Four collectable power-ups drop from enemies:
   - 💚 Health — Restores 35 HP
   - 💛 Rapid Fire — Double-barrel shots for 10 seconds
   - 💠 Shield — Absorbs one hit completely
   - 🔥 Bomb — Clears the entire screen of enemies

3. **Scoring System** — Points per kill, on-screen score flashes, persistent score tracking

4. **Wave Progression** — Enemies scale with each wave; boss battles every 5th wave

### Visual Elements
- Procedurally drawn sprites (ship, enemies, bullets, power-ups)
- Scrolling parallax star field
- Particle system for explosions, engine trails, bullet impacts
- Animated HUD with HP bar, timers, score
- Shield ring animation
- Score popup floaters on kill

### Audio Elements (requires NumPy)
- Procedurally generated sound effects: shoot, explode, hit, power-up, shield, level-up, game over
- Looping background music synthesised at runtime

---

## WAVE STRUCTURE

| Wave      | Enemies                              |
|-----------|--------------------------------------|
| 1         | 6 Basic                              |
| 2         | 8 Basic, 2 Fast                      |
| 3         | 10 Basic, 3 Fast, 2 Tank             |
| 4         | 12 Basic, 4 Fast, 3 Tank             |
| 5         | ⚠ BOSS WAVE                         |
| 6+        | Scales further + boss every 5 waves  |

---

## PROJECT COMPLIANCE CHECKLIST

- ✅ Built with Pygame (approved engine)
- ✅ Clear genre (Arcade Space Shooter)
- ✅ Storyline (Earth's last defender)
- ✅ 2D application
- ✅ At least one playable level (endless wave-based stage)
- ✅ Clear objective (survive, defeat enemies, score points)
- ✅ Sprites (procedurally drawn)
- ✅ Animations (engine trail, explosions, power-up bobbing, shield ring)
- ✅ Sound effects (shoot, explode, hit, power-up, etc.)
- ✅ Background music (procedurally synthesised)
- ✅ Mechanic 1: Enemy AI (4 types with unique patterns)
- ✅ Mechanic 2: Power-up system (4 types)
- ✅ Bonus: Scoring system
- ✅ Bonus: Boss battles

---

*NOVA STRIKE — Built for PBDE401 game development requirement*
