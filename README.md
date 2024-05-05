# Meeting Summary with OpenAI - STREAMLIT
Desenvolvido por: Valentim Uliana

Essa aplicação tem como intuito a facilitação no dia-dia de quem faz muitas reuniões, onde a partir de reunião, é possível gerar um resumo usando o ChatGPT e trazer tudo que foi acordado numa reunião, desde tópicos abordados até  próximos passos.

# Requisitos
   Python 3.8+ (para caso queira ver e rodar o código atráves de um IDE)<br>
   Testado com sistema operacional Windows.
   [OpenAI](https://platform.openai.com/docs/introduction) - Utilizado a API do OpenAI para fazer o resumo das reuniões (para isso foi pago, por exemplo, eu comprei $5 e já upei mais de 50 reuniões e ainda tenho créditos)<br>
   Use: <b>pip install -r requirements.txt</b> para instalar as bibliotecas necessárias<br>

# Features
1. Pode fazer o upload de um arquivo MP4, gravado de uma reunião
2. Gravação nativa do sistema operacional na saída e entrada de aúdio (real-time).
3. Interface amigável
4. Pode ver os resumos direto na interface
5. Arquivo de configuração, para setar chave API e tempo de gravação mínimo de uma reunião (padrão 1 min). Esse arquivo fica em: MeetGPTv2/config
6. Arquivo com prompt com as pré-definições para fazer o resumo junto ao ChatGPT.

<b>Prompt padrão:</b>
```
   PROMPT = '''
      Somos da empresa Yssy, empresa de tecnologia que atende diversas frentes.
      Faça o resumo do texto delimitado por #### 
      O texto é a transcrição de uma reunião.
      Tente identificar se foi citado nesse texto de algum cliente e colocar no nome dele.
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
   ```
   
# Como utilizar
1. Primeiramente, é ter o consentimento para gravar uma reunião
2. Os arquivos criados vão todos para uma pasta chamada <b>.MeetGPTv2</b> na pasta HOME do usuário do sistema operacional (ex: Windows vai para <b>C:\Users\Valentim-Home</b>), dentro dessa pasta será criada a pasta das reuniões que vai conter todas as reuniões salvas com resumo, titulo, audio convertido e a transcrição.
3. Na primeira vez que rodar a aplicação, vai ser pedido para informar a sua chave de API do OpenAI. Caso tenha colocado errado é possivel editar no arquivo de configuração. [Para pegar sua chave API](https://platform.openai.com/api-keys)
4. Módulos da aplicação<br>
   <b>a) Conversão de arquivo MP4:</b> A aplicação vai transformar o MP4 em áudio, transcrever esse aúdio para texto usando o modelo whisper-1 do OpenAI e depois fazer um resumo usando o ChatGPT. O título da reunião é obrigatório.<br>
   <b>b) Gravação de aúdio em real-time:</b> A aplicação vai gravar o áudio do seu computador, transcrever esse aúdio para texto usando o modelo whisper-1 do OpenAI e depois fazer um resumo usando o ChatGPT. O título da reunião é obrigatório.<br>
6. Foi usado um pyinstaller para gerar o .exe dessa aplicação, basta iniciar o arquivo meetingsummarize.exe para começar a usá-la.
7. Caso não queira usar o .exe, basta rodar a aplicação com o python ``` python ./meetingsummarize.py ```
9. Após a reunião tiver um resumo pronto, sendo ela convertida de um mp4 ou sendo gravada em real-time, ele vai para a ABA <b>"Ver Resumos"</b>. Após isso a reunião vai aparecer para você já resumida.

#Imagens
<img src="images/meet1.png"><br><br>
<img src="images/meet2.png"><br><br>
<img src="images/meet3.png"><br><br>
<img src="images/meet4.png"><br><br>

Para exemplo aqui usei uma entrevista de futebol.
<img src="images/meet5.png"><br><br>
# TODO list
* [ ] Implementar reconhecimento de fala através do microfone para fazer resumo em real-time da reunião (porém todos tem que estar presencialmente numa mesma sala, estou estudando se tem outra maneira de integrar com GoogleMeet, MSTEAMS etc.)
* [ ] Implementar para reconhecer quantos tokens vao ser utilizados, para que use o modelo mais adequado do OpenAI, fazendo com que gaste menos. Hoje esta sendo utilizado sempre o <b>gpt-4-turbo.</b>
* [ ] Implementar para passar o prompt padrão como parâmetro ou arquivo de texto </b>
* [ ] Fazer que a chave do OPENAI venha do arquivo .env, por enquanto esta no código </b>
* [ ] Comentar as linhas que faltam do código para melhor entendimento da comunidade</b>
