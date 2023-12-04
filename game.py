import datetime
import os
import argparse
import json
import random

import matplotlib.pyplot as plt
import networkx as nx


# Define the Game class
class Game:
    # Initialize the game with the given parameters
    def __init__(
        self,
        data_file,
        claimed_argument,
        verbose=False,
        show_graph=False,
        save_graph=False,
        add_game_text=False,
    ):
        self.data_file = data_file
        self.data = self.load_data()
        self.claimed_argument = claimed_argument
        self.proponent_arguments = []
        self.opponent_arguments = []
        self.verbose = verbose
        self.show_graph = show_graph
        self.save_graph = save_graph
        self.add_game_text = add_game_text
        self.game_text = ""
        self.step = 1

        # Initialize the graph
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.data["Arguments"].keys())
        self.G.add_edges_from(self.data["Attack Relations"])
        self.pos = nx.spring_layout(self.G, seed=10)

    # Load the data from the file
    def load_data(self):
        with open(self.data_file, "r") as f:
            data = json.load(f)
        return data

    # Draw the graph
    def draw_graph(self):
        if not self.show_graph and not self.save_graph:
            return

        plt.figure(figsize=(16, 10))
        nx.draw_networkx_nodes(
            self.G, self.pos, nodelist=self.proponent_arguments, node_color="blue"
        )
        nx.draw_networkx_nodes(
            self.G, self.pos, nodelist=self.opponent_arguments, node_color="red"
        )
        nx.draw_networkx_edges(
            self.G, self.pos, edge_color="black", arrowstyle="->", arrowsize=20
        )
        nx.draw_networkx_labels(self.G, self.pos, font_size=12)
        argument_text = {k: f"{v}" for k, v in self.data["Arguments"].items()}
        pos_higher = {k: (v[0], v[1] + 0.04) for k, v in self.pos.items()}
        nx.draw_networkx_labels(
            self.G,
            pos_higher,
            labels=argument_text,
            horizontalalignment="center",
            font_size=8,
        )

        # Add game text to the graph
        if self.add_game_text:
            plt.text(
                0.5,
                0.05,
                self.game_text,
                ha="center",
                va="center",
                transform=plt.gcf().transFigure,
            )

        # Adjust the margins
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)

        if self.save_graph:
            # Get the filename part of the data_file value without the extension
            data_file_name = os.path.splitext(os.path.basename(self.data_file))[0]

            # Get the current timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")

            # Define the directory
            directory = os.path.join(
                args.save_graph,
                data_file_name,
                f"{data_file_name}_claimed_{self.claimed_argument}_{timestamp}",
            )

            # Create the directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Create a filename using the data_file_name and claimed_argument attributes
            filename = os.path.join(
                directory,
                f"{data_file_name}_claimed_{self.claimed_argument}_step_{self.step}.png",
            )
            plt.savefig(filename)

        if self.show_graph:
            plt.show(block=False)
        else:
            plt.close()

        self.step += 1

    # Proponent's turn
    def proponent_turn(self):
        if not self.opponent_arguments:  # Check if opponent_arguments is empty
            # The proponent's argument is the claimed argument
            argument = self.claimed_argument
        else:
            # Find an argument that attacks the opponent's last argument and has not been used by the opponent
            options = [
                node
                for node in self.G.predecessors(self.opponent_arguments[-1])
                # if node not in self.opponent_arguments
            ]
            if not options:
                print("Proponent cannot make a move. Opponent wins!")
                return False
            # Choose a random argument from the options
            argument = random.choice(options)
            if argument in self.opponent_arguments:
                print(
                    "The proponent used an argument previously used by the opponent (contradiction). Opponent wins!"
                )

        # Add the argument to the proponent's arguments
        self.proponent_arguments.append(argument)
        # Print the proponent's argument
        print(f"Proponent's argument: {self.data['Arguments'][argument]}")
        if self.verbose:
            # Print the game state if verbose is True
            print("Game state:", self.__dict__)
        return True

    # Opponent's turn
    def opponent_turn(self):
        # Find an argument that has not been used by the opponent and attacks the proponent's arguments
        options = []
        for argument in set(self.proponent_arguments):
            attacks = self.G.predecessors(argument)
            for attack in attacks:
                if attack not in self.opponent_arguments:
                    options.append(attack)

        if not options:
            print("Opponent has no choices left. Proponent wins!")
            return False

        print("Opponent's options:")
        for i, option in enumerate(options):
            # Print the opponent's options
            print(f"{i+1}. {self.data['Arguments'][option]}")

        while True:
            try:
                # Get the opponent's choice
                choice = int(input("Enter the number of your choice: ")) - 1
                if choice < 0 or choice >= len(options):
                    raise ValueError
                break
            except ValueError:
                print(
                    "Invalid input. Please enter a number corresponding to one of the options."
                )

        # The opponent's argument is the chosen option
        argument = options[choice]
        if argument in self.proponent_arguments:
            print(
                "The opponent used an argument previously used by the proponent (contradiction). Opponent wins!"
            )
            return False
        # Add the argument to the opponent's arguments
        self.opponent_arguments.append(argument)
        # Print the opponent's argument
        print(f"Opponent's argument: {self.data['Arguments'][argument]}")

        if self.verbose:
            # Print the game state if verbose is True
            print("Game state:", self.__dict__)
        return True

    # Play the game
    def play(self):
        while True:
            print("\nProponent's turn...")
            if (
                not self.proponent_turn()
            ):  # If the proponent cannot make a move, break the loop
                break
            # Add the proponent's argument to the game text
            self.game_text += (
                f"Proponent: {self.data['Arguments'][self.proponent_arguments[-1]]}\n"
            )
            self.draw_graph()  # Draw the graph after updating game text

            print("\nOpponent's turn...")
            if (
                not self.opponent_turn()
            ):  # If the opponent cannot make a move, break the loop
                break
            # Add the opponent's argument to the game text
            self.game_text += (
                f"Opponent: {self.data['Arguments'][self.opponent_arguments[-1]]}\n"
            )
            self.draw_graph()  # Draw the graph after updating game text


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

    args = parser.parse_args()  # Parse the command-line arguments

    # Create a Game object and play the game
    game = Game(
        args.data_file,
        args.claimed_argument,
        args.verbose,
        args.show_graph,
        args.save_graph,
        args.add_game_text,
    )
    game.play()
