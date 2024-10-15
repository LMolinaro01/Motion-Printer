import serial
import time
import base64
from tkinter import messagebox, filedialog, Toplevel
from PIL import Image, ImageTk, ImageDraw, ImageFont
import customtkinter as ctk
import io
from datetime import datetime

ser = None

def conectar_arduino():
    global ser
    try:
        ser = serial.Serial('COM7', 115200)
        time.sleep(2)
        messagebox.showinfo("Conexão", "Conexão com Arduino estabelecida!")
        return True
    except Exception as e:
        return False

def tentar_conectar_novamente():
    if conectar_arduino():
        return
    else:
        retry = messagebox.askretrycancel("Erro de Conexão", "Erro ao conectar com o Arduino. Deseja tentar novamente?")
        if retry:
            tentar_conectar_novamente()
        else:
            app.quit()

def mostrar_preview(image_data):
    preview_window = Toplevel(app)
    preview_window.title("Prévia da Imagem")
    
    image = Image.open(io.BytesIO(image_data))
    photo = ImageTk.PhotoImage(image)
    
    label = ctk.CTkLabel(preview_window, image=photo)
    label.image = photo
    label.pack(padx=10, pady=10)
    
    def confirmar_salvar():
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            adicionar_data_hora(image)
            image.save(file_path)
            messagebox.showinfo("Sucesso", f"Imagem salva com sucesso em: {file_path}")
        else:
            messagebox.showwarning("Cancelado", "O usuário cancelou a operação de salvamento.")
        preview_window.destroy()

    def tirar_novamente():
        preview_window.destroy()
        tirar_foto()

    btn_salvar = ctk.CTkButton(preview_window, text="Salvar Imagem", command=confirmar_salvar)
    btn_salvar.pack(side='left', padx=20, pady=10)

    btn_tirar_novamente = ctk.CTkButton(preview_window, text="Tirar Novamente", command=tirar_novamente)
    btn_tirar_novamente.pack(side='right', padx=20, pady=10)

def adicionar_data_hora(image):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    largura, altura = image.size
    margem = 10
    texto_posicao = (largura - margem - 100, altura - margem - 20)
    cor_texto = (255, 255, 255)
    
    draw.text(texto_posicao, data_hora, font=font, fill=cor_texto)

def tirar_foto():
    global ser
    if ser and ser.is_open:
        try:
            ser.write(b't')
            time.sleep(1)
            
            base64_data = ""
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line == "#Inicio:":
                    base64_data = ""
                elif line == "#Fim":
                    break
                else:
                    base64_data += line
            
            print("Imagem em Base64 recebida.")
            image_data = base64.b64decode(base64_data)
            mostrar_preview(image_data)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar imagem: {e}")
    else:
        messagebox.showerror("Erro", "Arduino não conectado.")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("500x400")
app.title("SnapLink")

tentar_conectar_novamente()

label_titulo = ctk.CTkLabel(app, text="Snap Link", font=("Consolas bold", 24))
label_titulo.pack(padx=10, pady=10)

btn_capturar = ctk.CTkButton(app, text="Capturar Imagem", command=tirar_foto)
btn_capturar.pack(pady=20, padx=20, fill='x')

app.mainloop()

