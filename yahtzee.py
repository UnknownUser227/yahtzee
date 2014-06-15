#!/Users/syt/science/bin/python

from dice_set import DiceSet
import random
import yahtzee_score as ys

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
  'Aces' : (lambda dice : ys.num_count(dice, 1)),
  'Twos' : (lambda dice : ys.num_count(dice, 2)),
  'Threes' : (lambda dice : ys.num_count(dice, 3)),
  'Fours' : (lambda dice : ys.num_count(dice, 4)),
  'Fives' : (lambda dice : ys.num_count(dice, 5)),
  'Sixes' : (lambda dice : ys.num_count(dice, 6)),
  '3 of a kind' : ys.three_of_a_kind,
  '4 of a kind' : ys.four_of_a_kind,
  'Full House' : ys.full_house,
  'Small Straight' : ys.small_straight,
  'Large Straight' : ys.large_straight,
  'Yahtzee' : ys.yahtzee,
  'Chance' : ys.chance
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

  def record_score(self, scoreType, dice):

    assert scoreType in self._score_sheet, "Unrecognized score type {}".format(scoreType)
    assert self._score_sheet[scoreType] is None, "{} already used".format(scoreType)

    added_score = 0

    if ys.is_yahtzee(dice) and scoreType != 'Yahtzee':
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
      if self._upper_score < 63 and 63 <= self._upper_score + score:
        self._bonus = 35
        added_score += 35
      self._upper_score += score
    else:
      self._lower_score += score

    return added_score

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

    assert scoreName in scoring_rules.keys(), '{} is not a valid score type'.format(scoreName)
    self._scoreName = scoreName

  def score(self):

    return self._scoreName

class Player:

  def __init__(self, name):

    self.name = name

  def get_action(self, scoreSheet, dice):

    pass

class HumanPlayer(Player):

  def get_action(self, scoreSheet, dice):

    print dice
    while True:
      action_type = raw_input('Would you like to (R)oll or record a (S)core: ')
      if action_type == 'R':
        indices = raw_input('Which dice would you like to re-roll? ')
        try:
          indices = map(int, indices.split(' '))
          return Roll(indices)
        except ValueError as e:
          print "Expected dice to be listed as space-separated dice indices"
      elif action_type == 'S':
        score_type = raw_input('How would you like to record the dice? ')
        return RecordScore(score_type)
      else:
        print "Invalid action type"

class Game:

  def __init__(self, numPlayers):

    self._num_players = numPlayers
    self._game_state = [(HumanPlayer(raw_input("Player name: ")), ScoreSheet()) for i in xrange(numPlayers)]
    self._dice = DiceSet(5)

  def score_turn(self, scoreSheet, scoreType):

    scoreSheet.record_score(scoreType, self._dice)

  def player_turn(self, player, scoreSheet):

    assert isinstance(player, Player)
    assert isinstance(scoreSheet, ScoreSheet)

    self._dice.reset()
    self._dice.roll()

    print "It is {}'s turn. Current score sheet:\n".format(player.name)
    print scoreSheet

    while True:

      try:
        player_action = player.get_action(scoreSheet, self._dice)
        assert isinstance(player_action, Action), "Invalid action"
        if isinstance(player_action, Roll):
          assert self._dice.num_rolls() < 3, "Can only roll three times"
          self._dice.roll(player_action.indices())
        elif isinstance(player_action, RecordScore):
          self.score_turn(scoreSheet, player_action.score())
          break
      except AssertionError as e:
        print "Invalid player action: {}".format(e)

  def play_game(self):

    while True:

      remaining_moves = False
      for i in range(self._num_players):
        (player, sheet) = self._game_state[i]
        if not sheet.is_full():
          self.player_turn(player, sheet)
          remaining_moves = True

      if not remaining_moves:
        break

    print "FINAL SCORES"
    print "____________"
    for i in range(self._num_players):
      print self._game_state[i][0].name
      print self._game_state[i][1]

if __name__ == "__main__":

  pass
