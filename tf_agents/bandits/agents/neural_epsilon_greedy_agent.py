# coding=utf-8
# Copyright 2018 The TF-Agents Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A neural network based agent that implements epsilon greedy exploration.

Implements an agent based on a neural network that predicts arm rewards.
The policy adds epsilon greedy exploration.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gin
import tensorflow as tf

from tf_agents.bandits.agents import greedy_reward_prediction_agent
from tf_agents.policies import epsilon_greedy_policy


@gin.configurable
class NeuralEpsilonGreedyAgent(
    greedy_reward_prediction_agent.GreedyRewardPredictionAgent):
  """A neural network based epsilon greedy agent.

  This agent receives a neural network that it trains to predict rewards. The
  action is chosen greedily with respect to the prediction with probability
  `1 - epsilon`, and uniformly randomly with probability `epsilon`.
  """

  def __init__(
      self,
      time_step_spec,
      action_spec,
      reward_network,
      optimizer,
      epsilon,
      # Params for training.
      error_loss_fn=tf.compat.v1.losses.mean_squared_error,
      gradient_clipping=None,
      # Params for debugging.
      debug_summaries=False,
      summarize_grads_and_vars=False,
      train_step_counter=None,
      name=None):
    """Creates a Neural Epsilon Greedy Agent.

    Args:
      time_step_spec: A `TimeStep` spec of the expected time_steps.
      action_spec: A nest of `BoundedTensorSpec` representing the actions.
      reward_network: A `tf_agents.network.Network` to be used by the agent. The
        network will be called with call(observation, step_type) and it is
        expected to provide a reward prediction for all actions.
      optimizer: The optimizer to use for training.
      epsilon: A float representing the probability of choosing a random action
        instead of the greedy action.
      error_loss_fn: A function for computing the error loss, taking parameters
        labels, predictions, and weights (any function from tf.losses would
        work). The default is `tf.losses.mean_squared_error`.
      gradient_clipping: A float representing the norm length to clip gradients
        (or None for no clipping.)
      debug_summaries: A Python bool, default False. When True, debug summaries
        are gathered.
      summarize_grads_and_vars: A Python bool, default False. When True,
        gradients and network variable summaries are written during training.
      train_step_counter: An optional `tf.Variable` to increment every time the
        train op is run.  Defaults to the `global_step`.
      name: Python str name of this agent. All variables in this module will
        fall under that name. Defaults to the class name.

    Raises:
      ValueError: If the action spec contains more than one action or or it is
      not a bounded scalar int32 spec with minimum 0.
    """
    super(NeuralEpsilonGreedyAgent,
          self).__init__(time_step_spec, action_spec, reward_network, optimizer,
                         error_loss_fn, gradient_clipping, debug_summaries,
                         summarize_grads_and_vars, train_step_counter, name)
    self._policy = epsilon_greedy_policy.EpsilonGreedyPolicy(
        self._policy, epsilon=epsilon)
    self._collect_policy = self._policy
