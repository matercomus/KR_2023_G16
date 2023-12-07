import random
from game import Game


class AutoGame:
    def __init__(
        self, n_games, claimed_argument, data_file, save_graph_dir, save_res_dir
    ):
        self.n_games = n_games
        self.claimed_argument = claimed_argument
        self.data_file = data_file
        self.save_graph_dir = save_graph_dir
        self.save_res_dir = save_res_dir
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
        for _ in range(self.n_games):
            game = Game(
                claimed_argument=self.claimed_argument,
                data_file=self.data_file,
                verbose=False,
                save_graph_dir=self.save_graph_dir,
                save_res_dir=self.save_graph_dir,
                add_game_text=True,
                choose_proponent_move=self.choose_proponent_move,
                choose_opponent_move=self.choose_opponent_move,
            )
            game.play()


if __name__ == "__main__":
    auto_game = AutoGame(
        n_games=5,
        claimed_argument="0",
        data_file="Argumentation_Framework_tests/example-argumentation-framework.json",
        save_graph_dir="test_dir",  # save dir path
        save_res_dir="test_dir",  # save dir path
    )
    auto_game.play_games()
