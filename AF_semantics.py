import os
import json
from itertools import combinations


class ArgumentationFramework:
    def __init__(self, data_file, argument):
        data = self.load_data(data_file)
        self.argument = argument
        self.arguments = list(data["Arguments"].keys())
        self.attacks = tuple(tuple(pair) for pair in data["Attack Relations"])

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

    # Fast check
    def fast_check(self):
        is_attacked = False
        for relation in self.attacks:
            if relation[0] == relation[1] and relation[1] == self.argument:
                print(f"'{self.argument}' attacks itself, this argument is NOT credulously acceptable under Admissible Semantics.")
                return exit(0)
            elif relation[1] == self.argument:
                is_attacked = True
        return is_attacked

    # Function to check if an argument is credulously accepted under admissible semantics
    def is_credulously_accepted(self):
        # Generate all possible subsets of arguments that include the argument in question
        subsets = self.subsets_containing_target()
        for subset in subsets:
            if argument in subset and self.is_conflict_free(subset):
                if all(self.defends(subset, arg) for arg in subset):
                    print(f"'{self.argument}' is credulously acceptable under Admissible Semantics.")
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

    def subsets_containing_target(self):
        # First ensure that the target is in the set
        if self.argument not in self.arguments:
            print('The provided argument does not appear in the AF.')
            return exit(0)
        # Remove the target from the set temporarily to generate combinations of other elements
        self.arguments.remove(self.argument)
        # Use a list to accumulate subsets
        subsets = [tuple([self.argument])]
        # Generate all possible combinations of the remaining elements
        for i in range(1, len(self.arguments) + 1):
            for combo in combinations(self.arguments, i):
                subsets.append(tuple([self.argument]) + combo)
        # Convert the list of tuples into a set
        return set(subsets)

path = os.path.join(os.getcwd(), "Argumentation_Framework_tests/AF_test_3.json")
argument = "A"

af = ArgumentationFramework(path, argument)