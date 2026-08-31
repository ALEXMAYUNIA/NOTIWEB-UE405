
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
    st.markdown("**Modo Licenciada: Subir archivos | Modo Técnico: Carpeta automática**")
    modo = st.radio("Selecciona modo:", ["📁 Carpeta automática (DIABETES)", "📤 Subir archivos (para Licenciada - Excel diferente)"], horizontal=True, key="diab_modo")

    lista_df = []
    archivos = []

    if modo == "📤 Subir archivos (para Licenciada - Excel diferente)":
        archivos_subidos = st.file_uploader("📂 Arrastra aquí tus archivos Excel de DIABETES (cada módulo tiene excel diferente)", type=['xlsx','xls','csv'], accept_multiple_files=True, key="diab_upload")
        if not archivos_subidos:
            st.info("👆 Sube tus archivos Excel de DIABETES - Cada módulo es diferente: diabetes tiene columnas tdiabetes, redes, microredes, etc.")
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
        st.info(f"📁 Analizando: {ruta_carpeta} - Excel DIABETES tiene columnas: tdiabetes, redes, microredes, establecimiento, sexo, edad")
        if not os.path.exists(ruta_carpeta):
            st.warning(f"La carpeta {ruta_carpeta} no existe. Usa modo Subir archivos")
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

    st.success(f"✅ Archivos leídos: {len(lista_df)} de {len(archivos)} - Cada módulo tiene excel diferente, este es DIABETES con {len(lista_df)} archivos")

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

        # --- FUNCION EXCEL PRO ---
        def to_excel_pro():
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Formatos
                header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1c2e4a', 'font_color': 'white', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 11})
                total_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFD700', 'border': 2, 'align': 'center', 'font_size': 12})
                cell_fmt = workbook.add_format({'border': 1, 'align': 'center'})
                title_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'bg_color': '#E3F2FD', 'align': 'left'})
                percent_fmt = workbook.add_format({'border': 1, 'num_format': '0.0%', 'align': 'center'})
                
                # HOJA 1: RESUMEN
                ws_resumen = workbook.add_worksheet('RESUMEN')
                ws_resumen.write(0, 0, f"REPORTE DIABETES - {ano_filtro} - {microred_filtro} - {datetime.now().strftime('%d/%m/%Y')}", title_fmt)
                ws_resumen.write(2, 0, "INDICADOR", header_fmt)
                ws_resumen.write(2, 1, "VALOR", header_fmt)
                ws_resumen.write(3, 0, "Total Casos", cell_fmt)
                ws_resumen.write(3, 1, total_general, cell_fmt)
                ws_resumen.write(4, 0, "Total Femeninos", cell_fmt)
                ws_resumen.write(4, 1, total_f, cell_fmt)
                ws_resumen.write(5, 0, "Total Masculinos", cell_fmt)
                ws_resumen.write(5, 1, total_m, cell_fmt)
                ws_resumen.write(6, 0, "% Femenino", cell_fmt)
                ws_resumen.write(6, 1, porc_f/100, percent_fmt)
                ws_resumen.write(7, 0, "% Masculino", cell_fmt)
                ws_resumen.write(7, 1, porc_m/100, percent_fmt)
                ws_resumen.set_column('A:B', 25)

                # HOJA 2: TABLA 1
                tabla1_final.to_excel(writer, sheet_name='TABLA_1_DETALLE', index=False, startrow=1)
                ws1 = writer.sheets['TABLA_1_DETALLE']
                for col_num, value in enumerate(tabla1_final.columns.values):
                    ws1.write(1, col_num, value, header_fmt)
                for row_num in range(len(tabla1_final)):
                    for col_num in range(len(tabla1_final.columns)):
                        fmt = total_fmt if tabla1_final.iloc[row_num]['RED'] == 'TOTAL GENERAL' else cell_fmt
                        ws1.write(row_num + 2, col_num, tabla1_final.iloc[row_num, col_num], fmt)
                ws1.set_column('A:I', 18)
                ws1.write(0, 0, f"TABLA 1: Casos por EESS - Filtro: {ano_filtro} / {microred_filtro}", title_fmt)

                # Grafico 1 embebido en Excel
                chart1 = workbook.add_chart({'type': 'column'})
                last_row = len(tabla_graf) + 1
                chart1.add_series({'name': 'Femeninos', 'categories': f"=TABLA_1_DETALLE!$C$3:$C${last_row+1}", 'values': f"=GRAFICOS_DATOS!$B$2:$B${last_row+1}", 'fill': {'color': '#E91E8C'}})
                chart1.add_series({'name': 'Masculinos', 'categories': f"=TABLA_1_DETALLE!$C$3:$C${last_row+1}", 'values': f"=GRAFICOS_DATOS!$C$2:$C${last_row+1}", 'fill': {'color': '#0891B2'}})
                chart1.set_title({'name': 'Casos por Año - Sexo'})
                chart1.set_x_axis({'name': 'Año'})
                chart1.set_y_axis({'name': 'Casos'})
                chart1.set_style(10)
                ws1.insert_chart('K2', chart1, {'x_scale': 1.5, 'y_scale': 1.2})

                # HOJA 3: DATOS PARA GRAFICOS
                tabla_graf.to_excel(writer, sheet_name='GRAFICOS_DATOS', index=False)
                ws_graf = writer.sheets['GRAFICOS_DATOS']
                ws_graf.set_column('A:C', 15)

                # HOJA 4: GRUPO ETARIO + SEXO
                tabla3.to_excel(writer, sheet_name='GRUPO_ETARIO', index=False, startrow=0)
                ws_et = writer.sheets['GRUPO_ETARIO']
                ws_et.set_column('A:D', 18)
                # Grafico etario
                chart_et = workbook.add_chart({'type': 'column'})
                chart_et.add_series({'name': 'Grupo Etario', 'categories': f"=GRUPO_ETARIO!$A$2:$A${len(tabla3)+1}", 'values': f"=GRUPO_ETARIO!$D$2:$D${len(tabla3)+1}", 'fill': {'color': '#FF9800'}, 'data_labels': {'value': True}})
                chart_et.set_title({'name': 'Casos por Grupo Etario'})
                ws_et.insert_chart('F2', chart_et, {'x_scale': 1.5, 'y_scale': 1.2})

                # HOJA 5: DISTRIBUCION SEXO
                ws_sexo = workbook.add_worksheet('DISTRIBUCION_SEXO')
                ws_sexo.write(0, 0, "SEXO", header_fmt)
                ws_sexo.write(0, 1, "CASOS", header_fmt)
                ws_sexo.write(0, 2, "%", header_fmt)
                ws_sexo.write(1, 0, "FEMENINO", cell_fmt)
                ws_sexo.write(1, 1, total_f, cell_fmt)
                ws_sexo.write(1, 2, porc_f/100, percent_fmt)
                ws_sexo.write(2, 0, "MASCULINO", cell_fmt)
                ws_sexo.write(2, 1, total_m, cell_fmt)
                ws_sexo.write(2, 2, porc_m/100, percent_fmt)
                ws_sexo.set_column('A:C', 15)
                chart_sexo = workbook.add_chart({'type': 'doughnut'})
                chart_sexo.add_series({'name': 'Sexo', 'categories': '=DISTRIBUCION_SEXO!$A$2:$A$3', 'values': '=DISTRIBUCION_SEXO!$B$2:$B$3', 'points': [{'fill': {'color': '#E91E8C'}}, {'fill': {'color': '#0891B2'}}]})
                chart_sexo.set_title({'name': 'Distribución por Sexo'})
                ws_sexo.insert_chart('E2', chart_sexo)

            return output.getvalue()

        def to_pdf_pro():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
            styles = getSampleStyleSheet()
            style_title = ParagraphStyle('TitleCustom', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1c2e4a'), spaceAfter=12, alignment=1)
            style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1c2e4a'), spaceAfter=8)
            style_normal = ParagraphStyle('NormalCustom', parent=styles['Normal'], fontSize=9, leading=12)

            story = []

            # Logo y titulo
            story.append(Paragraph(f"<b>ANALISIS NOTIWEB 2026 - RED DE SALUD HUAMALIES UE 405</b><br/>REPORTE DE VIGILANCIA DE DIABETES<br/>Filtro: {ano_filtro} | {microred_filtro} | Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", style_title))
            story.append(Spacer(1, 4))

            # Resumen
            story.append(Paragraph("<b>1. RESUMEN EJECUTIVO</b>", style_h2))
            desc_resumen = f"""Se registraron <b>{total_general} casos totales de diabetes</b> en el periodo filtrado.
            De ellos, <b>{total_f} ({porc_f:.1f}%) corresponden a sexo femenino</b> y <b>{total_m} ({porc_m:.1f}%) a sexo masculino</b>.
            La microred con mayor carga se detalla en la tabla 1. La mayor concentración se observa en el grupo etario adulto y adulto mayor,
            consistente con la historia natural de la enfermedad."""
            story.append(Paragraph(desc_resumen, style_normal))
            story.append(Spacer(1, 4))

            # Tabla 1 - resumen top 10
            story.append(Paragraph("<b>2. TABLA 1: Casos por Establecimiento</b>", style_h2))
            tabla_pdf = tabla1.sort_values('TOTAL', ascending=False).head(15)
            data_tabla = [['RED','MICRORED','AÑO','EESS','TIPO','F','M','TOTAL']]
            for _, r in tabla_pdf.iterrows():
                data_tabla.append([str(r['RED'])[:12], str(r['MICRORED'])[:12], str(r['AÑO']), str(r['ESTABLECIMIENTO'])[:18], str(r['TIPO_DIABETES'])[:10], str(r['FEMENINOS']), str(r['MASCULINOS']), str(r['TOTAL'])])
            t = Table(data_tabla, colWidths=[55,55,25,90,45,20,20,30])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1c2e4a')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f1f5f9')),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"Total General: {total_general} casos. Tabla completa en Excel.", style_normal))
            story.append(Spacer(1, 3))

            # Graficos con matplotlib
            # Grafico 1 - Barras por año
            fig, ax = plt.subplots(figsize=(5,2.2))
            ax.bar(tabla_graf['AÑO'].astype(str), tabla_graf['FEMENINOS'], label='Femenino', color='#E91E8C')
            ax.bar(tabla_graf['AÑO'].astype(str), tabla_graf['MASCULINOS'], bottom=tabla_graf['FEMENINOS'], label='Masculino', color='#0891B2')
            ax.set_title('Casos por Año - Sexo')
            ax.legend(fontsize=8)
            plt.xticks(rotation=45, fontsize=8)
            plt.tight_layout()
            img_buf1 = BytesIO()
            plt.savefig(img_buf1, format='png', dpi=150)
            plt.close()
            img_buf1.seek(0)
            story.append(Paragraph("<b>3. GRAFICO 1: Casos por Año según Sexo</b>", style_h2))
            story.append(Image(img_buf1, width=420, height=160))
            story.append(Paragraph(f"Interpretación: La tendencia muestra variación anual. El año con mayor registro fue {tabla_graf.loc[tabla_graf['FEMENINOS'].add(tabla_graf['MASCULINOS']).idxmax(),'AÑO']} con {tabla_graf['FEMENINOS'].add(tabla_graf['MASCULINOS']).max()} casos.", style_normal))
            story.append(Spacer(1, 3))

            # Grafico 2 - Sexo
            fig, axes = plt.subplots(1,2, figsize=(5,1.8))
            axes[0].pie([porc_f, 100-porc_f], colors=['#E91E8C','#E5E7EB'], wedgeprops={'width':0.4})
            axes[0].text(0,0,f"♀ {porc_f:.0f}%", ha='center', va='center', fontsize=12, color='#E91E8C', weight='bold')
            axes[1].pie([porc_m, 100-porc_m], colors=['#0891B2','#E5E7EB'], wedgeprops={'width':0.4})
            axes[1].text(0,0,f"♂ {porc_m:.0f}%", ha='center', va='center', fontsize=12, color='#0891B2', weight='bold')
            plt.tight_layout()
            img_buf2 = BytesIO()
            plt.savefig(img_buf2, format='png', dpi=150)
            plt.close()
            img_buf2.seek(0)
            story.append(Paragraph("<b>4. GRAFICO 2: Distribución por Sexo</b>", style_h2))
            story.append(Image(img_buf2, width=320, height=110))
            story.append(Paragraph(f"El {porc_f:.1f}% de casos son mujeres, indicando mayor captación o prevalencia en este sexo. Requiere enfoque de género en prevención.", style_normal))
            story.append(Spacer(1, 3))

            # Grafico 3 - Grupo etario
            fig, ax = plt.subplots(figsize=(5,2.2))
            colors_et = {'NIÑO (0-11)': '#8BC34A','ADOLESCENTE (12-17)': '#00BCD4','JOVEN (18-29)': '#FF9800','ADULTO (30-59)': '#FFEB3B','ADULTO MAYOR (60+)': '#E91E63'}
            tabla3_sorted = tabla3.sort_values('TOTAL')
            ax.barh(tabla3_sorted['GRUPO_ETARIO'], tabla3_sorted['TOTAL'], color=[colors_et.get(x,'#9E9E9E') for x in tabla3_sorted['GRUPO_ETARIO']])
            ax.set_title('Casos por Grupo Etario')
            plt.tight_layout()
            img_buf3 = BytesIO()
            plt.savefig(img_buf3, format='png', dpi=150)
            plt.close()
            img_buf3.seek(0)
            story.append(Paragraph("<b>5. GRAFICO 3: Distribución por Grupo Etario</b>", style_h2))
            story.append(Image(img_buf3, width=420, height=160))
            tabla_et_desc = tabla3.to_string(index=False)
            story.append(Paragraph(f"El grupo más afectado es {tabla3.iloc[0]['GRUPO_ETARIO']} con {tabla3.iloc[0]['TOTAL']} casos ({tabla3.iloc[0]['TOTAL']/total_general*100:.1f}% del total). La diabetes se concentra en adultos y adultos mayores.", style_normal))
            story.append(Spacer(1, 4))

            # Tabla etario
            data_et = [['Grupo Etario','Femenino','Masculino','Total','%']]
            for _, r in tabla3.iterrows():
                data_et.append([r['GRUPO_ETARIO'], str(r['FEMENINOS']), str(r['MASCULINOS']), str(r['TOTAL']), f"{r['TOTAL']/total_general*100:.1f}%"])
            t2 = Table(data_et, colWidths=[110,60,60,50,40])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1c2e4a')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('FONTSIZE', (0,0), (-1,-1), 8),
            ]))
            story.append(t2)
            story.append(Spacer(1, 6))
            story.append(Paragraph("<b>Conclusiones y Recomendaciones:</b><br/>1. Fortalecer tamizaje en adultos 30-59 años.<br/>2. Estrategia diferenciada por sexo.<br/>3. Seguimiento en EESS con mayor carga.<br/>4. Capacitación continua al personal.", style_normal))

            doc.build(story)
            return buffer.getvalue()

        col_a, col_b = st.columns(2)
        with col_a:
            excel_pro = to_excel_pro()
            st.download_button("📊 DESCARGAR EXCEL ", data=excel_pro, file_name=f"DIABETES_PRO_{ano_filtro}_{microred_filtro}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
        with col_b:
            pdf_pro = to_pdf_pro()
            st.download_button("📄 DESCARGAR PDF", data=pdf_pro, file_name=f"DIABETES_INFORME_{ano_filtro}_{microred_filtro}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)

        st.caption("Excel incluye: Resumen, Tabla detalle, Gráficos con charts embebidos, Grupo Etario y Distribución Sexo. PDF incluye interpretación automática.")
