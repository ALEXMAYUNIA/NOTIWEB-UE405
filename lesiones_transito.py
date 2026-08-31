
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
    modo = st.radio("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos (para Licenciada - Excel diferente)"], horizontal=True, key="les_modo")

    lista_df = []
    archivos = []
    archivos_fallidos = []

    if modo == "📤 Subir archivos (para Licenciada - Excel diferente)":
        archivos_subidos = st.file_uploader("📂 Arrastra aquí tus archivos Excel de LESIONES DE TRANSITO (cada módulo tiene excel diferente - este usa lug_accid, dia_accd, mes_accd, ano_accd, mome_accid, dx1_categ, etc.)", type=['xlsx','xls','csv'], accept_multiple_files=True, key="les_upload")
        if not archivos_subidos:
            st.info("👆 Sube tus archivos Excel de LESIONES DE TRANSITO - Cada módulo es diferente: este módulo usa columnas lug_accid, dia_accd, mes_accd, ano_accd, mome_accid, dx1_categ, dx2_categ, sexo, edad, tcasos")
            return
        archivos = [f.name for f in archivos_subidos]
        st.write(f"📂 Total archivos cargados: {len(archivos)}")
        progress = st.progress(0)
        for idx, f in enumerate(archivos_subidos):
            progress.progress((idx+1)/len(archivos_subidos))
            df_temp = None
            for engine in ['openpyxl', 'xlrd', None]:
                try:
                    if f.name.lower().endswith('.csv'):
                        df_temp = pd.read_csv(f, encoding='utf-8', low_memory=False)
                    else:
                        if engine:
                            df_temp = pd.read_excel(f, engine=engine, header=0)
                        else:
                            df_temp = pd.read_excel(f, header=0)
                    if df_temp is not None and not df_temp.empty:
                        if len(df_temp.columns) < 3:
                            try:
                                df_temp2 = pd.read_excel(f, engine='openpyxl', header=1)
                                if len(df_temp2.columns) > len(df_temp.columns):
                                    df_temp = df_temp2
                            except:
                                pass
                        break
                except Exception as e:
                    continue
            if df_temp is not None and not df_temp.empty:
                try:
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                    df_temp = df_temp.dropna(axis=1, how='all')
                    df_temp = df_temp.dropna(how='all')
                    lista_df.append(df_temp)
                except:
                    archivos_fallidos.append(f.name)
            else:
                archivos_fallidos.append(f.name)
        progress.empty()
    else:
        RUTA_BASE = os.path.dirname(__file__)
        ruta_carpeta = os.path.join(RUTA_BASE, 'LESIONES DE TRANSITO')
        if not os.path.exists(ruta_carpeta):
            ruta_carpeta = 'LESIONES DE TRANSITO'
        st.info(f"📁 Analizando: LESIONES DE TRANSITO - Excel LESIONES TRANSITO tiene columnas: lug_accid, dia_accd, mes_accd, ano_accd, mome_accid, dx1_categ, sexo, edad, tcasos")
        if not os.path.exists(ruta_carpeta):
            st.warning("No existe la carpeta LESIONES DE TRANSITO - Usa modo Subir archivos")
            return
        archivos_raw = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
        archivos = archivos_raw
        if not archivos:
            st.warning("La carpeta LESIONES DE TRANSITO esta vacia")
            return
        st.write(f"📂 Total archivos encontrados: {len(archivos)}")
        progress = st.progress(0)
        for idx, archivo in enumerate(archivos):
            progress.progress((idx+1)/len(archivos))
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            df_temp = None
            for engine in ['openpyxl', 'xlrd', None]:
                try:
                    if archivo.lower().endswith('.csv'):
                        df_temp = pd.read_csv(ruta_archivo, encoding='utf-8', low_memory=False)
                    else:
                        if engine:
                            df_temp = pd.read_excel(ruta_archivo, engine=engine, header=0)
                        else:
                            df_temp = pd.read_excel(ruta_archivo, header=0)
                    if df_temp is not None and not df_temp.empty:
                        if len(df_temp.columns) < 3:
                            try:
                                df_temp2 = pd.read_excel(ruta_archivo, engine='openpyxl', header=1)
                                if len(df_temp2.columns) > len(df_temp.columns):
                                    df_temp = df_temp2
                            except:
                                pass
                        break
                except Exception as e:
                    continue
            
            if df_temp is not None and not df_temp.empty:
                try:
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                    df_temp = df_temp.dropna(axis=1, how='all')
                    lista_df.append(df_temp)
                except:
                    archivos_fallidos.append(archivo)
            else:
                archivos_fallidos.append(archivo)

        progress.empty()

    if not lista_df:
        st.error("No se pudo leer ningun archivo valido")
        if archivos_fallidos:
            st.write(archivos_fallidos)
        return

    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)} - Total registros: {sum(len(d) for d in lista_df)} - Excel diferente: LESIONES TRANSITO usa lug_accid, dia_accd, ano_accd, mome_accid, dx1_categ")
    if archivos_fallidos:
        with st.expander(f"⚠️ {len(archivos_fallidos)} archivos no leidos"):
            st.write(archivos_fallidos)

    df = pd.concat(lista_df, ignore_index=True, sort=False)
    df.columns = df.columns.astype(str).str.lower().str.strip()

    # ============ MAPEO CON TUS COLUMNAS REALES ============
    df['RED'] = df.get('red', 'SIN DATO')
    df['MICRORED'] = df.get('microred', 'SIN DATO')
    df['ESTABLECIMIENTO'] = df.get('eess', df.get('establecimiento', 'SIN DATO'))
    df['DEPARTAMENTO'] = df.get('depar', 'SIN DATO')
    df['PROVINCIA'] = df.get('prov', 'SIN DATO')
    df['DISTRITO'] = df.get('dis', 'SIN DATO')
    df['LUGAR_ACCIDENTE'] = df.get('lug_accid', 'SIN DATO')
    df['DIA_ACCIDENTE'] = df.get('dia_accd', 'S/D')
    df['MES_ACCIDENTE'] = df.get('mes_accd', 'S/D')
    
    df['AÑO'] = pd.to_numeric(df.get('ano_accd', df.get('ano', 0)), errors='coerce')
    df['AÑO'] = df['AÑO'].fillna(0).astype(int).astype(str)
    df.loc[df['AÑO'] == '0', 'AÑO'] = 'S/D'

    df['HORA_DIA'] = df.get('mome_accid', 'SIN DATO')
    df['HORA_DIA'] = df['HORA_DIA'].fillna('SIN DATO').astype(str).str.strip()
    df.loc[df['HORA_DIA'] == '', 'HORA_DIA'] = 'SIN DATO'

    df['DX1_CATEG'] = df.get('dx1_categ', '').fillna('').astype(str).str.strip()
    df['DX2_CATEG'] = df.get('dx2_categ', '').fillna('').astype(str).str.strip()
    df['GRAVEDAD'] = df['DX1_CATEG']
    df.loc[df['GRAVEDAD'] == '', 'GRAVEDAD'] = df.loc[df['GRAVEDAD'] == '', 'DX2_CATEG']
    df.loc[df['GRAVEDAD'] == '', 'GRAVEDAD'] = 'NO ESPECIFICADO'

    sexo = df.get('sexo', pd.Series(['']*len(df))).astype(str).str.upper().str.strip()
    df['FEMENINOS'] = (sexo == 'F').astype(int)
    df['MASCULINOS'] = (sexo == 'M').astype(int)
    # Si no hay sexo, cuenta como 1
    if df['FEMENINOS'].sum() + df['MASCULINOS'].sum() == 0:
        df['FEMENINOS'] = 1

    df['EDAD'] = pd.to_numeric(df.get('edad'), errors='coerce').fillna(0)
    tcasos = df.get('tcasos', pd.Series([1]*len(df)))
    df['TOTAL_CASOS'] = pd.to_numeric(tcasos, errors='coerce').fillna(1).astype(int)
    df['MASCULINOS'] = df['MASCULINOS'] * df['TOTAL_CASOS']
    df['FEMENINOS'] = df['FEMENINOS'] * df['TOTAL_CASOS']

    condiciones = [
        (df['EDAD'] >= 0) & (df['EDAD'] <= 11),
        (df['EDAD'] >= 12) & (df['EDAD'] <= 17),
        (df['EDAD'] >= 18) & (df['EDAD'] <= 29),
        (df['EDAD'] >= 30) & (df['EDAD'] <= 59),
        (df['EDAD'] >= 60)
    ]
    categorias = ['NIÑO (0-11)', 'ADOLESCENTE (12-17)', 'JOVEN (18-29)', 'ADULTO (30-59)', 'ADULTO MAYOR (60+)']
    df['GRUPO_ETARIO'] = np.select(condiciones, categorias, default='SIN DATO')

    st.subheader("2. Filtros:")
    col1, col2, col3 = st.columns(3)
    with col1:
        anos_disponibles = ['TODOS'] + sorted([x for x in df['AÑO'].unique() if x!= 'S/D'])
        ano_filtro = st.selectbox("Filtrar por AÑO ACCIDENTE:", anos_disponibles, key='lt_ano')
    with col2:
        prov_disponibles = ['TODAS'] + sorted([x for x in df['PROVINCIA'].astype(str).unique().tolist() if x!='nan' and x!='SIN DATO'])
        prov_filtro = st.selectbox("Filtrar por PROVINCIA:", prov_disponibles, key='lt_prov')
    with col3:
        lugar_disponibles = ['TODOS'] + sorted([x for x in df['LUGAR_ACCIDENTE'].astype(str).unique().tolist() if x!='nan' and x!='SIN DATO'])[:20]
        lugar_filtro = st.selectbox("Filtrar por LUGAR ACCIDENTE:", lugar_disponibles, key='lt_lugar')

    df_filtrado = df.copy()
    if ano_filtro != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['AÑO'] == ano_filtro]
    if prov_filtro != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['PROVINCIA'].astype(str) == prov_filtro]
    if lugar_filtro != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['LUGAR_ACCIDENTE'].astype(str) == lugar_filtro]

    total_general = int(df_filtrado['TOTAL_CASOS'].sum())
    total_f = int(df_filtrado['FEMENINOS'].sum())
    total_m = int(df_filtrado['MASCULINOS'].sum())
    porc_f = (total_f/total_general*100) if total_general>0 else 0
    porc_m = (total_m/total_general*100) if total_general>0 else 0

    st.subheader("TABLA 1 - Lesiones Tránsito Detalle")
    st.info(f"Total registros filtrados: {len(df_filtrado)} | Total casos: {total_general} | F: {total_f} M: {total_m}")

    # Tabla 1 agrupada para visualización
    tabla1 = df_filtrado.groupby(['AÑO','PROVINCIA','DISTRITO','ESTABLECIMIENTO','LUGAR_ACCIDENTE','GRAVEDAD','HORA_DIA'], dropna=False)[['FEMENINOS','MASCULINOS','TOTAL_CASOS']].sum().reset_index()
    tabla1 = tabla1.rename(columns={'TOTAL_CASOS':'TOTAL'})
    tabla1 = tabla1.sort_values('TOTAL', ascending=False)
    st.dataframe(tabla1.head(100), use_container_width=True, height=350)

    # Tabla grafico por año
    tabla_graf = df_filtrado.groupby('AÑO', dropna=False)[['FEMENINOS','MASCULINOS']].sum().reset_index()
    tabla_graf['TOTAL'] = tabla_graf['FEMENINOS']+tabla_graf['MASCULINOS']
    tabla_graf = tabla_graf[tabla_graf['AÑO']!='S/D'].sort_values('AÑO')

    c1,c2 = st.columns(2)
    with c1:
        fig1 = px.bar(tabla_graf, x='AÑO', y=['FEMENINOS','MASCULINOS'], title='Casos por Año según Sexo', barmode='stack', color_discrete_map={'FEMENINOS':'#FF6FB5','MASCULINOS':'#0EA5E9'}, text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        data_sexo = pd.DataFrame({'SEXO':['Femenino','Masculino'],'Casos':[total_f,total_m]})
        fig2 = px.pie(data_sexo, names='SEXO', values='Casos', title='Distribución por Sexo', hole=0.3, color='SEXO', color_discrete_map={'Femenino':'#FF6FB5','Masculino':'#0EA5E9'})
        fig2.update_traces(textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("TABLA 2 y GRAFICO 3 - Grupo Etario")
    tabla2 = df_filtrado.groupby('GRUPO_ETARIO', dropna=False)[['FEMENINOS','MASCULINOS','TOTAL_CASOS']].sum().reset_index().rename(columns={'TOTAL_CASOS':'TOTAL'})
    tabla2 = tabla2.sort_values('TOTAL', ascending=False)
    st.dataframe(tabla2, use_container_width=True, hide_index=True)
    fig3 = px.bar(tabla2, x='GRUPO_ETARIO', y='TOTAL', title='Lesiones Tránsito por Grupo Etario', text='TOTAL', color='GRUPO_ETARIO')
    fig3.update_traces(textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

    # Datos para tabla lugar y gravedad
    top_prov_nombre = df_filtrado.groupby('PROVINCIA')['TOTAL_CASOS'].sum().idxmax() if not df_filtrado.empty else 'S/D'

    def to_excel_pro():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            wb = writer.book
            hdr = wb.add_format({'bold':True,'bg_color':'#1c2e4a','font_color':'white','border':1,'align':'center'})
            cell = wb.add_format({'border':1,'align':'center'})
            title = wb.add_format({'bold':True,'font_size':12,'bg_color':'#D9E1F2','border':1})

            # Hoja 1 Detalle
            s1 = 'TABLA_1_DETALLE'
            df_exp = tabla1.replace([np.inf,-np.inf], np.nan).fillna('')
            df_exp.to_excel(writer, sheet_name=s1, index=False, startrow=1)
            ws = writer.sheets[s1]
            ws.write(0,0,f"LESIONES TRANSITO - {ano_filtro}/{prov_filtro}/{lugar_filtro} - Total {total_general} casos - {len(lista_df)} archivos - Excel diferente: lug_accid, mome_accid, dx1_categ", title)
            for c,v in enumerate(df_exp.columns):
                ws.write(1,c,v,hdr)
            for r in range(len(df_exp)):
                for c in range(len(df_exp.columns)):
                    ws.write(r+2,c,str(df_exp.iloc[r,c]),cell)
            ws.set_column('A:Z',18)

            # Hoja 2 año
            s2 = 'POR_AÑO'
            tabla_graf.to_excel(writer, sheet_name=s2, index=False, startrow=1)
            ws2 = writer.sheets[s2]
            ws2.write(0,0,f"Por Año - {total_general} casos", title)
            for c,v in enumerate(tabla_graf.columns):
                ws2.write(1,c,v,hdr)
            for r in range(len(tabla_graf)):
                for c in range(len(tabla_graf.columns)):
                    ws2.write(r+2,c,tabla_graf.iloc[r,c],cell)

            # Hoja 3 etario
            s3 = 'GRUPO_ETARIO'
            tabla2.to_excel(writer, sheet_name=s3, index=False, startrow=1)
            ws3 = writer.sheets[s3]
            ws3.write(0,0,"Grupo Etario", title)
            for c,v in enumerate(tabla2.columns):
                ws3.write(1,c,v,hdr)
            for r in range(len(tabla2)):
                for c in range(len(tabla2.columns)):
                    ws3.write(r+2,c,tabla2.iloc[r,c],cell)
        return output.getvalue()

    def to_pdf_completo():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        stt = ParagraphStyle('T', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#1c2e4a'), alignment=1, spaceAfter=8)
        sh2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1c2e4a'), spaceAfter=4, spaceBefore=10)
        s_desc = ParagraphStyle('Desc', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor('#334155'), leftIndent=6, borderPadding=6, backColor=colors.HexColor('#f8fafc'), spaceAfter=6)
        story = []
        story.append(Paragraph(f"<b>ANALISIS NOTIWEB 2026 - LESIONES DE TRANSITO UE 405</b><br/>Filtros: {ano_filtro}/{prov_filtro}/{lugar_filtro} - Total: {total_general} casos (F:{total_f} M:{total_m}) - {len(lista_df)} archivos de {len(archivos)} - Excel diferente: lug_accid, mome_accid, dx1_categ - {datetime.now().strftime('%d/%m/%Y')}", stt))
        story.append(Spacer(1,8))
        # Resumen
        story.append(Paragraph(f"Resumen: Se registraron <b>{total_general} casos</b> en {len(lista_df)} archivos. Distribucion {porc_f:.1f}% mujeres y {porc_m:.1f}% varones. Provincia con mayor carga: {top_prov_nombre}. Lugar accidente predominante y gravedad analizados. Cada modulo tiene excel diferente.", s_desc))
        story.append(Spacer(1,6))
        # Tabla 1
        story.append(Paragraph("<b>2. TABLA 1: Lesiones Transito Detalle (Top 20)</b>", sh2))
        data=[['AÑO','PROV','DIST','EESS','LUGAR','GRAVEDAD','HORA','F','M','TOTAL']]
        for _,r in tabla1.sort_values('TOTAL', ascending=False).head(20).iterrows():
            data.append([str(r['AÑO']),str(r['PROVINCIA'])[:8],str(r['DISTRITO'])[:8],str(r['ESTABLECIMIENTO'])[:12],str(r['LUGAR_ACCIDENTE'])[:10],str(r['GRAVEDAD'])[:10],str(r['HORA_DIA'])[:8],str(r['FEMENINOS']),str(r['MASCULINOS']),str(r['TOTAL'])])
        t=Table(data, colWidths=[25,35,35,60,40,40,30,20,20,25])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),6)]))
        story.append(t); story.append(Spacer(1,6))
        desc1 = f"Tabla 1 muestra los 20 EESS con mayor notificacion. Total {total_general} casos en {len(tabla1)} registros filtrados. Provincia {top_prov_nombre} concentra la mayor carga. Lugar de accidente mas frecuente: {tabla1['LUGAR_ACCIDENTE'].value_counts().index[0] if not tabla1.empty else 'S/D'} con {tabla1['LUGAR_ACCIDENTE'].value_counts().values[0] if not tabla1.empty else 0} casos. Gravedad predominante: {tabla1['GRAVEDAD'].value_counts().index[0] if not tabla1.empty else 'S/D'}. Esto indica necesidad de intervencion en seguridad vial y atencion de emergencias."
        story.append(Paragraph(desc1, s_desc))
        # GRAFICO 1
        fig,ax=plt.subplots(figsize=(5.5,2.2))
        ax.bar(tabla_graf['AÑO'].astype(str), tabla_graf['FEMENINOS'], label='F', color='#FF6FB5')
        ax.bar(tabla_graf['AÑO'].astype(str), tabla_graf['MASCULINOS'], bottom=tabla_graf['FEMENINOS'], label='M', color='#0EA5E9')
        ax.set_title('Casos por Año', fontsize=10); ax.legend(fontsize=7); plt.tight_layout()
        b=BytesIO(); plt.savefig(b, format='png', dpi=150); plt.close(); b.seek(0)
        story.append(Paragraph("<b>3. GRAFICO 1: Tendencia Anual por Sexo</b>", sh2))
        story.append(Image(b, width=420, height=150)); story.append(Spacer(1,4))
        if not tabla_graf.empty:
            ano_max = tabla_graf.loc[(tabla_graf['FEMENINOS']+tabla_graf['MASCULINOS']).idxmax(),'AÑO']; max_v=int((tabla_graf['FEMENINOS']+tabla_graf['MASCULINOS']).max())
        else:
            ano_max='S/D'; max_v=0
        g1 = f"El año con mayor registro fue <b>{ano_max} con {max_v} casos</b>. Tendencia muestra variacion anual relacionada a movilidad y operativos. Proporcion F/M se mantiene. Mantener vigilancia continua."
        story.append(Paragraph(g1, s_desc))
        # GRAFICO 2 SEXO
        fig,axes=plt.subplots(1,2, figsize=(5,1.8))
        axes[0].pie([porc_f,100-porc_f], colors=['#FF6FB5','#f1f5f9'], wedgeprops={'width':0.4}); axes[0].text(0,0,f"{porc_f:.0f}%", ha='center', weight='bold', color='#FF6FB5')
        axes[1].pie([porc_m,100-porc_m], colors=['#0EA5E9','#f1f5f9'], wedgeprops={'width':0.4}); axes[1].text(0,0,f"{porc_m:.0f}%", ha='center', weight='bold', color='#0EA5E9')
        plt.tight_layout(); b2=BytesIO(); plt.savefig(b2, format='png', dpi=150); plt.close(); b2.seek(0)
        story.append(Paragraph("<b>4. GRAFICO 2: Distribucion por Sexo</b>", sh2))
        story.append(Image(b2, width=320, height=110)); story.append(Spacer(1,4))
        s1 = f"Distribucion: <b>{porc_f:.1f}% mujeres ({total_f}) y {porc_m:.1f}% varones ({total_m})</b>. En lesiones de transito predomina varones por mayor exposicion laboral y conduccion. Requiere abordaje diferenciado y educacion vial con enfoque de genero."
        story.append(Paragraph(s1, s_desc))
        # GRAFICO 3 ETARIO + TABLA 2
        fig,ax=plt.subplots(figsize=(5.5,2.2))
        tabla2_sorted=tabla2.sort_values('TOTAL')
        ax.barh(tabla2_sorted['GRUPO_ETARIO'], tabla2_sorted['TOTAL'], color='#1c2e4a')
        ax.set_title('Lesiones Transito por Grupo Etario', fontsize=10); plt.tight_layout()
        b3=BytesIO(); plt.savefig(b3, format='png', dpi=150); plt.close(); b3.seek(0)
        story.append(Paragraph("<b>5. GRAFICO 3 y TABLA 2: Grupo Etario</b>", sh2))
        story.append(Image(b3, width=420, height=150)); story.append(Spacer(1,4))
        grupo_max=tabla2.iloc[0]['GRUPO_ETARIO'] if not tabla2.empty else "S/D"; grupo_max_n=int(tabla2.iloc[0]['TOTAL']) if not tabla2.empty else 0
        e1 = f"Grupo mas afectado: <b>{grupo_max} con {grupo_max_n} casos ({grupo_max_n/total_general*100:.1f}%)</b>. Adultos jovenes 18-29 y adultos 30-59 concentran mayoria por actividad laboral. Jovenes requieren prevencion en colegios y campanas de seguridad vial. Adulto mayor vulnerable por fragilidad."
        story.append(Paragraph(e1, s_desc))
        # TABLA 2 DETALLE
        data2=[['Grupo Etario','F','M','Total','%']]
        for _,r in tabla2.iterrows():
            data2.append([r['GRUPO_ETARIO'], str(r['FEMENINOS']), str(r['MASCULINOS']), str(r['TOTAL']), f"{r['TOTAL']/total_general*100:.1f}%" if total_general else "0%"])
        t2=Table(data2, colWidths=[90,30,30,35,35])
        t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),7)]))
        story.append(t2); story.append(Spacer(1,10))
        # TABLA LUGAR Y GRAVEDAD
        story.append(Paragraph("<b>6. TABLA 3: Lugar y Gravedad</b>", sh2))
        lugar_tab = df_filtrado.groupby('LUGAR_ACCIDENTE')['TOTAL_CASOS'].sum().sort_values(ascending=False).head(5)
        grav_tab = df_filtrado.groupby('GRAVEDAD')['TOTAL_CASOS'].sum().sort_values(ascending=False).head(5)
        data3=[['Lugar Accidente','Casos'], [f"{lugar_tab.index[0]}", str(lugar_tab.values[0])] if not lugar_tab.empty else ["S/D","0"]]
        for i in range(1, len(lugar_tab)):
            data3.append([str(lugar_tab.index[i]), str(lugar_tab.values[i])])
        t3=Table(data3, colWidths=[120,40])
        t3.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),7)]))
        story.append(t3); story.append(Spacer(1,6))
        story.append(Paragraph(f"<b>Conclusiones:</b> 1. {total_general} casos en {len(archivos)} archivos leidos ({len(lista_df)} validos). 2. Grupo mas afectado {grupo_max}. 3. Lugar predominante {tabla1['LUGAR_ACCIDENTE'].value_counts().index[0] if not tabla1.empty else 'S/D'}. 4. Fortalecer prevencion vial, atencion prehospitalaria y notificacion oportuna. 5. Capacitacion continua personal RSH.", s_desc))
        doc.build(story)
        return buffer.getvalue()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📊 DESCARGAR EXCEL", data=to_excel_pro(), file_name=f"LESIONES_TRANSITO_PRO_{ano_filtro}_{prov_filtro}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    with col2:
        st.download_button("📄 DESCARGAR PDF ", data=to_pdf_completo(), file_name=f"LESIONES_TRANSITO_PDF_GRAFICOS_{ano_filtro}.pdf", mime="application/pdf", use_container_width=True)
