import serial
import time
import base64
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import customtkinter as ctk
import io
from datetime import datetime
import threading
import os

ser = None
captura_ativa = False 
pasta_salvar = ""
preview_label = None
btn_salvar = None
btn_tirar_novamente = None
btn_sair = None

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
    global preview_label, btn_salvar, btn_tirar_novamente, btn_sair
    
    image = Image.open(io.BytesIO(image_data))
    photo = ImageTk.PhotoImage(image)
    
    if preview_label is None:
        preview_label = ctk.CTkLabel(app, image=photo, text="") 
        preview_label.image = photo
        preview_label.pack(padx=10, pady=10)
    else:
        preview_label.configure(image=photo)
        preview_label.image = photo

    if btn_salvar is None:
        btn_salvar = ctk.CTkButton(app, text="Salvar Imagem", command=lambda: confirmar_salvar(image))
        btn_salvar.pack(padx=50, pady=10, fill='x')

    if btn_tirar_novamente is None:
        btn_tirar_novamente = ctk.CTkButton(app, text="Tirar Novamente", command=tirar_foto_unica)
        btn_tirar_novamente.pack(padx=50, pady=10, fill='x')

    if btn_sair is None:
        btn_sair = ctk.CTkButton(app, text="Sair do Programa", command=app.destroy)
        btn_sair.pack(pady=15)

def confirmar_salvar(image):
    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", 
                                             initialfile="imagem_capturada",
                                             filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
    if file_path:
        adicionar_data_hora(image)
        image.save(file_path)
        messagebox.showinfo("Sucesso", f"Imagem salva com sucesso em: {file_path}")
    else:
        messagebox.showwarning("Cancelado", "O usuário cancelou a operação de salvamento.")

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
            return image_data

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar imagem: {e}")
    else:
        messagebox.showerror("Erro", "Arduino não conectado.")
    return None

def tirar_foto_unica():
    image_data = tirar_foto()
    if image_data:
        mostrar_preview(image_data)

def capturar_fotos_continuamente(intervalo):
    global captura_ativa
    while captura_ativa:
        image_data = tirar_foto()
        if image_data:
            image = Image.open(io.BytesIO(image_data))
            salvar_automatico(image)
        time.sleep(intervalo)  # Intervalo entre cada foto

def salvar_automatico(image):
    global pasta_salvar
    # Gera o nome do arquivo baseado na data e hora
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"foto_{timestamp}.jpg"
    file_path = os.path.join(pasta_salvar, file_name)

    # Adiciona data e hora na imagem e salva automaticamente
    adicionar_data_hora(image)
    image.save(file_path)
    print(f"Imagem salva automaticamente em: {file_path}")

def abrir_janela_temporizador():
    global janela_temporizador
    janela_temporizador = ctk.CTkToplevel(app)
    janela_temporizador.geometry("400x300")
    janela_temporizador.title("Captura com Temporizador")

    # Label e Entry para intervalo do temporizador
    temporizador_label = ctk.CTkLabel(janela_temporizador, text="Intervalo do Temporizador:") 
    temporizador_label.pack(pady=5)

    global temporizador_intervalo_entry
    temporizador_intervalo_entry = ctk.CTkEntry(janela_temporizador)
    temporizador_intervalo_entry.pack(pady=5)

    # ComboBox para selecionar a unidade de tempo
    global unidade_temporizador
    unidade_temporizador = ctk.CTkComboBox(janela_temporizador, values=["Segundos", "Minutos", "Horas"])
    unidade_temporizador.set("Segundos")  # Padrão é "Segundos"
    unidade_temporizador.pack(pady=5)

    # Botão para iniciar captura de imagens
    btn_iniciar_captura = ctk.CTkButton(janela_temporizador, text="Iniciar Captura", command=iniciar_captura_temporizador)
    btn_iniciar_captura.pack(padx=50, pady=10, fill='x')

    # Botão para parar captura de imagens
    btn_parar_captura = ctk.CTkButton(janela_temporizador, text="Parar Captura", command=parar_captura_temporizador)
    btn_parar_captura.pack(padx=50, pady=10, fill='x')

    # Botão para voltar para a janela principal
    btn_voltar = ctk.CTkButton(janela_temporizador, text="Voltar", command=janela_temporizador.destroy)
    btn_voltar.pack(pady=15)

def iniciar_captura_temporizador():
    global captura_ativa
    captura_ativa = True
    escolher_pasta_salvar()  # Escolhe a pasta antes de iniciar a captura
    if not pasta_salvar:
        return  # Cancela a operação se o usuário não escolher a pasta

    # Desabilitar o ComboBox durante a captura
    unidade_temporizador.configure(state='disabled')

    # Converte o intervalo para segundos
    intervalo = int(temporizador_intervalo_entry.get())
    unidade = unidade_temporizador.get()

    if unidade == "Minutos":
        intervalo *= 60  # Converte minutos para segundos
    elif unidade == "Horas":
        intervalo *= 3600  # Converte horas para segundos

    threading.Thread(target=capturar_fotos_continuamente, args=(intervalo,)).start()

def parar_captura_temporizador():
    global captura_ativa
    captura_ativa = False
    messagebox.showinfo("Captura Parada", "A captura de fotos foi parada.")

    # Reabilitar o ComboBox ao parar a captura
    unidade_temporizador.configure(state='normal')

def escolher_pasta_salvar():
    global pasta_salvar
    pasta_salvar = filedialog.askdirectory()
    if not pasta_salvar:
        messagebox.showwarning("Nenhuma pasta", "Você não selecionou nenhuma pasta. As fotos não serão salvas automaticamente.")

# Janela principal
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("500x650")
app.title("SnapLink")

tentar_conectar_novamente()

label_titulo = ctk.CTkLabel(app, text="Snap Link", font=("Consolas bold", 24))
label_titulo.pack(padx=10, pady=10)


# Botão para abrir a janela de captura com temporizador
btn_temporizador = ctk.CTkButton(app, text="Captura com Temporizador", command=abrir_janela_temporizador)
btn_temporizador.pack(padx=50, pady=10, fill='x')

# Botão para capturar uma foto única
btn_capturar = ctk.CTkButton(app, text="Capturar Imagem", command=tirar_foto_unica)
btn_capturar.pack(padx=50, pady=10, fill='x')

app.mainloop()
