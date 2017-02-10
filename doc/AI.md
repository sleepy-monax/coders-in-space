# IA
Salut bon voila quelque petit idée pour l'IA du projet :)
Enfaite ce que je pensais que l'on pourais faire c'est utiliser un resaux de reflexion.

![resaux de refllexion](https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Colored_neural_network.svg/300px-Colored_neural_network.svg.png)

## Un resaux de reflexion kesako ?!

Enfait un resaux est composer de noeud et de lien, chaque noeud peux contenire un valeur et chaque liens contien une force avec la quelle il connecte deux noeud.
Les noeud et les liens sour reparti en en couche.
Tout les noeud d'une couche sont relier a ceux de la couche inferieur avec un liens.
On peux tres facilement faire un analogie entre les noeud et les liens avec les neurone de notre cerveaux. Avec le noeud corespondent au noyeau et les liens aux axone de notre cerveaux.

![neurone biologique](http://physique.unice.fr/sem6/2011-2012/PagesWeb/PT/Modelisation/img/myel.gif)

## les trois type de couches

- INPUT : chaque noeud de cette couche auras une valeur egale a une valeur du jeux. par exemple la position d'un ship ou son orientation,...
- PROCESS : j'expliquerais celui ci plus tard car c'est un peux plus complexe ;)
- OUTPUT : ici c'est dans cette couche que l'on recupereras la decision de l'IA en ce basent sur la valeur du noeud. Par exemple il peux y avoir un noeud que quand la valeur est superieur à 0 et bien ca veux dire que l'IA veux attaquer.

## C'est bien jolie tout sa mais comment sa peux faire que notre IA vas aneantire les autre joueur ?

ET bien le secret c'est l'entrainement :) Enfaite a chaque partie on vas legerement faire varier aleatoirement les valeur des liens. Si les modification que l'on a effecteur permette a l'ia de gagner une partie on les garde aussi non on garde les valeur precedent.
Mintenant imaginer que l'on laisse l'IA faire des milier de partie contre elle meme, genre en faisent tourner le programme en boucle pendant des jours jusque au moment que le programe ne trouve plus de changement sur les liens qui ne permette plus a l'IA de s'ameliorer.
Et bien sa voudras dire que l'ordinateur auras trouver l'IA ultime pour gagner a ce jeux :) et ca c'est completement cheater XD

## Conclusion

Les avantage c'est que c'est pas trop copliquer a coder en revenache on ne sais pas combien de de temps il faut pour entrainer l'IA. j'ai deja vus plusieur system du meme type il faute en moyen aux moin 3000 iteration d'apprentisage pour commencer a avoir un IA qui commence a joeur corectement et 10000 pour qu'elle soit meillieur qu'un humain :/ donc faut voir ce qu'on fait moi je trouve juste sa cool de faire apprendre a jouer un ordinateur par lui meme mais bon faut voir si le prof est d'accord et si sa vous botte.
Evidament je ne suis pas un expert en machine learning donc si sa ce prouve j'ai dit de la merde XD

### La video qui ma donner l'idée :)
https://www.youtube.com/watch?v=pAqrSM3drxw
