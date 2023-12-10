import os
import json
import uuid
import argparse
import networkx as nx
import matplotlib.pyplot as plt


class Game:
    def __init__(
        self,
        data_file,
        claimed_argument,
        verbose=False,
        show_graph=False,
        save_graph_dir=None,
        save_res_dir=None,
        add_game_text=False,
        choose_opponent_move=None,
    ):
        self.data_file = data_file
        self.data = self.load_data(data_file)
        self.claimed_argument = claimed_argument
        self.proponent_arguments = []
        self.opponent_arguments = []
        self.verbose = verbose
        self.show_graph = show_graph
        self.save_graph_dir = save_graph_dir
        self.save_res_dir = save_res_dir
        self.add_game_text = add_game_text
        self.game_text = ""
        self.step = 1
        self.winner = None
        self.choose_opponent_move = choose_opponent_move
        self.G = self.initialize_graph()
        self.id = uuid.uuid4()

    @staticmethod
    def load_data(data_file):
        with open(data_file, "r") as f:
            return json.load(f)

    def initialize_graph(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.data["Arguments"].keys())
        G.add_edges_from(self.data["Attack Relations"])
        return G

    def draw_graph(self):
        if not self.show_graph and not self.save_graph_dir:
            return

        plt.figure(figsize=(16, 10))
        pos = nx.spring_layout(self.G, seed=10)
        nx.draw_networkx_nodes(
            self.G, pos, nodelist=self.proponent_arguments, node_color="blue"
        )
        nx.draw_networkx_nodes(
            self.G, pos, nodelist=self.opponent_arguments, node_color="red"
        )
        nx.draw_networkx_edges(
            self.G, pos, edge_color="black", arrowstyle="->", arrowsize=20
        )
        nx.draw_networkx_labels(self.G, pos, font_size=12)
        argument_text = {k: f"{v}" for k, v in self.data["Arguments"].items()}
        pos_higher = {k: (v[0], v[1] + 0.04) for k, v in pos.items()}
        nx.draw_networkx_labels(
            self.G,
            pos_higher,
            labels=argument_text,
            horizontalalignment="center",
            font_size=8,
        )

        if self.add_game_text:
            plt.text(
                0.5,
                0.05,
                self.game_text,
                ha="center",
                va="center",
                transform=plt.gcf().transFigure,
            )

        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)

        if self.save_graph_dir:
            self.save_graph_to_file()

        if self.show_graph:
            plt.show(block=False)
        else:
            plt.close()

        self.step += 1

    def save_graph_to_file(self):
        data_file_name = os.path.splitext(os.path.basename(self.data_file))[0]
        if self.save_graph_dir:
            directory = os.path.join(
                self.save_graph_dir,
                data_file_name,
                f"{data_file_name}_claimed_{self.claimed_argument}_{self.id}",
            )
            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(
                directory,
                f"{data_file_name}_claimed_{self.claimed_argument}_step_{self.step}.png",
            )
            plt.savefig(filename)

    def save_results(self):
        results = {
            "proponent_arguments": self.proponent_arguments,
            "opponent_arguments": self.opponent_arguments,
            "game_text": self.game_text,
            "winner": self.winner,
        }
        data_file_name = os.path.splitext(os.path.basename(self.data_file))[0]
        if self.save_res_dir:
            directory = os.path.join(
                self.save_res_dir,
                data_file_name,
                f"{data_file_name}_claimed_{self.claimed_argument}_{self.id}",
            )
            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(
                directory,
                f"{data_file_name}_claimed_{self.claimed_argument}_{self.id}_results.json",
            )
            with open(filename, "w") as f:
                json.dump(results, f)

    def choose_proponent_move(self, options):
        best_argument = None
        best_path_length = float('inf')

        def dfs(argument, path, visited_proponent, visited_opponent):
            nonlocal best_argument, best_path_length

            # Losing conditions
            if argument in visited_opponent or \
                not self.G.predecessors(argument) \
                    or argument in self.G.predecessors(argument):
                return False

            # Winning condition
            if all(pred in visited_proponent for pred in self.G.predecessors(argument)):
                if len(path) < best_path_length:
                    best_argument = path[0]
                    best_path_length = len(path)
                return True

            for next_argument in self.G.predecessors(argument):
                if next_argument not in visited_proponent:
                    visited_proponent.add(next_argument)
                    path.append(next_argument)
                    if dfs(next_argument, path, visited_proponent, visited_opponent):
                        return True
                    path.pop()
                    visited_proponent.remove(next_argument)

            return False

        for argument in options:
            dfs(argument, [argument], {argument}, set(self.opponent_arguments))

        return best_argument if best_argument else options[0]  # Fallback to the first option if no winning path is found

    def proponent_turn(self):
        options = (
            [node for node in self.G.predecessors(self.opponent_arguments[-1])]
            if self.opponent_arguments
            else [self.claimed_argument]
        )
        if not options or options[0] in self.opponent_arguments:
            print("Proponent cannot make a move. Opponent wins!")
            self.winner = "Opponent"
            return False
        if len(options) == 1:
            argument = options[0]
        else:
            argument = self.choose_proponent_move(options)

        self.proponent_arguments.append(argument)
        print(f"Proponent's argument: {self.data['Arguments'][argument]}")
        if self.verbose:
            print("Game state:", self.__dict__)
        return True

    def opponent_turn(self):
        options = [
            attack
            for argument in set(self.proponent_arguments)
            for attack in self.G.predecessors(argument)
            if attack not in self.opponent_arguments
        ]
        if not options:
            print("Opponent has no choices left. Proponent wins!")
            self.winner = "Proponent"
            return False

        argument = (
            self.choose_opponent_move(self, options)
            if self.choose_opponent_move
            else self.get_user_choice(options)
        )
        if argument in self.proponent_arguments:
            print("The opponent used an argument previously used by the proponent (contradiction). Opponent wins!")
            self.winner = "Opponent"
            return False

        self.opponent_arguments.append(argument)
        print(f"Opponent's argument: {self.data['Arguments'][argument]}")
        if self.verbose:
            print("Game state:", self.__dict__)
        return True

    def get_user_choice(self, options):
        print("Opponent's options:")
        for i, option in enumerate(options):
            print(f"{i+1}. {self.data['Arguments'][option]}")
        while True:
            try:
                choice = int(input("Enter the number of your choice: ")) - 1
                if 0 <= choice < len(options):
                    return options[choice]
            except ValueError:
                pass
            print("Invalid input. Please enter a number corresponding to one of the options.")

    def play(self):
        while True:
            print("\nProponent's turn...")
            if not self.proponent_turn():
                break
            self.game_text += f"Step({self.step}) Proponent: {self.data['Arguments'][self.proponent_arguments[-1]]}\n"
            self.draw_graph()

            print("\nOpponent's turn...")
            if not self.opponent_turn():
                break
            self.game_text += f"Step({self.step}) Opponent: {self.data['Arguments'][self.opponent_arguments[-1]]}\n"
            self.draw_graph()

        self.save_results()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play the argumentation game.")
    parser.add_argument("data_file", type=str, help="The path to the data file.")
    parser.add_argument("claimed_argument", type=str, help="The claimed argument.")
    parser.add_argument("--verbose", action="store_true", help="If set, print verbose output.")
    parser.add_argument("--show_graph", action="store_true", help="If set, show the graph.")
    parser.add_argument(
        "--save_graph",
        nargs="?",
        const=".",
        type=str,
        help="If set, save the graph. Optional: provide a directory.",
    )
    parser.add_argument(
        "--save_res",
        nargs="?",
        const=".",
        type=str,
        help="If set, save the results. Optional: provide a directory.",
    )
    parser.add_argument(
        "--add_game_text",
        action="store_true",
        help="If set, add game text to the graph.",
    )
    args = parser.parse_args()

    game = Game(
        args.data_file,
        args.claimed_argument,
        args.verbose,
        args.show_graph,
        args.save_graph,
        args.save_res,
        args.add_game_text
    )
    game.play()
