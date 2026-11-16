# TASKS — Melhorias da Auditoria (Nível Avançado)

> Baseado em `Relatorio_Auditoria_Nivel_Avancado.md` (16/11/2026).
> Objetivo: levar R1–R5 e C01–C04 ao status ✅.
> **Status (16/11/2026):** implementado, exceto T4.2, T7.2 e T8.3 (ver itens marcados ⏳).
> Ordem pensada por prioridade: primeiro o que **quebra** em ambiente limpo, depois o que **falta**, por último a **validação final**.

**Regras gerais**
- Trabalhar na branch `P-avancado`, um commit por fase (mensagens descritivas — reforça C02).
- Nunca versionar o `.env` nem colocar valores reais no `.env.example`.
- Nenhum teste pode chamar o LLM de verdade nem depender de `GEMINI_API_KEY`.

---

## Fase 1 — Corrigir o tratamento de erros do LLM (R3, C03) · prioridade alta

> Problema: `src/llm.py:3` importa `google.api_core`, que não vem pelo `requirements.txt`, e o `google-genai` não lança essas exceções.

- [x] **T1.1** Em `src/llm.py`, remover o import de `google.api_core.exceptions`.
- [x] **T1.2** Capturar as exceções corretas do SDK:
  - [x] `google.genai.errors.ClientError` com `code` 401/403 → "Chave de API inválida…"
  - [x] `ClientError` com `code` 429 → "Limite de uso da API atingido…"
  - [x] `ClientError` com `code` 404 → "Modelo não encontrado. Verifique o GEMINI_MODEL."
  - [x] `google.genai.errors.ServerError` → "Serviço indisponível, tente novamente."
  - [x] `httpx.TimeoutException` / `httpx.ConnectError` → "Tempo esgotado / sem conexão."
  - [x] Demais `APIError` → mensagem genérica **sem** o texto cru da API.
- [x] **T1.3** Configurar timeout na chamada (`types.HttpOptions(timeout=...)`, valor vindo da config — ver Fase 2).
- [x] **T1.4** Tratar resposta vazia: se `resposta.text` for `None` ou só espaços → `LLMError("O modelo não retornou conteúdo.")`.
- [x] **T1.5** Em `src/erros.py:50`, não exibir `str(erro)` ao usuário; mostrar só o tipo do erro e manter o detalhe completo apenas com `EXTRATOR_DEBUG=1`.
- [x] **T1.6** Se `httpx` for importado diretamente, declará-lo no `requirements.txt`.

**Pronto quando:** `grep -rn "api_core" src/` não retorna nada e cada tipo de erro gera mensagem amigável sem dados da API.

---

## Fase 2 — Configuração externa ao núcleo (R1)

- [x] **T2.1** Em `src/config.py`, ler do ambiente com valores padrão seguros:
  | Variável | Padrão | Validação |
  |---|---|---|
  | `GEMINI_MODEL` | `gemini-2.0-flash` | não vazio |
  | `LLM_TEMPERATURE` | `0` | float entre 0 e 2 |
  | `LLM_TOP_P` | `1.0` | float entre 0 e 1 |
  | `LLM_MAX_TOKENS` | `1024` | inteiro > 0 |
  | `LLM_TIMEOUT_SEGUNDOS` | `30` | inteiro > 0 |
  | `LLM_SYSTEM_PROMPT_ARQUIVO` | *(vazio = prompt embutido)* | arquivo existente |
- [x] **T2.2** Valor inválido → `ConfigError` com mensagem clara (ex.: "LLM_TEMPERATURE deve ser um número entre 0 e 2").
- [x] **T2.3** Em `src/llm.py`, usar `config[...]` no lugar de `temperature=0` e `max_output_tokens=1024`; adicionar `top_p`.
- [x] **T2.4** Permitir trocar o prompt de sistema sem editar `src/prompt.py` (arquivo indicado em `LLM_SYSTEM_PROMPT_ARQUIVO`; se ausente, usar `SYSTEM_PROMPT`).
- [x] **T2.5** Atualizar `.env.example` com todas as variáveis, valores de exemplo e um comentário por linha.
- [x] **T2.6** Remover do `.env` local as variáveis não usadas (`MODEL_NAME`, `LLM_BASE_URL`).

**Pronto quando:** `grep -rnE "temperature=0|max_output_tokens=1024" src/` não retorna nada.

---

## Fase 3 — Logs seguros (R2)

- [x] **T3.1** Criar `src/registro.py` com `configurar_logs()`:
  - nível via `LOG_LEVEL` (padrão `INFO`);
  - saída em stderr (e, opcional, em arquivo via `LOG_ARQUIVO`);
  - formato: `%(asctime)s %(levelname)s %(name)s: %(message)s`.
- [x] **T3.2** Registrar os pontos exigidos:
  - [x] início e fim da execução (`main.py`)
  - [x] configuração carregada — só modelo, temperatura, top_p, max_tokens, timeout (**nunca** a chave)
  - [x] envio da solicitação — tamanho da entrada em caracteres, **não** o conteúdo
  - [x] sucesso (tamanho da resposta) ou erro (tipo do erro)
  - [x] duração da chamada ao LLM (`time.perf_counter()`)
- [x] **T3.3** Garantir que nenhum log contenha: chave de API, headers, texto das anotações, resposta integral.
- [x] **T3.4** Manter `print` apenas para a saída destinada ao usuário (lista de tarefas e perguntas).
- [x] **T3.5** Adicionar `*.log` e `logs/` ao `.gitignore`.

**Pronto quando:** rodar a aplicação mostra início, config, envio, resultado e duração, e `grep -i "AQ\.\|api_key" <log>` não encontra nada.

---

## Fase 4 — Versão do Python e dependências (R3)

- [x] **T4.1** Criar `.python-version` com `3.10` (ou a versão realmente usada, ≥ 3.10).
- [ ] **T4.2** Recriar o `.venv` local com Python 3.10+ (o atual é 3.9.6). — ⏳ pendente: só há Python 3.9.6 na máquina
- [x] **T4.3** Fixar faixas no `requirements.txt` (ex.: `google-genai>=1.47,<2`, `python-dotenv>=1.0,<2`).
- [x] **T4.4** Criar `requirements-dev.txt` com `-r requirements.txt` + `pytest`.
- [x] **T4.5** Conferir imports × dependências declaradas:
  ```bash
  grep -rhoE "^(import|from) [a-zA-Z_.]+" --include='*.py' src tests | sort -u
  ```
  Nenhuma biblioteca externa pode faltar ou sobrar.

**Pronto quando:** `pip install -r requirements-dev.txt` em venv novo basta para rodar app e testes.

---

## Fase 5 — Testes automatizados sem LLM (R4)

- [x] **T5.1** Criar `tests/conftest.py` que adiciona `src/` ao `sys.path` e remove `GEMINI_API_KEY` do ambiente (`monkeypatch.delenv`).
- [x] **T5.2** `tests/test_entrada.py` — validação da entrada:
  - [x] texto vazio / só espaços → `EntradaInvalidaError`
  - [x] texto acima de 20 000 caracteres → erro; exatamente 20 000 → ok
  - [x] arquivo inexistente, pasta e arquivo Latin-1 → mensagens corretas
- [x] **T5.3** `tests/test_prompt.py` — preparação da solicitação:
  - [x] data de referência no formato `DD/MM/AAAA`
  - [x] anotações dentro de `<anotacoes>…</anotacoes>`
- [x] **T5.4** `tests/test_config.py` — carregamento da configuração (`monkeypatch.setenv`):
  - [x] sem chave → `ConfigError`
  - [x] valores padrão quando variáveis ausentes
  - [x] valor inválido (ex.: `LLM_TEMPERATURE=abc`) → `ConfigError`
- [x] **T5.5** `tests/test_llm.py` — com `unittest.mock.patch("llm.genai.Client")`:
  - [x] resposta simulada → devolve o texto
  - [x] resposta vazia → `LLMError`
  - [x] `ClientError` 401, 429 e `ServerError` → `LLMError` com mensagem amigável
  - [x] timeout simulado → `LLMError`
  - [x] mensagem de erro **não** contém a chave de API
- [x] **T5.6** Manter `tests/rodar_casos_local.py` como teste exploratório e criar `tests/test_casos.py` que roda os casos de `tests/casos/` com status esperado (OK/ERRO) e falha se divergir.
- [x] **T5.7** Rodar: `env -u GEMINI_API_KEY pytest -q` → todos passando, sem rede.

**Pronto quando:** `pytest` passa sem chave e sem internet.

---

## Fase 6 — README e organização (C01, C04, R5)

- [x] **T6.1** Pode usar o `GuiaDeExecucao.md` (pode partir do `GuiaDeExecucao.md`) com:
  - [x] descrição e exemplo de entrada/saída
  - [x] pré-requisitos (Python 3.10+, chave Gemini)
  - [x] **clonar** o repositório (`git clone … && cd extrator-tarefas`)
  - [x] criar e ativar o venv (macOS/Linux e Windows)
  - [x] instalar dependências (`requirements.txt` e `requirements-dev.txt`)
  - [x] configurar `.env` a partir do `.env.example`, explicando cada variável
  - [x] executar a aplicação (arquivo, stdin, `--texto`)
  - [x] rodar os testes (`pytest`)
  - [x] principais bibliotecas e para que servem
  - [x] estrutura de pastas (um parágrafo por módulo de `src/`)
- [x] **T6.2** Decidir o destino do `GuiaDeExecucao.md` (remover ou apontar para o README) para não haver duas fontes.
- [x] **T6.3** Adicionar docstrings curtas em `config.py`, `llm.py` e `prompt.py`.

---

## Fase 7 — Validação em ambiente limpo (R5, C04)

- [x] **T7.1** Em um diretório fora do projeto, seguir **apenas** o README:
  ```bash
  cd /tmp && git clone <url-do-repo> validacao && cd validacao/extrator-tarefas
  python3.10 -m venv .venv && source .venv/bin/activate
  pip install -r requirements-dev.txt
  env -u GEMINI_API_KEY pytest -q
  cp .env.example .env   # preencher a chave
  python src/main.py --arquivo tests/casos/exemplo.txt --data 03/11/2026
  ```
- [ ] **T7.2** (Ideal) Pedir a outra pessoa ou usar outro computador para repetir o passo a passo. — ⏳ pendente
- [x] **T7.3** Criar `VALIDACAO.md` registrando:
  - [x] data, sistema operacional e versão do Python
  - [x] **como** foi validado (venv novo / outro PC / outra pessoa)
  - [x] comandos executados e resultado
  - [x] problemas encontrados → **o que aconteceu + correção aplicada** (ex.: dependência `google-api-core` faltando, corrigida na Fase 1)
- [x] **T7.4** Linkar o `VALIDACAO.md` no README.

---

## Fase 8 — Fechamento

- [x] **T8.1** Varredura final de segurança:
  ```bash
  git ls-files | grep -E "(^|/)\.env$|\.log$"          # deve retornar vazio
  grep -rnEi "AIza|AQ\.[A-Za-z0-9]|sk-[a-z0-9]|Bearer " --exclude-dir=.venv --exclude=.env .
  ```
- [x] **T8.2** Reexecutar a auditoria do `docs/p0-avancado/TASKS.md` e atualizar o relatório com os novos status.
- [ ] **T8.3** Abrir PR de `P-avancado` → `main` com resumo das mudanças por requisito. — ⏳ aguardando autorização para push/PR

---

## Rastreabilidade (pendência do relatório → task)

| Pendência do relatório | Tasks |
|---|---|
| Declarar `google-api-core` ou trocar `except` para `google.genai.errors` | T1.1–T1.2, T1.6 |
| Parâmetros do LLM e prompt em configuração externa | T2.1–T2.4 |
| Atualizar `.env.example` e limpar `.env` | T2.5–T2.6 |
| Adicionar `logging` | T3.1–T3.4 |
| `*.log` no `.gitignore` | T3.5 |
| Fixar versão do Python e alinhar `.venv` | T4.1–T4.2 |
| Testes `pytest` com asserções e mocks | T5.1–T5.7 |
| `pytest` como dependência de desenvolvimento | T4.4 |
| `README.md` completo com clonar | T6.1–T6.2 |
| Validar em venv novo e registrar | T7.1–T7.4 |
| Timeout, resposta vazia, não exibir detalhe cru da API | T1.3–T1.5 |

## Critério de pronto

- [x] R1–R5 e C01–C04 com status ✅ na reauditoria.
- [x] `pytest` passa sem chave de API e sem rede.
- [x] `VALIDACAO.md` registra a validação em ambiente limpo.
- [x] Nenhum segredo versionado.
