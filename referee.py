import copy

import properties
from decisions import Decision
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

    def remove_to_lost(self) -> None:
        """
        Remove fish if it goes beyond the map
        """
        fishes = [fish for fish in self.state.fishes.values() if fish.kind != FishKind.ANGLER]
        for fish in fishes:
            new_position = fish.position + fish.speed
            if new_position.x < 0 or new_position.x > properties.MAP_SIZE - 1:
                self.state.lost_fishes[fish.fish_id] = self.state.fishes.pop(fish.fish_id)

    def do_scan(self) -> None:
        """
        Scan fish with drones within the lighting radius
        """
        for drone in (drone for drone in self.state.drones.values() if not drone.emergency):
            fishes = (fish for fish in self.state.fishes.values() if fish.fish_id not in drone.scans
                      and fish.fish_id not in self.state.scans[drone.player_id]
                      and fish.position.in_range_vec(drone.position, drone.light_radius))
            for fish in fishes:
                drone.scans.add(fish.fish_id)

    def do_report(self, end: bool = False) -> None:
        """
        Save fish on a surface
        :param end: Save fish anywhere
        """
        scans = set(), set()

        # get union scans
        for drone in self.state.drones.values():
            if drone.position.y <= properties.SURFACE or end:
                scans[drone.player_id] |= drone.scans
                drone.scans.clear()
        # remove already scanned fish
        scans[0] -= self.state.scans[0]
        scans[1] -= self.state.scans[1]

        # determinate first scan (not in enemy drone scans and saved scans)
        scans_bonus = (scans[0] - scans[1] - self.state.scans[1],
                       scans[1] - scans[0] - self.state.scans[0])
        scans[0] -= scans_bonus[0]
        scans[1] -= scans_bonus[1]

        # apply scans
        self.apply_scans(0, scans[0])
        self.apply_scans(1, scans[1])
        self.apply_scans(0, scans_bonus[0], True)
        self.apply_scans(1, scans_bonus[1], True)

    def apply_scans(self, player_id: int, scans: set[int], bonus: bool = False):
        """
        Apply scans to state scans and increase score
        :param player_id: Apply for player
        :param scans: Set of fish id
        :param bonus: It is first scan with bonus
        """
        fishes = map(self.state.get_fish, scans)

        for fish in fishes:
            self.state.scans[player_id].add(fish.fish_id)
            self.state.score[player_id] += properties.REWARDS[fish.kind]
            if bonus:
                self.state.score[player_id] += properties.REWARDS[fish.kind]

        colors = set(fish.color for fish in fishes)
        kinds = set(fish.kind for fish in fishes)
        fishes = map(self.state.get_fish, self.state.scans[player_id])

        for color in colors:
            if len([fish for fish in fishes if fish.color == color]) == 4:
                self.state.score[player_id] += properties.REWARDS_COLOR
                if bonus:
                    self.state.score[player_id] += properties.REWARDS_COLOR

        for kind in kinds:
            if len([fish for fish in fishes if fish.kind == kind]) == 3:
                self.state.score[player_id] += properties.REWARDS_KIND
                if bonus:
                    self.state.score[player_id] += properties.REWARDS_KIND

    def is_game_over(self) -> bool:
        """
        Check if the game is over
        """
        if self.state.turn > properties.MAX_TURN:
            return True

        for drone in self.state.drones.values():
            if drone.scans:
                return False

        fishes = set(fish.fish_id for fish in self.state.fishes.values() if fish.kind != FishKind.ANGLER)
        if fishes <= self.state.scans[0] and fishes <= self.state.scans[1]:
            return True

        return False

    def update_drone(self, decisions: list[Decision]) -> None:
        """
        Update drone position
        :param decisions: List of decisions on how to move drones
        """
        pass

    @staticmethod
    def simulate(state: GameState, decisions: list[Decision]) -> int:
        """
        Simulate state until end of game
        :param state: State for simulation
        :param decisions: List of decisions on how to move drones
        :return: Player score difference at the end of the game
        """
        referee = Referee(copy.deepcopy(state))

        # need to determinate fish speed (because need to kick some fish)
        for fish in referee.state.fishes.values():
            if fish.speed is None:
                fish.speed = Vector()

        # game loop
        while not referee.is_game_over():
            referee.remove_to_lost()
            referee.update_drone(decisions)
            referee.update_positions()
            referee.update_speed()
            referee.do_scan()
            referee.do_report()

        # in end of the game, save all scanned fish
        referee.do_report(True)

        return referee.state.score[0] - referee.state.score[1]
