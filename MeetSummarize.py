from tkinter import Toplevel,Menu,Label,Button,simpledialog,messagebox,filedialog,ttk,Text,Tk,Canvas,NW, StringVar,END,CENTER
from PIL import ImageTk,Image
import os,sys,webbrowser,requests
from pathlib import Path
import customtkinter
import threading
import os 
from moviepy.editor import *
from pydub import AudioSegment
import wave
import openai
from openai import OpenAI 
from datetime import datetime
from pathlib import Path
import sys
import pyaudio
import time
import configparser
import shutil
from typing import List
import requests
try:
    import pyi_splash
    pyi_splash.update_text('Datacombiner Loaded ...')
    pyi_splash.close()
except:
    pass
#variavel versão do projeto
versao = "v3.1"


#variavel para no minimo ter de reunião para iniciar uma transcrição + resumo (em segundos)


#Função para salvar arquivo
def salva_arquivo(caminho_arquivo, conteudo):  
    if not os.path.isfile(caminho_arquivo ):
        f = open(caminho_arquivo, "x")
        f.close()

    f = open(caminho_arquivo, "a")
    f.write(conteudo)
    f.close()

def le_arquivo(caminho_arquivo):  
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo) as f:
            return f.read()
    else:
        return ''



PROMPT = '''
Faça o resumo do texto delimitado por #### 
O texto é a transcrição de uma reunião.
Tente identificar se foi citado nesse texto de algum cliente e colocar no nome dele, como por exemplo se tiver na frase cliente XXXX
Se houver alguma data definida para alguma atividade ou próxima reuniao, colocar essa data no formato dd/MM/aaaa
O resumo deve contar com os principais assuntos abordados e separados por topico e bem detalhado.
O resumo deve estar em texto corrido.
O resumo deve contar com as soluções tecnologicas proposta.
No final, devem ser apresentados todos acordos,combinados e proximos passos
feitos na reunião no formato de bullet points.

O formato final que eu desejo é:

Resumo reunião:
- escrever aqui o resumo detalhado

Nome do cliente:
- escrever aqui o nome do cliente se foi identificado

Acordos da Reunião :
- acordo 1
- acordo 2
- acordo 3
- acordo n

Próximos passos :
- passo 1
- passo 2
- passo n


Soluções propostas:
- solução 1
- solução 2
- solução n

Data próximos passos ou reuinão:
- escrever aqui a data

texto: ####{}####
'''

#Criar diretorio na pasta root
PASTA_ARQUIVOS = os.path.expanduser("~") + "/.MeetGPTv2"
PASTA_MODELO = os.path.expanduser("~") + "/.MeetGPTv2/models"
PASTA_IMAGENS = os.path.expanduser("~") + "/.MeetGPTv2/images"
PASTA_PROMPT = os.path.expanduser("~") + "/.MeetGPTv2/prompt"
PASTA_CONFIG = os.path.expanduser("~") + "/.MeetGPTv2/config"

if not os.path.exists(PASTA_ARQUIVOS):
    os.makedirs(PASTA_ARQUIVOS)

if not os.path.exists(PASTA_MODELO):
    os.makedirs(PASTA_MODELO)

if not os.path.exists(PASTA_IMAGENS):
    os.makedirs(PASTA_IMAGENS)

if not os.path.exists(PASTA_PROMPT):
    os.makedirs(PASTA_PROMPT)

if not os.path.exists(PASTA_CONFIG):
    os.makedirs(PASTA_CONFIG)

iconImageFile = PASTA_IMAGENS + "/meetingAI.ico"
InfoImageFile = PASTA_IMAGENS + "/icon-logo.png"
RobotImageFile = PASTA_IMAGENS + "/robot.png"
promptFile = PASTA_PROMPT + "/prompt.txt"
configfile = PASTA_CONFIG + "/config"

#URLS de download
icon_download_url = 'https://raw.githubusercontent.com/ValentimMuniz/Meeting-Summary-with-OpenAI//main/images/meetingAI.ico'
InfoImage_download_url = 'https://raw.githubusercontent.com/ValentimMuniz/Meeting-Summary-with-OpenAI//main/images/info-logo.png'
RobotImage_download_url = 'https://raw.githubusercontent.com/ValentimMuniz/Meeting-Summary-with-OpenAI/main/images/robot.png'


if not os.path.isfile(iconImageFile):
    iconImageFile_download = requests.get(icon_download_url)
    open(iconImageFile, 'wb').write(iconImageFile_download.content)

if not os.path.isfile(InfoImageFile):
    InfoImageFile_download = requests.get(InfoImage_download_url)
    open(InfoImageFile, 'wb').write(InfoImageFile_download.content) 

if not os.path.isfile(RobotImageFile):
    RobotImageFile_download = requests.get(RobotImage_download_url)
    open(RobotImageFile, 'wb').write(RobotImageFile_download.content)

if not os.path.isfile(RobotImageFile):
    RobotImageFile_download = requests.get(RobotImage_download_url)
    open(RobotImageFile, 'wb').write(RobotImageFile_download.content)

if not os.path.isfile(promptFile):
    salva_arquivo(promptFile, PROMPT) 

if not os.path.isfile(configfile):
    #Cria arquivo de configuração
    f = open(configfile, "x")
    f.close()

    #Adiciona valores iniciais no arquivo de configuração
    f = open(configfile, "w")
    f.write("[OPENAI]\n")
    f.write(f"OPENAI_APIKEY = <OpenAIKey>\n")
    f.write("[CONFIG]\n")
    f.write("tempo_reuniao = 60\n")
    f.write("[TELEGRAM]\n")
    f.write("Bot_Token = <Bot_Token>\n")
    f.write("Chat_ID = <Chat_ID>\n")
    f.write("Usar_Telegram = <0/1>")
    f.close()

############################# Função para ler configuração #############################
def LerConfiguracao():
    global openai_api_key,tempo_reuniao, botToken, chat_id, usar_telegram
    # Lendo arquivo de configuração
    config = configparser.ConfigParser()
    config.read(configfile)
    openai_api_key = config['OPENAI']['OPENAI_APIKEY']
    tempo_reuniao = int(config['CONFIG']['tempo_reuniao'])
    botToken = config['TELEGRAM']['Bot_Token']
    chat_id = config['TELEGRAM']['Chat_ID']
    usar_telegram = config['TELEGRAM']['Usar_Telegram']
############################# Fim de função para ler configuração #############################


#############################  Função para setar aglum valor no arquivo de config #############################
def set_value_in_property_file(file_path, section, key, value):
    config = configparser.RawConfigParser()
    config.read(file_path)
    config.set(section,key,value)                         
    cfgfile = open(file_path,'w+')
    config.write(cfgfile) 
    cfgfile.close()


def FirstTimeScript(error, tipo_erro):

    LerConfiguracao()
    #Se nao tiver dado erro o script e não existir o arquvio de config
    if error == False: 
        #Pedir via askstring a chave do OpenAI
        APINone = False
        if openai_api_key == "<OpenAIKey>":
            while APINone == False:  
                APIKeyinput = simpledialog.askstring("OpenAI API", "Insira sua chave do OpenAI API", parent=root)           
                if APIKeyinput is not None and APIKeyinput != "":
                    set_value_in_property_file(configfile, 'OPENAI', 'OPENAI_APIKEY', APIKeyinput)
                    LerConfiguracao()
                    APINone = True
                else: 
                    messagebox.showerror("Vazio", "Chave de API não pode ser vazia", parent=root)

         #Verificar se o usuário vai querer usar o telegram
        UsarTelegram = False
        if usar_telegram == "<0/1>":
            while UsarTelegram == False:  
                UsarTelegramInput = simpledialog.askstring("Usar Telgram ?", "Digite 1 para sim / 0 para não.", parent=root)  
                if UsarTelegramInput is not None and UsarTelegramInput != "":
                    match = ['1','0']
                    if any(c in UsarTelegramInput for c in match):
                        set_value_in_property_file(configfile, 'TELEGRAM', 'Usar_Telegram', UsarTelegramInput)
                        LerConfiguracao()
                        UsarTelegram = True
                    else:
                        messagebox.showerror("Não permitido", "Valor não permitido, use somente 0 ou 1.", parent=root)
                else: 
                    messagebox.showerror("Vazio", "Não pode ser valor vazio.", parent=root)

        if usar_telegram == "1":
            #Verificar se o usuário digitou 1 
            BotTokenone = False
            if botToken == "<Bot_Token>":
                while BotTokenone == False:  
                    BotTokeninput = simpledialog.askstring("Telegram BOT Token", "Insira sua key do BOT do Telegram", parent=root)           
                    if BotTokeninput is not None and BotTokeninput != "":
                        set_value_in_property_file(configfile, 'TELEGRAM', 'Bot_Token', BotTokeninput)
                        LerConfiguracao()
                        BotTokenone = True
                    else: 
                        messagebox.showerror("Vazio", "Token não pode ser vazio", parent=root)

            ChatIDNone = False
            if chat_id == "<Chat_ID>":
                while ChatIDNone == False:  
                    ChatIDinput = simpledialog.askstring("OpenAI API", "Insira sua chave do OpenAI API", parent=root)           
                    if ChatIDinput is not None and ChatIDinput != "":
                        set_value_in_property_file(configfile, 'TELEGRAM', 'Chat_ID', ChatIDinput)
                        LerConfiguracao()
                        ChatIDNone = True
                    else: 
                        messagebox.showerror("Vazio", "Chat ID não pode ser vazio", parent=root)
    else:
        if tipo_erro == "OpenaAI":
            APINone = False
            while APINone == False:  
                APIKeyinput = simpledialog.askstring("Sua chave esta errada/sem permissão! Insira uma corretamente", "Insira sua chave do OpenAI API", parent=root)           
                if APIKeyinput is not None and APIKeyinput != "":
                    set_value_in_property_file(configfile, 'OPENAI', 'OPENAI_APIKEY', APIKeyinput)
                    APINone = True
                else: 
                    messagebox.showerror("Vazio", "Chave de API não pode ser vazia", parent=root)


#Função para converter de mp4 para mp3
def mp4_to_mp3():
    global fullMonoPathFile, pasta_reuniao_selecionada
    try:
        pasta_reuniao_path = os.path.expanduser(pasta_reuniao_selecionada)
        if not os.path.exists(pasta_reuniao_path):
            os.makedirs(pasta_reuniao_path)

        labelProgress.config(text = "Convertendo vídeo para aúdio...") 
        video = VideoFileClip(str(mp4path))
        audio = video.audio
        audio.write_audiofile(fullmp3path)


        #pegar o .mp3 e corverter para WAV 
        audioFromMP3 = AudioSegment.from_mp3(fullmp3path)
        
        #criar um WAV do MP3
        fullWAVpath = pasta_reuniao_selecionada + "/" + ArquivoMP3Renomeado + ".wav"
        audioFromMP3.export(fullWAVpath, format="wav")


        #Pegar o audio WAV convertido e transformar em MONO
        # Load audio file
        audiofromWAV = AudioSegment.from_wav(fullWAVpath) 

        # Convert to mono
        audiofromWAV = audiofromWAV.set_channels(1)

        # Set frame rate 
        audiofromWAV = audiofromWAV.set_frame_rate(16000)
        fullMonoPathFile = pasta_reuniao_selecionada + "/" + ArquivoMP3Renomeado + "_mono" + ".wav"
        # Save new audio
        audiofromWAV.export(fullMonoPathFile , format="wav")
            
        os.remove(fullmp3path) 
        os.remove(fullWAVpath)

        transcreve_audio(fullMonoPathFile, pasta_reuniao_selecionada, "conversao")
        
    except Exception as e: 
        messagebox.showerror("Error", e, parent=MeetingWindow)

    



#Função para enviar o texto com o Prompt para o OpenAI
def chat_openai(
        mensagem,
        modelo='gpt-4-turbo', 
    ): 
    client = OpenAI(api_key=openai_api_key)
    mensagens = [{'role': 'user', 'content': mensagem}]
    resposta = client.chat.completions.create(
        model=modelo,
        messages=mensagens,
        )
    return resposta.choices[0].message.content

#Função para pegar a transcrição do audio e gerar resumo com OpenAI
def gerar_resumo(transcricao, pasta_reuniao, tipo):       
    global resumo
    if tipo == "conversao":
       labelProgress.config(text = "Gerando resumo...")
    elif tipo == "gravacao":
        labelRecordingText.config(text = "Gerando resumo...")
    #Mandar texto da transcrição pro OpenAI para fazer o resumo
    resumo = chat_openai(mensagem=le_arquivo(promptFile).format(transcricao))    
    #Salvar o arquivo com o resumo
    salva_arquivo(pasta_reuniao + "/resumo.txt", resumo)

        
   



def run_progressbar(tipo):
    global p
    if tipo == "conversao":
        p = ttk.Progressbar(MeetingWindow, orient="horizontal", length=290, mode="indeterminate",
                            takefocus=True, maximum=100)
        p.place(relx=.01, rely=.6) 
        p.start()
    elif tipo == "gravacao":
        p = ttk.Progressbar(RecordWindow, orient="horizontal", length=200, mode="indeterminate",
                            takefocus=True, maximum=100, style='info.Striped.Horizontal.TProgressbar')
        p.place(relx=.170, rely=.4) 
        p.start()


#Thread para iniciar o processo de tudo, convsesao para mp3, transcricao e gerar resumo
def start_thread(tipo):
    global titulo,submit_thread_conversao, submit_thread_gravacao,error
    error = False
    if tipo == "conversao":   
        titulo = txtTituloReuniao.get("1.0",END).strip()
        if titulo != "":     
            #se nao usar o lambda nao consegue passar parametros e iniciar 
            submit_thread_conversao = threading.Thread(target= mp4_to_mp3)
            submit_thread_conversao.daemon = True
            submit_thread_conversao.start() 
            run_progressbar("conversao")
            root.after(20, check_thread_conversao)
            
        else:
            messagebox.showwarning("Campo vazio/invalido", "Preencha o campo titulo para gerar o resumo", parent=MeetingWindow)
            txtTituloReuniao.focus_set()
    elif tipo == "gravacao":
        titulo = txtTituloReuniao_Gravar.get("1.0",END).strip()
        if titulo != "":  
            labelRecordingTime.config(text = "00:00:00")   
            labelRecordingTime.place(relx=.01,rely=.315)      
            threading.Thread(target=record_audio).start()
        else:
            messagebox.showwarning("Campo vazio/invalido", "Preencha o campo titulo para gerar o resumo", parent=RecordWindow)
            txtTituloReuniao_Gravar.focus_set()
    elif tipo == "transcricao_gravacao":       
        submit_thread_gravacao = threading.Thread(target = lambda: transcreve_audio(CaminhoArquivoGravado, pasta_reuniao_gravada, "gravacao"))     
        submit_thread_gravacao.daemon = True
        submit_thread_gravacao.start()
        run_progressbar("gravacao")
        root.after(20, check_thread_gravacao)
    
       
 

#Checar se a Thread de conversao ainda esta ativa
def check_thread_conversao():
    if error == False:
        if submit_thread_conversao.is_alive():
            p.step()
            root.after(20, check_thread_conversao)
        else:
            p.stop()
            p.destroy()
            gerarResumoBtn.place_forget()
            
            labelSelectedFile.config(text='')
            labelProgress.config(text='')
            messagebox.showinfo("Resumo gerado com sucesso", "O Resumo foi gerado com sucesso e estará pronto para visualização na aba de Resumos", parent=MeetingWindow)
            if usar_telegram == "1":
                try:
                    tituloDataReuniao = txtTituloReuniao.get("1.0",END).strip() + " - " + agoraConversao + "\n"
                    print(tituloDataReuniao)
                    agoraConversao
                    url = f"https://api.telegram.org/bot{botToken}/sendMessage?chat_id={chat_id}&text={tituloDataReuniao}{resumo}"
                    r = requests.get(url)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    messagebox.showerror("Erro ao enviar para o Telegram", err, parent=MeetingWindow)
            txtTituloReuniao.delete('1.0', END)
            root.focus_force()
            MeetingWindow.focus_force()
            txtTituloReuniao.focus_set()
    else:
        p.stop()
        p.destroy()
        gerarResumoBtn.place_forget()
        txtTituloReuniao.delete('1.0', END)
        labelSelectedFile.config(text='')
        labelProgress.config(text='')
        messagebox.showinfo("Error - resumo e reunião deletados", erromsg, parent=MeetingWindow)
        FirstTimeScript(True, "OpenAI")
        shutil.rmtree(pasta_reuniao_selecionada + "/")
        root.focus_force()
        MeetingWindow.focus_force()
        txtTituloReuniao.focus_set()
        

#Checar se a Thread de gravacao ainda esta ativa
def check_thread_gravacao():
    if error == False:
        if submit_thread_gravacao.is_alive():
            p.step()
            p.step()
            root.after(20, check_thread_gravacao) 
        else:
            p.stop()
            p.destroy()      
            labelRecordingText.config(text = "")    
            labelRecordingTime.config(text = "")
            labelRecordingTime.place_forget()
            messagebox.showinfo("Resumo gerado com sucesso", "O Resumo foi gerado com sucesso e estará pronto para visualização na aba de Resumos", parent=RecordWindow)
            if usar_telegram == "1":
                try:
                    tituloDataReuniao = txtTituloReuniao_Gravar.get("1.0",END).strip() + " - " + agoraGravacao + "\n"
                    url = f"https://api.telegram.org/bot{botToken}/sendMessage?chat_id={chat_id}&text={tituloDataReuniao}{resumo}"
                    r = requests.get(url)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    messagebox.showerror("Erro ao enviar para o Telegram", err, parent=RecordWindow)
            txtTituloReuniao_Gravar.delete('1.0', END) 
            root.focus_force()
            RecordWindow.focus_force()
            txtTituloReuniao_Gravar.focus_set()
    else:
        p.stop()
        p.destroy()
        txtTituloReuniao_Gravar.delete('1.0', END)   
        labelRecordingText.config(text = "")    
        labelRecordingTime.config(text = "")
        labelRecordingTime.place_forget()
        shutil.rmtree(pasta_reuniao_gravada + "/")
        messagebox.showinfo("Error - resumo e reunião deletados", erromsg, parent=RecordWindow)
        root.focus_force()
        RecordWindow.focus_force()
        txtTituloReuniao_Gravar.focus_set()



def split_audio_file(audio_path: str, chunk_duration: int = 100000) -> List[str]:
    """
    Splits the audio file into chunks of 24MB or less.

    Parameters
    ----------
    audio_path : str
        The path to the audio file.
    chunk_duration : int, optional
        The duration of each audio chunk in milliseconds, by default 30000 (30 seconds).

    Returns
    -------
    List[str]
        A list of file paths for the generated audio chunks.
    """
    # load the audio file
    audio = AudioSegment.from_file(audio_path)
    audio_chunks = []

    # create a temp folder to store the audio chunks
    if not os.path.exists("temp"):
        os.makedirs("temp")

    for i, chunk in enumerate(audio[::chunk_duration]):
        chunk_path = f"temp/temp_audio_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        audio_chunks.append(chunk_path)

    return audio_chunks


#Função para transcrever aúdio em texto com o OpenAI
def transcreve_audio(caminho_audio, pasta_reuniao, tipo):
    global error, erromsg
    client = OpenAI(api_key=openai_api_key)
    if tipo == "conversao":
        labelProgress.config(text = "Transcrevendo áudio...")
    elif tipo == "gravacao":
        labelRecordingText.config(text = "Transcrevendo áudio...")
    try:     
        # if the file is larger than 24MB, split it into chunks
        audio_size = os.path.getsize(caminho_audio)
        max_size = 24 * 1024 * 1024

        if audio_size > max_size:
            # split the audio file into chunks
            audio_chunks = split_audio_file(caminho_audio)
        else:
            audio_chunks = [caminho_audio]  
         # Generate the transcription
        transcriptions = []

        i = 0
        for chunk_path in audio_chunks:
            with open(chunk_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                model='whisper-1',
                language='pt',
                response_format='text',
                file=audio_file,    
            )
            i += 1
            transcriptions.append(response)

            if audio_size > max_size:
                os.remove(chunk_path)

        transcriptions = "\n".join(transcriptions)
        error = False
        salva_arquivo(pasta_reuniao + "/transcricao.txt", transcriptions) 
        salva_arquivo(pasta_reuniao + '/titulo.txt', titulo)
        gerar_resumo(transcriptions, pasta_reuniao, tipo) 
    except openai.BadRequestError as e: # Don't forget to add openai
        # Handle error 400
        erromsg = e
        error = True
        return
    except openai.AuthenticationError as e: # Don't forget to add openai
        # Handle error 401
        erromsg = e
        error = True
        return
    except openai.PermissionDeniedError as e: # Don't forget to add openai
        # Handle error 403
        erromsg = e
        error = True
        return
    except openai.NotFoundError as e: # Don't forget to add openai
        # Handle error 404
        erromsg = e
        error = True
        return
    except openai.UnprocessableEntityError as e: # Don't forget to add openai
        # Handle error 422
        erromsg = e
        error = True
        return
    except openai.RateLimitError as e: # Don't forget to add openai
        # Handle error 429
        erromsg = e
        error = True
        return
    except openai.InternalServerError as e: # Don't forget to add openai
        # Handle error >=500
        erromsg = e
        error = True
        return
    except openai.APIConnectionError as e: # Don't forget to add openai
        # Handle API connection error
        erromsg = e
        error = True 
        return
    except openai.APIError as e:
        #Handle API error here, e.g. retry or log
        erromsg = e
        error = True
        return 
       

#Função para gravar audio do microfone/computador
def record_audio():
    global pasta_reuniao_gravada, CaminhoArquivoGravado, agoraGravacao
    labelRecordingText.config(text = "Gravando ...")  
    try: 
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=2, rate=48000, input=True, frames_per_buffer=1024)
      
        frames = []
        start = time.time()
        while gravando:
            data = stream.read(16000)
            frames.append(data)
            passed = time.time() - start
            seconds = passed % 60   
            minutes = passed // 60
            hours = minutes // 60
            labelRecordingTime.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        
        if passed < tempo_reuniao:
            txtTituloReuniao_Gravar.delete('1.0', END)    
            labelRecordingText.config(text = "")    
            labelRecordingTime.config(text = "")
            labelRecordingTime.place_forget()
            messagebox.showwarning("Reunião muito curta", f"Reunião com tempo de duração muito curta deve ser no mínimo de {int(tempo_reuniao/60)} minutos.", parent=RecordWindow)
            root.focus_force()
            RecordWindow.focus_force()
            txtTituloReuniao_Gravar.focus_set()
                      
        else:   
            stream.stop_stream()
            stream.close() 
            audio.terminate()
            # save the recorded input
            agoraGravacao = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            recording_file_name = f"recorded_input_{agoraGravacao}.wav"

            
            #Criar pasta da reunião com data atual 
            pasta_reuniao_gravada = PASTA_ARQUIVOS + "/reunioes/" + agoraGravacao
            
                
            reuniaoPath = os.path.expanduser(pasta_reuniao_gravada)
            if not os.path.exists(reuniaoPath):
                os.makedirs(reuniaoPath)

            sound_file = wave.open(pasta_reuniao_gravada + "/" + recording_file_name, "wb")
            
            sound_file.setnchannels(2)
            sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            sound_file.setframerate(48000)
            sound_file.writeframes(b"".join(frames))
            sound_file.close()

            CaminhoArquivoGravado = pasta_reuniao_gravada + "/" + recording_file_name
            start_thread("transcricao_gravacao")
    except Exception as e: 
        messagebox.showwarning("Error", e , parent=RecordWindow)
        
    
                    
#Função para fechar o texto resumo
def FecharTexto(textbox,btnFecharResumo):
    textbox.place_forget()
    textbox.delete('1.0', END)
    btnFecharResumo.place_forget()
    cmb_resumos.current(0)
    
#Função para remover strings da data e retonar no estilo XXXX_XX_XX_XX
def replaceSting(str):
    replace_list = ["_", ":", " ", "/"]
    for i in replace_list:
        str = str.replace(i, "_")
    return str

#Função para "triggar" e selecionar o index de um comboBox
def get_index(*arg): 
    teste= cmb_resumos.get()
    
    if teste != "Selecione uma reunião":
        reuniao_data = replaceSting(str(var.get()).split('-')[0].strip())
        pasta_reuniao_combo = PASTA_ARQUIVOS + "/reunioes/" + reuniao_data
        resumo = le_arquivo(pasta_reuniao_combo + '/resumo.txt')

        ResumoTxt.configure(state="normal")
        ResumoTxt.place(relx=.0, rely=.2)
        
        ResumoTxt.delete('1.0', END)
        ResumoTxt.insert("0.0", resumo)
        
        ResumoTxt.configure(state="disabled")
        
        btnFecharResumo.place(relx=.01, rely=.150)
    else:
        ResumoTxt.delete('1.0', END)
        ResumoTxt.place_forget()
        btnFecharResumo.place_forget()

#Função para listar as reuniões criadas dentro da pasta de reuniões
def listar_reunioes():
    lista_reunioes = Path(PASTA_ARQUIVOS + "/reunioes").glob('*')
    lista_reunioes = list(lista_reunioes)
    lista_reunioes.sort(reverse=True)
    reunioes_dict = {}
    for pasta_reuniao in lista_reunioes:
        data_reuniao = Path(pasta_reuniao).stem
        
        ano, mes, dia, hora, min, seg = data_reuniao.split('_')
        reunioes_dict[data_reuniao] = f'{ano}/{mes}/{dia} {hora}:{min}:{seg}'
        titulo = le_arquivo(pasta_reuniao / 'titulo.txt')
        if titulo != '':
            reunioes_dict[data_reuniao] += f' - {titulo}'
    return reunioes_dict

#Função para identificar que a janela esta sendo fechada e colocar foco na root
def on_closingResumoWindow():
    ResumoWindow.destroy()
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

############################# Janela Resumos #############################
def AbrirJanelaResumos():
    global cmb_resumos,ResumoWindow, var, ResumoTxt, btnFecharResumo
    ResumoWindow = Toplevel(root) 
    ResumoWindow.title("Resumos de reuniões") 
    ResumoWindow.wm_iconbitmap(iconImageFile)
    ResumoWindow.minsize(1500,700)
    center(ResumoWindow)
    ResumoWindow.resizable(0,0)
    ResumoWindow.configure(background='#F0FFFF')

    label = Label(ResumoWindow,text="Selecione uma reunião: ",font='Calibri 14 bold',background='#F0FFFF')
    label.place(relx=.01, rely=.050)

    var = StringVar() 
    reunioes_dict = listar_reunioes()
    cmb_resumos = ttk.Combobox(ResumoWindow,state="readonly", width = 40, textvariable=var, justify='center')
    cmb_resumos['value'] = ["Selecione uma reunião"]
    cmb_resumos.current(0) 
    cmb_resumos.place(relx=.14, rely=.057)
    ResumoTxt = Text(ResumoWindow, width=187, height=35)
    
    if len(reunioes_dict) > 0: 
        for key, value in reunioes_dict.items():
            cmb_resumos['value'] = (*cmb_resumos['values'], value)
        
        var.trace('w', get_index) 
        
        cmb_resumos.bind("<<ComboboxSelected>>",lambda e: ResumoWindow.focus())       
    else:
        messagebox.showinfo("Sem reuniões", "Não há reunições salvas", parent=ResumoWindow)

    btnFecharResumo = customtkinter.CTkButton(ResumoWindow,text="Fechar Resumo", command=lambda: FecharTexto(ResumoTxt, btnFecharResumo))
    ResumoWindow.protocol("WM_DELETE_WINDOW", on_closingResumoWindow) 
    

############################# Funções pra abrir Explorer para escolher MP4 #############################
def EscolherArquivo(closing): 
    global ArquivoMP4,ArquivoMP3Renomeado,fullmp3path,pasta_reuniao_selecionada,mp4path, agoraConversao
    if closing == False:
        ArquivoMP4 = filedialog.askopenfilename(title = "Selecione um arquivo", filetypes=(('MP4 Files', '*.mp4'),))

        #print(teste.getvalue()) 
        MeetingWindow.focus_set()
        mp4path = Path(ArquivoMP4)
        if ArquivoMP4 != "":

            ''' Se quiser usar um diretorio temporario para esse MP4, mas daí nao da pra deletar e fica usando muito espaço da %temp%
            #criar arquivo temporario para o mp4
            #temp_dir = tempfile.mkdtemp()
            #mp4path = os.path.join(temp_dir, uploaded_file.name)
            #shutil.copyfile(uploaded_file, mp4path)'''
                     
            agoraConversao = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
            #Criar pasta da reunião com data atual 
            pasta_reuniao_selecionada = PASTA_ARQUIVOS + "/reunioes/" + agoraConversao
            

            ArquivoMP3Renomeado = mp4path.name.replace('.mp4', '')
            fullmp3path = pasta_reuniao_selecionada + "/" + ArquivoMP3Renomeado + ".mp3"
  
            labelSelectedFile.config(text = "Arquivo selecionado: " + mp4path.name)
            txtTituloReuniao.focus_set()
            gerarResumoBtn.place(relx=.2, rely=.7)
    else:
        ArquivoMP4 = ""


#Função para identificar que a janela esta sendo fechada e colocar foco na root
def on_closingMeetingWindow():
    MeetingWindow.destroy()
    EscolherArquivo(True)
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

#Função de quando clicar no botão de gerar resumo
def GerarResumoAction(MeetingWindow):
    start_thread("conversao")

############################# Janela MeetingGPT #############################
def AbrirGerarResumo():
    global txtTituloReuniao,MeetingWindow,labelSelectedFile,gerarResumoBtn,labelProgress
    MeetingWindow = Toplevel(root) 
    MeetingWindow.title("Geração de resumos") 
    MeetingWindow.wm_iconbitmap(iconImageFile)
    MeetingWindow.minsize(800,300)
    center(MeetingWindow)
    MeetingWindow.resizable(0,0)
    MeetingWindow.configure(background='#F0FFFF')
    #MeetingWindow.configure(background='#8c8f91')

    label = Label(MeetingWindow,text="Gerar resumo das reuniões",font='Calibri 18 bold', background="#F0FFFF")
    label.place(relx=.01, rely=.0)

    label = Label(MeetingWindow,text='Título da reunião: ', font='Calibri 12 bold', background="#F0FFFF")
    label.place(relx=.01, rely=.19)

    txtTituloReuniao = Text(MeetingWindow, width=45, height=1) 
    txtTituloReuniao.place(relx=.170, rely=.199)
    txtTituloReuniao.focus_set()

    labelSelectedFile = Label(MeetingWindow,text='',font='Calibri 12 bold', fg = '#757575', background="#F0FFFF")
    labelSelectedFile.place(relx=.01,rely=.3)

    selectFileBTN = customtkinter.CTkButton(MeetingWindow,text="Escolher arquivo", command=lambda: EscolherArquivo(False))
    selectFileBTN.place(relx=.01, rely=.7)
    
    gerarResumoBtn = customtkinter.CTkButton(MeetingWindow,text="Gerar Resumo", command=lambda root=root: GerarResumoAction(root))
    
    gerarResumoBtn.place_forget()

    labelProgress = Label(MeetingWindow,text='',font='Calibri 12 bold', fg = '#757575', background="#F0FFFF")
    labelProgress.place(relx=.01,rely=.520)


    MeetingWindow.protocol("WM_DELETE_WINDOW", on_closingMeetingWindow) 
    

#Função para identificar que a janela esta sendo fechada e colocar foco na root
def on_closingRecordWindow():
    RecordWindow.destroy()
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

#Função quando clicar no botão para gravar
def GravarReuniao():
    global gravando
    tituloGravacao = txtTituloReuniao_Gravar.get("1.0",END).strip()
    if gravando:
        gravando = False
        StartRecordBTN.config(fg="black")
        labelRecordingText.config(text = "")
    else:
        if tituloGravacao != "":
            gravando = True
            StartRecordBTN.config(fg="red")
            
            start_thread("gravacao")
        else:
            messagebox.showwarning("Campo vazio/invalido", "Preencha o campo titulo para gerar o resumo", parent=RecordWindow)

############################# Janela Gravar #############################
def AbrirGravarReuniao():
    global txtTituloReuniao_Gravar,RecordWindow,StartRecordBTN, labelRecordingTime, labelRecordingText
    RecordWindow = Toplevel(root) 
    RecordWindow.title("Gravar reuniões") 
    RecordWindow.wm_iconbitmap(iconImageFile)
    RecordWindow.minsize(800,100)
    center(RecordWindow)
    RecordWindow.resizable(0,0)
    RecordWindow.configure(background='#F0FFFF')

    label = Label(RecordWindow,text="Gravar reunião e gerar resumo",font='Calibri 18 bold', background="#F0FFFF")
    label.place(relx=.01, rely=.0)

    label = Label(RecordWindow,text='Título da reunião: ', font='Calibri 12 bold', background="#F0FFFF")
    label.place(relx=.01, rely=.19)

    txtTituloReuniao_Gravar = Text(RecordWindow, width=45, height=1) 
    txtTituloReuniao_Gravar.place(relx=.170, rely=.2)
    txtTituloReuniao_Gravar.focus_set()

    labelRecordingTime = Label(RecordWindow, text="", font='Georgia 13 bold', background="#F0FFFF", width=8, fg='grey') 
   
    StartRecordBTN = Button(RecordWindow, text="🎤",font=("Arial","40","bold"),background="#F0FFFF", border=0.5, activebackground="#F0FFFF", command= GravarReuniao)
    StartRecordBTN.place(relx=.01, rely=.45)

   
    labelRecordingText = Label(RecordWindow, text="", font='Georgia 13 bold', background="#F0FFFF", fg="grey")
    labelRecordingText.place(relx=.170,rely=.6)


    RecordWindow.protocol("WM_DELETE_WINDOW", on_closingRecordWindow) 





############################# Função para abrir URL de informação #############################
def AbreURL(url):
    webbrowser.open(url, new=2)


############################# Função para centralizar as Windows #############################
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

############################# Função para definir imagens de background do TopLevel do Menu Pricipal #############################
def backgroundImage(win):
    IMAGE_PATH = RobotImageFile
    WIDTH, HEIGTH = win.winfo_width(), win.winfo_height()

    canvas = Canvas(win, width=WIDTH, height=HEIGTH)
    canvas.pack()

    img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((WIDTH, HEIGTH), Image.LANCZOS))
    canvas.background = img
    canvas.create_image(0, 0, anchor=NW, image=img)


############################# Root Window com as informações de acesso e primeiras configurações padrões #############################
root = Tk()
menubar = Menu(root,activebackground='#6C24EA', activeforeground='#6C24EA',font="Calibri 13 bold") 
root.config(menu=menubar)

gravando = False
#Menubar Cadastrar Sites    
filemenu = Menu(menubar, tearoff=0, foreground='#6C24EA', font="Calibri 13 bold")
filemenu.add_separator()
filemenu.add_command(label="Gerar Resumo de Reunião", command=AbrirGerarResumo)
filemenu.add_command(label="Gravar reunião", command=AbrirGravarReuniao)
filemenu.add_command(label="Ver resumos", command=AbrirJanelaResumos)
menubar.add_cascade(label="MeetGPT", menu=filemenu)
root.title("Meeting GPT" + " ({})".format(versao)) 
root.wm_iconbitmap(iconImageFile)
root.minsize(1400,600)
center(root)
root.resizable(0,0)
root.configure(background='#F0FFFF')
root.focus_force()

FirstTimeScript(False, None)
LerConfiguracao()

labelNomePrograma = Label(root,font='Calibri 65 bold', text="Meeting AI Summary", bg="#F0FFFF")
labelNomePrograma.place(relx=0.5, rely=0.3, anchor=CENTER) 

labelSlogan = Label(root,font='Calibri 20 bold', text="AI to transcript and summarize meetings", fg="#6C24EA", bg="#F0FFFF")
labelSlogan.place(relx=0.460, rely=0.42, anchor=CENTER)

imgRobot = ImageTk.PhotoImage(Image.open(RobotImageFile).resize((250, 250)))

lblRobot = Label(root,image = imgRobot, cursor="hand2", bg='#F0FFFF')
lblRobot.place(relx=0.460, rely=0.75, anchor=CENTER)

imghelp = ImageTk.PhotoImage(Image.open(InfoImageFile).resize((30, 30)))
labelHelp = Label(root,image = imghelp, cursor="hand2", bg='#F0FFFF')
labelHelp.place(relx=.978, rely=.958)

labelcopyright = Label(root,font='Calibri 10 bold', text="© Valentim Uliana. All rights reserved", bg='#F0FFFF')
labelcopyright.place(relx=.0, rely=.97)

urlInfo = 'https://github.com/ValentimMuniz/Meeting-Summary-with-OpenAI'
labelHelp.bind('<Button-1>', lambda event : AbreURL(urlInfo))
############################# Fim da root Window #############################

'''
############################# Estilizar progress bar e combobox #############################
# tem que colocar aqui porque aplica a todos combos e progress
s = ttk.Style()
s.theme_use('winnative')

TROUGH_COLOR = 'black' 
BG_COLOR = '#F0FFFF'
BAR_COLOR = 'green'
s.configure("bar.Horizontal.TProgressbar", troughcolor=BG_COLOR, bordercolor=TROUGH_COLOR, background=BAR_COLOR, lightcolor=BAR_COLOR, darkcolor=BAR_COLOR)
############################# Estilizar progress bar e combobox #############################
'''

try:
    root.mainloop()
except (KeyboardInterrupt, SystemExit):
    sys.stdout.flush()
    pass
