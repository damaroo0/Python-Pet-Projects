# main.py
# import necessary libraries

import json
import random


# generating a map and creating rooms in it
class MapGenerator:
    def __init__(self, json_data, all_end_spaces, map_size):
        self.json_data = json_data
        self.current_direction = "vertical"

        # split elements configuration
        self.split_elements = self.json_data.get("map_elements").get("split_elements")

        # initialize an empty subspace stack and set maximum recursion depth
        self.subspace_stuck = []
        self.max_recursion_depth = 0

        #
        self.all_end_spaces = all_end_spaces

        # initialize map settings
        self.difficulty_level = None
        self.map_array = None
        self.random_factor = None
        self.split_ratio = None
        self.min_partition_size = None
        self.map_size = map_size
        self.difficulty_data = None

    # function to prompt the user to choose a difficulty level
    def level_check(self):
        available_levels = list(self.json_data.get("difficulty_level", {}).keys())
        try:
            while True:
                self.difficulty_level = input("Choose a difficulty level: ").lower()
                if self.difficulty_level in available_levels:
                    self.definition_map_settings()
                    self.bsp_splitting(
                        current_space={
                            "x": 0,
                            "y": 0,
                            "end_x": self.map_size["end_x"] + 2,
                            "end_y": self.map_size["end_y"] + 2,
                            "depth": 0,
                        }
                    )
                    break
                print(
                    f"We don't have your chosen level. You can choose one from: {available_levels}"
                )
        except KeyboardInterrupt:
            print("\nUser interrupted the program.")
        except Exception as e:
            print(f"An error occurred: {e}")

    # definition of dependent elements
    def definition_map_settings(self):
        # retrieve data for the chosen difficulty level
        self.difficulty_data = self.json_data["difficulty_level"].get(
            self.difficulty_level, {}
        )

        self.max_recursion_depth = self.difficulty_data.get("max_recursion_depth", 1)

        self.map_size = self.difficulty_data.get("map_size", None)
        self.min_partition_size = self.difficulty_data.get("min_partition_size", None)

        self.split_ratio = self.difficulty_data.get("split_ratio", None)
        self.random_factor = self.difficulty_data.get("random_factor", None)

    def bsp_splitting(self, current_space):
        if current_space["depth"] < self.max_recursion_depth:
            self.splitting(current_space)
        else:
            # adding a finite space to the list of spaces between which there will be rooms
            self.all_end_spaces.append(current_space)
            # remove this space from the list of the binary tree and try to split another space
            if self.subspace_stuck:
                previous_space = self.subspace_stuck.pop()
                self.bsp_splitting(previous_space)
            else:
                print(
                    "The recursive maximum has been reached. Selecting game spaces..."
                )
                GameAreasChooser(
                    self.all_end_spaces, self.json_data, self.map_size
                ).point_relation_to_free_space()

    def splitting(self, current_space):
        x, y, end_x, end_y, depth = current_space.values()
        if self.current_direction == "vertical":
            split_x_point = round(
                x
                + (end_x - x)
                * (
                    self.split_ratio
                    + random.uniform(self.random_factor[0], self.random_factor[1])
                )
            )
            if split_x_point - x and end_x - split_x_point > self.min_partition_size[0]:
                split_y_point = None
                self.make_subspaces(current_space, split_x_point)
            else:
                # because the space cannot be divided, we transfer it as the final format of the finished room
                # we do the same thing in the case of horizontal space division
                current_space["depth"] = self.max_recursion_depth
                self.bsp_splitting(current_space)
        elif self.current_direction == "horizontal":
            split_y_point = round(
                y
                + (end_y - y)
                * (
                    self.split_ratio
                    + random.uniform(self.random_factor[0], self.random_factor[1])
                )
            )
            if split_y_point - y and end_y - split_y_point > self.min_partition_size[1]:
                split_x_point = None
                self.make_subspaces(current_space, split_y_point)
            else:
                current_space["depth"] += 1
                self.bsp_splitting(current_space)
        else:
            print(
                f"Cutting direction error. Current direction is: {self.current_direction}"
            )

    def make_subspaces(self, current_space, split_x_point=None, split_y_point=None):
        current_space_copy = current_space.copy()
        current_space_copy["depth"] += 1

        if split_x_point is not None:
            subspace1, subspace2 = current_space_copy.copy(), current_space_copy.copy()
            subspace1["end_x"], subspace2["x"] = split_x_point - 1, split_x_point + 1

            self.subspace_stuck.append(subspace1)
            self.current_direction = "horizontal"
            self.bsp_splitting(subspace2)

        elif split_y_point is not None:
            subspace1, subspace2 = current_space_copy.copy(), current_space_copy.copy()
            subspace1["end_y"], subspace2["y"] = split_y_point - 1, split_y_point + 1

            self.subspace_stuck.append(subspace1)
            self.current_direction = "vertical"
            self.bsp_splitting(subspace2)

        else:
            print("Error: No split points provided")


# creating a chain of passageways between the main rooms
class GameAreasChooser(MapGenerator):
    def __init__(self, all_end_spaces, json_data, map_size):
        super().__init__(json_data, all_end_spaces, map_size)

        self.map_size = map_size
        self.free_spaces = all_end_spaces
        self.game_spaces = []
        self.blocked_spaces = ()

    def point_generation(self):
        return (
            random.randint(self.map_size["x"], self.map_size["end_x"]),
            random.randint(self.map_size["y"], self.map_size["end_y"]),
        )

    def point_relation_to_free_space(self):
        while self.free_spaces:
            point = self.point_generation()
            if len(self.free_spaces) == 1:
                self.game_spaces.append(self.free_spaces[0])
                del self.free_spaces[0]
                print("before else on function")
            else:
                for index, space in enumerate(self.free_spaces):
                    if (
                        space["x"] <= point[0] <= space["end_x"]
                        and space["y"] <= point[1] <= space["end_y"]
                    ):
                        self.game_spaces.append(self.free_spaces[index])
                        del self.free_spaces[index]

                        for block_space_index in self.block_space():
                            del self.free_spaces[block_space_index]
        else:
            print("Play spaces are spelled out. Creating passageways...")
            PassageGeneration(
                self.all_end_spaces, self.json_data, self.map_size
            ).area_picker()

    def block_space(self):
        self.blocked_spaces = ()

        for index, space in enumerate(self.free_spaces):
            if self.game_spaces[-1]["x"] == space["x"] and space["y"] in range(
                self.game_spaces[-1]["y"], self.game_spaces[-1]["end_y"]
            ):
                self.blocked_spaces.append(index)
            elif self.game_spaces[-1]["y"] == space["y"] and space["x"] in range(
                self.game_spaces[-1]["x"], self.game_spaces[-1]["end_x"]
            ):
                self.blocked_spaces.append(index)

            self.blocked_spaces = sorted(self.blocked_spaces)
            self.blocked_spaces = tuple(
                value - index for index, value in enumerate(self.blocked_spaces)
            )

            return self.blocked_spaces


class PassageGeneration(GameAreasChooser):
    def __init__(self, all_end_spaces, json_data, map_size):
        super().__init__(all_end_spaces, json_data, map_size)

        self.max_connection_per_area = self.difficulty_data(
            "max_connection_per_area", None
        )

        self.picked_space1, self.picked_space2 = None, None
        self.used_combination = []
        self.obstacles = []
        self.passages = []

    def area_picker(self):
        while not self.all_spaces_connect():
            index1 = self.game_spaces[random.randint(0, len(self.game_spaces) - 1)]
            index2 = self.game_spaces[random.randint(0, len(self.game_spaces) - 1)]

            if index1 != index2 and (index1, index2) not in self.used_combination:
                if (
                    self.count_connections(index1) < self.max_connection_per_area
                    and self.count_connections(index2) < self.max_connection_per_area
                ):
                    self.used_combination.append((index1, index2))
                    self.choose_side(
                        space1=self.game_spaces[index1], space2=self.game_spaces[index2]
                    )
                else:
                    self.area_picker()
            else:
                self.area_picker()

    def all_spaces_connect(self):
        connected_spaces = set()

        for pair in self.used_combination:
            connected_spaces.add(pair[0])
            connected_spaces.add(pair[1])

        return len(connected_spaces) == len(self.game_spaces)

    def count_connections(self, index):
        return sum(1 for pair in self.used_combination if index in pair)

    def a_star(self, points):
        start_point, end_point = points[0], points[1]
        path = []

        #
        open_notes = [start_point]
        #
        closed_notes = []

        # way cost from start point to current point
        g_score = {start_point: 0}
        # way cost current point to end point
        h_score = {start_point: self.manhattan_distance(start_point, end_point)}
        #
        f_score = {start_point: h_score[start_point]}

        came_from = {}

        while open_notes:
            current_point = min(
                open_notes,
                key=lambda point: self.manhattan_distance(start_point, point)
                + self.manhattan_distance(point, end_point),
            )

            if current_point == end_point:
                path = self.reconstruct_path(came_from, end_point)
                self.passages.append(path)

                return

            open_notes.remove(current_point)
            closed_notes.append(current_point)

            for neighbor_point in self.get_neighbors(current_point):
                if neighbor_point in self.obstacles or neighbor_point in closed_notes:
                    continue

                preliminary_assessment_g_score = g_score.get(current_point) + 1

                if neighbor_point not in open_notes:
                    open_notes.append(neighbor_point)
                elif preliminary_assessment_g_score >= g_score.get(
                    neighbor_point, float("inf")
                ):
                    continue

                came_from[neighbor_point] = current_point
                g_score[neighbor_point] = preliminary_assessment_g_score
                h_score[neighbor_point] = self.manhattan_distance(
                    neighbor_point, end_point
                )
                f_score[neighbor_point] = (
                    g_score[neighbor_point] + h_score[neighbor_point]
                )

        else:
            print("No path found")

    @staticmethod
    def reconstruct_path(came_from, end_point):
        path = [end_point]
        while end_point in came_from:
            end_point = came_from[end_point]
            path.insert(0, end_point)
        return path

    def get_neighbors(self, current_point):
        neighbors = []

        top_neighbor = (current_point[0], current_point[1] - 1)
        if top_neighbor not in self.obstacles:
            neighbors.append(top_neighbor)

        bottom_neighbor = (current_point[0], current_point[1] + 1)
        if bottom_neighbor not in self.obstacles:
            neighbors.append(bottom_neighbor)

        left_neighbor = (current_point[0] - 1, current_point[1])
        if left_neighbor not in self.obstacles:
            neighbors.append(left_neighbor)

        right_neighbor = (current_point[0] + 1, current_point[1])
        if right_neighbor not in self.obstacles:
            neighbors.append(right_neighbor)

        return neighbors

    def choose_side(self, space1, space2):
        open_sides_space1 = self.check_space_sides(space1)
        open_sides_space2 = self.check_space_sides(space2)

        min_distance = float("inf")
        min_distance_sides = None
        for start_side in open_sides_space1:
            for end_side in open_sides_space2:
                start_side_middle_point = (
                    (start_side[0][0] + start_side[1][0]) // 2,
                    (start_side[0][1] + start_side[1][1]) // 2,
                )
                end_side_middle_point = (
                    (end_side[0][0] + end_side[1][0]) // 2,
                    (end_side[0][1] + end_side[1][1]) // 2,
                )

                distance = self.manhattan_distance(
                    start_side_middle_point, end_side_middle_point
                )

                if distance < min_distance:
                    min_distance = distance
                    min_distance_sides = [start_side, end_side]

        self.make_points_on_side(min_distance_sides)

    def check_space_sides(self, space):
        sides = []

        # top side
        if space["x"] != 0:
            sides.append(((space["x"], space["y"]), (space["end_x"], space["y"])))
        # right side
        if space["end_x"] != self.map_size["end_x"]:
            sides.append(
                ((space["end_x"], space["y"]), (space["end_x"], space["end_y"]))
            )
        # left side
        if space["y"] != 0:
            sides.append(((space["x"], space["y"]), (space["x"], space["end_y"])))
        # bottom side
        if space["end_y"] != self.map_size["end_y"]:
            sides.append(
                ((space["x"], space["end_y"]), (space["end_x"], space["end_y"]))
            )

        return sides

    def make_points_on_side(self, sides):
        start_side, end_side = sides[0], sides[1]
        start_side_points = self.points_on_side(
            start_side, self.direction_check(start_side)
        )
        end_side_points = self.points_on_side(end_side, self.direction_check(end_side))

        min_distance = None
        start_end_points = []

        for start_point in start_side_points:
            for end_point in end_side_points:
                distance = self.manhattan_distance(start_point, end_point)

                if distance < min_distance:
                    min_distance = distance
                    start_end_points = (start_point, end_point)
            pass

        self.a_star(start_end_points)

    @staticmethod
    def direction_check(side):
        return "x" if side[0][0] == side[1][0] else "y"

    @staticmethod
    def points_on_side(side, direction):
        points = []
        if direction == "x":
            for x in range(side[0][0] + 3, side[1][0] - 3):
                points.append((x, side[0][1]))
        else:
            for y in range(side[0][1] + 3, side[1][1] - 3):
                points.append((side[0][1], y))
        return points

    # make obstacles points as stop points for A* algorithm
    def obstacles_point(self):
        for area in self.game_spaces:
            # add boundaries of areas
            for y in range(area["y"], area["end_y"] + 1):
                # check if the current point is not on the map boundary
                if (
                    area["x"] != self.map_size["x"]
                    and area["x"] != self.map_size["end_x"]
                ):
                    self.obstacles.append((area["x"], y))
                if (
                    area["end_x"] != self.map_size["x"]
                    and area["end_x"] != self.map_size["end_x"]
                ):
                    self.obstacles.append((area["end_x"], y))

            for x in range(area["x"], area["end_x"] + 1):
                # check if the current point is not on the map boundary
                if (
                    area["y"] != self.map_size["y"]
                    and area["y"] != self.map_size["end_y"]
                ):
                    self.obstacles.append((x, area["y"]))
                if (
                    area["end_y"] != self.map_size["y"]
                    and area["end_y"] != self.map_size["end_y"]
                ):
                    self.obstacles.append((x, area["end_y"]))

            # add boundaries of the map
            for y in range(self.map_size["y"], self.map_size["end_y"] + 1):
                if (self.map_size["x"], y) not in self.obstacles:
                    self.obstacles.append((self.map_size["x"], y))
                if (self.map_size["end_x"], y) not in self.obstacles:
                    self.obstacles.append((self.map_size["end_x"], y))

            for x in range(self.map_size["x"], self.map_size["end_x"] + 1):
                if (x, self.map_size["y"]) not in self.obstacles:
                    self.obstacles.append((x, self.map_size["y"]))
                if (x, self.map_size["end_y"]) not in self.obstacles:
                    self.obstacles.append((x, self.map_size["end_y"]))

    @staticmethod
    def manhattan_distance(point1, point2):
        return abs(point2[0] - point1[0]) + abs(point2[1] - point1[1])


# visualization of the edges / corners of the entire map, for a more pleasant game interface
class MapVisualizer:
    def __init__(self) -> None:
        pass

    # future elements
    # map array generation (visual part) transplanted to Map_visualisation class
    # self.map_array = [['•' for _ in range(self.map_size['end_x'] + 2)] for _ in range(self.map_size['end_y'] + 2)]


# control part
if __name__ == "__main__":
    # read data from data.jsom
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        map_generator = MapGenerator(json_data=data, all_end_spaces=[], map_size=[])
        # prompt user to choose difficulty level and initialize map
        map_generator.level_check()
    except FileNotFoundError:
        print("File .json not found. Please make sure the file path is correct.")
    except Exception as ErrorName:
        print(f"An error occurred: {ErrorName}")
