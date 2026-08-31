import streamlit as st, pandas as pd, os, numpy as np, plotly.graph_objects as go, plotly.express as px
from io import BytesIO
from datetime import datetime
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def detectar_columna(df, posibles):
    # Busqueda mas amplia y con contains
    cols_lower = {c.lower(): c for c in df.columns}
    for p in posibles:
        p = p.lower()
        for col_lower, col_orig in cols_lower.items():
            if p in col_lower:
                return col_orig
    return None

def mostrar_aplicativo(nombre_app):
    st.markdown("""
    <style>
    .stApp, .block-container {background:#ffffff !important; color:#0f172a !important;}
    h1,h2,h3, p, label {color:#0f172a !important;}
    div[data-baseweb="select"] > div {background:#ffffff !important; color:#000000 !important; border:1px solid #cbd5e1 !important;}
    </style>
    """, unsafe_allow_html=True)

    RUTA_BASE = os.path.dirname(__file__)
    ruta_carpeta = os.path.join(RUTA_BASE, "APLICACIONES", nombre_app)

    if not os.path.exists(ruta_carpeta):
        st.warning(f"La carpeta APLICACIONES/{nombre_app} no existe. Créala y mete tus excels.")
        return

    archivos = [f for f in os.listdir(ruta_carpeta) if f.endswith(('.xlsx','.xls','.csv'))]
    if not archivos:
        st.warning(f"APLICACIONES/{nombre_app} vacía.")
        return

    lista_df=[]
    for archivo in archivos:
        ruta=os.path.join(ruta_carpeta, archivo)
        try: df_temp=pd.read_excel(ruta, engine='openpyxl', header=0)
        except:
            try: df_temp=pd.read_excel(ruta, engine='xlrd', header=0)
            except:
                try: df_temp=pd.read_csv(ruta)
                except: continue
        if df_temp is not None and not df_temp.empty:
            # Limpiar columnas sin nombre
            df_temp = df_temp.loc[:, df_temp.columns.notna()]
            df_temp.columns = df_temp.columns.astype(str)
            # Eliminar columnas Unnamed vacias si tienen todo NaN
            df_temp = df_temp.dropna(axis=1, how='all')
            df_temp=df_temp.loc[:, ~df_temp.columns.duplicated()]
            lista_df.append(df_temp)

    if not lista_df: st.error("No se pudo leer"); return
    df=pd.concat(lista_df, ignore_index=True, sort=False)
    st.success(f"Archivos: {len(lista_df)} | Registros: {len(df)}")

    # Mostrar preview para debug
    with st.expander(f"📋 Ver primeras filas de {nombre_app} - para ver nombres reales de columnas", expanded=False):
        st.dataframe(df.head(5), use_container_width=True)
        st.write("Columnas exactas:", df.columns.tolist())

    # DETECCION MEJORADA - MAS POSIBILIDADES
    # Para RED: en defunciones neumonia viene como 'DIRESA' o 'RED' o 'Diresa'
    col_red = detectar_columna(df, ['redes','_red','diresa','disas','disa','departamento','region'])
    col_micro = detectar_columna(df, ['microred','micro_red','microrred','mr'])
    col_eess = detectar_columna(df, ['establecimiento','establec','eess','ipre','estable','nombre_estab','establecimiento_notifica'])
    col_ano = detectar_columna(df, ['ano','año','anio','year','ano_notif','año_notif'])
    col_sexo = detectar_columna(df, ['sexo','sex','genero','género'])
    col_edad = detectar_columna(df, ['edad','age'])
    col_fecha = detectar_columna(df, ['fecha_def','fecha_notif','fecha','f_notif','fec_'])

    # Si no detecta, permitir mapeo manual
    st.divider()
    st.subheader("🔧 Mapeo de Columnas (si sale SIN DATO, corrigelo aquí)")
    c1,c2,c3,c4 = st.columns(4)
    opciones = ["--AUTO--"] + df.columns.tolist()
    def get_idx(auto_col):
        if auto_col and auto_col in df.columns.tolist():
            return opciones.index(auto_col)
        return 0
    with c1:
        sel_red = st.selectbox(f"RED ({col_red})", opciones, index=get_idx(col_red), key=f"{nombre_app}_map_red")
        sel_micro = st.selectbox(f"MICRORED ({col_micro})", opciones, index=get_idx(col_micro), key=f"{nombre_app}_map_micro")
    with c2:
        sel_eess = st.selectbox(f"EESS ({col_eess})", opciones, index=get_idx(col_eess), key=f"{nombre_app}_map_eess")
        sel_ano = st.selectbox(f"AÑO ({col_ano})", opciones, index=get_idx(col_ano), key=f"{nombre_app}_map_ano")
    with c3:
        sel_sexo = st.selectbox(f"SEXO ({col_sexo})", opciones, index=get_idx(col_sexo), key=f"{nombre_app}_map_sexo")
        sel_edad = st.selectbox(f"EDAD ({col_edad})", opciones, index=get_idx(col_edad), key=f"{nombre_app}_map_edad")

    # Usar seleccion manual si el usuario eligio
    if sel_red != "--AUTO--": col_red = sel_red
    if sel_micro != "--AUTO--": col_micro = sel_micro
    if sel_eess != "--AUTO--": col_eess = sel_eess
    if sel_ano != "--AUTO--": col_ano = sel_ano
    if sel_sexo != "--AUTO--": col_sexo = sel_sexo
    if sel_edad != "--AUTO--": col_edad = sel_edad

    # Normalizar
    df['RED_N'] = df[col_red].astype(str) if col_red and col_red in df.columns else 'SIN DATO'
    df['MICRORED_N'] = df[col_micro].astype(str) if col_micro and col_micro in df.columns else 'SIN DATO'
    df['EESS_N'] = df[col_eess].astype(str) if col_eess and col_eess in df.columns else 'SIN DATO'

    if col_ano and col_ano in df.columns:
        try:
            df['AÑO_N'] = pd.to_numeric(df[col_ano], errors='coerce')
            # Si es fecha completa extrae año
            if df['AÑO_N'].isna().all():
                df['AÑO_N'] = pd.to_datetime(df[col_ano], errors='coerce').dt.year
            df['AÑO_N'] = df['AÑO_N'].fillna(0).astype(int).astype(str)
            df.loc[df['AÑO_N']=='0','AÑO_N']='S/D'
        except:
            df['AÑO_N']='S/D'
    elif col_fecha and col_fecha in df.columns:
        df['AÑO_N'] = pd.to_datetime(df[col_fecha], errors='coerce').dt.year.fillna(0).astype(int).astype(str)
    else:
        df['AÑO_N']='S/D'

    if col_sexo and col_sexo in df.columns:
        sexo = df[col_sexo].astype(str).str.upper().str.strip()
        df['FEM'] = sexo.isin(['2','F','FEMENINO','MUJER','FEMENINO ','MUJER']).astype(int)
        df['MASC'] = sexo.isin(['1','M','MASCULINO','VARON','HOMBRE','MASCULINO ']).astype(int)
        # Si no detecta, intenta numerico
        if df['FEM'].sum()==0 and df['MASC'].sum()==0:
            try:
                vals = pd.to_numeric(df[col_sexo], errors='coerce')
                df['FEM'] = (vals==2).astype(int)
                df['MASC'] = (vals==1).astype(int)
            except:
                df['FEM']=0; df['MASC']=1
        # Si aun nada, cuenta 1 por fila como FEM para que no salga 0
        if df['FEM'].sum()+df['MASC'].sum()==0:
            df['FEM']=1; df['MASC']=0
    else:
        df['FEM']=1; df['MASC']=0

    if col_edad and col_edad in df.columns:
        df['EDAD_N'] = pd.to_numeric(df[col_edad], errors='coerce').fillna(0)
    else:
        df['EDAD_N']=0

    cond=[(df['EDAD_N']>=0)&(df['EDAD_N']<=11),(df['EDAD_N']>=12)&(df['EDAD_N']<=17),(df['EDAD_N']>=18)&(df['EDAD_N']<=29),(df['EDAD_N']>=30)&(df['EDAD_N']<=59),(df['EDAD_N']>=60)]
    cat=['NIÑO (0-11)','ADOLESCENTE (12-17)','JOVEN (18-29)','ADULTO (30-59)','ADULTO MAYOR (60+)']
    df['GRUPO_ETARIO'] = np.select(cond, cat, default='SIN DATO')

    # FILTROS
    st.subheader("2. Filtros:")
    c1,c2=st.columns(2)
    with c1:
        anos = ['TODOS'] + sorted([x for x in df['AÑO_N'].unique() if x!='S/D'])
        ano_filtro=st.selectbox("AÑO:", anos, key=f'{nombre_app}_ano_f')
    with c2:
        micros = ['TODAS'] + sorted([x for x in df['MICRORED_N'].astype(str).unique().tolist() if x!='SIN DATO' and x!='0' and x!='nan'])
        if not micros or len(micros)==1:
            micros = ['TODAS'] + sorted(df['RED_N'].astype(str).unique().tolist())
        micro_filtro=st.selectbox("MICRORED/RED:", micros, key=f'{nombre_app}_micro_f')

    df_f = df.copy()
    if ano_filtro!='TODOS': df_f=df_f[df_f['AÑO_N']==ano_filtro]
    if micro_filtro!='TODAS':
        # filtra por micro o red
        if micro_filtro in df_f['MICRORED_N'].values:
            df_f=df_f[df_f['MICRORED_N']==micro_filtro]
        else:
            df_f=df_f[df_f['RED_N']==micro_filtro]

    # TABLA 1
    tabla1 = df_f.groupby(['RED_N','MICRORED_N','AÑO_N','EESS_N'])[['FEM','MASC']].sum().reset_index()
    tabla1['TOTAL']=tabla1['FEM']+tabla1['MASC']
    total_general=tabla1['TOTAL'].sum()
    if total_general==0: st.warning("No hay casos con filtro"); return
    fila_total=pd.DataFrame([{'RED_N':'TOTAL GENERAL','MICRORED_N':'','AÑO_N':'','EESS_N':'','FEM':tabla1['FEM'].sum(),'MASC':tabla1['MASC'].sum(),'TOTAL':total_general}])
    tabla1_final=pd.concat([tabla1,fila_total], ignore_index=True)

    st.subheader(f"TABLA 1 — {nombre_app} por EESS ({total_general} casos)")
    def style_row(row):
        if row['RED_N']=='TOTAL GENERAL': return ['background-color:#FFD700; color:black; font-weight:bold;']*len(row)
        return ['background-color:white; color:black; border:1px solid #ddd']*len(row)
    st.dataframe(tabla1_final.style.apply(style_row, axis=1), use_container_width=True, hide_index=True)

    # GRAFICOS
    tabla_graf=tabla1.groupby('AÑO_N')[['FEM','MASC']].sum().reset_index()
    fig1=go.Figure()
    fig1.add_trace(go.Bar(name='FEMENINOS', x=tabla_graf['AÑO_N'], y=tabla_graf['FEM'], marker_color='#E91E8C', text=tabla_graf['FEM'], textposition='outside'))
    fig1.add_trace(go.Bar(name='MASCULINOS', x=tabla_graf['AÑO_N'], y=tabla_graf['MASC'], marker_color='#0891B2', text=tabla_graf['MASC'], textposition='outside'))
    fig1.update_layout(title=f'{nombre_app} por AÑO - {total_general} casos', barmode='group', template='plotly_white', plot_bgcolor='white', paper_bgcolor='white', font=dict(color='black'))
    st.plotly_chart(fig1, use_container_width=True)

    total_f=tabla1['FEM'].sum(); total_m=tabla1['MASC'].sum()
    porc_f=round(total_f/(total_f+total_m)*100,1) if (total_f+total_m)>0 else 0
    porc_m=round(total_m/(total_f+total_m)*100,1) if (total_f+total_m)>0 else 0

    st.subheader("Distribución por Sexo")
    st.markdown(f"""
    <div style="display:flex; justify-content:center; gap:100px; background:white; padding:20px;">
        <div style="text-align:center"><svg width="130" height="130" style="transform:rotate(-90deg)"><circle cx="65" cy="65" r="50" fill="none" stroke="#f1f5f9" stroke-width="12"/><circle cx="65" cy="65" r="50" fill="none" stroke="#E91E8C" stroke-width="12" stroke-dasharray="{porc_f*3.14} 314" stroke-linecap="round"/></svg><div style="margin-top:-95px; margin-bottom:60px;"><div style="font-size:28px; font-weight:900; color:#E91E8C;">{porc_f:.0f}%</div><div style="color:black;">{total_f} F</div></div></div>
        <div style="text-align:center"><svg width="130" height="130" style="transform:rotate(-90deg)"><circle cx="65" cy="65" r="50" fill="none" stroke="#f1f5f9" stroke-width="12"/><circle cx="65" cy="65" r="50" fill="none" stroke="#0891B2" stroke-width="12" stroke-dasharray="{porc_m*3.14} 314" stroke-linecap="round"/></svg><div style="margin-top:-95px; margin-bottom:60px;"><div style="font-size:28px; font-weight:900; color:#0891B2;">{porc_m:.0f}%</div><div style="color:black;">{total_m} M</div></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("TABLA 2 — Grupo Etario")
    tabla3=df_f.groupby(['GRUPO_ETARIO'])[['FEM','MASC']].sum().reset_index()
    tabla3['TOTAL']=tabla3['FEM']+tabla3['MASC']
    tabla3=tabla3.sort_values('TOTAL', ascending=False)
    st.dataframe(tabla3, use_container_width=True, hide_index=True)
    fig3=px.bar(tabla3, x='GRUPO_ETARIO', y='TOTAL', color='GRUPO_ETARIO', text='TOTAL', title=f'{nombre_app} por Grupo Etario')
    fig3.update_traces(textposition='outside'); fig3.update_layout(template='plotly_white', showlegend=False, font=dict(color='black'))
    st.plotly_chart(fig3, use_container_width=True)

    def to_excel_pro():
        output=BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            wb=writer.book
            hdr=wb.add_format({'bold':True,'bg_color':'#1c2e4a','font_color':'white','border':1,'align':'center'})
            tot=wb.add_format({'bold':True,'bg_color':'#FFD700','border':2,'align':'center'})
            cell=wb.add_format({'border':1,'align':'center'})
            title=wb.add_format({'bold':True,'font_size':12,'bg_color':'#D9E1F2','border':1})
            s1='TABLA_1_EESS'; tabla1_final.to_excel(writer, sheet_name=s1, index=False, startrow=1)
            ws=writer.sheets[s1]; ws.write(0,0,f"TABLA 1: {nombre_app} - {ano_filtro}/{micro_filtro}",title)
            for c,v in enumerate(tabla1_final.columns): ws.write(1,c,v,hdr)
            for r in range(len(tabla1_final)):
                for c in range(len(tabla1_final.columns)):
                    f=tot if tabla1_final.iloc[r]['RED_N']=='TOTAL GENERAL' else cell
                    ws.write(r+2,c,tabla1_final.iloc[r,c],f)
            ws.set_column('A:G',18)
        return output.getvalue()

    def to_pdf_pro():
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=A4, rightMargin=35, leftMargin=35, topMargin=40, bottomMargin=30)
        styles=getSampleStyleSheet()
        stt=ParagraphStyle('T', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#1c2e4a'), alignment=1, spaceAfter=6)
        sh2=ParagraphStyle('H2', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#1c2e4a'), spaceAfter=3, spaceBefore=8)
        s_desc=ParagraphStyle('Desc', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor('#334155'), leftIndent=6, borderPadding=6, backColor=colors.HexColor('#f8fafc'), spaceAfter=6)
        story=[]
        story.append(Paragraph(f"<b>ANALISIS NOTIWEB 2026 - RSH UE 405</b><br/>{nombre_app} - {ano_filtro}/{micro_filtro}", stt))
        story.append(Spacer(1,6))
        story.append(Paragraph(f"<b>1. RESUMEN:</b> {total_general} casos. F {total_f} ({porc_f:.1f}%) M {total_m} ({porc_m:.1f}%)", s_desc))
        data=[['RED','MICRORED','AÑO','EESS','F','M','TOTAL']]
        for _,r in tabla1.sort_values('TOTAL', ascending=False).head(10).iterrows():
            data.append([str(r['RED_N'])[:8],str(r['MICRORED_N'])[:8],str(r['AÑO_N']),str(r['EESS_N'])[:15],str(r['FEM']),str(r['MASC']),str(r['TOTAL'])])
        t=Table(data, colWidths=[45,45,22,95,18,18,28])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1c2e4a')),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),6.5)]))
        story.append(t)
        doc.build(story)
        return buffer.getvalue()

    ca,cb=st.columns(2)
    with ca: st.download_button("📊 EXCEL PRO", data=to_excel_pro(), file_name=f"{nombre_app}_PRO.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)
    with cb: st.download_button("📄 PDF PRO", data=to_pdf_pro(), file_name=f"{nombre_app}_PDF.pdf", mime="application/pdf", use_container_width=True)