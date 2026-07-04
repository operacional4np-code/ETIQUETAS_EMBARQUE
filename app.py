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
    c = canvas.Canvas(buffer, pagesize=(100 * mm, 100 * mm))
    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    
    for i in range(1, quantidade + 1):
        # 1. Cabeçalho: Sigla e Número
        c.setFont('Helvetica-Bold', 36)
        c.drawString(4*mm, 85*mm, sigla)
        c.drawString(78*mm, 85*mm, f"#{i}")
        
        # 2. OVERPACK USED - Fonte 40 (Desenhado fixo)
        c.setFont('Helvetica-Bold', 40)
        c.drawString(4*mm, 68*mm, "OVERPACK")
        c.drawString(4*mm, 52*mm, "USED")
        
        # 3. Textos (Expedidor e Recebedor)
        exp = f"<b>EXPEDIDOR:</b> NEW POST LOGISTICA ENDEREÇO: R UBALDO FAGGEANI, 355,0 - JARDIM RESIDENCIAL LAS PALMAS MUNICÍPIO: PORTO FERREIRA - SP CEP: 13660-000 CNPJ/CPF: 28.678.104/0001-79"
        rec = f"<b>RECEBEDOR:</b> {dados['nome_recebedor']} CNPJ {dados['cnpj_recebedor']} ENDEREÇO: {dados['endereco_recebedor']}, {dados['cidade_recebedor']} - {dados['uf_recebedor']} CEP: {dados['cep_recebedor']}"
        
        p1 = Paragraph(exp, style_normal)
        p1.wrapOn(c, 92*mm, 30*mm)
        p1.drawOn(c, 4*mm, 32*mm)
        
        p2 = Paragraph(rec, style_normal)
        p2.wrapOn(c, 92*mm, 20*mm)
        p2.drawOn(c, 4*mm, 15*mm)
        
        # 4. Data
        c.setFont('Helvetica', 8)
        c.drawString(4*mm, 6*mm, f"DATA DE EXPEDIÇÃO: {datetime.now().strftime('%d/%m/%Y')}")
        
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO ---
st.title("✈️ Emissor de Etiquetas")
df = carregar_dataframe()

if not df.empty:
    sigla = st.selectbox("Destino:", df['sigla'].unique())
    qtd = st.number_input("Quantidade:", min_value=1, value=1)
    
    if st.button("Gerar PDF"):
        dados = df[df['sigla'] == sigla].iloc[0]
        pdf = gerar_etiquetas_pdf(sigla, qtd, dados)
        st.download_button("📥 Baixar PDF", pdf, "etiqueta.pdf", "application/pdf")
else:
    st.warning("Adicione destinos no arquivo CSV primeiro.")
