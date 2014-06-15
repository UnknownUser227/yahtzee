#!/Users/syt/science/bin/python

import collections
import random

class DiceSet:
  ''' Class representing an ordered collection of dice. When unrolled the dice
  values are set to None.
  '''

  def __init__(self, numDice, dice = None):

    self._num_dice = numDice
    self._dice = [None for i in xrange(self._num_dice)] if dice is None else dice
    self._num_rolls = 0

  def num_dice(self):

    return self._num_dice

  def num_rolls(self):

    return self._num_rolls

  def dice(self):

    return self._dice

  def reset(self):

    self._dice = [None for i in xrange(self._num_dice)]
    self._num_rolls = 0

  def roll(self, indices=None):

    if indices is None:
      indices = range(self._num_dice)

    for i in indices:
      self._dice[i] = random.randint(1, 6)

    self._dice = sorted(self._dice)

    self._num_rolls += 1

  def as_set(self):

    return set(self._dice)

  def as_count(self):

    return collections.Counter(self._dice)

  def __str__(self):

    return str(self._dice).strip('[').strip(']')
