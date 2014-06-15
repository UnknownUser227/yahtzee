#!/Users/syt/science/bin/python

from dice_set import DiceSet

''' Module providing functions for scoring a dice_set.DiceSet as the various
legal Yahtzee combinations, e.g. threes or four-of-a-kind, and for then storing
those scores in a player's score sheet (ScoreSheet object)
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

upper_score_types = [
  'Aces',
  'Twos',
  'Threes',
  'Fours',
  'Fives',
  'Sixes'
]

lower_score_types = [
  '3 of a kind',
  '4 of a kind',
  'Full House',
  'Small Straight',
  'Large Straight',
  'Yahtzee',
  'Chance'
]

all_score_types = upper_score_types + lower_score_types

scoring_rules = {
  'Aces' : (lambda dice : num_count(dice, 1)),
  'Twos' : (lambda dice : num_count(dice, 2)),
  'Threes' : (lambda dice : num_count(dice, 3)),
  'Fours' : (lambda dice : num_count(dice, 4)),
  'Fives' : (lambda dice : num_count(dice, 5)),
  'Sixes' : (lambda dice : num_count(dice, 6)),
  '3 of a kind' : three_of_a_kind,
  '4 of a kind' : four_of_a_kind,
  'Full House' : full_house,
  'Small Straight' : small_straight,
  'Large Straight' : large_straight,
  'Yahtzee' : yahtzee,
  'Chance' : chance
}

class ScoreSheet:
  ''' Class representing a standard Yahtzee score sheet
  '''
  def __init__(self, used_type_list=None, yahtzee=0):

    self._score_sheet = {score_type : None for score_type in scoring_rules}
    self._upper_score = 0
    self._lower_score = 0
    self._bonus = 0
    self._bonus_chips = 0

    if used_type_list is not None:
      assert ((isinstance(used_type_list, list) or isinstance(used_type_list, tuple)) and 
              len(used_type_list) == len(all_score_types))
      for i in xrange(len(all_score_types)):
        if used_type_list[i] == 1:
          self._score_sheet[all_score_types[i]] = 0
          if i < len(upper_score_types):
            # random guess
            self._score_sheet[all_score_types[i]] = 3*(i+1)
            self._upper_score += 3*(i+1)
      if yahtzee == 1:
        self._score_sheet['Yahtzee'] = 50

  def is_full(self):

    return None not in self._score_sheet.values()

  def upper_score(self):

    return self._upper_score

  def lower_score(self):

    return self._lower_score

  def curr_score(self):

    return self._upper_score + self._lower_score + self._bonus + 100*self._bonus_chips

  # Marks the score on score sheet
  def record_score(self, scoreType, dice):

    assert scoreType in self._score_sheet, "Unrecognized score type {}".format(scoreType)
    assert self._score_sheet[scoreType] is None, "{} already used".format(scoreType)

    added_score = 0

    if is_yahtzee(dice) and scoreType != 'Yahtzee':
      # Special handling when trying to use yahtzee as a wildcard
      if self._score_sheet['Yahtzee'] == 50:
        self._bonus_chips += 1
        added_score += 100
      if (self._score_sheet[upper_score_types[dice.dice()[0]-1]] is None and
          scoreType in ['Full House', 'Small Straight', 'Large Straight']):
        print "Checked and {} is {}".format(upper_score_types[dice.dice()[0]-1], 
                                        self._score_sheet[upper_score_types[dice.dice()[0]-1]])
        # Bad wildcard attempt forces use of Upper Section
        scoreType = upper_score_types[dice.dice()[0]-1]

    score = scoring_rules[scoreType](dice)
    added_score += score

    self._score_sheet[scoreType] = score

    if scoreType in upper_score_types:
      # Special handling for upper score bonus
      if self._upper_score < 63 and 63 <= self._upper_score + score:
        self._bonus = 35
        added_score += 35
      self._upper_score += score
    else:
      self._lower_score += score

    return added_score

  def get_score(self, scoreType):

    assert scoreType in self._score_sheet, "Unrecognized score type {}".format(scoreType)
    return self._score_sheet[scoreType]
    
  # List of which score types have been used (indicated by a 1)
  def scored_list(self):

    scored_list = []
    for score_type in all_score_types:
      if self._score_sheet[score_type] is None:
        scored_list.append(0)
      else:
        scored_list.append(1)

    return scored_list

  def __str__(self):

    str_repr = "{:-<25}\n".format('')
    str_repr += "|{:^23}|\n".format("UPPER SECTION")
    str_repr += "{:-<25}\n".format('')
    for score_type in upper_score_types:
      str_repr += '|{:<15}|'.format(score_type)
      if self._score_sheet[score_type] is not None:
        str_repr += ' {:^5d} |\n'.format(self._score_sheet[score_type])
      else:
        str_repr += ' {:^5} |\n'.format('-')
    str_repr += "{:-<25}\n".format('')
    str_repr += "|{:<15}| {:^5d} |\n".format('TOTAL', self._upper_score)
    str_repr += "|{:<15}| {:^5d} |\n".format('Bonus', self._bonus)
    str_repr += "|{:<15}| {:^5d} |\n".format('UPPER TOTAL', self._upper_score + self._bonus)
    str_repr += "{:-<25}\n".format('')
    str_repr += "|{:^23}|\n".format("LOWER SECTION")
    str_repr += "{:-<25}\n".format('')
    for score_type in lower_score_types:
      str_repr += '|{:<15}|'.format(score_type)
      if self._score_sheet[score_type] is not None:
        str_repr += ' {:^5d} |\n'.format(self._score_sheet[score_type])
      else:
        str_repr += ' {:^5} |\n'.format('-')
    str_repr += "|{:<15}| {:^5d} |\n".format('Bonus chips', 100*self._bonus_chips)
    str_repr += "{:-<25}\n".format('')
    str_repr += "|{:<15}| {:^5d} |\n".format('Lower Total', self._lower_score)
    str_repr += "|{:<15}| {:^5d} |\n".format('Upper Total', self._upper_score + self._bonus)
    str_repr += "|{:<15}| {:^5d} |\n".format('Combined Total', self.curr_score())
    str_repr += "{:-<25}\n".format('')

    return str_repr


