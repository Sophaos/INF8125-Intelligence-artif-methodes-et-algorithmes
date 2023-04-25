# Guillaume Thibault : 1948612
# Jacob Brisson : 1954091

from quoridor import NoPath


def other_player(player):
    """
    Function to give the other player's number
    """
    return (player + 1) % 2


def utility(board, player):
    """
    Utility function, returning 100 if the player wins and -100 if he loses
    """
    if board.pawns[player][0] == board.goals[player]:
        return 100
    elif board.pawns[other_player(player)][0] == board.goals[other_player(player)]:
        return -100
    return 0


def action_is_wall(action):
    """
    Tell if an action is a wall move
    """
    return True if 'W' in action[0] else False


def action_is_horizontal_wall(action):
    """
    Tell if an action is a horizontal wall move
    """
    return True if 'WH' in action[0] else False


def action_is_vertical_wall(action):
    """
    Tell if an action is a vertical wall move
    """
    return True if 'WV' in action[0] else False


def action_is_move(action):
    """
    Tell if an action is a pawn move
    """
    return True if 'P' in action[0] else False


def is_wall_near_pon(wall, pon_pos, r=2) -> bool:
    """
    See if a wall move is near the pawn inside a radius of value r
    """
    wall_position = wall[1:]
    if (wall_position[0] - r < pon_pos[0] < wall_position[0] + r) \
            and (wall_position[1] - r < pon_pos[1] < wall_position[1] + r):
        return True
    return False


def is_wall_blocking_path(wall, path, depth_block=-1) -> bool:
    """
    See if a wall move blocks the path of the other player
    """
    wall_position = wall[1:]

    for i in range(1, len(path)):
        # Cutoff a depth_block
        if 0 < depth_block < i:
            break
        # get the pawn moves
        live_square = path[i - 1]
        next_square = path[i]

        # Condition for a horizontal wall
        if action_is_horizontal_wall(wall):
            if (live_square[0] == wall_position[0]) and (next_square[0] == wall_position[0] + 1) and \
                    (live_square[1] == wall_position[1] or live_square[1] == wall_position[1] + 1):
                return True  # wall on the pawn path

        # Condition for a vertical wall
        elif action_is_vertical_wall(wall):
            if (live_square[1] == wall_position[1]) and (next_square[1] == wall_position[1] + 1) and \
                    (live_square[0] == wall_position[0] or live_square[0] == wall_position[0] + 1):
                return True  # wall on the pawn path

    return False  # wall not on the pawn path


def get_shortest_path_simplified(board, player, actual_pos=(-1, -1), end_pos=(-1, -1)):
    """
    Function adapted from get_shortest_path. It uses is_simplified_pawn_move_ok instead of is_pawn_move_ok to find the
      legal pawn moves, so that it wont crash because of a No_path exception. It also can find the shortest path between
      any inital position and final position, specified in the parameters
    """

    def get_pawn_moves(pos):
        (x, y) = pos
        positions = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                     (x + 1, y + 1), (x - 1, y -
                                      1), (x + 1, y - 1), (x - 1, y + 1),
                     (x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2)]
        moves = []
        for new_pos in positions:
            if board.is_simplified_pawn_move_ok(pos, new_pos):
                moves.append(new_pos)
        return moves

    if actual_pos == (-1, -1):
        actual_pos = board.pawns[player]
    if end_pos == (-1, -1):
        end_pos = (board.goals[player], [0, 1, 2, 3, 4, 5, 6, 7, 8])
    (a, b) = actual_pos
    if a == end_pos[0] and b in end_pos[1]:
        return []
    visited = [[False for i in range(board.size)] for i in range(board.size)]
    # Predecessor matrix in the BFS
    prede = [[None for i in range(board.size)] for i in range(board.size)]
    neighbors = [actual_pos]
    while len(neighbors) > 0:
        neighbor = neighbors.pop(0)
        (x, y) = neighbor
        visited[x][y] = True
        if x == end_pos[0] and y in end_pos[1]:
            succ = [neighbor]
            curr = prede[x][y]
            while curr is not None and curr != actual_pos:
                succ.append(curr)
                (x_, y_) = curr
                curr = prede[x_][y_]
            succ.reverse()
            return succ
        unvisited_succ = [(x_, y_) for (x_, y_) in
                          get_pawn_moves(neighbor) if not visited[x_][y_]]
        for n_ in unvisited_succ:
            (x_, y_) = n_
            if not n_ in neighbors:
                neighbors.append(n_)
                prede[x_][y_] = neighbor
    raise NoPath()


def get_pons_shortest_paths(board, player) -> (list, list):
    """
    Get the shortest path of each player with their current position
    """
    adv = other_player(player)
    try:
        adv_shortest_path = board.get_shortest_path(adv)
    except:
        adv_shortest_path = get_shortest_path_simplified(board, adv)
    adv_shortest_path.insert(0, tuple(board.pawns[adv]))
    try:
        my_shortest_path = board.get_shortest_path(player)
    except:
        my_shortest_path = get_shortest_path_simplified(board, player)

    my_shortest_path.insert(0, tuple(board.pawns[player]))

    return my_shortest_path, adv_shortest_path


def is_wall_increasing_path(board, player, action) -> bool:
    """
    Find if a wall move is increasing the path of the opponent pawn
    """
    if is_wall_near_pon(action, board.pawns[player]):
        new_board = board.clone()
        try:
            init_path_len = new_board.min_steps_before_victory(player)
        except:
            init_path_len = len(
                get_shortest_path_simplified(new_board, player))
        next_state = new_board.play_action(action, player)
        try:
            new_path_len = next_state.min_steps_before_victory(player)
        except:
            new_path_len = len(
                get_shortest_path_simplified(next_state, player))
        if new_path_len > init_path_len:
            return True

    return False


def number_of_paths(board, player, inv):
    """
    Find the number of paths in front or behind the player. If the inv parameter is true, then it is the number of paths
    behind. A path is defined as a hole through a wall in front or behind the player
    """
    y_pawn = board.pawns[player][0]
    x_pawn = board.pawns[player][1]
    # Get the direction in which we want to iterate
    if player == 0:
        if inv:
            direction = -1
        else:
            direction = 1
    else:
        if inv:
            direction = 1
        else:
            direction = -1

    wall_found = False
    wall_pos = {}
    y = y_pawn
    y_goal = board.goals[player]
    if inv:
        y_goal = board.goals[other_player(player)]

    # Search for walls in front or behind the player and save the corresponding x position
    while not wall_found and y != y_goal:
        for i in range(9):
            if not board.is_simplified_pawn_move_ok((y, i), (y+direction, i)):
                wall_found = True
                if(y in wall_pos):
                    wall_pos[y].append(i)
                else:
                    wall_pos[y] = [i]
        y += direction
    paths = 0
    keys = [key for key in wall_pos.keys()]

    # If a wall was found
    if len(keys) > 0:
        pos_x = [x for x in wall_pos[keys[0]]]
        new_board = board.clone()
        # Find holes in the found walls
        for i in range(10):
            if (i in pos_x or i == 9) and i-1 not in pos_x and i-1 >= 0:
                paths += 1
                # Block the path to this hole for the player
                if i-1 < x_pawn:
                    new_board.verti_walls.append(
                        [0, i-1])
                    new_board.verti_walls.append(
                        [2, i-1])
                    new_board.verti_walls.append(
                        [4, i-1])
                    new_board.verti_walls.append(
                        [6, i-1])
                    new_board.verti_walls.append(
                        [7, i-1])
                else:
                    new_board.verti_walls.append(
                        [0, i-2])
                    new_board.verti_walls.append(
                        [2, i-2])
                    new_board.verti_walls.append(
                        [4, i-2])
                    new_board.verti_walls.append(
                        [6, i-2])
                    new_board.verti_walls.append(
                        [7, i-2])
                # See if there still is a way to finish the game for the player
                try:
                    shortest_path = get_shortest_path_simplified(
                        board=board, player=player, end_pos=(board.goals[other_player(player)], [0, 1, 2, 3, 4, 5, 6, 7, 8]))
                except:
                    return paths

    else:
        return 2

    return max(1, paths)


def number_of_wall_behind(board, player):
    """
    Find the number of horizontal walls behind the player. The value is better if the wall is closer to the player's back
    """
    overall_value = 0
    for wall in board.horiz_walls:
        if player == 0 and wall[0] < board.pawns[player][0]:
            overall_value += 1/(2*(board.pawns[player][0] - wall[0]))
        elif player == 1 and wall[0] > board.pawns[player][0]:
            overall_value += 1/(2*(wall[0] - board.pawns[player][0]))

    return overall_value


def position_value(board, player):
    """
    Gives a negative value to positions near the walls of the board, so that the player won't get trapped on the sides
    """
    value = 0
    if board.pawns[player][1] == 1 or board.pawns[player][1] == 7:
        value -= 1

    return value