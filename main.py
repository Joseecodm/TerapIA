import tkinter as tk
from tkinter import scrolledtext, messagebox
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import pyttsx3
from gpt4all import GPT4All
import shutil
import threading
import hashlib

# === Función para cifrar contraseñas ===
def cifrar_contraseña(contraseña):
    return hashlib.sha256(contraseña.encode('utf-8')).hexdigest()

# === Base de datos simulada ===
usuarios_validos = {
    "admin": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4",  # 1234
    "jose": "08a417d732e03b18797c81e6f9befd5ef3632f162c5b920e2bec64e89a2dce33"   # miclave
}

# === Ruta del modelo IA ===
RUTA_MODELO = "./model"

# === funciones principales ===
def grabar_audio(duracion=2, fs=16000):
    audio = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write("entrada.wav", fs, audio)

def transcribir_audio():
    if shutil.which("ffmpeg") is None:
        messagebox.showerror("Falta ffmpeg", "Instala ffmpeg y reinicia la app.")
        return "[ERROR: ffmpeg no instalado]"
    model = whisper.load_model("base")
    result = model.transcribe("entrada.wav", language="es")
    return result["text"]

def preguntar_ia(prompt):
    model = GPT4All("mistral", model_path=RUTA_MODELO, allow_download=False)
    with model.chat_session(system_prompt="Eres un psicólogo virtual empático que responde en español.") as chat:
        return chat.generate(prompt)

def hablar_texto(texto):
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)
    for voz in engine.getProperty('voices'):
        if "TTS_MS_ES-MX_SABINA_11.0" in voz.id:
            engine.setProperty('voice', voz.id)
            break
    else:
        print("⚠️ Voz Sabina no encontrada, se usará la predeterminada.")
    engine.say(texto)
    engine.runAndWait()

def ejecutar_flujo():
    canvas.itemconfig(boton_mic, fill="#ff0000")
    entrada_textbox.configure(state=tk.NORMAL)
    respuesta_textbox.configure(state=tk.NORMAL)
    entrada_textbox.delete("1.0", tk.END)
    respuesta_textbox.delete("1.0", tk.END)

    grabar_audio()
    entrada = transcribir_audio()
    entrada_textbox.insert("end", entrada)

    respuesta = preguntar_ia(entrada)
    respuesta_textbox.insert("end", respuesta)
    hablar_texto(respuesta)

    entrada_textbox.configure(state=tk.DISABLED)
    respuesta_textbox.configure(state=tk.DISABLED)
    canvas.itemconfig(boton_mic, fill="#2196f3")

def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = int((pantalla_ancho / 2) - (ancho / 2))
    y = int((pantalla_alto / 2) - (alto / 2))
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def hilo_flujo():
    threading.Thread(target=ejecutar_flujo).start()
    
# === Pantalla principal del psicólogo virtual ===
def abrir_ventana_principal():
    global ventana, canvas, boton_mic, entrada_textbox, respuesta_textbox

    ventana = tk.Tk()
    ventana.title("Psicólogo Virtual")
    centrar_ventana(ventana, 400, 550)  # centrar app principal
    ventana.configure(bg="#eeeeee")
    ventana.resizable(False, False)


    tk.Label(ventana, text="Psicólogo Virtual", bg="#eeeeee", font=("Arial", 16)).pack(pady=(15, 10))

    entrada_textbox = scrolledtext.ScrolledText(ventana, height=5, wrap=tk.WORD, font=("Arial", 10), bd=0, bg="white")
    entrada_textbox.pack(padx=20, pady=10, fill="x")
    entrada_textbox.configure(state=tk.DISABLED)

    canvas = tk.Canvas(ventana, width=100, height=100, bg="#eeeeee", highlightthickness=0)
    canvas.pack()

    boton_mic = canvas.create_oval(10, 10, 90, 90, fill="#2196f3", outline="")
    icono = canvas.create_text(50, 50, text="🎙", font=("Arial", 24))

    canvas.tag_bind(boton_mic, "<Button-1>", lambda e: hilo_flujo())
    canvas.tag_bind(icono, "<Button-1>", lambda e: hilo_flujo())

    respuesta_textbox = scrolledtext.ScrolledText(ventana, height=5, wrap=tk.WORD, font=("Arial", 10), bd=0, bg="white")
    respuesta_textbox.pack(padx=20, pady=10, fill="x")
    respuesta_textbox.configure(state=tk.DISABLED)

    boton_salir = tk.Button(
        ventana,
        text="Salir",
        font=("Arial", 12),
        bg="#d9534f",
        fg="white",
        relief="flat",
        command=ventana.destroy
    )
    boton_salir.pack(pady=(10, 20))

    ventana.mainloop()

# === Pantalla de login ===
def verificar_login():
    usuario = entry_usuario.get()
    contraseña = entry_contraseña.get()
    hash_ingresado = cifrar_contraseña(contraseña)

    if usuario in usuarios_validos and usuarios_validos[usuario] == hash_ingresado:
        messagebox.showinfo("Acceso correcto", f"Bienvenido {usuario}")
        login.destroy()
        abrir_ventana_principal()
    else:
        messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos")

# === Crear ventana de login ===
login = tk.Tk()
login.title("Inicio de sesión")
centrar_ventana(login, 300, 200)  # centrar login
login.resizable(False, False)

tk.Label(login, text="Usuario:", font=("Arial", 12)).pack(pady=5)
entry_usuario = tk.Entry(login, font=("Arial", 12))
entry_usuario.pack(pady=5)

tk.Label(login, text="Contraseña:", font=("Arial", 12)).pack(pady=5)
entry_contraseña = tk.Entry(login, show="*", font=("Arial", 12))
entry_contraseña.pack(pady=5)

btn_login = tk.Button(login, text="Ingresar", font=("Arial", 12), command=verificar_login, bg="#2196f3", fg="white")
btn_login.pack(pady=15)

login.mainloop()