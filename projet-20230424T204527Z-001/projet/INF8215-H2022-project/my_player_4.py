#!/usr/bin/env python3
"""
Quoridor agent.
Copyright (C) 2013, <<<<<<<<<<< BAUFAYS BENOIT & COLMONTS JULIEN >>>>>>>>>>>
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

https://github.com/BenBauf/LINGI2261-IA/blob/master/assigment3/quoridor/super_player.py
"""

import random
import time
from quoridor import *
from heapq import *
import minimax


class MyAgent(Agent, minimax.Game):

    """My Quoridor agent."""
    defaultDepthValue=3
    maxTime = 20*60
    depth =3
    count=0
    startTime = time.time()
    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s; s is the new state, i.e. a pair (b, p) where
        b is the new board after the action a has been played and
        p is the player to play the next move.
        """
        board, player = state
        return self.IA(board,player)



    def IA(self, board,player):
        score=board.get_score(self.player)
        otherPlayer=(player-1)%2
        #si le joueur est en position de perdre, il tente de mettre des murs
        if score<0 and board.nb_walls[player]>0:
            otherPlayerPosition=board.pawns[otherPlayer]
            for action in ['WH','WV']:
                for a in [(0,0),(-1,-1),(0,-1),(-1,0),(0,1),(1,0),(1,1)]:
                    wallPosition=(a[0]+otherPlayerPosition[0],a[1]+otherPlayerPosition[1])
                    if board.is_wall_possible_here(wallPosition, action=='WH'):
                        newBoard=board.clone()
                        newBoard.add_wall(wallPosition,action=='WH',player)
                        actionTuple=(action,wallPosition[0],wallPosition[1])

                        yield (actionTuple, (newBoard,otherPlayer))
        
        pawn_moves=board.get_legal_pawn_moves(player)
        for pawn in pawn_moves:
            newPosition=(pawn[1],pawn[2])
            newBoard=board.clone()
            newBoard.pawns[player]=newPosition
            yield (pawn,(newBoard, otherPlayer))

    #the depth evolue en fonction du temps car, au début, peu de coups sont possibles
    #et l'intelligence doit analyser plus de coups vers la fin
    def getCurrentDepth(self,board,player):
        current = time.time() - self.startTime
        if(current < self.maxTime/2):
            self.count+=1
        else:
            self.count-=1
        if self.count==10 and self.depth <8:
            self.count=0
            self.depth+=1
        if self.count==-10 and self.depth > 3:
            self.count=0
            self.depth-=1
        if board.nb_walls[player]==0:
            self.depth=1

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        board, player = state
        return board.is_finished() or depth >=self.depth

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        board, player = state
     
        costPlayer = self.evaluateAux(board, self.player)
        costOpponent = self.evaluateAux(board, (self.player-1)%2)

        if(costPlayer==0):
            return 100
        else:
            return costOpponent-costPlayer+random.randint(0, 1) #+(board.nb_walls[player]/2)+(board.nb_walls[(player-1)%2]/2)


    #dijkstra minimal pour un player
    def evaluateAux(self, board, player):
        default=10000000
        dij=(self.dijkstra(board.pawns[player],(board.goals[player],0),board,board.pawns[(player+1)%2]))
        if dij[0]==-1:
            dij=(default,)
        i=1
        #on regarde le path le plus court pour gagner (chemin vers toutes les cases de la lignes d'arrivée et on prend le plus court
        while i<board.size+1:
                dijTMP=(self.dijkstra(board.pawns[player],(board.goals[player],i),board,board.pawns[(player+1)%2])) 
                if dijTMP[0]>-1 and dijTMP[0]<dij[0]:
                    dij=dijTMP
                i=i+1

        #maybe no path
        if dij[0]==default:
            return default
        cost=dij[0]
        path=dij[1]
        index=len(path)-1
        finalPos=path[index]
        #on supprime les pas sur la ligne d'arrivée
        while(index>=0 and path[index][0]==finalPos[0]):
           if(path[index][1]!=finalPos[1]):
             cost=cost-1
           index=index-1
        return cost


    def play(self, percepts, player, step, time_left):
        """This function is used to play a move according
        to the percepts, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        self.player = player
        state = (dict_to_board(percepts), player)
        self.getCurrentDepth(state[0],state[1])
        value=minimax.search(state, self)
        return value

    #inspiré par un code trouvé sur internet mais optimisé pour notre cas
    def dijkstra (self,actualPosition, t, board,opponent):
        M = set()
        s=(actualPosition[0],actualPosition[1])
        d = {s: 0}
        p = {}
        suivants = [(0, s)] # tas de couples (d[x],x)
        while suivants != []:
            dx, x = heappop(suivants)
            if x in M:
                continue

            M.add(x)

            for w, y in self.voisins(x,board, opponent):
                if y in M:
                    continue
                dy = dx + w
                if y not in d or d[y] > dy:
                    d[y] = dy
                    heappush(suivants, (dy, y))
                    p[y] = x
        path = [t]
        x = t
        if x not in p.keys():
            return (-1,)
        while x != s:
            x = p[x]
            path.insert(0, x)
        return d[t], path

        #Source: http://www.google.be/url?sa=t&rct=j&q=&esrc=s&source=web&cd=9&ved=0CIEBEBYwCA&url=http%3A%2F%2Fisn.irem.univ-mrs.fr%2F2011-2012%2Fmedia%2Fresources%2Fdijkstra.py&ei=v2ZmUr0_p6XTBb_dgJAH&usg=AFQjCNEhlZhMqGk0vRgu3dvWcVEoEQ-Dog&sig2=rZD0OZl9QP4zshOOZ4IqfQ&bvm=bv.55123115,d.d2k&cad=rja
    def voisins(self,position,board,opponent):
        for a in [(0,-1),(0,1),(1,0),(-1,0)]:
            newPosition = (position[0]+a[0],position[1]+a[1])
            if newPosition[0]==opponent[0] and newPosition[1]==opponent[1]:
                newPosition=(newPosition[0]+a[0],newPosition[1]+a[1])
            if board.is_simplified_pawn_move_ok(position,newPosition):
                yield (1,newPosition)
                


if __name__ == "__main__":
    agent_main(MyAgent())