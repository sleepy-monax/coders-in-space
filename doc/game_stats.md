# Game Stats
> Bonjour jeune Padawan, dans cette documentation je vais te guider dans les méandres tordus et mal foutu la variable "game_stats".

## Le Tableaux de jeux.
Le tableau de jeu est représenté par un dictionnaire de tuples contenant la liste des vaisseaux sur la case.

```python
# pour acceder aux tableau.
game_stats['board']

# pour recupere les vaisseaux sur une case :
x, y = 5, 10
chips = game_stats['board'][(x, y)]
```

## Les vaisseaux spatiaux.
Les vaisseaux sont contenu dans un dictionaire qui prend en clé le nom du vaisseau.

```python
# Rcupere un vaiseau precis :
ship = game_stats['ships']['star-destroyer']
```

Les vaiseaux ont les parametres suivant :
- **type** : le type du vaiseaux (string) pouvant être : fighter, destroyer, battlecruiser.
```python
game['ships'][name]['type']
```

- **heal_point** : nombre point de vie restant du vaisseau (int).
```python
game['ships'][name]['heal_point']
```

- **owner** : proprietaire du vaiseaux (string)
```python
game['ship'][name]['owner']
```
> Attention ! cette valeur est a '*none*' pour un vaiseaux abandonner.

- **direction** : direction vers laquelle il se dirige. c'est un tuple contenat deux int qui reprsent un vecteur 2D.
```python
game['ships'][name]['direction'] = (-1, 1)
```

- **speed** : represent la vitesse du vaisseau (int).
```python
game['ships'][name]['speed']
```

- **position** : postion sur le plateux de jeux (tuple(int,int)).

```python
# Changer la postion (Atention il ne faut pas oublier de la changer sur le plateau de jeu !):
game['ships'][name]['postion'] = (y, x)

# Position en X :
game['ships'][name]['postion'][0]

# Position en y :
game['ships'][name]['postion'][1]
```

## Les models de vaisseaux spatiaux.
Les models de vaisseaux spatiaux sont contenus dans un dictionnaire qui prend en clé le nom du vaisseau.
```python
game_stats['model_ship']['fighter']
```

Un vaiseau a les paramètres suivants:
- **icon** : represnetation sur le plateaux de jeux (string).

> Attention ! cette valeur ne peut faire qu'un seul caractère.

```python
game_stats['model_ship'][name]['icon']
```
- **max_heal** : vie maximal (int).
```python
game_stats['model_ship'][name]['max_heal']
```
- **max_speed** : vitessse maximal (int).
```python
game_stats['model_ship'][name]['max_speed']
```
- **damages** : dégas maximaux du vaisseau (int).
```python
game_stats['model_ship'][name]['damages']
```
- **range** : distance d'attack (int).
```python
game_stats['model_ship'][name]['range']
```

- **price** : prix du vaisseau (int).
```python
game_stats['model_ship'][name]['price']
```

## Les joueurs.
Les joueurs sont contenus dans un dictionnaire qui prend en clé le nom du joueur.
```python
player = game_stats['players']['john']
```

Un joueur a les paramètres suivants:
- **money** : argent du joueur (int).
```python
game_stats['players'][name]['money']
```
- **nb_ship** : nombre de vaiseaux sur le plateaux (int).
```python
game_stats['players'][name]['nb_ship']
```
- **type** : type du joueur (string), la valeur peuxt être :```<human|ia|remote>```
```python
game_stats['players'][name]['type']
```
- **color** : couleur du joueur sur le plateaux de jeux (string).
```python
game_stats['players'][name]['color']
```
- **ships_starting_point** : point d'aparition des vaisseaux du joueur (tuple(int, int)).
```python
game_stats['players'][name]['ships_starting_point']
```
- **ships_starting_direction** : direction des vaisseaux au point d'aparition (tuple(int, int)).
```python
game_stats['players'][name]['ships_starting_direction']
```

- **fitness** : valeur servant a determiner l'ia la plus smart (int).
```python
game_stats['players'][name]['fitness']
``` 

## Les autres clés.
- **nb_round** : nombre de round depuis la derniere attack (int).
- **max_nb_round** : Nombre maximal de round sans dega avant la fin de la partie (int).
- **board_size** : Taile du plateau de jeux (tuple(int, int)).
- **pending_attacks** : liste des attacks en cours list(tuple).
- **is_game_continue** : defini si on dois continuer la boucle de jeux (bool).
