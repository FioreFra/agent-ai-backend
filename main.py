
from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    nome_brand = data.get("nome_brand", "Brand")
    prodotti = data.get("prodotti", "prodotti decorativi")
    tone = data.get("tone", "romantico")
    obiettivi = data.get("obiettivi", "aumentare visibilità social")
    mood = data.get("mood", "shabby chic")
    colori = data.get("colori", "rosa cipria, bianco panna")
    formati = data.get("formati", ["Post Instagram"])

    # Prompt GPT
    prompt = f'''
Hai ricevuto queste informazioni:
- Brand: {nome_brand}
- Prodotti: {prodotti}
- Tone of voice: {tone}
- Obiettivi: {obiettivi}
- Mood visivo: {mood}
- Colori: {colori}
- Formati: {", ".join(formati)}

Genera una proposta creativa con:
- headline
- CTA
- colore sfondo
- tipo sfondo
- font headline
- font CTA
- elementi grafici
- specifica che il testo dev'essere in italiano
Restituisci il tutto in formato JSON.
    '''

    gpt = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )

    messaggio = gpt.choices[0].message.content

    # Prompt per immagine AI
    prompt_ai = f"""
Usa questo contenuto per generare un'immagine grafica social.
- Stile: {mood}
- Colori: {colori}
- Testo in italiano
- Headline e CTA: estratte dalla proposta
- Tema: {prodotti}
- Layout armonioso, romantico e professionale
- Evita elementi cosmetici o unghie
"""

    img = client.images.generate(
        model="dall-e-3",
        prompt=prompt_ai,
        size="1024x1024",
        n=1
    )
    img_url = img.data[0].url

    return jsonify({
        "proposta": messaggio,
        "immagine_url": img_url
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
