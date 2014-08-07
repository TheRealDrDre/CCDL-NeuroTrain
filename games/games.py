#!/usr/bin/env python

import wx
from core.manager import ManagerWrapper

class Game(object, ManagerWrapper):
    """A Game is an object that contains and uses analyzers to
    update a simulated world that is visualized on a panel
    """
    def __init__(self, manager=manager, analyzers=[]):
        """Initializes a game"""
        ManagerWrapper.__init__(self, manager)
        self._analyzers = analyzers


class ThetaAlphaVisualizer(wx.Panel):
    pass

