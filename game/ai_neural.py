from random import *

def create_network(layers_description):
    """
    Create a new network.

    Parameter
    ---------
    layers_description : constitution of the network (tuple(int)).

    Return
    ------
    network : new ai network (dic).
    """

    network = {}
    layer_depht = 0

    for nb_nodes in layers_description:
        # Create the layer.
        layer = { 'nodes' : {}, 'nb_nodes' : nb_nodes }

        # Create nodes of the layer.
        for node in range(nb_nodes):
            layer['nodes'][node] = {}
            layer['nodes'][node]['value'] = 0
            # Create connection to sub nodes.
            if layer_depht != 0:
                layer['nodes'][node]['connections'] = {}
                for sub_node_index in range(len(network[layer_depht - 1]['nodes'])):
                    layer['nodes'][node]['connections'][sub_node_index] = ( randint(-100, 100) * .01 )

        # Add the layer to the network.
        network[layer_depht] = layer
        layer_depht += 1

    return network

def run_network(network, input_data):
    """
    Run the network with input data.

    Parameters
    ----------
    network : network to run (dic).
    input_data : data to input to the network (tuple).

    Return
    ------
    output_data : output of the network.
    """

    output = {}
    for layer in network:
        output = {}
        for node in network[layer]['nodes']:
            if layer == 0:
                network[layer]['nodes'][node]['value'] = input_data[node]
            else:
                for connection in network[layer]['nodes'][node]['connections']:
                    connected_node_value = network[layer - 1]['nodes'][connection]['value']
                    connection_value = network[layer]['nodes'][node]['connections'][connection]
                    value = connected_node_value * connection_value
                    network[layer]['nodes'][node]['value'] = value
                    output[node] = value

    return output

def randomize_network(network, max_value = .01):
    """
    Randomize the network.

    Parameters
    ----------
    network : network to randomize (dic).
    (optional) max_value (float).

    Return
    ------
    network : randomize network (dic).
    """
    pass

def save_network(network, file_name):
    """
    Save a network in a file.

    Parameters
    ----------
    network : network to save in the file (dic).
    file_name : name of the output file (str).
    """
    pass

def load_network(file_name):
    """
    Load a network from a file.

    Parameter
    ---------
    file_name : name of the file of the network (str).

    Return
    ------
    network : network in the file(dic).
    """
    pass
