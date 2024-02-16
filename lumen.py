import openai
import random
import pyttsx3
import pygame
import threading
import speech_recognition as sr

from actions.music_player import play_playlist

# OpenAPI key is needed to ask Lumen question.
# Not needed for requests.
openai.api_key = ""
model = "text-davinci-002"

# Text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
engine.setProperty('voice', voices[2].id)
engine.setProperty('rate', 210)

# Speech-recognizer
speech = sr.Recognizer()
mic = sr.Microphone(device_index=1)

# Music-player
pygame.mixer.init()

# Random number, used to get a random greeting/goodbye from Lumen.
rng = random.randint(0, 5)

greetings = ["Hey", "Good Day! How may I be of assistance", "What's up?",
             "Yo bro", "Hello, how are you today?", "Hello there. How can I help you today?"]
goodbyes = ["Until next time", "Sayonara", "Glad to be of service", "Goodbye", "See you", "Bye"]

# Saying "Lumen" and one of the exit_inputs shuts down the program.
exit_inputs = ["goodbye", "that will be all", "good night", "go to sleep"]

# Prompt for AI
initial_request = "From now on you are called Lumen, keep answers as short as possible."


def main():
    lumen_speak(get_greeting())

    while True:
        question = get_question()
        if question is None:
            continue
        if question in exit_inputs:
            lumen_speak(get_goodbye())
            print("Exiting program now")
            break
        elif "set" in question and "timer" in question:
            if "minutes" in question:
                minutes_index = question.index("minutes")
                minutes = int(question[question.rfind(" ", 0, minutes_index-1) + 1:minutes_index])
                lumen_speak(f"Setting timer for {minutes} minutes")
                print("Timer set")
                timer = threading.Timer(minutes*60, timer_callback)
                timer.start()
            elif "minute" in question:
                lumen_speak("Setting timer for one minute")
                print("Timer set")
                timer = threading.Timer(60, timer_callback)
                timer.start()
            elif "seconds" in question:
                seconds_index = question.index("seconds")
                seconds = int(question[question.rfind(" ", 0, seconds_index-1) + 1:seconds_index])
                lumen_speak(f"Setting timer for {seconds} seconds")
                print("Timer set")
                timer = threading.Timer(seconds, timer_callback)
                timer.start()
        elif "play" in question and "random" in question:
            lumen_speak("Playing a random song")
            folder_path = "songs/"
            play_playlist(folder_path)
            print("Playing song")
        else:
            prompt = initial_request + " " + question
            try:
                response, tokens_used = request(prompt)
                lumen_speak(response)
            except openai.error.AuthenticationError:
                lumen_speak("No API key")
                continue
            print("Tokens used: " + str(tokens_used))


def request(question):
    response = openai.Completion.create(
        engine=model,
        prompt=question,
        max_tokens=100,
        temperature=1.0,
    )
    return str.strip(response['choices'][0]['text']), response['usage']['total_tokens']


def get_question():
    audio = None
    with mic as source:
        speech.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening")
        try:
            audio = speech.listen(source, timeout=8, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("Timeout occurred while listening.")
        except sr.UnknownValueError:
            print("Unable to recognize speech.")
        except sr.RequestError as e:
            print(f"Error: {str(e)}")

        print("Done Listening")

    if audio is None:
        return None

    try:
        question = speech.recognize_google(audio)
        print(question)
        if "lumen" in question.lower():
            return question.lower().replace("lumen", "").strip()
        if "stop the song" in question.lower():
            pygame.mixer.music.stop()
            return None
        else:
            return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print("Error: {0}".format(e))
    return None


def lumen_speak(text):
    engine.startLoop(False)
    engine.say(text)
    engine.iterate()
    engine.endLoop()


def get_greeting():
    return random.choice(greetings)


def get_goodbye():
    return random.choice(goodbyes)


def timer_callback():
    lumen_speak("Ding Ding Ding Ding, Ding Ding Ding Ding, Timer is done!")


def play_song(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


if __name__ == "__main__":
    main()
