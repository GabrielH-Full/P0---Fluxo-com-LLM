# Extrator de Tarefas de Reunião

> Recebe anotações soltas de uma reunião e devolve uma lista de tarefas com responsável, ação e prazo.

Este é o guia principal do projeto: instalação, configuração, execução e testes.
A validação em ambiente limpo está registrada em [VALIDACAO.md](VALIDACAO.md).

## Problema

Depois de reuniões, as anotações costumam ser apressadas: frases incompletas, nomes abreviados, datas relativas ("sexta", "semana que vem") e decisões misturadas com conversa. Organizar isso à mão é trabalhoso e as tarefas combinadas se perdem.

## Público

Qualquer pessoa que participa de reuniões e anota de forma desestruturada.

## Por que um LLM

A entrada é linguagem livre, sem padrão fixo. É preciso interpretar ambiguidades, distinguir tarefas de decisões e converter datas relativas com base em uma referência.

## Exemplo

**Entrada:**
```
reunião kickoff 03/11
joão vai ver o orçamento com o fornecedor até sexta
precisamos definir o logo, ana talvez
ficou decidido usar react
carla manda a ata amanhã
```

**Saída:**
```
1. Responsável: João   | Ação: Verificar orçamento com o fornecedor | Prazo: 07/11/2026
2. Responsável: Ana    | Ação: Definir o logo                       | Prazo: não informado
3. Responsável: Carla  | Ação: Enviar a ata                         | Prazo: 04/11/2026
```

## Pré-requisitos

- Python **3.10 ou superior** (versão indicada em `.python-version`)
- Git
- Chave de API do Google Gemini ([aistudio.google.com](https://aistudio.google.com))

## Principais bibliotecas

| Biblioteca | Para que serve |
|---|---|
| `google-genai` | SDK oficial do Google Gemini: envia o prompt e recebe a resposta |
| `httpx` | Cliente HTTP usado pelo SDK; importado para tratar timeout e falha de conexão |
| `python-dotenv` | Carrega as variáveis do arquivo `.env` |
| `pytest` *(desenvolvimento)* | Executa os testes automatizados |

As versões aceitas estão em `requirements.txt` (aplicação) e `requirements-dev.txt` (aplicação + testes).

## Instalação

**1. Clonar o repositório**
```bash
git clone https://github.com/GabrielH-Full/P0---Fluxo-com-LLM.git
cd P0---Fluxo-com-LLM/extrator-tarefas
```

**2. Criar e ativar o ambiente virtual**
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```
Confira a versão com `python --version` (deve ser 3.10+).

**3. Instalar as dependências**
```bash
pip install -r requirements.txt        # só para usar a aplicação
pip install -r requirements-dev.txt    # aplicação + ferramentas de teste
```

## Configuração

```bash
cp .env.example .env        # Windows: copy .env.example .env
```
Edite o `.env` e preencha **`GEMINI_API_KEY`** com sua chave real. As demais variáveis são opcionais: se ficarem vazias ou ausentes, o valor padrão é usado.

| Variável | Padrão | O que controla |
|---|---|---|
| `GEMINI_API_KEY` | — (obrigatória) | Chave de acesso à API do Gemini |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Modelo usado |
| `LLM_TEMPERATURE` | `0` | Criatividade da resposta (0 a 2) |
| `LLM_TOP_P` | `1.0` | Amostragem nucleus (0 a 1) |
| `LLM_MAX_TOKENS` | `1024` | Limite de tokens da resposta |
| `LLM_TIMEOUT_SEGUNDOS` | `30` | Tempo máximo de espera pela API |
| `LLM_SYSTEM_PROMPT_ARQUIVO` | vazio (prompt embutido) | Caminho de um `.txt` UTF-8 com outro prompt de sistema |
| `LOG_LEVEL` | `INFO` | Nível dos logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LOG_ARQUIVO` | vazio (só terminal) | Arquivo para gravar os logs (ex.: `logs/extrator.log`) |

Valores inválidos (ex.: `LLM_TEMPERATURE=abc`) geram uma mensagem clara indicando qual variável corrigir.
O `.env` nunca deve ser versionado (já está no `.gitignore`).

## Execução

```bash
# via arquivo
python src/main.py --arquivo tests/casos/exemplo.txt --data 03/11/2026

# via terminal (cole o texto e finalize com Ctrl+D; no Windows, Ctrl+Z e Enter)
python src/main.py --data 03/11/2026

# texto direto no comando
python src/main.py --texto "pedro revisa o dashboard até quarta" --data 10/11/2026

# ver todas as opções
python src/main.py --help
```

A flag `--data` define a data de referência usada para resolver datas relativas (padrão: hoje).
Ao final, a aplicação pergunta se deseja salvar a lista em `tarefas_DD-MM-AAAA.txt`.

### Logs

Cada execução registra no terminal (stderr) o início e o fim, a configuração carregada, o envio ao LLM, o resultado e a duração.
Os logs **não** incluem a chave de API, o texto das anotações nem a resposta completa, apenas metadados (modelo, tamanhos, tempo).
Para silenciá-los use `LOG_LEVEL=WARNING`; para gravá-los em arquivo, defina `LOG_ARQUIVO`.

### Erros

Problemas previsíveis (chave inválida, limite de uso, modelo inexistente, timeout, sem internet, arquivo inválido, resposta vazia) mostram uma mensagem explicando o que fazer.
Em um erro não previsto, só o tipo do erro é exibido; para ver o detalhe técnico completo, rode com `EXTRATOR_DEBUG=1`.

## Testes

Os testes **não chamam o LLM** e não precisam de chave de API nem de internet: o SDK do Gemini é substituído por simulações (`unittest.mock`).

```bash
pip install -r requirements-dev.txt
pytest                      # todos os testes
pytest -v tests/test_llm.py # só os testes do cliente do LLM
```

| Arquivo | O que verifica |
|---|---|
| `tests/test_entrada.py` | Validação da entrada (vazia, limite de 20 000 caracteres, arquivo inexistente, pasta, Latin-1) |
| `tests/test_prompt.py` | Montagem da solicitação (data de referência, delimitação das anotações, prompt de sistema) |
| `tests/test_config.py` | Carregamento da configuração (padrões, valores do ambiente, valores inválidos, chave fora dos logs) |
| `tests/test_llm.py` | Resposta simulada, resposta vazia, erros 401/403/404/429/5xx, timeout, sem conexão, ausência de segredos |
| `tests/test_casos.py` | Fluxo completo do `main.py` para cada arquivo de `tests/casos/`, com status esperado |

Há também um script exploratório que mostra um resumo legível de todos os casos:
```bash
python tests/rodar_casos_local.py          # todos os casos
python tests/rodar_casos_local.py 11 17    # só os casos que começam com 11 ou 17
python tests/rodar_casos_local.py 16 -v    # mostra também o prompt que seria enviado ao LLM
```

## Estrutura do projeto

```
extrator-tarefas/
├── src/
│   ├── main.py       # ponto de entrada: argumentos, orquestração e tratamento de erros
│   ├── config.py     # lê e valida o .env (chave, modelo, parâmetros do LLM)
│   ├── entrada.py    # lê arquivo/stdin e valida as anotações
│   ├── prompt.py     # monta o prompt de sistema e a mensagem do usuário
│   ├── llm.py        # chama o Gemini e traduz falhas em mensagens amigáveis
│   ├── registro.py   # configuração dos logs
│   └── erros.py      # textos das mensagens de erro exibidas ao usuário
├── tests/            # testes pytest, casos de exemplo e script exploratório
├── docs/             # PRD, TASKS e relatórios de auditoria por nível
├── .env.example      # modelo do .env, sem valores reais
├── requirements.txt  # dependências da aplicação
├── requirements-dev.txt  # dependências de desenvolvimento (testes)
├── .python-version   # versão do Python do projeto
└── VALIDACAO.md      # registro da validação em ambiente limpo
```

- **`main.py`**: único ponto de entrada. Lê os argumentos, chama os outros módulos em sequência e converte qualquer falha em mensagem e código de saída.
- **`config.py`**: concentra tudo o que é configurável. Para mudar o comportamento do LLM edita-se o `.env`, não o código.
- **`entrada.py`**: garante que o texto existe, está em UTF-8 e respeita o limite de tamanho antes de qualquer chamada à API.
- **`prompt.py`**: define as regras do assistente e coloca as anotações entre `<anotacoes>` para que sejam tratadas como dados.
- **`llm.py`**: único módulo que fala com a API; isola o SDK e garante que nada sensível chegue ao usuário ou aos logs.
- **`registro.py`**: define formato, nível e destino dos logs e silencia bibliotecas de rede que poderiam registrar headers.
- **`erros.py`**: mensagens explicativas reutilizáveis (pasta no lugar de arquivo, codificação inválida, erro inesperado).
