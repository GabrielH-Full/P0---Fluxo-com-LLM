# Validação em ambiente limpo

Registro da validação da versão final seguindo **apenas** o [GuiaDeExecucao.md](GuiaDeExecucao.md).

## Execução 1 — 16/11/2026

| Item | Valor |
|---|---|
| Como foi validado | Clone novo do repositório (branch `P-avancado`) em um diretório temporário fora do projeto + **venv novo**, instalando somente pelo `requirements-dev.txt` |
| Sistema operacional | macOS 26.6.2 |
| Python | 3.9.6 (única versão disponível na máquina — ver pendência abaixo) |
| Dependências instaladas | `google-genai 1.47.0`, `httpx 0.28.1`, `python-dotenv 1.2.1`, `pytest 8.4.2` |

### Comandos executados e resultado

```bash
git clone --branch P-avancado <repositório> validacao && cd validacao/extrator-tarefas
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt                 # ok
env -u GEMINI_API_KEY pytest -q                     # 66 passed, sem chave e sem rede
python tests/rodar_casos_local.py                   # OK: 18 | ERRO tratado: 7 | QUEBRA: 0
python src/main.py --arquivo tests/casos/exemplo.txt --data 03/11/2026
```

| Cenário | Resultado |
|---|---|
| Sem `.env` | `Erro: Defina GEMINI_API_KEY no arquivo .env (veja o .env.example).` — código 1 |
| `.env` copiado do `.env.example` (chave de exemplo), chamada real | `Erro: Chave de API inválida ou sem permissão…` — código 1, sem texto da API |
| `.env` com chave real, 1ª tentativa | API respondeu 503 → `Erro: Serviço do LLM indisponível no momento…` — código 1 |
| `.env` com chave real, 2ª tentativa | Lista de 3 tarefas gerada em ~2,9 s — código 0 |
| Logs | Início, configuração (sem a chave), envio, resposta, duração e fim registrados; nenhum segredo, anotação ou resposta nos logs |

### Problemas encontrados e correções

| # | O que aconteceu | Correção |
|---|---|---|
| 1 | Na versão anterior (`65f1427`), a aplicação quebrava ao iniciar no venv limpo: `ModuleNotFoundError: No module named 'google.api_core'`. O pacote só existia no venv antigo como sobra de bibliotecas que não estão no `requirements.txt`. | `src/llm.py` passou a usar as exceções do próprio SDK (`google.genai.errors`) e `httpx`, ambos declarados no `requirements.txt`. Confirmado: `google.api_core` não está instalado no venv limpo e a aplicação funciona. |
| 2 | Com a chave de exemplo, o Gemini respondeu **400** (motivo `API_KEY_INVALID`), não 401; a mensagem exibida era genérica ("A API recusou a solicitação (código 400)"). | `src/llm.py` reconhece `API_KEY_INVALID` como chave inválida; teste adicionado em `tests/test_llm.py`. Revalidado: mensagem correta. |
| 3 | A primeira chamada com a chave real recebeu **503** (instabilidade do serviço do Google). | Nenhuma correção de código necessária: o erro foi tratado com mensagem amigável. A segunda tentativa funcionou. |

### Pendências

- [ ] Repetir esta validação com **Python 3.10+** (versão documentada em `.python-version`). A máquina usada só tinha Python 3.9.6, que funciona, mas está fora de suporte e gera avisos do `google-auth`.
- [ ] (Ideal) Repetir em outro computador ou com outra pessoa seguindo só o guia.
