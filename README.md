
<h1 align = "center"> Snap Link </h1>

![{E4A940DA-8117-42A2-9D5A-A0B8C86AC63A}](https://github.com/user-attachments/assets/35107e40-9f5a-4660-b6cc-1246fae79de3)

## Descrição

![image](https://github.com/user-attachments/assets/5113eead-7c4e-4030-9f4b-7d13d71572a8)

SnapLink é uma aplicação Python que interage com um dispositivo Arduino e ESP32, permitindo a captura, visualização e salvamento de imagens com um carimbo de data e hora. A aplicação foi desenvolvida com uma interface gráfica moderna usando a biblioteca Custom Tkinter, proporcionando uma experiência de usuário intuitiva.

## Funcionalidades
- **Conexão Automática**: O programa tenta automaticamente se conectar ao Arduino ao iniciar. Se a conexão falhar, o usuário é questionado se deseja tentar novamente.
- **Captura de Imagens**: Captura imagens enviando um comando ao Arduino, que as retorna em formato base64.
- **Visualização na Interface**: A imagem capturada é exibida diretamente na tela principal, eliminando a necessidade de abrir uma nova janela.
- **Salvamento com Carimbo de Data e Hora**: As imagens podem ser salvas no formato JPEG ou PNG, com um carimbo de data e hora no canto inferior direito.
- **Controles Intuitivos**: Botões para salvar ou capturar novas imagens aparecem lado a lado na interface.

## Tecnologias Utilizadas
- **Arduino**: Plataforma de prototipagem eletrônica para controle de hardware.
- **ESP32**: Microcontrolador com conectividade Wi-Fi e Bluetooth, usado para comunicação sem fio com o Arduino.
- **Python**: Linguagem de programação utilizada para implementar a lógica da aplicação e a interface gráfica.
- **Custom Tkinter**: Biblioteca para criar interfaces gráficas modernas e personalizáveis.
- **Pillow (PIL)**: Biblioteca para manipulação de imagens, incluindo decodificação de base64 e adição de textos.

## Testes Unitários

O projeto inclui testes unitários desenvolvidos com `unittest`, que cobrem as principais funcionalidades da aplicação, como:

- **Adicionar Data e Hora à Imagem**: Verifica se a data e hora são corretamente adicionadas às imagens capturadas.
- **Conexão com o Arduino**: Testa se a aplicação consegue se conectar corretamente ao Arduino via porta serial.
- **Captura e Decodificação de Imagens**: Garante que as imagens sejam capturadas em formato base64 e decodificadas corretamente.
- **Interação com a Interface Gráfica**: Simula a interação da interface para capturar, visualizar e salvar imagens.

### Executando os Testes

Para rodar os testes unitários, execute o seguinte comando no terminal:

```bash
python -m unittest discover
```

Ou, se quiser rodar testes específicos:

```bash
python -m unittest test_snaplink.py
```

Isso executará todos os testes presentes no arquivo `test_snaplink.py` e exibirá o status de sucesso ou falha de cada teste.

## Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Contato

Se você tiver dúvidas ou precisar de mais informações, sinta-se à vontade para entrar em [Contato](https://linktr.ee/leomolinarodev01)!

