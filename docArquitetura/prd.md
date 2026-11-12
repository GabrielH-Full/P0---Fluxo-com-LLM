# PRD: Transformador de Anotações de Reunião em Lista de Tarefas

**Bloco:** P0 - Fluxo com LLM
**Etapa:** 1 de 3 (Nível básico: construção incremental)
**Status:** Rascunho
**Data:** 11/11/2026

---

## 1. Resumo

Aplicação em Python, executada no terminal, que recebe anotações soltas de uma reunião e usa um LLM para devolver uma lista de tarefas com responsável, ação e prazo.

> **Frase única:** Recebe anotações soltas de uma reunião e devolve uma lista de tarefas com responsável, ação e prazo.

## 2. Problema

Depois de reuniões, as anotações costumam ser apressadas: frases incompletas, nomes abreviados, datas relativas ("sexta", "semana que vem") e decisões misturadas com conversa. Organizar isso à mão é trabalhoso e as tarefas combinadas se perdem, porque ninguém lembra com clareza **quem ficou de fazer o quê e até quando**.

## 3. Público

Qualquer pessoa que participa de reuniões e anota de forma desestruturada: profissionais, estudantes em projetos de grupo, membros de associações e equipes pequenas.

## 4. Por que um LLM

- A entrada é linguagem livre, sem padrão fixo (regex e regras não cobrem).
- É preciso interpretar ambiguidades ("ana talvez", "ficou de ver").
- É preciso distinguir **tarefa** de **decisão** e de conversa solta.
- Datas relativas exigem interpretação com uma data de referência.

## 5. Objetivo desta etapa (Nível básico)

Entregar um fluxo mínimo, funcional e reproduzível de ponta a ponta:

**entrada pelo terminal → solicitação ao LLM → resposta apresentada ao usuário.**

### Métrica de sucesso

Ao executar o programa e fornecer uma entrada válida, o usuário recebe uma resposta útil do modelo (uma lista legível de tarefas com responsável, ação e prazo).

## 6. Requisitos funcionais

| ID | Requisito |
|---|---|
| RF01 | A aplicação deve ser escrita em Python. |
| RF02 | Deve receber uma entrada textual pelo terminal (digitada/colada ou via argumento). |
| RF03 | Deve montar uma solicitação derivada da entrada e enviá-la ao LLM escolhido. |
| RF04 | Deve apresentar a resposta do modelo ao usuário no terminal. |
| RF05 | Quando não houver prazo ou responsável claro, deve indicar "não informado" em vez de inventar. |
| RF06 | Deve exibir mensagem de erro compreensível se a entrada estiver vazia ou a chave de API estiver ausente. |

## 7. Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF01 | Credenciais e parâmetros sensíveis ficam fora do código, em variáveis de ambiente (`.env`). |
| RNF02 | O `.env` nunca é versionado; um `.env.example` documenta as variáveis. |
| RNF03 | Dependências declaradas em `requirements.txt`. |
| RNF04 | Reproduzível por terceiros: clonar, instalar e rodar seguindo o README. |
| RNF05 | Código organizado em funções pequenas, preparado para evoluir nos níveis seguintes. |

## 8. Competências exercitadas

| Código | Competência | Como é atendida |
|---|---|---|
| C01 | Programa Python funcional com bibliotecas externas | Script em Python usando SDK do LLM e `python-dotenv` |
| C02 | Criar, versionar e publicar o repositório | Git com commits convencionais e publicação em repositório remoto |
| C03 | Configurar acesso ao serviço, autenticar, enviar e processar resposta | Chave via variável de ambiente, chamada à API e tratamento da resposta |
| C04 | Configurar e executar o ambiente local | Ambiente virtual, `requirements.txt` e instruções no README |

## 9. Exemplo

**Entrada:**
```text
reunião kickoff 03/11
joão vai ver o orçamento com o fornecedor até sexta
precisamos definir o logo, ana talvez
ficou decidido usar react
carla manda a ata amanhã
```

**Saída esperada:**
```text
1. Responsável: João   | Ação: Verificar orçamento com o fornecedor | Prazo: 07/11/2026
2. Responsável: Ana    | Ação: Definir o logo                       | Prazo: não informado
3. Responsável: Carla  | Ação: Enviar a ata                         | Prazo: 04/11/2026
```

## 10. Fora do escopo desta etapa

- Saída em JSON com schema validado, retry e chunking (Nível intermediário).
- Defesa contra prompt injection, testes com métrica e avaliação (Nível avançado).
- Banco de dados, interface gráfica, aplicação web, RAG, agentes, integração com calendário, transcrição de áudio.

## 11. Riscos e premissas

| Risco / premissa | Mitigação |
|---|---|
| Tema comum (muita gente faz) | Tratar incerteza com "não informado" e documentar bem as decisões. |
| LLM pode inventar prazos ou responsáveis | Instrução explícita no prompt (RF05). |
| Vazamento da chave de API | `.env` no `.gitignore`; apenas `.env.example` versionado. |
| Custo/limite de uso da API | Entradas curtas no básico; modelo configurável por variável. |
| Premissa | O usuário tem uma chave de API válida do provedor escolhido. |

## 12. Critérios de aceite

- [ ] Executar `python src/main.py` e colar uma anotação retorna uma lista de tarefas legível.
- [ ] Entrada vazia exibe erro claro, sem stack trace.
- [ ] Sem chave configurada, exibe erro claro orientando a criar o `.env`.
- [ ] Nenhuma credencial no código ou no histórico do Git.
- [ ] `pip install -r requirements.txt` instala tudo o que é necessário.
- [ ] README descreve problema, público, frase única e como executar.