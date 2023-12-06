import os
import json
import networkx as nx

# DEFENDERS
# no loop to itself
# all attackers ( paernets ) need to have a defender ( grandparent ) to counter, or so on and so on...
# In order to be conflict free the defender canot be attacked by the argument itself.
# 


class ArgumentationFramework:
    def __init__(self, data_file, argument):
        self.CFS = {}
        self.argument = argument
        self.data = self.load_data(data_file)

        # Initialize the graph
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.data["Arguments"].keys())
        self.G.add_edges_from(self.data["Attack Relations"])

        # Get attackers of the argument.
        self.attackers = list(self.G.predecessors(self.argument))
        print('Attackers: ', self.attackers)
        self.compute_defenders()
        print('Defenders: ', self.CFS)
        self.check_defenders()

    def compute_defenders(self):
        for attacker in self.attackers:
            defenders = list(self.G.predecessors(attacker))
            if len(defenders) == 0:
                print(f"'{self.argument}' is not credulously acceptable under the respective semantics")
                return False
            else:
                self.CFS[attacker] = defenders

    def check_defenders(self):
        for attacker, defenders in self.CFS.items():
            for defender in defenders:
                parents = list(self.G.predecessors(defender))
                if len(parents) == 0:
                    del self.CFS[attacker]
                    break
                if self.G.has_edge(defender, defender):
                    continue
                else:
                    self.find_and_add_defenders(parents)
            if len(self.CFS) == 0:
                print(f"'{self.argument}' is credulously acceptable under the respective semantics in a given AF")
                return True

    def find_and_add_defenders(self, attackers):
        for attacker in attackers:
            defenders = list(self.G.predecessors(attacker))
            self.CFS[attacker] = defenders


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
path = os.path.join(os.getcwd(), "Argumentation_Framework_tests/AF_test_1.json")
argument = "B"

af = ArgumentationFramework(path, argument)
