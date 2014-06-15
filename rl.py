#!/Users/syt/science/bin/python

import pickle

def StateActionValue(nextStateValues, state, action, rewardFunc, transFunc, gamma):

  state_action_value = rewardFunc(state, action)
  new_states_dist = transFunc(state, action)
  for new_state, p in new_states_dist:
    state_action_value += gamma*p*nextStateValues[new_state]
  return state_action_value

def StateValue(nextStateValues, state, actions, rewardFunc, transFunc, gamma):

  assert isinstance(actions, list)
  if len(actions) == 0:
    return 0

  best_action = actions[0]
  best_state_action_value = StateActionValue(nextStateValues, state, best_action, rewardFunc,
                                             transFunc, gamma)
  for action in actions[1:]:
    state_action_value = StateActionValue(nextStateValues, state, action, rewardFunc, transFunc,
                                          gamma)
    if best_state_action_value < state_action_value:
      best_action = action
      best_state_action_value = state_action_value

  return best_state_action_value

def ValueIteration(values, actionFunc, rewardFunc, transFunc, gamma,
                   outputName='state_values', outputFreq=10,
                   nextStateValues=None):

  iters = 0
  old_state_values = {}
  while True:
    print iters
    # Repeat until convergence
    state_num = 0
    for state in values:
      # Get the allowable actions
      action_list = actionFunc(state)
      new_state_value = StateValue(nextStateValues, state, action_list, rewardFunc,
                                   transFunc, gamma)
      values[state] = new_state_value
      state_num += 1
      if state_num % 1000 == 0:
        print '  {}'.format(state_num)

    iters += 1
    #if iters % outputFreq == 0:
    #  print "Writing to {}_{}".format(iters)
    #  pickle.dump(values, open('{}_{}'.format(outputName, iters), 'wt'))
    #if old_state_values == values:
    print "Writing to {}".format(outputName, iters)
    pickle.dump(values, open('{}'.format(outputName), 'wt'))
    break
    old_state_values = values

def SolveForPolicy(states, nextStateValues, actionFunc, rewardFunc, transFunc, gamma, outputName):

  policy = {}
  for state in states:
    actions = actionFunc(state)
    best_action = actions[0]
    best_state_action_value = StateActionValue(nextStateValues, state, best_action, rewardFunc,
                                               transFunc, gamma)
    for action in actions[1:]:
      state_action_value = StateActionValue(nextStateValues, state, action,
                                            rewardFunc, transFunc, gamma)
      if best_state_action_value < state_action_value:
        best_action = action
        best_state_action_value = state_action_value

    policy[state] = best_action
  pickle.dump(policy, open('{}'.format(outputName), 'wt'))
