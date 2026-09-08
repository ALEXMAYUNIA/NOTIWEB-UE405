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
    st.subheader("Módulo LESIONES DE TRANSITO - Análisis")
    try:
        modo = st.segmented_control("Selecciona modo:", options=["📁 Carpeta automática", "📤 Subir archivos"], key="les_modo", default="📁 Carpeta automática")
    except AttributeError:
        try:
            modo = st.pills("Selecciona modo:", options=["📁 Carpeta automática", "📤 Subir archivos"], key="les_modo", default="📁 Carpeta automática")
        except AttributeError:
            modo = st.radio("Selecciona modo:", options=["📁 Carpeta automática", "📤 Subir archivos"], horizontal=True, key="les_modo")
    if modo is None:
        modo = "📁 Carpeta automática"

    lista_df = []
    archivos = []
    archivos_fallidos = []

    if "Subir" in modo:
        archivos_subidos = st.file_uploader("📂 Arrastra aquí tus archivos Excel de LESIONES DE TRANSITO", type=['xlsx','xls','csv'], accept_multiple_files=True, key="les_upload")
        if not archivos_subidos:
            st.info("👆 Sube tus archivos Excel de LESIONES DE TRANSITO")
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

    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)}")
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
        # FIX: evita error '<' not supported between float and str
        anos_raw = df['AÑO'].dropna().astype(str).str.strip().unique().tolist()
        anos_clean = [x for x in anos_raw if x.lower() not in ['nan','nat','none',''] and x != 'S/D']
        anos_disponibles = ['TODOS'] + sorted(anos_clean, key=lambda x: str(x))
        ano_filtro = st.selectbox("Filtrar por AÑO ACCIDENTE:", anos_disponibles, key='lt_ano')
    with col2:
        prov_raw = df['PROVINCIA'].dropna().astype(str).str.strip().unique().tolist()
        prov_clean = [x for x in prov_raw if x.lower() not in ['nan','nat','none',''] and x.upper() != 'SIN DATO']
        prov_disponibles = ['TODAS'] + sorted(prov_clean)
        prov_filtro = st.selectbox("Filtrar por PROVINCIA:", prov_disponibles, key='lt_prov')
    with col3:
        lugar_raw = df['LUGAR_ACCIDENTE'].dropna().astype(str).str.strip().unique().tolist()
        lugar_clean = [x for x in lugar_raw if x.lower() not in ['nan','nat','none',''] and x.upper() != 'SIN DATO']
        lugar_disponibles = ['TODOS'] + sorted(lugar_clean)[:20]
        lugar_filtro = st.selectbox("Filtrar por LUGAR ACCIDENTE:", lugar_disponibles, key='lt_lugar')

    df_filtrado = df.copy()
    if ano_filtro != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['AÑO'].astype(str).str.strip() == str(ano_filtro).strip()]
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


    # ============================================================
    # DESCARGAS — MISMA INFORMACIÓN QUE SE MUESTRA EN EL SISTEMA
    # ============================================================
    def to_excel_pro():
        output=BytesIO()
        with pd.ExcelWriter(output,engine='xlsxwriter',engine_kwargs={'options':{'nan_inf_to_errors':True}}) as writer:
            wb=writer.book
            navy,blue,light,gold='#1c2e4a','#4472C4','#D9E1F2','#FFD700'
            pink,cyan='#FF6FB5','#0EA5E9'
            title=wb.add_format({'bold':True,'font_size':16,'font_color':'white','bg_color':navy,'align':'left','valign':'vcenter'})
            sub=wb.add_format({'bold':True,'font_color':navy,'bg_color':light,'align':'left'})
            header=wb.add_format({'bold':True,'font_color':'white','bg_color':navy,'border':1,'align':'center','valign':'vcenter','text_wrap':True})
            cell=wb.add_format({'border':1,'align':'center','valign':'vcenter'})
            text=wb.add_format({'border':1,'align':'left','valign':'vcenter'})
            totalf=wb.add_format({'bold':True,'bg_color':gold,'border':2,'align':'center'})
            kpi=wb.add_format({'bold':True,'font_size':18,'font_color':navy,'border':1,'align':'center','valign':'vcenter'})
            kf=wb.add_format({'bold':True,'font_size':18,'font_color':pink,'border':1,'align':'center'})
            km=wb.add_format({'bold':True,'font_size':18,'font_color':cyan,'border':1,'align':'center'})

            ws=wb.add_worksheet('RESUMEN'); ws.hide_gridlines(2); ws.set_tab_color(blue)
            ws.merge_range('A1:H1','MÓDULO LESIONES DE TRÁNSITO — ANÁLISIS NOTIWEB',title)
            ws.merge_range('A2:H2',f'Año: {ano_filtro} | Provincia: {prov_filtro} | Lugar: {lugar_filtro} | Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',sub)
            ws.merge_range('A4:H4','INDICADORES DEL REPORTE',wb.add_format({'bold':True,'font_color':'white','bg_color':blue}))
            for a,b,label,val,fmt in [('A5:B5','A6:B7','TOTAL CASOS',total_general,kpi),('C5:D5','C6:D7','FEMENINOS',total_f,kf),('E5:F5','E6:F7','MASCULINOS',total_m,km),('G5:H5','G6:H7','REGISTROS',len(df_filtrado),kpi)]:
                ws.merge_range(a,label,sub); ws.merge_range(b,val,fmt)
            ws.set_column('A:H',16)

            d=tabla1.copy(); d.to_excel(writer,sheet_name='TABLA_1_DETALLE',index=False,startrow=2)
            w=writer.sheets['TABLA_1_DETALLE']; w.hide_gridlines(2); w.set_tab_color(navy)
            w.merge_range(0,0,0,len(d.columns)-1,'TABLA 1 — LESIONES DE TRÁNSITO DETALLE',title)
            w.merge_range(1,0,1,len(d.columns)-1,f'Filtros: {ano_filtro} | {prov_filtro} | {lugar_filtro}',sub)
            for c,v in enumerate(d.columns): w.write(2,c,v,header)
            for r in range(len(d)):
                for c in range(len(d.columns)):
                    v=d.iloc[r,c]; w.write(r+3,c,v,text if isinstance(v,str) else cell)
            w.set_column(0,len(d.columns)-1,17); w.autofilter(2,0,len(d)+2,len(d.columns)-1)

            g=tabla_graf.copy(); g.to_excel(writer,sheet_name='POR_AÑO',index=False,startrow=2)
            wg=writer.sheets['POR_AÑO']; wg.hide_gridlines(2); wg.set_tab_color(blue)
            wg.merge_range(0,0,0,len(g.columns)-1,'GRÁFICO 1 — CASOS POR AÑO SEGÚN SEXO',title)
            for c,v in enumerate(g.columns): wg.write(2,c,v,header)
            for r in range(len(g)):
                for c in range(len(g.columns)): wg.write(r+3,c,g.iloc[r,c],cell)
            wg.set_column('A:A',12); wg.set_column('B:D',14)
            ch=wb.add_chart({'type':'column'})
            lr=len(g)+3
            for col,name,color in [(2,'FEMENINOS',pink),(3,'MASCULINOS',cyan)]:
                ch.add_series({'name':name,'categories':f'=POR_AÑO!$A$4:$A${lr}','values':f'=POR_AÑO!${chr(64+col)}$4:${chr(64+col)}${lr}','fill':{'color':color},'border':{'color':color},'data_labels':{'value':True}})
            ch.set_title({'name':'Casos por Año según Sexo'}); ch.set_y_axis({'name':'Casos','major_gridlines':{'visible':False}}); ch.set_legend({'position':'bottom'}); ch.set_size({'width':650,'height':350})
            wg.insert_chart('F3',ch,{'object_position':1})

            e=tabla2.copy(); e.to_excel(writer,sheet_name='GRUPO_ETARIO',index=False,startrow=2)
            we=writer.sheets['GRUPO_ETARIO']; we.hide_gridlines(2); we.set_tab_color('#70AD47')
            we.merge_range(0,0,0,len(e.columns)-1,'TABLA 2 — GRUPO ETARIO',title)
            for c,v in enumerate(e.columns): we.write(2,c,v,header)
            for r in range(len(e)):
                for c in range(len(e.columns)): we.write(r+3,c,e.iloc[r,c],cell)
            we.set_column('A:A',28); we.set_column('B:D',14)
            ce=wb.add_chart({'type':'bar'})
            ce.add_series({'name':'TOTAL','categories':f'=GRUPO_ETARIO!$A$4:$A${len(e)+3}','values':f'=GRUPO_ETARIO!$D$4:$D${len(e)+3}','fill':{'color':'#1c2e4a'},'border':{'color':'#1c2e4a'},'data_labels':{'value':True}})
            ce.set_title({'name':'Lesiones Tránsito por Grupo Etario'}); ce.set_legend({'none':True}); ce.set_size({'width':650,'height':350})
            we.insert_chart('F3',ce,{'object_position':1})
        return output.getvalue()

    def to_pdf_completo():
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=34,leftMargin=34,topMargin=42,bottomMargin=42)
        styles=getSampleStyleSheet()
        title=ParagraphStyle('lt',parent=styles['Heading1'],fontSize=15,textColor=colors.HexColor('#1c2e4a'),alignment=1,spaceAfter=5)
        h2=ParagraphStyle('lh',parent=styles['Heading2'],fontSize=10,textColor=colors.HexColor('#1c2e4a'),spaceBefore=8,spaceAfter=5)
        desc=ParagraphStyle('ld',parent=styles['Normal'],fontSize=8.2,leading=11,textColor=colors.HexColor('#334155'),backColor=colors.HexColor('#F8FAFC'),borderPadding=6,spaceAfter=6)
        story=[Paragraph('MÓDULO LESIONES DE TRÁNSITO — ANÁLISIS NOTIWEB',title),
               Paragraph(f'Año: {ano_filtro} | Provincia: {prov_filtro} | Lugar: {lugar_filtro} | Total: {total_general} casos | Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',desc)]
        story.append(Paragraph('1. RESUMEN EJECUTIVO',h2))
        story.append(Paragraph(f'Se registraron <b>{total_general} casos</b>, con <b>{total_f} femeninos ({porc_f:.1f}%)</b> y <b>{total_m} masculinos ({porc_m:.1f}%)</b>.',desc))
        story.append(Paragraph('2. TABLA 1 — DETALLE',h2))
        dp=tabla1.head(20); data=[['AÑO','PROVINCIA','DISTRITO','EESS','LUGAR','GRAVEDAD','HORA','F','M','TOTAL']]
        for _,r in dp.iterrows(): data.append([str(r['AÑO']),str(r['PROVINCIA'])[:10],str(r['DISTRITO'])[:10],str(r['ESTABLECIMIENTO'])[:14],str(r['LUGAR_ACCIDENTE'])[:12],str(r['GRAVEDAD'])[:10],str(r['HORA_DIA'])[:8],str(r['FEMENINOS']),str(r['MASCULINOS']),str(r['TOTAL'])])
        t=Table(data,colWidths=[24,43,40,55,48,42,35,18,18,25],repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#D0D7DE')),('FONTSIZE',(0,0),(-1,-1),5.8),('ALIGN',(0,0),(-1,-1),'CENTER'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F6F9')])]))
        story.append(t); story.append(Paragraph(f'Se muestran hasta 20 registros. El Excel conserva el detalle completo.',desc))
        # gráfico año
        fig,ax=plt.subplots(figsize=(5.4,2.2))
        ax.bar(tabla_graf['AÑO'].astype(str),tabla_graf['FEMENINOS'],label='Femenino',color='#FF6FB5')
        ax.bar(tabla_graf['AÑO'].astype(str),tabla_graf['MASCULINOS'],bottom=tabla_graf['FEMENINOS'],label='Masculino',color='#0EA5E9')
        ax.set_title('Casos por Año según Sexo'); ax.legend(fontsize=7,frameon=False); ax.spines[['top','right']].set_visible(False)
        plt.tight_layout(); b=BytesIO(); plt.savefig(b,format='png',dpi=170,bbox_inches='tight'); plt.close(); b.seek(0)
        story.append(Paragraph('3. GRÁFICO — CASOS POR AÑO SEGÚN SEXO',h2)); story.append(Image(b,width=430,height=175))
        # sexo
        fig,ax=plt.subplots(figsize=(4.2,1.8)); ax.pie([total_f,total_m],labels=['Femenino','Masculino'],colors=['#FF6FB5','#0EA5E9'],autopct='%1.1f%%'); ax.set_title('Distribución por Sexo'); plt.tight_layout()
        b2=BytesIO(); plt.savefig(b2,format='png',dpi=170,bbox_inches='tight'); plt.close(); b2.seek(0)
        story.append(Paragraph('4. GRÁFICO — DISTRIBUCIÓN POR SEXO',h2)); story.append(Image(b2,width=300,height=125))
        story.append(Paragraph(f'Distribución: <b>{porc_f:.1f}% mujeres ({total_f})</b> y <b>{porc_m:.1f}% varones ({total_m})</b>.',desc))
        # etario
        fig,ax=plt.subplots(figsize=(5.4,2.2)); ee=tabla2.sort_values('TOTAL'); ax.barh(ee['GRUPO_ETARIO'],ee['TOTAL'],color='#1c2e4a'); ax.set_title('Lesiones Tránsito por Grupo Etario'); ax.spines[['top','right']].set_visible(False); plt.tight_layout()
        b3=BytesIO(); plt.savefig(b3,format='png',dpi=170,bbox_inches='tight'); plt.close(); b3.seek(0)
        story.append(Paragraph('5. GRÁFICO Y TABLA — GRUPO ETARIO',h2)); story.append(Image(b3,width=430,height=175))
        de=[['Grupo Etario','F','M','Total','%']]
        for _,r in tabla2.iterrows(): de.append([r['GRUPO_ETARIO'],str(r['FEMENINOS']),str(r['MASCULINOS']),str(r['TOTAL']),f"{r['TOTAL']/total_general*100:.1f}%" if total_general else '0%'])
        te=Table(de,colWidths=[115,45,45,45,45],repeatRows=1); te.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.35,colors.grey),('FONTSIZE',(0,0),(-1,-1),7),('ALIGN',(0,0),(-1,-1),'CENTER')]))
        story.append(te)
        def footer(canvas,doc):
            canvas.saveState(); canvas.setFont('Helvetica',7); canvas.setFillColor(colors.HexColor('#6B7280')); canvas.drawString(34,24,'ANÁLISIS NOTIWEB 2026 — RED DE SALUD HUAMALIES UE 405'); canvas.drawRightString(A4[0]-34,24,f'Página {doc.page}'); canvas.restoreState()
        doc.build(story,onFirstPage=footer,onLaterPages=footer); return buffer.getvalue()

    col1,col2=st.columns(2)
    with col1:
        st.download_button("📊 DESCARGAR EXCEL",data=to_excel_pro(),file_name=f"LESIONES_TRANSITO_PRO_{ano_filtro}_{prov_filtro}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary",use_container_width=True)
    with col2:
        st.download_button("📄 DESCARGAR PDF",data=to_pdf_completo(),file_name=f"LESIONES_TRANSITO_INFORME_{ano_filtro}_{prov_filtro}.pdf",mime="application/pdf",use_container_width=True)
