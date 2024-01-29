import copy

import properties
from bot import Bot
from game_math import Vector, RectangleRange
from game_objects import GameState, Fish, FishColor, FishKind, Drone, BlipType


def read_initialize() -> GameState:
    state = GameState()

    for i in range(int(input())):
        inputs = input().split()
        fish = Fish(int(inputs[0]), FishColor(int(inputs[1])), FishKind(int(inputs[2])))
        state.fishes[fish.fish_id] = fish

    return state


def read_state(state: GameState) -> GameState:
    new_state = copy.deepcopy(state)
    new_state.turn += 1

    # Score
    new_state.score = int(input()), int(input())

    # Scans
    for player_id in range(2):
        new_state.scans[player_id].clear()
        for i in range(int(input())):
            new_state.scans[player_id].add(int(input()))

    # Drones
    for player_id in range(2):
        for i in range(int(input())):
            inputs = [int(s) for s in input().split()]

            drone_id = inputs[0]
            drone = new_state.drones.setdefault(drone_id, Drone(drone_id, player_id))
            last_drone = state.drones.get(drone_id)

            drone.position = Vector(inputs[1], inputs[2])
            drone.speed = Vector() if last_drone is None else drone.position - last_drone.position
            drone.motor_on = drone.speed != Vector(0, properties.DRONE_SINK_SPEED)
            drone.emergency = inputs[3]
            drone.battery = inputs[4]
            drone.Lighting = drone.battery < (properties.MAX_BATTERY if last_drone is None else last_drone.battery)
            drone.LightRadius = properties.LIGHT_SCAN_RADIUS if drone.Lighting else properties.DARK_SCAN_RADIUS

            drone.scans.clear()
            drone.radar_blips.clear()

    # Drone's scans
    for i in range(int(input())):
        drone_id, fish_id = [int(j) for j in input().split()]
        new_state.drones[drone_id].scans.add(fish_id)

    # Drone's new scans
    if state.drones:
        for drone in new_state.drones.values():
            drone.new_scans = drone.scans - state.drones.get(drone.drone_id).scans

    # Visible fishes
    for i in range(int(input())):
        inputs = [int(s) for s in input().split()]

        fish = new_state.fishes[inputs[0]]

        fish.position = Vector(inputs[1], inputs[2])
        fish.speed = Vector(inputs[3], inputs[4])
        fish.location = RectangleRange(fish.position, fish.position)
        fish.last_seen = 0

    # Radar blips
    lost_fishes = set(new_state.fishes.keys())

    for i in range(int(input())):
        inputs = input().split()

        drone = new_state.drones[int(inputs[0])]
        fish_id = int(inputs[1])

        drone.radar_blips[fish_id] = getattr(BlipType, inputs[2])
        lost_fishes.discard(fish_id)

    # Set lost
    for fish_id in lost_fishes:
        new_state.lost_fishes[fish_id] = new_state.fishes.pop(fish_id)

    return new_state


# initialize state
state_ = read_initialize()

# game loop
while True:
    state_ = read_state(state_)
    print(Bot.get_action(state_))
