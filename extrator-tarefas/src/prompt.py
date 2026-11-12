from datetime import date

SYSTEM_PROMPT = """Você é um assistente que transforma anotações de reunião em uma lista de tarefas.

Regras:
- Extraia apenas tarefas concretas com responsável e ação. Decisões e conversa solta não são tarefas.
- Converta datas relativas ("sexta", "amanhã", "semana que vem") usando a data de referência fornecida.
- Se o responsável ou o prazo não estiverem claros, escreva "não informado". Nunca invente.
- Formato fixo, uma tarefa por linha: N. Responsável: X | Ação: Y | Prazo: DD/MM/AAAA
- Se não houver tarefas, responda apenas: Nenhuma tarefa identificada.
- Responda em português do Brasil. Não inclua nenhum texto além da lista."""


def montar_prompt(anotacoes: str, data_referencia: date) -> tuple[str, str]:
    user = (
        f"Data de referência: {data_referencia.strftime('%d/%m/%Y')}\n\n"
        f"<anotacoes>\n{anotacoes}\n</anotacoes>"
    )
    return SYSTEM_PROMPT, user
