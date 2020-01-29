---
title: "Nous sommes désolés de vous apprendre que..."
date: 2017-01-26 11:11:03 +0100
draft: false
---

*Ce post est une traduction libre de ["We Are Sorry To Inform You"](http://www.fang.ece.ufl.edu/reject.html)*

*Il présente des commentaires de peers auxquels certains articles fondateurs de l'informatique et de la cryptographie moderne ont été envoyés.*

<!-- more -->

# E.W. DIJKSTRA

**"Goto Statements Considered Harmful"** Cette publication essaie de nous convaincre que la fonctionnalité *goto* devrait être retirée des langages de programmation, ou au moins (puisque je ne pense pas qu'elle sera un jour éliminée) que les programmeurs cessent de l'utiliser. Son successeur n'est pas vraiment explicité. Ce document n'explique pas comment le "if" serait utilisé sans *goto* pour rediriger le flux d'exécution : est-ce que toutes les post-conditions devraient être contenues dans un seul bloc, ou est-ce que nous devrions utiliser le "if" arithmétique, qui ne contient pas ce méchant *goto* ?

Et comment gérer le cas dans lequel il est nécessaire, après avoir atteint la fin d'une alternative, de continuer l'exécution dans une autre partie du programme ?

L'auteur est un défendeur d'un style de programmation "structurée" dans lequel, si je comprends bien, les *goto* sont remplacés par de l'indentation. La programmation structurée est un exercice académique intéressant qui fonctionne bien pour des exemples simples, mais je doute qu'aucun programme sérieux soit jamais écrit dans ce style. Dix ans d'expérience du Fortran dans l'industrie ont prouvé à toutes les parties concernées que, dans le monde réel, *goto* est utile et nécessaire : sa présence présente peut-être certains inconvénients au niveau du débuggage, mais c'est un standard *de facto* et nous devons essayer de vivre avec. Il faudra plus que les élucubrations académiques d'un puriste pour le supprimer de nos langages.

Publier ce document serait un gaspillage de papier : s'il est publié, je suis prêt à parier que personne ne le citera ni ne le remarquera car je suis sûr que dans 30 ans le *goto* sera encore en grande forme et toujours autant utilisé qu'aujourd'hui.

Commentaires confidentiels à l'éditeur : l'auteur devrait retirer le papier et l'envoyer quelque part où il ne subira pas de *peer review*. Une lettre à l'éditeur serait le choix parfait : personne ne le remarquera !

# E.F. CODD

**"A Relational Model of Data for Large Shared Data Banks"** Ce document propose que toutes les données dans les bases de données soient représentées sous la forme de relations - des ensembles de tuples - et que toutes les opérations d'accès aux données soient faites sur ce modèle. Certaines des idées présentées dans ce document sont intéressantes et pourraient être utiles mais, en général, ce travail très préliminaire ne parvient pas à démontrer ni son implémentation, ni sa performance, ni son utilité pratique. L'argument général du document est que la représentation tabulaire qui est présentée devrait être utilisable pour un accès général aux données, mais je peux voir deux problèmes avec cette affirmation : l'expressivité et l'efficacité.

Le document ne contient aucun vrai exemple pour nous convaincre qu'un modèle ayant un interêt pratique puisse être représenté de cette manière. Bien au contraire, je doute à première vue que quelque chose d'assez complexe pour avoir un interêt pratique puisse être modélisé avec des relations. La simplicité de ce modèle empêche par exemple de représenter directement des hiérarchies et force à les remplacer par un système complexe de "clés étrangères". Dans cette situation, n'importe quel modèle réaliste finirait par être composé de douzaines de tables interconnectées - ce qui semble difficilement être une solution pratique vu que nous pourrions probablement représenter le même modèle en deux ou trois fichiers bien formatés.

Encore pire, le document ne contient aucune évaluation d'efficacité : il n'y a pas d'expérience avec des données vraies ou synthétiques afin de comparer la performance de cette approche avec celle plus traditionnelle sur des problèmes de la vraie vie. La raison principale d'utiliser des formats de fichier spécialisés est l'efficacité : les données peuvent être organisées de manière à ce que les méthodes d'accès classiques soient efficaces. Ce document propose un modèle dans lequel, pour extraire n'importe quelle réponse relativement significative depuis une vraie base de données, l'utilisateur se retrouvera à devoir faire un nombre très important de jointures. Pourtant, aucun résultat expérimental ni aucune indication ne sont donnés sur la manière dont il serait possible de gérer de plus importantes quantités de données.

Le formalisme présenté est trop complexe et mathématique sans vrai raison, utilise des concepts et une notation avec lesquels l'employé de banque moyen n'est pas familier. Le document n'explique pas comment transformer ces opérations ésotériques en blocs d'accès exécutables.

En additionant le manque d'exemples concrets, de tests de performances et de détails concernant une possible implémentation, il ne reste qu'un exercice obscur utilisant des mathématiques très peu familières et avec de faibles conséquences pratiques. Il peut être rejeté sans peur.

# R.L. RIVEST, A. SHAMIR, AND L. ADELMAN

**"A Method for Obtaining Digital Signatures and Public-Key Cryptosystems"** D'après la (très courte) introduction, ce document a pour but de présenter une implémentation du crypto-système à clé publique de Diffie et Hellman pour le courrier électronique. S'il s'avère que c'est bien son but, ce document devrait être rejeté à cause du fait qu'il n'est pas à la hauteur de ce qu'il annonce et pour sa non-pertinence.

Je doute qu'un tel système soit un jour utilisable en pratique. Ce document n'arrive pas à convaincre le lecteur de la praticité de la solution. Premièrement, il y a le problème du nombre *n* utilisé pour factoriser le message. La sécurité de cette technique repose sur le fait que factoriser *n* en facteurs premiers prenne tellement de temps qu'elle en soit impossible en pratique. Les auteurs insistent aussi sur la nécessité pour l'algorithme de chiffrement d'être rapide et - si l'on veut que l'application au courrier électronique ait du sens - de pouvoir tourner sur beaucoup de sortes de machines différentes. Soyons généreux et imaginons que chaque utilisateur d'ordinateur ait accès à un mini-ordinateur dernière génération tel que le VAX. Les considérations de vitesse de cette machine 32-bits limitent le choix de *n* à *n < 2^32 = 4 294 967 296*. C'est en effet un grand nombre, mais d'après les résultats du Tableau 1 du document, il peut être factorisé en quelques heures. Difficilement une marge de temps inspirant la sécurité !

De plus, comme l'avouent les auteurs, un standard de chiffrement de données existe déjà et est supporté par le Nation Bureau of Standards américain et IBM, le plus gros fabricant d'ordinateurs. Il y a très peu de chances qu'une méthode allant à l'encontre de ce standard soit adoptée d'une manière significative. Il est vrai que la méthode d'IBM peut se heurter à un problème de distribution de clés, mais leur méthode est un standard et nous devons vivre avec. Au lieu de créer des méthodes non-standard qui seront bientôt abandonnées faute d'utilisateurs, les auteurs devraient essayer d'étendre le standard et trouver des moyens de distribuer les clés de chiffrement de manière sécurisée.

Dernièrement, il se pose la question de l'application. Le courrier électronique sur Arpanet est un gadget sympathique, mais il est peu probable qu'il soit un jour diffusé en dehors des cercles académiques et des laboratoires publics - des environnements dans lesquels la nécessité de confidentialité n'est pas pressante. Les laboratoires ayant des contacts militaires ne communiqueront jamais au travers d'Arpanet ! Soit des gens normaux ou des petites entreprises pourront chacun s'offrir un VAX, ou bien le marché du courrier électronique restera minuscule. Il est vrai que nous voyons l'apparition de micro-ordinateurs, comme le récemment annoncé Apple II, mais leurs limitations sont telles que ni eux ni leurs successeurs n'auront la puissance nécessaire pour communiquer sur un réseau.

L'introduction ne fait que deux paragraphes de long, les sources ne sont pas présentées ni citées, et il n'y a presque aucune comparaison avec l'état de l'art. En résummé, il semblerait que ce document soit un exercice mathématique peu original (les auteurs affirment que la plupart de leurs idées proviennent d'autres publications) trop éloigné d'une implémentation pratique, allant à l'encontre des standards établis et ayant une aire d'application dont la faisabilité est douteuse. Ceci n'est pas le genre d'article que nos lecteurs souhaitent voir dans notre journal. Rejet.
