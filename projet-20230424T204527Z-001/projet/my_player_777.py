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
        print("------")
        print("player:", player)
        print("step:", step)
        print("time left:", time_left if time_left else '+inf')
        board = dict_to_board(percepts)
        vertical_middle = 3
        ennemy_pos = board.pawns[1-player]
        my_pos = board.pawns[player]
        isRightSide = False
        # print(board.horiz_walls)
        # print(board.verti_walls)

        if (time_left < 60):
            return get_first_move_sh_path(board,player)
        # ------------------------ first player
        if (ennemy_pos[1] <= vertical_middle):
            print("left side")
        else:
            print("right side")
            isRightSide = True
        if player == 0:
            if not isRightSide and ennemy_pos[0] <= my_pos[0]:
                if (board.is_wall_possible_here((0, 2), True)):
                    return ('WH', 0, 2)
                if (board.is_wall_possible_here((0, 0), True)):
                    return ('WH', 0, 0)

            # garantie
            # vertical middle wall
            if (step == 1):
                return ('WV', 0, 3)
            if (set([(0,3)]).issubset(board.verti_walls) and board.is_wall_possible_here((2, 3), False)):
                return ('WV', 2, 3)
            if (set([(0,3),(2, 3)]).issubset(board.verti_walls) and board.is_wall_possible_here((4, 3), False)):
                return ('WV', 4, 3)
            if (set([(0,3),(2, 3),(4, 3)]).issubset(board.verti_walls) and board.is_wall_possible_here((6, 3), False)):
                return ('WV', 6, 3)
            
            #second option
            if (set([(0, 4)]).issubset(board.horiz_walls) and my_pos == [0,4]) and board.is_wall_possible_here((0, 7), False):
                return ('WH', 0, 7)
            if (set([(0, 4), (0, 7)]).issubset(board.horiz_walls) and my_pos[0] == 0):
                return get_first_move_sh_path(board,player)
            if (set([(0, 4), (0, 7)]).issubset(board.horiz_walls) and my_pos[0] == 1 and board.is_wall_possible_here((1, 6), True)):
                return ('WH', 1, 6)
            if (set([(0, 4), (0, 7), (1, 6)]).issubset(board.horiz_walls) and my_pos[0] == 1):
                if board.is_wall_possible_here((0, 5), False):
                    return ('WV', 0, 5)
                else: return get_first_move_sh_path(board,player)
            # if  set([(0,5)]).issubset(board.verti_walls) and ennemy_pos == [1,7] and board.is_wall_possible_here((0, 6), False):
            #         return ('WV', 0, 6)
            
            #horizontal wall most common option
            if (set([(0,3),(2, 3),(4, 3),(6,3)]).issubset(board.verti_walls) and board.is_wall_possible_here((0, 4), True) and my_pos[0] == 1):
                return ('WH', 0, 4)
            if (set([(0, 4)]).issubset(board.horiz_walls) and board.is_wall_possible_here((0, 6), True)):
                return ('WH', 0, 6)
            if (set([(0, 4),(0, 6)]).issubset(board.horiz_walls) and board.is_wall_possible_here((1, 7), True)):
                return ('WH', 1, 7)
            # if (set([(0, 4),(0, 6)]).issubset(board.horiz_walls) and board.is_wall_possible_here((1, 7), True)) and (set([(0, 2)]).issubset(board.horiz_walls) or set([(0, 4)]).issubset(board.horiz_walls)):
            #     return ('WH', 1, 7)

            #horizontal mid wall block
            if (set([(0,3),(2, 3),(4, 3),(6,3)]).issubset(board.verti_walls) and set([(1,4)]).issubset(board.horiz_walls)):
                if board.is_wall_possible_here((1, 7), True):
                    return ('WH', 1, 7)

            # stall oponent and wall the right side
            if (set([(0, 4),(0, 6), (1, 7)]).issubset(board.horiz_walls) and isRightSide and ennemy_pos[0] <= my_pos[0]):
                if board.is_wall_possible_here((0, 7), False):
                    return ('WV', 0, 7)

            # detect if oponnent is trying to close other side
            if ((set([(0, 4),(0, 6), (1, 7)]).issubset(board.horiz_walls) and isRightSide)) and (set([(0, 0)]).issubset(board.horiz_walls) or set([(0, 2)]).issubset(board.horiz_walls)):
                if board.is_wall_possible_here((0, 7), False):
                    return ('WV', 0, 7)

            if isRightSide and set([(0, 4),(0, 6), (1, 7)]).issubset(board.horiz_walls) and ennemy_pos[0] - 1 >= my_pos[0]:
                return get_first_move_sh_path(board,player)

            if ennemy_pos[0] - 1 <= my_pos[0]:
                print("min-max 2")
                return self.minmax_alpha_beta_pruning(board, player)

            if isRightSide and set([(0, 7)]).issubset(board.verti_walls):
                return get_first_move_sh_path(board,player)

        # ------------------------

        # if (step == 2):
        #     return ('WV', 7, 3)
        # if (step == 4 and board.is_wall_possible_here((1, 3), True)):
        #     return ('WH', 6, 3)
        # if (step == 6 and board.is_wall_possible_here((2, 3), False)):
        #     return ('WV', 5, 3)

        enemy_goal = board.goals[1-player]
        my_y, _ = board.pawns[player]
        my_distance = abs(enemy_goal - my_y)
        if board.nb_walls[1-player] == 0:
            
            try:
                sh_path_player = len(board.get_shortest_path(player))
                sh_path_opp = len(board.get_shortest_path(1-player))
                if sh_path_player < sh_path_opp:
                    return get_first_move_sh_path(board,player)
            except NoPath:
                pass
        if (my_distance < 1 and step < 20) or time_left < 60 or board.nb_walls[player] == 0:
            return get_first_move_sh_path(board,player)
        print("--------MINIMAX--------------")
        action = self.minmax_alpha_beta_pruning(board, player)
        return action

    def minmax_alpha_beta_pruning(self, board, player):
        infinity = math.inf

        def max_value(board, alpha, beta, depth):
            if cutoff(board, depth):
                return board.get_score(player), None
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
                return board.get_score(player), None
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
        print("score")
        print(_)
        print(action)
        return action

def cutoff(board: Board, depth):
    return board.is_finished() or depth >= 2

def actions(board, player):
    return pogne_murs(board, player)

def walls_around_player(wall, player):
    return (abs(wall[0] - player[0]) <= 1) and (abs(wall[1]-player[1]) <= 1)

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
        elif walls_around_player(a_pos, my_pos):
            good_action.append(a)
    return good_action

def get_first_move_sh_path(board: Board, player):
    try:
        shortest_path = board.get_shortest_path(player)
        next_y, next_x = shortest_path[0]
    except:
        print('get_shortest_path error')
        shortest_path = board.get_legal_pawn_moves(player)
        _, next_y, next_x = shortest_path[0]
    # print("sh")
    # print(shortest_path)
    next_move = ('P', next_y, next_x)
    return next_move


if __name__ == "__main__":
    agent_main(MyAgent())
