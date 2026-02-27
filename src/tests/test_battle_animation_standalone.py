"""Standalone tests for the battle animation system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from unittest.mock import Mock, MagicMock, patch

from pokete.classes.battle_animation import (
    AnimationType,
    AnimationFrame,
    DamageNumberDisplay,
    StatusEffectAnimation,
    AttackAnimationSystem,
    battle_animations,
)
from pokete.base.color import Color


class MockMap:
    """Mock map for testing animations."""

    def __init__(self, width=80, height=24):
        self.width = width
        self.height = height
        self.show_called = 0

    def show(self):
        self.show_called += 1


class MockIcon:
    """Mock icon for testing."""

    def __init__(self, x=10, y=5, width=10, height=4):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.map = MockMap()


class TestAnimationType(unittest.TestCase):
    def test_animation_types_exist(self):
        self.assertEqual(AnimationType.PHYSICAL.value, "physical")
        self.assertEqual(AnimationType.PROJECTILE.value, "projectile")
        self.assertEqual(AnimationType.EFFECT.value, "effect")
        self.assertEqual(AnimationType.BUFF.value, "buff")
        self.assertEqual(AnimationType.DEBUFF.value, "debuff")
        self.assertEqual(AnimationType.ELEMENTAL.value, "elemental")


class TestAnimationFrame(unittest.TestCase):
    def test_frame_creation(self):
        frame = AnimationFrame(
            chars=["*", "X", "*"],
            duration=0.1,
            color=Color.red,
            x_offset=1,
            y_offset=-1
        )
        self.assertEqual(frame.chars, ["*", "X", "*"])
        self.assertEqual(frame.duration, 0.1)
        self.assertEqual(frame.color, Color.red)
        self.assertEqual(frame.x_offset, 1)
        self.assertEqual(frame.y_offset, -1)

    def test_frame_default_values(self):
        frame = AnimationFrame(chars=["o"], duration=0.5)
        self.assertEqual(frame.color, "")
        self.assertEqual(frame.x_offset, 0)
        self.assertEqual(frame.y_offset, 0)


class TestDamageNumberDisplay(unittest.TestCase):
    def setUp(self):
        self.display = DamageNumberDisplay()
        self.mock_map = MockMap()

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_normal_damage(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.display.show(self.mock_map, 10, 5, 25)

        mock_text.assert_called()
        args = mock_text.call_args
        self.assertEqual(args[0][0], "25")

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_critical_damage(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.display.show(self.mock_map, 10, 5, 50, is_critical=True)

        mock_text.assert_called()
        args = mock_text.call_args
        self.assertEqual(args[0][0], "50!")

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_heal(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.display.show(self.mock_map, 10, 5, 15, is_heal=True)

        mock_text.assert_called()
        args = mock_text.call_args
        self.assertEqual(args[0][0], "+15")

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_miss(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.display.show(self.mock_map, 10, 5, 0, is_miss=True)

        mock_text.assert_called()
        args = mock_text.call_args
        self.assertEqual(args[0][0], "MISS")


class TestStatusEffectAnimation(unittest.TestCase):
    def setUp(self):
        self.status_anim = StatusEffectAnimation()
        self.mock_map = MockMap()
        self.mock_ico = MockIcon()
        self.mock_ico.map = self.mock_map

    def test_effect_visuals_defined(self):
        expected_effects = [
            "paralyzation", "sleep", "burning",
            "poison", "confusion", "freezing"
        ]
        for effect in expected_effects:
            self.assertIn(effect, self.status_anim.EFFECT_VISUALS)
            visual = self.status_anim.EFFECT_VISUALS[effect]
            self.assertIn("char", visual)
            self.assertIn("color", visual)
            self.assertIn("pattern", visual)

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_play_effect_applied_unknown_effect(self, mock_sleep, mock_text):
        # Should not raise for unknown effect
        self.status_anim.play_effect_applied(
            self.mock_map, self.mock_ico, "unknown_effect"
        )
        mock_text.assert_not_called()

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_play_paralyzation_effect(self, mock_sleep, mock_text):
        mock_obj = MagicMock()
        mock_text.return_value = mock_obj

        self.status_anim.play_effect_applied(
            self.mock_map, self.mock_ico, "paralyzation"
        )

        # Spark animation should create multiple text objects
        self.assertTrue(mock_text.called)


class TestAttackAnimationSystem(unittest.TestCase):
    def setUp(self):
        self.anim_system = AttackAnimationSystem()
        self.mock_map = MockMap()
        self.attacker_ico = MockIcon(x=5, y=10)
        self.defender_ico = MockIcon(x=50, y=5)
        self.attacker_ico.map = self.mock_map
        self.defender_ico.map = self.mock_map

    def test_type_colors_defined(self):
        expected_types = [
            "normal", "fire", "water", "plant", "electro",
            "ice", "ground", "stone", "flying", "undead", "poison"
        ]
        for type_name in expected_types:
            self.assertIn(type_name, self.anim_system.TYPE_COLORS)

    def test_type_chars_defined(self):
        expected_types = [
            "normal", "fire", "water", "plant", "electro",
            "ice", "ground", "stone", "flying", "undead", "poison"
        ]
        for type_name in expected_types:
            self.assertIn(type_name, self.anim_system.TYPE_CHARS)

    def test_get_type_color_known(self):
        color = self.anim_system.get_type_color("fire")
        self.assertEqual(color, Color.thicc + Color.red)

    def test_get_type_color_unknown(self):
        color = self.anim_system.get_type_color("unknown")
        self.assertEqual(color, Color.white)

    def test_get_type_char_known(self):
        char = self.anim_system.get_type_char("water")
        self.assertEqual(char, "o")

    def test_get_type_char_unknown(self):
        char = self.anim_system.get_type_char("unknown")
        self.assertEqual(char, "*")

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_damage(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.anim_system.show_damage(self.mock_map, self.defender_ico, 30)

        mock_text.assert_called()

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_heal(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.anim_system.show_heal(self.mock_map, self.defender_ico, 10)

        mock_text.assert_called()

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_miss(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.anim_system.show_miss(self.mock_map, self.defender_ico)

        mock_text.assert_called()

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_effectiveness_super(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.anim_system.show_effectiveness(self.mock_map, self.defender_ico, 1.3)

        mock_text.assert_called()
        args = mock_text.call_args
        self.assertEqual(args[0][0], "SUPER!")

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_effectiveness_weak(self, mock_sleep, mock_text):
        mock_label = MagicMock()
        mock_text.return_value = mock_label

        self.anim_system.show_effectiveness(self.mock_map, self.defender_ico, 0.5)

        mock_text.assert_called()
        args = mock_text.call_args
        self.assertEqual(args[0][0], "weak")

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_show_effectiveness_normal_no_display(self, mock_sleep, mock_text):
        self.anim_system.show_effectiveness(self.mock_map, self.defender_ico, 1.0)

        mock_text.assert_not_called()

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_play_attack_animation_projectile(self, mock_sleep, mock_text):
        mock_obj = MagicMock()
        mock_text.return_value = mock_obj

        self.anim_system.play_attack_animation(
            self.mock_map, self.attacker_ico, self.defender_ico,
            "fire", "Fireball", "fireball"
        )

        self.assertTrue(mock_text.called)

    @patch('pokete.classes.battle_animation.se.Text')
    @patch('pokete.classes.battle_animation.time.sleep')
    def test_play_attack_animation_impact(self, mock_sleep, mock_text):
        mock_obj = MagicMock()
        mock_text.return_value = mock_obj

        self.anim_system.play_attack_animation(
            self.mock_map, self.attacker_ico, self.defender_ico,
            "normal", "Tackle", "attack"
        )

        self.assertTrue(mock_text.called)


class TestGlobalInstance(unittest.TestCase):
    def test_battle_animations_instance_exists(self):
        self.assertIsInstance(battle_animations, AttackAnimationSystem)

    def test_battle_animations_has_damage_display(self):
        self.assertIsInstance(
            battle_animations.damage_display, DamageNumberDisplay
        )

    def test_battle_animations_has_status_animation(self):
        self.assertIsInstance(
            battle_animations.status_animation, StatusEffectAnimation
        )


if __name__ == "__main__":
    unittest.main()
