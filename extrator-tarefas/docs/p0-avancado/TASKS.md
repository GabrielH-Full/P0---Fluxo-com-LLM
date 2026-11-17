# TASK — Auditoria do Projeto (baseada no `extrator-tarefas/docs/p0-avancado/PRD.md`)

> **Regra de ouro:** modo **somente leitura**. Nenhum arquivo do projeto pode ser criado, editado, movido ou apagado. Sem commits, sem instalação de dependências no projeto, sem chamadas reais ao LLM. Segredos encontrados devem ser **mascarados** no relatório.

---

## Fase 0 — Preparação

- [ ] **T0.1** Registrar o estado inicial do repositório
  - Comando: `git status --porcelain` e `git rev-parse HEAD`
  - Guardar a saída para comparar no final (T8.1).
- [ ] **T0.2** Listar a estrutura do projeto
  - Comando: `tree -a -I '.git|venv|.venv|__pycache__|node_modules'` (ou `find . -type f -not -path './.git/*'`)
- [ ] **T0.3** Identificar o ponto de entrada (`main.py`, `app.py`, `__main__.py`, script no `pyproject.toml`).
- [ ] **T0.4** Identificar o módulo que faz a chamada ao LLM (busca: `openai`, `anthropic`, `google.generativeai`, `requests.post`, `httpx`).

---

## Fase 1 — R1: Configuração externa ao núcleo

- [ ] **T1.1** Localizar arquivos de configuração: `.env`, `.env.example`, `config.*`, `settings.*`.
- [ ] **T1.2** Verificar se os parâmetros do LLM vêm de config/variáveis de ambiente:
  - [ ] modelo
  - [ ] `max_tokens` / limite de tokens
  - [ ] `temperature` / `top_p`
  - [ ] prompt de sistema / comportamento básico
- [ ] **T1.3** Buscar valores *hardcoded* no núcleo
  - Comando: `grep -rnE "max_tokens|temperature|top_p|model\s*=" --include=*.py .`
- [ ] **T1.4** Verificar se existe `.env.example` **sem valores reais**.
- [ ] **T1.5** Verificar se há valores padrão seguros quando a config está ausente.
- [ ] **T1.6** Registrar status (✅ / ⚠️ / ❌) + evidência `arquivo:linha` + o que falta.

---

## Fase 2 — R2: Logs seguros

- [ ] **T2.1** Verificar uso de `logging`
  - Comando: `grep -rnE "import logging|getLogger|print\(" --include=*.py .`
- [ ] **T2.2** Conferir os pontos registrados:
  - [ ] início/fim da execução
  - [ ] configuração carregada (sem segredos)
  - [ ] envio da solicitação
  - [ ] sucesso/erro da resposta
  - [ ] duração
- [ ] **T2.3** Procurar logs que vazem dados sensíveis (chave, header `Authorization`, prompt completo, resposta integral, dados pessoais).
- [ ] **T2.4** Verificar se há arquivos `*.log` versionados
  - Comando: `git ls-files | grep -E "\.log$"`
- [ ] **T2.5** Verificar se o `.gitignore` exclui logs, `.env` e venv.
- [ ] **T2.6** Registrar status + evidência + o que falta.

---

## Fase 3 — R3: Versão do Python e bibliotecas

- [ ] **T3.1** Procurar a versão do Python em: README, `pyproject.toml`, `.python-version`, `runtime.txt`.
- [ ] **T3.2** Localizar o arquivo de dependências (`requirements.txt`, `pyproject.toml`, `Pipfile`).
- [ ] **T3.3** Verificar se as versões estão fixadas ou com faixas.
- [ ] **T3.4** Comparar os imports do código com as dependências declaradas
  - Comando: `grep -rhoE "^(import|from) [a-zA-Z_]+" --include=*.py . | sort -u`
  - Apontar bibliotecas **faltando** ou **sobrando**.
- [ ] **T3.5** Verificar se o README lista as principais bibliotecas.
- [ ] **T3.6** Registrar status + evidência + o que falta.

---

## Fase 4 — R4: Teste local sem chamada ao LLM

- [ ] **T4.1** Localizar testes (`tests/`, `test_*.py`, `*_test.py`).
- [ ] **T4.2** Verificar se pelo menos um teste cobre:
  - [ ] validação da entrada
  - [ ] preparação da solicitação
  - [ ] carregamento da configuração
  - [ ] tratamento de resposta simulada
  - [ ] tratamento de erro simulado
- [ ] **T4.3** Confirmar uso de simulação
  - Comando: `grep -rnE "mock|patch|monkeypatch|MagicMock|fake|stub" tests/`
- [ ] **T4.4** Verificar se os testes dependem de chave de API ou de rede (não deveriam).
- [ ] **T4.5** *(Opcional, só se seguro)* Rodar os testes **fora do projeto** (cópia em diretório temporário + venv temporário), sem chave de API definida:
  ```bash
  cp -r <projeto> /tmp/auditoria && cd /tmp/auditoria
  python -m venv /tmp/venv-audit && source /tmp/venv-audit/bin/activate
  pip install -r requirements.txt && env -u OPENAI_API_KEY pytest -q
  ```
- [ ] **T4.6** Verificar se o README explica como rodar os testes.
- [ ] **T4.7** Registrar status + evidência + o que falta.

---

## Fase 5 — R5: Validação em ambiente limpo

- [ ] **T5.1** Conferir se o README tem o passo a passo completo:
  - [ ] clonar o repositório
  - [ ] criar o ambiente virtual
  - [ ] instalar as dependências
  - [ ] configurar as variáveis (`.env` a partir do `.env.example`)
  - [ ] executar a aplicação
  - [ ] rodar os testes
- [ ] **T5.2** Procurar o registro da validação (seção no README, `VALIDACAO.md`, `CHANGELOG.md`).
- [ ] **T5.3** Verificar se o registro informa **como** foi validado (novo venv, outro PC ou outra pessoa).
- [ ] **T5.4** Verificar se os problemas encontrados foram registrados com **o que aconteceu + a correção**.
- [ ] **T5.5** Buscar caminhos absolutos da máquina do desenvolvedor
  - Comando: `grep -rnE "C:\\\\|/home/|/Users/" --include=*.py --include=*.md .`
- [ ] **T5.6** Registrar status + evidência + o que falta.

---

## Fase 6 — Competências C01 a C04

- [ ] **T6.1 — C01 (código para terceiros):** avaliar estrutura de pastas, separação núcleo/config/cliente LLM, nomes legíveis, tamanho das funções, docstrings e clareza do README.
- [ ] **T6.2 — C02 (histórico do Git):** somente leitura
  - `git log --oneline | wc -l` → quantidade de commits
  - `git log --format="%ad %s" --date=short` → distribuição no tempo e qualidade das mensagens
  - `git log --stat` → evolução incremental (não um commit único)
- [ ] **T6.3 — C03 (falhas sem expor dados):** verificar `try/except` na chamada ao LLM e o tratamento de:
  - [ ] timeout
  - [ ] erro de autenticação
  - [ ] limite de requisições
  - [ ] resposta vazia/inválida
  - [ ] mensagens amigáveis, sem stack trace ou chave para o usuário
- [ ] **T6.4 — C04 (outro ambiente):** consolidar R3 + R5 (dependências, `.env.example`, ausência de caminhos absolutos, README reprodutível).
- [ ] **T6.5** Registrar status + evidência + o que falta para cada competência.

---

## Fase 7 — Varredura de segurança

- [ ] **T7.1** Procurar segredos no código atual
  - Comando: `grep -rnEi "api_key|apikey|token|secret|password|sk-[a-z0-9]|Bearer " --exclude-dir=.git .`
- [ ] **T7.2** Procurar segredos no histórico do Git
  - Comando: `git log -p | grep -nEi "api_key|sk-[a-z0-9]|Bearer |password"`
- [ ] **T7.3** Verificar se o `.env` real está versionado: `git ls-files | grep -E "^\.env$"`
- [ ] **T7.4** Procurar dados pessoais (e-mails, CPFs, telefones) em código, exemplos e logs.
- [ ] **T7.5** Listar cada achado como `arquivo:linha — descrição` com o **valor mascarado**.

---

## Fase 8 — Fechamento

- [ ] **T8.1** Confirmar que nada foi alterado
  - `git status --porcelain` e `git rev-parse HEAD` devem ser **idênticos** ao T0.1.
- [ ] **T8.2** Montar o relatório no formato da seção 6 do `prd.md`:
  - [ ] resumo (X/5 requisitos, Y/4 competências, situação geral)
  - [ ] tabela de requisitos R1–R5
  - [ ] tabela de competências C01–C04
  - [ ] riscos de segurança
  - [ ] checklist de pendências
  - [ ] recomendações (sem aplicar)
- [ ] **T8.3** Entregar o relatório como resposta ou em arquivo **fora** do projeto.

---

## Critério de pronto

- [ ] Todos os itens R1–R5 e C01–C04 com status e evidência.
- [ ] Todas as pendências listadas no checklist.
- [ ] Estado do Git idêntico ao inicial (nenhuma modificação).