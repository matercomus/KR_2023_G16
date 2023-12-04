import os
import json
import networkx as nx


class ArgumentationFramework:
    def __init__(self, data_file, argument):
        self.argument = argument
        self.data = self.load_data(data_file)

        # Initialize the graph
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.data["Arguments"].keys())
        self.G.add_edges_from(self.data["Attack Relations"])

        self.has_grandparent()

    # Load the data from the file
    def load_data(self, data_file):
        with open(data_file, "r") as f:
            data = json.load(f)
        return data

    def has_grandparent(self):
        # Check if the graph contains the node
        if self.argument not in self.G:
            print("this argument does not apper in the AF.")
            return False

        parents = self.G.predecessors(self.argument)
        # If argument has no parents, then it's acceptable
        if not parents:
            print(
                f"'{self.argument}' is credulously acceptable under the respective semantics in a given AF"
            )
            return True
        # If argument is it's own parent, then it's not acceptable
        if self.argument in parents:
            print(
                f"'{self.argument}' is not credulously acceptable under the respective semantics"
            )
            return False

        # Iterate over the parents of the node
        for parent in parents:
            # Check if any parent has its own parent
            if len(list(self.G.predecessors(parent))) == 0:
                print(
                    f"'{self.argument}' is not credulously acceptable under the respective semantics in a given AF"
                )
                return False

        print(
            f"'{self.argument}' is credulously acceptable under the respective semantics in a given AF"
        )
        return True

    def is_conflict_free(self, args_set):
        for arg in args_set:
            for attacked in self.attack_relations.get(arg, []):
                if attacked in args_set:
                    return False
        return True


# Define the full file path
path = os.path.join(os.getcwd(), "Argumentation_Framework_tests/AF_accept_test.json")
argument = "E"

af = ArgumentationFramework(path, argument)
