"""Interface web para o extrator de tarefas (portal Devel)."""
import os
from datetime import date

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Extrator de Tarefas</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; color: #222; }
    header { background: #1a1a2e; color: #fff; padding: 1rem 2rem; }
    header h1 { font-size: 1.3rem; }
    header p  { font-size: .85rem; opacity: .7; margin-top: .2rem; }
    main { max-width: 820px; margin: 2rem auto; padding: 0 1rem; }
    section { background: #fff; border-radius: 8px; padding: 1.5rem;
              box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-bottom: 1.5rem; }
    h2 { font-size: 1rem; margin-bottom: 1rem; color: #333; }
    label { display: block; font-size: .85rem; font-weight: 600;
            margin-bottom: .3rem; color: #555; }
    input, textarea, select {
      width: 100%; padding: .6rem .8rem; border: 1px solid #ddd;
      border-radius: 6px; font-size: .95rem; font-family: inherit;
    }
    textarea { resize: vertical; min-height: 120px; }
    .hidden { display: none !important; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
    .full { margin-bottom: 1rem; }
    button {
      background: #1a1a2e; color: #fff; border: none; padding: .7rem 1.5rem;
      border-radius: 6px; cursor: pointer; font-size: .95rem;
    }
    button:hover { background: #2d2d5e; }
    button:disabled { opacity: .5; cursor: not-allowed; }
    #resultado { display: none; }
    #resultado h2 { margin-bottom: .8rem; }
    .tarefa {
      border: 1px solid #e8e8e8; border-radius: 6px; padding: .9rem 1rem;
      margin-bottom: .6rem; background: #fafafa;
    }
    .tarefa .acao { font-weight: 600; margin-bottom: .3rem; }
    .tarefa .meta { font-size: .82rem; color: #666; }
    .badge {
      display: inline-block; padding: .15rem .5rem; border-radius: 4px;
      font-size: .78rem; font-weight: 600; margin-right: .4rem;
    }
    .badge-resp { background: #e8f4fd; color: #1565c0; }
    .badge-prazo { background: #e8f5e9; color: #2e7d32; }
    .badge-sem { background: #f5f5f5; color: #999; }
    .vazio { color: #888; font-style: italic; }
    .erro { color: #c62828; background: #ffebee; padding: .8rem 1rem;
            border-radius: 6px; font-size: .9rem; }
    #status { font-size: .85rem; color: #666; margin-top: .5rem; min-height: 1.2rem; }
  </style>
</head>
<body>
<header>
  <h1>Extrator de Tarefas de Reunião</h1>
  <p>Analisa anotações e devolve uma lista estruturada de tarefas</p>
</header>
<main>

  <section>
    <h2>Configuração do LLM</h2>
    <div class="row">
      <div>
        <label for="provedor">Provedor</label>
        <select id="provedor" onchange="alternarProvedor()">
          <option value="ollama">Ollama (local)</option>
          <option value="gemini">Gemini (Google)</option>
        </select>
      </div>
      <div>
        <label for="data_ref">Data de referência</label>
        <input id="data_ref" type="date" value="{{ hoje }}">
      </div>
    </div>
    <div class="row" id="campo-ollama">
      <div>
        <label for="llm_url">Host do Ollama</label>
        <input id="llm_url" type="text"
               value="http://localhost:11434"
               placeholder="http://localhost:11434">
      </div>
      <div>
        <label for="llm_model">Modelo</label>
        <input id="llm_model" type="text" value="{{ model }}" placeholder="ex: qwen3.5:9b-q4_K_M">
      </div>
    </div>
    <div class="row hidden" id="campo-gemini">
      <div>
        <label for="gemini_api_key">Gemini API Key</label>
        <input id="gemini_api_key" type="password" placeholder="AIza...">
      </div>
      <div>
        <label for="gemini_model">Modelo</label>
        <input id="gemini_model" type="text" value="gemini-2.5-flash" placeholder="ex: gemini-2.5-flash">
      </div>
    </div>
  </section>

  <section>
    <h2>Anotações da reunião</h2>
    <div class="full">
      <label for="anotacoes">Cole ou digite as anotações</label>
      <textarea id="anotacoes" placeholder="Ex: Ana vai enviar o relatório até sexta. Carlos fecha o orçamento até dia 12."></textarea>
    </div>
    <button id="btn" onclick="extrair()">Extrair tarefas</button>
    <div id="status"></div>
  </section>

  <section id="resultado">
    <h2>Tarefas encontradas</h2>
    <div id="lista"></div>
  </section>

</main>
<script>
function alternarProvedor() {
  const provedor = document.getElementById('provedor').value;
  document.getElementById('campo-ollama').classList.toggle('hidden', provedor !== 'ollama');
  document.getElementById('campo-gemini').classList.toggle('hidden', provedor !== 'gemini');
}

async function extrair() {
  const btn = document.getElementById('btn');
  const status = document.getElementById('status');
  const resultado = document.getElementById('resultado');
  const lista = document.getElementById('lista');

  btn.disabled = true;
  status.textContent = 'Enviando para o LLM…';
  resultado.style.display = 'none';
  lista.innerHTML = '';

  const provedor = document.getElementById('provedor').value;
  const payload = {
    texto:    document.getElementById('anotacoes').value,
    data:     document.getElementById('data_ref').value,
    provedor: provedor,
  };
  if (provedor === 'ollama') {
    payload.llm_url = document.getElementById('llm_url').value;
    payload.modelo  = document.getElementById('llm_model').value;
  } else {
    payload.gemini_api_key = document.getElementById('gemini_api_key').value;
    payload.modelo         = document.getElementById('gemini_model').value;
  }

  try {
    const r = await fetch('/extrair', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    btn.disabled = false;
    status.textContent = '';

    if (data.erro) {
      lista.innerHTML = `<div class="erro">${data.erro}</div>`;
      resultado.style.display = 'block';
      return;
    }

    const tarefas = data.tarefas || [];
    if (tarefas.length === 0) {
      lista.innerHTML = '<p class="vazio">Nenhuma tarefa encontrada nas anotações.</p>';
    } else {
      lista.innerHTML = tarefas.map((t, i) => `
        <div class="tarefa">
          <div class="acao">${i+1}. ${t.acao}</div>
          <div class="meta">
            <span class="badge ${t.responsavel ? 'badge-resp' : 'badge-sem'}">
              👤 ${t.responsavel || 'sem responsável'}
            </span>
            <span class="badge ${t.prazo ? 'badge-prazo' : 'badge-sem'}">
              📅 ${t.prazo ? formatarData(t.prazo) : 'sem prazo'}
            </span>
          </div>
        </div>`).join('');
    }
    resultado.style.display = 'block';
  } catch (e) {
    btn.disabled = false;
    status.textContent = '';
    lista.innerHTML = `<div class="erro">Erro de comunicação: ${e.message}</div>`;
    resultado.style.display = 'block';
  }
}

function formatarData(iso) {
  const [a, m, d] = iso.split('-');
  return `${d}/${m}/${a}`;
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        HTML,
        hoje=date.today().isoformat(),
        model=os.getenv("MODEL_NAME", "qwen3.5:9b-q4_K_M"),
    )


@app.route("/extrair", methods=["POST"])
def extrair():
    from extrator import EntradaInvalida, extrair_tarefas
    from extrator.erros import ErroConfiguracao, ErroLLM

    body = request.get_json(force=True) or {}
    texto = body.get("texto", "")
    data_ref = body.get("data") or date.today().isoformat()

    provedor = body.get("provedor", "ollama").strip().lower()
    modelo = body.get("modelo", "").strip()
    os.environ["LLM_PROVIDER"] = provedor

    if provedor == "gemini":
        gemini_api_key = body.get("gemini_api_key", "").strip()
        if gemini_api_key:
            os.environ["GEMINI_API_KEY"] = gemini_api_key
        if modelo:
            os.environ["GEMINI_MODEL"] = modelo
    else:
        llm_url = body.get("llm_url", "").strip()
        if llm_url:
            os.environ["OLLAMA_HOST"] = llm_url
        if modelo:
            os.environ["MODEL_NAME"] = modelo

    try:
        resultado = extrair_tarefas(texto, data_ref)
        return jsonify(resultado)
    except EntradaInvalida as e:
        return jsonify({"erro": f"Entrada inválida: {e}"}), 400
    except ErroConfiguracao as e:
        return jsonify({"erro": f"Configuração: {e}"}), 500
    except ErroLLM as e:
        return jsonify({"erro": f"Erro no LLM: {e}"}), 503


@app.route("/health")
def health():
    return jsonify({"status": "ok", "data": date.today().isoformat()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
