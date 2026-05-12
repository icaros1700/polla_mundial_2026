import streamlit as st
from supabase import Client

def mostrar_auth(supabase: Client):
    st.markdown("<h2 style='text-align: center;'>⚽ Bienvenido a la Polla del Mundial 2026</h2>", unsafe_allow_html=True)
    
    tab_login, tab_registro = st.tabs(["🔑 Ingresar", "📝 Registrarse"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("Entrar al Juego", use_container_width=True)

            if btn_login:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = response.user
                    st.success("Acceso concedido. Cargando estadios...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error de acceso: Verifica tus credenciales.")

    with tab_registro:
        with st.form("registro_form"):
            new_email = st.text_input("Tu Correo")
            new_password = st.text_input("Crea una Contraseña Segura", type="password")
            username = st.text_input("Nombre de Usuario (Como te verán en el Ranking)")
            btn_reg = st.form_submit_button("Crear mi Perfil", use_container_width=True)

            if btn_reg:
                if not username:
                    st.warning("Necesitas un nombre de usuario para el ranking.")
                else:
                    try:
                        # 1. Crear usuario en Auth de Supabase
                        response = supabase.auth.sign_up({"email": new_email, "password": new_password})
                        user = response.user
                        
                        if user:
                            # 2. Crear el perfil en nuestra tabla personalizada 'profiles'
                            # Nota: El ID debe ser el mismo que el de Auth
                            supabase.table("profiles").insert({
                                "id": user.id,
                                "username": username,
                                "puntos": 0
                            }).execute()
                            
                            st.success("¡Cuenta creada! intenta ingresar.")
                    except Exception as e:
                        st.error(f"Fallo en el registro: {e}")