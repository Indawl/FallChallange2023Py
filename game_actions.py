from enum import Enum


class GameActionType(Enum):
    LIST, MOVE, WAIT = range(3)


class GameAction:
    __action_type: GameActionType
    text: str

    @property
    def action_type(self) -> GameActionType:
        return self.__action_type

    def __init__(self, action_type: GameActionType):
        """
        Base class for game action
        :param action_type: Type of action
        """
        self.__action_type = action_type
        self.text = ""

    def __str__(self):
        return self.__action_type.name


class GameActionList(GameAction):
    actions: list[GameAction]

    def __init__(self, game_action: GameAction | list[GameAction] = None):
        """
        List of game actions
        :param game_action: Game action or list of game action. Default is empty list
        """
        super().__init__(GameActionType.LIST)
        if game_action is None:
            self.actions = []
        elif isinstance(game_action, list):
            self.actions = game_action
        else:
            self.actions = [game_action]

    def __str__(self):
        return '\n'.join(str(a) for a in self.actions)


class GameActionWait(GameAction):
    light: bool

    def __init__(self, light: bool = False):
        """
        Wait action
        :param light: Light indicator
        """
        super().__init__(GameActionType.WAIT)
        self.light = light

    def __str__(self):
        return super().__str__() + f" {int(self.light)} {self.text}"


class GameActionMove(GameAction):
    position: tuple[int, int]
    light: bool

    def __init__(self, position: tuple[int, int], light: bool = False):
        """
        Move action
        :param position: Move to position
        :param light: Light indicator
        """
        super().__init__(GameActionType.MOVE)
        self.position = position
        self.light = light

    def __str__(self):
        return super().__str__() + f" {self.position} {int(self.light)} {self.text}"
