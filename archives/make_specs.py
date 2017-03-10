f = open('coders_in_space.py', 'r')

specs = ''
is_specs = False
ignore = False

for line in f:
    valide = False
    if 'def' in line:
        valide = True

    if '"""' in line:
        valide = True
        is_specs = not is_specs
        ignore = False

    if is_specs:
        valide = True

    if 'Implementation' in line or 'implementation' in line:
        valide = False
        ignore = True

    if ignore:
        valide = False

    if valide:
        specs += line

f.close()

f = open('coders_in_space_specs.py', 'w')
f.write(specs)
f.close
