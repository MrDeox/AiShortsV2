# Testes Manuais

Esta pasta contém scripts de teste manual que não seguem o padrão pytest oficial.

## Como Executar

```bash
# Testar pipeline real
python tests/manual/test_real_pipeline.py

# Teste simples de componentes
python tests/manual/simple_test.py

# Testar refatoração
python tests/manual/test_refactoring.py

# Testar integrações LLM
python tests/manual/test_llm_integrations.py

# Testar dashboard
python tests/manual/test_dashboard.py
```

⚠️ Estes scripts são para desenvolvimento e debug manual. Para testes automatizados, utilize `pytest tests/`.