
import argparse
import json

import matplotlib.pyplot as plt
import networkx as nx


class Game:
    def __init__(self, data_file, claimed_argument, verbose=False, show_graph=False, save_graph=False, add_game_text=False):
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
        self.G.add_nodes_from(self.data['Arguments'].keys())
        self.G.add_edges_from(self.data['Attack Relations'])
        self.pos = nx.spring_layout(self.G, seed=10)  # Graph Layout

    def load_data(self):
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        return data

    def draw_graph(self):
        if not self.show_graph and not self.save_graph:
            return

        plt.figure(figsize=(16, 10))
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.proponent_arguments, node_color='blue')
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.opponent_arguments, node_color='red')
        nx.draw_networkx_edges(self.G, self.pos, edge_color='black', arrowstyle='->', arrowsize=20)
        nx.draw_networkx_labels(self.G, self.pos, font_size=12)
        argument_text = {k: f'{v}' for k, v in self.data['Arguments'].items()}
        pos_higher = {k: (v[0], v[1]+0.04) for k, v in self.pos.items()}
        nx.draw_networkx_labels(self.G, pos_higher, labels=argument_text, horizontalalignment='center', font_size=8)

        # Add game text to the graph
        if self.add_game_text:
            plt.text(0.5, 0.05, self.game_text, ha='center', va='center', transform=plt.gcf().transFigure)

        # Adjust the margins
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)

        if self.save_graph:
            plt.savefig(f'game_output_{self.step}.png')

        if self.show_graph:
            plt.show(block=False)
        else:
            plt.close()

        self.step += 1


    def proponent_turn(self):
        if not self.opponent_arguments:  # Check if opponent_arguments is empty
            argument = self.claimed_argument
        else:
            # Find an argument that attacks the opponent's last argument and has not been used by the opponent
            for node in self.G.predecessors(self.opponent_arguments[-1]):
                if node not in self.opponent_arguments:
                    argument = node
                    break
            else:
                print("Proponent cannot make a move. Opponent wins!")
                return False

        self.proponent_arguments.append(argument)
        self.G.remove_node(argument)
        print(f"Proponent's argument: {self.data['Arguments'][argument]}")
        if self.verbose:
            print("Game state:", self.__dict__)
        return True

    def opponent_turn(self):
        options = []
        for node in self.G.nodes:
            if node not in self.opponent_arguments and self.G.has_edge(node, self.proponent_arguments[-1]):
                options.append(node)

        if not options:
            print("Opponent has no choices left. Proponent wins!")
            return False

        print("Opponent's options:")
        for i, option in enumerate(options):
            print(f"{i+1}. {self.data['Arguments'][option]}")

        while True:
            try:
                choice = int(input("Enter the number of your choice: ")) - 1
                if choice < 0 or choice >= len(options):
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a number corresponding to one of the options.")

        argument = options[choice]

        self.opponent_arguments.append(argument)
        self.G.remove_node(argument)
        print(f"Opponent's argument: {self.data['Arguments'][argument]}")
        if self.verbose:
            print("Game state:", self.__dict__)
        return True

    def play(self):
        while True:
            print("\nProponent's turn...")
            if not self.proponent_turn():
                break
            self.game_text += f"Proponent: {self.data['Arguments'][self.proponent_arguments[-1]]}\n"
            self.draw_graph()  # Draw the graph after updating game text

            print("\nOpponent's turn...")
            if not self.opponent_turn():
                break
            self.game_text += f"Opponent: {self.data['Arguments'][self.opponent_arguments[-1]]}\n"
            self.draw_graph()  # Draw the graph after updating game text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play the argumentation game.')
    parser.add_argument('data_file', type=str, help='The path to the data file.')
    parser.add_argument('claimed_argument', type=str, help='The claimed argument.')
    parser.add_argument('--verbose', action='store_true', help='If set, print verbose output.')
    parser.add_argument('--show_graph', action='store_true', help='If set, show the graph.')
    parser.add_argument('--save_graph', action='store_true', help='If set, save the graph.')
    parser.add_argument('--add_game_text', action='store_true', help='If set, add game text to the graph.')

    args = parser.parse_args()

    game = Game(args.data_file, args.claimed_argument, args.verbose, args.show_graph, args.save_graph, args.add_game_text)
    game.play()
