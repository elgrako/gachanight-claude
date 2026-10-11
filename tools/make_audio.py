#!/usr/bin/env python3
"""Synthesises GachaNight's placeholder audio with the standard library only.

    python tools/make_audio.py

Writes 16-bit mono WAV files to assets/audio/. Everything is original and
generated: short toy-like effects, a store hum and two small retro tunes.
"""
from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

RATE = 22050
OUT = Path(__file__).resolve().parent.parent / "assets" / "audio"
random.seed(1987)


def silence(seconds: float) -> list[float]:
    return [0.0] * int(RATE * seconds)


def envelope(index: int, total: int, attack: float, release: float) -> float:
    t = index / RATE
    length = total / RATE
    if t < attack:
        return t / attack
    remaining = length - t
    if remaining < release:
        return max(remaining / release, 0.0)
    return 1.0


def osc(kind: str, phase: float) -> float:
    cycle = phase % 1.0
    if kind == "sine":
        return math.sin(math.tau * cycle)
    if kind == "square":
        return 0.6 if cycle < 0.5 else -0.6
    if kind == "pulse":
        return 0.6 if cycle < 0.25 else -0.6
    if kind == "triangle":
        return 4.0 * abs(cycle - 0.5) - 1.0
    if kind == "noise":
        return random.uniform(-1.0, 1.0)
    return 0.0


def tone(freq: float, seconds: float, kind: str = "sine", volume: float = 0.5, attack: float = 0.004,
         release: float = 0.05, decay: float = 0.0, slide: float = 0.0, vibrato: float = 0.0) -> list[float]:
    """decay > 0 gives a bell-like exponential fade; slide is semitones over the note."""
    total = int(RATE * seconds)
    samples = []
    phase = 0.0
    for index in range(total):
        t = index / RATE
        progress = index / max(total - 1, 1)
        frequency = freq * 2.0 ** (slide * progress / 12.0)
        if vibrato:
            frequency *= 1.0 + 0.006 * math.sin(math.tau * vibrato * t)
        phase += frequency / RATE
        level = envelope(index, total, attack, release)
        if decay:
            level *= math.exp(-decay * t)
        samples.append(osc(kind, phase) * level * volume)
    return samples


def mix(*layers: list[float]) -> list[float]:
    length = max(len(layer) for layer in layers)
    return [sum(layer[i] for layer in layers if i < len(layer)) for i in range(length)]


def place(target: list[float], layer: list[float], seconds: float) -> None:
    start = int(RATE * seconds)
    if len(target) < start + len(layer):
        target.extend([0.0] * (start + len(layer) - len(target)))
    for index, value in enumerate(layer):
        target[start + index] += value


def lowpass(samples: list[float], strength: float) -> list[float]:
    out, previous = [], 0.0
    for value in samples:
        previous += strength * (value - previous)
        out.append(previous)
    return out


def write(name: str, samples: list[float], peak: float = 0.85) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    loudest = max((abs(s) for s in samples), default=1.0) or 1.0
    scale = peak / loudest if loudest > peak else 1.0
    with wave.open(str(OUT / f"{name}.wav"), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s * scale)) * 32767)) for s in samples))
    print(f"wrote {name}.wav ({len(samples) / RATE:.2f}s)")


def note(name: str) -> float:
    names = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    semitone = names[name[0]] + (1 if "#" in name else 0) + (int(name[-1]) - 4) * 12
    return 440.0 * 2.0 ** (semitone / 12.0)


def bell(name: str, seconds: float = 0.5, volume: float = 0.4) -> list[float]:
    frequency = note(name)
    return mix(tone(frequency, seconds, "sine", volume, decay=7.0),
               tone(frequency * 2.0, seconds, "sine", volume * 0.35, decay=11.0),
               tone(frequency * 3.01, seconds, "sine", volume * 0.12, decay=16.0))


def effects() -> None:
    coin: list[float] = []
    place(coin, bell("B5", 0.25, 0.45), 0.0)
    place(coin, bell("E6", 0.4, 0.45), 0.07)
    write("coin", coin)

    crank: list[float] = []
    for step in range(7):
        click = lowpass(tone(900 + step * 40, 0.035, "noise", 0.6, attack=0.001, release=0.03), 0.45)
        place(crank, mix(click, tone(180, 0.035, "square", 0.18, release=0.03)), step * 0.075)
    write("crank", crank)

    capsule: list[float] = []
    place(capsule, tone(520, 0.12, "sine", 0.6, slide=-14, release=0.08), 0.0)
    place(capsule, lowpass(tone(1, 0.05, "noise", 0.35, release=0.04), 0.5), 0.1)
    place(capsule, tone(880, 0.09, "triangle", 0.3, slide=5, release=0.06), 0.16)
    write("capsule", capsule)

    sell: list[float] = []
    place(sell, lowpass(tone(1, 0.05, "noise", 0.4, release=0.04), 0.6), 0.0)
    place(sell, bell("E6", 0.3, 0.4), 0.04)
    place(sell, bell("A6", 0.5, 0.4), 0.12)
    write("sell", sell)

    keep: list[float] = []
    place(keep, tone(note("C5"), 0.09, "triangle", 0.45, release=0.05), 0.0)
    place(keep, tone(note("G5"), 0.16, "triangle", 0.45, release=0.1), 0.08)
    write("keep", keep)

    complete: list[float] = []
    for index, name in enumerate(["C5", "E5", "G5", "C6", "E6"]):
        place(complete, bell(name, 0.5, 0.36), index * 0.09)
    place(complete, bell("G6", 0.9, 0.3), 0.5)
    write("complete", complete)

    switch: list[float] = []
    place(switch, lowpass(tone(1, 0.09, "noise", 0.9, attack=0.001, release=0.07), 0.25), 0.0)
    place(switch, tone(70, 0.2, "sine", 0.6, slide=-8, release=0.15), 0.0)
    place(switch, tone(55, 1.3, "triangle", 0.25, attack=0.5, release=0.5, slide=2), 0.12)
    for index in range(5):
        place(switch, bell(["C5", "E5", "G5", "B5", "D6"][index], 0.3, 0.16), 0.35 + index * 0.16)
    write("switch", switch)

    write("click", tone(1400, 0.035, "triangle", 0.4, attack=0.001, release=0.03))

    buy: list[float] = []
    place(buy, bell("G5", 0.2, 0.35), 0.0)
    place(buy, bell("C6", 0.2, 0.35), 0.07)
    place(buy, bell("E6", 0.2, 0.35), 0.14)
    place(buy, bell("G6", 0.6, 0.35), 0.21)
    write("buy", buy)

    error: list[float] = []
    place(error, tone(160, 0.11, "square", 0.3, release=0.04), 0.0)
    place(error, tone(120, 0.18, "square", 0.3, release=0.08), 0.13)
    write("error", error)

    write("robot", mix(tone(1900, 0.03, "square", 0.14, attack=0.001, release=0.025),
                       tone(950, 0.05, "triangle", 0.2, release=0.04)))

    write("plinko", mix(lowpass(tone(1, 0.03, "noise", 0.5, attack=0.001, release=0.025), 0.7),
                        tone(1250, 0.05, "sine", 0.35, decay=40.0)))

    unlock: list[float] = []
    for index, name in enumerate(["E5", "A5", "C#6", "E6", "A6"]):
        place(unlock, bell(name, 1.2, 0.26), index * 0.14)
    write("unlock", unlock)

    rebirth: list[float] = []
    for index, name in enumerate(["A5", "E5", "C5", "A4", "E4", "A3"]):
        place(rebirth, tone(note(name), 0.7, "sine", 0.3, attack=0.05, release=0.5, vibrato=5), index * 0.28)
    write("rebirth", rebirth)

    door: list[float] = []
    place(door, lowpass(tone(1, 0.06, "noise", 0.7, attack=0.001, release=0.05), 0.4), 0.0)
    place(door, tone(300, 0.05, "square", 0.2, release=0.03), 0.18)
    place(door, lowpass(tone(1, 0.06, "noise", 0.7, attack=0.001, release=0.05), 0.4), 0.3)
    place(door, tone(90, 1.1, "pulse", 0.16, attack=0.2, release=0.5, slide=7, vibrato=9), 0.5)
    place(door, lowpass(tone(1, 1.6, "noise", 0.2, attack=0.6, release=0.8), 0.05), 0.9)
    write("door", door)


def ambient() -> None:
    """Four seconds of machine hum that loops cleanly (whole cycles of every partial)."""
    total = RATE * 4
    samples = []
    for index in range(total):
        t = index / RATE
        value = 0.22 * math.sin(math.tau * 60.0 * t) + 0.1 * math.sin(math.tau * 120.0 * t)
        value += 0.04 * math.sin(math.tau * 180.0 * t) * (1.0 + 0.5 * math.sin(math.tau * 0.5 * t))
        samples.append(value)
    hiss = lowpass([random.uniform(-0.05, 0.05) for _ in range(total)], 0.08)
    fade = int(RATE * 0.25)
    for index in range(fade):
        blend = index / fade
        hiss[index] = hiss[index] * blend + hiss[total - fade + index] * (1.0 - blend)
    write("ambient", mix(samples, hiss), peak=0.5)


def sequence(track: list[tuple[str, float]], beat: float, kind: str, volume: float, release: float = 0.06,
             decay: float = 0.0) -> list[float]:
    out: list[float] = []
    time = 0.0
    for name, beats in track:
        if name != "-":
            place(out, tone(note(name), beats * beat * 0.95, kind, volume, release=release, decay=decay), time)
        time += beats * beat
    if len(out) < int(RATE * time):
        out.extend([0.0] * (int(RATE * time) - len(out)))
    return out


def music() -> None:
    """A light toy-shop loop on a pentatonic scale: lead, arpeggio and bass."""
    beat = 60.0 / 104.0
    phrase_a = [("E5", 1), ("G5", 1), ("A5", 1), ("G5", 1), ("E5", 1), ("D5", 1), ("C5", 2)]
    phrase_b = [("D5", 1), ("E5", 1), ("G5", 1), ("E5", 1), ("D5", 1), ("C5", 1), ("A4", 2)]
    phrase_c = [("C5", 1), ("D5", 1), ("E5", 2), ("G5", 1), ("A5", 1), ("C6", 2)]
    phrase_d = [("A5", 1), ("G5", 1), ("E5", 1), ("D5", 1), ("C5", 2), ("-", 2)]
    lead = sequence(phrase_a + phrase_b + phrase_c + phrase_d + phrase_a + phrase_b + phrase_c + phrase_d,
                    beat, "pulse", 0.2, release=0.08)
    chords = [("C4", "E4", "G4"), ("A3", "C4", "E4"), ("F3", "A3", "C4"), ("G3", "B3", "D4")] * 2
    arpeggio: list[tuple[str, float]] = []
    bass: list[tuple[str, float]] = []
    for chord in chords:
        for _ in range(2):
            arpeggio.extend([(chord[0], 0.5), (chord[1], 0.5), (chord[2], 0.5), (chord[1], 0.5),
                             (chord[0], 0.5), (chord[2], 0.5), (chord[1], 0.5), (chord[2], 0.5)])
        root = chord[0][:-1] + str(int(chord[0][-1]) - 1)
        bass.extend([(root, 2), (root, 1), ("-", 1), (root, 2), (root, 1), (root, 1)])
    write("music", mix(lead, sequence(arpeggio, beat, "triangle", 0.16, release=0.05),
                       sequence(bass, beat, "triangle", 0.3, release=0.1)), peak=0.7)

    slow = 60.0 / 66.0
    melody = [("C5", 2), ("E5", 2), ("G5", 3), ("E5", 1), ("A5", 2), ("G5", 2), ("E5", 4),
              ("D5", 2), ("E5", 2), ("G5", 3), ("A5", 1), ("C6", 6), ("-", 2)]
    pad = [("C3", 8), ("A2", 8), ("F2", 8), ("C3", 8)]
    write("ending", mix(sequence(melody, slow, "sine", 0.3, release=0.4, decay=1.2),
                        sequence(pad, slow, "triangle", 0.2, release=0.8)), peak=0.7)


if __name__ == "__main__":
    effects()
    ambient()
    music()
