from tkinter import *
from tkinter.ttk import *
from typing import Tuple, Union

from board import ChessBoard
from constants import *

sys.setrecursionlimit(100000)


def format_number(num: int, format_length: int = 2) -> str:
    if len(str(num)) == format_length:
        return str(num)
    else:
        out = "0" * (format_length - len(str(num)))
        return out + str(num)


class ChessBoardInterface:
    def __init__(self, pack_label: bool = False):
        self.chessBoard = ChessBoard("p", "p")
        self.root = Tk()
        self.root.resizable(width=FALSE, height=FALSE)
        self.root.title("GoBang")

        # Total chessboard
        self.boardFrame = Frame(self.root)

        # Menu
        self._init_menu()

        # Create canvas
        self.gap = 25
        self.mainBoard = Canvas(
            self.boardFrame, width=self.gap * 16, height=self.gap * 16
        )  # size: 400 * 400
        self._draw_lines()

        # Bind mouse action
        self.mainBoard.bind("<Button-1>", self.mouse_click)

        # Generate all positions
        self.all_positions = {
            (x, y)
            for x in range(self.gap, self.gap * 16, self.gap)
            for y in range(self.gap, self.gap * 16, self.gap)
        }
        self.operate = []
        # print(self.all_positions)

        # Create Label frames
        self.horLabel = Frame(self.boardFrame)
        self.verLabel = Frame(self.boardFrame)
        self._draw_label()

        # Pack Widgets
        if pack_label:
            self.horLabel.grid(row=0, column=1, pady=0)
            self.verLabel.grid(row=1, column=0, padx=0)
        self.mainBoard.grid(row=1, column=1, padx=0, pady=0)
        self.boardFrame.pack()

    def mouse_click(self, click):
        x, y = self._nearest_position(click)
        converted_coo = self.convert_coordinate(x, y)

        # Calculate is the place already has a chess
        if self.chessBoard.board[converted_coo[0]][converted_coo[1]] != 0:
            return

        # If the board is frozen...
        if self.chessBoard.freeze:
            return

        # Draw chess
        chess_size = self.gap * 2 // 5
        if self.chessBoard.next_turn == 1:
            color = "Black"
        else:
            color = "White"
        new_position = self.convert_coordinate(x, y)
        print(f"{color} chess at position({new_position[0]}, {new_position[1]})")
        self.operate.append(
            self.mainBoard.create_oval(
                x - chess_size,
                y - chess_size,
                x + chess_size,
                y + chess_size,
                fill=color,
                tag="{} {}".format(x, y),
            )
        )
        self.mainBoard.update()

        # Update Chessboard
        result = self.chessBoard.set_chess(converted_coo[0], converted_coo[1])
        # If the game is ended
        if result == TIE:
            print("Tie!")
            self.chessBoard.freeze = True
            ok_window = OkWindow(TIE)
            self.root.wait_window(ok_window.root)
            print("Restart: {}".format(ok_window.final_restart))
            # Restart game
            if ok_window.final_restart:
                self.restart_game()

        elif result != CONTINUE:
            if result == BLACK_WIN:
                winner = "Black"
            else:
                winner = "White"
            print("{} won!".format(winner))
            self.chessBoard.freeze = True
            ok_window = OkWindow(winner)
            self.root.wait_window(ok_window.root)
            print("Restart: {}".format(ok_window.final_restart))
            # Restart game
            if ok_window.final_restart:
                self.restart_game()
        # print(self.chessBoard)

    def _nearest_position(self, click) -> Tuple[int, int]:
        x, y = click.x, click.y
        return (
            sorted(
                range(self.gap, self.gap * 16, self.gap),
                key=lambda temp_x: abs(temp_x - x),
            )[0],
            sorted(
                range(self.gap, self.gap * 16, self.gap),
                key=lambda temp_y: abs(temp_y - y),
            )[0],
        )

    @staticmethod
    def convert_coordinate(x: int, y: int) -> Tuple[int, int]:
        if x > 16 or y > 16:
            return x // 25 - 1, y // 25 - 1
        else:
            return (x + 1) * 25, (y + 1) * 25

    def _init_menu(self):
        menu = Menu(self.root, tearoff=0)
        self.root.config(menu=menu)
        game_menu = Menu(menu)
        game_menu.add_command(label="New game", command=self.restart_game)
        game_menu.add_command(label="Withdraw", command=self.withdraw)
        game_menu.add_command(label="Exit", command=self.root.destroy)
        menu.add_cascade(label="Game", menu=game_menu)

    def _draw_label(self):
        for x in range(15):
            Label(self.horLabel, text=format_number(x)).pack(side=LEFT, padx=3, pady=0)
        for y in range(15):
            Label(self.verLabel, text=format_number(y)).pack(side=TOP, pady=2, padx=0)

    def _draw_lines(self):
        # horizontal
        for index in range(1, 16):
            self.mainBoard.create_line(
                self.gap * index, self.gap, self.gap * index, 25 * 15
            )
            self.mainBoard.create_line(
                self.gap, self.gap * index, 25 * 15, self.gap * index
            )

    def restart_game(self):
        global user_info, bd
        del bd
        print("\n----------Restart Game!----------")
        self.root.destroy()
        bd = ChessBoardInterface(pack_label=user_info["pack_label"])
        bd.root.mainloop()

    def withdraw(self):
        # Check if the chessboard is frozen
        if self.chessBoard.freeze:
            return

        withdraw_gen = self.chessBoard.withdraw()
        last_chess = next(withdraw_gen)
        player, position = last_chess
        print(
            "Withdraw {} chess at ({}, {})".format(
                "Black" if player == 1 else "White", position[0], position[1]
            )
        )

        # Change next player
        self.chessBoard.next_turn = 1 if self.chessBoard.next_turn == 2 else 2

        # Delete picture
        self.mainBoard.delete(self.operate.pop())


class OkWindow:
    def __init__(self, win: Union[str, int]):
        self.final_restart = False
        self.root = Toplevel()

        self.root.title("Game End")
        self.root.resizable(width=FALSE, height=FALSE)

        self.text = Label(self.root)

        if isinstance(win, str):
            self.text["text"] = "{} won the game! Retry?".format(win)
        else:
            self.text["text"] = "Tie! Retry?"

        self.button_frame = Frame(self.root)
        Button(self.button_frame, text="OK", command=self.restart).grid(
            row=0, column=0, padx=5, pady=5
        )
        Button(self.button_frame, text="Cancel", command=self.root.destroy).grid(
            row=0, column=1, padx=5, pady=5
        )

        self.text.pack(padx=10, pady=5)
        self.button_frame.pack()
        # self.root.mainloop()

    def restart(self):
        self.root.destroy()
        self.final_restart = True


if __name__ == "__main__":
    user_info = {"pack_label": False}
    while 1:
        try:
            bd = ChessBoardInterface(pack_label=user_info["pack_label"])
            bd.root.mainloop()
        except RecursionError:
            del bd
            print("Restart program...")
            continue
        finally:
            break
