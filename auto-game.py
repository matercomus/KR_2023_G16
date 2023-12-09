import json
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
        self.results = {}

    @staticmethod
    def choose_proponent_move(game, options):
        best_argument = None
        best_path_length = float("inf")

        def dfs(argument, path, visited_proponent, visited_opponent):
            nonlocal best_argument, best_path_length

            # Losing conditions
            if (
                argument in visited_opponent
                or not game.G.predecessors(argument)
                or argument in game.G.predecessors(argument)
            ):
                return False

            # Winning condition
            if all(pred in visited_proponent for pred in game.G.predecessors(argument)):
                if len(path) < best_path_length:
                    best_argument = path[0]
                    best_path_length = len(path)
                return True

            for next_argument in game.G.predecessors(argument):
                if next_argument not in visited_proponent:
                    visited_proponent.add(next_argument)
                    path.append(next_argument)
                    if dfs(next_argument, path, visited_proponent, visited_opponent):
                        return True
                    path.pop()
                    visited_proponent.remove(next_argument)

            return False

        for argument in options:
            dfs(argument, [argument], {argument}, set(game.opponent_arguments))

        return (
            best_argument if best_argument else options[0]
        )  # Fallback to the first option if no winning path is found

    @staticmethod
    def choose_opponent_move(_, options):
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
        # Save results
        self.write_results()

    def write_results(self):
        with open(os.path.join(self.save_res_dir, "results.json"), "w") as f:
            json.dump(self.results, f)

    def play_game(self, data_file, claimed_argument):
        for n in range(self.n_games):
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
            game.claimed_argument = (
                random.choice(list(game.G.nodes))
                if claimed_argument is None
                else claimed_argument
            )
            game.play()
            # Use the base name of the data file as the key
            key = os.path.basename(data_file)
            if key not in self.results:
                self.results[key] = []
            self.results[key].append(
                {
                    "game_number": n,
                    "winner": game.winner,  # assuming game object has a winner attribute
                }
            )


if __name__ == "__main__":
    auto_game = AutoGame(
        n_games=100,
        data_path="Argumentation_Framework_tests",  # directory path
        # save_graph_dir="test_dir",  # save dir path
        save_res_dir="test_dir",  # save dir path
        claimed_argument=None,  # No claimed argument provided
    )
    auto_game.play_games()
