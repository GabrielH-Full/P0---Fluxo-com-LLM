# PRD — Auditoria do Projeto (Nível Avançado: entrega reproduzível)

## 1. Objetivo

Analisar o projeto **sem realizar nenhuma modificação** e gerar um relatório indicando o que está atendido, o que está parcial e o que está faltando em relação aos requisitos do **Nível Avançado — entrega reproduzível**.

## 2. Regras da análise (obrigatórias)

- **Modo somente leitura.** Não criar, editar, mover, renomear ou apagar arquivos do projeto.
- **Não instalar dependências** no ambiente do projeto e **não fazer commits**, branches, stashes ou qualquer alteração no Git.
- **Não executar chamadas reais ao LLM.** Testes só podem ser rodados se não fizerem chamadas externas; na dúvida, apenas ler o código.
- **Não exibir segredos.** Se encontrar chaves, tokens, credenciais ou dados pessoais, registrar apenas *o arquivo e a linha*, mascarando o valor (ex.: `sk-****`).
- A única saída permitida é o relatório (ver seção 6), entregue como resposta ou em arquivo separado **fora** do projeto, se solicitado.

## 3. Escopo do que deve ser verificado

### R1 — Configuração externa ao núcleo
Configurações do LLM (limite de tokens, temperatura, top_p, modelo, prompt de sistema/comportamento básico etc.) devem poder ser alteradas **sem modificar o núcleo da aplicação**.

Verificar:
- Existe arquivo de configuração (`.env`, `config.yaml`, `config.json`, `settings.py` separado etc.) ou variáveis de ambiente?
- Existe `.env.example` (ou equivalente) documentando as variáveis, **sem valores reais**?
- Há valores *hardcoded* no código principal (modelo, max_tokens, temperatura, chave de API)?
- Há valores padrão seguros quando a configuração está ausente?

### R2 — Registros (logs) seguros
Deve haver registros simples que ajudem a entender a execução, **sem armazenar**: chaves, tokens, credenciais, dados pessoais ou conteúdo sensível desnecessário.

Verificar:
- Uso de `logging` (ou similar) em vez de apenas `print`.
- Pontos registrados: início/fim da execução, configuração carregada (sem segredos), envio da solicitação, sucesso/erro da resposta, duração.
- Ausência de logs com a chave da API, headers de autorização, prompt completo do usuário ou resposta integral quando desnecessário.
- Arquivos de log versionados indevidamente (ex.: `*.log` no repositório) e se `.gitignore` os exclui.

### R3 — Documentação de versão e bibliotecas
Verificar:
- Versão do Python documentada (README, `pyproject.toml`, `.python-version`, `runtime.txt`).
- Principais bibliotecas listadas (`requirements.txt`, `pyproject.toml`, `Pipfile`) — idealmente com versões fixadas ou faixas.
- Coerência entre o que é importado no código e o que está declarado nas dependências (bibliotecas faltando ou sobrando).

### R4 — Teste da lógica local sem chamada real ao LLM
Deve existir **pelo menos um teste** executável sem chamar o LLM de verdade.

Verificar se há teste cobrindo pelo menos um dos itens:
- validação da entrada;
- preparação da solicitação;
- carregamento da configuração;
- tratamento de uma resposta simulada;
- tratamento de um erro simulado.

Verificar também:
- Uso de *mocks/stubs/fakes* (ex.: `unittest.mock`, `pytest-mock`, `monkeypatch`).
- Instrução no README de como rodar os testes (ex.: `pytest`).
- Se os testes dependem de chave de API ou rede (não deveriam).

### R5 — Validação em ambiente limpo
A versão final deve ter sido validada em ambiente limpo (novo venv, outro computador ou outra pessoa seguindo apenas o README).

Verificar:
- README contém passo a passo completo: clonar, criar venv, instalar dependências, configurar variáveis, executar e testar.
- Existe registro dessa validação (seção no README, `VALIDACAO.md`, `CHANGELOG.md` ou similar) informando **como** foi feita.
- Se houve problemas, estão registrados **o que aconteceu e a correção realizada**.

> Observação: o auditor **não** deve criar o ambiente limpo dentro do projeto. Pode apenas avaliar se o README é suficiente para isso e apontar lacunas.

## 4. Competências a avaliar

| Código | Competência | Evidências esperadas |
|---|---|---|
| **C01** | Código compreensível e organizado para terceiros | Estrutura de pastas clara, separação núcleo/config/cliente LLM, nomes legíveis, funções pequenas, docstrings/comentários úteis, README objetivo. |
| **C02** | Histórico do Git como evidência real da construção | Vários commits ao longo do tempo, mensagens descritivas, evolução incremental (não um único commit final), ausência de segredos no histórico. Usar apenas comandos de leitura: `git log`, `git log --stat`, `git show`. |
| **C03** | Lidar com respostas e falhas sem expor dados sensíveis | `try/except` em torno da chamada ao LLM, mensagens de erro amigáveis, tratamento de timeout/limite/erro de autenticação/resposta vazia, nenhuma chave ou stack trace sensível exibido ao usuário. |
| **C04** | Instalação e execução em ambiente diferente | Dependências declaradas, sem caminhos absolutos da máquina do desenvolvedor, `.env.example`, README reprodutível, registro da validação em ambiente limpo. |

## 5. Procedimento sugerido

1. Listar a estrutura do projeto e identificar o ponto de entrada.
2. Ler README, arquivos de dependências e de configuração.
3. Ler o núcleo da aplicação e o módulo de chamada ao LLM.
4. Procurar segredos e dados sensíveis (busca por `api_key`, `token`, `secret`, `password`, `sk-`, `Bearer`, e-mails, CPFs etc.) em código, logs e histórico do Git.
5. Localizar a pasta de testes e verificar se usam simulação.
6. Inspecionar o histórico do Git (somente leitura).
7. Preencher o relatório.

## 6. Formato do relatório de saída

```markdown
# Relatório de Auditoria — Nível Avançado

**Projeto:** <nome>
**Data:** <data>
**Modificações realizadas:** nenhuma

## Resumo
- Atendidos: X de 5 requisitos | Y de 4 competências
- Situação geral: Aprovado / Aprovado com ressalvas / Pendente

## Requisitos
| ID | Requisito | Status | Evidência (arquivo:linha) | O que falta |
|---|---|---|---|---|
| R1 | Configuração externa ao núcleo | ✅ / ⚠️ / ❌ | ... | ... |
| R2 | Logs sem dados sensíveis | ... | ... | ... |
| R3 | Versão do Python e bibliotecas | ... | ... | ... |
| R4 | Teste local sem chamada ao LLM | ... | ... | ... |
| R5 | Validação em ambiente limpo | ... | ... | ... |

## Competências
| ID | Competência | Status | Evidência | O que falta |
|---|---|---|---|---|
| C01 | Código organizado para terceiros | ... | ... | ... |
| C02 | Histórico do Git como evidência | ... | ... | ... |
| C03 | Falhas sem expor dados sensíveis | ... | ... | ... |
| C04 | Execução em outro ambiente | ... | ... | ... |

## Riscos de segurança encontrados
- <arquivo:linha> — <descrição, com valor mascarado>

## Itens faltando (checklist de pendências)
- [ ] ...
- [ ] ...

## Recomendações (sem aplicar)
1. ...
2. ...
```

**Legenda de status:** ✅ Atendido · ⚠️ Parcial · ❌ Ausente

## 7. Critério de conclusão

A análise está concluída quando:
- todos os itens R1–R5 e C01–C04 tiverem status e evidência;
- todas as pendências estiverem listadas no checklist;
- for confirmado que **nenhum arquivo do projeto foi alterado** (ex.: `git status` limpo, igual ao início).