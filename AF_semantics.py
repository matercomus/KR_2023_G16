import os
import json
import argparse
from itertools import combinations


class ArgumentationFramework:
    def __init__(self, data_file, argument):
        data = self.load_data(data_file)
        self.argument = argument
        self.arguments = set(data["Arguments"].keys())
        self.attacks = {tuple(pair) for pair in data["Attack Relations"]}
    
    def compute(self):
        # First ensure that the target is in the set
        if self.argument not in self.arguments:
            print('The provided argument does not appear in the AF.')
            return exit(0)
        fast_check = self.fast_check()
        if not fast_check:
            print(f"'{self.argument}' has no attackers, this argument is credulously acceptable under Admissible Semantics.")
        if fast_check:
            self.is_credulously_accepted()

    # Load the data from the file
    def load_data(self, data_file):
        with open(data_file, "r") as f:
            data = json.load(f)
        return data

    # Function to check the argument itself and optimize computation.
    def fast_check(self):
        is_attacked = False
        for relation in self.attacks:
            if relation[0] == relation[1] and relation[1] == self.argument:  # Check loop to itself
                print(f"'{self.argument}' attacks itself, this argument is NOT credulously acceptable under Admissible Semantics.")
                return exit(0)
            elif relation[0] == relation[1]: # Check for loop
                self.arguments.discard(relation[0]) # Delete because it canot defend
                
            elif relation[1] == self.argument:
                is_attacked = True
                self.arguments.discard(relation[0]) # Delete because it attacks the argument

        return is_attacked

    # Function to check if an argument is credulously accepted under admissible semantics
    def is_credulously_accepted(self):
        subsets = self.subsets_containing_target()
        for subset in subsets:
            if self.is_conflict_free(subset):
                if all(self.defends(subset, arg) for arg in subset):
                    print(f"'{self.argument}' is credulously acceptable under Admissible Semantics.")
                    print(subset)
                    return True
        print(f"'{self.argument}' is NOT credulously acceptable under Admissible Semantics.")
        return False

    # Function to check if a set of arguments is conflict-free
    def is_conflict_free(self, s):
        return not any((a, b) in self.attacks or (b, a) in self.attacks for a in s for b in s)

    # Function to check if a set defends an argument
    def defends(self, s, argument):
        attackers = {attacker for attacker, target in self.attacks if target == argument}
        return all(any((defender, attacker) in self.attacks for defender in s) for attacker in attackers)
    
    # Function to generate all possible subsets with the given argument
    def subsets_containing_target(self):
        self.arguments.discard(self.argument)
        subsets = {tuple([self.argument])}
        for i in range(1, len(self.arguments) + 1):
            for combo in combinations(self.arguments - {self.argument}, i):
                subsets.add(tuple([self.argument]) + combo)
        return subsets


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", type=str, help="The path to the data file.")
    parser.add_argument("argument", type=str, help="The claimed argument.")
    args = parser.parse_args()

    ArgumentationFramework(args.data_file, args.argument).compute()
