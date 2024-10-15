import serial
import time
import base64
from tkinter import messagebox, filedialog, Toplevel
from PIL import Image, ImageTk
import customtkinter as ctk
import io

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

def mostrar_preview(image_data):
    """ Mostra uma prévia da imagem capturada """
    # Cria uma nova janela para o preview
    preview_window = Toplevel(app)
    preview_window.title("Prévia da Imagem")
    
    # Converte a string base64 para uma imagem
    image = Image.open(io.BytesIO(image_data))
    
    # Converte a imagem para um formato que pode ser exibido no Tkinter
    photo = ImageTk.PhotoImage(image)
    
    label = ctk.CTkLabel(preview_window, image=photo)
    label.image = photo  # Mantém uma referência para evitar coleta de lixo
    label.pack(padx=10, pady=10)
    
    def confirmar_salvar():
        """ Pergunta ao usuário onde salvar a imagem e salva a imagem """
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", 
                                                 filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if file_path:
            # Salva a imagem no caminho selecionado pelo usuário
            image.save(file_path)
            messagebox.showinfo("Sucesso", f"Imagem salva com sucesso em: {file_path}")
        else:
            messagebox.showwarning("Cancelado", "O usuário cancelou a operação de salvamento.")
        preview_window.destroy()  # Fecha a janela de prévia

    def tirar_novamente():
        """ Fecha a janela de preview e tira uma nova foto """
        preview_window.destroy()
        tirar_foto()  # Chama a função para tirar a foto novamente

    # Botões para salvar ou tirar novamente
    btn_salvar = ctk.CTkButton(preview_window, text="Salvar Imagem", command=confirmar_salvar)
    btn_salvar.pack(side='left', padx=20, pady=10)

    btn_tirar_novamente = ctk.CTkButton(preview_window, text="Tirar Novamente", command=tirar_novamente)
    btn_tirar_novamente.pack(side='right', padx=20, pady=10)

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
            
            # Transforma a base64_data em uma string e imprime no console
            print("Imagem em Base64 recebida.")
            
            # Decodifica a string base64 para bytes de imagem
            image_data = base64.b64decode(base64_data)

            # Mostra a prévia da imagem antes de salvar
            mostrar_preview(image_data)

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
