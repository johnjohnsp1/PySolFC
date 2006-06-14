# -*- mode: python; coding: utf-8 -*-
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
from pysollib.hint import KlondikeType_Hint
from pysollib.pysoltk import MfxCanvasText


# /***********************************************************************
# // Double Klondike (Klondike with 2 decks and 9 rows)
# ************************************************************************/

class DoubleKlondike(Game):
    Layout_Method = Layout.harpLayout
    RowStack_Class = KingAC_RowStack
    Hint_Class = KlondikeType_Hint

    def createGame(self, max_rounds=-1, num_deal=1, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=9, waste=1, texts=1, playcards=19)
        apply(self.Layout_Method, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = WasteTalonStack(l.s.talon.x, l.s.talon.y, self,
                                  max_rounds=max_rounds, num_deal=num_deal)
        s.waste = WasteStack(l.s.waste.x, l.s.waste.y, self)
        for r in l.s.foundations:
            s.foundations.append(SS_FoundationStack(r.x, r.y, self, suit=r.suit))
        for r in l.s.rows:
            s.rows.append(self.RowStack_Class(r.x, r.y, self))
        # default
        l.defaultAll()
        # extra
        if max_rounds > 1:
            assert s.talon.texts.rounds is None
            tx, ty, ta, tf = l.getTextAttr(s.talon, "nn")
            if layout.get("texts"):
                ty = ty - 2*l.YM
            s.talon.texts.rounds = MfxCanvasText(self.canvas, tx, ty,
                                                 anchor=ta,
                                                 font=self.app.getFont("canvas_default"))
        return l

    def startGame(self):
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[i+1:], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return (card1.color != card2.color and
                (card1.rank + 1 == card2.rank or card2.rank + 1 == card1.rank))


# /***********************************************************************
# // Double Klondike by Threes
# ************************************************************************/

class DoubleKlondikeByThrees(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, num_deal=3)


# /***********************************************************************
# // Gargantua (Double Klondike with one redeal)
# ************************************************************************/

class Gargantua(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=2)


# /***********************************************************************
# // Harp (Double Klondike with 10 non-king rows and no redeal)
# ************************************************************************/

class BigHarp(DoubleKlondike):
    RowStack_Class = AC_RowStack

    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=1, rows=10)

    #
    # game overrides
    #

    # no real need to override, but this way the layout
    # looks a little bit different
    def startGame(self):
        for i in range(len(self.s.rows)):
            self.s.talon.dealRow(rows=self.s.rows[:i], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()          # deal first card to WasteStack


# /***********************************************************************
# // Steps (Harp with 7 rows)
# ************************************************************************/

class Steps(DoubleKlondike):
    RowStack_Class = AC_RowStack

    def createGame(self):
        DoubleKlondike.createGame(self, max_rounds=2, rows=7)


# /***********************************************************************
# // Triple Klondike
# ************************************************************************/

class TripleKlondike(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, rows=13)


# /***********************************************************************
# // Triple Klondike by Threes
# ************************************************************************/

class TripleKlondikeByThrees(DoubleKlondike):
    def createGame(self):
        DoubleKlondike.createGame(self, rows=13, num_deal=3)


# register the game
registerGame(GameInfo(21, DoubleKlondike, "Double Klondike",
                      GI.GT_KLONDIKE, 2, -1))
registerGame(GameInfo(28, DoubleKlondikeByThrees, "Double Klondike by Threes",
                      GI.GT_KLONDIKE, 2, -1))
registerGame(GameInfo(25, Gargantua, "Gargantua",
                      GI.GT_KLONDIKE, 2, 1))
registerGame(GameInfo(15, BigHarp, "Big Harp",
                      GI.GT_KLONDIKE, 2, 0,
                      altnames=("Die große Harfe",) ))
registerGame(GameInfo(51, Steps, "Steps",
                      GI.GT_KLONDIKE, 2, 1))
registerGame(GameInfo(273, TripleKlondike, "Triple Klondike",
                      GI.GT_KLONDIKE, 3, -1))
registerGame(GameInfo(274, TripleKlondikeByThrees, "Triple Klondike by Threes",
                      GI.GT_KLONDIKE, 3, -1))
