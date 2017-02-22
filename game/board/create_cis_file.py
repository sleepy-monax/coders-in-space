from __future__ import print_function
import random

d = 0
while d < 10:
    print(d)

    ship_type = ['fighter', 'destroyer', 'battlecruiser']
    ship_direction = ['up', 'up-left', 'up-right', 'left', 'right', 'down', 'down-left', 'down-right']
    board_size = (random.randint(30, 60), random.randint(30, 40))
    file_name = 'board_%d.cis' % (random.randint(0, 10000))

    f = open(file_name, 'w')

    print("%d %d" % (board_size[0], board_size[1]), file=f)

    for i in range(random.randint(0, 40)):
        # x y ship_name:ship-type direction
        print('%d %d %s:%s %s' % (random.randint(0, board_size[0] - 1),\
        random.randint(0, board_size[1] - 1), 'ship_' + str(i),  ship_type[random.randint(0, len(ship_type) - 1)],\
        ship_direction[random.randint(0, len(ship_direction) - 1)]), file=f)

    f.close()
    d+=1
