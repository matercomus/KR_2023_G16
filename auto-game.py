import json
from game import Game  # Import the Game class from the game module


def choose_proponent_move(game, options):
    """
    Choose the option with the highest difference
    between the number of successors and predecessors
    """
    options.sort(
        key=lambda option: len(list(game.G.successors(option)))
        - len(list(game.G.predecessors(option))),
        reverse=True,
    )
    return options[0]


def choose_opponent_move(game, options):
    """
    Choose the option with the highest number of successors
    """
    options.sort(key=lambda option: len(list(game.G.successors(option))), reverse=True)
    return options[0]


def play_games(
    n,
    data_file,
    claimed_argument,
    verbose=False,
    show_graph=False,
    save_graph=False,
    add_game_text=False,
):
    results = []
    for i in range(n):
        game = Game(
            data_file,
            claimed_argument,
            verbose,
            show_graph,
            save_graph,
            add_game_text,
            choose_proponent_move,
            choose_opponent_move,
        )
        game.play()
        results.append(
            {
                "proponent_arguments": game.proponent_arguments,
                "opponent_arguments": game.opponent_arguments,
                "winner": "proponent"
                if len(game.opponent_arguments) == 0
                else "opponent",
            }
        )

    with open("results.json", "w") as f:
        json.dump(results, f)


# Call the play_games function to play n games and save the results
play_games(10, "path_to_your_data_file", "your_claimed_argument")
