from flask import Flask, request, Response, send_file
from twilio.twiml.voice_response import VoiceResponse, Gather
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
load_dotenv()

from elevenlabs import VoiceSettings
import os

app = Flask(__name__)
client = ElevenLabs(api_key=os.environ["ELEVEN_API_KEY"])

messages = {
    "1": ("Hello. I am MFriend. You are not alone. I am here to listen.", "en-US", "JUAXJdmq5qos1R1etewe"),
    "2": ("Hola. Soy tu amiga MFriend. No estás solo. Estoy aquí para escucharte.", "es", "JUAXJdmq5qos1R1etewe"),
    "3": ("안녕하세요. 저는 MFriend입니다. 당신은 혼자가 아닙니다. 저는 항상 여기 있어요.", "ko", "JUAXJdmq5qos1R1etewe"),
    "4": ("مرحباً، أنا صديقك MFriend. أنت لست وحدك. أنا هنا لأستمع إليك.", "ar", "JUAXJdmq5qos1R1etewe"),
    "5": ("Bonjour. Je suis MFriend. Tu n'es pas seul. Je suis là pour t'écouter.", "fr", "JUAXJdmq5qos1R1etewe"),
    "6": ("Hallo. Ich bin MFriend. Du bist nicht allein. Ich bin hier, um zuzuhören.", "de", "JUAXJdmq5qos1R1etewe"),
    "7": ("Olá. Eu sou o MFriend. Você não está sozinho. Estou aqui para ouvir você.", "pt", "JUAXJdmq5qos1R1etewe"),
    "8": ("Привет. Я твой друг MFriend. Ты не один. Я здесь, чтобы выслушать тебя.", "ru", "JUAXJdmq5qos1R1etewe"),
    "9": ("Привіт. Я твій друг MFriend. Ти не один. Я тут, щоб тебе вислухати.", "uk", "JUAXJdmq5qos1R1etewe"),
    "10": ("Xin chào. Tôi là MFriend. Bạn không đơn độc. Tôi ở đây để lắng nghe bạn.", "vi", "JUAXJdmq5qos1R1etewe"),
    "11": ("नमस्ते। मैं MFriend हूँ। आप अकेले नहीं हैं। मैं आपकी बात सुनने के लिए यहाँ हूँ।", "hi", "JUAXJdmq5qos1R1etewe"),
    "12": ("こんにちは。私はMFriendです。あなたは一人じゃありません。私はあなたの話を聞くためにここにいます。", "ja", "JUAXJdmq5qos1R1etewe"),
    "13": ("你好，我是你的朋友MFriend。你并不孤单，我在这里倾听你。", "zh", "JUAXJdmq5qos1R1etewe"),
    "14": ("Selam. Ben MFriend. Yalnız değilsin. Seni dinlemek için buradayım.", "tr", "JUAXJdmq5qos1R1etewe"),
    "15": ("Halo. Saya MFriend. Kamu tidak sendiri. Saya di sini untuk mendengarkanmu.", "id", "JUAXJdmq5qos1R1etewe"),
    "0": ("Let's repeat the menu. For English, press 1. Para español, marque 2. 한국어는 3번. العربية، اضغط 4...", "en-US", "JUAXJdmq5qos1R1etewe"),
    "fallback": ("Sorry, I didn’t get that. Let’s try again. For English, press 1. Para español, marque 2...", "en-US", "JUAXJdmq5qos1R1etewe")
}

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = response.gather(num_digits=2, action="/handle-language", method="POST")

    gather.say(
       "Welcome to MFriend. "
        "English, press 1. "
        "Español, marque 2. "
        "한국어는 3번을 누르세요. "
        "العربية، اضغط على الرقم 4. "
        "日本語は5番を押してください。 "
        "中文，请按6号键。 "
        "हिंदी के लिए 7 दबाएँ। "
        "Tiếng Việt, bấm phím 8. "
        "Русский, нажмите цифру 9. "
        "Українська, натисніть 10. "
        "Deutsch, drücken Sie die 11. "
        "Français, appuyez sur le 12. "
        "Türkçe için 13’e basın. "
        "Português, pressione o número 14. "
        "Bahasa Indonesia, tekan angka 15. "
        "To repeat this menu, press 0.",
        language="en-US"
    )

    
    response.redirect("/voice")
    return Response(str(response), mimetype="application/xml")


@app.route("/handle-language", methods=["POST"])
def handle_language():
    digit_pressed = request.form.get("Digits", "")
    response = VoiceResponse()

    if digit_pressed in messages:
        text, lang, voice_id = messages[digit_pressed]
    else:
        text, lang, voice_id = messages["fallback"]

    audio = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_multilingual_v2",
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.5)
    )

    filename = f"static/response_{digit_pressed if digit_pressed in messages else 'fallback'}.mp3"
    with open(filename, "wb") as f:
        f.write(audio)

    response.play(request.host_url + filename)
    if digit_pressed == "0" or digit_pressed not in messages:
        response.redirect("/voice")
    return Response(str(response), mimetype="application/xml")

@app.route("/static/<filename>")
def serve_audio(filename):
    return send_file(os.path.join("static", filename), mimetype="audio/mpeg")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5050))  # fallback to 5050 for local dev
    app.run(host="0.0.0.0", port=port)

