import torch
from matplotlib import pyplot
import random

class brain:
  def __init__(self,ancestor=None):
    num_of_states=7
    inner_layer=15
    num_of_actions=5
    
    self.W1=torch.randn((num_of_states,inner_layer))
    self.b1=torch.randn(inner_layer)
    self.W2=torch.randn((inner_layer,num_of_actions))
    self.b2=torch.randn(num_of_actions)

    if ancestor is not None:
      lr=.1
      self.W1=ancestor.W1+self.W1*lr
      self.b1=ancestor.b1+self.b1*lr
      self.W2=ancestor.W2+self.W2*lr
      self.b2=ancestor.b2+self.b2*lr

    self.parameters=(self.W1,self.b1,self.W2,self.b2)
    for p in self.parameters:
      p.requires_grad=False
class animal:
  def __init__(self,ancestor=None):
    self.hungry=0
    self.thirsty=0
    self.angry=0
    self.food=0
    self.water=1
    self.attempts_to_hunt=0
    self.health=100
    if ancestor==None:
      self.brain=brain()
    else:
      self.brain=brain(ancestor.brain)

  def hunt(self):
    prob_to_eat=.3
    prob_to_hurt=.1
    if self.angry:
      prob_to_eat*=2
      prob_to_hurt*=2

    rand=random.random()
    if rand<=prob_to_hurt:
      self.health-=10
      self.attempts_to_hunt+=1
      self.angry+=1
    elif rand<=prob_to_eat:
      self.angry=0
      self.attempts_to_hunt=0
      self.food+=3
    else:
      self.attempts_to_hunt+=1
      if self.attempts_to_hunt>3:
        self.angry+=1

  def search(self):
    prob_to_eat=.4
    prob_to_drink=.3
    if self.angry:
      prob_to_eat/=4
      prob_to_drink/=6

    rand=random.random()
    if rand<=prob_to_drink:
      self.angry=0
      self.water+=2
    elif rand<=prob_to_eat:
      self.angry=0
      self.food+=1

  def eat(self):
    if self.food>0:
      self.food-=1
      self.hungry=0

  def drink(self):
    if self.water>0:
      self.water-=1
      self.thirsty=0

  def chill_out(self):
    if self.angry>0:
      self.angry-=1

  def update_health(self):
    if self.hungry and self.thirsty:
      self.health-=8
    elif self.thirsty:
      self.health-=4
    elif self.hungry:
      self.health-=2
    else:
      self.health+=2

  def __lt__(self,other):
    mine=self.health+self.food+self.water-self.angry-self.thirsty-self.hungry
    theirs=other.health+other.food+other.water-other.angry-other.thirsty-other.hungry
    return mine<theirs

  def __repr__(self):
    return f'hungry?: {self.hungry}\nthirsty?: {self.thirsty}\nanger: {self.angry}\nfood: {self.food}\nwater: {self.water}\nattempts: {self.attempts_to_hunt}\nhealth: {self.health}'
def states_to_input(a:animal):
  states=[
    a.hungry,
    a.thirsty,
    a.angry,
    a.food,
    a.water,
    a.attempts_to_hunt,
    a.health
  ]
  return torch.tensor(states)
def output_to_action(a:animal,t:torch.Tensor):
  i=t.argmax().item()
  if i==0:
    #print("hunting")
    a.hunt()
  elif i==1:
    #print("searching")
    a.search()
  elif i==2:
    #print("eating")
    a.eat()
  elif i==3:
    #print("drinking")
    a.drink()
  elif i==4:
    #print("chilling")
    a.chill_out()
def update_animal(a:animal,i):
  a.update_health()
  if i%5==0:
    a.hungry=1
  if i%3==0:
    a.thirsty=1
def best_of_generation(best_fox=None, best_health=[], best_food=[], best_water=[], best_hunger=[], best_thirst=[], best_anger=[]):
  foxes=[animal(best_fox) for i in range(100)]

  if best_fox is None:
    best_fox=animal()
    best_fox.health=0

  max_iterations=10
  for fox in foxes:
    health=[]
    food=[]
    water=[]
    hunger=[]
    thirst=[]
    anger=[]
    i=0
    while fox.health>0 and i<max_iterations:
      input=states_to_input(fox).float()
      a1=input@fox.brain.W1+fox.brain.b1
      o1=a1.tanh()
      a2=o1@fox.brain.W2+fox.brain.b2
      output=a2.tanh()

      output_to_action(fox,output)
      update_animal(fox,i)

      health.append(fox.health)
      food.append(fox.food)
      water.append(fox.water)
      hunger.append(fox.hungry)
      thirst.append(fox.thirsty)
      anger.append(fox.angry)
      i+=1

    if best_fox<fox:
      best_fox=fox
      best_health=health
      best_food=food
      best_water=water
      best_hunger=hunger
      best_thirst=thirst
      best_anger=anger

  return best_fox, best_health, best_food, best_water, best_hunger, best_thirst, best_anger
def best_of_epoch(epoch=50):
  fox=None
  health=[]
  food=[]
  water=[]
  hunger=[]
  thirst=[]
  anger=[]
  for i in range(epoch):
    fox, health, food, water, hunger, thirst, anger=best_of_generation(fox, health, food, water, hunger, thirst, anger)
  return fox, health, food, water, hunger, thirst, anger
print(best_of_epoch(1))
