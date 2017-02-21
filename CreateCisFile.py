import random
from __future__ import print_function


f = open('board_%d.cis' % (random.randint(0, 10000), 'w')
board_size = ( random.randint(30, 60), random.randint(30, 40) )
print("%d %d" % (board_size[0], board_size[1]), file=f)

for (i in range(random(0, 40))):
    pass
