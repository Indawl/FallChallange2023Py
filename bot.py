from math import sqrt

import properties
from game_actions import GameAction
from game_math import Vector, RectangleRange
from game_objects import GameState, Fish, FishColor, FishKind, Drone, BlipType
from referee import Referee


class Bot:
    @staticmethod
    def get_action(state: GameState) -> GameAction:
        if state.turn == 1:  # If first turn, define start positions
            Bot.find_start_positions(state)
        else:  # else correct it
            Bot.correct_fish_positions(state)

        # Update speed for invisible fishes, because we have new drone positions
        referee = Referee(state)
        referee.update_speed([fish for fish in state.fishes.values() if fish.last_seen > 0])

        #

        # Update positions
        referee.update_positions()

        # Return actions
        return GameAction()

    @staticmethod
    def find_start_positions(state: GameState) -> None:
        for fish in state.fishes.values():
            if fish.fish_id % 2 == 0:  # without symmetric fish
                # Get symmetric fish
                sfish = state.fishes[fish.fish_id + 1]

                # Get start location
                if fish.kind == FishKind.ANGLER:
                    fish.location = RectangleRange(
                        Vector(0, properties.MAP_SIZE / 2),
                        Vector(properties.MAP_SIZE - 1, properties.MAP_SIZE - 1))
                else:
                    fish.location = RectangleRange(
                        Vector(1000, properties.HABITAT[fish.kind][0] + 1000),
                        Vector(properties.MAP_SIZE - 1001, properties.HABITAT[fish.kind][1] - 1001))
                sfish.location = fish.location

                # Correct location by radar
                for drone in state.drones.values():
                    if drone.player_id == 0:
                        fish.Location = fish.location.intersect(drone.get_range_by_radar(fish.fish_id))
                        sfish.Location = sfish.location.intersect(drone.get_range_by_radar(sfish.fish_id))

                # Correct by symmetric
                loc = fish.location.intersect(sfish.location.hsymm(properties.CENTER.x))
                sloc = sfish.location.intersect(fish.location.hsymm(properties.CENTER.x))

                # If undefined
                if loc == sloc:
                    if fish.kind == FishKind.ANGLER:
                        loc = RectangleRange(loc.from_, Vector((loc.from_.x + loc.to.x - 1) / 2, loc.to.y))
                        sloc = RectangleRange(Vector(loc.to.x + 1, loc.to.y), sloc.to)
                    else:
                        loc = RectangleRange(loc.from_, loc.from_)
                        sloc = RectangleRange(sloc.to, sloc.to)

                # Set location
                fish.location = loc
                sfish.location = sloc

                # Set position
                fish.position = fish.location.center
                sfish.position = sfish.location.center

    @staticmethod
    def correct_fish_positions(state: GameState) -> None:
        referee = Referee(state)

        # Symmetric Fish
        for fish in state.fishes.values():
            if fish.last_seen == 0:
                sfish = state.get_symmetric_fish(fish)

                if sfish is not None and sfish.speed is None:
                    sfish.location = fish.location.hsymm(properties.CENTER.x)
                    sfish.position = fish.position.hsymm(properties.CENTER.x)

                    # Check if we have fluence
                    if any(not drone.emergency and
                           drone.position.in_range(drone.light_radius if fish.kind == FishKind.ANGLER
                                                   else properties.MOTOR_RANGE)
                           for drone in state.drones.values()):
                        sfish.speed = Vector()
                        sfish.speed = referee.get_fish_speed(sfish)
                        if sfish.speed.is_zero():
                            sfish = None
                        else:
                            sfish.speed = fish.speed.hsymm()

        # From Enemy Scans
        for drone in state.drones.values():
            if drone.player_id == 1:
                for fish in (state.fishes[fish_id] for fish_id in drone.new_scans):
                    if fish.last_seen > 0:
                        # Undefined fish or position not for scan
                        if fish.speed is None or not fish.position.in_range_vec(drone.position, drone.light_radius):
                            fish.location = fish.location.intersect_radius(drone.position, drone.light_radius)
                            fish.position = fish.location.center
                            fish.speed = None

                            # Undefined symmetric fish
                            sfish = state.fishes.get(fish.fish_id)
                            if sfish is not None and sfish.speed is None:
                                sfish.location = fish.location.hsymm(properties.CENTER.x)
                                sfish.position = fish.position.hsymm(properties.CENTER.x)

        # Correct position from radar
        for fish in state.fishes.values():
            if fish.last_seen > 0:
                habitat = properties.HABITAT[fish.kind]
                loc = RectangleRange(Vector(0, habitat[0]), Vector(properties.MAP_SIZE - 1, habitat[1]))

                for drone in state.drones.values():
                    if drone.player_id == 0:
                        loc = loc.intersect(drone.get_range_by_radar(fish.fish_id))

                # Increase location
                fish.location = fish.location.scale(properties.MONSTER_SPEED if fish.kind == FishKind.ANGLER
                                                    else properties.FISH_SPEED).intersect(loc)

                # If fish position in wrong range
                if not fish.location.in_range(fish.position):
                    fish.position = fish.location.intersect_line(fish.position, fish.location.center)
                    fish.speed = None

                # If my light, but I don't see it
                drones = [drone for drone in state.drones.values() if drone.player_id == 0 and
                          not drone.emergency and fish.position.in_range_vec(drone.position, drone.light_radius)]
                if any(drones):
                    direction = None

                # If both drones did not see fish
                if len(drones) > 1 and drones[1].position != drones[0].position:
                    offset_position = drones[1].position - drones[0].position
                    offset_length2 = offset_position.length2()
                    radius2_0 = drones[0].light_radius**2 / offset_length2
                    radius2_1 = drones[1].light_radius**2 / offset_length2

                    project = (radius2_0 - radius2_1) / 2.0 + 0.5
                    cross = sqrt(radius2_0 - project * project) + properties.DELTA_RADIUS

                    fish.position = offset_position * project
                    direction = offset_position.cross() * cross
                    if not fish.location.in_range(direction + fish.position):
                        direction = offset_position.cross(-1) * cross
                else:
                    fish.position = drones[0].position
                    direction = (fish.location.center - drones[0].position).normalize() *\
                                (drones[0].light_radius + properties.DELTA_RADIUS)

                fish.position = (fish.position + direction).round()
                if not fish.location.in_range(fish.position):
                    fish.position = fish.location.intersect_line(fish.position, fish.location.center)
                    fish.speed = None
