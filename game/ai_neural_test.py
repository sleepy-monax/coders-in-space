from ai_neural import *
print 'creating neural network...'
network = create_network((3, 3, 3))
print 'calculating...'
result = run_network(network, (1.,2.,3.))
print 'done'

print result
raw_input()
