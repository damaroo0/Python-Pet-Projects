# main.py
# Import necessary libraries
import json
import random

# Class for generating a map using Binary Space Partitioning (BSP) algorithm
class MapGenerator:
    def __init__(self) -> None:
        # Current split direction
        self.current_direction = 'vertical'

        # Split elements configuration
        self.split_elements = data.get("map_elements").get("split_elements")

        # 
        self.subspace_stack = []

        # Recursion depth variables
        self.max_recursion_depth = 1


    # Function to prompt the user to choose a difficulty level
    def level_check(self):
        available_levels = list(data.get('difficulty_level', {}).keys())
        try:
            while True:
                self.difficulty_level = input("Choose a difficulty level: ").lower()
                if self.difficulty_level in available_levels:
                    break
                else:
                    print(f"We don't have your chosen level. You can choose one from: {available_levels}")
        except KeyboardInterrupt:
            print("\nUser interrupted the program.")
        except Exception as e:
            print(f"An error occurred: {e}")


    # Function to retrieve data for the chosen difficulty level
    def get_data_for_level(self):
        self.difficulty_data = data["difficulty_level"].get(self.difficulty_level, {})

        # Extracting map size and partition size parameters
        self.map_size = self.difficulty_data.get("map_size", None)
        self.min_partition_size = self.difficulty_data.get("min_partition_size", None)

        # Extracting split ratio and random factor parameters
        self.split_ratio = self.difficulty_data.get("split_ratio", None)
        self.random_factor = self.difficulty_data.get("random_factor", None)


    # Function to initialize the map array
    def render_map(self):
        # Map generation
        self.map_array = [["0" for _ in range(self.map_size['end_x'] + 2)] for _ in range(self.map_size['end_y'] + 2)]

        # clear subspace_stuck
        self.subspace_stack = []


    # Function to modify map elements for visualization
    def modify_map_elements(self):
        width = self.map_size['end_x'] + 2 
        height = self.map_size['end_y'] + 2

        boundary = data["map_elements"].get("boundary")

        # Create horizontal and vertical elements
        for i in range(width):
            # Horizontal 
            self.map_array[0][i] = self.map_array[height - 1][i] = boundary.get("horizontal", 2)
            if 0 < i < height - 1:
                # Vertical
                self.map_array[i][0] = self.map_array[i][width - 1] = boundary.get("vertical", 1)

        # Set corner elements
        self.map_array[0][0] = boundary.get("lu_corner", 4)
        self.map_array[height - 1][0] = boundary.get("ll_corner", 4)

        self.map_array[0][width - 1] = boundary.get("ru_corner", 4)
        self.map_array[height - 1][width - 1] = boundary.get("rl_corner", 4)


    # Recursive function for BSP splitting
    def bsp_spliting(self, current_space, depth=0):
        if depth < self.max_recursion_depth:
            if self.current_direction == 'vertical':
                self.vertical_split(current_space)
            elif self.current_direction == 'horzontal':
                self.horizontal_split(current_space)
            else:
                print(f"Cutting direction error. Current diraction is: {self.current_direction}")

            self.subspace_stack.append(current_space)

            self.bsp_spliting(self.subspace_stack[-1], depth + 1)
        else:
            current_space = self.subspace_stack.pop()

            self.bsp_spliting(current_space, depth - 1)


    # Function to check conditions before the split
    def before_split(self, current_space, caller):
        if caller == "vertical":
            if (current_space['end_x'] - current_space['x']) >= (self.difficulty_data["min_partition_size"][0] * 2 + 1):
                return True
        if caller == "horizontal":
            if (current_space['end_y'] - current_space['y']) >= (self.difficulty_data["min_partition_size"][1] * 2 + 1):
                return True


    # Function to check conditions after the split
    def after_split(self, current_space, split_point, caller):
        if caller == "vertical":
            if (current_space['end_x'] - split_point) >= self.difficulty_data["min_partition_size"][0] and (split_point - current_space['x']) >= self.difficulty_data["min_partition_size"][0]:
                return True
        if caller == "horizontal":
            if (current_space['end_y'] - split_point) >= self.difficulty_data["min_partition_size"][1] and (split_point - current_space['y']) >= self.difficulty_data["min_partition_size"][1]:
                return True


    # Function for vertical split
    def vertical_split(self, current_space):
        try:
            if self.before_split(current_space, "vertical") is True:
                split_x = random.randint(current_space['x'], current_space['end_x'])

                if self.after_split(current_space, split_x, "vertical") is True:
                    for i in range(current_space['y'] + 1, current_space['end_y'] + 1):
                        self.map_array[i][split_x] = self.split_elements.get("vertical", "|")

                    self.make_subspaces(current_space, split_x, "vertical")

                    self.current_direction = 'horizontal'
        except Exception as e:
            print(f"An error occurred in vertical_split: {e}")


    # Function for horizontal split
    def horizontal_split(self, current_space):
        try:
            if self.before_split(current_space, "horizontal"):        
                split_y = random.randint(current_space['y'], current_space['end_y'])

            if self.after_split(current_space, split_y, "horizontal"):
                for i in range(current_space['x'] + 1, current_space['end_x'] + 1):
                    self.map_array[split_y][i] = self.split_elements.get("horizontal", "—")

                self.current_direction = 'vertical'
        except Exception as e:
            print(f"An error occurred in horizontal_split: {e}")


    def make_subspaces(self, current_space, split_point, caller):
        if caller == 'vertical':
            subspace_1 = {'x': current_space['x'], 'y': current_space['y'], 'end_x': split_point, 'end_y': current_space['end_y']}
            subspace_2 = {'x': split_point + 1, 'y': current_space['y'], 'end_x': current_space['end_x'], 'end_y': current_space['end_y']}
        if caller == 'horizontal':
            subspace_1 = {'x': current_space['x'], 'y': current_space['y'], 'end_x': current_space['end_x'], 'end_y': split_point}
            subspace_2 = {'x': current_space['x'], 'y': split_point + 1, 'end_x': current_space['end_x'], 'end_y': current_space['end_y']}


    # Function for visualization
    def vizualization(self): 
        for row in self.map_array:
            print(' '.join(map(str, row)))


# Main part of the script
if __name__ == '__main__':
    # Read data from data.json
    with open("BSP_test\data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Create MapGenerator instance
    mapg = MapGenerator()

    # Prompt user to choose a difficulty level
    mapg.level_check()

    # Retrieve data for the chosen difficulty level
    mapg.get_data_for_level()

    # Initialize the map array
    mapg.render_map()

    # Perform BSP splitting
    mapg.bsp_spliting(mapg.map_size)

    # Modify map elements for visualization
    mapg.modify_map_elements()

    # Display the final map
    mapg.vizualization()
