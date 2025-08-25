#!/usr/bin/env python3
"""
Funny Joke Adventure — kid-friendly, replayable joke game (Desktop)
Author: You (Technical PM demo)

Controls:
- SPACE: fetch new joke (new "adventure event")
- ESC / Q: quit
- M: toggle text-to-speech (if pyttsx3 installed)
- D: toggle debug/chaos mode (simulated failures/delays)
- F: toggle full screen
"""
import os
import sys
import time
import random
import argparse
from datetime import datetime

# Optional deps
try:
    import requests
except Exception:
    requests = None

# TTS is optional
try:
    import pyttsx3
except Exception:
    pyttsx3 = None

import pygame

SAFE_API_URL = "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single"

OFFLINE_JOKES = [
    "Why did the teddy bear say no to dessert? Because it was stuffed!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why did the banana go to the doctor? It wasn't peeling well.",
    "What do you call a boomerang that doesn't come back? A stick!",
    "Why did the cookie go to the nurse? It felt crummy.",
    "Why did the student eat his homework? Because the teacher said it was a piece of cake!",
    "How do you make a lemon drop? Just let it fall.",
    "Why did the bicycle fall over? It was two-tired!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call cheese that isn't yours? Nacho cheese!",
]

def log_event(base_dir, payload):
    try:
        logs_dir = os.path.join(base_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        fp = os.path.join(logs_dir, "session_log.csv")
        header_needed = not os.path.exists(fp)
        with open(fp, "a", encoding="utf-8") as f:
            if header_needed:
                f.write("timestamp,source,success,joke_len,chaos_enabled\n")
            row = f"{datetime.utcnow().isoformat()}Z,{payload.get('source')},{payload.get('success')},{payload.get('joke_len')},{payload.get('chaos')}\n"
            f.write(row)
    except Exception:
        pass

def fetch_joke(timeout=5.0, chaos_p=0.0, base_dir="."):
    """Fetch a safe single-line joke. Fallback to offline list on error."""
    # Chaos: randomly simulate failure or delay
    if random.random() < chaos_p:
        if random.random() < 0.5:
            time.sleep(2.2)  # simulate slow network
        else:
            raise RuntimeError("Simulated chaos failure")

    if requests is None:
        joke = random.choice(OFFLINE_JOKES)
        log_event(base_dir, {"source":"offline:no_requests", "success":False, "joke_len":len(joke), "chaos":chaos_p})
        return joke, "offline"

    try:
        r = requests.get(SAFE_API_URL, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        joke = data.get("joke")
        if not joke or not isinstance(joke, str):
            raise ValueError("Malformed API response")
        log_event(base_dir, {"source":"api", "success":True, "joke_len":len(joke), "chaos":chaos_p})
        return joke, "api"
    except Exception:
        joke = random.choice(OFFLINE_JOKES)
        log_event(base_dir, {"source":"offline", "success":False, "joke_len":len(joke), "chaos":chaos_p})
        return joke, "offline"

def wrap_text(text, font, max_width):
    """Wrap text into lines that fit within max_width (in pixels)."""
    words = text.split()
    lines = []
    attempted = ""
    for w in words:
        test = attempted + (" " if attempted else "") + w
        if font.size(test)[0] <= max_width:
            attempted = test
        else:
            if attempted:
                lines.append(attempted)
            attempted = w
    if attempted:
        lines.append(attempted)
    return lines

def draw_centered_text(surface, lines, font, color, center_y, line_gap=10):
    total_h = sum(font.size(line)[1] for line in lines) + line_gap*(len(lines)-1)
    width = surface.get_width()
    y = center_y - total_h // 2
    for line in lines:
        surf = font.render(line, True, color)
        rect = surf.get_rect(center=(width//2, y + surf.get_height()//2))
        surface.blit(surf, rect)
        y += surf.get_height() + line_gap

def draw_title(surface, text, font, y, colors=((255,0,0),(255,165,0),(255,255,0),(0,128,0),(0,0,255),(75,0,130),(238,130,238))):
    # Simple "rainbow" title: color per character cycling
    x = surface.get_width() // 2
    char_surfs = [font.render(ch, True, colors[i % len(colors)]) for i, ch in enumerate(text)]
    total_w = sum(s.get_width() for s in char_surfs)
    start_x = x - total_w // 2
    cx = start_x
    for s in char_surfs:
        surface.blit(s, (cx, y))
        cx += s.get_width()

def main():
    parser = argparse.ArgumentParser(description="Funny Joke Adventure (Desktop)")
    parser.add_argument("--chaos", type=float, default=0.0, help="Probability [0..1] to simulate failure/delay per fetch")
    parser.add_argument("--fullscreen", action="store_true", help="Start in fullscreen")
    parser.add_argument("--tts", action="store_true", help="Start with text-to-speech ON (requires pyttsx3)")
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=600)
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    pygame.init()
    pygame.display.setCaption = pygame.display.set_caption  # alias safety
    pygame.display.set_caption("Funny Joke Adventure!")
    flags = pygame.FULLSCREEN if args.fullscreen else 0
    screen = pygame.display.set_mode((args.width, args.height), flags)
    clock = pygame.time.Clock()

    # Fonts
    try:
        title_font = pygame.font.SysFont("arial", 50, bold=True)
        joke_font = pygame.font.SysFont("arial", 36, bold=False)
        hint_font = pygame.font.SysFont("arial", 24)
    except Exception:
        pygame.font.init()
        title_font = pygame.font.Font(None, 50)
        joke_font  = pygame.font.Font(None, 36)
        hint_font  = pygame.font.Font(None, 24)

    # Colors
    BG = (66, 170, 255)   # sky blue
    PANEL = (255, 255, 255)
    TEXT = (0, 0, 0)
    HINT = (30, 30, 30)

    # Optional TTS setup
    tts_on = bool(args.tts) and (pyttsx3 is not None)
    tts_engine = None
    if tts_on and pyttsx3 is not None:
        try:
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', 160)
            tts_engine.setProperty('volume', 1.0)
        except Exception:
            tts_on = False
            tts_engine = None

    current_joke = "Press SPACE for your first adventure!"
    last_source = "offline"
    blink = 0
    fullscreen = args.fullscreen
    chaos_p = max(0.0, min(1.0, args.chaos))

    def speak(text):
        if not tts_on or tts_engine is None:
            return
        try:
            tts_engine.stop()
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception:
            pass

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    try:
                        joke, src = fetch_joke(timeout=5.0, chaos_p=chaos_p, base_dir=base_dir)
                        current_joke = joke
                        last_source = src
                        speak(joke)
                    except Exception:
                        current_joke = random.choice(OFFLINE_JOKES)
                        last_source = "offline"
                        speak(current_joke)
                elif event.key == pygame.K_m:  # toggle TTS
                    if pyttsx3 is not None:
                        nonlocal_tts = not tts_on  # for readability
                        tts_on = nonlocal_tts
                elif event.key == pygame.K_d:  # toggle chaos
                    chaos_p = 0.0 if chaos_p > 0 else 0.2
                elif event.key == pygame.K_f:  # toggle fullscreen
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((args.width, args.height))

        # Draw
        screen.fill(BG)

        # Title
        draw_title(screen, "Funny Joke Adventure!", title_font, 20)

        # "Speech bubble" panel
        margin = 40
        panel_w = screen.get_width() - margin*2
        panel_h = int(screen.get_height() * 0.55)
        panel_x = margin
        panel_y = int(screen.get_height() * 0.18)

        pygame.draw.rect(screen, PANEL, pygame.Rect(panel_x, panel_y, panel_w, panel_h), border_radius=24)
        pygame.draw.rect(screen, (220,220,220), pygame.Rect(panel_x, panel_y, panel_w, panel_h), width=4, border_radius=24)

        # Wrap and draw joke
        max_text_w = int(panel_w - 40)
        lines = wrap_text(current_joke, joke_font, max_text_w)
        draw_centered_text(screen, lines, joke_font, TEXT, int(panel_y + panel_h/2), line_gap=12)

        # Bottom prompts
        blink = (blink + 1) % 60
        hint_text = "Press SPACE for more fun!  (M: voice {}  D: chaos {}  Source: {})".format(
            "ON" if tts_on else "OFF",
            "ON" if chaos_p > 0 else "OFF",
            last_source.upper()
        )
        hint_surf = hint_font.render(hint_text, True, HINT)
        hint_rect = hint_surf.get_rect(center=(screen.get_width()//2, int(screen.get_height()*0.90)))
        if blink < 40:  # blink effect
            screen.blit(hint_surf, hint_rect)

        pygame.display.flip()
        clock.tick(60)

    if tts_engine is not None:
        try:
            tts_engine.stop()
        except Exception:
            pass
    pygame.quit()

if __name__ == "__main__":
    main()

