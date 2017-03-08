from neural import *
import time

while True:


    network = create_network((32, 100,32))
    start_time = time.time()
    result = run_network(network, (1 ,1) * 16)
    print (time.time() - start_time)

    if raw_input() == 's':
        break
