from math import sqrt

import properties
from game_actions import GameAction, GameActionWait
from game_math import Vector, RectangleRange
from game_objects import GameState, Fish, FishColor, FishKind, Drone, BlipType
from referee import Referee


class Bot:
    state: GameState

    def __init__(self, state: GameState):
        self.state = state

    def get_action(self) -> GameAction:
        if self.state.turn == 1:  # If first turn, define start positions
            self.find_start_positions()
        else:  # else correct it
            self.correct_fish_positions()

        # Update speed for invisible fishes, because we have new drone positions
        referee = Referee(self.state)
        referee.update_speed([fish for fish in self.state.fishes.values() if fish.last_seen > 0])

        # Get best variant


        # Update positions
        referee.update_positions()

        # Return actions
        return GameAction()

    def find_start_positions(self) -> None:
        for fish in self.state.fishes.values():
            if fish.fish_id % 2 == 0:  # without symmetric fish
                # Get symmetric fish
                sfish = self.state.fishes[fish.fish_id + 1]

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
                for drone in self.state.drones.values():
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

    def correct_fish_positions(self) -> None:
        referee = Referee(self.state)

        # Symmetric Fish
        for fish in self.state.fishes.values():
            if fish.last_seen == 0:  # visible
                sfish = self.state.get_symmetric_fish(fish)

                if sfish is not None and sfish.speed is None:
                    sfish.location = fish.location.hsymm(properties.CENTER.x)
                    sfish.position = fish.position.hsymm(properties.CENTER.x)

                    # Check if we have fluence
                    if any(fish.position.in_range_vec(drone.position,
                                                      drone.light_radius if fish.kind == FishKind.ANGLER
                                                      else properties.MOTOR_RANGE)
                           for drone in self.state.drones.values() if not drone.emergency):
                        sfish.speed = Vector()
                        sfish.speed = referee.get_fish_speed(sfish)
                        if sfish.speed.is_zero():
                            sfish.speed = None
                        else:
                            sfish.speed = fish.speed.hsymm()

        # From Enemy Scans
        for drone in self.state.drones.values():
            if drone.player_id == 1:  # enemy
                for fish in (self.state.fishes[fish_id] for fish_id in drone.new_scans):
                    if fish.last_seen > 0:  # invisible
                        # Undefined fish or position not for scan
                        if fish.speed is None or not fish.position.in_range_vec(drone.position, drone.light_radius):
                            fish.location = fish.location.intersect_radius(drone.position, drone.light_radius)
                            fish.position = fish.location.center
                            fish.speed = None

                            # Undefined symmetric fish
                            sfish = self.state.get_symmetric_fish(fish)
                            if sfish is not None and sfish.speed is None:
                                sfish.location = fish.location.hsymm(properties.CENTER.x)
                                sfish.position = fish.position.hsymm(properties.CENTER.x)

        # Correct position from radar
        for fish in self.state.fishes.values():
            if fish.last_seen > 0:  # invisible
                habitat = properties.HABITAT[fish.kind]
                loc = RectangleRange(Vector(0, habitat[0]), Vector(properties.MAP_SIZE - 1, habitat[1]))

                # Radar
                for drone in self.state.drones.values():
                    if drone.player_id == 0:  # my drone
                        loc = loc.intersect(drone.get_range_by_radar(fish.fish_id))

                # Increase location
                fish.location = fish.location.scale(properties.MONSTER_SPEED if fish.kind == FishKind.ANGLER
                                                    else properties.FISH_SPEED).intersect(loc)

                # If fish position in wrong range
                if not fish.location.in_range(fish.position):
                    fish.position = fish.location.intersect_line(fish.position, fish.location.center)
                    fish.speed = None

                # If my light, but I don't see it
                drones = [drone for drone in self.state.drones.values()
                          if drone.player_id == 0 and not drone.emergency
                          and fish.position.in_range_vec(drone.position, drone.light_radius)]
                if any(drones):
                    direction = None

                    # If both drones did not see fish
                    if len(drones) > 1 and drones[1].position != drones[0].position:
                        offset_position = drones[1].position - drones[0].position
                        offset_length2 = offset_position.length2()
                        radius0 = drones[0].light_radius ** 2 / offset_length2
                        radius1 = drones[1].light_radius ** 2 / offset_length2

                        project = (radius0 - radius1) / 2.0 + 0.5
                        cross = sqrt(radius0 - project ** 2) + properties.DELTA_RADIUS

                        fish.position = drones[0].position + offset_position * project
                        direction = offset_position.cross() * cross
                        if not fish.location.in_range(direction + fish.position):
                            direction = offset_position.cross(-1) * cross
                    else:
                        drone = max(drones, key=lambda drone: drone.light_radius)
                        fish.position = drone.position
                        direction = (fish.location.center - drone.position).set_length(
                            drone.light_radius + properties.DELTA_RADIUS)

                    fish.position = (fish.position + direction).round()
                    if not fish.location.in_range(fish.position):
                        fish.position = fish.location.intersect_line(fish.position, fish.location.center)
                    fish.speed = None
