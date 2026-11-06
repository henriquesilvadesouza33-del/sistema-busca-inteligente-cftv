import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import threading
import os
import pyttsx3
from PIL import Image, ImageTk

# --- CONFIGURAÇÃO DO AGENTE COGNITIVO (ESTILO TONY STARK) ---
class AssistenteVirtual:
    def __init__(self):
        self.mutex = threading.Lock()
        
    def falar(self, texto):
        def _falar():
            with self.mutex:
                engine = pyttsx3.init()
                engine.setProperty('rate', 160) 
                voices = engine.getProperty('voices')
                for voice in voices:
                    if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.say(texto)
                engine.runAndWait()
        threading.Thread(target=_falar, daemon=True).start()

# Inicializa o agente de IA
assistente = AssistenteVirtual()

# --- VARIÁVEIS GLOBAIS DE CONTROLE MULTIMODO ---
caminho_alvo = ""
caminho_video = ""
pasta_evidencias = "Evidencias_Encontradas"

def alternar_modo():
    # Limpa as seleções atuais ao mudar de modo para evitar conflitos
    global caminho_alvo, caminho_video
    caminho_alvo = ""
    caminho_video = ""
    
    if var_modo.get() == "individual":
        btn_foto.config(text="CARREGAR UMA FOTO")
        lbl_status_foto.config(text="Aguardando arquivo de foto...", fg="#888888")
        btn_video.config(text="SELECIONAR UM VÍDEO")
        lbl_status_video.config(text="Aguardando arquivo de vídeo...", fg="#888888")
        btn_iniciar.config(text="INICIAR INVESTIGAÇÃO INDIVIDUAL (IA)")
    else:
        btn_foto.config(text="CARREGAR PASTA DE ALVOS")
        lbl_status_foto.config(text="Aguardando pasta de alvos...", fg="#888888")
        btn_video.config(text="SELECIONAR FILA DE VÍDEOS")
        lbl_status_video.config(text="Aguardando fila de vídeos...", fg="#888888")
        btn_iniciar.config(text="INICIAR INVESTIGAÇÃO EM MASSA (IA)")

def acao_selecionar_alvo():
    global caminho_alvo
    if var_modo.get() == "individual":
        caminho_alvo = filedialog.askopenfilename(title="Selecionar Foto do Suspeito", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if caminho_alvo:
            lbl_status_foto.config(text=f"✓ {os.path.basename(caminho_alvo)}", fg="#00FF66")
            txt_console.insert(tk.END, "[ASSISTENTE]: Foto do alvo individual carregada com sucesso.\n", "info")
            assistente.falar("Assinatura biométrica individual carregada. Aguardando arquivo de vídeo.")
    else:
        caminho_alvo = filedialog.askdirectory(title="Selecionar Pasta com Fotos dos Suspeitos")
        if caminho_alvo:
            arquivos = [f for f in os.listdir(caminho_alvo) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            lbl_status_foto.config(text=f"✓ {len(arquivos)} Alvos Carregados", fg="#00FF66")
            txt_console.insert(tk.END, f"[ASSISTENTE]: Base de dados biométrica indexada com {len(arquivos)} suspeitos.\n", "info")
            assistente.falar(f"Banco de dados biométrico indexado com {len(arquivos)} suspeitos em lote. Aguardando fila de mídia.")

def acao_selecionar_video():
    global caminho_video
    if var_modo.get() == "individual":
        caminho_video = filedialog.askopenfilename(title="Selecionar Vídeo do CFTV", filetypes=[("Vídeos", "*.mp4 *.avi *.mkv")])
        if caminho_video:
            lbl_status_video.config(text=f"✓ {os.path.basename(caminho_video)}", fg="#00FF66")
            txt_console.insert(tk.END, "[ASSISTENTE]: Mídia individual de CFTV indexada ao sistema.\n", "info")
            assistente.falar("Feed de vídeo individual indexado. Pronto para iniciar a varredura, senhor.")
    else:
        caminho_video = filedialog.askdirectory(title="Selecionar Pasta com Vídeos do CFTV")
        if caminho_video:
            arquivos = [f for f in os.listdir(caminho_video) if f.lower().endswith(('.mp4', '.avi', '.mkv'))]
            lbl_status_video.config(text=f"✓ {len(arquivos)} Vídeos na Fila", fg="#00FF66")
            txt_console.insert(tk.END, f"[ASSISTENTE]: Fila de análise criada com {len(arquivos)} arquivos de vídeo.\n", "info")
            assistente.falar(f"Fila de análise criada com {len(arquivos)} vídeos. Pronto para iniciar a varredura multicanais, senhor.")

def limpar_sistema():
    global caminho_alvo, caminho_video
    caminho_alvo = ""
    caminho_video = ""
    alternar_modo()
    txt_console.delete("1.0", tk.END)
    txt_console.insert(tk.END, "[SISTEMA]: Memória volátil limpa. Painel operacional redefinido.\n", "info")
    lbl_painel_foto.config(image="", text="[NENHUMA IMAGEM\nCAPTURADA ATÉ O MOMENTO]")
    lbl_painel_foto.image = None
    assistente.falar("Terminal redefinido. Dados limpos, senhor.")

def abrir_registros_anteriores():
    if os.path.exists(pasta_evidencias):
        os.startfile(os.path.abspath(pasta_evidencias))
        txt_console.insert(tk.END, f"[SISTEMA]: Acessando diretório de arquivos e registros anteriores.\n", "info")
        assistente.falar("Abrindo arquivo de registros e buscas anteriores.")
    else:
        messagebox.showinfo("Histórico", "Nenhum registro anterior encontrado no sistema.")
        assistente.falar("Nenhum banco de dados de histórico foi localizado ainda.")

def iniciar_ia():
    if not caminho_alvo or not caminho_video:
        messagebox.showwarning("Erro", "Por favor, selecione os dados de alvos e mídias antes de iniciar!")
        return
    threading.Thread(target=processar_investigacao, daemon=True).start()

def atualizar_foto_painel(frame_cv):
    frame_rgb = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(frame_rgb)
    img_pil = img_pil.resize((230, 170), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    lbl_painel_foto.config(image=img_tk)
    lbl_painel_foto.image = img_tk
def processar_investigacao():
    btn_iniciar.config(state=tk.DISABLED, bg="#333333", text="SISTEMA OCUPADO...")
    txt_console.insert(tk.END, "\n[SISTEMA]: Inicializando varredura inteligente no perímetro...\n", "info")
    txt_console.see(tk.END)
    assistente.falar("Iniciando busca inteligente no perímetro da nova capital do brasil. Vasculhando banco de dados.")

    try:
        if not os.path.exists(pasta_evidencias):
            os.makedirs(pasta_evidencias)

        # 1. PREPARAÇÃO DOS ALVOS (INDIVIDUAL OU LOTE)
        banco_suspeitos = {}
        if var_modo.get() == "individual":
            img_g = cv2.imread(caminho_alvo, cv2.IMREAD_GRAYSCALE)
            if img_g is not None:
                img_g = cv2.resize(img_g, (100, 100))
                nome_sujeito = os.path.splitext(os.path.basename(caminho_alvo))[0].upper()
                banco_suspeitos[nome_sujeito] = img_g
        else:
            lista_fotos = [f for f in os.listdir(caminho_alvo) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for foto in lista_fotos:
                caminho_completo_foto = os.path.join(caminho_alvo, foto)
                img_g = cv2.imread(caminho_completo_foto, cv2.IMREAD_GRAYSCALE)
                if img_g is not None:
                    img_g = cv2.resize(img_g, (100, 100))
                    nome_sujeito = os.path.splitext(foto)[0].upper()
                    banco_suspeitos[nome_sujeito] = img_g

        # 2. PREPARAÇÃO DA FILA DE VÍDEOS (INDIVIDUAL OU LOTE)
        lista_videos = []
        if var_modo.get() == "individual":
            lista_videos.append(caminho_video)
        else:
            lista_videos = [os.path.join(caminho_video, f) for f in os.listdir(caminho_video) if f.lower().endswith(('.mp4', '.avi', '.mkv'))]

        descobertas = 0
        registros_alertas = []
        detector_faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Varre cada vídeo da fila
        for caminho_completo_video in lista_videos:
            video = cv2.VideoCapture(caminho_completo_video)
            fps = video.get(cv2.CAP_PROP_FPS) if video.get(cv2.CAP_PROP_FPS) > 0 else 30
            frame_count = 0
            
            nome_camera = os.path.splitext(os.path.basename(caminho_completo_video))[0].upper()
            txt_console.insert(tk.END, f"[FILA]: Analisando canal: {nome_camera}...\n", "info")
            txt_console.see(tk.END)

            while video.isOpened():
                sucesso, frame = video.read()
                if not sucesso:
                    break
                
                frame_count += 1
                if frame_count % int(fps) != 0:
                    continue

                frame_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector_faces.detectMultiScale(frame_cinza, 1.1, 4)

                for (x, y, w, h) in faces:
                    rosto_recortado = frame_cinza[y:y+h, x:x+w]
                    rosto_recortado = cv2.resize(rosto_recortado, (100, 100))

                    for nome_alvo, img_alvo in banco_suspeitos.items():
                        erro = np.sum((img_alvo.astype("float") - rosto_recortado.astype("float")) ** 2)
                        erro /= float(img_alvo.shape[0] * img_alvo.shape[1])

                        if erro < 4000:  
                            descobertas += 1
                            segundos_totais = int(frame_count / fps)
                            minutos = segundos_totais // 60
                            segundos = segundos_totais % 60
                            
                            tempo_formatado = f"{minutos:02d}:{segundos:02d}"
                            txt_console.insert(tk.END, f"[ALERTA CRÍTICO]: {nome_alvo} identificado em {nome_camera} aos {tempo_formatado}!\n", "alerta")
                            txt_console.see(tk.END)
                            
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, nome_alvo, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            
                            janela.after(0, atualizar_foto_painel, frame)
                            
                            foto_nome = f"flagrante_{nome_alvo}_{nome_camera}_{minutos:02d}_{segundos:02d}.jpg"
                            caminho_foto = os.path.join(pasta_evidencias, foto_nome)
                            registros_alertas.append(f"- [{nome_alvo}] localizado em [{nome_camera}] na linha do tempo: {tempo_formatado} -> Registro: {foto_nome}")
                            
                            cv2.imwrite(caminho_foto, frame)
                            assistente.falar(f"Atenção. Alvo {nome_alvo} localizado na câmera {nome_camera}.")

            video.release()

        # CRIAÇÃO DO RELATÓRIO
        nome_relatorio = os.path.join(pasta_evidencias, "Relatorio_Analise_CFTV_Hibrido.txt")
        with open(nome_relatorio, "w", encoding="utf-8") as f:
            f.write("===================================================\n")
            f.write("   NOVACAP - RELATÓRIO DE INTELIGÊNCIA HÍBRIDO     \n")
            f.write("===================================================\n\n")
            f.write(f"Modo de Operação: {var_modo.get().upper()}\n")
            f.write(f"Total de Suspeitos Mapeados: {len(banco_suspeitos)}\n")
            f.write(f"Total de Câmeras/Vídeos Scaneados: {len(lista_videos)}\n")
            f.write(f"Total Geral de Ocorrências Identificadas: {descobertas}\n\n")
            f.write("CRONOLOGIA E HISTÓRICO DE ACARIAÇÃO:\n")
            if descobertas > 0:
                for reg in registros_alertas:
                    f.write(f"{reg}\n")
            else:
                f.write("- Nenhuma correspondência de segurança detectada na varredura.\n")
            f.write("\n===================================================\n")
            f.write("Fim do Relatório Técnico Autônomo. Protocolo Schubert.\n")

        txt_console.insert(tk.END, f"\n[FIM]: Varredura concluída. {descobertas} capturas salvas.\n", "info")
        txt_console.insert(tk.END, f"[SISTEMA]: Relatório global emitido em '{nome_relatorio}'.\n", "info")
        txt_console.see(tk.END)
        
        if descobertas > 0:
            assistente.falar("Busca inteligente finalizada, senhor. Foram encontradas correspondências válidas. Relatório consolidado gravado.")
            os.startfile(os.path.abspath(pasta_evidencias))
        else:
            assistente.falar("Varredura concluída. Nenhuma assinatura correspondente foi detectada.")
        
    except Exception as e:
        txt_console.insert(tk.END, f"[ERRO NO AGENTE]: {str(e)}\n", "erro")
    
    alternar_modo()

# --- INTERFACE VISUAL CYBERPUNK ---
janela = tk.Tk()
janela.title("PROJETO SCHUBERT INVESTIGAÇÃO - NOVACAP")
janela.geometry("920x660")
janela.configure(bg="#0D0F12")

# BLOCO DA LOGOMARCA ATUALIZADA (ESTICADA EM ESCALA RETANGULAR)
frame_topo = tk.Frame(janela, bg="#0D0F12")
frame_topo.pack(pady=10, fill="x", padx=20)

try:
    # Carrega e Redimensiona a foto em formato horizontal esticado largo
    img_logo = Image.open("logo_novacap.png")
    img_logo = img_logo.resize((170, 55), Image.Resampling.LANCZOS)
    logo_tk = ImageTk.PhotoImage(img_logo)
    lbl_logo = tk.Label(frame_topo, image=logo_tk, bg="#0D0F12")
    lbl_logo.image = logo_tk
    lbl_logo.pack(side="left", padx=(0, 15))
except Exception:
    pass

frame_titulos = tk.Frame(frame_topo, bg="#0D0F12")
frame_titulos.pack(side="left")

lbl_titulo = tk.Label(frame_titulos, text="SISTEMA DE BUSCA INTELIGENTE CFTV", font=("Courier New", 16, "bold"), bg="#0D0F12", fg="#00FFFF")
lbl_titulo.pack(anchor="w")

lbl_subtitulo = tk.Label(frame_titulos, text="SISTEMA AUTÔNOMO DE DEFESA E RASTREIO - NOVACAP", font=("Arial", 9, "bold"), bg="#0D0F12", fg="#FF007F")
lbl_subtitulo.pack(anchor="w", pady=2)

# SELETOR DE MODO (INDIVIDUAL OU EM LOTE)
frame_modos = tk.LabelFrame(janela, text=" DIRETRIZ DE ESCALA (SELECIONE O MODO DE OPERAÇÃO) ", font=("Arial", 8, "bold"), bg="#0D0F12", fg="#00FFFF", bd=1, relief="flat")
frame_modos.pack(fill="x", padx=20, pady=5)

var_modo = tk.StringVar(value="lote") # Padrão inicia em lote

rb_lote = tk.Radiobutton(frame_modos, text="MODO EM MASSA / CONJUNTO (LOTE)", variable=var_modo, value="lote", font=("Arial", 9, "bold"), bg="#0D0F12", fg="#00FF66", selectcolor="#05070A", activebackground="#0D0F12", activeforeground="#00FF66", command=alternar_modo)
rb_lote.pack(side="left", padx=20, pady=5)

rb_individual = tk.Radiobutton(frame_modos, text="MODO INDIVIDUAL (1 FOTO / 1 VÍDEO)", variable=var_modo, value="individual", font=("Arial", 9, "bold"), bg="#0D0F12", fg="#FFFF00", selectcolor="#05070A", activebackground="#0D0F12", activeforeground="#FFFF00", command=alternar_modo)
rb_individual.pack(side="left", padx=20, pady=5)

# CONTAINER PRINCIPAL
frame_container = tk.Frame(janela, bg="#0D0F12")
frame_container.pack(fill="both", expand=True, padx=20, pady=5)

# LADO ESQUERDO
lado_esquerdo = tk.Frame(frame_container, bg="#0D0F12")
lado_esquerdo.pack(side="left", fill="both", expand=True)

frame_foto = tk.Frame(lado_esquerdo, bg="#161920", bd=2, relief="groove")
frame_foto.pack(fill="x", pady=5)
btn_foto = tk.Button(frame_foto, text="CARREGAR PASTA DE ALVOS", font=("Arial", 9, "bold"), bg="#FF007F", fg="white", width=25, command=acao_selecionar_alvo)
btn_foto.pack(side="left", padx=10, pady=10)
lbl_status_foto = tk.Label(frame_foto, text="Aguardando pasta de alvos...", font=("Arial", 8, "italic"), bg="#161920", fg="#888888")
lbl_status_foto.pack(side="left", padx=10)

frame_video = tk.Frame(lado_esquerdo, bg="#161920", bd=2, relief="groove")
frame_video.pack(fill="x", pady=5)
btn_video = tk.Button(frame_video, text="SELECIONAR FILA DE VÍDEOS", font=("Arial", 9, "bold"), bg="#00FFFF", fg="black", width=25, command=acao_selecionar_video)
btn_video.pack(side="left", padx=10, pady=10)
lbl_status_video = tk.Label(frame_video, text="Aguardando fila de vídeos...", font=("Arial", 8, "italic"), bg="#161920", fg="#888888")
lbl_status_video.pack(side="left", padx=10)

btn_iniciar = tk.Button(lado_esquerdo, text="INICIAR INVESTIGAÇÃO EM MASSA (IA)", font=("Arial", 11, "bold"), bg="#00FF66", fg="black", height=2, command=iniciar_ia)
btn_iniciar.pack(fill="x", pady=10)

frame_controles_rodape = tk.Frame(lado_esquerdo, bg="#0D0F12")
frame_controles_rodape.pack(fill="x", pady=5)

btn_limpar = tk.Button(frame_controles_rodape, text="✕ LIMPAR PAINEL", font=("Arial", 9, "bold"), bg="#444444", fg="white", width=22, command=limpar_sistema)
btn_limpar.pack(side="left", padx=(0, 10))

btn_historico = tk.Button(frame_controles_rodape, text="📂 BUSCAS ANTERIORES", font=("Arial", 9, "bold"), bg="#1A365D", fg="#00FFFF", width=22, command=abrir_registros_anteriores)
btn_historico.pack(side="left")

lbl_console = tk.Label(lado_esquerdo, text="INTERFACE COGNITIVA DO AGENTE:", font=("Arial", 9, "bold"), bg="#0D0F12", fg="#FFFFFF")
lbl_console.pack(anchor="w", pady=(10, 0))

txt_console = tk.Text(lado_esquerdo, height=8, bg="#05070A", fg="#00FF66", font=("Courier New", 9), insertbackground="#00FF66")
txt_console.pack(fill="both", expand=True, pady=5)

txt_console.tag_config("info", foreground="#00FFFF")
txt_console.tag_config("alerta", foreground="#FFFF00", background="#222200")
txt_console.tag_config("erro", foreground="#FF007F")

# LADO DIREITO
lado_direito = tk.Frame(frame_container, bg="#161920", bd=2, relief="groove", width=250)
lado_direito.pack(side="right", fill="both", padx=(15, 0), pady=5)
lado_direito.pack_propagate(False)

lbl_titulo_painel = tk.Label(lado_direito, text="ÚLTIMO FLAGRANTE CFTV", font=("Arial", 9, "bold"), bg="#161920", fg="#FFFF00")
lbl_titulo_painel.pack(pady=10)

lbl_painel_foto = tk.Label(lado_direito, bg="#05070A", text="[NENHUMA IMAGEM\nCAPTURADA ATÉ O MOMENTO]", font=("Arial", 9, "italic"), fg="#444444")
lbl_painel_foto.pack(fill="both", expand=True, padx=10, pady=10)

txt_console.insert(tk.END, "[SISTEMA]: Agente virtual online. Protocolo Schubert ativo.\n", "info")
assistente.falar("Sistêma online. Diretrizes de segurança da nova capital do brasil carregadas. Bom dia, senhôr.")

# --- ASSINATURA DO DESENVOLVEDOR (RODAPÉ) ---
lbl_assinatura = tk.Label(janela, text="Este sistema foi desenvolvido por Henrique Silva de Souza", font=("Arial", 8), bg="#0D0F12", fg="#555555")
lbl_assinatura.pack(side="bottom", pady=5)

janela.mainloop()
