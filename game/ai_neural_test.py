from ai_neural import create_neural_network, compute_neural_network, randomize_neural_network
from random import randint
import math

data_set_end_gate = {1 : [0, 0, 0],2 : [0, 1, 0],3 : [1, 0, 0],4 : [1, 1, 1]}

best_n = create_neural_network([2,2,1])
best_n_score = 0

for i in range(50000):
    print i
    
    n_score = 0    
    n_mutated = randomize_neural_network(best_n.copy(), 0.5)
    
    for selector in range(1, 5):
        n_input = data_set_end_gate[selector][:2]
        n_ouput = data_set_end_gate[selector][-1]


        mutated_n_output = compute_neural_network(n_mutated.copy(), n_input)[0]

        if mutated_n_output > 0.5:
            mutated_n_output = 1
        else:
            mutated_n_output = 0

        if mutated_n_output == n_ouput:
            print 'yep'
            n_score += 1

    

    if n_score > best_n_score:
        best_n = n_mutated.copy()
        if n_score == 4:
            break
        best_n_score = n_score
        print '=' * 80

while True:
    print compute_neural_network(best_n.copy(), input('Neural input ?'))
