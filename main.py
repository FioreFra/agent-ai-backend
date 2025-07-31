
from flask import Flask, request, jsonify
from openai import OpenAI
import os
import json

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# STEP 1: Genera due proposte creative complete
@app.route("/genera_proposte", methods=["POST"])
def genera_proposte():
    data = request.get_json()

    nome_brand = data.get("nome_brand", "Brand")
    tone = data.get("tone_of_voice", "elegante")
    obiettivi = data.get("obiettivi", "aumentare visibilità")
    prodotti = data.get("prodotti_servizi", "arredi")
    colori = data.get("colori_brand", "rosa cipria, panna")
    formati = data.get("formati_social", ["Post Instagram"])

    prompt = f"""
Sei un brand designer, copywriter e graphic creator.

Hai ricevuto queste informazioni di brief da un brand:
- Nome brand: {nome_brand}
- Tone of voice: {tone}
- Obiettivi della comunicazione: {obiettivi}
- Prodotti o servizi: {prodotti}
- Colori principali del brand: {colori}
- Formati social richiesti: {", ".join(formati)}

🎯 Il tuo compito è creare DUE proposte creative distinte per una campagna social coordinata.

Ogni proposta deve contenere:
- Un nome del concept
- Una descrizione del mood visivo
- Un oggetto JSON con le versioni grafiche per TUTTI i formati richiesti

Per ogni formato:
- Dimensioni in pixel
- Tipo e colore sfondo
- Headline
- CTA
- Font headline e CTA
- Elementi grafici suggeriti

📦 Output in JSON come lista con 2 oggetti.
Nessun testo aggiuntivo, solo JSON.
"""

    gpt = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )

    try:
        contenuto = gpt.choices[0].message.content
        proposte = json.loads(contenuto)
        return jsonify({"proposte": proposte})
    except:
        return jsonify({"errore": "Output non valido", "contenuto": gpt.choices[0].message.content}), 400

# STEP 2: Genera immagine da proposta scelta
@app.route("/genera_immagine", methods=["POST"])
def genera_immagine():
    data = request.get_json()
    proposta = data.get("proposta")

    if not proposta:
        return jsonify({"errore": "Proposta non fornita"}), 400

    formato = proposta["formati"][0]

    prompt_ai = f"""
Crea un template social {formato['formato']} di dimensioni {formato['dimensione']}, 
con sfondo {formato['tipo_sfondo']} di colore {formato['sfondo_colore']}, 
in stile {proposta['mood_visivo']}.

Headline: "{formato['headline']}"
CTA: "{formato['cta']}"
Font headline: {formato['font_headline']}
Font CTA: {formato['font_cta']}

Elementi decorativi: {", ".join(formato['elementi_grafici'])}.
Layout ordinato, armonioso e professionale. Testo in italiano.
"""

    img = client.images.generate(
        model="dall-e-3",
        prompt=prompt_ai,
        size="1024x1024",
        n=1
    )

    return jsonify({
        "prompt_usato": prompt_ai.strip(),
        "immagine_url": img.data[0].url
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
