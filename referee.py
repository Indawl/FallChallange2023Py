import properties
from game_math import Vector
from game_objects import GameState, Fish, FishKind


class Referee:
    state: GameState

    def __init__(self, state: GameState):
        self.state = state

    @staticmethod
    def snap_to_fish_zone(kind: FishKind, position: Vector) -> Vector:
        """
        Prevents fish from leaving their habitat
        """
        habitat = properties.HABITAT[kind]

        if position.x < 0:
            position = Vector(0, position.y)
        elif position.x > properties.MAP_SIZE - 1:
            position = Vector(properties.MAP_SIZE - 1, position.y)
        if position.y < habitat[0]:
            position = Vector(position.x, habitat[0])
        elif position.y > habitat[1]:
            position = Vector(position.x, habitat[1])

        return position

    def update_positions(self, fishes: list[Fish] = None) -> None:
        """
        Update position for fishes
        :param fishes: List of fish for update position in state.
        Default is all swimming fishes
        """
        if fishes is None:
            fishes = self.state.fishes.values()

        for fish in fishes:
            if fish.speed is not None:
                fish.position = Referee.snap_to_fish_zone(fish.kind, fish.position + fish.speed)

    def update_speed(self, fishes: list[Fish] = None) -> None:
        """
        Update speed for fishes
        :param fishes: List of fish for update speed in state.
        Default is all swimming fishes
        """
        if fishes is None:
            fishes = self.state.fishes.values()

        for fish in fishes:
            if fish.speed is not None:
                fish.speed = self.get_fish_speed(fish)

    def get_ugly_speed(self, fish: Fish) -> Vector:
        """
        Update speed for ugly
        """
        # Near drone
        drone_positions = fish.position.get_closest(
            [drone.position for drone in self.state.drones.values()
             if not drone.emergency and fish.position.in_range_vec(drone.position, drone.light_radius)])
        if drone_positions:
            pos = sum(drone_positions) / len(drone_positions)
            speed = (fish.position - pos).set_length(properties.MONSTER_ATTACK_SPEED).round()
        else:
            # Near other ugly
            fish_positions = fish.position.get_closest(
                [f.position for f in self.state.fishes.values()
                 if f.speed is not None and f.fish_id != fish.fish_id and f.kind == FishKind.ANGLER and
                 fish.position.in_range_vec(f.position, properties.MIN_DISTANCE_BT_MONSTER)])
            if fish_positions:
                pos = sum(fish_positions) / len(fish_positions)
                # set_length(MONSTER_SPEED) but must repeat error from official referee
                speed = (fish.position - pos).set_length(properties.FISH_SPEED).round()
            elif fish.speed.length() > properties.MONSTER_SPEED:
                speed = fish.speed.set_length(properties.MONSTER_SPEED).round()
            else:
                speed = fish.speed

            # Border
            next_position = fish.position + speed

            habitat = properties.HABITAT[FishKind.ANGLER]
            if next_position.x < 0 or next_position.x > properties.MAP_SIZE - 1:
                speed = speed.hsymm()
            if next_position.y < habitat[0] or next_position.y > habitat[1]:
                speed = speed.vsymm()

        return speed

    def get_fish_speed(self, fish: Fish) -> Vector:
        """
        Update speed for any fish
        """
        # if is ugly, use another algorithm
        # slightly different constants and rounding method
        if fish.kind == FishKind.ANGLER:
            return self.get_ugly_speed(fish)

        # Near drone
        drone_positions = fish.position.get_closest(
            [drone.position for drone in self.state.drones.values()
             if not drone.emergency and fish.position.in_range_vec(drone.position, properties.MOTOR_RANGE)])
        if drone_positions:
            pos = sum(drone_positions) / len(drone_positions)
            speed = (fish.position - pos).set_length(properties.FISH_FRIGHTENED_SPEED).round()
        else:
            # Near fish
            fish_positions = fish.position.get_closest(
                [f.position for f in self.state.fishes.values()
                 if f.speed is not None and f.fish_id != fish.fish_id and f.kind != FishKind.ANGLER and
                 fish.position.in_range_vec(f.position, properties.MIN_DISTANCE_BT_FISH)])
            if fish_positions:
                pos = sum(fish_positions) / len(fish_positions)
                speed = (fish.position - pos).set_length(properties.FISH_SPEED)
            else:
                speed = fish.speed.set_length(properties.FISH_SPEED)

            # Border
            next_position = fish.position + speed

            habitat = properties.HABITAT[fish.kind]
            if next_position.x < 0 or next_position.x > properties.MAP_SIZE - 1:
                speed = speed.hsymm()
            if next_position.y < habitat[0] or next_position.y > habitat[1]:
                speed = speed.vsymm()

            speed = speed.epsilon_round().round()

        return speed
