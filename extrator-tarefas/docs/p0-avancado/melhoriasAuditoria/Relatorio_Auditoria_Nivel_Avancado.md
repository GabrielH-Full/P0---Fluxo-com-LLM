# Relatório de Auditoria — Nível Avançado

**Projeto:** extrator-tarefas
**Data:** 16/11/2026
**Modificações realizadas:** nenhuma

## Resumo
- Atendidos: 0 de 5 requisitos (3 parciais, 2 ausentes) | 2 de 4 competências (2 parciais)
- Situação geral: **Pendente**
- Problema mais grave: em ambiente limpo a aplicação provavelmente não inicia. `src/llm.py:3` importa `google.api_core`, que **não** vem pelo `requirements.txt` (nem como dependência do `google-genai`). No `.venv` local ele existe apenas como sobra de pacotes antigos (`google-generativeai`, `google-api-python-client`, `proto-plus`).

## Requisitos
| ID | Requisito | Status | Evidência (arquivo:linha) | O que falta |
|---|---|---|---|---|
| R1 | Configuração externa ao núcleo | ⚠️ | Modelo vem do ambiente com valor padrão (`src/config.py:16`); `.env.example` sem valores reais (`.env.example:1-2`) | `temperature=0` e `max_output_tokens=1024` fixos no código (`src/llm.py:23-24`); prompt de sistema fixo (`src/prompt.py:3`); sem `top_p`; `.env` local contém `MODEL_NAME` e `LLM_BASE_URL`, que o código não usa. |
| R2 | Logs sem dados sensíveis | ❌ | Nenhum `import logging` em `src/` ou `tests/`; saída apenas por `print`/stderr (`src/erros.py:57`) | Nenhum registro de início/fim, configuração carregada, envio, sucesso/erro ou duração. `.gitignore` não exclui `*.log` (nenhum `.log` versionado). |
| R3 | Versão do Python e bibliotecas | ⚠️ | `GuiaDeExecucao.md:37` (“Python 3.10+”); `requirements.txt:1-2` com faixas `>=` | `google-api-core` não declarado (usado em `src/llm.py:3`); sem limite superior de versões; sem `.python-version`/`pyproject.toml`; `.venv` usa Python 3.9.6, contrariando o 3.10+ documentado; o guia não lista as bibliotecas. |
| R4 | Teste local sem chamada ao LLM | ⚠️ | `tests/rodar_casos_local.py:24-38` substitui o módulo `llm` por uma versão falsa e dispensa a chave. Executado numa cópia fora do projeto, sem `GEMINI_API_KEY`: **OK 18 · erro tratado 7 · quebra 0 · exit=0** | É um script, não um teste com verificação: só falha se houver quebra, não compara com o resultado esperado. Cobre validação da entrada e montagem do prompt; não cobre `obter_config`, nem resposta/erro simulados dentro de `chamar_llm`. Sem pytest/unittest. |
| R5 | Validação em ambiente limpo | ❌ | Não existem `README.md`, `VALIDACAO.md` nem `CHANGELOG.md` | Guia sem o passo de clonar; nenhum registro de validação (como foi feita, problemas e correções). A dependência faltante indica que a validação não ocorreu. |

## Competências
| ID | Competência | Status | Evidência | O que falta |
|---|---|---|---|---|
| C01 | Código organizado para terceiros | ✅ | `src/` separado em config / entrada / prompt / llm / erros / main; funções pequenas; docstrings em `src/erros.py` | Docstrings em `config.py`, `llm.py`, `prompt.py`; documentação principal se chama `GuiaDeExecucao.md` em vez de `README.md`. |
| C02 | Histórico do Git como evidência | ✅ | 18 commits entre 04/11 e 13/11/2026, evolução incremental, PRs #1 e #2 | Algumas mensagens vagas (“arquivo de intrucao atualizado”) e uma excessivamente longa (`5864eca`). |
| C03 | Falhas sem expor dados sensíveis | ⚠️ | `try/except` em `src/llm.py:17-35`; mensagens amigáveis em `src/main.py:87-95`; stack trace só com `EXTRATOR_DEBUG=1` (`src/erros.py:62`) | O `google-genai` lança `google.genai.errors.APIError`/`ClientError`/`ServerError`, não as exceções do `api_core`: os `except` de autenticação, limite e conexão provavelmente nunca disparam. O erro cai em “erro inesperado” e exibe `Detalhe técnico: {erro}` (`src/erros.py:50`), com a mensagem crua da API. Sem tratamento de timeout. Resposta vazia (`resposta.text` = `None`) imprimiria `None`. |
| C04 | Execução em outro ambiente | ⚠️ | `.env.example`; `.gitignore` exclui `.env` e venv; nenhum caminho absoluto em `.py`/`.md` | Dependência faltando (R3), sem registro de ambiente limpo (R5), versão do Python inconsistente. |

## Riscos de segurança encontrados
- `extrator-tarefas/.env:3` — `GEMINI_API_KEY=AQ.****`: chave real presente localmente, **não versionada** (excluída pelo `.gitignore` e ausente do histórico). Manter assim.
- Histórico do Git — um Dockerfile antigo usava `ARG/ENV GEMINI_API_KEY` e uma interface web antiga recebia a chave por formulário. Nenhum valor real de chave (`AIza`, `sk-`, `Bearer`) encontrado no histórico.
- `src/erros.py:50` — risco indireto: a mensagem crua de erro da API pode ser exibida ao usuário (ver C03).
- Nenhum e-mail, CPF ou telefone encontrado no código ou nos casos de teste.

## Itens faltando (checklist de pendências)
- [ ] Declarar `google-api-core` **ou** (preferível) trocar os `except` para `google.genai.errors`
- [ ] Levar `temperature`, `max_output_tokens`, `top_p` e prompt de sistema para configuração externa, com valores padrão
- [ ] Atualizar o `.env.example` com as novas variáveis e remover as não usadas do `.env`
- [ ] Adicionar `logging` (início/fim, modelo carregado sem a chave, envio, sucesso/erro, duração)
- [ ] Incluir `*.log` no `.gitignore`
- [ ] Fixar a versão do Python (`.python-version`) e alinhar o `.venv` ao 3.10+
- [ ] Criar testes `pytest` com asserções e mocks: configuração, `chamar_llm` com resposta simulada e com erro simulado
- [ ] Declarar `pytest` como dependência de desenvolvimento e documentar como rodar
- [ ] Criar `README.md` com passo a passo completo, incluindo clonar o repositório
- [ ] Validar em venv novo e registrar como foi feito, problemas e correções (`VALIDACAO.md`)
- [ ] Tratar timeout e resposta vazia; não exibir o detalhe cru da API ao usuário

## Recomendações (sem aplicar)
1. Corrigir primeiro `src/llm.py`: capturar `google.genai.errors.ClientError` (códigos 401/403 e 429), `ServerError` e `httpx.TimeoutException`. Resolve R3 e C03 de uma vez e dispensa o `api_core`.
2. Centralizar todos os parâmetros do LLM em `config.py`, lidos do ambiente com padrões seguros, e passar o dicionário de configuração para `chamar_llm`.
3. Criar `tests/test_*.py` usando `unittest.mock.patch("llm.genai.Client")` para simular sucesso, resposta vazia e cada tipo de erro.
4. Validar com `python3.10 -m venv /tmp/x`, instalando apenas pelo `requirements.txt`, e documentar o resultado em `VALIDACAO.md`.

## Confirmação final
- `git rev-parse HEAD`: `65f1427e14f226424920c219b5918c706fe8294e` — igual ao início.
- `git status --porcelain`: `?? extrator-tarefas/docs/p0-avancado/` — igual ao início (pasta já estava não versionada).
- Os testes foram executados em uma cópia fora do projeto, com o Python do `.venv`, sem instalar dependências e sem chamadas ao LLM.

**Legenda de status:** ✅ Atendido · ⚠️ Parcial · ❌ Ausente
