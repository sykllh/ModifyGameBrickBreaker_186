
import tkinter as tk
import random

class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 17
        self.direction = [1, -1]
        self.speed = 6
        self.tag = "catball"

        # Telinga kiri
        canvas.create_polygon(
            x-15, y-8,
            x-17, y-25,
            x-3, y-16,
            fill="#ffb6c1", outline="#ffffff",
            width=2, tags=self.tag
        )

        # Telinga kanan
        canvas.create_polygon(
            x+15, y-8,
            x+17, y-25,
            x+3, y-16,
            fill="#ffb6c1", outline="#ffffff",
            width=2, tags=self.tag
        )

        # Wajah kucing
        item = canvas.create_oval(
            x-17, y-17, x+17, y+17,
            fill="#ffb6c1", outline="#ffffff",
            width=2, tags=self.tag
        )

        # Mata
        canvas.create_oval(
            x-10, y-5, x-5, y+1,
            fill="#292044", tags=self.tag
        )
        canvas.create_oval(
            x+5, y-5, x+10, y+1,
            fill="#292044", tags=self.tag
        )

        # Hidung
        canvas.create_polygon(
            x-3, y+5, x+3, y+5, x, y+9,
            fill="#ff69b4", tags=self.tag
        )

        # Kumis kiri
        canvas.create_line(
            x-10, y+7, x-19, y+5,
            fill="white", width=1, tags=self.tag
        )
        canvas.create_line(
            x-10, y+10, x-19, y+12,
            fill="white", width=1, tags=self.tag
        )

        # Kumis kanan
        canvas.create_line(
            x+10, y+7, x+19, y+5,
            fill="white", width=1, tags=self.tag
        )
        canvas.create_line(
            x+10, y+10, x+19, y+12,
            fill="white", width=1, tags=self.tag
        )

        super().__init__(canvas, item)

    def move(self, x, y):
        self.canvas.move(self.tag, x, y)

    def delete(self):
        self.canvas.delete(self.tag)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] <= 0:
            self.direction[0] = 1
        elif coords[2] >= width:
            self.direction[0] = -1

        if coords[1] <= 45:
            self.direction[1] = 1

        self.move(
            self.direction[0] * self.speed,
            self.direction[1] * self.speed
        )

    def collide(self, game_objects):
        for obj in game_objects:

            if isinstance(obj, Paddle):
                if self.direction[1] > 0:
                    ball_coords = self.get_position()
                    paddle_coords = obj.get_position()

                    ball_center = (
                        ball_coords[0] + ball_coords[2]
                    ) / 2

                    paddle_center = (
                        paddle_coords[0] + paddle_coords[2]
                    ) / 2

                    # Pantulan mengikuti posisi tabrakan
                    offset = (
                        ball_center - paddle_center
                    ) / (obj.width / 2)

                    self.direction[0] = offset
                    self.direction[1] = -1

            elif isinstance(obj, Brick):
                if obj.hits > 0:
                    obj.hit()
                    self.direction[1] *= -1

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 110
        self.height = 15

        item = canvas.create_rectangle(
            x-self.width/2, y-self.height/2,
            x+self.width/2, y+self.height/2,
            fill="#ff8fab",
            outline="#ffffff",
            width=2
        )

        super().__init__(canvas, item)

        # Hiasan ikan
        self.decoration = canvas.create_text(
            x, y-2,
            text="🐟",
            font=("Arial", 12)
        )

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)
            self.canvas.move(self.decoration, offset, 0)

class Brick(GameObject):

    COLORS = {
        1: "#ffb3c6",
        2: "#cdb4db",
        3: "#a2d2ff"
    }

    def __init__(self, canvas, x, y, hits):
        self.width = 65
        self.height = 22
        self.hits = hits

        item = canvas.create_rectangle(
            x-self.width/2, y-self.height/2,
            x+self.width/2, y+self.height/2,
            fill=self.COLORS[hits],
            outline="#ffffff",
            width=2,
            tags="brick"
        )

        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1

        if self.hits <= 0:
            self.delete()
        else:
            self.canvas.itemconfig(
                self.item,
                fill=self.COLORS[self.hits]
            )

class Game(tk.Frame):

    def __init__(self, master):
        super().__init__(master)

        self.width = 700
        self.height = 500

        self.lives = 3
        self.score = 0
        self.running = False
        self.started = False
        self.ball = None

        master.title("CAT BREAKOUT - Paws & Bricks")
        master.resizable(False, False)
        master.configure(bg="#17152e")

        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#211d3b",
            highlightthickness=0
        )

        self.canvas.pack()
        self.pack(padx=10, pady=10)

        self.items = {}

        self.draw_background()
        self.create_hud()

        self.paddle = Paddle(
            self.canvas,
            self.width/2,
            445
        )

        self.items[self.paddle.item] = self.paddle

        self.create_bricks()
        self.add_ball()

        self.show_start_screen()

        self.canvas.focus_set()

        self.canvas.bind(
            "<Left>",
            lambda event: self.paddle.move(-25)
        )

        self.canvas.bind(
            "<Right>",
            lambda event: self.paddle.move(25)
        )

        self.canvas.bind(
            "<space>",
            lambda event: self.start_game()
        )

        self.canvas.bind(
            "p",
            lambda event: self.pause_game()
        )

        self.canvas.bind(
            "P",
            lambda event: self.pause_game()
        )

        self.canvas.bind(
            "r",
            lambda event: self.restart_game()
        )

        self.canvas.bind(
            "R",
            lambda event: self.restart_game()
        )

    def draw_background(self):

        # Bintang-bintang
        for i in range(65):
            x = random.randint(5, self.width-5)
            y = random.randint(5, self.height-5)

            self.canvas.create_oval(
                x, y, x+3, y+3,
                fill="#ffffff",
                outline=""
            )

        # Dekorasi bulan
        self.canvas.create_oval(
            610, 55, 660, 105,
            fill="#fff1b6",
            outline=""
        )

        self.canvas.create_oval(
            625, 45, 665, 90,
            fill="#211d3b",
            outline=""
        )

        self.canvas.create_text(
            350, 25,
            text="🐱  CAT BREAKOUT  🐱",
            fill="#ffc8dd",
            font=("Arial", 21, "bold")
        )

    def create_hud(self):

        self.score_text = self.canvas.create_text(
            85, 65,
            text="⭐ SCORE: 0",
            fill="#ffffff",
            font=("Arial", 12, "bold")
        )

        self.lives_text = self.canvas.create_text(
            580, 65,
            text="❤️ LIVES: 3",
            fill="#ffffff",
            font=("Arial", 12, "bold")
        )

    def update_hud(self):

        self.canvas.itemconfig(
            self.score_text,
            text="⭐ SCORE: " + str(self.score)
        )

        self.canvas.itemconfig(
            self.lives_text,
            text="❤️ LIVES: " + str(self.lives)
        )

    def create_bricks(self):

        colors = [1, 2, 3, 2]

        for row, hits in enumerate(colors):

            for col in range(9):

                x = 75 + col * 68
                y = 115 + row * 32

                brick = Brick(
                    self.canvas,
                    x,
                    y,
                    hits
                )

                self.items[brick.item] = brick

    def add_ball(self):

        self.ball = Ball(
            self.canvas,
            self.width/2,
            410
        )

    def show_start_screen(self):

        self.overlay = self.canvas.create_rectangle(
            130, 175, 570, 325,
            fill="#39305b",
            outline="#ffc8dd",
            width=3
        )

        self.start_text = self.canvas.create_text(
            350, 220,
            text="WELCOME TO CAT BREAKOUT!",
            fill="#ffc8dd",
            font=("Arial", 19, "bold")
        )

        self.instruction = self.canvas.create_text(
            350, 270,
            text="Press SPACE to start\n← → Move Paddle",
            fill="white",
            font=("Arial", 13),
            justify="center"
        )

    def start_game(self):

        if self.running:
            return

        if self.started:
            return

        self.started = True
        self.running = True

        self.canvas.delete(self.overlay)
        self.canvas.delete(self.start_text)
        self.canvas.delete(self.instruction)

        self.game_loop()

    def pause_game(self):

        if not self.started:
            return

        self.running = not self.running

        if self.running:
            self.canvas.delete("pause_text")
            self.game_loop()
        else:
            self.canvas.create_text(
                350, 250,
                text="⏸ PAUSED",
                fill="#ffc8dd",
                font=("Arial", 30, "bold"),
                tags="pause_text"
            )

    def check_collisions(self):

        coords = self.ball.get_position()

        overlapping = self.canvas.find_overlapping(
            *coords
        )

        objects = [
            self.items[item]
            for item in overlapping
            if item in self.items
        ]

        old_bricks = {
            obj.item: obj.hits
            for obj in objects
            if isinstance(obj, Brick)
        }

        self.ball.collide(objects)

        for brick_id, old_hits in old_bricks.items():

            if old_hits > 0:

                self.score += 10
                self.update_hud()

                if self.canvas.type(brick_id) == "":
                    self.items.pop(brick_id, None)

    def game_loop(self):

        if not self.running:
            return

        self.check_collisions()

        # Menang
        if len(self.canvas.find_withtag("brick")) == 0:
            self.end_game("YOU WIN! 🏆")
            return

        # Kehilangan bola
        if self.ball.get_position()[3] >= self.height:

            self.lives -= 1
            self.update_hud()

            if self.lives <= 0:
                self.end_game("GAME OVER! 😿")
                return

            self.ball.delete()
            self.add_ball()

            self.started = False
            self.running = False

            self.canvas.create_text(
                350, 250,
                text="😿 TRY AGAIN!\nPress SPACE",
                fill="#ffc8dd",
                font=("Arial", 24, "bold"),
                justify="center"
            )

            self.canvas.delete("retry_text")

            return

        self.ball.update()

        self.after(20, self.game_loop)

    def end_game(self, message):

        self.running = False
        self.started = False

        self.canvas.create_rectangle(
            130, 175, 570, 325,
            fill="#39305b",
            outline="#ffc8dd",
            width=3
        )

        self.canvas.create_text(
            350, 220,
            text=message,
            fill="#ffc8dd",
            font=("Arial", 28, "bold")
        )

        self.canvas.create_text(
            350, 275,
            text="Final Score: " + str(self.score)
                 + "\nPress R to Restart",
            fill="white",
            font=("Arial", 14),
            justify="center"
        )

    def restart_game(self):

        self.running = False
        self.started = False

        self.canvas.delete("all")

        self.items.clear()

        self.lives = 3
        self.score = 0

        self.draw_background()
        self.create_hud()

        self.paddle = Paddle(
            self.canvas,
            self.width/2,
            445
        )

        self.items[self.paddle.item] = self.paddle

        self.create_bricks()
        self.add_ball()
        self.update_hud()

        self.show_start_screen()

if __name__ == "__main__":

    root = tk.Tk()

    game = Game(root)

    game.mainloop()
