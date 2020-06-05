# Exercice pour le poste de Développeur/Développeuse Intégrations

## Objectif

Le but de cet exercice est de nous permettre d'évaluer tes compétences de développement pour le poste
de développeur/développeuse intégrations.

Cette évaluation se fera sur :
- l'organisation générale du code
- la qualité du code (style cohérent, simplicité, bonnes pratiques, ...)
- la qualité de la UI et UX de ton rendu
- le respect des consignes de l'exercice
- nos discussions lors du debrief technique sur ta solution

Il n'y a pas de contrainte de temps, mais l'exercice se veut toutefois réalisable en quelques heures de 
travail.

## Exercice

L'objectif est de réaliser un faux site e-commerce qui permette à un visiteur :
- de consulter la fiche d'un produit
- d'ajouter ce produit à son panier
- de visualiser son panier
- de passer commande avec Alma

Le présent dépôt Git contient un faux serveur d'API Alma, qui émule les fonctionnalités d'Alma 
nécessaires à cet exercice ; son utilisation est détaillée un peu plus bas.

### Rendu

Code ta solution dans un dépôt Git séparé, auquel tu pourras nous donner accès sur la plateforme de ton choix.
Un fichier README doit être présent et contenir les instructions qui nous permettront d'installer les 
dépendances de ta solution et de l'exécuter localement.

### Contraintes techniques

- Backend en PHP (Framework au choix)
- Front-end libre ; l'utilisation d'une stack JS moderne est un plus, mais pas une nécessité

### Précisions et contraintes fonctionnelles

Il ne s'agit pas de développer un site e-commerce dans son intégralité.
Voici donc ci-dessous quelques précisions sur le périmètre du développement attendu et quelques contraintes 
imposées. Tu es libre de laisser ta créativité s'exprimer autour de cette base :)

**Page produit :**
- Le produit doit valoir **moins de 100€**
- Pas besoin de page d'accueil / listing de produits ; la racine du site peut directement afficher la 
  page du produit. Celle-ci peut être majoritairement statique.
- Il n'est pas nécessaire d'implémenter un "minicart" (panier en popup) : le bouton d'ajout au panier peut 
  rediriger directement vers la page du panier
- Le client doit pouvoir choisir la quantité de produits qu'il ajoute à son panier
- Toutes les données du produit peuvent être statiques 

**Panier :**
- Le client doit pouvoir modifier la quantité de produits qu'il commande
- Un bouton "Commander" doit permettre à l'utilisateur de démarrer le tunnel de paiement

**Tunnel de paiement :**
- Tous les "achats" se font sans inscription/compte
- Alma a besoin des informations suivantes sur le client :
  - Nom/Prénom
  - Email
  - Numéro de téléphone
  - Adresse
- Le formulaire pour rentrer ces infos peut être prérempli pour gagner du temps

### Intégration d'Alma

L'intégration doit être faite avec la fausse API fournie dans ce dépôt ; cette API est toutefois proche de 
notre véritable API, et pour une bonne intégration il peut être intéressant que tu te familiarises avec notre
[guide d'intégration](https://getalma.eu/documentation/integration-guide/#compte-alma-et-sandbox).

Petit TL;DR :

- Un paiement Alma est d'abord créé via l'API lorsque le client choisit Alma dans le tunnel de paiement
  et clique sur le bouton "Payer".
- Le client est alors redirigé depuis la boutique du marchand vers la page du paiement Alma, dont l'URL est
  fournie dans les données du paiement.
- Cette page présente au client son échéancier, et procède au paiement avec un formulaire de carte bancaire.  
- Une fois le paiement effectué, le client est renvoyé vers la boutique du marchand, typiquement vers la route
  d'un contrôleur qui vérifie que le paiement a été correctement effectué et pour le bon montant
- En fonction de cette vérification, la commande est validée et une page de confirmation affichée ; une erreur 
  dans le cas contraire.

![](https://getalma.eu/documentation/integration-guide/images/general-flow.svg)

Quelques considérations d'UX à garder en tête :

- Une bonne intégration Alma permet au client de savoir, au plus tôt, qu'il pourra ou non régler l'achat d'un
  produit ou de son panier en plusieurs fois.
- On parle souvent de "3x sans frais" ou "4x sans frais", mais les marchands font souvent le choix d'appliquer
  des frais à cette facilité de paiement. Pour éviter des surprises au client, il est idéal de lui faire 
  savoir __en amont de la page de paiement Alma__ le montant des échéances et les frais éventuels qu'il
  aurait à payer s'il choisissait de payer avec Alma.

Pour t'aider à adresser ces points, l'API fournit un endpoint `POST /payments/eligibility`, décrit ci-après.
N'hésite pas à l'utiliser !

## Serveur d'API

###  Exécution du serveur

- Si ce n'est pas déjà fait, installe [Docker](https://www.docker.com/get-started) sur ta machine
- Clone ou télécharge ce dépôt
- Depuis le répertoire racine du dépôt, exécute `./serve.sh`
- L'API Alma sera alors accessible localement sur https://0.0.0.0:5000 après que Docker aura assemblé l'image
  du container
  
Si pour une raison ou une autre, tu as besoin d'utiliser un autre port que le port 5000 sur ta machine, passe
le port à utiliser au script via la variable d'environnement `PORT`. Par exemple pour le port 8080 :

```shell script
PORT=8080 ./serve.sh
``` 
  
### Endpoints disponibles

#### `POST /payments/eligibility`

Permet de savoir si un achat peut être fait en plusieurs fois avec Alma.

Le montant de l'achat et les nombres d'échéances à évaluer doivent être passés en JSON dans le corps de la 
requête :

```javascript
{
  "payment": {
    "purchase_amount": 12000,     // Montant de l'achat, en centimes
    "installments_counts": [3, 4]  // Nombres d'échéances à évaluer
  }
}
```

La réponse JSON est une liste d'objets d'éligibilité, un par nombre d'échéances demandé.
Le contenu de l'objet dépend de l'éligibilité pour chaque nombre d'échéances. Si le montant est éligible, un 
échéancier complet est fourni ; sinon, un objet détaillant les raisons du refus.

Dans l'exemple ci-dessous, l'achat est éligible au paiement en 3 fois, mais pas à celui en 4 fois car son 
montant est trop faible (inférieur à 150€) : 

```javascript
[
  {
    "installments_count": 3,      // Nombre d'échéances concerné par ce résultat
    "eligible": true,             // Résultat de l'évaluation d'éligibilité
    "installments": [             // Échéancier applicable
      {
        "due_date": 1591362744,   // Date de prélèvement de la première échéance
        "net_amount": 4000,       // Montant "net" de la première échéance (en centimes)
        "customer_fee": 180       // Montant des frais prélevés en sus du principal (en centimes)
      },   
      {
        "due_date": 1591362744,   // Date de prélèvement de la seconde échéance
        "net_amount": 4000,       // Montant "net" de la seconde échéance (en centimes)
        "customer_fee": 0         // Montant des frais prélevés en sus du principal (en centimes)
      },   
      {
        "due_date": 1591362744,   // Date de prélèvement de la troisième échéance
        "net_amount": 4000,       // Montant "net" de la troisième échéance (en centimes)
        "customer_fee": 0         // Montant des frais prélevés en sus du principal (en centimes)
      }   
    ]
  },
  {
    "installments_count": 4,      // Nombre d'échéances concerné par ce résultat
    "eligible": false,            // Résultat de l'évaluation d'éligibilité
    "constraints": {              // Contraintes auxquelles l'achat ne répond pas 
      "purchase_amount": {        
        "minimum": 15000,         // Montant minimum d'éligibilité (en centimes)
        "maximum": 100000         // Montant maximum d'éligibilité (en centimes)
      }
    }
  }
]
```

Note que dans ce cas de figure, pour un achat de 120€ payé en 3 fois, le client paie au total 121,8€ : 
3 x 40€ + 1,8€ de frais prélevés sur la première échéance _en plus_ des 40€. 

---

#### `POST /payments`

Crée un nouveau paiement vers la page duquel le client pourra être redirigé.
L'objet `Payment` est le "first-class citizen" de l'API Alma. Une fois créé grâce aux informations du panier et
du client, c'est cet objet qui représente la transaction de paiement côté Alma.

Pour le créer, il faut fournir un certain nombre d'informations, en JSON dans le corps de la requête :

```javascript
{
  "payment": {                                              // Infos du paiement
    "purchase_amount": 12000,                                 // Montant de l'achat en centimes
    "installments_count": 3,                                  // Nombre d'échéances à appliquer
    "return_url": "https://myshop.com/alma/confirm-order",     // URL vers laquelle renvoyer le client après paiement
    "shipping_address": {                                     // Adresse de livraison
      "line1": "2 rue de la Paix",                              // Numéro et rue
      "postal_code": "75008",                                   // Code postal
      "city": "Paris"                                           // Ville
    }
  },
  "customer": {                                            // Infos du client
    "first_name": "Jane",                                     // Prénom
    "last_name": "Doe",                                      // Nom
    "email": "janedoe@dummy.com",                            // Email
    "phone": "+33607080900"                                  // Téléphone
  }
}
```

Si le paiement a bien été créé, sa représentation JSON est renvoyée avec un code 200 :

````javascript
{
  "id": "47bd43628d3f4a78ab1e76f52f288f3c",                           // ID unique du paiement
  "url": "http://127.0.0.1:5000/pp/47bd43628d3f4a78ab1e76f52f288f3c", // URL de la page de paiement vers laquelle rediriger le client

  "purchase_amount": 12000,                                 // Montant du paiement
  "installments_count": 3,                                  // Nombre d'échéances
  "return_url": "https://myshop.com/alma/confirm-order",     // URL de renvoi post-paiement
  "state": "not_started",                                   // État du paiement (voir ci après)
  
  "installments": [
      {
        "due_date": 1591362744,   // Date de prélèvement de la première échéance
        "net_amount": 4000,       // Montant "net" de la première échéance (en centimes)
        "customer_fee": 180       // Montant des frais prélevés en sus du principal (en centimes)
      },
      {
        "due_date": 1591362744,   // Date de prélèvement de la seconde échéance
        "net_amount": 4000,       // Montant "net" de la seconde échéance (en centimes)
        "customer_fee": 0         // Montant des frais prélevés en sus du principal (en centimes)
      },
      {
        "due_date": 1591362744,   // Date de prélèvement de la troisième échéance
        "net_amount": 4000,       // Montant "net" de la troisième échéance (en centimes)
        "customer_fee": 0         // Montant des frais prélevés en sus du principal (en centimes)
      }
  ],

  "shipping_address": {                                     // Adresse de livraison
    "line1": "2 rue de la Paix",                              // Numéro et rue
    "postal_code": "75008",                                   // Code postal
    "city": "Paris"                                           // Ville
  },

  "customer": {                                            // Infos du client
    "first_name": "Jane",                                    // Prénom
    "last_name": "Doe",                                      // Nom
    "email": "janedoe@dummy.com",                            // Email
    "phone": "+33607080900"                                  // Téléphone
  }
}
````

Quatre valeurs sont particulièrement importantes dans le cadre de cet exercice :

- `id` permet d'associer le paiement Alma au panier du client de ton côté.
- `url` te donne l'URL vers laquelle rediriger le client lorsqu'il clique sur "Commander". 
- `return_url` est l'URL vers laquelle ton client sera renvoyé lorsqu'il aura payé avec Alma – c'est sur cette
  URL que tu dois déterminer s'il faut valider ou non la commande.
- `state` représente l'état dans lequel se trouve le paiement. Dans cette version simplifiée de l'API, seuls 
  deux états sont implémentés : `not_started` indique que le paiement _n'a pas été payé_, tandis que 
  `in_progress` indique que le paiement de la première échéance a bien eu lieu.

---

#### `GET /payments/<payment_id>`

S'il existe, renvoie le paiement correspondant à l'id demandé.

La réponse est le même objet JSON que celui renvoyé lors de la création du paiement ; si l'appel à ce endpoint
est fait _après_ le paiement par le client, alors la valeur de `state` aura changé de `not_started` vers
`in_progress`.

#### Erreurs

Cette API n'a pas été conçue de façon aussi robuste qu'une API de production : certains cas d'erreurs 
renverront potentiellement du HTML.

En cas d'erreur lors de l'appel à l'un des endpoints, la réponse sera une erreur 400 avec des informations en
JSON :

```javascript
{
  "error": {
    "field": "customer.first_name",
    "code": "missing_field"
  }
}
```

Le champ `field` est optionnel. Les trois codes d'erreur possibles sont :
- `missing_field` : une information manque dans la donnée envoyée. `field` indique alors le champ manquant.
- `invalid_value` : la valeur du champ indiqué par `field` n'est pas valide : ça peut être un problème de type
  de donnée comme un problème de valeur interdite
- `not_found` : la ressource demandée n'a pas été trouvée


## Besoin d'aide ?

Les éléments ci-dessus et la documentation d'Alma devrait te permettre de mener à bien cet exercice.  
Si toutefois quelque chose n'est pas clair pour toi, n'hésite pas à nous contacter !
