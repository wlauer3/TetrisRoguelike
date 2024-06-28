import math

class ScoreManager:
    def __init__(self, level_manager):
        self.lines_cleared = 0
        self.score = 0
        self.gravity = 500  # Gravity at level 0
        self.level_manager = level_manager

    def add_lines_cleared(self, lines):
        previous_lines_cleared = self.lines_cleared
        self.lines_cleared += lines
        self.level_manager.update_level(self.lines_cleared)
        self.add_score(lines)

        # Adjust gravity if an interval of 10 lines is cleared
        if self.lines_cleared // 10 > previous_lines_cleared // 10:
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
        self.gravity = math.floor(self.gravity*.007**(1/29)) # At level 29 this = 1 ms

    def get_gravity(self):
        return self.gravity

    def get_lines_cleared(self):
        return self.lines_cleared

    def get_score(self):
        return self.score
    

