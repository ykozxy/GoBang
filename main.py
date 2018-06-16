from tkinter import *
from tkinter.ttk import *
from typing import List, Tuple, Union

sys.setrecursionlimit(100000)

BLACK_WIN = 1
WHITE_WIN = 2
TIE = 3
CONTINUE = 0


def format_number(num: int, format_length: int = 2) -> str:
    if len(str(num)) == format_length:
        return str(num)
    else:
        out = "0" * (format_length - len(str(num)))
        return out + str(num)


class ChessBoard:
    def __init__(
        self, p1: str, p2: str, data: List[List] = None, size: Tuple = (15, 15)
    ):
        # Create main board
        # Note: the x and y coordinate are stored reversely in self.board than in real board.
        # That is: x is vertical coordinate here, while y is horizontal coordinate
        if not data:
            self.board = [[0 for _ in range(size[0])] for _ in range(size[1])]
        else:
            self.board = data

        # Record all operations
        # Format: (player, (x, y))
        self.operations: List[Tuple[int, Tuple(int, int)]] = []

        # Currently, board size must be 15*15
        assert size == (15, 15), "Currently, board size must be 15*15"
        self.size = size
        # The next player set the chess. 1 for black and 2 for white. Always black first.
        self.next_turn = 1

        # Set mode
        if p1 not in ["p", "c"]:
            raise ValueError(f"Player must be 'p' or 'c', {p1} given!")
        if p2 not in ["p", "c"]:
            raise ValueError(f"Player must be 'p' or 'c', {p2} given!")
        # Currently, there are three modes:
        # player vs. player, player vs. computer, computer vs. computer(this will turn into training process in future)
        self.mode = p1, p2

        self.freeze = False

    def win_determine(
        self, x: Union[int, None] = None, y: Union[int, None] = None
    ) -> int:
        """
        Determine if there's player win in the chessboard
        :param x: x coordinate of last chess
        :param y: y coordinate of last chess
        :return: a integer determine who wins the game (1 for black, 2 for white, 3 for tie, and 0 for no on win)
        """
        # Tie
        for line in self.board:
            for each in line:
                if each == 0:
                    break
            else:
                continue
            break
        else:
            return TIE

        # Detect according to the last chess set
        if all((isinstance(x, int), isinstance(y, int))):
            # Horizontal
            start_x = x - 4 if x - 4 >= 0 else 0
            end_x = x if x + 4 < 15 else 10
            for current_x in range(start_x, end_x + 1):
                result = self._all_same(
                    [self.board[new_x][y] for new_x in range(current_x, current_x + 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

            # Vertical
            start_y = y - 4 if y - 4 >= 0 else 0
            end_y = y if y + 4 < 15 else 10
            for current_y in range(start_y, end_y + 1):
                result = self._all_same(
                    [self.board[x][new_y] for new_y in range(current_y, current_y + 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

            # Diagonal
            # Upper-left to Down-right
            nearest_to_upper_left = min(x, y)
            if nearest_to_upper_left < 4:
                start_x = x - nearest_to_upper_left
                start_y = y - nearest_to_upper_left
            nearest_to_down_right = min(14 - x, 14 - y)
            if nearest_to_down_right < 4:
                end_x = x - (4 - nearest_to_down_right)
            for index, current_x in enumerate(range(start_x, end_x + 1)):
                current_y = start_y + index
                result = self._all_same(
                    [self.board[current_x + d][current_y + d] for d in range(0, 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

            # Down-left to Upper-right
            nearest_to_down_left = min(x, 14 - y)
            if nearest_to_down_left < 4:
                start_x = x - nearest_to_down_left
                start_y = y + nearest_to_down_left
            else:
                # Here need to re-calculate start x and y because they are changed previously
                start_x = x - 4
                start_y = y + 4
            nearest_to_upper_right = min(14 - x, y)
            if nearest_to_upper_right < 4:
                end_x = x - (4 - nearest_to_upper_right)
            else:
                # Need to re-calculate end x as the same reason above
                end_x = x
            for index, current_x in enumerate(range(start_x, end_x + 1)):
                current_y = start_y - index
                result = self._all_same(
                    [self.board[current_x + d][current_y - d] for d in range(0, 5)]
                )
                if result:
                    return BLACK_WIN if self.board[x][y] == 1 else WHITE_WIN

        else:
            raise ValueError(
                "Judgement of total chessboard has not be implemented yet!"
            )
        return CONTINUE

    @staticmethod
    def _all_same(lst: list) -> bool:
        """
        Determine is all the elements in the given iterable is same(despite the condition of all 0)
        :return: if there is player win
        """
        first = lst[0]
        if first == 0:
            return False
        for item in lst[1:]:
            if item != first:
                return False
        return True

    def evaluate(self, player: int) -> int:
        """
        Evaluate the situation on chessboard for one player, calculate an int as the result.
        :param player: 1 for black and 2 for white
        :return: Current situation. Bigger the outcome, more favourable the situation to the player
        """
        # TODO
        standard = {
            "5+": 100000,  # live 5
            "4+": 10000,  # live 4
            "3+": 1000,  # live 3
            "2+": 100,  # live 2
            "1+": 10,  # live 1

            "4-": 1000,  # dead 4
            "3-": 100,  # dead 3
            "2-": 10  # dead 2
        }
        return 0

    def __repr__(self):
        """
        Should output x and y reversely, since they are stored differently in self.board
        """
        out = "   "
        for x in range(self.size[0]):
            temp_x = format_number(x)
            out += f"{temp_x} "
        out += "\n"
        for y in range(self.size[0]):
            temp_y = format_number(y)
            out += f"{temp_y}"
            for x in range(self.size[1]):
                out += f"  {str(self.board[x][y])}"
            out += "\n"
        return out

    def get_board(self):
        return self.board

    def copy_board(self):
        """
        This function is used to calculate winning possibilities
        :return: Chessboard instance with initial data of current board.
        """
        return ChessBoard(self.mode[0], self.mode[1], data=self.board)

    def set_chess(self, x: int, y: int, reset: bool = False):
        """
        Set a chess to board and return if there's a player win the game
        :param x: x coordinate
        :param y: y coordinate
        :param reset: initialize the position (turn the date into 0)
        :return:
        """
        # Check input
        if x not in range(self.size[0]):
            raise ValueError(
                f"X coordinate should be in range 0~{self.size[0]}, {x} given!"
            )
        if y not in range(self.size[1]):
            raise ValueError(
                f"Y coordinate should be in range 0~{self.size[1]}, {y} given!"
            )

        # Add operation to recorder
        self.operations.append((self.next_turn, (x, y)))
        if reset:
            self.board[x][y] = 0
        else:
            self.board[x][y] = self.next_turn
            # Switch the value of self.next_turn from 1 to 2 or vise versa
            self.next_turn = 1 if self.next_turn == 2 else 2
        return self.win_determine(x, y)

    def withdraw(self):
        """
        Usage: next(self.withdraw())
        :return: Generator, return (player, (x, y))
        """
        operation_length = len(self.operations)
        withdraw_times = 0
        while True:
            withdraw_times += 1
            if not self.operations:
                raise ValueError(
                    f"Stored {operation_length} operations, {withdraw_times} withdraw times given!"
                )
            withdraw_item = self.operations.pop()
            self.set_chess(withdraw_item[1][0], withdraw_item[1][1], reset=True)
            yield withdraw_item


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
        print("Withdraw {} chess at ({}, {})".format("Black" if player == 1 else "White", position[0], position[1]))

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
