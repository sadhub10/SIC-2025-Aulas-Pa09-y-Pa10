# =========================================================
# src/app.py - PyBrAIn | Digital Modulation Classifier (CNN)
# =========================================================

import base64
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import streamlit as st
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms

# =========================================================
# CONFIG APP
# =========================================================
st.set_page_config(
    page_title="PyBrAIn | Clasificador de Modulaciones",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# RUTAS (compatibles con tu estructura real)
# =========================================================
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent

ASSETS_DIR = ROOT_DIR / "assets"
NOTEBOOK_DIR = ROOT_DIR / "notebook"
LOGS_DIR = ROOT_DIR / "logs"
IMG_LOG_DIR = LOGS_DIR / "images"
CSV_LOG_PATH = LOGS_DIR / "history.csv"

CSS_PATH = ASSETS_DIR / "styles.css"
LOGO_PATH = ASSETS_DIR / "logo.png"
MODEL_PATH = NOTEBOOK_DIR / "modelo_senalesIA.pth"

LOGS_DIR.mkdir(exist_ok=True)
IMG_LOG_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# CSS
# =========================================================
def load_css():
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"No se encontró styles.css en: {CSS_PATH}")

load_css()

# =========================================================
# LOGO (base64)
# =========================================================
LOGO_B64 = None
if LOGO_PATH.exists():
    with open(LOGO_PATH, "rb") as f:
        LOGO_B64 = base64.b64encode(f.read()).decode("utf-8")

# =========================================================
# CLASES
# =========================================================
CLASS_NAMES = [
    'ASK_16', 'ASK_2', 'ASK_32', 'ASK_4', 'ASK_64', 'ASK_8',
    'FSK_16', 'FSK_2', 'FSK_32', 'FSK_4', 'FSK_64', 'FSK_8',
    'PSK_16', 'PSK_2', 'PSK_32', 'PSK_4', 'PSK_64', 'PSK_8',
    'QAM_16', 'QAM_4', 'QAM_64', 'QAM_8'
]

HIDDEN_FSK = {'FSK_2', 'FSK_4', 'FSK_8', 'FSK_16', 'FSK_32', 'FSK_64'}

IMG_SIZE = 96
device = torch.device("cpu")

# =========================================================
# ESTADO DE SESIÓN
# =========================================================
if "last_pred_class" not in st.session_state:
    st.session_state["last_pred_class"] = None
    st.session_state["last_pred_conf"] = None
    st.session_state["last_prob_dict"] = None
    st.session_state["last_img_filename"] = None

# =========================================================
# MODELO (ResNet-like)
# =========================================================
class BasicBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_ch)

        self.shortcut = nn.Sequential()
        if in_ch != out_ch:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, kernel_size=1),
                nn.BatchNorm2d(out_ch),
            )

    def forward(self, x):
        identity = self.shortcut(x)
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = out + identity
        return F.relu(out)


class ModulationResNet(nn.Module):
    def __init__(self, num_classes: int, img_size: int = 96):
        super().__init__()
        self.conv_in = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn_in = nn.BatchNorm2d(32)

        self.block1 = BasicBlock(32, 64)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.block2 = BasicBlock(64, 128)
        self.pool2 = nn.MaxPool2d(2, 2)

        self.block3 = BasicBlock(128, 256)
        self.pool3 = nn.MaxPool2d(2, 2)

        feat_dim = 256 * (img_size // 8) * (img_size // 8)
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(feat_dim, 512)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = F.relu(self.bn_in(self.conv_in(x)))
        x = self.pool1(self.block1(x))
        x = self.pool2(self.block2(x))
        x = self.pool3(self.block3(x))
        x = x.view(x.size(0), -1)
        x = self.dropout(F.relu(self.fc1(x)))
        return self.fc2(x)


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        st.error(f"Model file not found: {MODEL_PATH}")
        st.stop()

    model = ModulationResNet(num_classes=len(CLASS_NAMES), img_size=IMG_SIZE)
    state = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model

model = load_model()

# =========================================================
# PREPROCESAMIENTO + PREDICCIÓN
# =========================================================
def get_preprocess():
    return transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5]),
    ])

def predict_image(pil_img: Image.Image):
    preprocess = get_preprocess()
    x = preprocess(pil_img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    idx = int(np.argmax(probs))
    pred_class = CLASS_NAMES[idx]
    prob_dict = {name: float(p) for name, p in zip(CLASS_NAMES, probs)}
    return pred_class, prob_dict

# =========================================================
# SNR (heurística por confianza)
# =========================================================
def get_snr_info(confidence: float):
    if confidence >= 0.80:
        return "HIGH", "snr-high", "Excelente calidad de señal (ruido mínimo)"
    elif confidence >= 0.50:
        return "MEDIUM", "snr-medium", "Calidad moderada (interferencia presente)"
    else:
        return "LOW", "snr-low", "Baja calidad (ruido/interferencia alta)"

# =========================================================
# LOGGING (CSV + imagen con acrónimo)
# =========================================================
def ensure_history_csv():
    if not CSV_LOG_PATH.exists():
        df = pd.DataFrame(columns=[
            "timestamp",
            "modulation",
            "confidence_pct",
            "snr_level",
            "image_file",
        ])
        df.to_csv(CSV_LOG_PATH, index=False)

def save_uploaded_image(pil_img: Image.Image, modulation: str) -> str:
    """Guarda imagen con acrónimo de la señal detectada"""
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Extraer familia (ASK, PSK, QAM, FSK)
    acronym = modulation.split("_")[0] if "_" in modulation else modulation
    filename = f"{acronym}_{ts}.png"
    out_path = IMG_LOG_DIR / filename
    pil_img.save(out_path)
    return filename

def append_history_row(modulation: str, confidence: float, snr_level: str, image_file: str):
    ensure_history_csv()
    row = {
        "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modulation": modulation,
        "confidence_pct": round(confidence * 100, 2),
        "snr_level": snr_level,
        "image_file": image_file,
    }
    df_old = pd.read_csv(CSV_LOG_PATH)
    df_new = pd.concat([df_old, pd.DataFrame([row])], ignore_index=True)
    df_new.to_csv(CSV_LOG_PATH, index=False)

def read_history():
    ensure_history_csv()
    return pd.read_csv(CSV_LOG_PATH)

# =========================================================
# UI
# =========================================================
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

st.markdown("""
<div class="header-section">
  <h1 class="main-title">PyBrAIn – Clasificador de Modulación Digital</h1>
  <p class="subtitle">CNN Supervisada (End-to-End) | ASK · PSK · QAM</p>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.8], gap="large")

# -----------------------------
# IZQUIERDA: UPLOAD + ACCIONES
# -----------------------------
with col_left:
    st.markdown('<div class="section-title">Entrada de Señal</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Adjuntar imagen de la señal (PNG, JPG)",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
        key="uploader",
    )

    pil_img = None
    if uploaded_file is not None:
        pil_img = Image.open(uploaded_file).convert("RGB")
        st.markdown('<div class="image-preview">', unsafe_allow_html=True)
        st.image(pil_img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    analyze_clicked = st.button("ANALIZAR SEÑAL", disabled=(pil_img is None))

    # Detalles sistema
    with st.expander("Detalles del Sistema entrenado"):
        st.markdown(f"""
        **Modelo** CNN tipo ResNet (bloques residuales)  
        **Tamaño de entrada** {IMG_SIZE}×{IMG_SIZE}px (grayscale)  
        **Clases** {len(CLASS_NAMES)} (incluye FSK; demo puede ocultarlas)  
        **Salida** Softmax multiclase  
        """)

# -----------------------------
# DERECHA: RESULTADO + LOGS
# -----------------------------
with col_right:
    st.markdown('<div class="section-title">Resultados</div>', unsafe_allow_html=True)

    if analyze_clicked and pil_img is not None:
        with st.spinner("Procesando señal..."):
            pred_class, prob_dict = predict_image(pil_img)
            max_prob = float(max(prob_dict.values()))

            st.session_state["last_pred_class"] = pred_class
            st.session_state["last_pred_conf"] = max_prob
            st.session_state["last_prob_dict"] = prob_dict

            # Guardar imagen CON ACRÓNIMO + historial
            img_filename = save_uploaded_image(pil_img, pred_class)
            st.session_state["last_img_filename"] = img_filename

            snr_level, snr_class, snr_desc = get_snr_info(max_prob)
            append_history_row(pred_class, max_prob, snr_level, img_filename)

    last_label = st.session_state.get("last_pred_class")
    last_conf = st.session_state.get("last_pred_conf")
    last_prob_dict = st.session_state.get("last_prob_dict")
    last_img_filename = st.session_state.get("last_img_filename")

    if last_label is None:
        st.info("Sube una imagen y presiona **ANALIZAR SEÑAL** para ver resultados.")
    elif last_label in HIDDEN_FSK:
        st.warning("Se detectó modulación FSK. Esta demo se enfoca en ASK, PSK y QAM.")
    else:
        snr_level, snr_class, snr_desc = get_snr_info(last_conf)

        # RESULT BOX + LOGO DENTRO (AGRANDADO)
        if LOGO_B64:
            result_html = f"""
            <div class="result-box">
              <div class="result-inner">
                <div class="result-text">
                  <div class="result-label">MODULACIÓN DETECTADA</div>
                  <div class="prediction">{last_label}</div>
                  <div class="confidence">
                    Confianza: <span class="confidence-value">{last_conf*100:.1f}%</span>
                  </div>
                </div>
                <div class="result-logo">
                  <img src="data:image/png;base64,{LOGO_B64}" alt="logo" />
                </div>
              </div>
            </div>
            """
        else:
            result_html = f"""
            <div class="result-box">
              <div class="result-label">MODULACIÓN DETECTADA</div>
              <div class="prediction">{last_label}</div>
              <div class="confidence">
                Confianza: <span class="confidence-value">{last_conf*100:.1f}%</span>
              </div>
            </div>
            """
        st.markdown(result_html, unsafe_allow_html=True)

        # SNR badge
        st.markdown(f"""
        <div class="snr-container">
          <div class="snr-badge {snr_class}">{snr_level}</div>
          <div class="snr-description">{snr_desc}</div>
        </div>
        """, unsafe_allow_html=True)

        # Distribución de probabilidades (top 8, sin FSK) - ALTURA AUMENTADA
        if last_prob_dict:
            filtered = {k: v for k, v in last_prob_dict.items() if k not in HIDDEN_FSK}
            top = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:8]
            if top:
                dfp = pd.DataFrame(top, columns=["Clase", "Probabilidad"])
                dfp["Probabilidad (%)"] = (dfp["Probabilidad"] * 100).round(2)
                dfp = dfp.drop(columns=["Probabilidad"]).set_index("Clase")

                st.markdown('<div class="section-title" style="margin-top: 1.25rem;">Distribución de Probabilidades</div>', unsafe_allow_html=True)
                st.bar_chart(dfp, height=350)

        # Detalles técnicos
        with st.expander("Detalles Técnicos"):
            family, order = last_label.split("_") if "_" in last_label else (last_label, "N/A")
            st.markdown(f"""
            **Familia** {family}  
            **Orden** M = {order}  
            **Confianza** {last_conf*100:.2f}%  
            **Imagen guardada** {last_img_filename if last_img_filename else "N/A"}  
            """)

    # -----------------------------
    # HISTORIAL (TABLA + DESCARGA)
    # -----------------------------
    st.markdown('<div class="section-title" style="margin-top: 1.75rem;">Historial de Predicciones</div>', unsafe_allow_html=True)

    history_df = read_history()
    if history_df.empty:
        st.info("Aún no hay registros. Analiza una señal para comenzar el historial.")
    else:
        # Mostrar últimos 20 primero
        show_df = history_df.tail(20).copy()

        # Link visual de archivo (nombre) - solo texto, la imagen está en logs/images/
        show_df = show_df.rename(columns={
            "timestamp": "Fecha/Hora",
            "modulation": "Modulación",
            "confidence_pct": "Confianza (%)",
            "snr_level": "SNR",
            "image_file": "Archivo Imagen",
        })

        st.dataframe(show_df, use_container_width=True, height=280)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.download_button(
                "DESCARGAR CSV",
                data=history_df.to_csv(index=False).encode("utf-8"),
                file_name="history.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c2:
            st.markdown('<div class="history-actions">', unsafe_allow_html=True)
            if st.button("LIMPIAR HISTORIAL", use_container_width=True):
                # Reinicia CSV
                pd.DataFrame(columns=[
                    "timestamp", "modulation", "confidence_pct", "snr_level", "image_file"
                ]).to_csv(CSV_LOG_PATH, index=False)
                st.success("Historial limpiado.")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)