"""Battle animation system for attack animations, damage numbers, and status effects.

This module provides visual feedback during battles through:
- Attack animations with type-specific visual effects
- Floating damage numbers that rise and fade
- Status effect indicators with color coding
- Screen shake effects for powerful attacks
- Hit flash effects on the target
"""

import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, TYPE_CHECKING

import scrap_engine as se

from pokete.base.color import Color
from pokete.release import SPEED_OF_TIME

if TYPE_CHECKING:
    from pokete.classes.poke import Poke
    from pokete.classes.attack import Attack


class AnimationIntensity(Enum):
    """Attack animation intensity levels based on damage factor."""
    WEAK = 1
    NORMAL = 2
    STRONG = 3
    CRITICAL = 4


@dataclass
class TypeEffects:
    """Visual configuration for attack type animations."""
    color: str
    particle_char: str
    impact_chars: list[str]
    trail_char: str


# Type-specific visual effects configuration
TYPE_EFFECT_CONFIG: dict[str, TypeEffects] = {
    "normal": TypeEffects(Color.white, "*", ["*", "x", "*"], "."),
    "fire": TypeEffects(Color.red + Color.thicc, "~", ["*", "⁂", "✦", "*"], "°"),
    "water": TypeEffects(Color.blue, "~", ["o", "O", "o"], "·"),
    "plant": TypeEffects(Color.green, "#", ["❋", "*", "❋"], "·"),
    "electro": TypeEffects(Color.yellow + Color.thicc, "⚡", ["*", "X", "*"], "-"),
    "ground": TypeEffects(Color.brown if hasattr(Color, "brown") else Color.yellow, "▪", ["■", "□", "■"], "."),
    "stone": TypeEffects(Color.grey, "●", ["◆", "◇", "◆"], "·"),
    "ice": TypeEffects(Color.cyan, "❄", ["✦", "✧", "✦"], "*"),
    "flying": TypeEffects(Color.lightblue, "~", ["≈", "~", "≈"], "·"),
    "poison": TypeEffects(Color.purple, "☠", ["✗", "X", "✗"], "·"),
    "undead": TypeEffects(Color.purple + Color.thicc, "☠", ["✝", "†", "✝"], "·"),
}


def get_type_effects(type_name: str) -> TypeEffects:
    """Get visual effects configuration for a given type."""
    return TYPE_EFFECT_CONFIG.get(type_name, TYPE_EFFECT_CONFIG["normal"])


class DamageNumber:
    """Floating damage number that rises and fades out."""

    def __init__(self, damage: int, x: int, y: int, _map: se.Map,
                 color: str = Color.white, is_critical: bool = False,
                 is_heal: bool = False):
        self.damage = damage
        self.x = x
        self.y = y
        self.map = _map
        self.is_critical = is_critical
        self.is_heal = is_heal

        if is_heal:
            text = f"+{damage}"
            color = Color.green + Color.thicc
        elif damage == 0:
            text = "MISS"
            color = Color.grey
        else:
            text = str(damage)
            if is_critical:
                text = f"!{damage}!"
                color = Color.yellow + Color.thicc

        self.text_obj = se.Text(text, esccode=color, state="float")
        self.added = False

    def play(self, duration: float = 0.8):
        """Animate the damage number rising and fading."""
        if self.damage == 0 and not self.is_heal:
            self._play_miss()
            return

        try:
            self.text_obj.add(self.map, self.x, self.y)
            self.added = True
        except (se.CoordinateError, AttributeError):
            return

        steps = max(3, int(duration / 0.15))
        for i in range(steps):
            self.map.show()
            time.sleep(SPEED_OF_TIME * (duration / steps))
            try:
                if self.y > 1:
                    self.text_obj.move(0, -1)
                    self.y -= 1
            except (se.CoordinateError, AttributeError):
                break

        self._cleanup()

    def _play_miss(self):
        """Animate miss text with shake effect."""
        try:
            self.text_obj.add(self.map, self.x, self.y)
            self.added = True
        except (se.CoordinateError, AttributeError):
            return

        for _ in range(3):
            self.map.show()
            time.sleep(SPEED_OF_TIME * 0.1)
            try:
                self.text_obj.move(1 if random.random() > 0.5 else -1, 0)
            except (se.CoordinateError, AttributeError):
                pass
            self.map.show()
            time.sleep(SPEED_OF_TIME * 0.1)
            try:
                self.text_obj.move(-1 if random.random() > 0.5 else 1, 0)
            except (se.CoordinateError, AttributeError):
                pass

        self._cleanup()

    def _cleanup(self):
        """Remove the damage number from the map."""
        if self.added:
            try:
                self.text_obj.remove()
            except (AttributeError, ValueError):
                pass
            self.added = False


class StatusEffectIndicator:
    """Visual indicator for status effect application or removal."""

    EFFECT_COLORS = {
        "paralyzation": Color.yellow + Color.thicc,
        "sleep": Color.white,
        "burning": Color.red + Color.thicc,
        "poison": Color.purple,
        "confusion": Color.lightblue,
        "freezing": Color.cyan,
    }

    EFFECT_SYMBOLS = {
        "paralyzation": "⚡",
        "sleep": "Z",
        "burning": "🔥",
        "poison": "☠",
        "confusion": "?",
        "freezing": "❄",
    }

    def __init__(self, effect_name: str, x: int, y: int, _map: se.Map,
                 is_applied: bool = True):
        self.effect_name = effect_name
        self.x = x
        self.y = y
        self.map = _map
        self.is_applied = is_applied

        color = self.EFFECT_COLORS.get(effect_name, Color.white)
        symbol = self.EFFECT_SYMBOLS.get(effect_name, "*")

        if is_applied:
            text = f"+{symbol}"
        else:
            text = f"-{symbol}"

        self.text_obj = se.Text(text, esccode=color, state="float")
        self.added = False

    def play(self, duration: float = 0.6):
        """Animate the status effect indicator."""
        try:
            self.text_obj.add(self.map, self.x, self.y)
            self.added = True
        except (se.CoordinateError, AttributeError):
            return

        for _ in range(3):
            self.map.show()
            time.sleep(SPEED_OF_TIME * (duration / 6))
            try:
                self.text_obj.move(0, -1)
            except (se.CoordinateError, AttributeError):
                break

        if self.added:
            try:
                self.text_obj.remove()
            except (AttributeError, ValueError):
                pass


class ScreenShake:
    """Screen shake effect for powerful attacks."""

    def __init__(self, _map: se.Map, intensity: AnimationIntensity):
        self.map = _map
        self.intensity = intensity
        self.shake_amounts = {
            AnimationIntensity.WEAK: 0,
            AnimationIntensity.NORMAL: 1,
            AnimationIntensity.STRONG: 2,
            AnimationIntensity.CRITICAL: 3,
        }

    def play(self):
        """Execute the screen shake effect by rapidly showing the map."""
        amount = self.shake_amounts.get(self.intensity, 0)
        if amount == 0:
            return

        for _ in range(amount * 2):
            self.map.show()
            time.sleep(SPEED_OF_TIME * 0.03)


class HitFlash:
    """Flash effect on the target when hit."""

    def __init__(self, target_ico: se.Box, _map: se.Map, type_name: str = "normal"):
        self.target_ico = target_ico
        self.map = _map
        self.type_effects = get_type_effects(type_name)

    def play(self, flashes: int = 2):
        """Execute hit flash effect around the target icon."""
        if not hasattr(self.target_ico, 'x') or not hasattr(self.target_ico, 'y'):
            return

        flash_positions = [
            (self.target_ico.x - 1, self.target_ico.y),
            (self.target_ico.x + self.target_ico.width, self.target_ico.y),
            (self.target_ico.x - 1, self.target_ico.y + self.target_ico.height - 1),
            (self.target_ico.x + self.target_ico.width, self.target_ico.y + self.target_ico.height - 1),
        ]

        flash_objs = []
        for char in self.type_effects.impact_chars[:flashes]:
            for x, y in flash_positions:
                obj = se.Text(char, esccode=self.type_effects.color, state="float")
                try:
                    obj.add(self.map, x, y)
                    flash_objs.append(obj)
                except (se.CoordinateError, AttributeError):
                    pass

            self.map.show()
            time.sleep(SPEED_OF_TIME * 0.08)

            for obj in flash_objs:
                try:
                    obj.remove()
                except (AttributeError, ValueError):
                    pass
            flash_objs.clear()


class TypeParticles:
    """Particle effect based on attack type."""

    def __init__(self, start_x: int, start_y: int, end_x: int, end_y: int,
                 _map: se.Map, type_name: str = "normal"):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.map = _map
        self.type_effects = get_type_effects(type_name)

    def play(self, num_particles: int = 3):
        """Emit particles from start to end position."""
        particles = []
        for _ in range(num_particles):
            offset_x = random.randint(-1, 1)
            offset_y = random.randint(-1, 1)
            particle = se.Text(
                self.type_effects.particle_char,
                esccode=self.type_effects.color,
                state="float"
            )
            try:
                particle.add(self.map, self.start_x + offset_x, self.start_y + offset_y)
                particles.append({
                    'obj': particle,
                    'x': self.start_x + offset_x,
                    'y': self.start_y + offset_y
                })
            except (se.CoordinateError, AttributeError):
                pass

        steps = max(abs(self.end_x - self.start_x), abs(self.end_y - self.start_y), 1)
        dx = (self.end_x - self.start_x) / steps
        dy = (self.end_y - self.start_y) / steps

        for step in range(int(steps)):
            for p in particles:
                try:
                    new_x = int(self.start_x + dx * step + random.randint(-1, 1))
                    new_y = int(self.start_y + dy * step + random.randint(-1, 1))
                    move_x = new_x - p['x']
                    move_y = new_y - p['y']
                    p['obj'].move(move_x, move_y)
                    p['x'] = new_x
                    p['y'] = new_y
                except (se.CoordinateError, AttributeError):
                    pass

            self.map.show()
            time.sleep(SPEED_OF_TIME * 0.05)

        for p in particles:
            try:
                p['obj'].remove()
            except (AttributeError, ValueError):
                pass


class EffectivityIndicator:
    """Visual indicator for attack effectiveness."""

    def __init__(self, x: int, y: int, _map: se.Map, effectiveness: float):
        self.x = x
        self.y = y
        self.map = _map
        self.effectiveness = effectiveness

        if effectiveness > 1:
            self.text = "SUPER!"
            self.color = Color.green + Color.thicc
        elif effectiveness < 1:
            self.text = "WEAK..."
            self.color = Color.red
        else:
            self.text = ""
            self.color = Color.white

        self.text_obj = se.Text(self.text, esccode=self.color, state="float")
        self.added = False

    def play(self, duration: float = 0.5):
        """Display effectiveness indicator."""
        if not self.text:
            return

        try:
            self.text_obj.add(self.map, self.x, self.y)
            self.added = True
        except (se.CoordinateError, AttributeError):
            return

        self.map.show()
        time.sleep(SPEED_OF_TIME * duration)

        if self.added:
            try:
                self.text_obj.remove()
            except (AttributeError, ValueError):
                pass


def get_animation_intensity(damage: int, attack_factor: float) -> AnimationIntensity:
    """Determine animation intensity based on damage dealt."""
    effective_power = damage * attack_factor
    if effective_power <= 2:
        return AnimationIntensity.WEAK
    elif effective_power <= 5:
        return AnimationIntensity.NORMAL
    elif effective_power <= 10:
        return AnimationIntensity.STRONG
    else:
        return AnimationIntensity.CRITICAL


class BattleAnimator:
    """Coordinates all battle animations for a single attack sequence."""

    def __init__(self, _map: se.Map):
        self.map = _map

    def play_attack_animation(
        self,
        attacker: "Poke",
        defender: "Poke",
        attack: "Attack",
        damage: int,
        effectiveness: float,
        is_miss: bool = False
    ):
        """Play the complete attack animation sequence.

        Args:
            attacker: The attacking Poke
            defender: The defending Poke
            attack: The Attack used
            damage: Damage dealt
            effectiveness: Attack effectiveness multiplier
            is_miss: Whether the attack missed
        """
        if not hasattr(defender, 'ico') or not hasattr(defender.ico, 'x'):
            return

        type_name = attack.type.name if hasattr(attack, 'type') else "normal"
        intensity = get_animation_intensity(damage, attack.factor)

        # Play hit flash on defender
        if not is_miss and damage > 0:
            hit_flash = HitFlash(defender.ico, self.map, type_name)
            hit_flash.play()

        # Calculate damage number position (above defender icon)
        dmg_x = defender.ico.x + defender.ico.width // 2
        dmg_y = defender.ico.y - 1

        # Play damage number
        is_critical = effectiveness > 1.2 and damage > 5
        damage_num = DamageNumber(
            0 if is_miss else damage,
            dmg_x,
            max(1, dmg_y),
            self.map,
            is_critical=is_critical
        )
        damage_num.play(duration=0.5)

        # Play effectiveness indicator
        if not is_miss and effectiveness != 1:
            eff_indicator = EffectivityIndicator(
                dmg_x - 2,
                max(1, dmg_y - 1),
                self.map,
                effectiveness
            )
            eff_indicator.play(duration=0.4)

        # Screen shake for strong attacks
        if intensity in (AnimationIntensity.STRONG, AnimationIntensity.CRITICAL):
            screen_shake = ScreenShake(self.map, intensity)
            screen_shake.play()

    def play_status_effect_animation(
        self,
        target: "Poke",
        effect_name: str,
        is_applied: bool = True
    ):
        """Play animation for status effect application or removal.

        Args:
            target: The affected Poke
            effect_name: Name of the status effect
            is_applied: True if effect is being applied, False if removed
        """
        if not hasattr(target, 'ico') or not hasattr(target.ico, 'x'):
            return

        indicator = StatusEffectIndicator(
            effect_name,
            target.ico.x + target.ico.width // 2,
            target.ico.y - 1,
            self.map,
            is_applied
        )
        indicator.play()

    def play_heal_animation(self, target: "Poke", heal_amount: int):
        """Play healing animation.

        Args:
            target: The healed Poke
            heal_amount: Amount of HP healed
        """
        if not hasattr(target, 'ico') or not hasattr(target.ico, 'x'):
            return

        dmg_x = target.ico.x + target.ico.width // 2
        dmg_y = target.ico.y - 1

        damage_num = DamageNumber(
            heal_amount,
            dmg_x,
            max(1, dmg_y),
            self.map,
            is_heal=True
        )
        damage_num.play(duration=0.6)


if __name__ == "__main__":
    print("\033[31;1mDo not execute this!\033[0m")
