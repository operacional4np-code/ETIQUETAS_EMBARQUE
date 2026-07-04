import os
import io
import pandas as pd
import streamlit as st
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(
    page_title="Gerador de Etiquetas - New Post",
    page_icon="✈️",
    layout="centered"
)

CSV_PATH = 'destinos.csv'

# --- CONFIGURAÇÕES DE FONTE ---
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
except Exception as e:
    pass

# --- FUNÇÕES DE MANIPULAÇÃO DE DADOS ---
def carregar_dataframe():
    if not os.path.exists(CSV_PATH):
        colunas = ['sigla', 'nome_recebedor', 'cnpj_recebedor', 'endereco_recebedor', 'cidade_recebedor', 'uf_recebedor', 'cep_recebedor', 'pais_recebedor']
        return pd.DataFrame(columns=colunas)
    
    df = pd.read_csv(CSV_PATH, sep=';')
    df.columns = df.columns.str.lower()
    
    colunas_obrigatorias = ['sigla', 'nome_recebedor', 'cnpj_recebedor', 'endereco_recebedor', 'cidade_recebedor', 'uf_recebedor', 'cep_recebedor', 'pais_recebedor']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = ""
    return df

def salvar_dataframe(df):
    df.to_csv(CSV_PATH, index=False, sep=';')

# --- GERAÇÃO DA ETIQUETA TRAVADA EM 150mm x 100mm ---
def gerar_etiquetas_pdf(sigla, quantidade, dados_recebedor):
    buffer = io.BytesIO()
    
    # Travado exatamente no tamanho solicitado por você: 150mm x 100mm
    c = canvas.Canvas(buffer, pagesize=(150 * mm, 100 * mm))
    styles = getSampleStyleSheet()
    
    # Travado exatamente nas configurações de estilo normais que você enviou
    style_normal = ParagraphStyle(
        name='Normal', 
        parent=styles['Normal'], 
        fontName='Arial', 
        fontSize=11, 
        leading=13, 
        alignment=TA_LEFT
    )
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    for i in range(1, quantidade + 1):
        margem_h = 5 * mm
        largura_maxima = 140 * mm
        
        # --- Trecho exato enviado por você para o Cabeçalho ---
        c.setFont('Arial-Bold', 56)
        c.drawString(margem_h, 75 * mm, sigla)
        
        numero_str = f"#{i}"
        c.setFont('Arial-Bold', 49)
        largura_texto_num = c.stringWidth(numero_str, 'Arial-Bold', 49)
        c.drawString((150 * mm) - margem_h - largura_texto_num, 75 * mm, numero_str)
        
        c.setFont('Arial-Bold', 46)
        c.drawString(margem_h, 55 * mm, "Overpack used")
        # -----------------------------------------------------
        
        # Montagem dos Textos dos Blocos
        expedidor_text = "<b>EXPEDIDOR:</b> NEW POST LOGISTICA ENDEREÇO: R UBALDO FAGGEANI, 355,0 - JARDIM RESIDENCIAL LAS PALMAS MUNICÍPIO: PORTO FERREIRA - SP CEP: 13660-000 CNPJ/CPF: 28.678.104/0001-79 IE: 555074223110 UF: SP PAÍS: BRASIL"
        recebedor_text = f"<b>RECEBEDOR:</b> {dados_recebedor['nome_recebedor']} CNPJ {dados_recebedor['cnpj_recebedor']} ENDEREÇO: {dados_recebedor['endereco_recebedor']}, {dados_recebedor['cidade_recebedor']} - {dados_recebedor['uf_recebedor']} CEP: {dados_recebedor['cep_recebedor']}"
        data_text = f"<b>DATA DE EXPEDIÇÃO:</b> {data_atual}"
        
        p_expedidor = Paragraph(expedidor_text, style_normal)
        p_recebedor = Paragraph(recebedor_text, style_normal)
        p_data = Paragraph(data_text, style_normal)
        
        # Ajuste milimétrico das alturas para garantir os espaçamentos de respiro sem cortar nada:
        
        # 4. Desenha EXPEDIDOR (Inicia logo abaixo de Overpack Used, em 33mm)
        p_expedidor.wrapOn(c, largura_maxima, 15 * mm)
        p_expedidor.drawOn(c, margem_h, 33 * mm)
        
        # 5. Desenha RECEBEDOR (Afastado no centro, iniciando em 15mm)
        p_recebedor.wrapOn(c, largura_maxima, 12 * mm)
        p_recebedor.drawOn(c, margem_h, 15 * mm)
        
        # 6. Desenha DATA DE EXPEDIÇÃO (Isolada na última linha do rodapé, a 4mm da base)
        p_data.wrapOn(c, largura_maxima, 6 * mm)
        p_data.drawOn(
