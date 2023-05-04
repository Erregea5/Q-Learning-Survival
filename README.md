# ReinforcementLearning
Predator-Prey Simulator using "deep" Q-learning (hardly deep)

# If you want to play around with it:
Create animals by either using the prebuilt fox, rabbit or default animal class or make your own by inheriting, defining all the animals parameters and then calling super.

Tweak the brain by changing parameters such as the decay factor:gamma, the learning rate:alpha, and the probability to explore rather than exploit:epsilon

Pygame isn't super fast and I haven't optimized so limit the number of animals at a single time

If you want some real deep Q-learning just make one animal with a deep network and make a bunch of dummy predators and prey that our animal can learn from 

# References
Source for reinforcement learning:
https://lilianweng.github.io/posts/2018-02-19-rl-overview/

Source for algorithm used to train:
https://www.cs.swarthmore.edu/~meeden/cs63/s15/nature15b.pdf
