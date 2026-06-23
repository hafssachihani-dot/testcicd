# Tests automatises et CI/CD avec LangGraph

## Cas d'utilisation

L'agent recoit une question et cherche la reponse dans Wikipedia.

- Si Wikipedia fonctionne, LangGraph route le flux vers `answer`.
- Si Wikipedia retourne une erreur, LangGraph route le flux vers `dlq`.
- La DLQ conserve la question en erreur sans faire planter l'agent.

## Fichiers

- `agent.py` : workflow LangGraph et appels HTTP.
- `test_agent.py` : exactement 5 tests pytest.
- `workflow_final.json` : export simple du workflow.
- `requirements.txt` : bibliotheques Python.
- `.github/workflows/ci-agent.yml` : tests automatiques sur GitHub.

## Lancer les tests

```powershell
py -m pip install -r requirements.txt
py -m pytest test_agent.py -v
```

Si la commande `py` n'existe pas, utiliser `python` a sa place.

## Utilisation de pytest

Le fichier `test_agent.py` importe vraiment `pytest` et utilise :

- `@pytest.fixture` pour creer le mock de la DLQ.
- `pytest.raises` pour verifier qu'un bug inattendu reste visible.
- Les instructions `assert` pour verifier les resultats.

## Mocks utilises

`unittest.mock.Mock` remplace les services externes :

- `mock_wikipedia` simule une reponse ou une panne de Wikipedia.
- `mock_dlq` simule le serveur de quarantaine.

Les tests n'appellent donc ni Wikipedia, ni une vraie DLQ, ni une API payante.

## Les 5 tests

1. Wikipedia repond : l'agent retourne la reponse.
2. Timeout Wikipedia : la question est envoyee vers la DLQ.
3. Erreurs reseau parametrees : l'agent affiche un message de secours.
4. Aucun resultat : la question est envoyee vers la DLQ.
5. Bug Python inattendu : pytest verifie que l'erreur n'est pas cachee.
