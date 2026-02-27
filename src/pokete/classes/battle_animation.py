"""Battle animation system for attack animations, damage numbers, and status effects."""

import time
import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable

import scrap_engine as se

from pokete.release import SPEED_OF_TIME
from pokete.base.color import Color


class AnimationType(Enum):
    PHYSICAL = "physical"
    PROJECTILE = "projectile"
    EFFECT = "effect"
    BUFF = "buff"
    DEBUFF = "debuff"
    ELEMENTAL = "elemental"


@dataclass
class AnimationFrame:
    chars: list[str]
    duration: float
    color: str = ""
    x_offset: int = 0
    y_offset: int = 0


class DamageNumberDisplay:
    """Shows floating damage numbers during battle."""

    def __init__(self):
        self.active_numbers: list[tuple[se.Text, float, int, int]] = []

    def show(self, _map, x: int, y: int, damage: int, is_critical: bool = False,
             is_heal: bool = False, is_miss: bool = False):
        """Display a damage number that floats upward."""
        if is_miss:
            text = "MISS"
            color = Color.lightgrey
        elif is_heal:
            text = f"+{damage}"
            color = Color.green
        elif is_critical:
            text = f"{damage}!"
            color = Color.thicc + Color.yellow
        else:
            text = str(damage)
            color = Color.thicc + Color.red if damage > 0 else Color.white

        label = se.Text(text, esccode=color, state="float")
        try:
            label.add(_map, x, y)
        except se.CoordinateError:
            return

        for offset in range(3):
            label.remove()
            new_y = y - offset - 1
            if new_y >= 0:
                try:
                    label.add(_map, x, new_y)
                    _map.show()
                    time.sleep(SPEED_OF_TIME * 0.12)
                except se.CoordinateError:
                    break
            else:
                break

        label.remove()
        _map.show()


class StatusEffectAnimation:
    """Animations for status effect application and removal."""

    EFFECT_VISUALS = {
        "paralyzation": {"char": "⚡", "color": Color.thicc + Color.yellow, "pattern": "spark"},
        "sleep": {"char": "z", "color": Color.white, "pattern": "float"},
        "burning": {"char": "*", "color": Color.thicc + Color.red, "pattern": "flicker"},
        "poison": {"char": "~", "color": Color.purple, "pattern": "wave"},
        "confusion": {"char": "?", "color": Color.lightblue, "pattern": "spin"},
        "freezing": {"char": "#", "color": Color.cyan, "pattern": "crystallize"},
    }

    def __init__(self):
        pass

    def play_effect_applied(self, _map, target_ico, effect_name: str):
        """Play animation when a status effect is applied."""
        if effect_name not in self.EFFECT_VISUALS:
            return

        visual = self.EFFECT_VISUALS[effect_name]
        pattern = visual["pattern"]
        char = visual["char"]
        color = visual["color"]

        x = target_ico.x + target_ico.width // 2
        y = target_ico.y + target_ico.height // 2

        if pattern == "spark":
            self._spark_animation(_map, x, y, char, color)
        elif pattern == "float":
            self._float_animation(_map, x, y, char, color)
        elif pattern == "flicker":
            self._flicker_animation(_map, x, y, char, color)
        elif pattern == "wave":
            self._wave_animation(_map, x, y, char, color)
        elif pattern == "spin":
            self._spin_animation(_map, x, y, char, color)
        elif pattern == "crystallize":
            self._crystallize_animation(_map, x, y, char, color)

    def _spark_animation(self, _map, x: int, y: int, char: str, color: str):
        """Quick spark effect for paralysis."""
        positions = [
            (0, -1), (1, 0), (0, 1), (-1, 0),
            (1, -1), (1, 1), (-1, 1), (-1, -1)
        ]
        sparks = []
        for dx, dy in positions:
            spark = se.Text(char, esccode=color, state="float")
            try:
                spark.add(_map, x + dx, y + dy)
                sparks.append(spark)
            except se.CoordinateError:
                pass

        _map.show()
        time.sleep(SPEED_OF_TIME * 0.15)

        for spark in sparks:
            spark.remove()
        _map.show()

    def _float_animation(self, _map, x: int, y: int, char: str, color: str):
        """Floating Z's for sleep."""
        for i in range(3):
            z = se.Text(char * (i + 1), esccode=color, state="float")
            try:
                z.add(_map, x + i, y - i)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.2)
                z.remove()
            except se.CoordinateError:
                pass

    def _flicker_animation(self, _map, x: int, y: int, char: str, color: str):
        """Flickering effect for burning."""
        flame = se.Text(char, esccode=color, state="float")
        for _ in range(4):
            offset_x = random.randint(-1, 1)
            offset_y = random.randint(-1, 0)
            try:
                flame.add(_map, x + offset_x, y + offset_y)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.08)
                flame.remove()
            except se.CoordinateError:
                pass

    def _wave_animation(self, _map, x: int, y: int, char: str, color: str):
        """Wave pattern for poison."""
        for i in range(3):
            wave = se.Text(char * 3, esccode=color, state="float")
            try:
                wave.add(_map, x - 1, y + i - 1)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.1)
                wave.remove()
            except se.CoordinateError:
                pass

    def _spin_animation(self, _map, x: int, y: int, char: str, color: str):
        """Spinning effect for confusion."""
        positions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        q = se.Text(char, esccode=color, state="float")
        for dx, dy in positions * 2:
            try:
                q.add(_map, x + dx, y + dy)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.08)
                q.remove()
            except se.CoordinateError:
                pass

    def _crystallize_animation(self, _map, x: int, y: int, char: str, color: str):
        """Crystallizing effect for freezing."""
        crystals = []
        for i in range(5):
            crystal = se.Text(char, esccode=color, state="float")
            cx = x + random.randint(-2, 2)
            cy = y + random.randint(-1, 1)
            try:
                crystal.add(_map, cx, cy)
                crystals.append(crystal)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.05)
            except se.CoordinateError:
                pass

        time.sleep(SPEED_OF_TIME * 0.15)
        for crystal in crystals:
            crystal.remove()
        _map.show()


class AttackAnimationSystem:
    """Main system for coordinating attack animations."""

    TYPE_COLORS = {
        "normal": Color.white,
        "fire": Color.thicc + Color.red,
        "water": Color.blue,
        "plant": Color.green,
        "electro": Color.yellow,
        "ice": Color.cyan,
        "ground": Color.gold,
        "stone": Color.lightgrey,
        "flying": Color.lightblue,
        "undead": Color.purple,
        "poison": Color.purple,
    }

    TYPE_CHARS = {
        "normal": "*",
        "fire": "~",
        "water": "o",
        "plant": "#",
        "electro": "z",
        "ice": "*",
        "ground": "=",
        "stone": "@",
        "flying": "^",
        "undead": "$",
        "poison": "~",
    }

    def __init__(self):
        self.damage_display = DamageNumberDisplay()
        self.status_animation = StatusEffectAnimation()

    def get_type_color(self, type_name: str) -> str:
        return self.TYPE_COLORS.get(type_name, Color.white)

    def get_type_char(self, type_name: str) -> str:
        return self.TYPE_CHARS.get(type_name, "*")

    def play_attack_animation(self, _map, attacker_ico, defender_ico,
                               attack_type: str, attack_name: str,
                               move_type: str = "attack"):
        """Play the main attack animation based on attack type and move."""
        color = self.get_type_color(attack_type)
        char = self.get_type_char(attack_type)

        if move_type in ("fireball", "throw", "gun"):
            self._projectile_animation(_map, attacker_ico, defender_ico, char, color)
        elif move_type == "arch":
            self._arc_animation(_map, attacker_ico, defender_ico, color)
        elif move_type == "bomb":
            self._explosion_animation(_map, defender_ico, color)
        elif move_type in ("shine", "smell"):
            self._buff_animation(_map, attacker_ico, color)
        elif move_type == "downgrade":
            self._debuff_animation(_map, defender_ico)
        elif move_type == "rain":
            pass  # Rain has its own animation in moves.py
        else:
            self._impact_animation(_map, defender_ico, color, char)

    def _projectile_animation(self, _map, attacker_ico, defender_ico,
                               char: str, color: str):
        """Animate a projectile moving from attacker to defender."""
        is_player = attacker_ico.x < defender_ico.x

        start_x = attacker_ico.x + (attacker_ico.width if is_player else 0)
        start_y = attacker_ico.y + attacker_ico.height // 2
        end_x = defender_ico.x + (0 if is_player else defender_ico.width)
        end_y = defender_ico.y + defender_ico.height // 2

        dx = end_x - start_x
        dy = end_y - start_y
        steps = max(abs(dx), 1)

        projectile = se.Text(color + char + Color.reset, state="float")
        trail_chars: list[se.Text] = []

        for i in range(steps):
            t = i / steps
            x = int(start_x + dx * t)
            y = int(start_y + dy * t)

            try:
                projectile.add(_map, x, y)

                # Add trail
                if i > 0 and len(trail_chars) < 3:
                    trail = se.Text(Color.white + "." + Color.reset, state="float")
                    prev_t = (i - 1) / steps
                    prev_x = int(start_x + dx * prev_t)
                    prev_y = int(start_y + dy * prev_t)
                    try:
                        trail.add(_map, prev_x, prev_y)
                        trail_chars.append(trail)
                    except se.CoordinateError:
                        pass

                _map.show()
                time.sleep(SPEED_OF_TIME * 0.03)
                projectile.remove()

                # Clean old trail
                if len(trail_chars) > 2:
                    old_trail = trail_chars.pop(0)
                    old_trail.remove()

            except se.CoordinateError:
                break

        for trail in trail_chars:
            trail.remove()
        _map.show()

    def _arc_animation(self, _map, attacker_ico, defender_ico, color: str):
        """Electric arc animation."""
        is_player = attacker_ico.x < defender_ico.x

        start_x = attacker_ico.x + (attacker_ico.width if is_player else 0)
        start_y = attacker_ico.y + 1
        end_x = defender_ico.x + (0 if is_player else defender_ico.width)
        end_y = defender_ico.y + 1

        arc_chars = ["-", "~", "=", "z", "Z"]
        dx = end_x - start_x
        steps = max(abs(dx), 1)

        arc_objects: list[se.Text] = []
        for i in range(steps):
            t = i / steps
            x = int(start_x + dx * t)
            # Arc trajectory (parabola)
            y = int(start_y + (end_y - start_y) * t - 2 * (t * (1 - t) * 3))

            char = random.choice(arc_chars)
            arc_obj = se.Text(color + char + Color.reset, state="float")
            try:
                arc_obj.add(_map, x, y)
                arc_objects.append(arc_obj)
            except se.CoordinateError:
                pass

        _map.show()
        time.sleep(SPEED_OF_TIME * 0.4)

        for obj in arc_objects:
            obj.remove()
        _map.show()

    def _explosion_animation(self, _map, target_ico, color: str):
        """Explosion animation at target location."""
        cx = target_ico.x + target_ico.width // 2
        cy = target_ico.y + target_ico.height // 2

        frames = [
            ([("o", 0, 0)], 0.05),
            ([("O", 0, 0), ("*", -1, 0), ("*", 1, 0), ("*", 0, -1), ("*", 0, 1)], 0.05),
            ([("*", -1, -1), ("*", 1, -1), ("*", -1, 1), ("*", 1, 1),
              ("-", -2, 0), ("-", 2, 0), ("|", 0, -2), ("|", 0, 2)], 0.05),
            ([("`", -2, -1), ("'", 2, -1), (",", -2, 1), (".", 2, 1)], 0.08),
        ]

        for chars_list, duration in frames:
            explosions = []
            for char, dx, dy in chars_list:
                exp = se.Text(color + char + Color.reset, state="float")
                try:
                    exp.add(_map, cx + dx, cy + dy)
                    explosions.append(exp)
                except se.CoordinateError:
                    pass

            _map.show()
            time.sleep(SPEED_OF_TIME * duration)

            for exp in explosions:
                exp.remove()

        _map.show()

    def _impact_animation(self, _map, target_ico, color: str, char: str):
        """Quick impact flash on target."""
        cx = target_ico.x + target_ico.width // 2
        cy = target_ico.y + target_ico.height // 2

        impact_chars = ["*", "X", "*"]
        impact = se.Text(Color.thicc + Color.yellow + impact_chars[0] + Color.reset,
                         state="float")
        try:
            impact.add(_map, cx, cy)
            for ic in impact_chars:
                impact.rechar(Color.thicc + Color.yellow + ic + Color.reset)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.06)
            impact.remove()
            _map.show()
        except se.CoordinateError:
            pass

    def _buff_animation(self, _map, target_ico, color: str):
        """Buff/power-up animation."""
        corners = [
            (target_ico.x - 1, target_ico.y),
            (target_ico.x + target_ico.width, target_ico.y),
            (target_ico.x - 1, target_ico.y + target_ico.height - 1),
            (target_ico.x + target_ico.width, target_ico.y + target_ico.height - 1),
        ]

        stars = []
        for x, y in corners:
            star = se.Text(color + "*" + Color.reset, state="float")
            try:
                star.add(_map, x, y)
                stars.append(star)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.1)
            except se.CoordinateError:
                pass

        time.sleep(SPEED_OF_TIME * 0.15)

        for star in stars:
            star.remove()
        _map.show()

    def _debuff_animation(self, _map, target_ico):
        """Debuff/weakness animation."""
        corners = [
            (target_ico.x - 1, target_ico.y),
            (target_ico.x + target_ico.width, target_ico.y),
            (target_ico.x - 1, target_ico.y + target_ico.height - 1),
            (target_ico.x + target_ico.width, target_ico.y + target_ico.height - 1),
        ]

        arrows = []
        for x, y in corners:
            arrow = se.Text(Color.thicc + Color.red + "-" + Color.reset, state="float")
            try:
                arrow.add(_map, x, y)
                arrows.append(arrow)
                _map.show()
                time.sleep(SPEED_OF_TIME * 0.1)
            except se.CoordinateError:
                pass

        time.sleep(SPEED_OF_TIME * 0.15)

        for arrow in arrows:
            arrow.remove()
        _map.show()

    def show_damage(self, _map, target_ico, damage: int, is_critical: bool = False):
        """Show floating damage number on target."""
        x = target_ico.x + target_ico.width // 2
        y = target_ico.y
        self.damage_display.show(_map, x, y, damage, is_critical=is_critical)

    def show_heal(self, _map, target_ico, amount: int):
        """Show floating heal number on target."""
        x = target_ico.x + target_ico.width // 2
        y = target_ico.y
        self.damage_display.show(_map, x, y, amount, is_heal=True)

    def show_miss(self, _map, target_ico):
        """Show miss indicator."""
        x = target_ico.x + target_ico.width // 2
        y = target_ico.y
        self.damage_display.show(_map, x, y, 0, is_miss=True)

    def show_effectiveness(self, _map, target_ico, effectiveness: float):
        """Show effectiveness indicator (super effective, not very effective)."""
        x = target_ico.x + target_ico.width // 2
        y = target_ico.y - 1

        if effectiveness > 1:
            text = "SUPER!"
            color = Color.thicc + Color.yellow
        elif effectiveness < 1:
            text = "weak"
            color = Color.lightgrey
        else:
            return

        label = se.Text(text, esccode=color, state="float")
        try:
            label.add(_map, x - len(text) // 2, y)
            _map.show()
            time.sleep(SPEED_OF_TIME * 0.4)
            label.remove()
            _map.show()
        except se.CoordinateError:
            pass

    def play_status_effect(self, _map, target_ico, effect_name: str):
        """Play animation for status effect application."""
        self.status_animation.play_effect_applied(_map, target_ico, effect_name)


# Global instance
battle_animations = AttackAnimationSystem()


if __name__ == "__main__":
    print("\033[31;1mDo not execute this!\033[0m")
