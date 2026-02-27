"""Tests for the battle animation system."""

import unittest
from unittest.mock import MagicMock
import sys

# Mock all required modules before importing battle_animations
mock_se = MagicMock()
mock_se.Map = MagicMock
mock_se.Text = MagicMock
mock_se.Box = MagicMock
mock_se.CoordinateError = Exception
sys.modules['scrap_engine'] = mock_se

mock_color = MagicMock()
mock_color.Color = type('Color', (), {
    'white': '\033[1;37m',
    'red': '\033[38;5;196m',
    'green': '\033[38;5;70m',
    'yellow': '\033[38;5;226m',
    'blue': '\033[34m',
    'purple': '\033[1;35m',
    'cyan': '\033[1;36m',
    'grey': '\033[1;30m',
    'lightblue': '\033[1;34m',
    'thicc': '\033[1m',
    'brown': '\033[38;5;88m',
    'reset': '\033[0m',
})
sys.modules['pokete'] = MagicMock()
sys.modules['pokete.base'] = MagicMock()
sys.modules['pokete.base.color'] = mock_color
sys.modules['pokete.release'] = MagicMock(SPEED_OF_TIME=0.001)
sys.modules['pokete.classes'] = MagicMock()

# Mock settings
mock_setting = MagicMock()
mock_setting.val = True
mock_settings_func = MagicMock(return_value=mock_setting)
mock_settings_module = MagicMock()
mock_settings_module.settings = mock_settings_func
sys.modules['pokete.classes.settings'] = mock_settings_module

# Now import the module directly by loading the file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "battle_animations",
    "pokete/classes/fight/battle_animations.py"
)
battle_animations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(battle_animations)

AnimationIntensity = battle_animations.AnimationIntensity
TypeEffects = battle_animations.TypeEffects
TYPE_EFFECT_CONFIG = battle_animations.TYPE_EFFECT_CONFIG
get_type_effects = battle_animations.get_type_effects
get_animation_intensity = battle_animations.get_animation_intensity
are_battle_animations_enabled = battle_animations.are_battle_animations_enabled
DamageNumber = battle_animations.DamageNumber
StatusEffectIndicator = battle_animations.StatusEffectIndicator
ScreenShake = battle_animations.ScreenShake
HitFlash = battle_animations.HitFlash
TypeParticles = battle_animations.TypeParticles
EffectivityIndicator = battle_animations.EffectivityIndicator
BattleAnimator = battle_animations.BattleAnimator


class TestAnimationIntensity(unittest.TestCase):
    """Tests for AnimationIntensity enum."""

    def test_intensity_values(self):
        self.assertEqual(AnimationIntensity.WEAK.value, 1)
        self.assertEqual(AnimationIntensity.NORMAL.value, 2)
        self.assertEqual(AnimationIntensity.STRONG.value, 3)
        self.assertEqual(AnimationIntensity.CRITICAL.value, 4)


class TestTypeEffects(unittest.TestCase):
    """Tests for TypeEffects configuration."""

    def test_all_types_have_config(self):
        expected_types = [
            "normal", "fire", "water", "plant", "electro",
            "ground", "stone", "ice", "flying", "poison", "undead"
        ]
        for type_name in expected_types:
            self.assertIn(type_name, TYPE_EFFECT_CONFIG)

    def test_type_effects_have_required_fields(self):
        for type_name, effects in TYPE_EFFECT_CONFIG.items():
            self.assertIsInstance(effects, TypeEffects)
            self.assertIsNotNone(effects.color)
            self.assertIsNotNone(effects.particle_char)
            self.assertIsInstance(effects.impact_chars, list)
            self.assertGreater(len(effects.impact_chars), 0)
            self.assertIsNotNone(effects.trail_char)

    def test_all_chars_are_ascii(self):
        """Verify all characters are ASCII-compatible."""
        for type_name, effects in TYPE_EFFECT_CONFIG.items():
            self.assertTrue(
                effects.particle_char.isascii(),
                f"{type_name} particle_char is not ASCII"
            )
            self.assertTrue(
                effects.trail_char.isascii(),
                f"{type_name} trail_char is not ASCII"
            )
            for char in effects.impact_chars:
                self.assertTrue(
                    char.isascii(),
                    f"{type_name} impact_char '{char}' is not ASCII"
                )


class TestGetTypeEffects(unittest.TestCase):
    """Tests for get_type_effects function."""

    def test_returns_correct_type(self):
        fire_effects = get_type_effects("fire")
        self.assertIsInstance(fire_effects, TypeEffects)

    def test_unknown_type_returns_normal(self):
        unknown_effects = get_type_effects("unknown_type")
        normal_effects = get_type_effects("normal")
        self.assertEqual(unknown_effects.particle_char, normal_effects.particle_char)


class TestGetAnimationIntensity(unittest.TestCase):
    """Tests for get_animation_intensity function."""

    def test_weak_intensity(self):
        result = get_animation_intensity(1, 1.0)
        self.assertEqual(result, AnimationIntensity.WEAK)

    def test_normal_intensity(self):
        result = get_animation_intensity(3, 1.5)
        self.assertEqual(result, AnimationIntensity.NORMAL)

    def test_strong_intensity(self):
        result = get_animation_intensity(5, 1.5)
        self.assertEqual(result, AnimationIntensity.STRONG)

    def test_critical_intensity(self):
        result = get_animation_intensity(10, 2.0)
        self.assertEqual(result, AnimationIntensity.CRITICAL)


class TestAreBattleAnimationsEnabled(unittest.TestCase):
    """Tests for are_battle_animations_enabled function."""

    def test_returns_bool(self):
        result = are_battle_animations_enabled()
        self.assertIsInstance(result, bool)


class TestDamageNumber(unittest.TestCase):
    """Tests for DamageNumber class."""

    def setUp(self):
        self.mock_map = MagicMock()

    def test_init_regular_damage(self):
        dn = DamageNumber(10, 5, 5, self.mock_map)
        self.assertEqual(dn.damage, 10)
        self.assertEqual(dn.x, 5)
        self.assertEqual(dn.y, 5)
        self.assertFalse(dn.is_critical)
        self.assertFalse(dn.is_heal)

    def test_init_heal(self):
        dn = DamageNumber(5, 5, 5, self.mock_map, is_heal=True)
        self.assertTrue(dn.is_heal)

    def test_init_critical(self):
        dn = DamageNumber(20, 5, 5, self.mock_map, is_critical=True)
        self.assertTrue(dn.is_critical)

    def test_init_miss(self):
        dn = DamageNumber(0, 5, 5, self.mock_map)
        self.assertEqual(dn.damage, 0)


class TestStatusEffectIndicator(unittest.TestCase):
    """Tests for StatusEffectIndicator class."""

    def setUp(self):
        self.mock_map = MagicMock()

    def test_effect_colors_defined(self):
        expected_effects = [
            "paralyzation", "sleep", "burning",
            "poison", "confusion", "freezing"
        ]
        for effect in expected_effects:
            self.assertIn(effect, StatusEffectIndicator.EFFECT_COLORS)

    def test_effect_symbols_defined(self):
        expected_effects = [
            "paralyzation", "sleep", "burning",
            "poison", "confusion", "freezing"
        ]
        for effect in expected_effects:
            self.assertIn(effect, StatusEffectIndicator.EFFECT_SYMBOLS)

    def test_effect_symbols_are_ascii(self):
        """Verify all effect symbols are ASCII-compatible."""
        for effect, symbol in StatusEffectIndicator.EFFECT_SYMBOLS.items():
            self.assertTrue(
                symbol.isascii(),
                f"Effect symbol for '{effect}' is not ASCII: '{symbol}'"
            )

    def test_init_applied(self):
        indicator = StatusEffectIndicator("burning", 5, 5, self.mock_map, is_applied=True)
        self.assertTrue(indicator.is_applied)

    def test_init_removed(self):
        indicator = StatusEffectIndicator("burning", 5, 5, self.mock_map, is_applied=False)
        self.assertFalse(indicator.is_applied)


class TestScreenShake(unittest.TestCase):
    """Tests for ScreenShake class."""

    def setUp(self):
        self.mock_map = MagicMock()

    def test_shake_amounts_defined(self):
        shake = ScreenShake(self.mock_map, AnimationIntensity.CRITICAL)
        self.assertIn(AnimationIntensity.WEAK, shake.shake_amounts)
        self.assertIn(AnimationIntensity.NORMAL, shake.shake_amounts)
        self.assertIn(AnimationIntensity.STRONG, shake.shake_amounts)
        self.assertIn(AnimationIntensity.CRITICAL, shake.shake_amounts)

    def test_weak_no_shake(self):
        shake = ScreenShake(self.mock_map, AnimationIntensity.WEAK)
        self.assertEqual(shake.shake_amounts[AnimationIntensity.WEAK], 0)


class TestEffectivityIndicator(unittest.TestCase):
    """Tests for EffectivityIndicator class."""

    def setUp(self):
        self.mock_map = MagicMock()

    def test_super_effective(self):
        indicator = EffectivityIndicator(5, 5, self.mock_map, 1.5)
        self.assertEqual(indicator.text, "SUPER!")

    def test_not_effective(self):
        indicator = EffectivityIndicator(5, 5, self.mock_map, 0.5)
        self.assertEqual(indicator.text, "WEAK...")

    def test_normal_effective(self):
        indicator = EffectivityIndicator(5, 5, self.mock_map, 1.0)
        self.assertEqual(indicator.text, "")


class TestBattleAnimator(unittest.TestCase):
    """Tests for BattleAnimator class."""

    def setUp(self):
        self.mock_map = MagicMock()
        self.animator = BattleAnimator(self.mock_map)

    def test_init(self):
        self.assertEqual(self.animator.map, self.mock_map)

    def test_play_attack_animation_no_ico(self):
        mock_attacker = MagicMock()
        mock_defender = MagicMock()
        del mock_defender.ico
        mock_attack = MagicMock()

        # Should not raise exception
        self.animator.play_attack_animation(
            mock_attacker, mock_defender, mock_attack,
            damage=10, effectiveness=1.0
        )

    def test_play_status_effect_animation_no_ico(self):
        mock_target = MagicMock()
        del mock_target.ico

        # Should not raise exception
        self.animator.play_status_effect_animation(
            mock_target, "burning", is_applied=True
        )

    def test_play_heal_animation_no_ico(self):
        mock_target = MagicMock()
        del mock_target.ico

        # Should not raise exception
        self.animator.play_heal_animation(mock_target, heal_amount=5)


if __name__ == "__main__":
    unittest.main()
