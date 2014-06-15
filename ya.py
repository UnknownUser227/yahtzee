#!/Users/syt/science/bin/python

from dice_set import DiceSet
import random
import ys

''' Module containing the actions that a player in Yahtzee may take
'''

class Action:

  def __init__(self):

    pass

class Roll(Action):

  def __init__(self, indices):

    Action.__init__(self)
    
    assert isinstance(indices, list), "Dice to be re-rolled must be a list"
    indices = sorted(set(indices))
    assert len(indices) <= 5, "There are only five dice in Yahtzee"
    for index in indices:
      assert 0 <= index and index < 5, "{} is an invalid die index".format(index)

    self._indices = indices

  def indices(self):

    return self._indices

class RecordScore(Action):

  def __init__(self, scoreName):

    Action.__init__(self)

    assert scoreName in ys.scoring_rules.keys(), '{} is not a valid score type'.format(scoreName)
    self._scoreName = scoreName

  def score(self):

    return self._scoreName
