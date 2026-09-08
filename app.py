from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator
import requests
import re

app = Flask(__name__, static_folder="static", template_folder="templates")


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# CHECK IF TEXT IS ROMANIZED
# --------------------------------------------------

def is_romanized(text):
    letters = re.findall(r"[A-Za-z]", text)
    if not letters:
        return False
    return (len(letters) / max(len(text), 1)) > 0.5


# --------------------------------------------------
# TRANSLITERATION (GOOGLE INPUT TOOLS)
# --------------------------------------------------

def transliterate_text(text, language):
    transliteration_codes = {
        "te": "te-t-i0-und",
        "hi": "hi-t-i0-und",
        "ta": "ta-t-i0-und",
        "kn": "kn-t-i0-und",
        "ml": "ml-t-i0-und",
        "bn": "bn-t-i0-und",
        "mr": "mr-t-i0-und",
        "gu": "gu-t-i0-und",
        "pa": "pa-t-i0-und",
        "ur": "ur-t-i0-und",
        "ne": "ne-t-i0-und",
        "si": "si-t-i0-und",
        "or": "or-t-i0-und"
    }

    if language not in transliteration_codes:
        return text

    url = "https://inputtools.google.com/request"
    params = {
        "text": text,
        "itc": transliteration_codes[language],
        "num": 1,
        "cp": 0,
        "cs": 1,
        "ie": "utf-8",
        "oe": "utf-8",
        "app": "translate"
    }

    try:
        response = requests.get(url, params=params, timeout=6)
        if response.status_code == 200:
            result = response.json()
            if (
                isinstance(result, list)
                and len(result) >= 2
                and result[0] == "SUCCESS"
                and len(result[1]) > 0
                and len(result[1][0]) > 1
                and len(result[1][0][1]) > 0
            ):
                return result[1][0][1][0]
    except Exception as error:
        print(f"Transliteration skipped: {error}")

    return text


# --------------------------------------------------
# TRANSLATE ROUTE
# --------------------------------------------------

@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data received."}), 400

        text = data.get("text", "").strip()
        source = data.get("source", "en")
        target = data.get("target", "hi")

        if not text:
            return jsonify({"success": False, "error": "Please enter text to translate."}), 400

        if source == target:
            return jsonify({"success": False, "error": "Source and target languages must be different."}), 400

        # Transliterate Romanized Indic text if applicable
        romanized_languages = {"te", "hi", "ta", "kn", "ml", "bn", "mr", "gu", "pa", "ur", "ne", "si", "or"}
        if source in romanized_languages and is_romanized(text):
            text = transliterate_text(text, source)

        # Primary translation using GoogleTranslator
        try:
            translated_text = GoogleTranslator(source=source, target=target).translate(text)
        except Exception:
            translated_text = GoogleTranslator(source="auto", target=target).translate(text)

        if not translated_text:
            return jsonify({"success": False, "error": "Unable to produce translation."}), 500

        return jsonify({
            "success": True,
            "translation": translated_text
        })

    except Exception as error:
        print(f"Translation Error: {error}")
        return jsonify({"success": False, "error": str(error)}), 500


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)