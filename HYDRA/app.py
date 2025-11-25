from flask import Flask, request, jsonify, render_template
from fuzzywuzzy import process
import json
import wikipedia
from symspellpy.symspellpy import SymSpell, Verbosity

sym_spell = SymSpell(max_dictionary_edit_distance=2)
sym_spell.load_dictionary("frequency_dictionary_en_82_765.txt", 0, 1) 

app = Flask(__name__)

with open("data.json", "r") as f:
    data = json.load(f)

INTENTS = ["timetable", "holiday", "roadmap", "career"]

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]


def extract_day(text):
        sen=text.split()
        for i in sen:
            match, score = process.extractOne(i, DAYS)

            if score > 80:
                return match
        return None

def get_intent(text):
    best_intent = None
    best_score = 0
    
    for word in text.split():
        match, score = process.extractOne(word, INTENTS)
        if score > best_score:
            best_intent = match
            best_score = score

    if best_score > 80:
        return best_intent
    
    return None

def is_greeting(text):
    GREETINGS = [
    "hi", "hello", "hey", "yo", "hai", "hii",
    "good morning", "good afternoon", "good evening"]
    text = text.lower()
    for g in GREETINGS:
        if g in text:
            return True
    return False

def is_thank(text):
    THANK=["thankyou",'thanks',"okay","bye","fine","thank you"]
    text = text.lower()
    for g in THANK:
        if g in text:
            return True
    return False

def ask_wikipedia(text):
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(text, sentences=2)
        return summary
    except:
        return "Sorry, I couldn't find anything about that."

def leetcode(text):
    KEYS=["placed","placement"]
    text = text.lower()
    for g in KEYS:
        if g in text:
            return True
    return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data_inp = request.get_json()
    user = data_inp.get("message", "")
    user_inp=user

    intent = get_intent(user)

    if intent == "timetable":
        day = extract_day(user)
        if day:
            timetable = data["timetable"][day]
            return jsonify({"reply": "\n".join(timetable)})
        else:
            ans = ask_wikipedia(user)

            if isinstance(ans, str):
                reply_text = ans
            else:
                reply_text = "\n".join(map(str, ans))

            return jsonify({"reply": reply_text})

    if intent == "holiday":
        return jsonify({"reply": "Holidays are: Jan 1, May 1, Aug 15, Oct 2, Dec 25"})

    if leetcode(user):
        return jsonify({"reply": "Roadmap:\n1. DSA\n2. Projects\n3. Internships\n4. Resume"})

    if intent == "career":
        return jsonify({"reply": "Focus on DSA + LeetCode + Projects + Internships"})
    
    if is_greeting(user):
        return jsonify({"reply": "Hello! How can I help you?"})
    
    if is_thank(user):
        return jsonify({"reply":"It's my plessure working with you"})

    else:
        ans = ask_wikipedia(user_inp.lower())

        if isinstance(ans, str):
            reply_text = ans
        else:
            reply_text = "\n".join(map(str, ans))

    return jsonify({"reply": reply_text})
if __name__ == "__main__":
    app.run(debug=True)