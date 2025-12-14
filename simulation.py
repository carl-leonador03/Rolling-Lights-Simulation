import numpy as np

class Game:
    __c = [20, 50, 100, 200, 500, 750, 1000]

    """Abstract Game class object used as template for other Games."""
    def __init__(self, lights: int = 12, weights: list[int]|list[float]|None = None, initial_bank: int = 10000):
        self.lights = lights if lights >= 12 else 12
        self.weights = weights if weights != None else [1 / lights] * lights
        self.players = []
        self.selected = 0
        self.prize_poll = [np.random.choice(self.__c) for _ in range(self.lights)]
        self.initial_bank = initial_bank
    
    def bet(self, player: int, amount: int, slot: int):
        raise NotImplementedError()
    
    def play(self):
        raise NotImplementedError()

class FairGame(Game):
    def __init__(self, lights: int = 12, initial_bank: int = 10000):
        super(FairGame, self).__init__(lights, initial_bank = initial_bank)
    
    def bet(self, player: int, amount: int, slot: int) -> None:
        if len(self.players) > 0:
            for i, p in enumerate(self.players):
                # Check if the player has betted before.
                # Overwrite old bet with new.
                if p[0] == player and p[2] == slot:
                    _ = self.players.pop(i)

        self.players.append((player, amount, slot))
    
    def play(self):
        self.selected = np.random.choice(range(self.lights), p=self.weights)
        won = []

        # Check if a player or more has been selected
        for player in self.players:
            if player[2] == self.selected:
                won.append(player)

        self.initial_bank += sum([p[1] for p in self.players])

        if len(won) > 0:
            self.initial_bank -= (self.prize_poll[self.selected] * len(won))

            return dict(
                [(p[0], self.prize_poll[self.selected]) for p in won]
            )

        else:
            return {}

class TweakedGame(Game):
    def __init__(self, lights: int = 12, weights: list[int]|list[float]|None = None, initial_bank: int = 10000):
        super(TweakedGame, self).__init__(lights, weights = weights, initial_bank = initial_bank)
    
    def bet(self, player: int, amount: int, slot: int) -> None:
        if len(self.players) > 0:
            for i, p in enumerate(self.players):
                # Check if the player has betted before.
                # Overwrite old bet with new.
                if p[0] == player and p[2] == slot:
                    _ = self.players.pop(i)

        self.players.append((player, amount, slot))
    
    def play(self):
        self.selected = np.random.choice(range(self.lights), p=self.weights)
        won = []

        # Check if a player or more has been selected
        for player in self.players:
            if player[2] == self.selected:
                won.append(player)

        self.initial_bank += sum([p[1] for p in self.players])

        if len(won) > 0:
            self.initial_bank -= (self.prize_poll[self.selected] * len(won))

            return dict(
                [(p[0], self.prize_poll[self.selected]) for p in won]
            )

        else:
            return {}

class Simulator:
    def __init__(self, game_model: Game, n_of_sims: int = 10000, random_seed: int = 42):
        np.random.seed(random_seed)
        self.game = game_model
        self.n_of_sims = n_of_sims if n_of_sims >= 10000 else 10000
    
    def simulate(self):
        for _ in range(self.n_of_sims):
            yield self.game.play()