class Game:
    def __init__(self, nA, nB, nC):
        self.nA = nA
        self.nB = nB
        self.nC = nC
        self.winner = 0     # 1 is client, 2 is server

    def is_done(self):
        return self.nA == 0 and self.nB == 0 and self.nC == 0

    def apply_server_turn(self):
        if (self.nA > self.nB):
            if (self.nA > self.nC):
                self.nA -= 1
            else:
                self.nC -= 1
        else:
            if (self.nB > self.nC):
                self.nB -= 1
            else:
                self.nC -= 1
        if self.is_done():
            self.winner = 2

    def apply_client_turn(self,heap,amount):
        if heap == 'A':
            if self.nA >= amount:
                self.nA -= amount
                if self.is_done():
                    self.winner = 1
                return True
        if heap == 'B':
            if self.nB >= amount:
                self.nB -= amount
                if self.is_done():
                    self.winner = 1
                return True
        if heap == 'C':
            if self.nC >= amount:
                self.nC -= amount
                if self.is_done():
                    self.winner = 1
                return True
        return False
