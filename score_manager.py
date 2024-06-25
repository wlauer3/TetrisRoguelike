class ScoreManager:
    def __init__(self):
        self.lines_cleared = 0
        self.gravity = 500  # Gravity at level 0

    def add_lines_cleared(self, lines):
        self.lines_cleared += lines
        self.adjust_gravity()

    def adjust_gravity(self):
        if self.lines_cleared % 10 == 0:
            self.gravity = max(100, self.gravity - 50)  # Decrease gravity interval but not below 100ms

    def get_gravity(self):
        return self.gravity

    def get_lines_cleared(self):
        return self.lines_cleared
