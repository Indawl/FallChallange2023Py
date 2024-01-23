from enum import Enum


class GameActionType(Enum):
    LIST, MOVE, WAIT = range(3)


class GameAction:
    action_type: GameActionType
    text: str

    def __init__(self, action_type: GameActionType):
        self.action_type = action_type

    def __str__(self):
        return self.action_type


class GameActionList(GameAction):
    actions: list[GameAction]

    def __init__(self, game_action: GameAction | list[GameAction]):
        super().__init__(GameActionType.LIST)
        if isinstance(game_action, list):
            self.actions = game_action
        else:
            self.actions.append(game_action)

    def __str__(self):
        return '\n'.join(self.actions)


class GameActionWait(GameAction):
    light: bool

    def __init__(self, light: bool):
        super().__init__(GameActionType.WAIT)
        self.light = light

    def __str__(self):
        return super().__str__() + f" {int(self.light)} {self.text}"


class GameActionMove(GameAction):
    position: tuple[int, int]
    light: bool

    def __init__(self, position: tuple[int, int], light: bool):
        super().__init__(GameActionType.MOVE)
        self.position = position
        self.light = light

    def __str__(self):
        return super().__str__() + f" {self.position} {int(self.light)} {self.text}"
