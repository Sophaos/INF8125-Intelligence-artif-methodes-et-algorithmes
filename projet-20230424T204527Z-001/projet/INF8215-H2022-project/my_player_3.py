#!/usr/bin/env python3
"""
Quoridor agent.
Copyright (C) 2013, <<<<<<<<<<< YOUR NAMES HERE >>>>>>>>>>>
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

# Guillaume Thibault : 1948612
# Jacob Brisson : 1954091

import math
from heuristic_1948612_1954091 import *
from quoridor import *
from utils_1948612_1954091 import *
from time import sleep, time
import traceback
global_actions = []


def minimax_search(current_board, my_player, cutoff,
                   h=lambda b, p, **k: 0,
                   worth_exploring_h=lambda a, b, p, **k: True,
                   time_left=0,
                   **kwargs):
    """
    Minimax Algo for Quoridor
    @params:
        - current_board: Current stage of the game to analyse with minimax
        - my_player: my player number
        - cutoff: cutoff depth to stop the minimax and use the heuristic
        - h: heuristic use for the leaf evaluation a the cutoff depth (base h: always return 0)
        - pruning_h: heuristic use to evaluate if the leaf is worth evaluating (base h: always True)
    @return
        - best_action found
    """

    infinity = math.inf
    initial_time = time()

    def max_value(board, player, alpha, beta, depth, try_deeper=False, init_time=0.0, time_left=0.0):
        # End of the game
        if board.is_finished():
            return utility(board, my_player), None
        # If we want to look deeper into this branch
        if depth > (cutoff + 2):
            return h(board, my_player, **kwargs), None
        # Else, return the heuristic value if the current depth is higher than the cutoff value
        if depth > cutoff and not try_deeper:
            return h(board, my_player, **kwargs), None
        max_v = -infinity
        best_action = None
        for action in board.get_actions(player):
            new_board = board.clone()
            # Stop if it has been too much time or if there is not much time left
            time_now = time()
            if (time_now - init_time) > 25 and time_left <= 75 or ((time_now - init_time) > 45 and time_left <= 100):
                action = ('P', *get_shortest_path_simplified(board, player)[0])
                return 90, action
            # We want to prioritize actions where the player can jump over the other player in the direction of his goal
            if depth == 0:
                if player == 0:
                    direction = 2
                else:
                    direction = -2
                if action_is_move(action) and action[1] == (board.pawns[player][0] + direction):
                    return 90, action

            # See if the action is worth testing and look deeper into it if it is a pawn move that is on the shortest path to the goal
            if worth_exploring_h(action, new_board, player, **kwargs):
                try:
                    try_deeper = True if action_is_move(action) and \
                                         (action[1], action[2]) in new_board.get_shortest_path(player) else False
                except:
                    try_deeper = False
                next_state = new_board.play_action(action, player)
                (value, _) = min_value(next_state, other_player(player), alpha, beta, depth + 1, try_deeper, init_time, time_left)
                if try_deeper:
                    print(f"action {action} : {value} ")
            # If the action is not woth exploring, this gives a general value for it without going deeper into the tree
            else:
                next_state = new_board.play_action(action, player)
                value = heuristic_general(next_state, my_player, **kwargs)

            # If the action is the same as the one taken 2 turns ago, give a negative penalty to its value. This is to avoid the fact that the player is stuck in a loop of repeating actions
            if len(global_actions) > 2 and action == global_actions[len(global_actions) - 2]:
                value -= 5

            if value > max_v:
                max_v = value
                best_action = action
                alpha = max(alpha, max_v)
            if max_v >= beta:
                return max_v, best_action
        global_actions.append(best_action)
        return max_v, best_action

    def min_value(board, player, alpha, beta, depth, try_deeper=False, init_time=0, time_left=0):
        """
        This function is similar to max_value, but it is minimizing the score of the player
        """
        if board.is_finished():
            return utility(board, my_player), None
        if depth > (cutoff + 2):
            return h(board, my_player, **kwargs), None
        if depth > cutoff and not try_deeper:
            return h(board, my_player, **kwargs), None
        min_v = infinity
        best_action = None
        for action in board.get_actions(player):
            new_board = board.clone()

            time_now = time()
            if (time_now - init_time) > 25 and time_left <= 75 or ((time_now - init_time) > 45 and time_left <= 100):
                action = ('P', *get_shortest_path_simplified(board, player)[0])
                return 90, action

            if worth_exploring_h(action, new_board, player, **kwargs):
                try_deeper = True if action_is_move(action) and \
                                     (action[1], action[2]) in new_board.get_shortest_path(player) else False
                next_state = new_board.play_action(action, player)
                (value, _) = max_value(next_state, other_player(player),
                                       alpha, beta, depth + 1, try_deeper, init_time, time_left)
                if try_deeper:
                    print(f"action {action} : {value} ")
            else:
                next_state = new_board.play_action(action, player)
                value = heuristic_general(next_state, my_player, **kwargs)

            if value < min_v:
                min_v = value
                best_action = action
                beta = min(beta, min_v)
            if min_v <= alpha:
                return min_v, best_action
        return min_v, best_action

    return max_value(current_board, my_player, -infinity, +infinity, 0, init_time=initial_time, time_left=time_left)


class MyAgent(Agent):
    """My Quoridor agent."""

    def play(self, percepts, player, step, time_left):
        """
        This function is used to play a move according
        to the percepts, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        :param percepts: dictionary representing the current board
            in a form that can be fed to `dict_to_board()` in quoridor.py.
        :param player: the player to control in this step (0 or 1)
        :param step: the current step number, starting from 1
        :param time_left: a float giving the number of seconds left from the time
            credit. If the game is not time-limited, time_left is None.
        :return: an action
          eg: ('P', 5, 2) to move your pawn to cell (5,2)
          eg: ('WH', 5, 2) to put a horizontal wall on corridor (5,2)
          for more details, see `Board.get_actions()` in quoridor.py
        """
        print(f"time left at step {step}: ",
              time_left if time_left else '+inf')

        # Construct the board
        board = dict_to_board(percepts)
        try:

            #   Check if we have time to guess the best path   OR  Return quickest path if the two players have no wall
            if ((time_left <= 50) and (time_left is not None)) or (board.nb_walls[player] == 0):
                try:
                    if board.pawns[other_player(player)][0] == abs(board.goals[other_player(player)] - 1):
                        action = minimax_search(board, player, 0, heuristic_basic, time_left=time_left)
                        action = action[1]
                    else:
                        action = ('P', *board.get_shortest_path(player)[0])
                except:
                    action = minimax_search(
                        board, player, 0, heuristic_basic, time_left=time_left)
                    action = action[1]

                print(f'No Time or Wall left!, action: {action}')
                sleep(0.2)
                return action

            # Opening moves if the player is the one to start
            action = get_opening_move(board, player, step)
            if action is not None and board.is_action_valid(action, player):
                print(f"Opening #{SELECTED_OPENING} action: {action}")
                return action


            # End game
            if step > 30:
                params_h = {'range_player': 3, 'range_opp': 3}
                action = minimax_search(
                    board, player, 1, heuristic_end_game, pruning_block_player_only, time_left=time_left, **params_h)

                print(f'action choose with h1: {action}')
                return action[1]
            else:
                # Normal action found with basic heuristic
                action = minimax_search(
                    board, player, 0, heuristic_basic, time_left=time_left)
                print(f'action choose with h3: {action}')
                return action[1]

        except Exception as e:
            print(e)
            traceback.print_exc()
            # If there's an error, make a move so we are not disqualified
            actions = list(board.get_actions(player))
            return random.choice(actions)


if __name__ == "__main__":
    agent_main(MyAgent())