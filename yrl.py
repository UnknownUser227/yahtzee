#!/Users/syt/science/bin/python

import dice_set
import pickle
import random
import rl
import ys
import ya

''' Assorted functions to be used with the rl module to train a computer to
play yahtzee
'''

# Returns a representation of n as a list of digits with base base and min
# number of digits minLen
def to_bits(n, minLen=0, base=2, offset=0):

  bits = []
  while 0 < n or len(bits) < minLen:
    bits.append(n%base + offset)
    n /= base

  return bits

# Returns a map of all possible sorted dims-tuples with elements between min
# and max and their probability of being drawn at random
def enum_sorted_prob(min, max, dims):

  base = max - min + 1
  num_poss = (base)**dims
  sorted_count_map = {}
  for i in xrange(num_poss):
    poss = tuple(sorted(to_bits(i, minLen=dims, base=base, offset=min)))
    if poss in sorted_count_map:
      sorted_count_map[poss] += 1
    else:
      sorted_count_map[poss] = 1

  prob_map = {poss : sorted_count_map[poss]/float(num_poss) for poss in
              sorted_count_map}

  return prob_map

kScoreTypesIndex = 0
kYahtzeeUsedIndex = 11
kYahtzeeScoredIndex = 13
kRollsIndex = 14
kDiceIndex = 15
rolled_prob = [
  {},
  enum_sorted_prob(1, 6, 1),
  enum_sorted_prob(1, 6, 2),
  enum_sorted_prob(1, 6, 3),
  enum_sorted_prob(1, 6, 4),
  enum_sorted_prob(1, 6, 5)
]

# Helper function for generating state-keys
def state_tuple(i, y, r, d1, d2, d3, d4, d5):

  i_bits = to_bits(i, 13)
  return (i_bits[0], i_bits[1], i_bits[2], i_bits[3], i_bits[4], i_bits[5], i_bits[6], 
          i_bits[7], i_bits[8], i_bits[9], i_bits[10], i_bits[11], i_bits[12], y, r, 
          d1, d2, d3, d4, d5)

# Returns a map of all state-values corresponding to having scored numScored
# types already and used numRolls re-rolls this turn with their initial value
# (0)
def init_state_values(numScored=None, numRolls=None):

  num = 0
  state_values = {}
  for i in xrange(2**13 - 1):
    # Every combination of score types
    if numScored is not None and sum(to_bits(i, 13)) != numScored:
      continue
    for r in xrange(3):
      if numRolls is not None and numRolls != r:
        continue
      # How many re-rolls have been taken
      for d1 in xrange(1, 7):
        for d2 in xrange(d1, 7):
          for d3 in xrange(d2, 7):
            for d4 in xrange(d3, 7):
              for d5 in xrange(d4, 7):
                if num % 100000 == 0:
                  print num
                state_values[state_tuple(i, 0, r, d1, d2, d3, d4, d5)] = 0
                num += 1
                if to_bits(i, 13)[kYahtzeeUsedIndex] == 1:
                  state_values[state_tuple(i, 1, r, d1, d2, d3, d4, d5)] = 0
                  num += 1

  return state_values


def RollList():

  rolls = []
  for i in xrange(1, 2**5):
    bits = to_bits(i, 5)
    roll = []
    for j in range(len(bits)):
      if bits[j] == 1:
        roll.append(j)
    rolls.append(roll)
  return rolls

# All possible five-dice rolls
rolls = RollList()

# Returns a list of all Actions that can be taken from the given state
def StateActions(state):

  actions = []
  for i in xrange(kYahtzeeScoredIndex):
    if state[i] == 0:
      if (state[kDiceIndex:].count(state[kDiceIndex]) == 5 and
          state[state[kDiceIndex] - 1] == 0 and
          (ys.all_score_types[i] == 'Full House' or
           ys.all_score_types[i] == 'Small Straight' or
           ys.all_score_types[i] == 'Large Straight')):
        # Illegal to use wildcard in this case
        continue
      actions.append(ya.RecordScore(ys.all_score_types[i]))
  if state[kRollsIndex] < 2:
    for roll in rolls:
      actions.append((ya.Roll(roll)))

  return actions

# Returns the reward for taking the passed action in the passed state
def reward_func(state, action):

  if isinstance(action, ya.Roll):
    return 0
  else:
    dice = dice_set.DiceSet(5, dice=list(state[kDiceIndex:]))
    sheet = ys.ScoreSheet(state[:kYahtzeeScoredIndex],
                               state[kYahtzeeScoredIndex])
    return sheet.record_score(action.score(), dice)

# Returns a map of (state, probability of entering state) pairs when the passed
# action is taken in the passed state
def trans_func(state, action):

  new_states = []
  state_list = list(state)
  if isinstance(action, ya.Roll):
    # Generate list of all possible next states when re-rolling dice
    num_rolled = len(action.indices())
    dice = [state[kDiceIndex + i] for i in xrange(5) if i not in
            action.indices()]
    state_list[kRollsIndex] += 1
    new_dice_prob = rolled_prob[num_rolled]
    for new_dice in new_dice_prob:
      all_dice = sorted(dice + list(new_dice))
      for i in xrange(5):
        state_list[kDiceIndex + i] = all_dice[i]
      new_states.append((tuple(state_list), new_dice_prob[new_dice]))
  else:
    # Generate list of all possible next states when scoring a category
    dice = dice_set.DiceSet(5, dice=list(state[kDiceIndex:]))
    sheet = ys.ScoreSheet(state[:kYahtzeeScoredIndex],
                               state[kYahtzeeScoredIndex])
    sheet.record_score(action.score(), dice)
    state_list[ys.all_score_types.index(action.score())] = 1
    if sum(state_list[:kYahtzeeScoredIndex]) == kYahtzeeScoredIndex:
      for i in xrange(kYahtzeeScoredIndex, len(state_list)):
        state_list[i] = 0
      new_states.append((tuple(state_list), 1.0))
    else:
      state_list[kRollsIndex] = 0
      for new_dice in rolled_prob[5]:
        for i in xrange(5):
          state_list[kDiceIndex + i] = new_dice[i]
        new_states.append((tuple(state_list), rolled_prob[5][new_dice]))
  
  return new_states

# Generates optimal value functions for yahtzee
def train_comp_player():

  pickle.dump({state_tuple(2**13 - 1, 0, 0, 0, 0, 0, 0, 0) : 0},
              open('yahtzee_13_0', 'wt'))

  for num_scored in range(12, -1, -1):
    for num_rolls in range(2, -1, -1):
      print "Finding moves when we have scored {} boxes and re-rolled {} times".format(num_scored, num_rolls)
      state_values = init_state_values(numScored=num_scored, numRolls=num_rolls)
      next_state_values = pickle.load(open('yahtzee_{}_0'.format(num_scored+1)))
      for i in range(num_rolls + 1, 3):
        next_state_values.update(pickle.load(open('yahtzee_{}_{}'.format(num_scored, i), 'rt')))
      rl.value_iteration(state_values, StateActions, reward_func, trans_func, 1.0,
                        nextStateValues=next_state_values,
                        outputName='yahtzee_{}_{}'.format(num_scored, num_rolls))
      del state_values
      del next_state_values

# Generates optimal player policy from optimal value functions
def train_comp_player_policy():

  for num_scored in range(12, -1, -1):
    for num_rolls in range(2, -1, -1):
      print "Finding policy when we have scored {} boxes and re-rolled {} times".format(num_scored, num_rolls)
      state_values = init_state_values(numScored=num_scored, numRolls=num_rolls)
      next_state_values = pickle.load(open('yahtzee_{}_0'.format(num_scored+1)))
      for i in range(num_rolls + 1, 3):
        next_state_values.update(pickle.load(open('yahtzee_{}_{}'.format(num_scored, i), 'rt')))
      rl.solve_for_policy(state_values.keys(), next_state_values, StateActions,
                        reward_func, trans_func, 1.0,
                        outputName='yahtzee_{}_{}_policy'.format(num_scored, num_rolls))
      del state_values
      del next_state_values
