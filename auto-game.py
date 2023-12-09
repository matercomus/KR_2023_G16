import os
import random
from game import Game


class AutoGame:
    def __init__(
        self,
        n_games,
        data_path,
        save_graph_dir=None,
        save_res_dir=None,
        claimed_argument=None,
    ):
        self.n_games = n_games
        self.data_path = data_path
        self.save_graph_dir = save_graph_dir
        self.save_res_dir = save_res_dir
        self.claimed_argument = claimed_argument
        self.results = []

    def choose_proponent_move(self, game, options):
        options.sort(
            key=lambda option: len(list(game.G.successors(option)))
            - len(list(game.G.predecessors(option))),
            reverse=True,
        )
        return options[0]

    def choose_opponent_move(self, _, options):
        return random.choice(options)

    def play_games(self):
        # Check if data_path is a directory or a file
        if os.path.isdir(self.data_path):
            # If it's a directory, iterate over all JSON files
            for filename in os.listdir(self.data_path):
                if filename.endswith(".json"):
                    self.play_game(
                        os.path.join(self.data_path, filename), self.claimed_argument
                    )
        else:
            # If it's a file, just play the game
            self.play_game(self.data_path, self.claimed_argument)

    def play_game(self, data_file, claimed_argument):
        for _ in range(self.n_games):
            game = Game(
                data_file=data_file,
                claimed_argument=claimed_argument,
                verbose=False,
                save_graph_dir=self.save_graph_dir,
                save_res_dir=self.save_res_dir,
                add_game_text=True,
                choose_proponent_move=self.choose_proponent_move,
                choose_opponent_move=self.choose_opponent_move,
            )
            # If claimed_argument is None, select a random node from the graph
            if claimed_argument is None:
                game.claimed_argument = random.choice(list(game.G.nodes))
            else:
                game.claimed_argument = claimed_argument
            game.play()


if __name__ == "__main__":
    auto_game = AutoGame(
        n_games=5,
        data_path="Argumentation_Framework_tests",  # directory path
        # save_graph_dir="test_dir",  # save dir path
        save_res_dir="test_dir",  # save dir path
        claimed_argument=None,  # No claimed argument provided
    )
    auto_game.play_games()
