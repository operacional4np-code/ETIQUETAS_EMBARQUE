import os
import io
import pandas as pd
import streamlit as st
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="Gerador de Etiquetas", layout="centered")
CSV_PATH = 'destinos.csv'

def carregar_dataframe():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=['sigla', 'nome_recebedor', 'cnpj_recebedor', 'endereco_recebedor', 'cidade_recebedor', 'uf_recebedor', 'cep_recebedor', 'pais_recebedor'])
    return pd.read_csv(CSV_PATH, sep=';')

def gerar_etiquetas_pdf(sigla, quantidade, dados):
    buffer = io.BytesIO()
    # Tamanho fixo 100x100mm
    c = canvas.Canvas(buffer, pagesize=(100 * mm, 100 * mm))
    styles = getSampleStyleSheet()
    
    # Estilo dos blocos de dados
    style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    
    for i in range(1, quantidade + 1):
        # 1. Cabeçalho (Topo)
        c.setFont('Helvetica-Bold', 36)
        c.drawString(4*mm, 86*mm, sigla)
        c.drawString(78*mm, 86*mm, f"#{i}")
        
        # 2. OVERPACK USED (Fonte 40, alinhado com a referência)
        c.setFont('Helvetica-Bold', 40)
        c.drawString(4*mm, 70*mm, "OVERPACK")
        c.drawString(4*mm, 58*mm, "USED")
        
        # 3. Blocos de Texto (Expedidor e Recebedor)
        # Ajustamos o início do desenho para 45mm para não bater no "USED"
        exp = f"<b>EXPEDIDOR:</b> NEW POST LOGISTICA | R UBALDO FAGGEANI, 355 - PORTO FERREIRA/SP | CNPJ: 28.678.104/0001-79"
        rec = f"<b>RECEBEDOR:</b> {dados['nome_recebedor']} | {dados['endereco_recebedor']}, {dados['cidade_recebedor']}-{dados['uf_recebedor']} | CEP: {dados['cep_recebedor']}"
        
        p1 = Paragraph(exp, style_normal)
        p1.wrapOn(c, 92*mm, 20*mm)
        p1.drawOn(c, 4*mm, 35*mm)
        
        p2 = Paragraph(rec, style_normal)
        p2.wrapOn(c, 92*mm, 20*mm)
        p2.drawOn(c, 4*mm, 18*mm)
        
        # 4. Data
        c.setFont('Helvetica', 8)
        c.drawString(4*mm, 6*mm, f"DATA DE EXPEDIÇÃO: {datetime.now().strftime('%d/%m/%Y')}")
        
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
st.title("✈️ Emissor de Etiquetas")
df = carregar_dataframe()

if not df.empty:
    sigla = st.selectbox("Destino:", df['sigla'].unique())
    qtd = st.number_input("Quantidade:", min_value=1, value=1)
    if st.button("Gerar PDF"):
        dados = df[df['sigla'] == sigla].iloc[0]
        pdf = gerar_etiquetas_pdf(sigla, qtd, dados)
        st.download_button("📥 Baixar PDF", pdf, "etiqueta.pdf", "application/pdf")
