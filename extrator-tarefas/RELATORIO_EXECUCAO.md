## Estrutura do Projeto

```text
extrator-tarefas/
├── README.md          # Documentação do projeto
├── requirements.txt   # Arquivo de dependências
├── .env.example       # Exemplo de variáveis de ambiente (sem segredos)
├── .gitignore         # Arquivos ignorados pelo Git
├── src/               # Código-fonte
└── tests/             # Casos de teste
```

## Como Configurar e Executar



1. Entrar na pasta do projeto
   ```bash
   cd extrator-tarefas
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```

5. Execute os testes:
   ```bash
   pytest tests/
   ```