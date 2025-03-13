""" Execucao principal e funcoes principais """

import pyautogui as bot
import time
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from dictionary import projetos

PAUSE = 1
CONFIDENCE = 0.6
STATUS_FILE = 'status_execucao.txt'
bot.PAUSE = PAUSE

load_dotenv()
senha = os.getenv("SENHA")

logging.basicConfig(
    filename='relatorio_rpa.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Iniciando o Robo.")
    print("[INFO] Iniciando o Robo...\n")

    if verificar_primeira_execucao():
        logging.info("Executando a primeira inicializacao.")
        print("[INFO] Executando a primeira inicializacao...\n")
        abrir_autodoc()
        selecionar_pasta_destino()

    limpar_busca()
    limpar_downloads()
    selecionar_projetos()

    logging.info("Robo executado com sucesso.")
    print("[SUCESSO] Robo executado com sucesso.\n")

def verificar_primeira_execucao():
    if not os.path.exists(STATUS_FILE):
        logging.info("Primeira execucao detectada. Criando arquivo de status.")
        print("[INFO] Primeira execucao detectada. Criando arquivo de status.\n")
        with open(STATUS_FILE, 'w') as file:
            file.write('executado')
        return True
    logging.info("Execucao ja registrada anteriormente.")
    print("[INFO] Execucao ja registrada anteriormente.\n")
    return False

def abrir_autodoc():
    logging.info("Iniciando a abertura do AutoDoc.")
    print("[INFO] Iniciando a abertura do AutoDoc...\n")
    try:
        bot.press('win')
        bot.typewrite("AutoDoc")
        bot.press('enter')
        time.sleep(2)
        bot.hotkey("win", "up")
        logging.info("AutoDoc aberto com sucesso.")
        print("[SUCESSO] AutoDoc aberto com sucesso.\n")
    except Exception as e:
        logging.error(f"Erro ao abrir o AutoDoc: {e}")
        print(f"[ERRO] Falha ao abrir o AutoDoc: {e}\n")
        raise

def realizar_login():
    logging.info("Iniciando o processo de login.")
    print("[INFO] Iniciando o processo de login...\n")
    try:
        bot.press("tab")
        bot.typewrite(senha)
        bot.press("tab")
        bot.press("enter")
        time.sleep(1.5)
        bot.press("down")
        bot.press("enter")
        bot.press("tab")
        bot.press("enter")
        logging.info("Login realizado com sucesso.")
        print("[SUCESSO] Login realizado com sucesso.\n")
    except Exception as e:
        logging.error(f"Erro ao realizar login: {e}")
        print(f"[ERRO] Falha ao realizar login: {e}\n")
        raise

def selecionar_pasta_destino():
    logging.info("Iniciando a selecao da pasta de destino.")
    print("[INFO] Iniciando a selecao da pasta de destino...\n")
    time.sleep(1)
    if clicar_elemento('imagens/pasta.png', 'Pasta'):
        time.sleep(1)
        if clicar_elemento('imagens/downloads.png', 'Downloads'):
            time.sleep(1)
            if clicar_elemento('imagens/selecionar_pasta.png', 'Selecionar Pasta'):
                logging.info("Pasta de destino selecionada com sucesso.")
                print("[SUCESSO] Pasta de destino selecionada com sucesso.\n")
            else:
                logging.warning("Falha ao selecionar a pasta de destino.")
                print("[ATENCAO] Falha ao selecionar a pasta de destino.\n")
        else:
            logging.warning("Falha ao selecionar a pasta 'Downloads'.")
            print("[ATENCAO] Falha ao selecionar a pasta 'Downloads'.\n")
    else:
        logging.warning("Falha ao localizar o botao 'Pasta'.")
        print("[ATENCAO] Falha ao localizar o botao 'Pasta'.\n")

def clicar_elemento(imagem, descricao, timeout=10):
    start_time = time.time()

    while time.time() - start_time < timeout:
        localizacao = bot.locateOnScreen(imagem, confidence=CONFIDENCE)

        if localizacao:
            bot.click(bot.center(localizacao))
            logging.info(f"Elemento '{descricao}' clicado com sucesso.")
            print(f"[SUCESSO] Elemento '{descricao}' clicado com sucesso.\n")
            return True

        time.sleep(1)

    logging.warning(f"Elemento '{descricao}' nao encontrado dentro do timeout.")
    print(f"[ATENCAO] Elemento '{descricao}' nao encontrado apos {timeout} segundos.\n")
    return False

def capturar_tela(nome_projeto):
    if not os.path.exists("prints"):
        os.makedirs("prints")
    data_hora = datetime.now().strftime("%d-%m-%Y__%H-%M-%S")
    nome_arquivo = f"prints/{nome_projeto}_{data_hora}.png"
    bot.screenshot(nome_arquivo)
    logging.info(f"Print da tela salvo em: {nome_arquivo}")
    print(f"[INFO] Print da tela salvo em: {nome_arquivo}\n")

def selecionar_projetos():
    try:
        projetos

        indice_atual = ler_indice()

        lista_projetos = list(projetos.keys())

        for i in range(indice_atual, len(lista_projetos)):
            nome_projeto = lista_projetos[i]
            logging.info(f"Processando projeto: {nome_projeto}")
            print(f"[INFO] Processando projeto: {nome_projeto}\n")

            bot.click(x=681, y=320)

            if i > 0:
                for _ in range(i):
                    bot.press("down")

            bot.press("enter")

            salvar_indice(i + 1)

            if clicar_elemento("imagens/botao_buscar.png", "Botao de Buscar"):
                time.sleep(25)

                try:
                    baixar_todos = bot.locateOnScreen("imagens/baixar_todos.png", confidence=CONFIDENCE)

                    if baixar_todos:
                        logging.info(f"Conteudo encontrado no projeto '{nome_projeto}'. Iniciando download.")
                        print(f"[INFO] Conteudo encontrado no projeto '{nome_projeto}'. Iniciando download.\n")
                        bot.click(bot.center(baixar_todos))

                        if not verificar_download():
                            continue

                        limpar_busca()

                    else:
                        logging.warning(f"Botao 'Baixar Todos' nao encontrado no projeto '{nome_projeto}'.")
                        print(f"[ATENCAO] Botao 'Baixar Todos' nao encontrado no projeto '{nome_projeto}'.\n")

                except bot.ImageNotFoundException:
                    logging.warning(f"Nenhum registro encontrado no projeto '{nome_projeto}'.")
                    print(f"[ATENCAO] Nenhum registro encontrado no projeto '{nome_projeto}'.\n")

    except Exception as e:
        logging.error(f"Erro ao processar projetos: {e}")
        print(f"[ERRO] Ocorreu um erro ao processar projetos: {e}\n")

def salvar_indice(indice):
    with open("indice_atual.txt", "w") as f:
        f.write(str(indice))
    logging.info(f"Indice atual {indice} salvo com sucesso.")
    print(f"[INFO] Indice atual {indice} salvo com sucesso.\n")

def ler_indice():
    if os.path.exists("indice_atual.txt"):
        with open("indice_atual.txt", "r") as f:
            indice = int(f.read())
            logging.info(f"Indice atual {indice} lido com sucesso.")
            print(f"[INFO] Indice atual {indice} lido com sucesso.\n")
            return indice
    else:
        logging.info("Nenhum indice salvo encontrado. Iniciando do indice 0.")
        print("[INFO] Nenhum indice salvo encontrado. Iniciando do indice 0.\n")
        return 0

def verificar_download():
    pasta_download = r"C:\Users\lucas.arruda\Downloads\BILD"
    logging.info(f"Iniciando monitoramento da pasta: {pasta_download}")
    print(f"[INFO] Monitorando a pasta: {pasta_download}\n")

    evento_handler = MonitorarPasta()
    observador = Observer()
    observador.schedule(evento_handler, pasta_download, recursive=True)
    observador.start()

    verificacoes = 0
    try:
        while verificacoes < 30:
            time.sleep(10)
            if evento_handler.downloads_ativos:
                logging.info("Arquivos sendo baixados ou modificados na pasta. Aguardando.")
                print("[INFO] Arquivos sendo baixados ou modificados na pasta. Aguardando.\n")
                evento_handler.downloads_ativos = False
                verificacoes = 0
            else:
                logging.info(f"Nenhuma alteracao detectada {verificacoes}. Monitorando...")
                print(f"[INFO] Nenhuma alteracao detectada {verificacoes}. Monitorando...\n")
                verificacoes += 1

        logging.info("Download parou de ser modificado. Verificando se esta travado no status 'obtendo endereco'.")
        print("[INFO] Download parou de ser modificado. Verificando se esta travado no status 'obtendo endereco'.\n")

        bot.click(x=1500, y=90)
        bot.click(x=1596, y=92)
        time.sleep(2)

        try:
            status_obtendo_endereco = bot.locateOnScreen("imagens/status_obtendo_endereco.png", confidence=0.5)
            if status_obtendo_endereco:
                logging.warning("Download travado no status 'obtendo endereco'. Reiniciando o processo.")
                print("[ATENCAO] Download travado no status 'obtendo endereco'. Reiniciando o processo.\n")

                capturar_tela("status_obtendo_endereco")

                reiniciar_autodoc()

                return False
            else:
                logging.info("Download concluido com sucesso. Prosseguindo para o proximo projeto.")
                print("[INFO] Download concluido com sucesso. Prosseguindo para o proximo projeto.\n")
                return True
        except bot.ImageNotFoundException:
            logging.info("Status 'obtendo endereco' nao encontrado. Download concluido com sucesso.")
            print("[INFO] Status 'obtendo endereco' nao encontrado. Download concluido com sucesso.\n")
            return True

    except KeyboardInterrupt:
        logging.warning("Monitoramento interrompido pelo usuario.")
        print("[ATENCAO] Monitoramento interrompido pelo usuario.\n")

    finally:
        observador.stop()
        observador.join()

def limpar_downloads():
    logging.info("Iniciando a limpeza do historico de downloads.")
    print("[INFO] Iniciando a limpeza do historico de downloads...\n")
    time.sleep(1)
    try:
        bot.click(x=1596, y=92)
        time.sleep(1)
        if clicar_elemento("imagens/lixeira.png", "Limpar Downloads"):
            bot.click(x=1500, y=90)
            logging.info("Historico de downloads limpo com sucesso.")
            print("[SUCESSO] Historico de downloads limpo com sucesso.\n")
        else:
            logging.warning("Falha ao limpar o historico de downloads.")
            print("[ATENCAO] Falha ao limpar o historico de downloads.\n")
    except bot.ImageNotFoundException:
        logging.warning("Sem historico de downloads para limpar.")
        print("[ATENCAO] Sem historico de downloads para limpar.\n")

def limpar_busca():
    logging.info("Iniciando a limpeza da busca.")
    print("[INFO] Iniciando a limpeza da busca...\n")
    time.sleep(1)
    bot.moveTo(x=61, y=143)
    bot.click(x=61, y=143)
    bot.moveTo(x=364, y=142)
    logging.info("Busca limpa com sucesso.")
    print("[SUCESSO] Busca limpa com sucesso.\n")

def reiniciar_autodoc():
    logging.info("Iniciando o reinicio do AutoDoc.")
    print("[INFO] Iniciando o reinicio do AutoDoc...\n")

    try:
        bot.click(x=1500, y=90)
        bot.hotkey('alt', 'f4')
        time.sleep(2)

        bot.press('win')
        bot.typewrite("AutoDoc")
        bot.press('enter')
        time.sleep(2)
        bot.hotkey("win", "up")
        
        time.sleep(2)

        limpar_downloads()
        time.sleep(2)
        limpar_busca()

        logging.info("AutoDoc reiniciado com sucesso.")
        print("[SUCESSO] AutoDoc reiniciado com sucesso.\n")

    except Exception as e:
        logging.error(f"Erro ao reiniciar o AutoDoc: {e}")
        print(f"[ERRO] Falha ao reiniciar o AutoDoc: {e}\n")
        raise

class MonitorarPasta(FileSystemEventHandler):
    def __init__(self):
        self.downloads_ativos = False

    def on_created(self, event):
        if not event.is_directory:
            print(f"[INFO] Novo arquivo detectado: {event.src_path}\n")
            self.downloads_ativos = True

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[INFO] Arquivo modificado: {event.src_path}\n")
            self.downloads_ativos = True

if __name__ == "__main__":
    main()