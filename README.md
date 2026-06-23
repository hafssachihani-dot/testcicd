# Documentation - Tests automatises et CI/CD agentique

Petit livrable inspire de l'exemple du PDF, mais simplifie pour rester facile a comprendre.
Le projet contient un agent Python, 5 tests pytest, un export JSON du workflow et une pipeline GitHub Actions.

## Fichiers

- `agent.py` : logique simple de l'agent.
- `test_agent.py` : suite de 5 tests pytest.
- `workflow_final.json` : export JSON simplifie du workflow.
- `requirements.txt` : dependance de test.
- `.github/workflows/ci-agent.yml` : pipeline CI qui lance les tests a chaque push ou pull request.

## Lancer les tests

```bash
python -m pip install pytest
pytest -q
```

## Mocks utilises

Les tests utilisent `unittest.mock.Mock` pour eviter les dependances lourdes.

- Le LLM est mocke avec `llm.invoke.return_value`.
- LangGraph est mocke avec `graph_factory` et `graph`.
- Le test `test_build_workflow_uses_mocked_langgraph_builder` verifie que le workflow appelle bien :
  - `add_node`
  - `set_entry_point`
  - `set_finish_point`
  - `compile`

Cela permet de tester le comportement attendu sans lancer un vrai serveur LangGraph.

## Cas testes

1. Reponse conforme acceptee.
2. Reponse avec faible confiance bloquee.
3. Reponse avec phrase interdite bloquee.
4. Reponse texte simple acceptee.
5. Construction du workflow avec LangGraph mocke.
