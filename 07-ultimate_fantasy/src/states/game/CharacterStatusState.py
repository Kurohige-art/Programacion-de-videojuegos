"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

This file contains the character status and action menus available while
exploring the world, including individual and global healing flows.
"""

from typing import Any, Dict, List

import pygame

import settings
from gale.state import BaseState
from src.gui.Panel import Panel


class CharacterStatusState(BaseState):
    def enter(self, play_state: Any, character: Any) -> None:
        self.play_state = play_state
        self.character = character
        self.party = play_state.world.party
        self.actions: List[Dict[str, Any]] = list(character.actions)
        self.action_index = len(self.actions)
        self._action_rows = self.actions + [None]

        self.stats_panel = Panel(8, 8, 184, 208)
        self.actions_panel = Panel(200, 8, 176, 208)

    def _is_usable(self, action: Dict[str, Any]) -> bool:
        return action["target_type"] == "character"

    def _enabled_indices(self) -> List[int]:
        return [
            index
            for index, action in enumerate(self._action_rows)
            if action is None or self._is_usable(action)
        ]

    def _move_action(self, direction: int) -> None:
        enabled = self._enabled_indices()
        current = enabled.index(self.action_index) if self.action_index in enabled else 0
        self.action_index = enabled[(current + direction) % len(enabled)]
        settings.SOUNDS["blip"].stop()
        settings.SOUNDS["blip"].play()

    def _confirm_action(self) -> None:
        if self.action_index == len(self.actions):
            self.state_machine.pop()
            return

        action = self.actions[self.action_index]
        if not self._is_usable(action):
            return

        if not action["require_target"]:
            targets = [target for target in self.party.characters.values() if not target.dead]
            start_hp = {target: target.current_hp for target in targets}
            amount = action["func"](self.character, targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()
            self.state_machine.push(
                GlobalHealState(self.state_machine),
                status_state=self,
                targets=targets,
                start_hp=start_hp,
            )
            return

        self.state_machine.push(
            StatusTargetState(self.state_machine),
            status_state=self,
            action=action,
        )

    def _render_text(self, surface, text: str, x: int, y: int,
                     color=(255, 255, 255), font=None, alpha=255) -> None:
        rendered = (font or settings.FONTS["small"]).render(text, True, color)
        if alpha != 255:
            rendered.set_alpha(alpha)
        surface.blit(rendered, (x, y))

    def update(self, dt: float) -> None:
        pass

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self._move_action(-1)
        elif input_id == "move_down":
            self._move_action(1)
        elif input_id == "enter":
            self._confirm_action()

    def render(self, surface) -> None:
        self.stats_panel.render(surface)
        self.actions_panel.render(surface)

        self._render_text(
            surface,
            self.character.name,
            20,
            18,
            font=settings.FONTS["medium"],
        )
        rows = [
            f"Class: {self.character.klass}",
            f"Level: {self.character.level}",
            f"EXP: {self.character.current_exp:.0f}/{self.character.exp_to_level:.0f}",
            f"HP: {self.character.current_hp:.0f}/{self.character.hp:.0f}",
            f"Attack: {self.character.attack:.0f}",
            f"Defense: {self.character.defense:.0f}",
            f"Magic: {self.character.magic:.0f}",
            f"Status: {'Fainted' if self.character.dead else 'Healthy'}",
        ]
        for index, row in enumerate(rows):
            self._render_text(surface, row, 20, 48 + index * 18)

        self._render_text(surface, "Actions", 216, 18, font=settings.FONTS["medium"])
        for index, action in enumerate(self._action_rows):
            label = "Return" if action is None else action["name"]
            enabled = action is None or self._is_usable(action)
            color = (255, 255, 255) if enabled else (128, 128, 128)
            alpha = 255 if enabled else 110
            y = 52 + index * 24
            self._render_text(surface, label, 232, y, color=color, alpha=alpha)
            if enabled and index == self.action_index:
                surface.blit(settings.TEXTURES["cursor-right"], (216, y + 2))


class StatusTargetState(BaseState):
    def enter(self, status_state: CharacterStatusState, action: Dict[str, Any]) -> None:
        self.status_state = status_state
        self.action = action
        self.targets = [
            target
            for target in status_state.party.characters.values()
            if not target.dead and target.current_hp < target.hp
        ]
        self.current_selection = 0
        self.return_index = len(self.targets)
        self.selection = self.return_index if not self.targets else 0
        self.animating = False
        self.animation_time = 0.0
        self.animation_duration = 0.5
        self.animation_start = 0.0
        self.animation_end = 0.0

    def _move(self, direction: int) -> None:
        count = len(self.targets) + 1
        self.selection = (self.selection + direction) % count

    def _resolve(self) -> None:
        if self.selection == self.return_index:
            self.state_machine.pop()
            return

        target = self.targets[self.selection]
        self.animation_start = target.current_hp
        amount = self.action["func"](
            self.status_state.character, target, self.action.get("strength")
        )
        self.animation_end = target.current_hp
        self.animation_time = 0.0
        self.animating = True
        self.current_selection = self.selection

        settings.SOUNDS[self.action["sound_effect"]].play()

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self._move(-1)
        elif input_id == "move_down":
            self._move(1)
        elif input_id == "enter":
            self._resolve()

    def update(self, dt: float) -> None:
        if self.animating:
            self.animation_time += dt
            if self.animation_time >= self.animation_duration:
                self.animation_time = self.animation_duration
                self.animating = False
                self.targets = [
                    target
                    for target in self.status_state.party.characters.values()
                    if not target.dead and target.current_hp < target.hp
                ]
                self.return_index = len(self.targets)
                self.selection = min(self.selection, self.return_index)

    def render(self, surface) -> None:
        panel = Panel(40, 28, 304, 168)
        panel.render(surface)
        font = settings.FONTS["small"]
        title = font.render("Choose character to heal", True, (255, 255, 255))
        surface.blit(title, title.get_rect(centerx=settings.VIRTUAL_WIDTH / 2, y=40))

        for index, target in enumerate(self.targets):
            hp = target.current_hp
            if index == self.current_selection and self.animating:
                progress = self.animation_time / self.animation_duration
                hp = self.animation_start + (
                    self.animation_end - self.animation_start
                ) * progress
            row = f"{target.name}: {hp:.0f}/{target.hp:.0f}"
            color = (255, 255, 255)
            y = 72 + index * 24
            surface.blit(font.render(row, True, color), (88, y))
            if index == self.selection:
                surface.blit(settings.TEXTURES["cursor-right"], (72, y + 2))

        return_y = 72 + len(self.targets) * 24
        surface.blit(font.render("Return", True, (255, 255, 255)), (88, return_y))
        if self.selection == self.return_index:
            surface.blit(settings.TEXTURES["cursor-right"], (72, return_y + 2))


class GlobalHealState(BaseState):
    def enter(
        self,
        status_state: CharacterStatusState,
        targets: List[Any],
        start_hp: Dict[Any, float],
    ) -> None:
        self.status_state = status_state
        self.targets = targets
        self.start_hp = start_hp
        self.duration = 0.8
        self.elapsed = 0.0

    def update(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.state_machine.pop()

    def on_input(self, input_id: str, input_data: Any) -> None:
        pass

    def render(self, surface) -> None:
        panel = Panel(28, 20, 328, 184)
        panel.render(surface)
        font = settings.FONTS["small"]
        title = font.render("Global Heal", True, (255, 255, 255))
        surface.blit(title, title.get_rect(centerx=settings.VIRTUAL_WIDTH / 2, y=34))

        progress = min(self.elapsed / self.duration, 1.0)
        for index, target in enumerate(self.targets):
            start = self.start_hp[target]
            hp = start + (target.current_hp - start) * progress
            row = f"{target.name}: {hp:.0f}/{target.hp:.0f}"
            y = 70 + index * 28
            surface.blit(font.render(row, True, (255, 255, 255)), (92, y))

            bar_x, bar_y, bar_width, bar_height = 92, y + 12, 200, 5
            pygame.draw.rect(
                surface,
                (24, 24, 24),
                (bar_x, bar_y, bar_width, bar_height),
            )
            fill_width = int(bar_width * hp / target.hp) if target.hp else 0
            pygame.draw.rect(
                surface,
                (189, 32, 32),
                (bar_x, bar_y, fill_width, bar_height),
            )