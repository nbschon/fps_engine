import arcade
import arcade.key
from arcade import color
from typing import Optional
import json

class Wall:
    left: tuple[float, float]
    right: tuple[float, float]
    top: float
    bottom: float
    color: tuple[int, int, int]

    def __init__(self, left: tuple[float, float], right: tuple[float, float], top: float, bottom: float, color: tuple[int, int, int]=(255, 0, 0)):
        self.left = left
        self.right = right 
        self.top = top 
        self.bottom = bottom
        self.color = color

    def reverse(self):
        self.left, self.right = self.right, self.left

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "level editor for fps_engine"

X_COUNT = 20
Y_COUNT = 20
MARGIN = 2

class MyGame(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        arcade.set_background_color(color.AMAZON)
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
        self.radius = self.rect_width / 2
        self.node_left: Optional[tuple[float, float]] = None
        self.node_right: Optional[tuple[float, float]] = None

    def setup(self):
        for y in range(Y_COUNT):
            for x in range(X_COUNT):
                # center_x = (x * self.rect_width) + self.rect_width / 2
                # center_y = (y * self.rect_height) + self.rect_height / 2
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

        for p in self.points:
            circle_x, circle_y = p
            arcade.draw_circle_filled(
                circle_x * (self.rect_width + (MARGIN)),# + radius / 2, 
                circle_y * (self.rect_height + (MARGIN)),# + radius / 2, 
                self.rect_width / 2, 
                color.CYAN
            )

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

        arcade.draw_text(f"mouse x: {self.mouse_x}, mouse y: {self.mouse_y}", start_x, start_y, color.WHITE, 20)
        arcade.draw_text(f"coord x: {self.coord_x}", start_x, start_y - 30, color.WHITE, 20)
        arcade.draw_text(f"coord y: {self.coord_y}", start_x, start_y - 60, color.WHITE, 20)
        arcade.draw_text(f"# points: {len(self.points)}", start_x, start_y - 90, color.WHITE, 20)
        arcade.draw_text(f"# lines:  {len(self.line_shape_list)}", start_x, start_y - 120, color.WHITE, 20)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        pass

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        match key:
            case arcade.key.Q | arcade.key.ESCAPE:
                arcade.exit()
            case arcade.key.LSHIFT:
                self.shift_pressed = True
            case arcade.key.EQUAL:
                self.rect_width = min(self.rect_width + 2, 40)
                self.rect_height = min(self.rect_height + 2, 40)
            case arcade.key.MINUS:
                self.rect_width = max(self.rect_width - 2, 10)
                self.rect_height = max(self.rect_height - 2, 10)
            case arcade.key.ENTER:
                print(json.dumps(self.walls))
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
                    if c_x - self.radius <= self.coord_x <= c_x + self.radius and c_z - self.radius <= self.coord_y <= c_z + self.radius:
                        add_point = False
                        print(f"p x: {c_x}, p z: {c_z}, coord x: {self.coord_x}, coord y: {self.coord_y}")
                        if self.node_left is None:
                            print("setting left node")
                            self.node_left = p
                        else:
                            print("creating line")

                            left_x, left_z = self.node_left

                            new_left_x = left_x * (self.rect_width + MARGIN)
                            new_left_z = left_z * (self.rect_width + MARGIN)
                            new_c_x = c_x * (self.rect_width + MARGIN)
                            new_c_z = c_z * (self.rect_width + MARGIN)

                            self.line_shape_list.append(arcade.create_line(new_left_x, new_left_z, new_c_x, new_c_z, color.RADICAL_RED))
                            self.walls.append(Wall((left_x, left_z), (c_x, c_z), 0.5, -0.5))
                            self.node_left = None

                if add_point:
                    self.points.append((float(self.coord_x), float(self.coord_y)))
                    print(f"screen x: {x}, screen y: {y}, coord x: {self.coord_x}, coord y: {self.coord_y}")
            case arcade.MOUSE_BUTTON_RIGHT:
                print("right pressed")
                self.pan_cam = True

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
