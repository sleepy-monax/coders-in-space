from neural import *
while True:

    network = create_network((3, 3, 3))
    result = run_network(network, (100,100,100))

    print result

    if raw_input() == 's':
        break
