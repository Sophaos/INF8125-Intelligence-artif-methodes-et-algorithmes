# Guillaume Thibault : 1948612
# Jacob Brisson : 1954091


import random
from utils_1948612_1954091 import *
from opening_1948612_1954091 import *

# ~~~~~~~~~~ Opening Move ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OPENINGS = [RUSH_OPENING, SIDE_WALL_OPENING,
            GAP_OPENING, SHILLER_OPENING]

SELECTED_OPENING = random.randint(0, 3)

print(SELECTED_OPENING)


def get_opening_move(board, player, step):
    # Return the move
    if step in OPENINGS[SELECTED_OPENING].keys():
        action = OPENINGS[SELECTED_OPENING][step]
        if board.is_action_valid(action, player):
            return action
        else:
            try:
                action = ('P', *board.get_shortest_path(player)[0])
                if board.is_action_valid(action, player):
                    return action
            except:
                return None
    return None


# ~~~~~~~~~~ Evaluation Heuristic ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def heuristic_basic(board, player, **kwargs):
    """
    Heuristic that only considers the distance to the goal of both players and the number of walls
    """
    try:
        distance = board.min_steps_before_victory(other_player(player)) - board.min_steps_before_victory(player)
    except:
        distance = len(get_shortest_path_simplified(board, other_player(player))) - \
            len(get_shortest_path_simplified(board, player))

    walls = board.nb_walls[player] - board.nb_walls[other_player(player)]

    try:
        # If the other player is one step away from winning, return a negative value for this state
        if board.pawns[other_player(player)][0] == abs(board.goals[other_player(player)] - 1) and \
                board.min_steps_before_victory(other_player(player)) <= 1:
            return -(100 - board.min_steps_before_victory((player + 1) % 2))
    except:
        print("Error occured while finding if the other player is winning on the next step")

    return 5 * distance + 2 * walls


def heuristic_general(board, player, **kwargs):
    """
    Heuristic using the distance to the goal of both players, the number of walls, the number of paths behind and in
    front of the player, the number of walls behind the player and custom weights for the different features
    """
    # Weights of the features
    if 'theta' in kwargs.keys():
        theta_0, theta_1, theta_2, theta_3 = kwargs['theta']
    else:
        theta_0, theta_1, theta_2, theta_3 = 5, 2, 2, 1

    # Number of paths behind and in front of the player
    paths_forward = number_of_paths(board, other_player(player), True)
    paths_backwards = number_of_paths(board, player, True)

    path_heuristic = paths_forward - paths_backwards

    # Number of walls behind the player
    wall_heuristic = number_of_wall_behind(board, player)

    # Difference of distances to the goal of both players
    try:
        diff_distance = board.min_steps_before_victory(
            other_player(player)) - board.min_steps_before_victory(player)
        # Check if other player will win
        if board.pawns[other_player(player)][0] == abs(board.goals[other_player(player)] - 1) \
                and board.min_steps_before_victory(other_player(player)) <= 2 \
                and board.min_steps_before_victory(player) > 1:
            return -(100 - board.min_steps_before_victory(other_player(player)))

    except:
        diff_distance = len(get_shortest_path_simplified(board, other_player(player))) - \
            len(get_shortest_path_simplified(board, player))

    # Number of walls
    diff_walls = board.nb_walls[player] - board.nb_walls[other_player(player)]

    pos_value = 0
    if player == 0 and board.pawns[player][0] == 0:
        pos_value -= 1

    elif player == 1 and board.pawns[player][0] == 8:
        pos_value -= 1

    return theta_0 * diff_distance + theta_1 * diff_walls + theta_2 * path_heuristic + theta_3 * wall_heuristic + pos_value


def heuristic_0_wall(board, player):
    """
    Heuristic to use if there is no wall move left
    """
    try:
        distance = 100 - len(get_shortest_path_simplified(board, player))
    except:
        distance = 0
    return distance


def heuristic_end_game(board, player, **kwargs):
    """
    Heuristic for the end of the game using the distances to the goal of both players, the number of walls behind the player
    and the value of the actual position on the board of the player
    """
    try:
        player_path = get_shortest_path_simplified(board, player)
        distance = len(get_shortest_path_simplified(
            board, other_player(player))) - len(player_path)
    except:
        return heuristic_general(board, player)

    if board.nb_walls[other_player(player)] == 0 and distance > 0:
        return heuristic_0_wall(board, player)

    pos_value = position_value(board, player)
    wall_heuristic = number_of_wall_behind(board, player)

    return 5 * distance + 10 * wall_heuristic + pos_value


# ~~~~~~~~~~ Pruning Heuristic ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def pruning_block_player_only(action, board, player, **kwargs) -> bool:
    """
    Strategy: Only consider actions that blocks the other player.
        With parameter from kwargs: Can consider wall near, if it block my player,
    @params:
        - action: current action to test
        - board: Board state to analyse the action with
        - player: Player number
        - kwargs:
            * depth_cut: int -> to stop the path search at a certain position.
            * consider_me: bool -> if we should not block ourself
            * consider_near_adv: bool -> if we want to consider the wall near the pon
            * range_near_pon: int -> Distance of the adv pon to consider
    @return:
        - bool: if it is a worthy move to explore
    """

    # Extract extra parameter form kwargs
    depth_cut = kwargs['depth_cut'] if 'depth_cut' in kwargs.keys() else -1
    should_not_block_my_pon = kwargs['consider_me'] if 'consider_me' in kwargs.keys() else False
    consider_near_adv = kwargs['consider_near_adv'] if 'consider_near_adv' in kwargs.keys() else False
    range_near_pon = kwargs['range_near_pon'] if 'range_near_pon' in kwargs.keys() else 2

    my_path, adv_path = get_pons_shortest_paths(board, player)

    block_adv = False
    block_me = False
    should_explore = False

    if action_is_move(action):
        should_explore = True
    elif action_is_wall(action):
        wall_increasing_path = is_wall_increasing_path(board, other_player(player), action)
        block_adv = is_wall_blocking_path(action, adv_path, depth_cut) or wall_increasing_path
        block_me = is_wall_blocking_path(action, my_path, depth_cut)
    if consider_near_adv and action_is_wall(action):
        should_explore = is_wall_near_pon(action, adv_path[0], range_near_pon)
    if should_not_block_my_pon:
        return should_explore or (block_adv and not block_me)

    return should_explore or block_adv


def pruning_wall_near(action, board, player, **kwargs) -> bool:
    """
    Strategy: Only consider actions that are near our pawn of the opponent's pawn.
    @params:
        - action: current action to test
        - board: Board state to analyse the action with
        - player: Player number
        - kwargs:
            * range_player: int -> radius near our pawn to test
            * range_opp: int -> radius near the opponent's pawn to test
    @return:
        - bool: if it is a worthy move to explore
    """
    range_player = kwargs['range_player'] if 'range_player' in kwargs.keys(
    ) else 1
    range_opp = kwargs['range_opp'] if 'range_opp' in kwargs.keys() else 1

    if action_is_move(action) \
            or (range_opp != 0 and is_wall_near_pon(action, board.pawns[other_player(player)], range_opp)) \
            or is_wall_near_pon(action, board.pawns[player], range_player):
        return True
    return False