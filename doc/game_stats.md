# Game Stats
> Bonjour jeune Padawan, dans cette documentation je vais te guider des méandres tordus et mal foutu la variable "game stats.

## Le Tableaux de jeux.
Le tableau de jeu est représenté par un dictionnaire de tuples contenant la liste des vaisseaux sur la case.

```python
# pour acceder aux tableau.
game_stats['board']

# pour recupere les vaisseaux sur un case :
x, y = 5, 10
chips = game_stats['board'][(x, y)]
```

## Les vaisseaux spatiaux.
Les vaisseaux sont contenu dans un dictionaire qui prend en clé le nom du vaisseau.

```python
# Rcupere un vaiseau precis :
name = 'adr'
ship = game_stats['ship'][name]
```

Les vaiseaux on les parametres suivant :
- type : le type du vaiseaux (string) pouvant être : fighter, destroyer, battlecruiser.
```python
game['ship'][name]['type']
```

- heal_point : nombre point de vie restant du vaisseau (int).
```python
game['ship'][name]['heal_point']
```

- owner : proprietaire du vaiseaux (string)
> Attention ! cette valeur est a none pour un vaiseaux abandonner. 
```python
game['ship'][name]['owner']
```

- direction : direction vers laquelle il se dirige. c'est un tuple contenat deux int qui reprsent un vecteur 2D.
```python
game['ship'][name]['direction'] = (-1, 1)
```

- speed : represent la vitesse du vaisseau (int).

- position : postion sur le plateux de jeux. c'est un tuple content deux int.
```python
# Changer la postion (Atention il ne faut pas oublier de la changer sur le plateau de jeu !):
game['ship'][name]['postion'] = (y, x)


# Position en X :
game['ship'][name]['postion'][0]

# Position en y :
game['ship'][name]['postion'][1]
```

## Les models de vaisseaux spatiaux.

## Les joueurs.

## Les autres clés.
