## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = []

# imports
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# /***********************************************************************
# //
# ************************************************************************/

class UnionSquare_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        if not AbstractFoundationStack.acceptsCards(self, from_stack, cards):
            return 0
        # check the rank
        if len(self.cards) > 12:
            return cards[0].rank == 25 - len(self.cards)
        else:
            return cards[0].rank == len(self.cards)


class UnionSquare_RowStack(OpenStack):
    def __init__(self, x, y, game, **cap):
        kwdefault(cap, mod=8192, dir=0, base_rank=ANY_RANK,
                  max_accept=1, max_move=1)
        apply(OpenStack.__init__, (self, x, y, game), cap)
        #self.CARD_YOFFSET = 1

    def acceptsCards(self, from_stack, cards):
        if not OpenStack.acceptsCards(self, from_stack, cards):
            return 0
        if not self.cards:
            return 1
        if cards[0].suit != self.cards[0].suit:
            return 0
        if len(self.cards) == 1:
            card_dir = cards[0].rank - self.cards[-1].rank
            return card_dir == 1 or card_dir == -1
        else:
            stack_dir = (self.cards[1].rank - self.cards[0].rank) % self.cap.mod
            return (self.cards[-1].rank + stack_dir) % self.cap.mod == cards[0].rank

    def getBottomImage(self):
        return self.game.app.images.getReserveBottom()


# /***********************************************************************
# //
# ************************************************************************/

class UnionSquare(Game):
    Hint_Class = CautiousDefaultHint
    RowStack_Class = UnionSquare_RowStack

    #
    # game layout
    #

    def createGame(self, rows=16):
        # create layout
        l, s = Layout(self, YM=18), self.s

        # set window
        self.setSize(l.XM + (5+rows/4)*l.XS, l.YM + 4*l.YS)

        # create stacks
        x, y, = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, "s")
        x = x + l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, "s")
        for i in range(4):
            x = 3*l.XS
            for j in range(rows/4):
                stack = self.RowStack_Class(x, y, self)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 1
                s.rows.append(stack)
                x = x + l.XS
            y = y + l.YS
        x, y = self.width-l.XS, l.YM
        for i in range(4):
            stack = UnionSquare_Foundation(x, y, self, i, max_move=0,
                                           dir=0, max_cards=26)
            l.createText(stack, "sw")
            s.foundations.append(stack)
            y = y + l.YS

        # define stack-groups
        l.defaultStackGroups()


    #
    # game overrides
    #

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))

    def getHighlightPilesStacks(self):
        return ()


# /***********************************************************************
# // Solid Square
# ************************************************************************/

class SolidSquare(UnionSquare):
    RowStack_Class = StackWrapper(UD_SS_RowStack, base_rank=NO_RANK,
                                  max_accept=1,  max_move=1, mod=13)
    def createGame(self):
        UnionSquare.createGame(self, rows=20)

    def _shuffleHook(self, cards):
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE and c.deck == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        UnionSquare.startGame(self)

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)


# register the game
registerGame(GameInfo(35, UnionSquare, "Union Square",
                      GI.GT_2DECK_TYPE, 2, 0,
                      altnames=('British Square',),
                      ))
registerGame(GameInfo(439, SolidSquare, "Solid Square",
                      GI.GT_2DECK_TYPE, 2, 0))