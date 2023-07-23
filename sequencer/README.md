# Sequenceur

## Installation:
```bash
python3 -m pip install -r requirements.txt
```

## Démarrage
```bash
python3 main.py
```

## Utilisation
La position des marqueurs est reçue en osc (depuis le tracker). Il est aussi possible de les déplacer à souris par drag-n-drop.
Pour sauvegarder une scène (position des marqueurs et vitesse de lecture), cliquer sur 'save' pour générer un fichier 'save.json'.
Pour le recharger, passer le nom du fichier en argument au lancement du script:
```bash
python3 main.py save.json
```
