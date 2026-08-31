import streamlit as st, json, os, hashlib
from datetime import datetime
RUTA_USUARIOS = "usuarios.json"
def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()
def cargar_usuarios():
    if not os.path.exists(RUTA_USUARIOS):
        d = {"alex":{"nombre":"Alex Quispe","password":hash_password("Huamalies2026"),"correo":"alex.quispe@huamalies.gob.pe","rol":"admin","creado":str(datetime.now())}}
        json.dump(d, open(RUTA_USUARIOS,"w"), indent=4)
        return d
    return json.load(open(RUTA_USUARIOS,"r"))
def guardar_usuarios(u): json.dump(u, open(RUTA_USUARIOS,"w"), indent=4)

def login_page():
    st.markdown("""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {background:#ffffff !important; color:#0f172a !important;}
    .block-container {background:#ffffff !important;}
    input, textarea {background:#e9ecef !important; color:#000000 !important; border:1px solid #94a3b8 !important;}
    div[data-baseweb="input"] {background:#e9ecef !important;}
    label, p, span, h1, h2, h3 {color:#0f172a !important;}
    .stButton>button {color:white !important;}
    </style>
    """, unsafe_allow_html=True)
    c1,c2 = st.columns([1,1], gap="large")
    with c1:
        if os.path.exists("logo_huamalies.png"): st.image("logo_huamalies.png", width=320)
    with c2:
        st.markdown("<h2 style='color:#1c2e4a !important;'>ANALISIS NOTIWEB 2026, RSH</h2>", unsafe_allow_html=True)
        u = st.text_input("Usuario", placeholder="Usuario")
        p = st.text_input("Contraseña", type="password", placeholder="Contraseña")
        if st.button("Ingresar", type="primary"):
            users=cargar_usuarios()
            if u in users and users[u]["password"]==hash_password(p):
                st.session_state["auth"]=True; st.session_state["usuario"]=u; st.session_state["rol"]=users[u]["rol"]; st.session_state["nombre"]=users[u]["nombre"]; st.rerun()
            else: st.error("Usuario o contraseña incorrectos")
        if st.button("Olvidé mi contraseña? Resetear contraseña"): st.session_state["show_reset"]=True
        if st.button("Aún no tienes cuenta? Registrarse aquí"): st.session_state["show_register"]=True
        if st.session_state.get("show_reset"):
            st.divider(); correo=st.text_input("Correo registrado")
            if st.button("Enviar Código"):
                users=cargar_usuarios()
                for k,v in users.items():
                    if v.get("correo")==correo: st.session_state["user_rec"]=k; st.success(f"Código: {k.upper()}-2026")
            if st.session_state.get("user_rec"):
                nueva=st.text_input("Nueva contraseña", type="password")
                if st.button("Cambiar ahora"):
                    users=cargar_usuarios(); users[st.session_state["user_rec"]]["password"]=hash_password(nueva); guardar_usuarios(users); st.success("Cambiada"); st.session_state["show_reset"]=False; st.rerun()
        if st.session_state.get("show_register"):
            st.divider(); nu=st.text_input("Usuario nuevo"); nn=st.text_input("Nombre"); nc=st.text_input("Correo"); np=st.text_input("Pass", type="password"); ca=st.text_input("Código Admin", type="password")
            if st.button("Crear cuenta"):
                if ca=="Huamalies2026":
                    users=cargar_usuarios(); users[nu]={"nombre":nn,"password":hash_password(np),"correo":nc,"rol":"usuario","creado":str(datetime.now())}; guardar_usuarios(users); st.success("Creado"); st.session_state["show_register"]=False; st.rerun()
                else: st.error("Código incorrecto")

def check_auth():
    if "auth" not in st.session_state: st.session_state["auth"]=False
    return st.session_state["auth"]