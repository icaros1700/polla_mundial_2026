from pandas.core.interchange import dataframe
import streamlit as st
import pandas as pd

def mostrar_top(supabase):
    st.title("🥇 Ranking y Verificacion")
    
    # 1. Ranking General
    res = supabase.table("profiles").select("id, username, puntos").order("puntos", desc=True).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        st.dataframe(df[['username', 'puntos']], use_container_width=True, hide_index=True)
        
        st.divider()
        
        
        # 2. SECCIÓN DE AUDITORÍA: Verificar a otro usuario
        st.subheader("🔍 Verificación de Jugadas")
        st.info("Este panel muestra las predicciones y los puntos calculados en tiempo real.")

        usuario_a_ver = st.selectbox("Selecciona un usuario para ver sus jugadas:", df['username'].tolist())
        user_id_sel = df[df['username'] == usuario_a_ver]['id'].values[0]

        # 🌟 MODIFICACIÓN 1: Traemos también los goles reales del partido (goles_a, goles_b)
        res_preds = supabase.table("predicciones").select("*, partidos(equipo_a, equipo_b, goles_a_real, goles_b_real)").eq("user_id", user_id_sel).execute()

        if res_preds.data:
            data_audit = []
            for r in res_preds.data:
                partido_info = r['partidos']
                partido = f"{partido_info['equipo_a']} vs {partido_info['equipo_b']}"
                marcador_pred = f"{r['goles_a_pred']} - {r['goles_b_pred']}"
        
                # Capturamos los goles reales (si el partido ya tiene resultado)
                g_a_real = partido_info.get('goles_a_real')
                g_b_real = partido_info.get('goles_b_real')
        
                # 🌟 MODIFICACIÓN 2: Lógica matemática en vivo
                puntos = 0
                if g_a_real is not None and g_b_real is not None:
                    # Validamos si acertó el marcador exacto (Ej: 3 puntos)
                    if r['goles_a_pred'] == g_a_real and r['goles_b_pred'] == g_b_real:
                        puntos = 2
                    # Validamos si solo acertó el ganador o el empate (Ej: 1 punto)
                    elif (r['goles_a_pred'] > r['goles_b_pred'] and g_a_real > g_b_real) or \
                         (r['goles_a_pred'] < r['goles_b_pred'] and g_a_real < g_b_real) or \
                         (r['goles_a_pred'] == r['goles_b_pred'] and g_a_real == g_b_real):
                         puntos = 1

                data_audit.append({
                    "Partido": partido, 
                    "Predicción": marcador_pred, 
                    "Resultado Real": f"{g_a_real} - {g_b_real}" if g_a_real is not None else "Pendiente",
                    "Pts Ganados": puntos})
    
        st.table(pd.DataFrame(data_audit))
    else:
        st.info("Este usuario aún no ha realizado predicciones.")




