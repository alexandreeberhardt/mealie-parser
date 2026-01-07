# Importateur de Recettes Mealie

Ce projet met à disposition une interface utilisateur web permettant de convertir des recettes de cuisine au format texte brut en fichiers JSON structurés, conformes au standard Schema.org/Recipe. L'objectif est de faciliter l'importation de recettes dans des gestionnaires comme Mealie.

L'application utilise l'API d'OpenAI (modèle GPT-4o-mini) pour analyser le texte et extraire les informations pertinentes telles que les ingrédients, les instructions, les temps de préparation et les données nutritionnelles.

## Fonctionnalités

* **Conversion de texte brut :** Transformation de n'importe quel texte de recette en structure de données JSON.
* **Conformité Schema.org :** Génération de fichiers JSON-LD compatibles avec le type `Recipe`, incluant les ingrédients, instructions et métadonnées.
* **Gestion des durées :** Conversion automatique des temps (préparation, cuisson) au format ISO 8601 (ex: PT15M).
* **Interface Web :** Interface simple développée avec Streamlit pour coller le texte et visualiser le résultat.
* **Déploiement conteneurisé :** Support complet pour Docker et Docker Compose.

## Prérequis technique

* Docker et Docker Compose (recommandé).
* Une clé API OpenAI valide.
* Python 3.11 (si exécution locale sans Docker).

## Installation et Démarrage

### Utilisation avec Docker (Recommandé)

Le projet inclut un fichier `docker-compose.yml` pour un déploiement rapide.

1.  **Configuration de l'environnement :**
    Assurez-vous que la variable d'environnement `OPENAI_API_KEY` est définie dans votre système ou créez un fichier `.env` à la racine du projet contenant :
    ```bash
    OPENAI_API_KEY=votre_cle_api_ici
    ```

2.  **Lancement du service :**
    Exécutez la commande suivante à la racine du projet :
    ```bash
    docker-compose up -d --build
    ```
    Le conteneur sera nommé `mealie_parser_ui` et l'application sera accessible sur le port 8501.

3.  **Accès à l'application :**
    Ouvrez votre navigateur et accédez à l'adresse : `http://localhost:8501`.

### Installation Locale (Sans Docker)

1.  **Installation des dépendances :**
    Il est recommandé d'utiliser un environnement virtuel. Installez les paquets requis listés dans `requirements.txt` :
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration de la clé API :**
    Créez un fichier `.env` à la racine ou exportez la variable dans votre terminal :
    ```bash
    export OPENAI_API_KEY=votre_cle_api_ici
    ```

3.  **Lancement de l'application :**
    Démarrez le serveur Streamlit :
    ```bash
    streamlit run app.py
    ```

## Structure du Projet

* `app.py` : Point d'entrée de l'application Streamlit. Gère l'interface utilisateur et l'affichage des résultats.
* `mealie_parser.py` : Contient la logique métier, l'appel à l'API OpenAI et la validation du schéma JSON.
* `Dockerfile` : Fichier de configuration pour la construction de l'image Docker (basée sur Python 3.11-slim).
* `docker-compose.yml` : Configuration pour l'orchestration du conteneur.
* `requirements.txt` : Liste des bibliothèques Python nécessaires (Streamlit, OpenAI, Python-dotenv, etc.).
* `recettes/` : Dossier contenant des exemples de fichiers JSON générés.

## Utilisation

1.  Lancez l'application.
2.  Copiez le texte de votre recette (titre, ingrédients, étapes) dans la zone de texte prévue à cet effet.
3.  Cliquez sur le bouton "Générer le JSON".
4.  L'application affichera le code JSON généré ainsi qu'un aperçu des données extraites.
5.  Vous pouvez copier ce code pour l'importer dans Mealie ou tout autre système compatible.

## Auteur

Développé par Alexandre Eberhardt.

## Licence

Ce projet est distribué sous la licence MIT. Vous êtes libre d'utiliser, de modifier et de distribuer ce logiciel, à condition de conserver la mention des droits d'auteur. Voir le fichier `LICENSE` pour plus de détails.