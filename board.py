class Board:
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]

    def add_tetromino(self, tetromino, position):
        for x, y in tetromino.shape:
            self.board[y + position[1]][x + position[0]] = 1

    def clear_lines(self):
        lines_to_clear = [i for i in range(self.height) if all(self.board[i])]
        for i in lines_to_clear:
            del self.board[i]
            self.board.insert(0, [0 for _ in range(self.width)])
        return len(lines_to_clear)  # Return the number of cleared lines

    def check_collision(self, tetromino, position):
        for x, y in tetromino.shape:
            if (x + position[0] < 0 or x + position[0] >= self.width or
                y + position[1] >= self.height or
                self.board[y + position[1]][x + position[0]]):
                return True
        return False

    def reset(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]