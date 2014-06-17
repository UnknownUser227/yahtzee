#!/Users/syt/science/bin/python

from dice_set import DiceSet
import pickle
import random
import ys
import ya

# Class representing a Yahtzee player. Subclasses should implement the
# get_action method
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
        indices = raw_input('Which dice would you like to re-roll? Enter as space-separated dice indices (from 1 to 5)')
        try:
          indices = [int(i) - 1 for i in indices.split(' ')]
          return ya.Roll(indices)
        except ValueError as e:
          print "Expected dice to be listed as space-separated dice indices"
      elif action_type == 'S':
        score_type = raw_input('How would you like to record the dice? ')
        return ya.RecordScore(score_type)
      else:
        print "Invalid action type"

class ComputerPlayer(Player):

  def __init__(self, name, dataDir):

    Player.__init__(self, name)
    if dataDir == '':
      self._data_dir = '.'
    elif dataDir[-1] == '/':
      self._data_dir = dataDir[:-1]
    else:
      self._data_dir = dataDir

  def get_action(self, scoreSheet, dice):

    print dice
    scored_list = scoreSheet.scored_list()
    num_scored = sum(scored_list)
    num_rolls = dice.num_rolls() - 1
    policy_file = open('{}/yahtzee_policy_{}_{}'.format(self._data_dir, num_scored, num_rolls),
                       'rt')
    policy = pickle.load(policy_file)
    policy_file.close()
    state_tuple = tuple(scored_list + [1 if scoreSheet.get_score('Yahtzee')
                                       else 0] + [num_rolls] + dice.dice())
    action = policy[state_tuple]
    del policy
    return action

class Game:

  def __init__(self, numPlayers = None):

    self._num_players = numPlayers
    if numPlayers is None:
      self._num_players = int(raw_input("How many players? "))

    self._game_state = []
    for i in range(self._num_players):
      player_type = ''
      while player_type != 'H' and player_type != 'C':
        player_type = raw_input("Is this a (H)uman or (C)omputer player? ")
      if player_type == 'H':
        self._game_state.append((HumanPlayer(raw_input("Player name: ")),
                                ys.ScoreSheet()))
      elif player_type == 'C':
        data_dir = raw_input("Where are the policy files located? ")
        self._game_state.append((ComputerPlayer(raw_input("Player name: "), dataDir=data_dir),
                                ys.ScoreSheet()))
    self._dice = DiceSet(5)

  def score_turn(self, scoreSheet, scoreType):

    scoreSheet.record_score(scoreType, self._dice)

  def player_turn(self, player, scoreSheet):

    assert isinstance(player, Player)
    assert isinstance(scoreSheet, ys.ScoreSheet)

    self._dice.reset()
    self._dice.roll()

    print "It is {}'s turn. Current score sheet:\n".format(player.name)
    print scoreSheet

    while True:

      try:
        player_action = player.get_action(scoreSheet, self._dice)
        assert isinstance(player_action, ya.Action), "Invalid action"
        if isinstance(player_action, ya.Roll):
          assert self._dice.num_rolls() < 3, "Can only roll three times"
          self._dice.roll(player_action.indices())
          print "{} re-rolled dice {} : {}".format(player.name,
                                                   [i + 1 for i in player_action.indices()],
                                                   self._dice)
        elif isinstance(player_action, ya.RecordScore):
          self.score_turn(scoreSheet, player_action.score())
          print "{} scored {}".format(player.name, player_action.score()) 
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

  game = Game()
  game.play_game()
