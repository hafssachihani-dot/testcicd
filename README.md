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

## Correlation ID et LangSmith

Chaque execution recoit un `correlation_id` unique. Il est conserve dans l'etat
LangGraph, transmis a la DLQ et ajoute aux metadonnees LangSmith. Tous les
noeuds d'une meme execution utilisent donc le meme identifiant.

Pour envoyer les traces locales vers LangSmith :

```powershell
$env:LANGSMITH_TRACING="true"
$env:LANGSMITH_API_KEY="NOUVELLE_CLE_LANGSMITH"
$env:LANGSMITH_PROJECT="agent-wikipedia"
```

Pour GitHub Actions, creer le secret `LANGSMITH_API_KEY` dans :

`Settings > Secrets and variables > Actions > New repository secret`

La cle LangSmith ne doit jamais etre ecrite dans le code ou dans Git.

## Les 5 tests

1. Wikipedia repond : l'agent retourne la reponse.
2. Timeout Wikipedia : la question est envoyee vers la DLQ.
3. Erreurs reseau parametrees : l'agent affiche un message de secours.
4. Aucun resultat : la question est envoyee vers la DLQ.
5. Bug Python inattendu : pytest verifie que l'erreur n'est pas cachee.
