import copy
from typing import List, Tuple, Union

from constants import *
from main import format_number


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

    def get_board(self):
        return copy.copy(self.board)

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

    def _split_board(self):
        """
        This generator split board vertically, horizontally and diagonally into one-dimension arrays
        :return: Yield all split arrays one by one
        """
        yield from self.board
        for index, _ in enumerate(self.board):
            yield [self.board[x][index] for x in range(15)]
        # Diagonal
        for base in range(29):
            yield [
                self.board[x][base - x]
                for x in range(
                    0 if base <= 14 else base - 14, base + 1 if base <= 14 else 15
                )
            ]
        for diff in range(-14, 15):
            yield [
                self.board[x][x + diff]
                for x in range(
                    abs(diff) if diff < 0 else 0, 15 if diff < 0 else 15 - diff
                )
            ]

    # Evaluate part
    def evaluate(self, player: int) -> int:
        """
        Evaluate the situation on chessboard for one player, calculate an int as the result.
        :param player: 1 for black and 2 for white
        :return: Current situation. Bigger the outcome, more favourable the situation to the player
        """

        standards = {
            "5+": 100000,  # live 5
            "4+": 10000,  # live 4
            "3+": 1000,  # live 3
            "2+": 100,  # live 2
            "1+": 10,  # live 1
            "4-": 1000,  # dead 4
            "3-": 100,  # dead 3
            "2-": 10,  # dead 2
        }

        for line in self._split_board():
            # 5+
            # TODO: complete evaluate function
            pass

        return 0

    def _evaluate_point(self, point: Tuple[int, int]) -> int:
        """
        Evaluate the score of a specific point in the board
        :param point: Coordinate of the point
        :return: Score of the point
        """

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
