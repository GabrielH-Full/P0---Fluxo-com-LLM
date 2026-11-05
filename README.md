# P0 - Fluxo com LLM

## Tema: Transformador de Anotações de Reunião em Lista de Tarefas

Repositório do bloco **P0 - Fluxo com LLM**, organizado conforme o padrão estrutural do curso.

---

## Problema escolhido

Depois de reuniões, as anotações costumam ficar soltas, incompletas e misturadas com conversa e decisões. Com isso, ninguém lembra com clareza **quem ficou de fazer o quê e até quando**, e as tarefas combinadas se perdem. Organizar essas anotações à mão é trabalhoso e propenso a esquecimentos.

## Usuário ou público

Qualquer pessoa que participa de reuniões e anota de forma apressada: profissionais, estudantes em projetos de grupo, membros de associações e equipes pequenas que precisam transformar anotações informais em compromissos claros.

## Explicação do problema e da solução em uma única frase

> Esta aplicação recebe anotações soltas de uma reunião e, usando um LLM, devolve uma lista organizada de tarefas com responsável, ação e prazo.

## Por que usar um LLM

As anotações são escritas em linguagem livre, com frases incompletas, nomes abreviados e datas relativas (como "sexta" ou "semana que vem"). Também é preciso distinguir **tarefas** de **decisões** e de conversa solta. Esse tipo de interpretação não é coberto por regras fixas ou expressões regulares, mas é adequado a um modelo de linguagem.

## Exemplo de uso

**Entrada:**

```text
reunião kickoff 03/11
joão vai ver o orçamento com o fornecedor até sexta
precisamos definir o logo, ana talvez
ficou decidido usar react
carla manda a ata amanhã
```

**Saída:**

```text
1. Responsável: João  | Ação: Verificar orçamento com o fornecedor | Prazo: 07/11/2026
2. Responsável: Ana   | Ação: Definir o logo                       | Prazo: não informado
3. Responsável: Carla | Ação: Enviar a ata                         | Prazo: 04/11/2026
```

---

## Estrutura do Bloco

```text
P0 - Fluxo com LLM/
├── README.md
├── CONTRIBUICOES.md
├── .gitignore
└── extrator-tarefas/
    ├── README.md
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── src/
    └── tests/
```

### Como executar o projeto

> As instruções detalhadas de instalação e execução estão no RELATORIO_EXECUCAO do projeto: [RELATORIO_EXECUCA.md](./extrator-tarefas/RELATORIO_EXECUCAO.md).

