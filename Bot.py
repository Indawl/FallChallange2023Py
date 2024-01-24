import copy

import Properties
from Drone import Drone, BlipType
from Fish import Fish, FishColor, FishKind
from GameAction import GameAction
from GameState import GameState
from RectangleRange import RectangleRange
from Vector import Vector


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

        # Initialize positions
        self.find_start_positions(self.__state)

    def read_state(self) -> GameState:
        state = copy.deepcopy(self.__state)

        # Score
        state.score = int(input()), int(input())

        # Scans
        for player_id in range(2):
            state.scans[player_id].clear()
            for i in range(int(input())):
                state.scans[player_id].add(int(input()))

        # Drones
        for player_id in range(2):
            for i in range(int(input())):
                inputs = [int(s) for s in input().split()]

                drone_id = inputs[0]
                drone = state.drones.setdefault(drone_id, Drone(drone_id, player_id))
                last_drone = self.__state.drones.get(drone_id)

                drone.position = Vector(inputs[1], inputs[2])
                drone.speed = Vector() if last_drone is None else drone.position - last_drone.position
                drone.motor_on = drone.speed != Vector(0, Properties.DRONE_SINK_SPEED)
                drone.emergency = inputs[3]
                drone.battery = inputs[4]
                drone.Lighting = drone.battery < (Properties.MAX_BATTERY if last_drone is None else last_drone.battery)
                drone.LightRadius = Properties.LIGHT_SCAN_RADIUS if drone.Lighting else Properties.DARK_SCAN_RADIUS

                drone.scans.clear()
                drone.radar_blips.clear()

        # Drone's scans
        for i in range(int(input())):
            drone_id, fish_id = [int(j) for j in input().split()]
            state.drones[drone_id].scans.add(fish_id)

        # Drone's new scans
        if self.__state.drones:
            for drone in state.drones.values():
                drone.new_scans = drone.scans - self.__state.drones.get(drone.drone_id).scans

        # Visible fishes
        state.visible_fishes.clear()

        for i in range(int(input())):
            inputs = [int(s) for s in input().split()]

            fish = state.get_fish(inputs[0])

            fish.position = Vector(inputs[1], inputs[2])
            fish.speed = Vector(inputs[3], inputs[4])
            fish.location = RectangleRange(fish.position, fish.position)

            state.visible_fishes.add(fish.fish_id)

        # Radar blips
        lost_fishes = set(state.fishes.keys())

        for i in range(int(input())):
            inputs = input().split()

            drone = state.drones[int(inputs[0])]
            fish_id = int(inputs[1])

            drone.radar_blips[fish_id] = getattr(BlipType, inputs[2])
            lost_fishes.discard(fish_id)

        # Set lost
        for fish_id in lost_fishes:
            state.lost_fishes[fish_id] = state.fishes.pop(fish_id)

        self.__state = state
        return state

    def get_action(self, state: GameState) -> GameAction:
        pass

    def find_start_positions(self, state: GameState) -> None:
        pass
