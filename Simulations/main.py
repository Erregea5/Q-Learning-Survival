import pygame
from animal_ai import *

pygame.init()
width=1280
height=720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
dt = 0

def in_torus(pos):
  return [pos[0]%width,pos[1]%height]
def in_bound(pos):
  lower_bound=20.0
  upper_bound=20.0
  x=pos[0]
  y=pos[1]
  if y<lower_bound:y=lower_bound
  elif y>height-upper_bound:y=height-upper_bound
  if x<lower_bound:x=lower_bound
  elif x>width-upper_bound:x=width-upper_bound
  return [x,y]

class fox(animal):
  def __init__(self):
    self.attack_range=20
    self.attack_damage=10
    self.anger_until_berserk=3
    self.vision_range=250
    self.species=3
    self.time_until_hunger=100
    self.damage_from_hunger=1
    self.hunger_until_damage=5
    self.food_from_kill=5
    self.healing_from_relaxing=2
    self.time_relaxing_until_healing=30
    self.relax_speed=5
    self.speed=5
    self.focus_capacity=3
    self.time_to_replicate=random.randint(200,400)
    self.hunger_to_replicate=0
    self.children=2
    self.color="red"
    self.starting_health=600
    self.delete_on_replicate=True
    super().__init__(default=False)

class rabbit(animal):
  def __init__(self):
    self.attack_range=10
    self.attack_damage=0
    self.anger_until_berserk=100
    self.vision_range=200
    self.species=2
    self.time_until_hunger=100000
    self.damage_from_hunger=1
    self.hunger_until_damage=5
    self.food_from_kill=5
    self.healing_from_relaxing=2
    self.time_relaxing_until_healing=30
    self.relax_speed=5
    self.speed=6
    self.focus_capacity=3
    self.time_to_replicate=random.randint(200,500)
    self.hunger_to_replicate=1
    self.children=3
    self.color="white"
    self.starting_health=1000
    self.delete_on_replicate=True
    super().__init__(default=False)

class player:
  def __init__(self):
    ###initial player parameters
    starting_pos=(screen.get_width() / 2, screen.get_height() / 2)
    self.species=5
    self.attack_range=20
    self.attack_damage=10
    self.anger_until_berserk=3
    self.time_until_hunger=50
    self.damage_from_hunger=0
    self.hunger_until_damage=5
    self.food_from_kill=5
    self.healing_from_relaxing=2
    self.time_relaxing_until_healing=30
    self.speed=300

    self.pos = starting_pos
    self.health=10000
    self.hunger=0
    self.anger=0
    self.time_relaxing=0
    
  def update_health(self,time):
    if time%self.time_until_hunger==0:
      self.hunger+=1
    if self.hunger>self.hunger_until_damage:
      self.health-=self.damage_from_hunger
    elif self.time_relaxing>self.time_relaxing_until_healing:
      self.health+=self.healing_from_relaxing
    elif self.time_relaxing<0:
      self.hunger+=1
  
  def attack_closest_animal(self,animals):
    for entity in animals:
      if ((entity.pos[0]-self.pos[0])**2 + (entity.pos[1]-self.pos[1])**2)<=self.attack_range**2:
        entity.health-=self.attack_damage
        if self.anger>self.anger_until_berserk:
          entity.health-=self.attack_damage
          self.anger-=1
        entity.anger+=1
        if entity.health<=0:
          self.hunger-=self.food_from_kill
        break

  def update(self,animals):
    if self.health>0:
      self.pos=in_bound(self.pos)
      pygame.draw.circle(screen, "black", self.pos, 12)

      relaxing=True
      keys = pygame.key.get_pressed()
      if keys[pygame.K_w]:
        self.pos[1] -= self.speed * dt
        relaxing=False
      if keys[pygame.K_s]:
        self.pos[1] += self.speed * dt
        relaxing=False
      if keys[pygame.K_a]:
        self.pos[0] -= self.speed * dt
        relaxing=False
      if keys[pygame.K_d]:
        self.pos[0] += self.speed * dt
        relaxing=False
      if keys[pygame.K_SPACE]:
        self.attack_closest_animal(animals)
      
      if relaxing:
        self.time_relaxing+=1
      else: self.time_relaxing=0

class animal_list:
  def __init__(self):
    foxes=5
    rabbits=6
    self.cap=15
    self.animals=[fox() for i in range(foxes)]+[rabbit() for i in range(rabbits)]

  def do_attacks(self,player):
    self.animals.append(player)
    n=len(self.animals)
    attacked=[]
    for i in range(n):
      animali=self.animals[i]
      for u in range(i+1,n):
        animalu=self.animals[u]
        if animalu in attacked or animali.species==animalu.species:
          continue
        if ((animalu.pos[0]-animali.pos[0])**2 + (animalu.pos[1]-animali.pos[1])**2)<=max(animali.attack_range,animalu.attack_range)**2:
          #print(animali.pos," attacking ",animalu.pos)
          attacked.append(animalu)
          animalu.health-=animali.attack_damage
          animali.health-=animalu.attack_damage
          if animali.anger>animali.anger_until_berserk:
            animalu.health-=animali.attack_damage
            animali.anger=0
          if animalu.anger>animalu.anger_until_berserk:
            animali.health-=animalu.attack_damage
            animalu.anger=0
          animalu.anger+=1
          animali.anger+=1
          if animalu.health<=0:
            animali.hunger-=animali.food_from_kill
          elif animali.health<=0:
            animalu.hunger-=animalu.food_from_kill
          break
    self.animals.pop()

  def give_rewards(self):
    for a in self.animals:
      if a.brain.time>1:
        last_memory=a.brain.prev_memory[0]
        d_health=a.health-last_memory[0]
        d_hunger=a.hunger-last_memory[1]
        d_anger=a.anger-last_memory[2]
        d_distances=0
        for i in range(a.focus_capacity):
          cur=a.surroundings[i]
          if cur==0:
            break
          dist=(cur.pos[0]**2+cur.pos[1]**2)**.5
          if cur.species>a.species:
            d_distances-=dist            
          else:d_distances+=dist
        a.reward=d_health-d_hunger-d_anger+d_distances*10/a.vision_range
      ##add + proximity to prey and - proximity to predators

  def update(self,player):
    for a in self.animals:
      a.pos=in_bound(a.pos)
      pygame.draw.circle(screen, a.color, a.pos, 10)
      a.act(self.animals,player)
      self.do_attacks(player)
      a.update_health(self.animals,self.cap)
      self.give_rewards()

p=player()
animals=animal_list()
time=0
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  screen.fill("green")

  p.update(animals.animals)
  animals.update(p)
  time+=1
  pygame.display.flip()
  dt = clock.tick(30) / 1000

pygame.quit()
### plot rewards and loss
##for a in animals.animals:
  ##plt.plot(a.brain.rewards)
  ##plt.plot(a.brain.loss)
##plt.show()