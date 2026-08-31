import streamlit as st
import pandas as pd
import os
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from io import BytesIO
import xlsxwriter
from datetime import datetime
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

def mostrar_pagina():
    st.markdown("**Modo Licenciada: Subir archivos | Modo Técnico: Carpeta automática**")
    modo = st.radio("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos (para Licenciada - Excel diferente)"], horizontal=True, key="plag_modo")

    RUTA_BASE = os.path.dirname(__file__)
    ruta_carpeta = os.path.join(RUTA_BASE, 'PLAGUICIDAS')

    lista_df = []
    archivos_fallidos = []
    archivos = []

    if modo == "📤 Subir archivos (para Licenciada - Excel diferente)":
        uploaded_files = st.file_uploader("Sube archivos Excel/CSV de PLAGUICIDAS (puede ser diferente formato - se adapta)", type=['xlsx','xls','csv'], accept_multiple_files=True, key="plag_uploader")
        if not uploaded_files:
            st.info("👆 Sube uno o más archivos para procesar - Excel diferente soportado")
            return
        archivos = [f.name for f in uploaded_files]
        progress = st.progress(0)
        for idx, archivo_obj in enumerate(uploaded_files):
            progress.progress((idx+1)/len(uploaded_files))
            df_temp = None
            nombre = archivo_obj.name
            try:
                if nombre.lower().endswith('.csv'):
                    archivo_obj.seek(0)
                    df_temp = pd.read_csv(archivo_obj, encoding='utf-8', low_memory=False)
                else:
                    archivo_obj.seek(0)
                    try:
                        df_temp = pd.read_excel(archivo_obj, engine='openpyxl', header=0)
                    except:
                        try:
                            archivo_obj.seek(0)
                            df_temp = pd.read_excel(archivo_obj, engine='xlrd', header=0)
                        except:
                            archivo_obj.seek(0)
                            df_temp = pd.read_excel(archivo_obj, header=0)
            except:
                archivos_fallidos.append(nombre)
                continue

            if df_temp is not None and not df_temp.empty:
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                df_temp = df_temp.dropna(how='all')
                df_temp = df_temp.dropna(axis=1, how='all')
                lista_df.append(df_temp)
            else:
                archivos_fallidos.append(nombre)
        progress.empty()
    else:
        # MODO CARPETA AUTOMATICA
        if not os.path.exists(ruta_carpeta):
            st.error(f"No existe la carpeta: {ruta_carpeta}")
            st.warning("Usa modo Subir archivos")
            return

        archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
        
        if not archivos:
            st.warning("La carpeta PLAGUICIDAS esta vacia")
            st.warning("Usa modo Subir archivos")
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
            except:
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

    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)} - Total: {sum(len(d) for d in lista_df)} casos - Excel diferente soportado (Modo Licenciada)")
    if archivos_fallidos:
        with st.expander(f"{len(archivos_fallidos)} archivos no leidos"):
            st.write(archivos_fallidos)

    df = pd.concat(lista_df, ignore_index=True, sort=False)
    df.columns = df.columns.astype(str).str.lower().str.strip()

    def col(*nombres):
        for nombre in nombres:
            if nombre in df.columns:
                return df[nombre]
        return pd.Series([None] * len(df))

    df['ANIO'] = pd.to_numeric(col('año', 'anio', 'ano', 'year'), errors='coerce')
    df['ANIO'] = df['ANIO'].fillna(0).astype(int).astype(str)
    df.loc[df['ANIO'] == '0', 'ANIO'] = 'S/D'

    df['DEPARTAMEN'] = col('disa', 'departamen').astype(str).str.strip()
    df['DEPARTAMEN'] = df['DEPARTAMEN'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    df['PROVINCIA'] = col('red', 'provincia').astype(str).str.strip()
    df['PROVINCIA'] = df['PROVINCIA'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    df['DISTRITO'] = col('microredes', 'microred', 'distrito').astype(str).str.strip()
    df['DISTRITO'] = df['DISTRITO'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    df['MICROREDES'] = df['DISTRITO']
    df['ESTABLECIMINETO'] = col('raz_soc', 'eess', 'establecimiento').astype(str).str.strip()
    df['ESTABLECIMINETO'] = df['ESTABLECIMINETO'].replace(['', 'nan', 'None', '0'], 'SIN DATO').fillna('SIN DATO')
    
    sexo = col('sexo', '').astype(str).str.upper().str.strip()
    df['SEXO'] = 'INDETERMINADO'
    df.loc[sexo == 'M', 'SEXO'] = 'MASCULINO'
    df.loc[sexo == 'F', 'SEXO'] = 'FEMENINO'

    df['EDAD'] = pd.to_numeric(col('edad', 0), errors='coerce').fillna(0).astype(int)
    # GRUPO ETARIO
    condiciones = [(df['EDAD']>=0)&(df['EDAD']<=11),(df['EDAD']>=12)&(df['EDAD']<=17),(df['EDAD']>=18)&(df['EDAD']<=29),(df['EDAD']>=30)&(df['EDAD']<=59),(df['EDAD']>=60)]
    categorias = ['NIÑO (0-11)','ADOLESCENTE (12-17)','JOVEN (18-29)','ADULTO (30-59)','ADULTO MAYOR (60+)']
    df['GRUPO_ETARIO'] = np.select(condiciones, categorias, default='SIN DATO')
    
    df['FECHA_NOTIF'] = pd.to_datetime(col('fecha_not', 'fecha_notif'), errors='coerce').dt.strftime('%d/%m/%Y')
    df['FECHA_NOTIF'] = df['FECHA_NOTIF'].fillna('S/D')
    df['CAUSA'] = col('causa_bas', 'causa').astype(str).str.strip().replace(['', 'nan', 'None', '0'], '')
    df['FALLECIDA'] = col('otro9', '').astype(str).str.upper().str.strip().replace(['', 'nan', 'None', '0'], 'NO')
    df.loc[df['FALLECIDA']!= 'FALLECIDA', 'FALLECIDA'] = 'NO'

    tipo = pd.to_numeric(col('tipo_intox', 0), errors='coerce').fillna(0).astype(int)
    df['TIPO_INTOX'] = tipo
    condiciones_gravedad = [(tipo == 1), (tipo == 2), (tipo == 3), (tipo == 4)]
    categorias_gravedad = ['EXTREMADAMENTE Y MUY PELIGROSOS (BANDA ROJA)','MODERADAMENTE PELIGROSOS (BANDA AMARILLA)','LIGERAMENTE PELIGROSOS (BANDA AZUL)','NORMALMENTE NO OFRECEN PELIGRO (BANDA VERDE)']
    df['DESC_GRAVEDAD'] = np.select(condiciones_gravedad, categorias_gravedad, default='')

    st.subheader("2. Filtros:")
    col1, col2, col3 = st.columns(3)
    with col1:
        anos_raw = [str(x) for x in df['ANIO'].astype(str).unique().tolist() if str(x).lower() not in ['nan','s/d','']]
        anos_disponibles = ['TODOS'] + sorted(anos_raw, key=lambda x: int(x) if x.isdigit() else x)
        ano_filtro = st.selectbox("Filtrar por AÑO:", anos_disponibles, key='pla_ano')
    with col2:
        prov_raw = [str(x).strip() for x in df['PROVINCIA'].astype(str).unique().tolist() if str(x).lower() not in ['nan','sin dato','']]
        prov_disponibles = ['TODAS'] + sorted(prov_raw)
        prov_filtro = st.selectbox("Filtrar por PROVINCIA:", prov_disponibles, key='pla_prov')
    with col3:
        if prov_filtro!= 'TODAS':
            distritos_filtrados = df[df['PROVINCIA'].astype(str) == prov_filtro]['DISTRITO'].astype(str).unique().tolist()
        else:
            distritos_filtrados = df['DISTRITO'].astype(str).unique().tolist()
        dis_raw = [str(x).strip() for x in distritos_filtrados if str(x).lower() not in ['nan','sin dato','']]
        dis_disponibles = ['TODOS'] + sorted(dis_raw)
        dis_filtro = st.selectbox("Filtrar por DISTRITO:", dis_disponibles, key='pla_dis')

    df_filtrado = df.copy()
    if ano_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['ANIO'].astype(str) == str(ano_filtro)]
    if prov_filtro!= 'TODAS': df_filtrado = df_filtrado[df_filtrado['PROVINCIA'].astype(str) == str(prov_filtro)]
    if dis_filtro!= 'TODOS': df_filtrado = df_filtrado[df_filtrado['DISTRITO'].astype(str) == str(dis_filtro)]

    st.subheader("TABLA 1: Casos de INTOXICACION POR PLAGUICIDAS")
    columnas_tabla1 = ['ANIO', 'DEPARTAMEN', 'PROVINCIA', 'DISTRITO', 'MICROREDES', 'ESTABLECIMINETO','SEXO', 'EDAD', 'GRUPO_ETARIO', 'FECHA_NOTIF', 'CAUSA', 'FALLECIDA', 'TIPO_INTOX', 'DESC_GRAVEDAD']
    for c in columnas_tabla1:
        if c not in df_filtrado.columns:
            df_filtrado[c]='S/D'
    tabla1 = df_filtrado[columnas_tabla1].copy()
    tabla1['TOTAL'] = 1
    total_general = len(tabla1)
    total_fallecidos = (df_filtrado['FALLECIDA'] == 'FALLECIDA').sum()
    st.info(f"Total de casos: {total_general} | **Fallecidos registrados: {total_fallecidos}**")
    if total_general == 0:
        st.warning("No se registraron casos")
        return
    fila_total = {col: '' for col in columnas_tabla1}
    fila_total['ANIO'] = 'TOTAL GENERAL'
    fila_total['FALLECIDA'] = f'{total_fallecidos} FALLECIDOS' if total_fallecidos > 0 else ''
    fila_total['TOTAL'] = total_general
    tabla1_final = pd.concat([tabla1, pd.DataFrame([fila_total])], ignore_index=True)
    def colorear_tabla(row):
        if row['ANIO'] == 'TOTAL GENERAL':
            return ['background-color: #FFD700; font-weight: bold; border: 2px solid black'] * len(row)
        elif row['FALLECIDA'] == 'FALLECIDA':
            return ['background-color: #FFCCCB; font-weight: bold; border: 1px solid red'] * len(row)
        else:
            return ['border: 1px solid #ddd'] * len(row)
    st.dataframe(tabla1_final.style.apply(colorear_tabla, axis=1), use_container_width=True, hide_index=True)

    tabla_graf = df_filtrado.groupby('ANIO').size().reset_index(name='TOTAL')
    tabla_graf = tabla_graf[tabla_graf['ANIO']!= 'S/D']
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=tabla_graf['ANIO'], y=tabla_graf['TOTAL'], marker_color='#32CD32', text=tabla_graf['TOTAL'], textposition='outside'))
    fig1.update_layout(title=f'PLAGUICIDAS por AÑO - {total_general} casos', plot_bgcolor='#F5F5F5', paper_bgcolor='white', template='plotly_white')
    st.plotly_chart(fig1, use_container_width=True)

    tabla_gravedad = df_filtrado.groupby('DESC_GRAVEDAD').size().reset_index(name='TOTAL')
    tabla_gravedad = tabla_gravedad[tabla_gravedad['DESC_GRAVEDAD']!= '']
    colores_banda = {'EXTREMADAMENTE Y MUY PELIGROSOS (BANDA ROJA)': '#FF0000','MODERADAMENTE PELIGROSOS (BANDA AMARILLA)': '#FFD700','LIGERAMENTE PELIGROSOS (BANDA AZUL)': '#0000FF','NORMALMENTE NO OFRECEN PELIGRO (BANDA VERDE)': '#00FF00'}
    fig2 = go.Figure(data=[go.Pie(labels=tabla_gravedad['DESC_GRAVEDAD'], values=tabla_gravedad['TOTAL'], hole=0.3, pull=[0.05]*len(tabla_gravedad),
                                  marker=dict(colors=[colores_banda.get(x,'#888') for x in tabla_gravedad['DESC_GRAVEDAD']], line=dict(color='#000', width=1)),
                                  textinfo='percent', 
                                  textposition='inside',
                                  textfont=dict(size=16, color='white', family='Arial Black'),
                                  insidetextorientation='horizontal')])
    fig2.update_layout(title='Distribucion por Banda Toxicologica', template='plotly_white')
    st.plotly_chart(fig2, use_container_width=True)

    # TABLA 2 GRUPO ETARIO
    st.subheader("TABLA 2: GRUPO ETARIO")
    tabla_etario = df_filtrado.groupby('GRUPO_ETARIO').size().reset_index(name='TOTAL')
    tabla_etario = tabla_etario.sort_values('TOTAL', ascending=False)
    # Calcula sexo dentro
    tabla_etario_det = df_filtrado.groupby(['GRUPO_ETARIO','SEXO']).size().unstack(fill_value=0).reset_index()
    for col in ['MASCULINO','FEMENINO','INDETERMINADO']:
        if col not in tabla_etario_det.columns:
            tabla_etario_det[col]=0
    tabla_etario_det['TOTAL']=tabla_etario_det.get('MASCULINO',0)+tabla_etario_det.get('FEMENINO',0)+tabla_etario_det.get('INDETERMINADO',0)
    st.dataframe(tabla_etario_det, use_container_width=True, hide_index=True)

    colores_etario = {'NIÑO (0-11)': '#8BC34A', 'ADOLESCENTE (12-17)': '#00BCD4', 'JOVEN (18-29)': '#FF9800','ADULTO (30-59)': '#FFEB3B', 'ADULTO MAYOR (60+)': '#E91E63', 'SIN DATO': '#F44336'}
    fig3 = px.bar(tabla_etario, x='GRUPO_ETARIO', y='TOTAL', title='Casos por Grupo Etario', color='GRUPO_ETARIO', color_discrete_map=colores_etario, text='TOTAL')
    fig3.update_traces(textposition='outside')
    fig3.update_layout(template='plotly_white', showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    # DESCARGAS
    def to_excel_pro():
        import numpy as np
        df_exp = tabla1_final.replace([np.inf, -np.inf], np.nan).fillna('')
        df_exp = df_exp.astype(str).replace(['nan','None'], '')
        df_exp2 = tabla_etario_det.replace([np.inf, -np.inf], np.nan).fillna(0)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            wb=writer.book
            hdr=wb.add_format({'bold':True,'bg_color':'#1c2e4a','font_color':'white','border':1,'align':'center'})
            tot=wb.add_format({'bold':True,'bg_color':'#FFD700','border':2,'align':'center'})
            cell=wb.add_format({'border':1,'align':'center'})
            title=wb.add_format({'bold':True,'font_size':12,'bg_color':'#D9E1F2','border':1})
            s1='TABLA_1_DETALLE'; df_exp.to_excel(writer, sheet_name=s1, index=False, startrow=1)
            ws=writer.sheets[s1]; ws.write(0,0,f"PLAGUICIDAS - {ano_filtro}/{prov_filtro}/{dis_filtro} - {total_general} casos",title)
            for c,v in enumerate(df_exp.columns): ws.write(1,c,v,hdr)
            for r in range(len(df_exp)):
                for c in range(len(df_exp.columns)):
                    f=tot if df_exp.iloc[r]['ANIO']=='TOTAL GENERAL' else cell
                    ws.write(r+2,c,str(df_exp.iloc[r,c]),f)
            ws.set_column('A:O',16)
            s2='BANDA_TOXICOLOGICA'; tabla_gravedad.to_excel(writer, sheet_name=s2, index=False, startrow=1)
            ws2=writer.sheets[s2]; ws2.write(0,0,"Banda Toxicologica",title)
            for c,v in enumerate(tabla_gravedad.columns): ws2.write(1,c,v,hdr)
            for r in range(len(tabla_gravedad)):
                for c in range(len(tabla_gravedad.columns)): ws2.write(r+2,c,tabla_gravedad.iloc[r,c],cell)
            s3='GRUPO_ETARIO'; df_exp2.to_excel(writer, sheet_name=s3, index=False, startrow=1)
            ws3=writer.sheets[s3]; ws3.write(0,0,"Grupo Etario",title)
            for c,v in enumerate(df_exp2.columns): ws3.write(1,c,v,hdr)
            for r in range(len(df_exp2)):
                for c in range(len(df_exp2.columns)): ws3.write(r+2,c,df_exp2.iloc[r,c],cell)
            s4='POR_AÑO'; tabla_graf.to_excel(writer, sheet_name=s4, index=False, startrow=1)
            ws4=writer.sheets[s4]
            for c,v in enumerate(tabla_graf.columns): ws4.write(1,c,v,hdr)
            for r in range(len(tabla_graf)):
                for c in range(len(tabla_graf.columns)): ws4.write(r+2,c,tabla_graf.iloc[r,c],cell)
        return output.getvalue()

    def to_pdf_3d():
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles=getSampleStyleSheet()
        stt=ParagraphStyle('T', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#1c2e4a'), alignment=1, spaceAfter=8)
        sh2=ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1c2e4a'), spaceAfter=4, spaceBefore=10)
        s_desc=ParagraphStyle('Desc', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor('#334155'), leftIndent=6, borderPadding=6, backColor=colors.HexColor('#f8fafc'), spaceAfter=6)
        story=[]
        story.append(Paragraph(f"<b>ANALISIS NOTIWEB 2026 - PLAGUICIDAS UE 405 RSH</b><br/>Filtros: {ano_filtro}/{prov_filtro}/{dis_filtro} - Total: {total_general} casos - Fallecidos: {total_fallecidos} - {len(lista_df)} archivos - {datetime.now().strftime('%d/%m/%Y')}", stt))
        story.append(Spacer(1,8))
        story.append(Paragraph("<b>1. RESUMEN EJECUTIVO</b>", sh2))
        banda_top = tabla_gravedad.loc[tabla_gravedad['TOTAL'].idxmax(),'DESC_GRAVEDAD'] if not tabla_gravedad.empty else "S/D"
        banda_top_n = tabla_gravedad['TOTAL'].max() if not tabla_gravedad.empty else 0
        story.append(Paragraph(f"Se registraron <b>{total_general} casos de intoxicacion por plaguicidas</b> de {len(lista_df)} archivos (de {len(archivos)}). <b>Fallecidos: {total_fallecidos} ({total_fallecidos/total_general*100:.1f}%)</b>. Banda toxicologica predominante: <b>{banda_top} con {banda_top_n} casos ({banda_top_n/total_general*100:.1f}%)</b>. Grupo etario mas afectado: <b>{tabla_etario.iloc[0]['GRUPO_ETARIO'] if not tabla_etario.empty else 'S/D'}</b>. Provincia mayor carga: <b>{df_filtrado['PROVINCIA'].value_counts().index[0] if not df_filtrado.empty else 'S/D'}</b>. Requiere fortalecimiento en regulacion de plaguicidas y capacitacion.", s_desc))
        story.append(Paragraph("<b>2. TABLA 1: Detalle</b>", sh2))
        data=[['AÑO','PROV','DISTRITO','EESS','SEXO','EDAD','GRUPO','BANDA','FALLECIDA']]
        for _,r in tabla1.sort_values('ANIO').head(20).iterrows():
            data.append([str(r['ANIO']),str(r['PROVINCIA'])[:8],str(r['DISTRITO'])[:8],str(r['ESTABLECIMINETO'])[:10],str(r['SEXO'])[:1],str(r['EDAD']),str(r['GRUPO_ETARIO'])[:8],str(r['DESC_GRAVEDAD'])[:8],str(r['FALLECIDA'])])
        t=Table(data, colWidths=[25,35,35,45,20,20,35,35,30])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),6)]))
        story.append(t); story.append(Spacer(1,6))
        story.append(Paragraph(f"Tabla muestra 20 casos de {total_general}. Predominio de {banda_top}. Fallecidos {total_fallecidos} requieren atencion de emergencia y disponibilidad de antidotos.", s_desc))
        # GRAFICO 1
        fig,ax=plt.subplots(figsize=(5,2))
        ax.bar(tabla_graf['ANIO'].astype(str), tabla_graf['TOTAL'], color='#32CD32')
        ax.set_title('Por Año', fontsize=9); plt.tight_layout()
        b=BytesIO(); plt.savefig(b, format='png', dpi=150); plt.close(); b.seek(0)
        story.append(Paragraph("<b>3. GRAFICO 1: Por Año</b>", sh2))
        story.append(Image(b, width=400, height=130))
        # GRAFICO 2 - 3D PIE BANDA
        fig = plt.figure(figsize=(5,2.8))
        ax = fig.add_subplot(111)
        labels = tabla_gravedad['DESC_GRAVEDAD'].tolist()
        sizes = tabla_gravedad['TOTAL'].tolist()
        # colores reales banda
        color_map = {'EXTREMADAMENTE Y MUY PELIGROSOS (BANDA ROJA)': '#FF0000','MODERADAMENTE PELIGROSOS (BANDA AMARILLA)': '#FFD700','LIGERAMENTE PELIGROSOS (BANDA AZUL)': '#0000FF','NORMALMENTE NO OFRECEN PELIGRO (BANDA VERDE)': '#00FF00'}
        colors_pie = [color_map.get(l, '#888888') for l in labels]
        explode = [0.1 if 'ROJA' in l else 0 for l in labels]
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', colors=colors_pie, shadow=True, startangle=90, pctdistance=0.7)
        for t in texts: t.set_fontsize(5)
        for t in autotexts: t.set_fontsize(6)
        ax.set_title('Distribucion por Banda Toxicologica', fontsize=9)
        plt.tight_layout()
        b2=BytesIO(); plt.savefig(b2, format='png', dpi=150); plt.close(); b2.seek(0)
        story.append(Paragraph("<b>4. GRAFICO 2: Banda Toxicologica</b>", sh2))
        story.append(Image(b2, width=400, height=200)); story.append(Spacer(1,4))
        story.append(Paragraph(f"Banda mas frecuente: <b>{banda_top} {banda_top_n} casos ({banda_top_n/total_general*100:.1f}%)</b>. Rojo indica extremada toxicidad. Requiere control de venta de plaguicidas altamente peligrosos.", s_desc))
        # GRAFICO 3 - GRUPO ETARIO
        fig,ax=plt.subplots(figsize=(5,2))
        tabla_et_sorted=tabla_etario.sort_values('TOTAL')
        ax.barh(tabla_et_sorted['GRUPO_ETARIO'], tabla_et_sorted['TOTAL'], color='#1c2e4a')
        ax.set_title('Por Grupo Etario', fontsize=9); plt.tight_layout()
        b3=BytesIO(); plt.savefig(b3, format='png', dpi=150); plt.close(); b3.seek(0)
        story.append(Paragraph("<b>5. GRAFICO 3 y TABLA 2: Grupo Etario</b>", sh2))
        story.append(Image(b3, width=400, height=130)); story.append(Spacer(1,4))
        grupo_max = tabla_etario.iloc[0]['GRUPO_ETARIO'] if not tabla_etario.empty else "S/D"
        grupo_max_n = tabla_etario.iloc[0]['TOTAL'] if not tabla_etario.empty else 0
        story.append(Paragraph(f"Grupo mas afectado: <b>{grupo_max} con {grupo_max_n} casos ({grupo_max_n/total_general*100:.1f}%)</b>. Adultos jovenes por exposicion laboral agricola. Niños por intoxicacion accidental domestica. Requiere educacion en almacenamiento seguro.", s_desc))
        data2=[['Grupo Etario','M','F','TOTAL','%']]
        for _,r in tabla_etario_det.iterrows():
            data2.append([r['GRUPO_ETARIO'], str(r.get('MASCULINO',0)), str(r.get('FEMENINO',0)), str(r['TOTAL']), f"{r['TOTAL']/total_general*100:.1f}%"])
        t2=Table(data2, colWidths=[80,25,25,30,25])
        t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),7)]))
        story.append(t2)
        doc.build(story)
        return buffer.getvalue()

    c1,c2,c3=st.columns(3)
    with c1:
        st.download_button("📊 DESCARGAR EXCEL", data=to_excel_pro(), file_name=f"PLAGUICIDAS_PRO_{ano_filtro}_{prov_filtro}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    with c2:
        st.download_button("📄 DESCARGAR PDF ", data=to_pdf_3d(), file_name=f"PLAGUICIDAS_3D_{ano_filtro}.pdf", mime="application/pdf", use_container_width=True)
   