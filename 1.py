import os
import requests
import pyttsx3
import pyaudio
import json
from vosk import Model, KaldiRecognizer


class VoiceAssistant:
    def __init__(self):
        self.model = Model("vosk-model-small-ru-0.22")
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # скорость
        self.engine.setProperty('volume', 0.9)  # громкость
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=8000)
        self.current_text = ""

    def listen(self):
        print("Слушаю...")
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                command = result.get('text', '').lower()
                if command:
                    print(f"Распознано: {command}")
                    return command

    def speak(self, text):
        print(f"Ассистент: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def get_text(self):
        try:
            response = requests.get("https://baconipsum.com/api/?type=all-meat¶s=3")
            self.current_text = "\n".join(response.json())
            self.speak("Текст успешно получен")
        except Exception as e:
            self.speak("Ошибка при получении текста")
            print(f"Ошибка: {e}")

    def read_text(self):
        if self.current_text:
            self.speak("Читаю текст")
            # читаем только первые 200 символов, чтобы не перегружать TTS
            self.engine.say(self.current_text[:200])
            self.engine.runAndWait()
        else:
            self.speak("Сначала получите текст командой создать")

    def save_html(self):
        if self.current_text:
            try:
                with open("text.html", "w", encoding="utf-8") as f:
                    f.write(self.current_text)
                self.speak("Текст сохранен как HTML")
            except Exception as e:
                self.speak("Ошибка при сохранении")
                print(f"Ошибка: {e}")
        else:
            self.speak("Сначала получите текст командой создать")

    def save_plain_text(self):
        if self.current_text:
            try:
                plain_text = self.current_text.replace("<p>", "\n").replace("</p>", "")
                plain_text = plain_text.replace("<h1>", "\n").replace("</h1>", "\n")
                plain_text = plain_text.replace("<h2>", "\n").replace("</h2>", "\n")

                with open("text.txt", "w", encoding="utf-8") as f:
                    f.write(plain_text)
                self.speak("Текст сохранен как обычный текст")
            except Exception as e:
                self.speak("Ошибка при сохранении")
                print(f"Ошибка: {e}")
        else:
            self.speak("Сначала получите текст командой создать")

    def run(self):
        self.speak("Голосовой ассистент запущен. Готов к работе.")

        while True:
            try:
                command = self.listen()

                if "создать" in command:
                    self.get_text()
                elif "прочесть" in command:
                    self.read_text()
                elif "сохранить html" in command:
                    self.save_html()
                elif "сохранить текст" in command:
                    self.save_plain_text()
                elif "выход" in command or "стоп" in command:
                    self.speak("Завершаю работу")
                    break
                else:
                    self.speak("Не распознал команду. Попробуйте еще раз.")
            except Exception as e:
                self.speak("Произошла ошибка")
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    if not os.path.exists("vosk-model-small-ru-0.22"):
        print("Пожалуйста, скачайте и распакуйте модель для распознавания речи")
        print("https://alphacephei.com/vosk/models")
        print("и поместите папку 'vosk-model-small-ru-0.22' в текущую директорию")
    else:
        assistant = VoiceAssistant()
        assistant.run()