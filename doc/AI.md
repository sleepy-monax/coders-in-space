# IA
Salut bon voila une petite idée pour l'IA du projet :)
Enfaite ce que je pensais que l'on pourais faire c'est utilisé un résaux de réflexion.

![resaux de refllexion](https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Colored_neural_network.svg/300px-Colored_neural_network.svg.png)

## Un réseau de réflexion kesako ?!

En fait un réseau est composé de noeud et de lien, chaque noeud peut contenir une valeur et chaque lien contient une force avec laquelle il connecte deux noeuds.
Les noeuds et les liens sissaient reparti en couche.
Tous les noeuds d'une couche sont relié à ceux de la couche inférieure avec un lien.
On peut très facilement faire une analogie entre les noeuds et les liens avec les neurones de notre cerveau. Avec le noeud correspondent au noyau et les liens aux axones de notre cerveau.

![neurone biologique](http://physique.unice.fr/sem6/2011-2012/PagesWeb/PT/Modelisation/img/myel.gif)

## les trois types de couches

- INPUT : chaque noeud de cette couche auras une valeur égale à une valeur du jeu. par exemple la position d'un ship ou son orientation, etc
- PROCESS : j'expliquerais celui-ci plus tard car c'est un peux plus complexe ;)
- OUTPUT : dans cette couche que on y recupereras la décision de l'IA en se basent sur la valeur des noeuds. Par exemple il peut y avoir un noeud que quand la valeur est supérieure à 0 et bien ça veut dire que l'IA veut attaquer.

## C'est bien jolie tout sa mais comment sa peux faire que notre IA vas aneantire les autre joueur ?

Et bien le secret c'est l'entrainement :) En Fait à chaque partie on va légèrement faire varier aléatoirement les valeurs des liens. Si les modifications que l'on a effectuées permettent à l'ia de gagner une partie, alors on les garde. Aussi non on garde les valeurs précédent.
Maintenant imaginer que l'on laisse l'IA faire des milliers de partie contre elle-même, genre en ferait tourner le programme en boucle pendant des jours jusqu'au moment où le programme ne trouve plus de changement sur les liens qui ne permette plus à l'IA de s'améliorer.
Et bien sa voudras dire que l'ordinateur auras trouver l'IA ultime pour gagner à ce jeu :) et ça c'est complètement cheater XD

## Conclusion

Les avantages ce n'est pas trop compliquer à coder, en revanche on ne sait pas combien de de temps il faut pour entrainer l'IA. j'ai déjà vu plusieurs systèmes du même type il faut en moyen au moins 3000 itérations d'apprentissage pour commencer à avoir un IA qui commence à jouer correctement et 100 000 pour qu'elle soit meilleure qu'un humain :/ donc faut voir ce qu'on fait moi je trouve juste sa cool à faire apprendre à jouer un ordinateur par lui-même mais bon faut voir si le prof est d'accord et si ça vous botte.
Evidament je ne suis pas un expert en machine learning donc si sa se prouve j'ai dit de la merde XD

### La video qui ma donner l'idée :)
https://www.youtube.com/watch?v=pAqrSM3drxw
