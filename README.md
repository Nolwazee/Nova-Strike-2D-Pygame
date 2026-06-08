# 🚀 NOVA STRIKE

### A 2D Top-Down Space Shooter Built with Pygame

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)
![Status](https://img.shields.io/badge/Project-Completed-success)
![Genre](https://img.shields.io/badge/Genre-Arcade%20Shooter-red)

---

# 🌌 Storyline

Humanity is on the brink of extinction.

An unstoppable alien race know as Void Armada has invaded Earth, destroying cities, countries and military defenses worldwide. As Earth's final fighter pilot, you are humanity's last hope.

Wave after wave of enemy ships descend from deep space.

Your mission:

**Survive. Defend Earth. Destroy the alien fleet. Defeat the invasion.**

---

# 🎮 Gameplay Preview

## Main Gameplay

Replace these placeholders with screenshots or GIFs.

| Main Battle                                 | Boss Fight                               |
| ------------------------------------------- | ---------------------------------------- |
| ![Gameplay Screenshot](images/gameplay.png) | ![Boss Screenshot](images/bossfight.png) |

---

## Power-Ups

| Health | Rapid Fire   | Shield        | Bomb                |
| ------ | ------------ | ------------- | ------------------- |
| 💚     | 💛           | 💠            | 🔥                  |
| +35 HP | Double Shots | Block One Hit | Destroy All Enemies |

---

# 🎯 Core Features

## Enemy AI System

### 🔴 Basic Enemy

* Steady downward movement
* Single projectile attacks
* Entry-level threat

### 🟣 Fast Enemy

* Sine-wave movement pattern
* Faster firing rate
* Harder to hit

### 🟠 Tank Enemy

* High health pool
* Slow movement
* Visible health bar

### 👾 Boss Enemy

* Appears every 5th wave
* Hovering movement
* Fires 3-way spread attacks
* Massive health pool

---

# 📊 Wave Progression

| Wave | Enemies                                    |
| ---- | ------------------------------------------ |
| 1    | 6 Basic                                    |
| 2    | 8 Basic + 2 Fast                           |
| 3    | 10 Basic + 3 Fast + 2 Tank                 |
| 4    | 12 Basic + 4 Fast + 3 Tank                 |
| 5    | 👾 BOSS WAVE                               |
| 6+   | Increased difficulty + Boss every 5th wave |

### Difficulty Growth

```text
Wave 1  ███
Wave 2  █████
Wave 3  ███████
Wave 4  █████████
Wave 5  ███████████████
Wave 6+ ████████████████████
```

---

# ⚡ Game Mechanics

## Combat System

* Smooth player movement
* Bullet collision detection
* Enemy projectile system
* Bomb attack mechanic

## Power-Up System

Enemies randomly drop collectible upgrades:

| Power-Up      | Effect                              |
| ------------- | ----------------------------------- |
| 💚 Health     | Restores 35 HP                      |
| 💛 Rapid Fire | Double-barrel weapon for 10 seconds |
| 💠 Shield     | Absorbs one incoming hit            |
| 🔥 Bomb       | Clears all enemies on screen        |

---

# 🎨 Visual Effects

### Procedurally Drawn Sprites

* Player ship
* Enemy ships
* Bullets
* Power-ups

### Particle System

* Explosions
* Bullet impacts
* Engine trails
* Score popups

### Background Effects

* Parallax star field
* Shield ring animation
* Floating score indicators

---

# 🔊 Audio System

Procedurally generated using NumPy.

### Sound Effects

* Laser shooting
* Explosions
* Damage hits
* Power-up collection
* Shield activation
* Wave completion
* Game over

### Music

* Runtime-generated looping soundtrack

---

# 🖥️ Controls

| Key        | Action            |
| ---------- | ----------------- |
| W A S D    | Move Ship         |
| Arrow Keys | Move Ship         |
| Z          | Shoot             |
| Left CTRL  | Shoot             |
| SPACE      | Use Bomb          |
| ESC        | Quit/Menu         |
| R          | Retry (Game Over) |

---

# 🏗️ Project Structure

```text
NOVA-STRIKE/
│
├── game.py
├── assets/
│   ├── sounds/
│   └── images/
│
├── screenshots/
│   ├── gameplay.png
│   ├── bossfight.png
│   └── powerups.png
│
├── README.md
│
└── requirements.txt
```

---

# ⚙️ Installation

## Requirements

* Python 3.8+
* Pygame 2.x
* NumPy

## Install Dependencies

```bash
pip install pygame numpy
```

## Run Game

```bash
python game.py
```

---

# 📈 Gameplay Systems Overview

```text
PLAYER
   │
   ├── Shoot
   │
   ▼
ENEMIES
   │
   ├── Drop Power-Ups
   │
   ▼
UPGRADES
   │
   ├── Improve Survival
   │
   ▼
HIGHER WAVES
   │
   ▼
BOSS BATTLES
```

---

# ✅ PBDE401 Requirements Compliance

| Requirement       | Status |
| ----------------- | ------ |
| Pygame Engine     | ✅      |
| 2D Application    | ✅      |
| Storyline         | ✅      |
| Playable Level    | ✅      |
| Objective         | ✅      |
| Sprites           | ✅      |
| Animations        | ✅      |
| Sound Effects     | ✅      |
| Background Music  | ✅      |
| Enemy AI Mechanic | ✅      |
| Power-Up Mechanic | ✅      |
| Scoring System    | ✅      |
| Boss Battles      | ✅      |

---

# 🏆 Learning Outcomes Demonstrated

* Object-Oriented Programming
* Event Handling
* Collision Detection
* Enemy AI Behaviour
* Particle Systems
* Procedural Audio Generation
* Game State Management
* HUD Design
* Wave-Based Difficulty Scaling

---

# 👨‍💻 Developer

**Group 25**

PBDE401 Game Development Project

NOVA STRIKE © 2026
