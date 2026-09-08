import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from io import BytesIO
import xlsxwriter
from plotly.subplots import make_subplots
from datetime import datetime

# Para PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def mostrar_pagina():
    st.subheader("Módulo Diabetes - Análisis")
    try:
        modo = st.segmented_control("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], key="diab_modo", default="📁 Carpeta automática")
    except Exception:
        modo = st.pills("Selecciona modo:", ["📁 Carpeta automática", "📤 Subir archivos"], key="diab_modo", default="📁 Carpeta automática")

    lista_df = []
    archivos = []

    if modo and "Subir" in modo:
        archivos_subidos = st.file_uploader("📂 Arrastra aquí tus archivos Excel de DIABETES", type=['xlsx','xls','csv'], accept_multiple_files=True, key="diab_upload")
        if not archivos_subidos:
            st.info("👆 Sube tus archivos Excel de DIABETES")
            return
        archivos = [f.name for f in archivos_subidos]
        prog = st.progress(0)
        for idx, f in enumerate(archivos_subidos):
            prog.progress((idx+1)/len(archivos_subidos))
            try:
                if f.name.lower().endswith('.csv'):
                    df_temp = pd.read_csv(f, dtype=str, encoding='utf-8', low_memory=False)
                else:
                    try:
                        df_temp = pd.read_excel(f, engine='openpyxl', header=0)
                    except:
                        df_temp = pd.read_excel(f, header=0)
                if df_temp is not None and not df_temp.empty:
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                    df_temp = df_temp.dropna(how='all')
                    lista_df.append(df_temp)
            except:
                continue
        prog.empty()
    else:
        RUTA_BASE = os.path.dirname(__file__)
        carpeta_seleccionada = 'DIABETES'
        ruta_carpeta = os.path.join(RUTA_BASE, carpeta_seleccionada)
        if not os.path.exists(ruta_carpeta):
            ruta_carpeta = carpeta_seleccionada
        if not os.path.exists(ruta_carpeta):
            st.warning(f"La carpeta {carpeta_seleccionada} no existe. Usa modo Subir archivos")
            return
        archivos = [f for f in os.listdir(ruta_carpeta) if f.endswith(('.xlsx', '.xls', '.csv'))]
        if not archivos:
            st.warning(f"La carpeta {carpeta_seleccionada} está vacía")
            return
        prog = st.progress(0)
        for idx, archivo in enumerate(archivos):
            prog.progress((idx+1)/len(archivos))
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            try:
                try:
                    df_temp = pd.read_excel(ruta_archivo, engine='openpyxl', header=0)
                except:
                    df_temp = pd.read_excel(ruta_archivo, header=0)
                if df_temp is not None and not df_temp.empty:
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                    lista_df.append(df_temp)
            except:
                continue
        prog.empty()

    if not lista_df:
        st.error("No se pudo leer ningún archivo válido")
        return

    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)}")

    df = pd.concat(lista_df, ignore_index=True, sort=False)
    df.columns = df.columns.astype(str).str.lower().str.strip()

    df['RED'] = df.get('redes', 'SIN DATO')
    df['MICRORED'] = df.get('microredes', 'SIN DATO')
    df['ESTABLECIMIENTO'] = df.get('establecimiento', 'SIN DATO')
    df['CATEGORIA'] = df.get('categoria', 'SIN DATO')

    if 'ano' in df.columns:
        df['AÑO'] = pd.to_numeric(df['ano'], errors='coerce')
    else:
        df['AÑO'] = pd.to_datetime(df.get('fecha_reg'), errors='coerce').dt.year
    df['AÑO'] = df['AÑO'].fillna(0).astype(int).astype(str)
    df.loc[df['AÑO'] == '0', 'AÑO'] = 'S/D'

    sexo = df.get('sexo', pd.Series(['0']*len(df))).astype(str)
    df['MASCULINOS'] = (sexo == '1').astype(int)
    df['FEMENINOS'] = (sexo == '2').astype(int)

    df['EDAD'] = pd.to_numeric(df.get('edad'), errors='coerce').fillna(0)
    tcasos = df.get('tcasos', pd.Series([1]*len(df)))
    df['TOTAL_CASOS'] = pd.to_numeric(tcasos, errors='coerce').fillna(1).astype(int)

    tdiab = df['tdiabetes'] if 'tdiabetes' in df.columns else pd.Series([0]*len(df))
    tdiab = pd.to_numeric(tdiab, errors='coerce').fillna(0).astype(int)
    condiciones_diab = [tdiab == 1, tdiab == 2, tdiab == 0]
    valores_diab = ['DIABETES TIPO 1', 'DIABETES TIPO 2', 'NO ESPECIFICADO']
    df['TIPO_DIABETES'] = np.select(condiciones_diab, valores_diab, default='OTRO TIPO')

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
    col1, col2 = st.columns(2)
    with col1:
        anos_disponibles = ['TODOS'] + sorted([x for x in df['AÑO'].unique() if x!= 'S/D'])
        ano_filtro = st.selectbox("Filtrar por AÑO:", anos_disponibles, key='diab_ano')
    with col2:
        microredes_disponibles = ['TODAS'] + sorted(df['MICRORED'].unique().tolist())
        microred_filtro = st.selectbox("Filtrar por MICRORED:", microredes_disponibles, key='diab_micro')

    df_filtrado = df.copy()
    if ano_filtro!= 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['AÑO'] == ano_filtro]
    if microred_filtro!= 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['MICRORED'] == microred_filtro]

    st.subheader("TABLA 1 — Casos de DIABETES por Red, Microred, EESS y Sexo")
    tabla1 = df_filtrado.groupby(['RED', 'MICRORED', 'AÑO', 'ESTABLECIMIENTO', 'CATEGORIA', 'TIPO_DIABETES'])[['FEMENINOS', 'MASCULINOS']].sum().reset_index()
    tabla1['TOTAL'] = tabla1['FEMENINOS'] + tabla1['MASCULINOS']
    total_general = tabla1['TOTAL'].sum()

    if total_general == 0:
        st.warning("⚠️ No se registraron casos con los filtros seleccionados")
        return
    else:
        fila_total = pd.DataFrame([{
            'RED': 'TOTAL GENERAL', 'MICRORED': '', 'AÑO': '', 'ESTABLECIMIENTO': '',
            'CATEGORIA': '', 'TIPO_DIABETES': '',
            'FEMENINOS': tabla1['FEMENINOS'].sum(),
            'MASCULINOS': tabla1['MASCULINOS'].sum(),
            'TOTAL': total_general
        }])
        tabla1_final = pd.concat([tabla1, fila_total], ignore_index=True)
        def colorear_tabla(row):
            if row['RED'] == 'TOTAL GENERAL':
                return ['background-color: #FFD700; font-weight: bold; border: 2px solid black'] * len(row)
            else:
                return ['border: 1px solid #ddd'] * len(row)
        st.dataframe(tabla1_final.style.apply(colorear_tabla, axis=1), use_container_width=True, hide_index=True)

        tabla_graf = tabla1.groupby('AÑO')[['FEMENINOS', 'MASCULINOS']].sum().reset_index()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(name='FEMENINOS', x=tabla_graf['AÑO'], y=tabla_graf['FEMENINOS'], marker_color='#E91E8C', text=tabla_graf['FEMENINOS'], textposition='outside'))
        fig1.add_trace(go.Bar(name='MASCULINOS', x=tabla_graf['AÑO'], y=tabla_graf['MASCULINOS'], marker_color='#0891B2', text=tabla_graf['MASCULINOS'], textposition='outside'))
        fig1.update_layout(title=f'Registro de Casos de DIABETES por AÑO - {total_general} casos totales', barmode='group', plot_bgcolor='#F5F5F5', paper_bgcolor='white')
        st.plotly_chart(fig1, use_container_width=True)

        # SEXO PRO
        total_f = tabla1['FEMENINOS'].sum()
        total_m = tabla1['MASCULINOS'].sum()
        total_sexo = total_f + total_m
        porc_f = round((total_f / total_sexo * 100), 1) if total_sexo > 0 else 0
        porc_m = round((total_m / total_sexo * 100), 1) if total_sexo > 0 else 0

        st.subheader("Distribución por Sexo")
        st.markdown(f"""
        <div style="display:flex; justify-content:center; gap:80px; padding:20px 0;">
            <div style="text-align:center">
                <div style="position:relative; width:120px; height:120px; margin:0 auto">
                    <svg width="120" height="120" style="transform: rotate(-90deg)">
                        <circle cx="60" cy="60" r="50" fill="none" stroke="#E5E7EB" stroke-width="10"/>
                        <circle cx="60" cy="60" r="50" fill="none" stroke="#E91E8C" stroke-width="10" stroke-dasharray="{porc_f * 3.14} 314" stroke-linecap="round"/>
                    </svg>
                    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center">
                        <div style="font-size:45px; color:#E91E8C; line-height:1">♀</div>
                        <div style="font-size:18px; font-weight:800; color:#E91E8C;">{porc_f:.0f}%</div>
                    </div>
                </div>
            </div>
            <div style="text-align:center">
                <div style="position:relative; width:120px; height:120px; margin:0 auto">
                    <svg width="120" height="120" style="transform: rotate(-90deg)">
                        <circle cx="60" cy="60" r="50" fill="none" stroke="#E5E7EB" stroke-width="10"/>
                        <circle cx="60" cy="60" r="50" fill="none" stroke="#0891B2" stroke-width="10" stroke-dasharray="{porc_m * 3.14} 314" stroke-linecap="round"/>
                    </svg>
                    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center">
                        <div style="font-size:45px; color:#0891B2; line-height:1">♂</div>
                        <div style="font-size:18px; font-weight:800; color:#0891B2;">{porc_m:.0f}%</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("TABLA 2 — Casos por Grupo Etario")
        tabla3 = df_filtrado.groupby(['GRUPO_ETARIO'])[['FEMENINOS', 'MASCULINOS']].sum().reset_index()
        tabla3['TOTAL'] = tabla3['FEMENINOS'] + tabla3['MASCULINOS']
        tabla3 = tabla3.sort_values('TOTAL', ascending=False)
        st.dataframe(tabla3, use_container_width=True, hide_index=True)

        colores_etario = {'NIÑO (0-11)': '#8BC34A','ADOLESCENTE (12-17)': '#00BCD4','JOVEN (18-29)': '#FF9800','ADULTO (30-59)': '#FFEB3B','ADULTO MAYOR (60+)': '#E91E63','SIN DATO': '#9E9E9E'}
        fig3 = px.bar(tabla3, x='GRUPO_ETARIO', y='TOTAL', title='Casos de DIABETES por Grupo Etario', color='GRUPO_ETARIO', color_discrete_map=colores_etario, text='TOTAL')
        fig3.update_traces(textposition='outside')
        fig3.update_layout(plot_bgcolor='#F5F5F5', paper_bgcolor='white', showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

        # ============ DESCARGAS PRO ============
        st.divider()
        st.subheader("📥 Descargas Profesionales")

        # Diseño de las descargas: se mantiene exactamente la misma información,
        # pero se mejora la presentación visual de Excel y PDF.
    
        # ============================================================
        # DESCARGAS — MISMA INFORMACIÓN DEL SISTEMA, ORDENADA
        # ============================================================
        def to_excel_pro():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter',
                                engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                wb = writer.book
                navy, blue, light, gold = '#1c2e4a', '#4472C4', '#D9E1F2', '#FFD700'
                pink, cyan = '#E91E8C', '#0891B2'
                fmt_title = wb.add_format({'bold': True, 'font_size': 16, 'font_color': 'white',
                                           'bg_color': navy, 'align': 'left', 'valign': 'vcenter'})
                fmt_sub = wb.add_format({'bold': True, 'font_color': navy, 'bg_color': light,
                                         'align': 'left', 'valign': 'vcenter'})
                fmt_section = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': blue,
                                              'align': 'left', 'valign': 'vcenter'})
                fmt_header = wb.add_format({'bold': True, 'font_color': 'white', 'bg_color': navy,
                                            'border': 1, 'align': 'center', 'valign': 'vcenter',
                                            'text_wrap': True})
                fmt_cell = wb.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
                fmt_text = wb.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
                fmt_total = wb.add_format({'bold': True, 'bg_color': gold, 'border': 2,
                                           'align': 'center', 'valign': 'vcenter'})
                fmt_kpi = wb.add_format({'bold': True, 'font_size': 18, 'font_color': navy,
                                         'border': 1, 'align': 'center', 'valign': 'vcenter'})
                fmt_kpi_f = wb.add_format({'bold': True, 'font_size': 18, 'font_color': pink,
                                           'border': 1, 'align': 'center', 'valign': 'vcenter'})
                fmt_kpi_m = wb.add_format({'bold': True, 'font_size': 18, 'font_color': cyan,
                                           'border': 1, 'align': 'center', 'valign': 'vcenter'})
                fmt_note = wb.add_format({'italic': True, 'font_color': '#666666', 'font_size': 9})

                # 1. RESUMEN
                ws = wb.add_worksheet('RESUMEN')
                ws.hide_gridlines(2); ws.set_tab_color(blue)
                ws.merge_range('A1:H1', 'MÓDULO DIABETES — ANÁLISIS NOTIWEB', fmt_title)
                ws.merge_range('A2:H2',
                               f'Año: {ano_filtro} | Microred: {microred_filtro} | Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                               fmt_sub)
                ws.merge_range('A4:H4', 'INDICADORES DEL REPORTE', fmt_section)
                for rg, label, value, fmt in [
                    ('A5:B5','TOTAL DE CASOS',total_general,fmt_kpi),
                    ('C5:D5','FEMENINOS',total_f,fmt_kpi_f),
                    ('E5:F5','MASCULINOS',total_m,fmt_kpi_m),
                    ('G5:H5','AÑO',ano_filtro,fmt_kpi)]:
                    ws.merge_range(rg, label, fmt_sub)
                    r2 = rg.replace('5','6') + ':' + rg.split(':')[1].replace('5','7')
                    # Escribir valor en el centro de cada tarjeta sin congelar la hoja.
                    c0 = ord(rg[0])-65
                    c1 = ord(rg[3])-65
                    ws.merge_range(5, c0, 6, c1, value, fmt)
                ws.merge_range('A9:H9', 'GRÁFICO 1 — CASOS POR AÑO Y SEXO', fmt_section)

                tabla_graf.to_excel(writer, sheet_name='DATOS_AÑO', index=False, startrow=2)
                wd = writer.sheets['DATOS_AÑO']; wd.hide_gridlines(2); wd.set_tab_color('#A5A5A5')
                for c,v in enumerate(tabla_graf.columns): wd.write(2,c,v,fmt_header)
                for r in range(len(tabla_graf)):
                    for c in range(len(tabla_graf.columns)): wd.write(r+3,c,tabla_graf.iloc[r,c],fmt_cell)
                wd.set_column('A:A',12); wd.set_column('B:C',16)

                chart1 = wb.add_chart({'type':'column'})
                lr = len(tabla_graf)+2
                chart1.add_series({'name':'FEMENINOS','categories':f'=DATOS_AÑO!$A$4:$A${lr+1}',
                                   'values':f'=DATOS_AÑO!$B$4:$B${lr+1}',
                                   'fill':{'color':pink},'border':{'color':pink},
                                   'data_labels':{'value':True}})
                chart1.add_series({'name':'MASCULINOS','categories':f'=DATOS_AÑO!$A$4:$A${lr+1}',
                                   'values':f'=DATOS_AÑO!$C$4:$C${lr+1}',
                                   'fill':{'color':cyan},'border':{'color':cyan},
                                   'data_labels':{'value':True}})
                chart1.set_title({'name':f'Registro de Casos de DIABETES por AÑO - {total_general} casos totales'})
                chart1.set_y_axis({'name':'Casos','major_gridlines':{'visible':False}})
                chart1.set_legend({'position':'bottom'})
                chart1.set_style(10); chart1.set_size({'width':700,'height':360})
                ws.insert_chart('A10', chart1, {'object_position':1})

                # 2. TABLA DETALLE
                d = tabla1_final.copy()
                d.to_excel(writer, sheet_name='TABLA_1_DETALLE', index=False, startrow=2)
                wd1 = writer.sheets['TABLA_1_DETALLE']; wd1.hide_gridlines(2); wd1.set_tab_color(navy)
                wd1.merge_range(0,0,0,len(d.columns)-1,
                                'TABLA 1 — CASOS DE DIABETES POR RED, MICRORED, EESS Y SEXO', fmt_title)
                wd1.merge_range(1,0,1,len(d.columns)-1,
                                f'Filtro: Año = {ano_filtro} | Microred = {microred_filtro}', fmt_sub)
                for c,v in enumerate(d.columns): wd1.write(2,c,v,fmt_header)
                for r in range(len(d)):
                    for c in range(len(d.columns)):
                        val=d.iloc[r,c]
                        wd1.write(r+3,c,val,fmt_total if str(d.iloc[r]['RED'])=='TOTAL GENERAL'
                                  else (fmt_text if isinstance(val,str) else fmt_cell))
                wd1.set_column('A:B',20); wd1.set_column('C:C',10); wd1.set_column('D:D',28)
                wd1.set_column('E:F',18); wd1.set_column('G:I',12)
                wd1.autofilter(2,0,len(d)+2,len(d.columns)-1)

                # 3. GRUPO ETARIO
                e = tabla3.copy()
                e.to_excel(writer, sheet_name='GRUPO_ETARIO', index=False, startrow=2)
                we = writer.sheets['GRUPO_ETARIO']; we.hide_gridlines(2); we.set_tab_color('#70AD47')
                we.merge_range(0,0,0,len(e.columns)-1,'TABLA 2 — CASOS POR GRUPO ETARIO',fmt_title)
                for c,v in enumerate(e.columns): we.write(2,c,v,fmt_header)
                for r in range(len(e)):
                    for c in range(len(e.columns)): we.write(r+3,c,e.iloc[r,c],fmt_cell)
                we.set_column('A:A',28); we.set_column('B:D',14)
                chart3 = wb.add_chart({'type':'column'})
                chart3.add_series({'name':'TOTAL','categories':f'=GRUPO_ETARIO!$A$4:$A${len(e)+3}',
                                   'values':f'=GRUPO_ETARIO!$D$4:$D${len(e)+3}',
                                   'fill':{'color':'#FF9800'},'border':{'color':'#FF9800'},
                                   'data_labels':{'value':True}})
                chart3.set_title({'name':'Casos de DIABETES por Grupo Etario'})
                chart3.set_legend({'none':True}); chart3.set_style(10)
                chart3.set_size({'width':650,'height':350})
                we.insert_chart('F3',chart3,{'object_position':1})

                # 4. SEXO
                wsx=wb.add_worksheet('DISTRIBUCION_SEXO'); wsx.hide_gridlines(2); wsx.set_tab_color(pink)
                wsx.merge_range('A1:F1','DISTRIBUCIÓN POR SEXO',fmt_title)
                wsx.write('A3','SEXO',fmt_header); wsx.write('B3','CASOS',fmt_header); wsx.write('C3','%',fmt_header)
                wsx.write('A4','FEMENINO',fmt_cell); wsx.write('B4',total_f,fmt_cell); wsx.write('C4',porc_f/100,fmt_cell)
                wsx.write('A5','MASCULINO',fmt_cell); wsx.write('B5',total_m,fmt_cell); wsx.write('C5',porc_m/100,fmt_cell)
                wsx.set_column('A:C',16)
                chs=wb.add_chart({'type':'doughnut'})
                chs.add_series({'name':'Sexo','categories':'=DISTRIBUCION_SEXO!$A$4:$A$5',
                                'values':'=DISTRIBUCION_SEXO!$B$4:$B$5',
                                'points':[{'fill':{'color':pink}},{'fill':{'color':cyan}}],
                                'data_labels':{'percentage':True,'category':True}})
                chs.set_title({'name':'Distribución por Sexo'}); chs.set_legend({'position':'bottom'})
                chs.set_style(10); chs.set_size({'width':520,'height':330})
                wsx.insert_chart('E3',chs,{'object_position':1})

            return output.getvalue()

        def to_pdf_pro():
            buffer=BytesIO()
            doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=34,leftMargin=34,topMargin=42,bottomMargin=42)
            styles=getSampleStyleSheet()
            title=ParagraphStyle('dt',parent=styles['Heading1'],fontSize=15,textColor=colors.HexColor('#1c2e4a'),alignment=1,spaceAfter=4)
            h2=ParagraphStyle('dh',parent=styles['Heading2'],fontSize=10,textColor=colors.HexColor('#1c2e4a'),spaceBefore=8,spaceAfter=5)
            desc=ParagraphStyle('dd',parent=styles['Normal'],fontSize=8.2,leading=11,textColor=colors.HexColor('#334155'),backColor=colors.HexColor('#F8FAFC'),borderPadding=6,spaceAfter=6)
            story=[Paragraph('<b>MÓDULO DIABETES — ANÁLISIS NOTIWEB</b>',title),
                   Paragraph(f'Año: {ano_filtro} | Microred: {microred_filtro} | Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',desc)]
            story.append(Paragraph('1. RESUMEN EJECUTIVO',h2))
            story.append(Paragraph(f'Se registraron <b>{total_general} casos</b>. Femenino: <b>{total_f} ({porc_f:.1f}%)</b>. Masculino: <b>{total_m} ({porc_m:.1f}%)</b>.',desc))
            # Tabla 1
            story.append(Paragraph('2. TABLA 1 — DETALLE',h2))
            dp=tabla1.sort_values('TOTAL',ascending=False).head(20)
            data=[['RED','MICRORED','AÑO','EESS','CATEG.','TIPO','F','M','TOTAL']]
            for _,r in dp.iterrows():
                data.append([str(r['RED'])[:12],str(r['MICRORED'])[:12],str(r['AÑO']),
                             str(r['ESTABLECIMIENTO'])[:16],str(r['CATEGORIA'])[:10],
                             str(r['TIPO_DIABETES'])[:10],str(r['FEMENINOS']),str(r['MASCULINOS']),str(r['TOTAL'])])
            t=Table(data,colWidths=[42,48,25,70,42,42,20,20,28],repeatRows=1)
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),
                                   ('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#D0D7DE')),
                                   ('FONTSIZE',(0,0),(-1,-1),6.2),('ALIGN',(0,0),(-1,-1),'CENTER'),
                                   ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F6F9')])]))
            story.append(t); story.append(Paragraph(f'Total general: <b>{total_general}</b> casos. Se muestran los primeros 20 registros; el Excel contiene el detalle completo.',desc))
            # Gráfico año
            fig,ax=plt.subplots(figsize=(5.4,2.2))
            ax.bar(tabla_graf['AÑO'].astype(str),tabla_graf['FEMENINOS'],label='Femeninos',color='#E91E8C')
            ax.bar(tabla_graf['AÑO'].astype(str),tabla_graf['MASCULINOS'],bottom=tabla_graf['FEMENINOS'],label='Masculinos',color='#0891B2')
            ax.set_title('Registro de Casos de DIABETES por AÑO'); ax.legend(fontsize=7,frameon=False); ax.spines[['top','right']].set_visible(False)
            plt.tight_layout(); b=BytesIO(); plt.savefig(b,format='png',dpi=170,bbox_inches='tight'); plt.close(); b.seek(0)
            story.append(Paragraph('3. GRÁFICO — CASOS POR AÑO Y SEXO',h2)); story.append(Image(b,width=430,height=175))
            # Sexo
            fig,ax=plt.subplots(figsize=(4.5,1.8))
            ax.pie([total_f,total_m],labels=['FEMENINO','MASCULINO'],colors=['#E91E8C','#0891B2'],autopct='%1.1f%%',startangle=90)
            ax.set_title('Distribución por Sexo'); plt.tight_layout(); b2=BytesIO(); plt.savefig(b2,format='png',dpi=170,bbox_inches='tight'); plt.close(); b2.seek(0)
            story.append(Paragraph('4. GRÁFICO — DISTRIBUCIÓN POR SEXO',h2)); story.append(Image(b2,width=300,height=125))
            story.append(Paragraph(f'La distribución corresponde a <b>{porc_f:.1f}% femenino</b> y <b>{porc_m:.1f}% masculino</b>.',desc))
            # Etario
            fig,ax=plt.subplots(figsize=(5.4,2.2))
            ee=tabla3.sort_values('TOTAL')
            ax.barh(ee['GRUPO_ETARIO'],ee['TOTAL'],color=['#8BC34A','#00BCD4','#FF9800','#FFEB3B','#E91E63'][:len(ee)])
            ax.set_title('Casos de DIABETES por Grupo Etario'); ax.spines[['top','right']].set_visible(False)
            plt.tight_layout(); b3=BytesIO(); plt.savefig(b3,format='png',dpi=170,bbox_inches='tight'); plt.close(); b3.seek(0)
            story.append(Paragraph('5. GRÁFICO Y TABLA — GRUPO ETARIO',h2)); story.append(Image(b3,width=430,height=175))
            de=[['GRUPO ETARIO','F','M','TOTAL']]
            for _,r in tabla3.iterrows(): de.append([r['GRUPO_ETARIO'],str(r['FEMENINOS']),str(r['MASCULINOS']),str(r['TOTAL'])])
            te=Table(de,colWidths=[125,55,55,55],repeatRows=1)
            te.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.35,colors.grey),('FONTSIZE',(0,0),(-1,-1),7),('ALIGN',(0,0),(-1,-1),'CENTER')]))
            story.append(te)
            def footer(canvas,doc):
                canvas.saveState(); canvas.setFont('Helvetica',7); canvas.setFillColor(colors.HexColor('#6B7280'))
                canvas.drawString(34,24,'ANÁLISIS NOTIWEB 2026 — RED DE SALUD HUAMALIES UE 405')
                canvas.drawRightString(A4[0]-34,24,f'Página {doc.page}'); canvas.restoreState()
            doc.build(story,onFirstPage=footer,onLaterPages=footer)
            return buffer.getvalue()

        col_a,col_b=st.columns(2)
        with col_a:
            st.download_button("📊 DESCARGAR EXCEL",data=to_excel_pro(),
                               file_name=f"DIABETES_PRO_{ano_filtro}_{microred_filtro}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary",use_container_width=True)
        with col_b:
            st.download_button("📄 DESCARGAR PDF",data=to_pdf_pro(),
                               file_name=f"DIABETES_INFORME_{ano_filtro}_{microred_filtro}_{datetime.now().strftime('%Y%m%d')}.pdf",
                               mime="application/pdf",use_container_width=True)
        st.caption("La descarga conserva la información del sistema y la presenta en Excel/PDF con tablas, gráficos, colores y descripción.")
