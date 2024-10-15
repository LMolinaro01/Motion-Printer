import serial
import time
import base64
from tkinter import messagebox, filedialog
import customtkinter as ctk
import os

# Configuração da porta serial
ser = None

def conectar_arduino():
    global ser
    try:
        ser = serial.Serial('COM7', 115200)
        time.sleep(2)  # Tempo para estabilizar a conexão
        messagebox.showinfo("Conexão", "Conexão com Arduino estabelecida!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar com o Arduino: {e}")

def tirar_foto():
    global ser
    if ser and ser.is_open:
        try:
            ser.write(b't')  # Envia o comando para tirar foto
            time.sleep(1)  # Aguardar a captura da foto
            
            # Receber a imagem em base64
            base64_data = ""
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line == "#Inicio:":
                    base64_data = ""
                elif line == "#Fim":
                    break
                else:
                    base64_data += line
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar imagem: {e}")
    else:
        messagebox.showerror("Erro", "Arduino não conectado.")

# Configuração da interface gráfica
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("300x200")
app.title("Interface Arduino - Captura de Imagem")

btn_conectar = ctk.CTkButton(app, text="Conectar Arduino", command=conectar_arduino)
btn_conectar.pack(pady=20)

btn_capturar = ctk.CTkButton(app, text="Capturar Imagem", command=tirar_foto)
btn_capturar.pack(pady=20)

app.mainloop()
