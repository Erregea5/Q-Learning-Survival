import torch
from matplotlib import pyplot as plt
import random
class brain:
  def __init__(self, ancestor=None, activation=None, num_of_states=None, inner_layers=None, num_of_actions=None):
    self.max_layers=10
    self.max_memory=20
    self.desired_min_memory=13
    self.memory=[]
    self.prev_memory=None
    self.parameters=[]
    self.parameters_temp=[]
    self.epsilon=.1
    self.gamma=.1
    self.alpha=.1
    self.copy_time=5
    self.time=0
    self.activation=activation
    self.loss=[]
    self.rewards=[]
    layers=inner_layers

    if ancestor is None:
      if activation is None:
        activation=torch.tanh
      if layers is None:
        layers=[]
        rand=random.randint(3,7)
        for i in range(rand):
          rand2=random.randint(3,7)
          layers.append(rand2)
      if num_of_states is not None:
        layers.insert(0,num_of_states)
      if num_of_actions is not None:
        layers.append(num_of_actions)
      prev=layers[0]
      for height in layers[1:]:
        self.parameters.append(torch.randn((prev,height)))
        self.parameters.append(torch.randn(height))
        prev=height
    else:
      activation=ancestor.activation
      rand=random.random()
      if rand<.05 and len(ancestor.parameters)>4:#lose layer
        for param in ancestor.parameters[:-2]:
          self.parameters.append(param.data+torch.randn(param.shape)*self.alpha)
        out=ancestor.parameters[-1].shape[0]
        prev=self.parameters[-3].shape[0]
        self.parameters[-2]=torch.randn((prev,out))
        self.parameters[-1]=torch.randn((out))
      elif rand<.1 and len(ancestor.parameters)<self.max_layers:#adds layer before output
        for param in ancestor.parameters[:-2]:
          self.parameters.append(param.data+torch.randn(param.shape)*self.alpha)
        rand=random.randint(3,7)
        out=ancestor.parameters[-1].shape[0]
        prev=self.parameters[-1].shape[0]
        self.parameters.append(torch.randn((prev,rand)))
        self.parameters.append(torch.randn((rand)))
        self.parameters.append(torch.randn((rand,out)))
        self.parameters.append(torch.randn(out))
      else:
        for param in ancestor.parameters:
          self.parameters.append(param.data+torch.randn(param.shape)*self.alpha)

    for p in self.parameters:
      temp_param=p.clone()
      temp_param.requires_grad=True
      self.parameters_temp.append(temp_param)

  def forward(self,input,parameters)->torch.Tensor:
    output=input##forward prop
    for i in range(len(parameters)//2):
      W=parameters[2*i]
      b=parameters[2*i+1]
      output=torch.tanh(output@W+b)
    return output
  
  def backward(self,expected,actual):
    for p in self.parameters_temp:
      p.grad=None
    loss=(expected-actual.max())**2
    ###self.loss.append(loss.data)###  uncomment this to track loss
    loss.backward(retain_graph=True)
    for p in self.parameters_temp:
      p.data+=-self.alpha*p.grad

  def pass_through(self,input,reward=None):
    cur_memory=[input]
    if self.prev_memory is not None:
      self.prev_memory.append(reward)
      ###self.rewards.append(reward.data)###  uncomment this to track rewards
      self.prev_memory.append(input)
      self.memory.append(self.prev_memory)

    ##epsilon greedy
    rand=random.random()
    if(rand<self.epsilon):
      output=torch.tensor(random.randint(0,8))
    else:
      output=self.forward(input,self.parameters_temp).argmax()
    
    cur_memory.append(output)
    self.prev_memory=cur_memory

    ##random recollection of memory
    mem_size=len(self.memory)
    if mem_size>0:
      if mem_size>self.max_memory:
        self.memory=[i for i in self.memory[mem_size-self.desired_min_memory:]]
        mem_size=len(self.memory)
      rand=random.randint(0,mem_size-1)
      mem=self.memory[rand]
      expected=mem[2]
      if rand!=mem_size-1:
        expected+=self.gamma*self.forward(mem[0],self.parameters).max()
      actual=self.forward(mem[0],self.parameters_temp)
      self.backward(expected,actual)

    self.time+=1
    if self.time%self.copy_time:
      self.parameters.clear()
      for p in self.parameters_temp:
        new_param=p.clone()
        self.parameters.append(new_param)
    return output


class animal:
  def __init__(self,pos=None,ancestor=None,default=True):
    ###Default Species Parameters
    if ancestor is not None:
      self.attack_range=ancestor.attack_range
      self.attack_damage=ancestor.attack_damage
      self.anger_until_berserk=ancestor.anger_until_berserk
      self.vision_range=ancestor.vision_range
      self.species=ancestor.species
      self.time_until_hunger=ancestor.time_until_hunger
      self.damage_from_hunger=ancestor.damage_from_hunger
      self.hunger_until_damage=ancestor.hunger_until_damage
      self.food_from_kill=ancestor.food_from_kill
      self.healing_from_relaxing=ancestor.healing_from_relaxing
      self.time_relaxing_until_healing=ancestor.time_relaxing_until_healing
      self.relax_speed=ancestor.relax_speed
      self.speed=ancestor.speed
      self.focus_capacity=ancestor.focus_capacity
      self.time_to_replicate=ancestor.time_to_replicate+random.randint(-10,50)
      self.hunger_to_replicate=ancestor.hunger_to_replicate
      self.delete_on_replicate=ancestor.delete_on_replicate
      self.children=ancestor.children+random.randint(-1,1)
      self.color=ancestor.color
      self.starting_health=ancestor.starting_health
    elif default:
      self.attack_range=20
      self.attack_damage=5
      self.anger_until_berserk=3
      self.vision_range=100
      self.species=1
      self.time_until_hunger=100
      self.damage_from_hunger=1
      self.hunger_until_damage=5
      self.food_from_kill=5
      self.healing_from_relaxing=2
      self.time_relaxing_until_healing=30
      self.relax_speed=5
      self.speed=20
      self.focus_capacity=5
      self.time_to_replicate=200
      self.hunger_to_replicate=-1
      self.delete_on_replicate=True
      self.children=3
      self.color="red"
      self.starting_health=100
    
    ###Pygame params
    offset=300
    size=100

    ###Learning values
    self.reward=torch.tensor(0.0)

    ###States of Animal
    self.health=self.starting_health
    self.hunger=0
    self.anger=0
    self.time_relaxing=0
    if pos is None:
      pos=[torch.randn(1).item()*size+offset for i in range(2)]
    self.pos=pos
    self.surroundings=[0 for i in range(self.focus_capacity)]

    s2=2**-.5
    self.directions={0:(1,0),1:(s2,s2),2:(0,1),3:(-s2,s2),4:(-1,0),5:(-s2,-s2),6:(0,-1),7:(s2,-s2),8:(0,0)}
    if ancestor==None:
      self.brain=brain(num_of_states=4+self.focus_capacity*3,num_of_actions=9)
    else:
      self.brain=brain(ancestor=ancestor.brain)

  def get_entities_in_range(self,animal_list,player=None):
    i=0
    if player!=None and ((player.pos[0]-self.pos[0])**2 + (player.pos[1]-self.pos[1])**2)**.5<self.vision_range:
      self.surroundings[i]=player
      i+=1
    for animal in animal_list:
      if i>=self.focus_capacity:
        break
      if animal!=self and ((animal.pos[0]-self.pos[0])**2 + (animal.pos[1]-self.pos[1])**2)**.5<self.vision_range:
        self.surroundings[i]=animal
        i+=1
    while i<self.focus_capacity:
      self.surroundings[i]=0
      i+=1

  def move(self,direction):
    self.pos[0]+=direction[0]*self.speed
    self.pos[1]+=direction[1]*self.speed
    if direction==(0,0):
      self.time_relaxing+=1
    else:
      self.time_relaxing=0

  def update_health(self,animal_list,cap):
    time=self.brain.time
    if time%self.time_until_hunger==0:
      self.hunger+=1
    if self.hunger>self.hunger_until_damage:
      self.health-=self.damage_from_hunger
    elif self.time_relaxing>self.time_relaxing_until_healing:
      self.health+=self.healing_from_relaxing
    elif self.time_relaxing<0:
      self.hunger+=1
    if self.health<=0:
      animal_list.remove(self)
    else: self.replicate(animal_list,cap)
    
  def replicate(self,animal_list,cap):
    time=self.brain.time
    if self.hunger<self.hunger_to_replicate and time%self.time_to_replicate==0 and len(animal_list)<cap:
      for i in range(self.children):
        new_pos=[self.pos[u]+torch.randn(1).item()*10 for u in range(2)]
        animal_list.append(animal(pos=new_pos,ancestor=self,default=False))
      if self.delete_on_replicate:
        animal_list.remove(self)

  def states_to_input(self):
    states=[
      self.health,
      self.hunger,
      self.anger,
      self.time_relaxing
    ]
    for entity in self.surroundings:
      pos=(0,0,0)
      if entity!=0:
        pos=(entity.species,entity.pos[0]-self.pos[0],entity.pos[1]-self.pos[1])
      for p in pos:
        states.append(p)
    return torch.tensor(states).float()

  def act(self,animal_list,player=None):
    self.get_entities_in_range(animal_list,player)
    dir=self.brain.pass_through(self.states_to_input(),self.reward).item()
    self.move(self.directions[dir])

  def __lt__(self,other):
    mine=self.health-self.anger-self.hunger
    theirs=other.health-other.anger-other.hunger
    return mine<theirs

  def __repr__(self):
    return f'[hunger: {self.hunger} anger: {self.anger} health: {self.health} pos: {self.pos}]'
    
