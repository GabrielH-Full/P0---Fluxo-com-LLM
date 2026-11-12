# Tasks: Nível Básico (Etapa 1 de 3)

**Origem:** [PRD.md](./PRD.md) e [TECHSPEC.md](./TECHSPEC.md)
**Meta:** ao executar o programa e fornecer uma entrada válida, receber uma lista de tarefas útil gerada pelo LLM.

**Legenda:** `[ ]` pendente · `[x]` concluída · **Ref.** = requisito do PRD / seção do TechSpec atendida

---

## Fase 0: Repositório e ambiente (C02, C04)

- [ ] **T01. Criar a estrutura de pastas**
  Criar `src/`, `tests/` e `docs/` dentro de `extrator-tarefas/`, com `.gitkeep` em `tests/`.
  *Ref.: TechSpec §3*
  *Pronto quando:* a árvore de pastas bate com o TechSpec.

- [ ] **T02. Criar `.gitignore`**
  Incluir `.env`, `.venv/`, `__pycache__/`, `*.pyc`.
  *Ref.: RNF02, TechSpec §7*
  *Pronto quando:* `git status` não mostra `.env` nem `.venv` depois de criados.

- [ ] **T03. Criar `requirements.txt`**
  Declarar `anthropic` e `python-dotenv`.
  *Ref.: RNF03, C04, TechSpec §7*
  *Pronto quando:* `pip install -r requirements.txt` roda sem erro em ambiente virtual limpo.

- [ ] **T04. Criar `.env.example`**
  Incluir `ANTHROPIC_API_KEY` com valor de exemplo e `LLM_MODEL`.
  *Ref.: RNF01, RNF02*
  *Pronto quando:* o arquivo está versionado e sem nenhuma chave real.

- [ ] **T05. Configurar o ambiente local**
  Criar `.venv`, instalar dependências, copiar `.env.example` para `.env` e preencher a chave real.
  *Ref.: C04, TechSpec §8*
  *Pronto quando:* `python -c "import anthropic, dotenv"` executa sem erro.

---

## Fase 1: Núcleo da aplicação (C01, C03)

- [ ] **T06. Implementar `config.py`**
  Carregar o `.env`, retornar chave e modelo e levantar `ConfigError` quando a chave estiver ausente.
  *Ref.: RNF01, RF06, TechSpec §4.1*
  *Pronto quando:* sem chave, a mensagem orienta criar o `.env`; com chave, retorna a configuração.

- [ ] **T07. Implementar `entrada.py`**
  `ler_entrada` (arquivo ou stdin) e `validar_entrada` (vazio, arquivo inexistente, limite de tamanho).
  *Ref.: RF02, RF06, TechSpec §4.2*
  *Pronto quando:* colar texto + Ctrl+D e `--arquivo` funcionam; os casos inválidos geram `EntradaInvalidaError`.

- [ ] **T08. Implementar `prompt.py`**
  `montar_prompt` com system prompt (regras, formato fixo, "não informado", "Nenhuma tarefa identificada") e user prompt com data de referência e anotações entre `<anotacoes>`.
  *Ref.: RF03, RF05, TechSpec §4.3*
  *Pronto quando:* a função retorna `(system, user)` e o texto contém a data e as anotações delimitadas.

- [ ] **T09. Implementar `llm.py`**
  `chamar_llm` com o SDK, `temperature=0`, extração do texto da resposta e conversão dos erros do SDK em `LLMError`.
  *Ref.: RF03, RF04, C03, TechSpec §4.4*
  *Pronto quando:* uma chamada real retorna texto; chave inválida gera erro amigável, sem stack trace.

- [ ] **T10. Implementar `main.py`**
  CLI com `--arquivo` e `--data`, orquestração do fluxo, captura das exceções do projeto, mensagem em `stderr` e código de saída `1`.
  *Ref.: RF02, RF04, RF06, TechSpec §4.5*
  *Pronto quando:* `python src/main.py` executa o fluxo completo e imprime a lista.

---

## Fase 2: Verificação manual (TechSpec §9)

- [ ] **T11. Criar `exemplo.txt` com a entrada do PRD**
  Colocar na raiz do projeto ou em `tests/casos/`.
  *Pronto quando:* o arquivo contém o texto do exemplo do PRD.

- [ ] **T12. Executar V1 a V7 e registrar os resultados**
  Rodar cada cenário da tabela de verificação e anotar o resultado (passou/falhou e observações).
  *Ref.: TechSpec §9, Critérios de aceite do PRD*
  *Pronto quando:* V1 a V7 passam; falhas viram ajustes no prompt ou no código.

- [ ] **T13. Ajustar o prompt com base nos testes**
  Se o modelo inventar prazo, tratar decisão como tarefa ou fugir do formato, refinar o system prompt e repetir V1 e V5.
  *Pronto quando:* a saída do exemplo bate com a saída esperada do PRD.

---

## Fase 3: Documentação e publicação (C02, C04)

- [ ] **T14. Escrever o `README.md` do projeto**
  Incluir problema, público, frase única, justificativa do LLM, exemplo, pré-requisitos, instalação, configuração do `.env` e execução.
  *Ref.: Critérios de aceite do PRD*
  *Pronto quando:* alguém que nunca viu o projeto consegue rodá-lo só com o README.

- [ ] **T15. Validar a reprodução em ambiente limpo**
  Clonar o repositório em outra pasta, criar um `.venv` novo, instalar e executar seguindo apenas o README.
  *Ref.: RNF04, C04*
  *Pronto quando:* roda do zero sem ajustes manuais além de preencher a chave.

- [ ] **T16. Auditoria de segredos**
  Conferir que nenhuma chave aparece no código, no `.env.example` ou no histórico do Git (`git log -p | grep -i "sk-"`, `git ls-files | grep .env`).
  *Ref.: RNF01, RNF02*
  *Pronto quando:* só `.env.example` está versionado e sem segredo.

- [ ] **T17. Commits e publicação**
  Commits pequenos no padrão Conventional Commits e push para o repositório remoto.
  *Ref.: C02*
  *Pronto quando:* o repositório remoto tem o código, os docs e o histórico organizado.

---

## Ordem sugerida e dependências

```
T01 → T02 → T03 → T04 → T05
                         ↓
         T06 → T07 → T08 → T09 → T10
                                  ↓
                         T11 → T12 → T13
                                       ↓
                           T14 → T15 → T16 → T17
```

## Sugestão de commits

| Após | Mensagem |
|---|---|
| T01 a T04 | `chore: cria estrutura, .gitignore, requirements e .env.example` |
| T06 | `feat: carrega configuração e chave de API via variáveis de ambiente` |
| T07 | `feat: lê anotações do terminal ou de arquivo com validação` |
| T08 | `feat: adiciona prompt de extração de tarefas` |
| T09 | `feat: integra chamada ao LLM com tratamento de erros` |
| T10 | `feat: adiciona CLI e orquestra o fluxo completo` |
| T11 a T13 | `test: adiciona exemplo e ajusta prompt após verificação manual` |
| T14 | `docs: documenta instalação, execução e uso no README` |
| `docs/` | `docs: adiciona PRD, TechSpec e Tasks do nível básico` |

## Definition of Done (nível básico)

- [ ] Python funcional com bibliotecas externas (C01)
- [ ] Repositório versionado e publicado (C02)
- [ ] Chave via variável de ambiente, chamada à API e resposta processada (C03)
- [ ] Ambiente reproduzível com `requirements.txt` e README (C04)
- [ ] Nenhuma credencial no código ou no histórico
- [ ] Entrada válida retorna uma lista de tarefas útil