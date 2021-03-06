import torch.nn.functional as F
from torch.optim import RMSprop

class Config:
    seed = 101
    num_agents = 0
    envs = None
    num_episodes = 2000
    steps = 5
    max_steps = 1000
    state_size = 0
    action_size = 0
    hidden_units = (64, 64)
    hidden_actor = (64, 64)
    hidden_critic = (64, 64)
    activ = F.relu
    activ_actor = F.relu
    activ_critic = F.relu
    optim = RMSprop
    optim_actor = RMSprop
    optim_critic = RMSprop
    lr = 0.001
    lr_actor = 0.001
    lr_critic = 0.001
    gamma = 0.99
    ppo_clip = 0.2
    ppo_epochs = 10
    ppo_batch_size = 64
    ent_weight = 0.01
    val_loss_weight = 0.5
    grad_clip = None
    grad_clip_actor = None
    grad_clip_critic = None
    use_gae = False
    lamda = 0.95
    env_solved = 30
    times_solved = 100
    