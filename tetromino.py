class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.rotation_index = 0
        self.x = 0
        self.y = 0

    def rotate(self):
        self.rotation_index = (self.rotation_index + 1) % len(self.shape)

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def drop(self):
        self.y += 1

    def get_current_shape(self):
        return self.shape[self.rotation_index]