#Comando para testar no cmd:

#python -m unittest test_snaplink.py


import unittest
from unittest.mock import MagicMock, patch
import io
import base64
from datetime import datetime
from PIL import Image
from python_cam import adicionar_data_hora, mostrar_preview, conectar_arduino, tirar_foto
import tkinter as tk


class TestSnapLink(unittest.TestCase):
    def setUp(self):
        """Configura uma imagem para testes."""
        self.image = Image.new('RGB', (100, 100), color='blue')

        self.root = tk.Tk()
        self.root.withdraw()  # Oculta a janela principal

    def tearDown(self):
        """Fecha a janela Tkinter após os testes."""
        self.root.destroy()  # Fecha a janela e libera recursos

    def test_adicionar_data_hora(self):
        """Testa se a data e hora são adicionadas corretamente à imagem."""
        adicionar_data_hora(self.image)

        # Verifica se houve alteração na imagem (simplesmente comparando o conteúdo).
        imagem_esperada = Image.new('RGB', (100, 100), color='blue')
        self.assertNotEqual(self.image.tobytes(), imagem_esperada.tobytes())

    @patch('python_cam.serial.Serial')
    def test_conectar_arduino(self, mock_serial):
        """Testa a conexão com o Arduino."""
        mock_serial.return_value.is_open = True

        conectado = conectar_arduino()
        self.assertTrue(conectado)
        mock_serial.assert_called_with('COM7', 115200)

    @patch('python_cam.serial.Serial')
    @patch('python_cam.mostrar_preview')
    def test_tirar_foto(self, mock_mostrar_preview, mock_serial):
        """Testa o processo de captura e decodificação da imagem."""
        mock_serial_instance = mock_serial.return_value
        mock_serial_instance.is_open = True

        # Simula a resposta do Arduino com dados base64 válidos.
        imagem_base64 = base64.b64encode(self.image.tobytes()).decode('utf-8')
        mock_serial_instance.readline.side_effect = [
            b'#Inicio:\n',
            imagem_base64.encode('utf-8'),
            b'#Fim\n'
        ]

        tirar_foto()  # Executa a função original.

        # Verifica se `mostrar_preview` foi chamada com a imagem decodificada.
        mock_mostrar_preview.assert_called_once()
        args = mock_mostrar_preview.call_args[0]
        self.assertIsInstance(args[0], bytes)  # Verifica se o argumento é um objeto bytes.

    @patch('tkinter.messagebox.showinfo')
    def test_mensagem_conexao_arduino(self, mock_showinfo):
        """Testa se a mensagem de sucesso é exibida após conectar com o Arduino."""
        conectar_arduino()
        mock_showinfo.assert_called_with("Conexão", "Conexão com Arduino estabelecida!")


if __name__ == '__main__':
    unittest.main()
