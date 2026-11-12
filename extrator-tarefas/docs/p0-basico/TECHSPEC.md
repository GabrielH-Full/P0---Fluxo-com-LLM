# TechSpec: Transformador de Anotações de Reunião em Lista de Tarefas

**Bloco:** P0 - Fluxo com LLM
**Etapa:** 1 de 3 (Nível básico)
**Documento de origem:** [PRD.md](./PRD.md)
**Data:** 11/11/2026

---

## 1. Visão técnica

Script Python de linha de comando com um fluxo linear:

```
terminal (texto) → validar entrada → montar prompt → chamar LLM → exibir resposta
```

Sem banco de dados, interface gráfica, web, RAG ou agentes. O código é dividido em funções pequenas e em módulos separados, para que os níveis intermediário e avançado possam evoluir cada parte sem reescrever tudo.

## 2. Decisões técnicas

| Decisão | Escolha | Justificativa |
|---|---|---|
| Linguagem | Python 3.10+ | Exigência do projeto (RF01, C01). |
| LLM / provedor | Gemini (Google) via SDK oficial `google-genai` | SDK simples, boa qualidade em extração de texto em português. |
| Modelo | Configurável por `GEMINI_MODEL` no `.env` | Evita fixar o modelo no código e facilita trocar por custo ou qualidade. |
| Credenciais | `GEMINI_API_KEY` em variável de ambiente, carregada com `python-dotenv` | RNF01, RNF02 e C03. |
| Entrada | `argparse` + `stdin` / arquivo `.txt` | Cobre colar texto no terminal e ler um arquivo, sem dependências extras. |
| Saída | Texto simples no terminal | Atende o nível básico; JSON fica para o intermediário. |
| Referência de data | Data da reunião via `--data` (padrão: hoje) | Permite resolver "sexta" e "amanhã" já no básico, de forma simples. |
| Dependências | `requirements.txt` com versões mínimas | RNF03 e C04. |

> Se for usar outro provedor (OpenAI, Gemini etc.), só `llm.py` e a variável de chave mudam. O restante da arquitetura permanece.

## 3. Estrutura de arquivos

```
extrator-tarefas/
├── docs/
│   ├── PRD.md
│   ├── TECHSPEC.md
│   └── TASKS.md
├── src/
│   ├── main.py        # ponto de entrada (CLI) e orquestração
│   ├── entrada.py     # leitura e validação da entrada
│   ├── prompt.py      # montagem do prompt (system + user)
│   ├── llm.py         # configuração do cliente e chamada ao modelo
│   └── config.py      # carrega variáveis de ambiente
├── tests/             # reservado para os níveis seguintes
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 4. Componentes

### 4.1 `config.py`
- Carrega o `.env` com `load_dotenv()`.
- Expõe `obter_config()` que retorna chave de API e modelo.
- Se `ANTHROPIC_API_KEY` não existir, levanta `ConfigError` com mensagem orientando criar o `.env`.

### 4.2 `entrada.py`
- `ler_entrada(arquivo: str | None) -> str`:
  - Com `--arquivo`: lê o `.txt` (UTF-8).
  - Sem argumento: lê do `stdin` até EOF (Ctrl+D no Linux/macOS, Ctrl+Z + Enter no Windows). Se o terminal for interativo, exibe uma instrução curta.
- `validar_entrada(texto: str) -> str`: remove espaços das pontas; se vazio, levanta `EntradaInvalidaError`.
- Limite de segurança de tamanho (ex.: 20.000 caracteres) com erro claro. Chunking fica para o intermediário.

### 4.3 `prompt.py`
- `montar_prompt(anotacoes: str, data_referencia: date) -> tuple[str, str]` retorna `(system, user)`.
- **System prompt** (instruções fixas):
  - Papel: assistente que transforma anotações de reunião em lista de tarefas.
  - Extrair apenas tarefas (responsável, ação, prazo). Decisões e conversa não são tarefas.
  - Converter datas relativas usando a data de referência informada.
  - Se responsável ou prazo não estiverem claros, escrever `não informado`. Nunca inventar.
  - Formato de saída fixo, uma tarefa por linha: `N. Responsável: X | Ação: Y | Prazo: DD/MM/AAAA`.
  - Se não houver tarefas, responder `Nenhuma tarefa identificada.`
  - Responder em português do Brasil, sem texto extra além da lista.
- **User prompt**: data de referência e as anotações, delimitadas por tags (`<anotacoes>...</anotacoes>`). Os delimitadores já preparam o terreno para a defesa contra prompt injection do nível avançado.

### 4.4 `llm.py`
- `chamar_llm(system: str, user: str, config) -> str`:
  - Cria `anthropic.Anthropic(api_key=...)`.
  - Chama `client.messages.create(model=..., max_tokens=1024, temperature=0, system=system, messages=[{"role": "user", "content": user}])`.
  - Extrai o texto da resposta (bloco de conteúdo do tipo texto).
  - Captura erros do SDK (`AuthenticationError`, `RateLimitError`, `APIConnectionError`, `APIStatusError`) e converte em `LLMError` com mensagem amigável.
- `temperature=0` para respostas mais estáveis em extração.

### 4.5 `main.py`
- Define a CLI com `argparse`:
  - `--arquivo, -a`: caminho de um `.txt` com as anotações.
  - `--data, -d`: data da reunião em `DD/MM/AAAA` (padrão: hoje).
- Orquestra: `obter_config` → `ler_entrada` → `validar_entrada` → `montar_prompt` → `chamar_llm` → `print`.
- Captura as exceções do projeto, imprime a mensagem em `stderr` e sai com código `1` (sem stack trace para o usuário).

## 5. Fluxo de dados

```
[usuário] ──texto──▶ entrada.py ──texto validado──▶ prompt.py ──(system, user)──▶ llm.py ──▶ API do LLM
                                                                                       │
[terminal] ◀──────────────── lista de tarefas (texto) ◀────────────────────────────────┘
```

## 6. Tratamento de erros

| Situação | Exceção | Mensagem ao usuário |
|---|---|---|
| Chave de API ausente | `ConfigError` | "Defina ANTHROPIC_API_KEY no arquivo .env (veja o .env.example)." |
| Entrada vazia | `EntradaInvalidaError` | "Nenhuma anotação informada." |
| Arquivo não encontrado | `EntradaInvalidaError` | "Arquivo não encontrado: <caminho>." |
| Entrada acima do limite | `EntradaInvalidaError` | "Texto muito longo (máx. N caracteres)." |
| Data inválida em `--data` | `argparse` / `EntradaInvalidaError` | "Use o formato DD/MM/AAAA." |
| Chave inválida, limite de uso, sem rede | `LLMError` | Mensagem específica por tipo de erro. |

## 7. Configuração e segurança

**`.env.example`** (versionado, sem segredos):
```dotenv
GEMINI_API_KEY=coloque_sua_chave_aqui
GEMINI_MODEL=gemini-2.0-flash
```

**`.gitignore`** (mínimo):
```
.env
.venv/
__pycache__/
*.pyc
```

**`requirements.txt`**:
```
google-genai>=1.0.0
python-dotenv>=1.0.0
```

> Confirme a versão instalada com `pip show google-genai` e ajuste o mínimo se necessário. Não imprima a chave de API em logs nem em mensagens de erro.

## 8. Ambiente e execução

```bash
cd extrator-tarefas
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # edite com a sua chave
python src/main.py --arquivo exemplo.txt --data 03/11/2026
# ou cole o texto e finalize com Ctrl+D
```

## 9. Plano de verificação (manual, nível básico)

| # | Cenário | Resultado esperado |
|---|---|---|
| V1 | Exemplo do PRD com `--data 03/11/2026` | 3 tarefas; João 07/11/2026, Ana "não informado", Carla 04/11/2026; "usar react" não aparece como tarefa |
| V2 | Entrada vazia | Erro claro, código de saída 1 |
| V3 | Sem `.env` / sem chave | Erro orientando criar o `.env` |
| V4 | Chave inválida | Erro de autenticação amigável, sem stack trace |
| V5 | Texto sem tarefas ("bom dia pessoal") | "Nenhuma tarefa identificada." |
| V6 | Arquivo inexistente em `--arquivo` | Erro claro |
| V7 | `git status` e histórico | `.env` ausente do repositório |

## 10. Preparação para os próximos níveis

| Ponto deixado pronto | Uso futuro |
|---|---|
| `prompt.py` isolado e com delimitadores | Versionar prompt (intermediário) e defender contra injection (avançado) |
| `llm.py` isolado | Retry, troca de modelo e fallback |
| `--data` como parâmetro | Resolução confiável de datas relativas |
| Pasta `tests/` reservada | Casos de teste e métrica de acerto (avançado) |
| Limite de tamanho com erro claro | Evolui para chunking (intermediário) |

## 11. Riscos técnicos

| Risco | Mitigação |
|---|---|
| Modelo inventa prazo ou responsável | Instrução explícita + `temperature=0` + verificação V1 |
| Formato de saída varia entre execuções | Formato fixo no system prompt; JSON validado no intermediário |
| Vazamento da chave | `.env` no `.gitignore`, `.env.example` sem segredo, checagem V7 |
| Nome do modelo mudar ou ser descontinuado | Modelo em variável de ambiente, não no código |