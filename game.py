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

    def load_data(self):
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        return data

    def draw_graph(self):
        if not self.show_graph:
            return

        G = nx.DiGraph()
        G.add_nodes_from(self.data['Arguments'].keys())
        G.add_edges_from(self.data['Attack Relations'])
        pos = nx.spring_layout(G, seed=24)  # Graph Layout
        plt.figure(figsize=(16, 10))
        nx.draw_networkx_nodes(G, pos, nodelist=self.proponent_arguments, node_color='blue')
        nx.draw_networkx_nodes(G, pos, nodelist=self.opponent_arguments, node_color='red')
        nx.draw_networkx_edges(G, pos, edge_color='black', arrowstyle='->', arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=12)
        argument_text = {k: f'{v}' for k, v in self.data['Arguments'].items()}
        pos_higher = {k: (v[0], v[1]+0.04) for k, v in pos.items()}
        nx.draw_networkx_labels(G, pos_higher, labels=argument_text, horizontalalignment='center', font_size=8)
        
        # Add game text to the graph
        if self.add_game_text:
            plt.text(0.5, 0.02, self.game_text, ha='center', va='center', transform=plt.gcf().transFigure)
        
        if self.save_graph:
            plt.savefig('game_output.png')

        plt.show(block=False)

    def proponent_turn(self):
        if not self.proponent_arguments:
            argument = self.claimed_argument
        else:
            # Find an argument that attacks the opponent's last argument and has not been used by the proponent
            for relation in self.data['Attack Relations']:
                if relation[1] == self.opponent_arguments[-1] and relation[0] not in self.proponent_arguments:
                    argument = relation[0]
                    break
            else:
                print("Proponent cannot make a move. Opponent wins!")
                return False

        self.proponent_arguments.append(argument)
        print(f"Proponent's argument: {self.data['Arguments'][argument]}")
        self.draw_graph()
        if self.verbose:
            print("Game state:", self.__dict__)
        return True

    def opponent_turn(self):
        options = [relation[0] for relation in self.data['Attack Relations'] if relation[1] == self.proponent_arguments[-1] and relation[0] not in self.opponent_arguments]

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
        print(f"Opponent's argument: {self.data['Arguments'][argument]}")
        # self.draw_graph()
        if self.verbose:
            print("Game state:", self.__dict__)
        return True

    def play(self):
        while True:
            print("Proponent's turn...")
            if not self.proponent_turn():
                break
            self.game_text += f"Proponent's turn...\nProponent's argument: {self.data['Arguments'][self.proponent_arguments[-1]]}\n"
            print("Opponent's turn...")
            if not self.opponent_turn():
                break
            self.game_text += f"Opponent's turn...\nOpponent's argument: {self.data['Arguments'][self.opponent_arguments[-1]]}\n"
        self.draw_graph()  # Draw the graph after the game



game = Game('./Argumentation_Framework_tests/test3.json', '0', verbose=False, show_graph=True, save_graph=True, add_game_text=True)
game.play()
