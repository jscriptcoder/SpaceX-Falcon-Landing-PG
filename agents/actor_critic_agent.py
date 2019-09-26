import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical
from collections import deque

from .device import device


class Policy(nn.Module):
    def __init__(self, input_size, output_size, hidden_size):
        super(Policy, self).__init__()
        
#        self.critic = nn.Sequential(
#            nn.Linear(input_size, hidden_size),
#            nn.ReLU(),
#            nn.Linear(hidden_size, 1)
#        )
#        
#        self.actor = nn.Sequential(
#            nn.Linear(input_size, hidden_size),
#            nn.ReLU(),
#            nn.Linear(hidden_size, output_size),
#            nn.Softmax(dim=1),
#        )
        
        self.affine = nn.Linear(input_size, hidden_size)
        self.action = nn.Linear(hidden_size, output_size)
        self.value = nn.Linear(hidden_size, 1)
        
    def forward(self, state):
        
#        value = self.critic(state)
#        probs = self.actor(state)
#        
#        return probs, value
        
        state = F.relu(self.affine(state))
        probs = F.softmax(self.action(state), dim=1)
        value = self.value(state)
        
        return probs, value


class ActorCriticAgent:
    def __init__(self, 
                 state_size, action_size,
                 hidden_size=16,
                 optim=optim.Adam, 
                 lr=1e-2):
        
        super(ActorCriticAgent, self).__init__()
        self.policy = Policy(state_size, 
                             action_size, 
                             hidden_size=hidden_size).to(device)
        self.optim = optim(self.policy.parameters(), lr=lr)
    
    def act(self, state):
        state = torch.FloatTensor(state).to(device)
        probs, value = self.policy(state)
        dist  = Categorical(probs)
        action = dist.sample()
        return action, value, dist
    
    def train(self, 
              envs, 
              n_episodes=2000,
              max_t=1000, 
              gamma=.99, 
              coef_ent=0.01, 
              coef_val=0.25, 
              print_every=100):

        scores_deque = deque(maxlen=100)
        
        for i_episode in range(1, n_episodes+1):
            
            log_probs = []
            values = []
            rewards = []
            masks = []
            entropy = 0
            scores = 0
            
            state = envs.reset()
            
            for t in range(max_t):
                action, value, dist = self.act(state)
                
                log_probs.append(dist.log_prob(action))
                values.append(value)
                entropy += dist.entropy().mean()
                
                next_state, reward, done, _ = envs.step(action.cpu().numpy())
                
                scores += reward.mean()
                
                rewards.append(torch.FloatTensor(reward).unsqueeze(1).to(device))
                masks.append(torch.FloatTensor(1 - done).unsqueeze(1).to(device))
                
                state = next_state
            
            scores = scores / max_t
            scores_deque.append(scores)
            
#            next_state = torch.FloatTensor(next_state).to(device)
#            _, next_value = self.policy(next_state)
            
            discounts = [gamma**i for i in range(len(rewards)+1)]
            
#            R = next_value
            R = 0
            returns = []
            for i in reversed(range(len(rewards))):
                R = rewards[i] + discounts[i] * R * masks[i]
                returns.insert(0, R)
            
            log_probs = torch.cat(log_probs)
            returns = torch.cat(returns).detach()
            values = torch.cat(values)
            
            advantage = returns - values
            
            actor_loss  = -(log_probs * advantage.detach()).mean()
            critic_loss = advantage.pow(2).mean()
            
            loss = actor_loss + (coef_val * critic_loss) - (coef_ent * entropy)
            
            self.optim.zero_grad()
            loss.backward()
            self.optim.step()
            
            if i_episode % print_every == 0:
                print('Episode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_deque)))
        
        envs.close()
            
        return scores