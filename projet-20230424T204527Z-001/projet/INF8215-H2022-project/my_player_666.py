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
        test = pogne_murs(board, player)
        print(test)
        action = self.search(board, player)

        # TODO: implement your agent and return an action for the current step.
        return action

    def search(self, board, player):
        infinity = math.inf
        def max_value(board, alpha, beta, depth):
            if cutoff(board, depth):
                return evaluate(board, player), None
            val, action = -infinity, None
            for a in successors(board, player):
                clone = board.clone()
                clone.play_action(a, player)
                next_state = clone
                v, _ = min_value(next_state, alpha, beta, depth + 1)
                if v > val:
                    val, action = v, a
                if v >= beta:
                    return v, a
                alpha = max(alpha, v)
            return val, action

        def min_value(board, alpha, beta, depth):
            if cutoff(board, depth):
                return evaluate(board, player), None
            val, action = infinity, None
            for a in successors(board, player):
                clone = board.clone()
                clone.play_action(a, player)
                next_state = clone
                v, _ = max_value(next_state, alpha, beta, depth + 1)
                if v < val:
                    val, action = v, a
                if v <= alpha:
                    return v, a
                beta = min(beta, v)
            return val, action

        _, action = max_value(board, -infinity, infinity, 0)
        print("wtf")
        print(_)
        print(action)

        return action

def cutoff(board, depth):
    return board.is_finished() or depth >= 2

def evaluate(board, player):

    return board.get_score(player)

def successors(board, player):
    return pogne_murs(board, player)

def walls_around_ennemy(action, player):
    #is wall next to player
    return (-1 <= (action[0] - player[0]) <=1) and (-1 <= (action[1]-player[1]) <= 1)

def pogne_murs(board: Board, player):
    all_pawn_moves = board.get_legal_pawn_moves(player)
    all_wall_moves = board.get_legal_wall_moves(player)
    good_action=[]   
    good_action.extend(all_pawn_moves)
    ennemy_pos = board.pawns[1-player]
    # print(good_action)
    for a in all_wall_moves:
        a_pos = (a[1],a[2])
        if walls_around_ennemy(a_pos, ennemy_pos):
            good_action.append(a)
    return good_action

def manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

if __name__ == "__main__":
    agent_main(MyAgent())
