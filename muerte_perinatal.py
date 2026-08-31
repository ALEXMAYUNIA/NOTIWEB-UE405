
import streamlit as st
import pandas as pd
import os
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from io import BytesIO
import xlsxwriter
from plotly.subplots import make_subplots
from datetime import datetime
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

def mostrar_pagina():
    st.markdown("**Modo Licenciada: Subir archivos | Modo Técnico: Carpeta automática**")
    modo = st.radio("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos (para Licenciada - Excel diferente)"], horizontal=True, key="mp_modo")

    lista_df = []
    archivos = []
    archivos_fallidos = []

    if modo == "📤 Subir archivos (para Licenciada - Excel diferente)":
        uploaded = st.file_uploader("📂 Arrastra aquí tus archivos Excel de MUERTE PERINATAL (excel diferente - múltiples)", type=['xlsx','xls','csv'], accept_multiple_files=True, key="mp_upload")
        if not uploaded:
            st.info("👆 Sube tus archivos Excel para empezar - Este módulo acepta el Excel diferente de la Licenciada")
            return
        archivos = [f.name for f in uploaded]
        progress = st.progress(0)
        for idx, f in enumerate(uploaded):
            progress.progress((idx+1)/len(uploaded))
            df_temp = None
            try:
                if f.name.lower().endswith('.csv'):
                    df_temp = pd.read_csv(f, encoding='utf-8', low_memory=False)
                else:
                    try:
                        df_temp = pd.read_excel(f, engine='openpyxl', header=0)
                    except:
                        try:
                            df_temp = pd.read_excel(f, engine='xlrd', header=0)
                        except:
                            df_temp = pd.read_excel(f, header=0)
            except Exception as e:
                archivos_fallidos.append(f.name)
                continue

            if df_temp is not None and not df_temp.empty:
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                df_temp = df_temp.dropna(how='all')
                df_temp = df_temp.dropna(axis=1, how='all')
                lista_df.append(df_temp)
            else:
                archivos_fallidos.append(f.name)
        progress.empty()
    else:
        RUTA_BASE = os.path.dirname(__file__)
        ruta_carpeta = os.path.join(RUTA_BASE, 'MUERTE PERINATAL')
        
        if not os.path.exists(ruta_carpeta):
            st.warning(f"⚠️ No existe la carpeta: {ruta_carpeta} - Usa modo Subir archivos")
            return

        archivos_raw = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
        archivos = archivos_raw
        
        if not archivos:
            st.warning("La carpeta MUERTE PERINATAL esta vacia - Usa modo Subir archivos")
            return

        progress = st.progress(0)
        
        for idx, archivo in enumerate(archivos):
            progress.progress((idx+1)/len(archivos))
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            df_temp = None
            try:
                if archivo.lower().endswith('.csv'):
                    df_temp = pd.read_csv(ruta_archivo, encoding='utf-8', low_memory=False)
                else:
                    try:
                        df_temp = pd.read_excel(ruta_archivo, engine='openpyxl', header=0)
                    except:
                        try:
                            df_temp = pd.read_excel(ruta_archivo, engine='xlrd', header=0)
                        except:
                            df_temp = pd.read_excel(ruta_archivo, header=0)
            except Exception as e:
                archivos_fallidos.append(archivo)
                continue

            if df_temp is not None and not df_temp.empty:
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                df_temp = df_temp.dropna(how='all')
                df_temp = df_temp.dropna(axis=1, how='all')
                lista_df.append(df_temp)
            else:
                archivos_fallidos.append(archivo)

        progress.empty()

    if not lista_df:
        st.error("No se pudo leer ningun archivo valido")
        return

    st.success(f"✅ Archivos leidos: {len(lista_df)} de {len(archivos)} - Total: {sum(len(d) for d in lista_df)} casos | Excel diferente de Licenciada compatible")

    df = pd.concat(lista_df, ignore_index=True, sort=False)
    df.columns = df.columns.astype(str).str.lower().str.strip()

    # MAPEO - PRESERVADO EXACTO ORIGINAL MUERTE PERINATAL
    df['ANIO'] = pd.to_numeric(df.get('anio', 0), errors='coerce')
    df['ANIO'] = df['ANIO'].fillna(0).astype(int).astype(str)
    df.loc[df['ANIO'] == '0', 'ANIO'] = 'S/D'

    df['DEPARTAMEN'] = df.get('departamen', df.get('depar', 'SIN DATO')).fillna('SIN DATO')
    df['PROVINCIA'] = df.get('provincia', df.get('prov', 'SIN DATO')).fillna('SIN DATO')
    df['DISTRITO'] = df.get('distrito', df.get('dis', 'SIN DATO')).fillna('SIN DATO')
    df['MICROREDES'] = df.get('microredes', df.get('microred', 'SIN DATO')).fillna('SIN DATO')
    df['ESTABLECIMINETO'] = df.get('establecimineto', df.get('eess', df.get('establecimiento', 'SIN DATO'))).fillna('SIN DATO')
    
    sexo = df.get('sexo', pd.Series(['']*len(df))).astype(str).str.upper().str.strip()
    df['SEXO'] = 'INDETERMINADO'
    df.loc[sexo == 'M', 'SEXO'] = 'MASCULINO'
    df.loc[sexo == 'F', 'SEXO'] = 'FEMENINO'
    
    df['FECHA_NAC'] = pd.to_datetime(df.get('fecha_nac'), errors='coerce').dt.strftime('%d/%m/%Y')
    df['FECHA_NAC'] = df['FECHA_NAC'].fillna('S/D')
    df['FECHA_MTE'] = pd.to_datetime(df.get('fecha_mte'), errors='coerce').dt.strftime('%d/%m/%Y')
    df['FECHA_MTE'] = df['FECHA_MTE'].fillna('S/D')

    tipo = df.get('tipo_mte', pd.Series(['']*len(df))).astype(str).str.upper().str.strip()
    df['TIPO_MTE'] = 'SIN DATO'
    df.loc[tipo == 'F', 'TIPO_MTE'] = 'MTE FETAL'
    df.loc[tipo == 'N', 'TIPO_MTE'] = 'MTE NEONATAL'

    st.subheader("2. Filtros:")
    col1, col2, col3 = st.columns(3)
    with col1:
        anos_raw = [str(x) for x in df['ANIO'].astype(str).unique().tolist() if str(x).lower() not in ['nan','s/d','']]
        anos_disponibles = ['TODOS'] + sorted(anos_raw, key=lambda x: int(x) if x.isdigit() else x)
        ano_filtro = st.selectbox("Filtrar por AÑO:", anos_disponibles, key='mp_ano')
    with col2:
        prov_raw = [str(x).strip() for x in df['PROVINCIA'].astype(str).unique().tolist() if str(x).lower() not in ['nan','sin dato','']]
        prov_disponibles = ['TODAS'] + sorted(prov_raw)
        prov_filtro = st.selectbox("Filtrar por PROVINCIA:", prov_disponibles, key='mp_prov')
    with col3:
        if prov_filtro != 'TODAS':
            distritos_filtrados = df[df['PROVINCIA'].astype(str) == prov_filtro]['DISTRITO'].astype(str).unique().tolist()
        else:
            distritos_filtrados = df['DISTRITO'].astype(str).unique().tolist()
        dis_raw = [str(x).strip() for x in distritos_filtrados if str(x).lower() not in ['nan','sin dato','']]
        dis_disponibles = ['TODOS'] + sorted(dis_raw)
        dis_filtro = st.selectbox("Filtrar por DISTRITO:", dis_disponibles, key='mp_dis')

    df_filtrado = df.copy()
    if ano_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['ANIO'].astype(str) == str(ano_filtro)]
    if prov_filtro!= 'TODAS': df_filtrado = df_filtrado[df_filtrado['PROVINCIA'].astype(str) == str(prov_filtro)]
    if dis_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['DISTRITO'].astype(str) == str(dis_filtro)]

    st.subheader("TABLA 1: Casos de MUERTE PERINATAL")
    columnas_tabla1 = ['ANIO', 'DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'MICROREDES', 'ESTABLECIMINETO','SEXO', 'FECHA_NAC', 'FECHA_MTE', 'TIPO_MTE']
    for c in columnas_tabla1:
        if c not in df_filtrado.columns:
            df_filtrado[c]='S/D'
    tabla1 = df_filtrado[columnas_tabla1].copy()
    tabla1['TOTAL'] = 1
    total_general = len(tabla1)
    if total_general == 0:
        st.warning("No se registraron casos con los filtros seleccionados")
        return
    fila_total = {col: '' for col in columnas_tabla1}
    fila_total['ANIO'] = 'TOTAL GENERAL'
    fila_total['TOTAL'] = total_general
    tabla1_final = pd.concat([tabla1, pd.DataFrame([fila_total])], ignore_index=True)
    def colorear_tabla(row):
        if row['ANIO'] == 'TOTAL GENERAL':
            return ['background-color: #FFD700; font-weight: bold'] * len(row)
        return [''] * len(row)
    st.dataframe(tabla1_final.style.apply(colorear_tabla, axis=1), use_container_width=True, hide_index=True)

    # TABLAS PARA GRAFICOS
    tabla_graf = df_filtrado.groupby('ANIO').size().reset_index(name='TOTAL').sort_values('ANIO')
    tabla_tipo = df_filtrado.groupby('TIPO_MTE').size().reset_index(name='TOTAL').sort_values('TOTAL', ascending=False)
    tabla2 = df_filtrado.groupby('SEXO').size().reset_index(name='TOTAL').sort_values('TOTAL', ascending=False)

    # GRAFICOS
    c1_g, c2_g = st.columns(2)
    with c1_g:
        fig1 = px.bar(tabla_graf, x='ANIO', y='TOTAL', title='Muerte Perinatal por Año', text='TOTAL', color='ANIO')
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)
    with c2_g:
        fig2 = px.pie(tabla_tipo, names='TIPO_MTE', values='TOTAL', title='Distribución MTE FETAL vs NEONATAL (3D)', hole=0.3, color='TIPO_MTE', color_discrete_map={'MTE FETAL': '#0052CC', 'MTE NEONATAL': '#5FA8FF', 'SIN DATO': '#D3D3D3'})
        fig2.update_traces(textinfo='percent+label', pull=[0.1 if 'FETAL' in str(x) else 0 for x in tabla_tipo['TIPO_MTE']])
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(tabla2, x='SEXO', y='TOTAL', title='Distribución por Sexo', text='TOTAL', color='SEXO', color_discrete_sequence=['#FF6FB5','#0EA5E9','#9E9E9E'])
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

    def to_excel_pro():
        df_exp = tabla1_final.replace([np.inf, -np.inf], np.nan).fillna('')
        tabla_tipo_exp = tabla_tipo.copy()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            wb=writer.book
            hdr=wb.add_format({'bold':True,'bg_color':'#1c2e4a','font_color':'white','border':1,'align':'center'})
            tot=wb.add_format({'bold':True,'bg_color':'#FFD700','border':2,'align':'center'})
            cell=wb.add_format({'border':1,'align':'center'})
            title=wb.add_format({'bold':True,'font_size':12,'bg_color':'#D9E1F2','border':1})
            s1='TABLA_1'; df_exp.to_excel(writer, sheet_name=s1, index=False, startrow=1)
            ws=writer.sheets[s1]; ws.write(0,0,f"MUERTE PERINATAL - {ano_filtro}/{prov_filtro}/{dis_filtro} - {total_general} casos",title)
            for c,v in enumerate(df_exp.columns): ws.write(1,c,v,hdr)
            for r in range(len(df_exp)):
                for c in range(len(df_exp.columns)):
                    f=tot if df_exp.iloc[r]['ANIO']=='TOTAL GENERAL' else cell
                    ws.write(r+2,c,str(df_exp.iloc[r,c]),f)
            ws.set_column('A:K',18)
            # HOJA POR TIPO
            s2='POR_TIPO'; tabla_tipo_exp.to_excel(writer, sheet_name=s2, index=False, startrow=1)
            ws2=writer.sheets[s2]
            for c,v in enumerate(tabla_tipo_exp.columns): ws2.write(1,c,v,hdr)
            for r in range(len(tabla_tipo_exp)):
                for c in range(len(tabla_tipo_exp.columns)): ws2.write(r+2,c,tabla_tipo_exp.iloc[r,c],cell)
        return output.getvalue()

    def to_pdf_3d():
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles=getSampleStyleSheet()
        stt=ParagraphStyle('T', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#1c2e4a'), alignment=1, spaceAfter=8)
        sh2=ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1c2e4a'), spaceAfter=4, spaceBefore=10)
        s_desc=ParagraphStyle('Desc', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor('#334155'), leftIndent=6, borderPadding=6, backColor=colors.HexColor('#f8fafc'), spaceAfter=6)
        story=[]
        story.append(Paragraph(f"<b>ANALISIS NOTIWEB 2026 - MUERTE PERINATAL UE 405</b><br/>Filtros: {ano_filtro}/{prov_filtro}/{dis_filtro} - Total: {total_general} casos - {len(lista_df)} archivos - {datetime.now().strftime('%d/%m/%Y')}", stt))
        story.append(Spacer(1,8))
        story.append(Paragraph("<b>1. RESUMEN EJECUTIVO</b>", sh2))
        fetal = len(df_filtrado[df_filtrado['TIPO_MTE']=='MTE FETAL']); neonatal = len(df_filtrado[df_filtrado['TIPO_MTE']=='MTE NEONATAL'])
        porc_fetal = fetal/total_general*100 if total_general>0 else 0
        story.append(Paragraph(f"Se registraron <b>{total_general} casos</b> de {len(lista_df)} archivos (de {len(archivos)}). <b>MTE FETAL: {fetal} casos ({porc_fetal:.1f}%) y MTE NEONATAL: {neonatal} casos ({100-porc_fetal:.1f}%)</b>. Provincia mayor carga: <b>{df_filtrado['PROVINCIA'].value_counts().index[0] if not df_filtrado.empty else 'S/D'}</b>. Predominio sexo: <b>{df_filtrado['SEXO'].value_counts().index[0] if not df_filtrado.empty else 'S/D'}</b>. Requiere fortalecimiento de control prenatal y atencion neonatal.", s_desc))
        story.append(Paragraph("<b>2. TABLA 1: Detalle</b>", sh2))
        data=[['AÑO','PROV','DISTRITO','MICRORED','EESS','SEXO','TIPO_MTE']]
        for _,r in tabla1.sort_values('ANIO').head(20).iterrows():
            data.append([str(r['ANIO']),str(r['PROVINCIA'])[:8],str(r['DISTRITO'])[:8],str(r['MICROREDES'])[:8],str(r['ESTABLECIMINETO'])[:12],str(r['SEXO'])[:1],str(r['TIPO_MTE'])])
        t=Table(data, colWidths=[30,45,45,45,70,25,60])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),6)]))
        story.append(t); story.append(Spacer(1,6))
        story.append(Paragraph(f"Tabla muestra 20 casos de {total_general}. Total general incluye todos los filtros. La distribucion por provincia y distrito permite identificar zonas de mayor riesgo perinatal.", s_desc))
        # GRAFICO 1
        fig,ax=plt.subplots(figsize=(5,2))
        ax.bar(tabla_graf['ANIO'].astype(str), tabla_graf['TOTAL'], color='#FF6FB5')
        ax.set_title('Muerte Perinatal por Año', fontsize=9); plt.tight_layout()
        b=BytesIO(); plt.savefig(b, format='png', dpi=150); plt.close(); b.seek(0)
        story.append(Paragraph("<b>3. GRAFICO 1: Tendencia Anual</b>", sh2))
        story.append(Image(b, width=400, height=130)); story.append(Spacer(1,4))
        story.append(Paragraph(f"Año con mayor registro: <b>{tabla_graf.loc[tabla_graf['TOTAL'].idxmax(),'ANIO'] if not tabla_graf.empty else 'S/D'} con {tabla_graf['TOTAL'].max() if not tabla_graf.empty else 0} casos</b>.", s_desc))
        # GRAFICO 2 - 3D PIE
        fig = plt.figure(figsize=(5,2.5))
        ax = fig.add_subplot(111)
        labels = tabla_tipo['TIPO_MTE'].tolist()
        sizes = tabla_tipo['TOTAL'].tolist()
        colors_pie = ['#0052CC','#5FA8FF','#D3D3D3'][:len(labels)]
        explode = [0.1 if 'FETAL' in str(l) else 0 for l in labels]
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', colors=colors_pie, shadow=True, startangle=90, pctdistance=0.6)
        ax.set_title('Distribución MTE FETAL vs MTE NEONATAL ', fontsize=9)
        plt.tight_layout()
        b2=BytesIO(); plt.savefig(b2, format='png', dpi=150); plt.close(); b2.seek(0)
        story.append(Paragraph("<b>4. GRAFICO 2: MTE FETAL vs NEONATAL</b>", sh2))
        story.append(Image(b2, width=380, height=180)); story.append(Spacer(1,4))
        story.append(Paragraph(f"Distribucion: <b>MTE FETAL {fetal} casos ({fetal/total_general*100:.1f}%) y MTE NEONATAL {neonatal} casos ({neonatal/total_general*100:.1f}%)</b>. Predominio fetal indica necesidad de mejorar control prenatal y deteccion de riesgo. Neonatal requiere fortalecimiento de atencion inmediata del recien nacido.", s_desc))
        # GRAFICO 3
        fig,ax=plt.subplots(figsize=(5,2))
        tabla2_sorted=tabla2.sort_values('TOTAL')
        ax.bar(tabla2_sorted['SEXO'], tabla2_sorted['TOTAL'], color=['#FF6FB5','#0EA5E9','#9E9E9E'][:len(tabla2_sorted)])
        ax.set_title('Por Sexo', fontsize=9); plt.tight_layout()
        b3=BytesIO(); plt.savefig(b3, format='png', dpi=150); plt.close(); b3.seek(0)
        story.append(Paragraph("<b>5. GRAFICO 3: Por Sexo</b>", sh2))
        story.append(Image(b3, width=400, height=130))
        doc.build(story)
        return buffer.getvalue()

    c1,c2,c3=st.columns(3)
    with c1:
        st.download_button("📊 DESCARGAR EXCEL", data=to_excel_pro(), file_name=f"MUERTE_PERINATAL_PRO_{ano_filtro}_{prov_filtro}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    with c2:
        st.download_button("📄 DESCARGAR PDF", data=to_pdf_3d(), file_name=f"MUERTE_PERINATAL_3D_{ano_filtro}.pdf", mime="application/pdf", use_container_width=True)
