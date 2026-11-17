"""Monta o prompt enviado ao LLM (instruções de sistema + mensagem do usuário)."""
from datetime import date
from typing import Optional, Tuple

SYSTEM_PROMPT = """Você é um assistente que transforma anotações de reunião em uma lista de tarefas.

Regras:
- Extraia apenas tarefas concretas com responsável e ação. Decisões e conversa solta não são tarefas.
- Converta datas relativas ("sexta", "amanhã", "semana que vem") usando a data de referência fornecida.
- Se o responsável ou o prazo não estiverem claros, escreva "não informado". Nunca invente.
- Formato fixo, uma tarefa por linha: N. Responsável: X | Ação: Y | Prazo: DD/MM/AAAA
- Se não houver tarefas, responda apenas: Nenhuma tarefa identificada.
- Responda em português do Brasil. Não inclua nenhum texto além da lista."""


def montar_prompt(anotacoes: str, data_referencia: date,
                  prompt_sistema: Optional[str] = None) -> Tuple[str, str]:
    """Devolve (system, user).

    Usa o prompt de sistema recebido (vindo de LLM_SYSTEM_PROMPT_ARQUIVO) ou,
    se ausente, o SYSTEM_PROMPT embutido. As anotações vão delimitadas por
    <anotacoes> para o modelo tratá-las como dados, não como instruções.
    """
    user = (
        f"Data de referência: {data_referencia.strftime('%d/%m/%Y')}\n\n"
        f"<anotacoes>\n{anotacoes}\n</anotacoes>"
    )
    return prompt_sistema or SYSTEM_PROMPT, user
