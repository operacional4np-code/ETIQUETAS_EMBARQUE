import os
import io
import pandas as pd
import streamlit as st
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(page_title="Gerador de Etiquetas", page_icon="✈️", layout="centered")
CSV_PATH = 'destinos.csv'

def carregar_dataframe():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=['sigla', 'nome_recebedor', 'cnpj_recebedor', 'endereco_recebedor', 'cidade_recebedor', 'uf_recebedor', 'cep_recebedor', 'pais_recebedor'])
    df = pd.read_csv(CSV_PATH, sep=';')
    df.columns = df.columns.str.lower()
    return df

def gerar_etiquetas_pdf(sigla, quantidade, dados_recebedor):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(100 * mm, 100 * mm))
    styles = getSampleStyleSheet()
    
    # Estilo dos blocos
    style_normal = ParagraphStyle(name='Normal', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    
    # Estilo do Overpack com fonte 46 como pedido
    style_overpack = ParagraphStyle(name='Overpack', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=46, leading=48)
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    for i in range(1, quantidade + 1):
        # 1. Cabeçalho Principal (Topo)
        c.setFont('Helvetica-Bold', 36)
        c.drawString(4*mm, 85*mm, sigla)
        
        numero_str = f"#{i}"
        largura_num = c.stringWidth(numero_str, 'Helvetica-Bold', 36)
        c.drawString(96*mm - largura_num, 85*mm, numero_str)
        
        # 2. OVERPACK USED (Fonte 46 como solicitado)
        # Usamos uma área de desenho menor para o parágrafo respeitar a largura
        p_overpack = Paragraph("OVERPACK<br/>USED", style_overpack)
        p_overpack.wrapOn(c, 92*mm, 50*mm)
        p_overpack.drawOn(c, 4*mm, 50*mm)
        
        # 3. Textos (Baixados para não colidir com a fonte 46)
        expedidor_text = f"<b>EXPEDIDOR:</b> NEW POST LOGISTICA ENDEREÇO: R UBALDO FAGGEANI, 355,0 - JARDIM RESIDENCIAL LAS PALMAS MUNICÍPIO: PORTO FERREIRA - SP CEP: 13660-000 CNPJ/CPF: 28.678.104/0001-79 IE: 555074223110 UF: SP PAÍS: BRASIL"
        recebedor_text = f"<b>RECEBEDOR:</b> {dados_recebedor['nome_recebedor']} CNPJ {dados_recebedor['cnpj_recebedor']} ENDEREÇO: {dados_recebedor['endereco_recebedor']}, {dados_recebedor['cidade_recebedor']} - {dados_recebedor['uf_recebedor']} CEP: {dados_recebedor['cep_recebedor']}"
        data_text = f"<b>DATA DE EXPEDIÇÃO:</b> {data_atual}"
        
        Paragraph(expedidor_text, style_normal).wrapOn(c, 92*mm, 20*mm)
        Paragraph(expedidor_text, style_normal).drawOn(c, 4*mm, 30*mm)
        
        Paragraph(recebedor_text, style_normal).wrapOn(c, 92*mm, 20*mm)
        Paragraph(recebedor_text, style_normal).drawOn(c, 4*mm, 15*mm)
        
        c.setFont('Helvetica-Bold', 8)
        c.drawString(4*mm, 6*mm, data_text.replace("<b>", "").replace("</b>", ""))
        
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Interface Streamlit (mantida igual)
st.title("✈️ Emissor de Etiquetas")
# ... (restante do código do formulário permanece igual)
