import requests
from flask import Flask
from instagrapi import Client

app = Flask(__name__)

SESSION_ID = "43150243824%3AcR1T3NOTsJ6JM2%3A10%3AAYnVQVbMhJhk-O-O6rquDs7KVufVeB895_8Vs1axbw"
GEMINI_API_KEY = "AQ.Ab8RN6LMgSsixB8zwgT346n-kT4TZjesdtWYUz8ptBCR6szurg"


def ask_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Sen Instagram sahifaning yordamchisisan. O'zbek tilida, qisqa, samimiy va tushunarli javob ber. Xabar: {text}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    try:
        res = requests.post(url, json=payload, timeout=15).json()
        return res["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return "Salom! Savolingiz uchun rahmat, tez orada javob beramiz."


@app.route("/")
@app.route("/api/check")
def check_instagram():
    try:
        cl = Client()
        cl.login_by_sessionid(SESSION_ID)
        my_id = str(cl.user_id)
        replied_count = 0

        threads = cl.direct_threads(amount=5)
        for thread in threads:
            if not thread.messages:
                continue
            last_msg = thread.messages[0]
            if str(last_msg.user_id) != my_id and last_msg.text:
                reply = ask_gemini(last_msg.text)
                cl.direct_send(reply, thread_ids=[thread.id])
                replied_count += 1

        medias = cl.user_medias(cl.user_id, amount=3)
        for media in medias:
            comments = cl.media_comments(media.id, amount=5)
            for comment in comments:
                if str(comment.user.pk) != my_id:
                    already_replied = any(
                        str(c.user.pk) == my_id and f"@{comment.user.username}" in c.text
                        for c in comments
                    )
                    if not already_replied:
                        reply = ask_gemini(comment.text)
                        cl.media_comment(
                            media.id,
                            f"@{comment.user.username} {reply}",
                            replied_to_comment_id=comment.pk
                        )
                        replied_count += 1

        return f"OK: {replied_count} ta javob yuborildi", 200
    except Exception as e:
        return f"Xatolik: {str(e)}", 500
