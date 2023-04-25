#!/usr/bin/env python3
"""
=======================================================================================================
INF8215: Projet - Agent intelligent pour le jeu Quoridor

Auteurs:
-> William Balea       1904905
-> Jean-Michel Lasnier 1905682
=======================================================================================================


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

from quoridor import *
import math

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
        print("step:", step)
        print("time left:", time_left if time_left else '+inf')
        
        # TODO: implement your agent and return an action for the current step.
        
        #board variable
        board = dict_to_board(percepts)
                
        #change depth according to step number and time left
        depth = 0
        if step > 10 and time_left > 60:
            depth =1
        
        try:
            shortestP = board.get_shortest_path(player)
        except:
            print('NoPath Exception')
            shortestP = board.get_legal_pawn_moves(player)
        
        towards_goal = ('P', shortestP[0][0], shortestP[0][1])
        #Move forward for 2 first move if possible (strategy)
        if (step < 5) and (board.is_action_valid(towards_goal, player)):
            return towards_goal

        #If 1 step from victory, go for it!
        if len(shortestP)==1:
            return towards_goal
            

        # call apha-beta search
        _, move = h_alphabeta_search(board, player, depth ,step, heuristic)
        print('move: ',move)
        return move


def h_alphabeta_search(board, player, max_depth, step, h=lambda s , p: 0):

    def max_value(board, alpha, beta, depth, act=None):
        if board.is_finished():
            return board.get_score(player), None
        
        if depth > max_depth:
            return h(board, player, step, act), None
        
        v, move = -math.inf, None
        for a in remove_useless_actions(board, player):
            transition = board.clone().play_action(a, player)
            v2, _ = min_value(transition, alpha, beta, depth+1, a)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(board: Board, alpha, beta, depth, act=None):
        if board.is_finished():
            return board.get_score(player), None
        if depth > max_depth:
            return h(board, player, step, act), None
        v, move = math.inf, None
        for a in remove_useless_actions(board, 1 - player):
            transition = board.clone().play_action(a, 1 - player)
            v2, _ = max_value(transition, alpha, beta, depth+1, a)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(board, -math.inf, math.inf, 0)

def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda board, depth: depth > d

def heuristic(board: Board, player, step, act):
    #[sh_path_player, sh_path_opponent, wall_player, wall_ennemy]
    percentage = [2, 1.8, 0.5, 0.5, 0.4]
    percentage_player_plusproche = [2.2, 1.5, 0.7, 0.5]
    percentage_ennemy_plusproche = [1.7, 1.5, 0.4, 0.3]
    
    score = board.get_score(player)
    if score >0:
        percentage = percentage_player_plusproche
    elif score< 0:
        percentage = percentage_ennemy_plusproche

    try:
        sh_path_player = -len(board.get_shortest_path(player))
        sh_path_opponent = len(board.get_shortest_path(1 - player))
    except:
        print('NoPathError')
        sh_path_player = manhattan(board.pawns[player], board.goals[player])
        sh_path_opponent = manhattan(board.pawns[1-player], board.goals[1-player])
        
    wall_player = board.nb_walls[player]
    wall_ennemy = -board.nb_walls[1 - player]
    
    return (sh_path_player * percentage[0] + sh_path_opponent * percentage[1]
             + wall_player * percentage[2] + wall_ennemy * percentage[3])

def remove_useless_actions(board: Board, player):
    actions = board.get_actions(player)
    ennemy_pos = board.pawns[1-player]
    my_pos = board.pawns[player]
    walls = board.horiz_walls + board.verti_walls
    
    good_action=[]   
    for a in actions:
        a_pos = (a[1],a[2])
        #keep moving actions
        if a[0]=='P':
            good_action.append(a)
        #keep walls around ennemy
        elif walls_around_ennemy(a_pos, ennemy_pos):
            good_action.append(a)
        #keep walls around my_player
        elif walls_around_player(a_pos, my_pos):
            good_action.append(a)
    
    return good_action
#========================UTILS========================#
def manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def walls_around_ennemy(action, player):
    #is wall next to player
    return (-2 <= (action[0] - player[0]) <=1) and (-2 <= (action[1]-player[1]) <= 1)
def walls_around_player(action, player):
    #is wall next to player
    return (-2 <= (action[0] - player[0]) <=1) and (-2 <= (action[1]-player[1]) <= 1)

if __name__ == "__main__":
    agent_main(MyAgent())
