import GameAction
import GameState
from Fish import Fish, FishColor, FishKind


class Bot:
    __state: GameState

    def read_initialize(self) -> None:
        self.__state = GameState()

        for i in range(int(input())):
            inputs = input().split()
            fish = Fish(int(inputs[0]), FishColor(int(inputs[1])), FishKind(int(inputs[2])))
            if fish.kind == FishKind.ANGLER:
                self.__state.monsters[fish.fish_id] = fish
            else:
                self.__state.fishes[fish.fish_id] = fish

    def read_state(self) -> GameState:
        pass

    # my_score = int(input())
    # foe_score = int(input())
    # my_scan_count = int(input())
    # for i in range(my_scan_count):
    #     creature_id = int(input())
    # foe_scan_count = int(input())
    # for i in range(foe_scan_count):
    #     creature_id = int(input())
    # my_drone_count = int(input())
    # for i in range(my_drone_count):
    #     drone_id, drone_x, drone_y, emergency, battery = [int(j) for j in input().split()]
    # foe_drone_count = int(input())
    # for i in range(foe_drone_count):
    #     drone_id, drone_x, drone_y, emergency, battery = [int(j) for j in input().split()]
    # drone_scan_count = int(input())
    # for i in range(drone_scan_count):
    #     drone_id, creature_id = [int(j) for j in input().split()]
    # visible_creature_count = int(input())
    # for i in range(visible_creature_count):
    #     creature_id, creature_x, creature_y, creature_vx, creature_vy = [int(j) for j in input().split()]
    # radar_blip_count = int(input())
    # for i in range(radar_blip_count):
    #     inputs = input().split()
    #     drone_id = int(inputs[0])
    #     creature_id = int(inputs[1])
    #     radar = inputs[2]

    def get_action(self, state: GameState) -> GameAction:
        pass
