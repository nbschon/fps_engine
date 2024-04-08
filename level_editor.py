import arcade
from arcade import color

class Wall:
    left: tuple[float, float]
    right: tuple[float, float]
    top: float
    bottom: float

    def __init__(self, left: tuple[float, float], right: tuple[float, float], top: float, bottom: float):
        self.left = left
        self.right = right 
        self.top = top 
        self.bottom = bottom

    def reverse(self):
        self.left, self.right = self.right, self.left

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "level editor for fps_engine"

class MyGame(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        arcade.set_background_color(color.AMAZON)
        self.mouse_x = 0
        self.mouse_y = 0
        self.cam_x = 0
        self.cam_y = 0
        self.rect_width = 10
        self.rect_height = 10
        self.walls: list[Wall] = []
        self.pan_cam: bool = False
        # self.grid = []
        # for row in range(ROW_COUNT):
        #     self.grid.append([])
        #     for _ in range(COL_COUNT):
        #         self.grid[row].append(0)

    def setup(self):
        pass

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        X_COUNT = 20
        Y_COUNT = 50

        # Call draw() on all your sprite lists below
        for y in range(Y_COUNT):
            for x in range(X_COUNT):
                center_x = (x * self.rect_width) - self.rect_width / 2
                center_y = (y * self.rect_height) - self.rect_height / 2
                arcade.draw_rectangle_filled(
                    center_x + 1 + self.cam_x, 
                    center_y + 1 + self.cam_y, 
                    self.rect_width - 2, 
                    self.rect_height - 2, 
                    color.BLACK
                )

        font_size: int = 20
        start_x: int = 10
        start_y: int = SCREEN_HEIGHT - font_size - 10
        arcade.draw_text(f"mouse x: {self.mouse_x}, mouse y: {self.mouse_y}", start_x, start_y, arcade.color.WHITE, 20)

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
            case arcade.key.EQUAL:
                self.rect_width += 2
                self.rect_height += 2
                self.rect_width = min(self.rect_width, 40)
                self.rect_height = min(self.rect_height, 40)
            case arcade.key.MINUS:
                self.rect_width -= 2
                self.rect_height -= 2
                self.rect_width = max(self.rect_width, 10)
                self.rect_height = max(self.rect_height, 10)
            case _:
                pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        self.mouse_x = x
        self.mouse_y = y

        if self.pan_cam:
            self.cam_x += delta_x
            self.cam_y += delta_y

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        match button:
            case arcade.MOUSE_BUTTON_LEFT:
                print(f"x: {x}, y: {y}")
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
