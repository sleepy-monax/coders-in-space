from PIL import Image
import random

def convert(file_name, output):
	"""
	Convert a image to a CIS file.
	
	Parameters
	----------
	file_name: path to the IMG (str).
	out_put: name of the cis file (str).
	
	Notes
	-----
	pillow need to be intalled (pip install pillow) !.
	image only on ".PNG" format.
	"""
    im = Image.open(file_name)
    pix = im.load()

    ships_names = ['Aeneas', 'Aleksander', 'Amphitrite', 'Antigone', 'Bismarck', 'Bucephalus', 'Cerberus',
				   'Circe', 'Cyrus', 'Emperor\'s_Fury', 'Eos', 'Fury', 'Gray_Tiger', 'Helios', 'Hephaestus',
				   'Herakles', 'Hoosier', 'Huey_Long', 'Hurricane', 'Hyperion', 'Iron_Fist', 'Iron_Justice',
				   'Jackson_V', 'Jackson\'s_Revenge', 'Kimera', 'Kimeran_Juggernaut', 'Leviathan', 'Loki',
				   'Meleager', 'Merrimack', 'Metis', 'Napoleon', 'Norad_II', 'Norad_III', 'Palatine',
				   'Patroclus', 'Phobos', 'Ragnorak', 'Scion', 'Tahoe', 'Theodore_G._Bilbo', 'Thunder_Child',
				   'Titan', 'Valor_of_Vardona', 'Victory', 'White_Star']

    ship_facing = ['up', 'up-left', 'up-right', 'left', 'right', 'down', 'down-left', 'down-right']

    buffer = ''  # Create the string buffer for the file.
    buffer += "%d %d\n" % (im.size)  # Add the first of the file whith the size of the game board.

    i = 0

    for x in range(im.size[0]):
        for y in range(im.size[1]):
            pixel_value = pix[x, y]

            r = pixel_value[0]
            g = pixel_value[1]
            b = pixel_value[2]

            ship_type = ''

            if r == 255:
                ship_type = 'battlecruiser'
            elif g == 255:
                ship_type = 'destroyer'
            elif b == 255:
                ship_type = 'fighter'
            else: continue

            buffer += '%d %d %s:%s %s\n' % (y + 1,  # Y coodinate of the ship.
                                            x + 1,  # X coodinate of the ship.
                                            random.choice(ships_names) + str(i),  # Name of the ship.
                                            ship_type,  # Type of the ship.
                                            ship_facing[random.randint(0, len(ship_facing) - 1)])  # Facing of the ship
            i += 1


    f = open(output, 'w')
    f.write(buffer)
    f.close()

convert('test.png', 'board/test.cis')