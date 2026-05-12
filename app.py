from random import choice
import streamlit as st
from supabase import create_client, Client
from auth import mostrar_auth
import predictions  # <--- Importación del nuevo módulo
import admin
import leaderboard
import groups

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Polla Mundial 2026", 
    page_icon="⚽", 
    layout="wide"  # 'wide' para que las tarjetas de partidos se vean mejor
)

# --- 2. CONEXIÓN A LA MATRIX (SUPABASE) ---
@st.cache_resource
def init_connection():
    # Extrae las llaves de .streamlit/secrets.toml
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# --- 3. GESTIÓN DE SESIÓN ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- 4. LÓGICA PRINCIPAL DE NAVEGACIÓN ---

def main():
    if st.session_state.user is None:
        mostrar_auth(supabase)
    else:
        # --- VERIFICACIÓN DE SEGURIDAD PARA ADMIN ---
        # 2. Buscamos en la tabla profiles si este usuario tiene is_admin = True
        res_perfil = supabase.table("profiles").select("is_admin").eq("id", st.session_state.user.id).single().execute()
        es_admin = res_perfil.data.get("is_admin", False)

        st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/FIFA_World_Cup_2026_logo.svg/1200px-FIFA_World_Cup_2026_logo.svg.png", width=100)
        st.sidebar.title("🏆 Mundial 2026")
        st.sidebar.write(f"👤 **Usuario:** {st.session_state.user.email}")
        
        

        # --- CÁLCULO DEL POZO ACUMULADO ---
        # 1. Contamos el total de jugadores registrados
        res_count = supabase.table("profiles").select("id", count="exact").execute()
        total_jugadores = res_count.count if res_count.count else 0
        
        # 2. Definimos las variables de dinero
        costo_entrada = 50000
        pozo_total = total_jugadores * costo_entrada
        premio_1 = pozo_total * 0.70
        premio_2 = pozo_total * 0.30

        # 3. Diseño visual en la barra lateral
        st.sidebar.divider()
        st.sidebar.subheader("💰 Pozo del Mundial")
        
        # Mostramos el total de forma llamativa
        st.sidebar.metric(label="Total Acumulado", value=f"${pozo_total:,.0f} COP")

        
        # Mostramos la repartición
        col_p1, col_p2 = st.sidebar.columns(2)
        with col_p1:
            st.sidebar.caption("🥇 1er Puesto (70%)")
            st.sidebar.write(f"**${premio_1:,.0f}**")
        with col_p2:
            st.sidebar.caption("🥈 2do Puesto (30%)")
            st.sidebar.write(f"**${premio_2:,.0f}**")
            
        st.sidebar.info(f"👥 Jugadores: {total_jugadores}")
        st.sidebar.divider()
        
        # 3. Menú Dinámico: Solo agregamos el panel si es_admin es True
        menu = ["🏟️ Mis Predicciones", "📊 Tabla de Grupos","🥇 Ranking y Auditoría"]
        if es_admin:
            menu.append("👨‍💻 Panel del Arquitecto") # Secreto revelado

        choice = st.sidebar.radio("Ir a:", menu)
        
        st.sidebar.divider()
        
        if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()

        # --- NAVEGACIÓN ---
        if choice == "🏟️ Mis Predicciones":
            predictions.mostrar_carteleras_partidos(supabase, st.session_state.user.id)
        elif choice == "📊 Tabla de Grupos":
            groups.mostrar_tablas_grupos(supabase)
        elif choice == "🥇 Ranking y Auditoría":
            leaderboard.mostrar_top(supabase)
        elif choice == "👨‍💻 Panel del Arquitecto":
            admin.mostrar_panel_admin(supabase)
            
        # 4. Conectamos la ruta hacia la consola secreta
        elif choice == "👨‍💻 Panel del Arquitecto":
            admin.mostrar_panel_admin(supabase)

if __name__ == "__main__":
    main()