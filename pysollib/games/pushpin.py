##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
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
##---------------------------------------------------------------------------##

__all__ = []

# imports
import sys, types

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

# /***********************************************************************
# //
# ************************************************************************/

class PushPin_Hint(AbstractHint):

    def computeHints(self):
        game = self.game
        rows = game.s.rows
        for i in range(len(rows)-3):
            r = rows[i+1]
            if not rows[i+2].cards:
                break
            if r._checkPair(i, i+2):
                self.addHint(5000, 1, r, game.s.foundations[0])
            if not rows[i+3].cards:
                break
            if r._checkPair(i, i+3):
                self.addHint(5000, 1, r, rows[i+2])


class PushPin_Foundation(AbstractFoundationStack):
    def acceptsCards(self, from_stack, cards):
        return True

class PushPin_Talon(DealRowTalonStack):
    def dealCards(self, sound=0):
        for r in self.game.s.rows:
            if not r.cards:
                return self.dealRowAvail(rows=[r], sound=sound)
        return self.dealRowAvail(rows=[self.game.s.rows[0]], sound=sound)
    def getBottomImage(self):
        return None

class PushPin_RowStack(ReserveStack):

    def _checkPair(self, ps, ns):
        if ps < 0 or ns > 51:
            return False
        rows = self.game.allstacks
        pc, nc = rows[ps].cards, rows[ns].cards
        if pc and nc:
            if pc[0].suit == nc[0].suit or pc[0].rank == nc[0].rank:
                return True
        return False

    def clickHandler(self, event):
        ps, ns = self.id - 1, self.id + 1
        if self._checkPair(ps, ns):
            if not self.game.demo:
                self.game.playSample("autodrop", priority=20)
            self.playMoveMove(1, self.game.s.foundations[0], sound=0)
            return True
        return False

    def acceptsCards(self, from_stack, cards):
        if not self.cards:
            return from_stack.id > self.id
            return True
        if abs(self.id - from_stack.id) != 1:
            return False
        ps = min(self.id, from_stack.id)-1
        ns = ps + 3
        return self._checkPair(ps, ns)

    def fillStack(self):
        self.game.fillEmptyStacks()

    def moveMove(self, ncards, to_stack, frames=-1, shadow=-1):
        if not to_stack is self.game.s.foundations[0]:
            self._dropPairMove(ncards, to_stack, frames=-1, shadow=shadow)
        else:
            ReserveStack.moveMove(self, ncards, to_stack, frames=frames, shadow=shadow)

    def _dropPairMove(self, n, other_stack, frames=-1, shadow=-1):
        game = self.game
        old_state = game.enterState(game.S_FILL)
        f = game.s.foundations[0]
        game.updateStackMove(game.s.talon, 2|16)            # for undo
        if not game.demo:
            game.playSample("droppair", priority=200)
        game.moveMove(n, self, f, frames=frames, shadow=shadow)
        game.moveMove(n, other_stack, f, frames=frames, shadow=shadow)
        self.fillStack()
        game.updateStackMove(game.s.talon, 1|16)            # for redo
        game.leaveState(old_state)

    def getBottomImage(self):
        return None


class PushPin(Game):

    Hint_Class = PushPin_Hint

    #
    # game layout
    #

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        xx, yy = 9, 6
        w, h = l.XM+xx*l.XS, l.YM+yy*l.YS
        self.setSize(w, h)

        # create stacks
        for i in range(yy):
            for j in range(xx):
                n = j+xx*i
                if n < 1:
                    continue
                if n > 52:
                    break
                k = j
                if i%2:
                    k = xx-j-1
                x, y = l.XM + k*l.XS, l.YM + i*l.YS
                s.rows.append(PushPin_RowStack(x, y, self))
        s.talon = PushPin_Talon(l.XM, l.YM, self)
        s.foundations.append(PushPin_Foundation(l.XM, h-l.YS, self,
                             suit=ANY_SUIT, dir=0, base_rank=ANY_RANK,
                             max_accept=0, max_move=0, max_cards=52))

        # define stack-groups
        l.defaultStackGroups()
        return l

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.rows[:3])

    def isGameWon(self):
        return len(self.s.foundations[0].cards) == 50

    def fillEmptyStacks(self):
        if not self.demo:
            self.startDealSample()
        rows = self.s.rows
        i = 0
        for r in rows:
            if not r.cards:
                break
            i += 1
        j = i
        for r in rows[i:]:
            if r.cards:
                break
            j += 1
        for r in rows[j:]:
            if not r.cards:
                break
            self.moveMove(1, r, rows[i], frames=2, shadow=0)
            i += 1
        if not self.demo:
            self.stopSamples()
        return 0

    def getAutoStacks(self, event=None):
        return ((), (), ())


class RoyalMarriage(PushPin):
    def _shuffleHook(self, cards):
        qi, ki = -1, -1
        for i in range(len(cards)):
            c = cards[i]
            if c.suit == 2 and c.rank == 11:
                qi = i
            if c.suit == 2 and c.rank == 12:
                ki = i
            if qi >= 0 and ki >= 0:
                break
        q, k = cards[qi], cards[ki]
        del cards[max(qi, ki)]
        del cards[min(qi, ki)]
        cards.insert(0, k)
        cards.append(q)
        return cards


class Queens(PushPin):
    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()


registerGame(GameInfo(287, PushPin, "Push Pin",
                      GI.GT_1DECK_TYPE, 1, 0))
registerGame(GameInfo(288, RoyalMarriage, "Royal Marriage",
                      GI.GT_1DECK_TYPE, 1, 0))
## registerGame(GameInfo(303, Queens, "Queens",
##                       GI.GT_1DECK_TYPE | GI.GT_OPEN, 1, 0))