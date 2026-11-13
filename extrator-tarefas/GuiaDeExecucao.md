# Extrator de Tarefas de Reunião

> Recebe anotações soltas de uma reunião e devolve uma lista de tarefas com responsável, ação e prazo.

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

- Python 3.10+
- Chave de API do Google Gemini ([aistudio.google.com](https://aistudio.google.com))

## Instalação

```bash
cd extrator-tarefas
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

```bash
cp .env.example .env
# edite .env e preencha GEMINI_API_KEY com sua chave real
```

## Execução

```bash
# via arquivo(esse e um arquivo test.text)
python src/main.py --arquivo tests/casos/exemplo.txt --data 03/11/2026 

# via terminal (cole o texto e finalize com Ctrl+D)
# A flag --data define a data de referência para o LLM resolver datas relativas que aparecem nas anotações.
python src/main.py --data 03/11/2026

# Texto direto no comando (sem Ctrl+D, sessão fica viva)
python src/main.py --texto "pedro revisa o dashboard até quarta" --data 10/11/2026

# ver todas as opções
python src/main.py --help
```

# Como rodar (a partir da pasta extrator-tarefas, com o ambiente virtual ativado):

```bash
source .venv/bin/activate
python tests/rodar_casos_local.py          # todos os casos
python tests/rodar_casos_local.py 11 17    # só os casos que começam com 11 ou 17
python tests/rodar_casos_local.py 16 -v    # mostra também o prompt que seria enviado ao LLM
```