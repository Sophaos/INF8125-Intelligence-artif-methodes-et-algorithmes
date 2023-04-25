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

import math
from quoridor import *


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
        # print("percept:", percepts)
        print("player:", player)
        print("step:", step)
        print("time left:", time_left if time_left else '+inf')
        board = dict_to_board(percepts)
        # test = pogne_murs(board, player)
        # print(test)
        if (step == 1):
            return ('WV', 0, 3)
        enemy_goal = board.goals[1-player]
        my_y, _ = board.pawns[player]
        my_distance = abs(enemy_goal - my_y)
        if board.nb_walls[1-player] == 0:
            
            try:
                sh_path_player = len(board.get_shortest_path(player))
                sh_path_opp = len(board.get_shortest_path(1-player))
                if sh_path_player < sh_path_opp:
                    print("im shorter")
                    return get_first_move_sh_path(board,player)
            except NoPath:
                pass
        if my_distance < 2 or time_left < 60 or board.nb_walls[player] == 0:
            print("quick i got no times left !")
            return get_first_move_sh_path(board,player)
        action = self.minmax_alpha_beta_pruning(board, player)
        print("end play")
        print(action)
        return action

    def minmax_alpha_beta_pruning(self, board, player):
        infinity = math.inf

        def max_value(board, alpha, beta, depth):
            if cutoff(board, depth):
                return evaluate(board, player), None
            score, action = -infinity, None
            for a in actions(board, player):
                clone = board.clone()
                clone.play_action(a, player)
                next_board = clone
                s, _ = min_value(next_board, alpha, beta, depth + 1)
                if s > score:
                    score, action = s, a
                    alpha = max(alpha, s)
                if s >= beta:
                    return s, a

            return score, action

        def min_value(board, alpha, beta, depth):
            if cutoff(board, depth):
                return evaluate(board, player), None
            score, action = infinity, None
            for a in actions(board, player):
                clone = board.clone()
                clone.play_action(a, player)
                next_board = clone
                s, _ = max_value(next_board, alpha, beta, depth + 1)
                if s < score:
                    score, action = s, a
                    beta = min(beta, s)
                if s <= alpha:
                    return s, a
                
            return score, action

        _, action = max_value(board, -infinity, infinity, 0)

        return action

def cutoff(board: Board, depth):
    return board.is_finished() or depth >= 2

def evaluate(board: Board, player):
    # test = board.get_score(player)
    # print(test)
    shortestDistanceDiff = board.get_score(player)
    wallsDiff = board.nb_walls[player] - board.nb_walls[1 - player]
    # total = 50*shortestDistanceDiff + wallsDiff*wallsDiff
    total = 2*shortestDistanceDiff + 4*wallsDiff
    # print(total)
    return total

def actions(board, player):
    return pogne_murs(board, player)

def walls_around_player(wall, player):
    #is wall next to player
    return (abs(wall[0] - player[0]) <=1) and (abs(wall[1]-player[1]) <= 1)

def pogne_murs(board: Board, player):
    all_pawn_moves = board.get_legal_pawn_moves(player)
    all_pawn_opp_moves = board.get_legal_pawn_moves(1-player)
    all_wall_moves = board.get_legal_wall_moves(player)
    good_action=[]   
    good_action.extend(all_pawn_moves)
    ennemy_pos = board.pawns[1-player]
    my_pos = board.pawns[player]
    # print(good_action)
    for a in all_wall_moves:
        a_pos = (a[1],a[2])
        if walls_around_player(a_pos, ennemy_pos): # and not len(all_pawn_opp_moves) == 2
            good_action.append(a)
        # elif walls_around_player(a_pos, my_pos):
        #     good_action.append(a)
    return good_action

def get_first_move_sh_path(board: Board, player):
    shortest_path = board.get_shortest_path(player)
    print("sh")
    print(shortest_path)
    next_y, next_x = shortest_path[0]
    next_move = ('P', next_y, next_x)
    return next_move

# def manhattan(pos1, pos2):
#     return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

if __name__ == "__main__":
    agent_main(MyAgent())
