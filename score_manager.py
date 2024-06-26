class ScoreManager:
    def __init__(self):
        self.lines_cleared = 0
        self.score = 0
        self.gravity = 500  # Gravity at level 0

    def add_lines_cleared(self, lines):
        self.lines_cleared += lines
        self.add_score(lines)
        self.adjust_gravity()

    def add_score(self, lines_cleared):
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 200
        elif lines_cleared == 3:
            self.score += 400
        elif lines_cleared == 4:
            self.score += 800

    def adjust_gravity(self):
        if (self.lines_cleared != 0):
            if self.lines_cleared % 10 == 0:
                self.gravity = max(50, self.gravity - 50)  # Decrease gravity interval but not below 100ms

    def get_gravity(self):
        return self.gravity

    def get_lines_cleared(self):
        return self.lines_cleared

    def get_score(self):
        return self.score
