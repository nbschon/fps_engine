import arcade
import arcade.key
import copy
import json
from arcade import color
from enum import Enum, auto
from math import cos, sin, atan2, pi
from typing import Optional

class ScaleFactor(Enum):
    One = 1.0
    OnePtTwoFive = 1.25
    OnePtFive = 1.5
    OnePtSevenFive = 1.75
    Two = 2.0

class Actions(Enum):
    Point = auto()
    Wall = auto()
    SetLeft = auto()

class Export:
    def __init__(self) -> None:
        self.scale_factor: float = 0.0
        self.walls: list[Wall] = []
        self.points: list[tuple[float, float]] = []

class Wall:
    left_x: float
    left_z: float
    right_x: float
    right_z: float
    top: float
    bottom: float
    color: tuple[int, int, int]

    def __init__(self, left_x: float, left_z: float, right_x: float, right_z: float, top: float, bottom: float, color: tuple[int, int, int]=(255, 0, 0)):
        self.left_x = left_x
        self.left_z = left_z
        self.right_x = right_x
        self.right_z = right_z
        self.top = top 
        self.bottom = bottom
        self.color = color

    def reverse(self):
        self.left, self.right = self.right, self.left

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "level editor for fps_engine"

X_COUNT = 90
Y_COUNT = 50
MARGIN = 2

class MyGame(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        arcade.set_background_color(color.DIM_GRAY)
        self.mouse_x = 0
        self.mouse_y = 0
        self.cam_x = 0
        self.cam_y = 0
        self.coord_x = 0
        self.coord_y = 0
        self.rect_width = 10
        self.rect_height = 10
        self.walls: list[Wall] = []
        self.points: list[tuple[float, float]] = []
        self.pan_cam: bool = False
        self.shift_pressed: bool = False
        self.grid_shape_list = arcade.ShapeElementList()
        self.point_shape_list = arcade.ShapeElementList()
        self.line_shape_list = arcade.ShapeElementList()
        self.radius = self.rect_width
        self.node_left: Optional[tuple[float, float]] = None
        self.node_right: Optional[tuple[float, float]] = None
        self.undo_stack: list[Actions] = []
        self.scale_factor: ScaleFactor = ScaleFactor.One

    def setup(self):
        for y in range(Y_COUNT):
            for x in range(X_COUNT):
                center_x = (MARGIN + self.rect_width) * x + MARGIN + self.rect_width // 2
                center_y = (MARGIN + self.rect_height) * y + MARGIN + self.rect_height // 2
                rect = arcade.create_rectangle_filled(
                    center_x + self.cam_x, 
                    center_y + self.cam_y, 
                    self.rect_width, 
                    self.rect_height, 
                    color.BLACK
                )
                self.grid_shape_list.append(rect)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below

        self.grid_shape_list.draw()
        self.point_shape_list.draw()
        self.line_shape_list.draw()

        WIDTH = (self.rect_width + (MARGIN)) * X_COUNT
        arcade.draw_line(0, 0, WIDTH, 0, color.RED)

        # TODO: make this less dumb
        cursor_x = int(self.mouse_x // (self.rect_width + MARGIN)) * (self.rect_width + MARGIN) if self.shift_pressed else self.mouse_x
        cursor_y = int(self.mouse_y // (self.rect_height + MARGIN)) * (self.rect_width + MARGIN) if self.shift_pressed else self.mouse_y

        arcade.draw_rectangle_filled(
            cursor_x,
            cursor_y,
            self.rect_width, 
            self.rect_height, 
            color.RED
        )

        font_size: int = 20
        start_x: int = 10
        start_y: int = SCREEN_HEIGHT - font_size - 10

        # arcade.draw_text(f"mouse x: {self.mouse_x}, mouse y: {self.mouse_y}", start_x, start_y, color.WHITE, 20)
        # arcade.draw_text(f"coord x: {self.coord_x}", start_x, start_y - 30, color.WHITE, 20)
        # arcade.draw_text(f"coord y: {self.coord_y}", start_x, start_y - 60, color.WHITE, 20)
        arcade.draw_text(f"# points: {len(self.points)}", start_x, start_y, color.WHITE, 20)
        arcade.draw_text(f"# lines:  {len(self.line_shape_list)}", start_x, start_y - 30, color.WHITE, 20)

        arcade.draw_text(f"level export scale factor: {self.scale_factor.value}", SCREEN_WIDTH - 360, start_y, color.WHITE, 20)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        temp_points = arcade.ShapeElementList()
        for p in self.points:
            point_col = color.ORANGE if self.node_left == p else color.CYAN
            circle_x, circle_y = p
            point = arcade.create_ellipse_filled(
                circle_x * (self.rect_width + (MARGIN)),# + radius / 2, 
                circle_y * (self.rect_height + (MARGIN)),# + radius / 2, 
                self.radius,
                self.radius,
                point_col
            )
            temp_points.append(point)
        self.point_shape_list = temp_points

        temp_lines = arcade.ShapeElementList()
        for w in self.walls:
            left_x, left_z = w.left_x, w.left_z
            right_x, right_z = w.right_x, w.right_z
            new_left_x = left_x * (self.rect_width + MARGIN)
            new_left_z = left_z * (self.rect_width + MARGIN)
            new_right_x = right_x * (self.rect_width + MARGIN)
            new_right_z = right_z * (self.rect_width + MARGIN)
            line = arcade.create_line(new_left_x, new_left_z, new_right_x, new_right_z, color.RADICAL_RED)
            temp_lines.append(line)
        for w in self.walls:
            left_x = w.left_x * (self.rect_width + MARGIN)
            left_z = w.left_z * (self.rect_width + MARGIN)
            right_x = w.right_x * (self.rect_width + MARGIN)
            right_z = w.right_z * (self.rect_width + MARGIN)

            y = (left_z - right_z)
            x = (left_x - right_x)

            x_0 = (left_x + right_x) / 2
            y_0 = (left_z + right_z) / 2
            rad = atan2(x, y)
            size = 1
            to_deg_num = 180 / size
            to_deg_denom = pi / size
            coeff = to_deg_num / to_deg_denom
            # TODO: actually make this scale appropriately
            x_1 = (x_0 + sin(rad + pi / 2) * coeff)
            y_1 = (y_0 + cos(rad + pi / 2) * coeff)

            normal_line = arcade.create_line(x_0, y_0, x_1, y_1, color.RICH_BRILLIANT_LAVENDER)
            temp_lines.append(normal_line)

        self.line_shape_list = temp_lines

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        match key:
            case arcade.key.Q | arcade.key.ESCAPE if key_modifiers & (arcade.key.MOD_CTRL | arcade.key.MOD_COMMAND):
                arcade.exit()
            case arcade.key.LSHIFT:
                self.shift_pressed = True
            case arcade.key.EQUAL:
                self.rect_width = min(self.rect_width + 2, 40)
                self.rect_height = min(self.rect_height + 2, 40)
            case arcade.key.MINUS:
                self.rect_width = max(self.rect_width - 2, 10)
                self.rect_height = max(self.rect_height - 2, 10)
            case arcade.key.A:
                for w in self.walls:
                    left_x, left_z = w.left
                    right_x, right_z = w.right
                    y = (right_z - left_z)
                    x = (right_x - left_x)
                    rad = atan2(y, x)
                    print(f"rad: {rad}, deg: {(rad * 180) / pi}")
            case arcade.key.C if key_modifiers & (arcade.key.MOD_ALT | arcade.key.MOD_OPTION):
                self.walls.clear()
            case arcade.key.C if key_modifiers & (arcade.key.MOD_CTRL | arcade.key.MOD_COMMAND):
                self.points.clear()
            case arcade.key.C:
                self.walls.clear()
                self.points.clear()
                self.node_left = None
            case arcade.key.Z if key_modifiers & (arcade.key.MOD_CTRL | arcade.key.MOD_COMMAND):
                if len(self.undo_stack) > 0:
                    last_placement = self.undo_stack.pop()
                    match last_placement:
                        case Actions.Point:
                            self.points.pop()
                        case Actions.Wall:
                            self.walls.pop()
                        case Actions.SetLeft:
                            self.node_left = None
                    self.node_left = None
            case arcade.key.S if key_modifiers & (arcade.key.MOD_CTRL | arcade.key.MOD_COMMAND):
                new_walls = copy.deepcopy(self.walls)
                export = Export()
                for nw in new_walls:
                    nw.left_x *= self.scale_factor.value
                    nw.left_z *= self.scale_factor.value
                    nw.right_x *= self.scale_factor.value
                    nw.right_z *= self.scale_factor.value
                    nw.left_x -= X_COUNT / 2
                    nw.left_z -= Y_COUNT / 2
                    nw.right_x -= X_COUNT / 2
                    nw.right_z -= Y_COUNT / 2
                    export.walls.append(nw)
                for p in self.points:
                    l, r = p
                    l -= X_COUNT / 2
                    r -= Y_COUNT / 2
                    l *= (self.scale_factor.value)
                    r *= (self.scale_factor.value)
                    export.points.append((l, r))
                export.scale_factor = self.scale_factor.value
                with open("level.json", "w") as f:
                    json.dump(export, f, default=vars, indent=4)
            case arcade.key.S:
                match self.scale_factor:
                    case ScaleFactor.One:
                        self.scale_factor = ScaleFactor.OnePtTwoFive
                    case ScaleFactor.OnePtTwoFive:
                        self.scale_factor = ScaleFactor.OnePtFive
                    case ScaleFactor.OnePtFive:
                        self.scale_factor = ScaleFactor.OnePtSevenFive
                    case ScaleFactor.OnePtSevenFive:
                        self.scale_factor = ScaleFactor.Two
                    case ScaleFactor.Two:
                        self.scale_factor = ScaleFactor.One
            case arcade.key.O if key_modifiers & (arcade.key.MOD_CTRL | arcade.key.MOD_COMMAND):
                if not self.points and not self.walls:
                    try:
                        with open("level.json") as f:
                            d = json.load(f)
                            scale_factor: float = d["scale_factor"]
                            walls: list[Wall] = []
                            for w in d["walls"]:
                                wc = Wall(**w)
                                wc.left_x += X_COUNT / 2
                                wc.left_z += Y_COUNT / 2
                                wc.right_x += X_COUNT / 2
                                wc.right_z += Y_COUNT / 2
                                wc.left_x /= scale_factor
                                wc.left_z /= scale_factor
                                wc.right_x /= scale_factor
                                wc.right_z /= scale_factor
                                walls.append(wc)
                            points: list[tuple[float, float]] = []
                            for pt in d["points"]:
                                l, r = pt
                                l /= scale_factor
                                r /= scale_factor
                                l += X_COUNT / 2
                                r += Y_COUNT / 2
                                points.append((l, r))
                            print(f"sf: {scale_factor:.2}")
                            print(f"walls: {walls}")
                            print(f"pts: {points}")
                            self.walls = walls
                            self.points = points
                    except KeyError:
                        print("bad level format!")

            case _:
                pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        match key:
            case arcade.key.LSHIFT:
                self.shift_pressed = False
            case _:
                pass

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """
        self.mouse_x = x
        self.mouse_y = y
        self.coord_x = int((x - self.cam_x) // (self.rect_width + MARGIN)) if self.shift_pressed else (x - self.cam_x) / (self.rect_width + MARGIN)
        self.coord_y = int((y - self.cam_y) // (self.rect_height + MARGIN)) if self.shift_pressed else (y - self.cam_y) / (self.rect_height + MARGIN)

        if self.pan_cam:
            self.cam_x += dx
            self.cam_y += dy

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        match button:
            case arcade.MOUSE_BUTTON_LEFT:
                # self.coord_x = (x - self.cam_x) // self.rect_width if self.shift_pressed else (x - self.cam_x) / self.rect_width
                # self.coord_y = (y - self.cam_y) // self.rect_height if self.shift_pressed else (x - self.cam_x) / self.rect_width
                add_point: bool = True
                for p in self.points:
                    c_x, c_z = p
                    left_bound = c_x - 1.0
                    right_bound = c_x + 1.0
                    bottom_bound = c_z - 1.0
                    top_bound = c_z + 1.0
                    is_x_aligned = left_bound <= self.coord_x <= right_bound
                    is_y_aligned = bottom_bound <= self.coord_y <= top_bound
                    if is_x_aligned and is_y_aligned:
                        if key_modifiers & (arcade.key.MOD_CTRL | arcade.key.MOD_COMMAND):
                            self.points.remove(p)
                            return
                        else:
                            add_point = False
                            # print(f"p x: {c_x}, p z: {c_z}, coord x: {self.coord_x}, coord y: {self.coord_y}")
                            if self.node_left is None:
                                # print("setting left node")
                                self.node_left = p
                                self.undo_stack.append(Actions.SetLeft)
                            else:
                                # print("creating line")

                                left_x, left_z = self.node_left

                                self.walls.append(Wall(c_x, c_z, left_x, left_z, 5.0, 0.0))
                                self.node_left = None
                                self.undo_stack.append(Actions.Wall)

                if add_point:
                    self.points.append((float(self.coord_x), float(self.coord_y)))
                    self.undo_stack.append(Actions.Point)
                    # print(f"screen x: {x}, screen y: {y}, coord x: {self.coord_x}, coord y: {self.coord_y}")
            case arcade.MOUSE_BUTTON_RIGHT:
                self.node_left = None

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        match button:
            case arcade.MOUSE_BUTTON_RIGHT:
                self.pan_cam = False

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
