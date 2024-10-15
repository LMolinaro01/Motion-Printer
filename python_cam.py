import serial
import time
import base64
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import customtkinter as ctk
import io
from datetime import datetime, timedelta
import threading
import os

ser = None
captura_ativa = False 
pasta_salvar = ""
preview_label = None
btn_salvar = None
btn_tirar_novamente = None
btn_sair = None
temporizador_label = None
timer_thread = None

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

def abrir_janela_agendar_captura():
    global janela_agendar
    janela_agendar = ctk.CTkToplevel(app)
    janela_agendar.geometry("400x300")
    janela_agendar.title("Agendar Captura")

    # Label e Entry para data e hora
    data_label = ctk.CTkLabel(janela_agendar, text="Data (DD/MM/AAAA):") 
    data_label.pack(pady=5)

    global data_entry
    data_entry = ctk.CTkEntry(janela_agendar)
    data_entry.pack(pady=5)
    data_entry.bind("<KeyRelease>", formatar_data)  # Formatação automática de data

    hora_label = ctk.CTkLabel(janela_agendar, text="Hora (HH:MM):") 
    hora_label.pack(pady=5)

    global hora_entry
    hora_entry = ctk.CTkEntry(janela_agendar)
    hora_entry.pack(pady=5)
    hora_entry.bind("<KeyRelease>", formatar_hora)  # Formatação automática de hora

    # Botão para confirmar agendamento
    global btn_agendar
    btn_agendar = ctk.CTkButton(janela_agendar, text="Confirmar Agendamento", command=confirmar_agendamento)
    btn_agendar.pack(pady=10)

    # Botão para voltar para a janela principal
    btn_voltar = ctk.CTkButton(janela_agendar, text="Voltar", command=janela_agendar.destroy)
    btn_voltar.pack(pady=5)

def formatar_data(event):
    text = data_entry.get()
    if len(text) == 2 or len(text) == 5:
        data_entry.insert(len(text), "/")  # Adiciona "/" após dia e mês

def formatar_hora(event):
    text = hora_entry.get()
    if len(text) == 2:
        hora_entry.insert(len(text), ":")  # Adiciona ":" após horas

def confirmar_agendamento():
    global captura_ativa, timer_thread
    captura_ativa = True
    escolher_pasta_salvar()  # Escolher a pasta antes de agendar a captura
    if not pasta_salvar:
        return  # Cancela a operação se o usuário não escolher a pasta

    data_str = data_entry.get()
    hora_str = hora_entry.get()

    try:
        # Combinar data e hora em um único objeto datetime
        data_hora_str = f"{data_str} {hora_str}"
        data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M")

        # Calcular a diferença até o horário agendado
        agora = datetime.now()
        if data_hora <= agora:
            messagebox.showerror("Erro", "A data e hora devem ser futuras.")
            return

        # Calcular o tempo até o agendamento
        tempo_ate_agendamento = (data_hora - agora).total_seconds()

        # Desabilitar botões e entradas durante o agendamento
        btn_agendar.configure(state='disabled')  # Desabilitar o botão após confirmar
        data_entry.configure(state='disabled')
        hora_entry.configure(state='disabled')

        # Iniciar o timer na tela de agendamento
        start_timer(tempo_ate_agendamento)

        threading.Timer(tempo_ate_agendamento, iniciar_captura_agendada).start()
        messagebox.showinfo("Agendamento Confirmado", f"Captura agendada para: {data_hora_str}")

    except ValueError:
        messagebox.showerror("Erro", "Formato de data ou hora inválido.")

def start_timer(tempo):
    global temporizador_label, timer_thread
    temporizador_label = ctk.CTkLabel(janela_agendar, text="", font=("Arial", 16))
    temporizador_label.pack(pady=20)

    def update_timer():
        nonlocal tempo
        while tempo > 0:
            mins, secs = divmod(int(tempo), 60)
            temporizador_label.configure(text=f"Tempo até a captura: {mins:02}:{secs:02}")
            time.sleep(1)
            tempo -= 1

        temporizador_label.configure(text="Captura em Andamento...")
        finalizar_agendamento()

    timer_thread = threading.Thread(target=update_timer)
    timer_thread.start()

def finalizar_agendamento():
    global captura_ativa
    captura_ativa = False

    # Habilitar botões e entradas após a captura
    btn_agendar.configure(state='normal')
    data_entry.configure(state='normal')
    hora_entry.configure(state='normal')

def iniciar_captura_agendada():
    global captura_ativa
    if captura_ativa:
        for _ in range(5):  # Tirar 5 fotos
            image_data = tirar_foto()
            if image_data:
                image = Image.open(io.BytesIO(image_data))
                salvar_automatico(image)
            time.sleep(2)  # Intervalo de 2 segundos entre as fotos

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

# Botão para agendar captura
btn_agendar = ctk.CTkButton(app, text="Agendar Captura", command=abrir_janela_agendar_captura)
btn_agendar.pack(padx=50, pady=10, fill='x')

# Botão para capturar uma foto única
btn_capturar = ctk.CTkButton(app, text="Capturar Imagem", command=tirar_foto_unica)
btn_capturar.pack(padx=50, pady=10, fill='x')

app.mainloop()
