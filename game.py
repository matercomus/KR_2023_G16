import uuid
import os
import argparse
import json
import matplotlib.pyplot as plt
import networkx as nx


class Game:
    def __init__(
        self,
        data_file,
        claimed_argument,
        verbose=False,
        show_graph=False,
        save_graph=False,
        add_game_text=False,
        choose_proponent_move=None,
        choose_opponent_move=None,
    ):
        self.data_file = data_file
        self.data = self.load_data(data_file)
        self.claimed_argument = claimed_argument
        self.proponent_arguments = []
        self.opponent_arguments = []
        self.verbose = verbose
        self.show_graph = show_graph
        self.save_graph = save_graph
        self.add_game_text = add_game_text
        self.game_text = ""
        self.step = 1
        self.choose_proponent_move = choose_proponent_move
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
        if not self.show_graph and not self.save_graph:
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

        if self.save_graph:
            self.save_graph_to_file()

        if self.show_graph:
            plt.show(block=False)
        else:
            plt.close()

        self.step += 1

    def save_graph_to_file(self):
        data_file_name = os.path.splitext(os.path.basename(self.data_file))[0]
        directory = os.path.join(
            args.save_graph,
            data_file_name,
            f"{data_file_name}_claimed_{self.claimed_argument}_{self.id}",
        )
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(
            directory,
            f"{data_file_name}_claimed_{self.claimed_argument}_step_{self.step}.png",
        )
        plt.savefig(filename)

    def proponent_turn(self):
        options = (
            [node for node in self.G.predecessors(self.opponent_arguments[-1])]
            if self.opponent_arguments
            else [self.claimed_argument]
        )
        if not options or options[0] in self.opponent_arguments:
            print("Proponent cannot make a move. Opponent wins!")
            return False

        argument = (
            self.choose_proponent_move(self, options)
            if self.choose_proponent_move
            else options[0]
        )
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
            return False

        choice = (
            self.choose_opponent_move(self, options)
            if self.choose_opponent_move
            else self.get_user_choice(options)
        )
        argument = options[choice]
        if argument in self.proponent_arguments:
            print(
                "The opponent used an argument previously used by the proponent (contradiction). Opponent wins!"
            )
            return False

        self.opponent_arguments.append(argument)
        print(f"Opponent's argument: {self.data['Arguments'][argument]}")
        if self.verbose:
            print("Game state:", self.__dict__)
        return True

    @staticmethod
    def get_user_choice(options):
        print("Opponent's options:")
        for i, option in enumerate(options):
            print(f"{i+1}. {game.data['Arguments'][option]}")
        while True:
            try:
                choice = int(input("Enter the number of your choice: ")) - 1
                if 0 <= choice < len(options):
                    return choice
            except ValueError:
                pass
            print(
                "Invalid input. Please enter a number corresponding to one of the options."
            )

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


def choose_proponent_move(game, options):
    options.sort(
        key=lambda option: len(list(game.G.successors(option)))
        - len(list(game.G.predecessors(option))),
        reverse=True,
    )
    return options[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play the argumentation game.")
    parser.add_argument("data_file", type=str, help="The path to the data file.")
    parser.add_argument("claimed_argument", type=str, help="The claimed argument.")
    parser.add_argument(
        "--verbose", action="store_true", help="If set, print verbose output."
    )
    parser.add_argument(
        "--show_graph", action="store_true", help="If set, show the graph."
    )
    parser.add_argument(
        "--save_graph",
        nargs="?",
        const=".",
        type=str,
        help="If set, save the graph. Optional: provide a directory.",
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
        args.add_game_text,
        choose_proponent_move,
    )
    game.play()
