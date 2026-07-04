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

# --- GERAÇÃO DA ETIQUETA COM DISTRIBUIÇÃO CORRETA (150mm x 100mm) ---
def gerar_etiquetas_pdf(sigla, quantidade, dados_recebedor):
    buffer = io.BytesIO()
    
    # Tamanho padrão: 150mm x 100mm
    c = canvas.Canvas(buffer, pagesize=(150 * mm, 100 * mm))
    styles = getSampleStyleSheet()
    
    font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    font_bold = 'Arial-Bold' if 'Arial-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
    
    style_normal = ParagraphStyle(
        name='Normal', 
        parent=styles['Normal'], 
        fontName=font_name, 
        fontSize=11,       
        leading=14,        # Aumentado levemente para melhor leitura das linhas
        alignment=TA_LEFT
    )
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    for i in range(1, quantidade + 1):
        margem_h = 5 * mm
        largura_maxima = 140 * mm
        
        # 1. Sigla do Destino (Topo Esquerda)
        c.setFont(font_bold, 56)
        c.drawString(margem_h, 75 * mm, sigla)
        
        # 2. Número da Saca (Topo Direita)
        numero_str = f"#{i}"
        c.setFont(font_bold, 49)
        largura_texto_num = c.stringWidth(numero_str, font_bold, 49)
        c.drawString((150 * mm) - margem_h - largura_texto_num, 75 * mm, numero_str)
        
        # 3. Overpack used (Abaixo do bloco do topo)
        c.setFont(font_bold, 46)
        c.drawString(margem_h, 55 * mm, "Overpack used")
        
        # Textos estruturados
        expedidor_text = "<b>EXPEDIDOR:</b> NEW POST LOGISTICA ENDEREÇO: R UBALDO FAGGEANI, 355,0 - JARDIM RESIDENCIAL LAS PALMAS MUNICÍPIO: PORTO FERREIRA - SP CEP: 13660-000 CNPJ/CPF: 28.678.104/0001-79 IE: 555074223110 UF: SP PAÍS: BRASIL"
        recebedor_text = f"<b>RECEBEDOR:</b> {dados_recebedor['nome_recebedor']} CNPJ {dados_recebedor['cnpj_recebedor']} ENDEREÇO: {dados_recebedor['endereco_recebedor']}, {dados_recebedor['cidade_recebedor']} - {dados_recebedor['uf_recebedor']} CEP: {dados_recebedor['cep_recebedor']}"
        data_text = f"<b>DATA DE EXPEDIÇÃO:</b> {data_atual}"
        
        # 4. Desenha EXPEDIDOR (Subiu para 38mm para abrir espaço)
        p_expedidor = Paragraph(expedidor_text, style_normal)
        p_expedidor.wrapOn(c, largura_maxima, 25 * mm)
        p_expedidor.drawOn(c, margem_h, 38 * mm)
        
        # 5. Desenha RECEBEDOR (Posicionado em 16mm, perfeitamente distante do de cima)
        p_recebedor = Paragraph(recebedor_text, style_normal)
        p_recebedor.wrapOn(c, largura_maxima, 25 * mm)
        p_recebedor.drawOn(c, margem_h, 16 * mm)
        
        # 6. Desenha DATA DE EXPEDIÇÃO (Isolada na última linha do rodapé)
        p_data = Paragraph(data_text, style_normal)
        p_data.wrapOn(c, largura_maxima, 10 * mm)
        p_data.drawOn(c, margem_h, 4 * mm)
        
        c.showPage()
        
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO (STREAMLIT) ---
st.title("✈️ Emissor de Etiquetas de Embarque")

df_destinos = carregar_dataframe()
df_destinos = df_destinos.dropna(subset=['sigla'])
df_destinos['sigla'] = df_destinos['sigla'].str.upper()
destinos_dict = df_destinos.set_index('sigla').to_dict('index')

aba_gerar, aba_admin = st.tabs(["📄 Gerar Etiquetas", "⚙️ Configurar Aeroportos/Destinos"])

with
