## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
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


# imports
import os, types

# PySol imports
from version import VERSION, VERSION_TUPLE
from mfxutil import Pickler, Unpickler, UnpicklingError
from mfxutil import Struct, EnvError

# Toolkit imports
from pysoltk import tkversion, loadImage, copyImage, createImage

try:
    import Image
except ImportError:
    Image = None

# /***********************************************************************
# // Images
# ************************************************************************/


class ImagesCardback:
    def __init__(self, index, name, image, menu_image=None):
        if menu_image is None: menu_image = image
        self.index = index
        self.name = name
        self.image = image
        self.menu_image = menu_image


class Images:
    def __init__(self, dataloader, cs, r=1):
        self.d = dataloader
        self.cs = cs
        self.reduced = r
        if cs is None:
            return
        # copy from cardset
        self.CARDW, self.CARDH, self.CARDD = cs.CARDW/r, cs.CARDH/r, cs.CARDD/r
        self.CARD_XOFFSET = cs.CARD_XOFFSET
        self.CARD_YOFFSET = cs.CARD_YOFFSET
        if r > 1:
            self.CARD_XOFFSET = max(10, cs.CARD_XOFFSET)/r
            self.CARD_YOFFSET = max(10, cs.CARD_YOFFSET)/r
        self.SHADOW_XOFFSET, self.SHADOW_YOFFSET = cs.SHADOW_XOFFSET/r, cs.SHADOW_YOFFSET/r
        self.CARD_DX, self.CARD_DY = cs.CARD_DX/r, cs.CARD_DY/r
        # other
        self._shade_index = 0
        self._card = []
        self._back = []
        self._bottom = []
        self._bottom_negative = []
        self._bottom_positive = []
        self._letter = []
        self._letter_negative = []
        self._letter_positive = []
        self._shadow = []
        self._shade = []

    def destruct(self):
        pass

    def __loadCard(self, filename, check_w=1, check_h=1):
        ##print '__loadCard:', filename
        f = os.path.join(self.cs.dir, filename)
        img = loadImage(file=f)
        w, h = img.width(), img.height()
        if self.CARDW < 0:
            self.CARDW, self.CARDH = w, h
        else:
            if ((check_w and w != self.CARDW) or
                (check_h and h != self.CARDH)):
                raise Exception, "Invalid size %dx%d of image %s" % (w, h, f)
        return img

    def __addBack(self, im1, name):
        r = max(self.CARDW / 40.0, self.CARDH / 60.0)
        r = max(2, int(round(r)))
        im2 = im1.subsample(r)
        self._back.append(ImagesCardback(len(self._back), name, im1, im2))

    def _createMissingImages(self):
        # back
        if not self._back:
            im = createImage(self.CARDW, self.CARDH, fill="#a0a0a0", outline="#000000")
            name = ""
            self.__addBack(im, name)
            self.cs.backnames = tuple(self.cs.backnames) + (name,)
        # bottoms / letters
        bottom = None
        while len(self._bottom_positive) < 7:
            if bottom is None:
                bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#000000")
            self._bottom_positive.append(bottom)
        while len(self._bottom_negative) < 7:
            if bottom is None:
                bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#ffffff")
            self._bottom_negative.append(bottom)
        while len(self._letter_positive) < 4:
            if bottom is None:
                bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#000000")
            self._letter_positive.append(bottom)
        while len(self._letter_negative) < 4:
            if bottom is None:
                bottom = createImage(self.CARDW, self.CARDH, fill=None, outline="#ffffff")
            self._letter_negative.append(bottom)

    def load(self, app, progress=None, fast=0):
        ##fast = 1
        ##fast = 2
        if fast > 1:
            # only for testing
            self.cs.backnames = ()
            self.cs.nbottoms = 0
            self.cs.nletters = 0
        ext = self.cs.ext[1:]
        pstep = 0
        if progress:
            pstep = self.cs.ncards + len(self.cs.backnames) + self.cs.nbottoms + self.cs.nletters
            if not fast:
                pstep = pstep + self.cs.nshadows + 1    # shadows & shade
            pstep = max(0, (80.0 - progress.percent) / pstep)
        # load face cards
        for n in self.cs.getFaceCardNames():
            self._card.append(self.__loadCard(n + self.cs.ext))
            self._card[-1].filename = n
            if progress: progress.update(step=pstep)
        assert len(self._card) == self.cs.ncards
        # load backgrounds
        for name in self.cs.backnames:
            if name:
                try:
                    im = self.__loadCard(name)
                    self.__addBack(im, name)
                except:
                    pass
        if progress: progress.update(step=1)
        # load bottoms
        for i in range(self.cs.nbottoms):
            try:
                name = "bottom%02d.%s" % (i + 1, ext)
                self._bottom_positive.append(self.__loadCard(name))
            except:
                pass
            if progress: progress.update(step=pstep)
            # load negative bottoms
            try:
                name = "bottom%02d-n.%s" % (i + 1, ext)
                self._bottom_negative.append(self.__loadCard(name))
            except:
                pass
            if progress: progress.update(step=pstep)
        # load letters
        for rank in range(self.cs.nletters):
            try:
                name = "l%02d.%s" % (rank + 1, ext)
                self._letter_positive.append(self.__loadCard(name))
            except:
                pass
            if progress: progress.update(step=pstep)
            # load negative letters
            try:
                name = "l%02d-n.%s" % (rank + 1, ext)
                self._letter_negative.append(self.__loadCard(name))
            except:
                pass
            if progress: progress.update(step=pstep)
        # shadow
        for i in range(self.cs.nshadows):
            if fast:
                self._shadow.append(None)
            else:
                name = "shadow%02d.%s" % (i, ext)
                try:
                    im = self.__loadCard(name, check_w=0, check_h=0)
                except:
                    im = None
                self._shadow.append(im)
            if progress: progress.update(step=pstep)
        # shade
        if fast:
            self._shade.append(None)
        else:
            self._shade.append(self.__loadCard("shade." + ext))
        if progress: progress.update(step=pstep)
        # create missing
        self._createMissingImages()
        #
        self._bottom = self._bottom_positive
        self._letter = self._letter_positive
        return 1

    def getFace(self, deck, suit, rank):
        index = suit * len(self.cs.ranks) + rank
        ##print "getFace:", suit, rank, index
        return self._card[index % self.cs.ncards]

    def getBack(self, deck, suit, rank):
        index = self.cs.backindex % len(self._back)
        return self._back[index].image

    def getTalonBottom(self):
        return self._bottom[0]

    def getReserveBottom(self):
        return self._bottom[0]

    def getSuitBottom(self, suit=-1):
        assert type(suit) is types.IntType
        if suit == -1: return self._bottom[1]   # any suit
        i = 3 + suit
        if i >= len(self._bottom):
            # Trump (for Tarock type games)
            return self._bottom[1]
        return self._bottom[i]

    def getBraidBottom(self):
        return self._bottom[2]

    def getLetter(self, rank):
        assert 0 <= rank <= 3
        if rank >= len(self._letter):
            return self._bottom[0]
        return self._letter[rank]

    def getShadow(self, ncards):
        assert ncards >= 0
        if ncards >= len(self._shadow):
            ##ncards = len(self._shadow) - 1
            return None
        return self._shadow[ncards]

    def getShade(self):
        return self._shade[self._shade_index]

    def getCardbacks(self):
        return self._back

    def setNegative(self, flag=0):
        if flag:
            self._bottom = self._bottom_negative
            self._letter = self._letter_negative
        else:
            self._bottom = self._bottom_positive
            self._letter = self._letter_positive


# /***********************************************************************
# //
# ************************************************************************/

class SubsampledImages(Images):
    def __init__(self, images, r=2):
        Images.__init__(self, None, images.cs, r=r)
        self._card = self._subsample(images._card, r)
        self._bottom_positive = self._subsample(images._bottom_positive, r)
        self._letter_positive = self._subsample(images._letter_positive, r)
        self._bottom_negative = self._subsample(images._bottom_negative, r)
        self._letter_negative = self._subsample(images._letter_negative, r)
        self._bottom = self._bottom_positive
        self._letter = self._letter_positive
        #
        for _back in images._back:
            if _back is None:
                self._back.append(None)
            else:
                im = _back.image.subsample(r)
                self._back.append(ImagesCardback(len(self._back), _back.name, im, im))
        #
        CW, CH = self.CARDW, self.CARDH
        for im in images._shade:
            if im is None or tkversion < (8, 3, 0, 0):
                self._shade.append(None)
            else:
                self._shade.append(copyImage(im, 0, 0, CW, CH))

    def getShadow(self, ncards):
        return None

    def _subsample(self, l, r):
        s = []
        for im in l:
            if im is None or r == 1:
                s.append(im)
            else:
                s.append(im.subsample(r))
        return s
