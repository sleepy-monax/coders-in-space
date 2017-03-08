from ai_neural import create_neural_network, compute_neural_network, randomize_neural_network
from random import randint
import math

data_set_end_gate = {1 : [1, 0, 0, 0],2 : [1, 0, 1, 1],3 : [1, 1, 0, 1],4 : [1, 1, 1, 0]}

best_n = create_neural_network([3, 1])

for i in range(50000):
    print i
    selector = randint(1, 4)
    n_input = data_set_end_gate[selector][:3]
    n_ouput = data_set_end_gate[selector][-1]
    n_mutated = randomize_neural_network(best_n.copy(), 0.5)

    mutated_n_output = compute_neural_network(n_mutated.copy(), n_input)[0]

    if mutated_n_output > 0.5:
        mutated_n_output = 1
    else:
        mutated_n_output = 0

    if mutated_n_output == n_ouput:
        print 'yep'
        n = n_mutated.copy()

while True:
    print compute_neural_network(n.copy(), input('Neural input ?'))
