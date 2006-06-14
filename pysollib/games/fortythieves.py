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
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint
from pysollib.pysoltk import MfxCanvasText

# /***********************************************************************
# //
# ************************************************************************/

class FortyThieves_Hint(CautiousDefaultHint):
    # FIXME: demo is not too clever in this game
    pass


# /***********************************************************************
# // Forty Thieves
# //   rows build down by suit
# ************************************************************************/

class FortyThieves(Game):
    Foundation_Class = SS_FoundationStack
    RowStack_Class = SS_RowStack
    Hint_Class = FortyThieves_Hint

    FOUNDATION_MAX_MOVE = 1
    ROW_MAX_MOVE = 1
    DEAL = (0, 4)
    FILL_EMPTY_ROWS = 0

    #
    # game layout
    #

    def createGame(self, max_rounds=1, num_deal=1, rows=10, playcards=12, XCARDS=64, XOFFSET=None):
        # create layout
        XM = (10, 4)[rows > 10]
        if XOFFSET is None:
            l, s = Layout(self, XM=XM, YBOTTOM=16), self.s
        else:
            l, s = Layout(self, XM=XM, XOFFSET=XOFFSET, YBOTTOM=16), self.s

        # set window
        # (compute best XOFFSET - up to 64/72 cards can be in the Waste)
        decks = self.gameinfo.decks
        maxrows = max(rows, 4*decks+2)
        w1, w2 = maxrows*l.XS+l.XM, 2*l.XS
        if w2 + XCARDS * l.XOFFSET > w1:
            l.XOFFSET = int((w1 - w2) / XCARDS)
        # (piles up to 12 cards are playable without overlap in default window size)
        h = max(2*l.YS, l.YS+(playcards-1)*l.YOFFSET)
        self.setSize(w1, l.YM + l.YS + h + l.YS + l.YBOTTOM)

        # create stacks
        x = l.XM + (maxrows - 4*decks) * l.XS / 2
        y = l.YM
        for i in range(4*decks):
            s.foundations.append(self.Foundation_Class(x, y, self, suit=i/decks, max_move=self.FOUNDATION_MAX_MOVE))
            x = x + l.XS
        x = l.XM + (maxrows - rows) * l.XS / 2
        y = l.YM + l.YS
        for i in range(rows):
            s.rows.append(self.RowStack_Class(x, y, self, max_move=self.ROW_MAX_MOVE))
            x = x + l.XS
        x = self.width - l.XS
        y = self.height - l.YS - l.YBOTTOM
        s.talon = WasteTalonStack(x, y, self, max_rounds=max_rounds, num_deal=num_deal)
        l.createText(s.talon, "s")
        if max_rounds > 1:
            s.talon.texts.rounds = MfxCanvasText(self.canvas,
                                                 x + l.CW / 2, y - l.YM,
                                                 anchor="s",
                                                 font=self.app.getFont("canvas_default"))
        x = x - l.XS
        s.waste = WasteStack(x, y, self)
        s.waste.CARD_XOFFSET = -l.XOFFSET
        l.createText(s.waste, "s")

        # define stack-groups
        l.defaultStackGroups()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(self.DEAL[0]):
            self.s.talon.dealRow(flip=0, frames=0)
        for i in range(self.DEAL[1] - 1):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if self.FILL_EMPTY_ROWS and stack in self.s.rows and not stack.cards:
            old_state = self.enterState(self.S_FILL)
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)
            elif self.s.talon.canDealCards():
                self.s.talon.dealCards()
                self.s.waste.moveMove(1, stack)
            self.leaveState(old_state)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit == card2.suit and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# /***********************************************************************
# // Busy Aces
# // Limited
# // Courtyard
# // Waning Moon
# // Lucas
# // Napoleon's Square
# // Carre Napoleon
# // Josephine
# //   rows build down by suit
# ************************************************************************/

class BusyAces(FortyThieves):
    DEAL = (0, 1)

    def createGame(self):
        FortyThieves.createGame(self, rows=12)


class Limited(BusyAces):
    DEAL = (0, 3)


class Courtyard(BusyAces):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    FILL_EMPTY_ROWS = 1


class WaningMoon(FortyThieves):
    def createGame(self):
        FortyThieves.createGame(self, rows=13)


class Lucas(WaningMoon):
    ROW_MAX_MOVE = UNLIMITED_MOVES


class NapoleonsSquare(FortyThieves):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    def createGame(self):
        FortyThieves.createGame(self, rows=12)


class CarreNapoleon(FortyThieves):
    RowStack_Class = StackWrapper(SS_RowStack, base_rank=KING)

    def createGame(self):
        FortyThieves.createGame(self, rows=12)

    def _fillOne(self):
        for r in self.s.rows:
            if r.cards:
                c = r.cards[-1]
                for f in self.s.foundations:
                    if f.acceptsCards(r, [c]):
                        self.moveMove(1, r, f, frames=4, shadow=0)
                        return 1
        return 0

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        for i in range(4):
            self.s.talon.dealRow()
            while True:
                if not self._fillOne():
                    break
        self.s.talon.dealCards()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == 0, c.suit))


class Josephine(FortyThieves):
    ROW_MAX_MOVE = UNLIMITED_MOVES


# /***********************************************************************
# // Deuces
# ************************************************************************/

class Deuces(FortyThieves):
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=1)
    RowStack_Class = StackWrapper(SS_RowStack, mod=13)

    DEAL = (0, 1)

    def _shuffleHook(self, cards):
        # move Twos to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 1, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        FortyThieves.startGame(self)


# /***********************************************************************
# // Corona
# // Quadrangle
# ************************************************************************/

class Corona(FortyThieves):
    FOUNDATION_MAX_MOVE = 0
    DEAL = (0, 3)
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        FortyThieves.createGame(self, rows=12)


class Quadrangle(Corona):
    Foundation_Class = StackWrapper(SS_FoundationStack, mod=13, base_rank=NO_RANK)
    RowStack_Class = StackWrapper(SS_RowStack, mod=13)

    def startGame(self):
        FortyThieves.startGame(self)
        self.s.talon.dealSingleBaseCard()


# /***********************************************************************
# // Forty and Eight
# ************************************************************************/

class FortyAndEight(FortyThieves):
    def createGame(self):
        FortyThieves.createGame(self, max_rounds=2, rows=8, XCARDS=72)


# /***********************************************************************
# // Little Forty
# ************************************************************************/

class LittleForty(FortyThieves):
    RowStack_Class = Spider_SS_RowStack

    ROW_MAX_MOVE = UNLIMITED_MOVES
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        FortyThieves.createGame(self, max_rounds=4, num_deal=3, XOFFSET=0)

    def getQuickPlayScore(self, ncards, from_stack, to_stack):
        if to_stack.cards:
            return int(from_stack.cards[-1].suit == to_stack.cards[-1].suit)+1
        return 0


# /***********************************************************************
# // Streets
# // Maria
# // Number Ten
# // Rank and File
# // Emperor
# // Triple Line
# //   rows build down by alternate color
# ************************************************************************/

class Streets(FortyThieves):
    RowStack_Class = AC_RowStack

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


class Maria(Streets):
    def createGame(self):
        Streets.createGame(self, rows=9)


class NumberTen(Streets):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (2, 2)


class RankAndFile(Streets):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (3, 1)


class Emperor(Streets):
    DEAL = (3, 1)


class TripleLine(Streets):
    GAME_VERSION = 2

    FOUNDATION_MAX_MOVE = 0
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (0, 3)
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        Streets.createGame(self, max_rounds=2, rows=12)


# /***********************************************************************
# // Red and Black
# // Zebra
# //   rows build down by alternate color, foundations up by alternate color
# ************************************************************************/

class RedAndBlack(Streets):
    Foundation_Class = AC_FoundationStack

    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (0, 1)

    def createGame(self):
        FortyThieves.createGame(self, rows=8)

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards, lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow(rows=self.s.foundations)
        Streets.startGame(self)


class Zebra(RedAndBlack):
    FOUNDATION_MAX_MOVE = 0
    ROW_MAX_MOVE = 1
    FILL_EMPTY_ROWS = 1

    def createGame(self):
        FortyThieves.createGame(self, max_rounds=2, rows=8, XOFFSET=0)


# /***********************************************************************
# // Indian
# // Midshipman
# // Mumbai
# //   rows build down by any suit but own
# ************************************************************************/

class Indian_RowStack(SequenceRowStack):
    def _isSequence(self, cards):
        return isAnySuitButOwnSequence(cards, self.cap.mod, self.cap.dir)
    def getHelp(self):
        return _('Row. Build down in any suit but the same.')


class Indian(FortyThieves):
    RowStack_Class = Indian_RowStack
    DEAL = (1, 2)

    def createGame(self):
        FortyThieves.createGame(self, XCARDS=74)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.suit != card2.suit and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


class Midshipman(Indian):
    DEAL = (2, 2)

    def createGame(self):
        FortyThieves.createGame(self, rows=9)


class Mumbai(Indian):
    def createGame(self):
        FortyThieves.createGame(self, XCARDS=84, rows=13)


# /***********************************************************************
# // Napoleon's Exile
# // Double Rail
# // Single Rail (1 deck)
# //   rows build down by rank
# ************************************************************************/

class NapoleonsExile(FortyThieves):
    RowStack_Class = RK_RowStack

    DEAL = (0, 4)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank


class DoubleRail(NapoleonsExile):
    ROW_MAX_MOVE = UNLIMITED_MOVES
    DEAL = (0, 1)

    def createGame(self):
        FortyThieves.createGame(self, rows=5)


class SingleRail(DoubleRail):
    def createGame(self):
        FortyThieves.createGame(self, rows=4, XCARDS=48)


# /***********************************************************************
# // Octave
# ************************************************************************/

class Octave_Talon(WasteTalonStack):

    def dealCards(self, sound=0):
        if self.round == self.max_rounds:
            # last round
            old_state = self.game.enterState(self.game.S_DEAL)
            num_cards = 0
            wastes = [self.waste]+list(self.game.s.reserves)
            if self.cards:
                if sound and not self.game.demo:
                    self.game.startDealSample()
                num_cards = min(len(self.cards), 8)
                for i in range(num_cards):
                    if not self.cards[-1].face_up:
                        self.game.flipMove(self)
                    self.game.moveMove(1, self, wastes[i], frames=4, shadow=0)
                if sound and not self.game.demo:
                    self.game.stopSamples()
            self.game.leaveState(old_state)
            return num_cards
        return WasteTalonStack.dealCards(self, sound)


class Octave(Game):

    #
    # game layout
    #

    def createGame(self):

        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+9*l.XS, l.YM+3*l.YS+12*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self,
                                 suit=int(i/2), max_cards=10))
            x += l.XS

        x, y = l.XM, l.YM+l.YS
        for i in range(8):
            s.rows.append(AC_RowStack(x, y, self,
                                      base_rank=ANY_RANK, max_move=1))
            x += l.XS

        x, y = l.XM, h-l.YS
        s.talon = Octave_Talon(x, y, self, max_rounds=2)
        l.createText(s.talon, "n")
        x += l.XS
        s.waste = WasteStack(x, y, self)
        x += l.XS
        for i in range(7):
            s.reserves.append(OpenStack(x, y, self, max_accept=0))
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == 0, c.suit))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        for i in range(2):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def isGameWon(self):
        for s in self.s.foundations:
            if len(s.cards) != 10:
                return False
        for s in self.s.reserves:
            if s.cards:
                return False
        return not self.s.waste.cards

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.color != card2.color and abs(card1.rank-card2.rank) == 1

    def _autoDeal(self, sound=1):
        ncards = len(self.s.waste.cards) + sum([len(i.cards) for i in self.s.reserves])
        if ncards == 0:
            return self.dealCards(sound=sound)
        return 0


# /***********************************************************************
# // Fortune's Favor
# ************************************************************************/

class FortunesFavor(Game):

    def createGame(self):

        l, s = Layout(self), self.s

        w, h = l.XM+7*l.XS, 2*l.YM+3*l.YS
        self.setSize(w, h)

        x, y = l.XM+3*l.XS, l.YM
        for i in range(4):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i))
            x += l.XS
        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')
        y += l.YS+2*l.YM
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')
        y = 2*l.YM+l.YS
        for i in range(2):
            x = l.XM+l.XS
            for j in range(6):
                stack = SS_RowStack(x, y, self, max_move=1)
                stack.CARD_XOFFSET, stack.CARD_YOFFSET = 0, 0
                s.rows.append(stack)
                x += l.XS
            y += l.YS

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                                          lambda c: (c.rank == ACE, c.suit))


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


    def fillStack(self, stack):
        if len(stack.cards) == 0:
            if stack is self.s.waste and self.s.talon.cards:
                self.s.talon.dealCards()
            elif stack in self.s.rows and self.s.waste.cards:
                self.s.waste.moveMove(1, stack)


    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1


# /***********************************************************************
# // Octagon
# ************************************************************************/

class Octagon(Game):
    Hint_Class = CautiousDefaultHint

    def createGame(self):

        l, s = Layout(self), self.s

        w1 = l.XS+12*l.XOFFSET
        w, h = l.XM+2*l.XS+2*w1, l.YM+3*l.YS
        self.setSize(w, h)

        for x, y in ((l.XM,                l.YM),
                     (l.XM+w1+2*l.XS+l.XM, l.YM),
                     (l.XM,                l.YM+2*l.YS),
                     (l.XM+w1+2*l.XS+l.XM, l.YM+2*l.YS),):
            stack = SS_RowStack(x, y, self, max_move=1)
            stack.CARD_XOFFSET, stack.CARD_YOFFSET = l.XOFFSET, 0
            s.rows.append(stack)
        i = 0
        for x, y in ((l.XM+w1,        l.YM),
                     (l.XM+w1+l.XS,   l.YM),
                     (l.XM+w1-2*l.XS-l.XM, l.YM+l.YS),
                     (l.XM+w1-l.XS-l.XM,   l.YM+l.YS),
                     (l.XM+w1+2*l.XS+l.XM, l.YM+l.YS),
                     (l.XM+w1+3*l.XS+l.XM, l.YM+l.YS),
                     (l.XM+w1,        l.YM+2*l.YS),
                     (l.XM+w1+l.XS,   l.YM+2*l.YS),):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i%4))
            i += 1
        x, y = l.XM+w1, l.YM+l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=4)
        x += l.XS
        s.waste = WasteStack(x, y, self)

        l.defaultStackGroups()


    def _shuffleHook(self, cards):
        # move Aces to top of the Talon (i.e. first cards to be dealt)
        return self._shuffleHookMoveToTop(cards,
                   lambda c: (c.rank == ACE, (c.deck, c.suit)))

    def startGame(self):
        self.s.talon.dealRow(rows=self.s.foundations, frames=0)
        self.startDealSample()
        for i in range(5):
            self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def fillStack(self, stack):
        if stack in self.s.rows and not stack.cards:
            if not self.s.waste.cards:
                self.s.talon.dealCards()
            if self.s.waste.cards:
                self.s.waste.moveMove(1, stack)

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1


# /***********************************************************************
# // Squadron
# ************************************************************************/

class Squadron(FortyThieves):

    def createGame(self):
        l, s = Layout(self), self.s

        self.setSize(l.XM+12*l.XS, l.YM+max(4.5*l.YS, 2*l.YS+12*l.YOFFSET))

        x, y = l.XM, l.YM
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 's')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 's')
        x += 2*l.XS
        for i in range(8):
            s.foundations.append(SS_FoundationStack(x, y, self, suit=i/2))
            x += l.XS
        x, y = l.XM, l.YM+l.YS*3/2
        for i in range(3):
            s.reserves.append(ReserveStack(x, y, self))
            y += l.YS
        x, y = l.XM+2*l.XS, l.YM+l.YS
        for i in range(10):
            s.rows.append(SS_RowStack(x, y, self, max_move=1))
            x += l.XS

        l.defaultStackGroups()


    def startGame(self):
        self.s.talon.dealRow(rows=self.s.reserves, frames=0)
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack



# register the game
registerGame(GameInfo(13, FortyThieves, "Forty Thieves",
                      GI.GT_FORTY_THIEVES, 2, 0,
                      altnames=("Napoleon at St.Helena",
                                "Big Forty", "Le Cadran")))
registerGame(GameInfo(80, BusyAces, "Busy Aces",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(228, Limited, "Limited",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(79, WaningMoon, "Waning Moon",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(125, Lucas, "Lucas",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(109, Deuces, "Deuces",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(196, Corona, "Corona",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(195, Quadrangle, "Quadrangle",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(110, Courtyard, "Courtyard",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(23, FortyAndEight, "Forty and Eight",
                      GI.GT_FORTY_THIEVES, 2, 1))
registerGame(GameInfo(115, LittleForty, "Little Forty",         # was: 72
                      GI.GT_FORTY_THIEVES, 2, 3))
registerGame(GameInfo(76, Streets, "Streets",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(73, Maria, "Maria",
                      GI.GT_FORTY_THIEVES, 2, 0,
                      altnames=("Maria Luisa",) ))
registerGame(GameInfo(70, NumberTen, "Number Ten",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(71, RankAndFile, "Rank and File",
                      GI.GT_FORTY_THIEVES, 2, 0,
                      altnames=("Dress Parade") ))
registerGame(GameInfo(197, TripleLine, "Triple Line",
                      GI.GT_FORTY_THIEVES | GI.GT_XORIGINAL, 2, 1))
registerGame(GameInfo(126, RedAndBlack, "Red and Black",        # was: 75
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(113, Zebra, "Zebra",
                      GI.GT_FORTY_THIEVES, 2, 1))
registerGame(GameInfo(69, Indian, "Indian",
                      GI.GT_FORTY_THIEVES, 2, 0,
                      altnames=("Indian Patience",) ))
registerGame(GameInfo(74, Midshipman, "Midshipman",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(198, NapoleonsExile, "Napoleon's Exile",
                      GI.GT_FORTY_THIEVES | GI.GT_XORIGINAL, 2, 0))
registerGame(GameInfo(131, DoubleRail, "Double Rail",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(199, SingleRail, "Single Rail",
                      GI.GT_FORTY_THIEVES, 1, 0))
registerGame(GameInfo(295, NapoleonsSquare, "Napoleon's Square",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(310, Emperor, "Emperor",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(323, Octave, "Octave",
                      GI.GT_FORTY_THIEVES, 2, 1))
registerGame(GameInfo(332, Mumbai, "Mumbai",
                      GI.GT_FORTY_THIEVES, 3, 0))
registerGame(GameInfo(411, CarreNapoleon, "Carre Napoleon",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(416, FortunesFavor, "Fortune's Favor",
                      GI.GT_FORTY_THIEVES, 1, 0))
registerGame(GameInfo(426, Octagon, "Octagon",
                      GI.GT_FORTY_THIEVES, 2, 3))
registerGame(GameInfo(440, Squadron, "Squadron",
                      GI.GT_FORTY_THIEVES, 2, 0))
registerGame(GameInfo(462, Josephine, "Josephine",
                      GI.GT_FORTY_THIEVES, 2, 0))