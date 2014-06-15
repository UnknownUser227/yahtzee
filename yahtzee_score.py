#!/Users/syt/science/bin/python

from dice_set import DiceSet

''' Module providing functions for scoring a dice_set.DiceSet as the various
legal Yahtzee combinations, e.g. threes or four-of-a-kind
'''

def is_dice_set(scoreFun):
  def yahtzee_score(dice, *args):
    assert isinstance(dice, DiceSet), "Can only score a DiceSet"
    assert dice.num_dice() == 5, "A valid Yahtzee DiceSet must have five dice"
    assert dice.num_rolls() <= 3, "Dice may only be rolled three times"
    return scoreFun(dice, *args)
  return yahtzee_score


@is_dice_set
def is_yahtzee(dice):

  dice_count = dice.as_count()
  for num in dice_count.keys():
    if 5 == dice_count[num]:
      return True
  return False

@is_dice_set
def num_count(dice, num):

  dice_count = dice.as_count()
  return num*dice_count[num] if num in dice_count else 0

@is_dice_set
def three_of_a_kind(dice):

  dice_count = dice.as_count()
  for num in dice_count.keys():
    if 3 <= dice_count[num]:
      return sum(dice.dice())

  return 0

@is_dice_set
def four_of_a_kind(dice):

  dice_count = dice.as_count()
  for num in dice_count.keys():
    if 4 <= dice_count[num]:
      return sum(dice.dice())
  
  return 0

@is_dice_set
def full_house(dice):

  if is_yahtzee(dice):
    return 25

  dice_count = dice.as_count()
  for num in dice_count.keys():
    if 2 != dice_count[num] and 3 != dice_count[num]:
      return 0

  return 25

@is_dice_set
def small_straight(dice):

  dice_set = dice.as_set()
  if (set([1, 2, 3, 4]) <= dice_set or
      set([2, 3, 4, 5]) <= dice_set or
      set([3, 4, 5, 6]) <= dice_set or
      is_yahtzee(dice)):

    return 30

  return 0

@is_dice_set
def large_straight(dice):

  dice_set = dice.as_set()
  if (set([1, 2, 3, 4, 5]) <= dice_set or
      set([2, 3, 4, 5, 6]) <= dice_set or
      is_yahtzee(dice)):

    return 40

  return 0

@is_dice_set
def yahtzee(dice):

  if is_yahtzee(dice):
      return 50
  return 0

@is_dice_set
def chance(dice):

  return sum(dice.dice())
