import serial
import time
import base64
from tkinter import messagebox, filedialog
import customtkinter as ctk

# Configuração da porta serial
ser = None

def conectar_arduino():
    global ser
    try:
        ser = serial.Serial('COM7', 115200)
        time.sleep(2)  # Estabilizar conexão
        messagebox.showinfo("Conexão", "Conexão com Arduino estabelecida!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar com o Arduino: {e}")

def capturar_imagem():
    global ser
    if ser is None:
        messagebox.showwarning("Atenção", "Arduino não conectado.")
        return

    try:
        # Enviar comando 'a' para capturar imagem
        ser.write(b'a')
        time.sleep(0.5)

        base64_data = ""
        start_time = time.time()

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"Recebido: {line}")  # Debug

                if "Success" in line:
                    break
                else:
                    base64_data += line

            # Timeout após 20 segundos
            if time.time() - start_time > 20:
                messagebox.showerror("Erro", "Tempo limite atingido ao receber a imagem.")
                return

        # Ajuste de padding da base64
        base64_data += '=' * ((4 - len(base64_data) % 4) % 4)

        try:
            image_data = base64.b64decode(base64_data)

            # Verificar se a imagem está vazia
            if len(image_data) == 0:
                messagebox.showerror("Erro", "Imagem decodificada vazia.")
                return

            # Perguntar onde salvar a imagem
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", 
                                                     filetypes=[("JPEG files", "*.jpg"), 
                                                                ("All files", "*.*")])
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(image_data)
                messagebox.showinfo("Sucesso", f"Imagem recebida e salva como '{file_path}'")
            else:
                messagebox.showwarning("Atenção", "Nenhum caminho de arquivo selecionado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao decodificar a imagem: {e}")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro durante a captura: {e}")

# Interface CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("300x200")
app.title("Interface Arduino - Captura de Imagem")

# Botão para conectar com o Arduino
btn_conectar = ctk.CTkButton(app, text="Conectar Arduino", command=conectar_arduino)
btn_conectar.pack(pady=20)

# Botão para capturar imagem
btn_capturar = ctk.CTkButton(app, text="Capturar Imagem", command=capturar_imagem)
btn_capturar.pack(pady=20)

app.mainloop()
