import streamlit as st
import pandas as pd
from ui import page_header, section_title

def mostrar_top(supabase):
    page_header(
        "Ranking y Auditoria",
        "Mira quien va arriba y prepara la revision de jugadas cuando los marcadores esten completos.",
        "Competencia",
    )
    
    # 1. Ranking General
    res = supabase.table("profiles").select("id, username, puntos").order("puntos", desc=True).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        section_title("Tabla general", "Los puntos se actualizan cuando el administrador publica resultados oficiales.")
        st.dataframe(df[['username', 'puntos']], use_container_width=True, hide_index=True)
        
        st.divider()
        
        # 2. SECCIÓN DE AUDITORÍA: Verificar a otro usuario
        section_title("Verificacion de jugadas")
        st.info("Este panel solo estara visible cuando todos los marcadores esten completos")
        ##usuario_a_ver = st.selectbox("Selecciona un usuario para ver sus jugadas:", df['username'].tolist())
        
        #user_id_sel = df[df['username'] == usuario_a_ver]['id'].values[0]
        
        # Traer predicciones del usuario seleccionado
        #res_preds = supabase.table("predicciones").select("*, partidos(equipo_a, equipo_b)").eq("user_id", user_id_sel).execute()
        
        #if res_preds.data:
            #data_audit = []
            #for r in res_preds.data:
                #partido = f"{r['partidos']['equipo_a']} vs {r['partidos']['equipo_b']}"
                #marcador = f"{r['goles_a_pred']} - {r['goles_b_pred']}"
                #puntos = r.get('puntos_ganados', 0)
                #data_audit.append({"Partido": partido, "Predicción": marcador, "Pts Ganados": puntos})
            
            #st.table(pd.DataFrame(data_audit))
        #else:
            #st.info("Este usuario aún no ha realizado predicciones.")
