import streamlit as st
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import base64

# Configuração da página com ícone de espada (tema Zelda)
st.set_page_config(page_title="Assistente Zelda IA", page_icon="🗡️", layout="wide")

# Carrega variáveis do .env
load_dotenv()
stability_api_key = os.getenv("STABILITY_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Inicializa Gemini
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    st.error("API Key do Gemini não encontrada.")

# Estilo da página com tema de Zelda + customização dos campos de entrada
st.markdown("""
    <style>
        .stApp {
            background-image: url("https://images8.alphacoders.com/923/thumb-1920-923533.jpg");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            font-family: 'Georgia', serif;
            color: #fffbe0;
        }

        .main > div {
            display: flex;
            justify-content: center;
        }

        .chat-bubble-user {
            background-color: #4c8b5d;
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            text-align: right;
            display: inline-block;
            max-width: 80%;
            margin-left: auto;
            word-wrap: break-word;
            float: right;
            clear: both;
        }

        .chat-bubble-bot {
            background-color: #2f4f2f;
            color: #fffbe0;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            text-align: left;
            display: inline-block;
            max-width: 80%;
            margin-right: auto;
            word-wrap: break-word;
            float: left;
            clear: both;
        }

        .input-container {
            display: flex;
            width: 100%;
            margin-top: 1rem;
            align-items: center;
        }

        input[type="text"], textarea {
            background-color: rgba(60, 85, 60, 0.85) !important;
            color: #fffbe0 !important;
            border-radius: 15px !important;
            border: 2px solid #d4af37 !important;
            padding: 1.3rem 1.5rem !important;
            font-size: 20px !important;
            width: 100% !important;
            max-width: 100% !important;
            text-align: center !important;
        }

        textarea {
            height: 140px !important;
        }

        .send-button {
            background-color: #3c6e47;
            border-radius: 50%;
            padding: 0.8rem 0.9rem;
            border: 2px solid #d4af37;
            cursor: pointer;
            font-size: 20px;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 3.5rem;
            width: 3.5rem;
        }

        .send-button:hover {
            background-color: #4c8b5d;
            transition: 0.3s ease-in-out;
        }

        .input-label-container {
            width: 100%;
            display: flex;
            justify-content: center;
            margin-bottom: 0.3rem;
        }

        .input-label {
            font-size: 16px !important;
            font-weight: bold;
            color: #fffbe0 !important;
        }

        h2 {
            color: #fffbe0;
            margin-top: 2rem;
            font-size: 26px;
            text-align: center;
        }

        img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Função para converter imagem para base64
def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Título e ícone da Triforce
st.title("🗡️ Assistente de Hyrule IA")
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Triforce.svg/1024px-Triforce.svg.png", width=100)

# Função para gerar resposta com Gemini
def generate(prompt_text):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"Erro ao gerar resposta com Gemini: {e}"

# Função para gerar imagem com Stability AI
def gerar_imagem_stability(prompt_text, api_key):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*",
    }
    files = {
        "prompt": (None, prompt_text),
    }
    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return image
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Erro HTTP: {http_err.response.text}")
        return None
    except Exception as e:
        st.error(f"Erro ao gerar imagem: {e}")
        return None

# Inicializa estado da sessão
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mostrar_gerar_imagem" not in st.session_state:
    st.session_state.mostrar_gerar_imagem = False

# Título centralizado
st.markdown("""
<div style="background-color: rgba(0,0,0,0.4); padding: 30px; border-radius: 18px; text-align: center; box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);">
    <h1 style="color: #fffbe0;">Como posso ajudar o Herói de Hyrule?</h1>
</div>
""", unsafe_allow_html=True)

# Entrada de texto e botão enviar
with st.container():
    st.markdown("<div class='input-label-container'><label class='input-label'>Digite uma pergunta ou comando...</label></div>", unsafe_allow_html=True)
    col_input, col_button = st.columns([9, 1])
    with col_input:
        user_input = st.text_input("", placeholder="", label_visibility="collapsed", key="pergunta_usuario")
    with col_button:
        enviar = st.button("\u27a4", use_container_width=True)

# Processa a entrada
if enviar:
    if not gemini_api_key:
        st.error("API Key do Gemini não encontrada.")
    elif not user_input:
        st.warning("Por favor, digite algo.")
    else:
        st.session_state.chat_history.append({"sender": "user", "message": user_input})
        with st.spinner("Invocando sabedoria ancestral..."):
            resposta = generate(user_input)
            st.session_state.chat_history.append({"sender": "bot", "message": resposta})

# Exibe histórico de mensagens
for msg in st.session_state.chat_history:
    if msg["sender"] == "user":
        st.markdown(f"""
            <div class='chat-bubble-user'><b>Você:</b><br>{msg["message"]}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='chat-bubble-bot'><b>Oráculo:</b><br>{msg["message"]}</div>
        """, unsafe_allow_html=True)

# Alternar modo imagem
if st.button("🎨 Alternar modo: Gerar Imagem"):
    st.session_state.mostrar_gerar_imagem = not st.session_state.mostrar_gerar_imagem

# Interface de geração de imagem
if st.session_state.mostrar_gerar_imagem:
    with st.container():
        st.subheader("🌌 Criar Visão da Pedra Sheikah")
        st.markdown("<div class='input-label-container'><label class='input-label'>Descreva sua visão mística:</label></div>", unsafe_allow_html=True)

        col_img1, col_img2 = st.columns([9, 1])
        with col_img1:
            prompt_imagem = st.text_input("", placeholder="", label_visibility="collapsed", key="imagem_input")
        with col_img2:
            gerar = st.button("🎨", help="Gerar imagem")

        if gerar:
            if not stability_api_key:
                st.error("API Key da Stability AI não encontrada.")
            elif not prompt_imagem:
                st.warning("Por favor, descreva a imagem.")
            else:
                with st.spinner("Desenhando visão mística..."):
                    imagem = gerar_imagem_stability(prompt_imagem, stability_api_key)
                    if imagem:
                        st.markdown(
                            f"""
                            <div class='chat-box' style='text-align:center'>
                                <b>Visão da Pedra Sheikah:</b><br><br>
                                <img src='data:image/png;base64,{image_to_base64(imagem)}' width='100%' style='border-radius: 10px; margin-top: 1rem; max-width: 100%;'/>
                            </div>
                            """,
                            unsafe_allow_html=True)
