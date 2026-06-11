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

        # =====================================================================
        # 2. SECCIÓN DE AUDITORÍA: Verificar a otro usuario (¡AHORA ADENTRO E INDENTADO!)
        # =====================================================================
        st.subheader("🔍 Verificación de Jugadas")
        st.info("Este panel muestra las predicciones y los puntos calculados en tiempo real.")

        # Selector de usuarios basado en el DataFrame general de posiciones
        usuario_a_ver = st.selectbox("Selecciona un usuario para ver sus jugadas:", df['username'].tolist())
        user_id_sel = df[df['username'] == usuario_a_ver]['id'].values[0]

        # Consulta a Supabase cruzando tablas con los nombres de columna correctos
        res_preds = supabase.table("predicciones").select(
            "*, partidos(equipo_a, equipo_b, goles_a_real, goles_b_real)"
        ).eq("user_id", user_id_sel).execute()

        if res_preds.data:
            data_audit = []
            for r in res_preds.data:
                partido_info = r['partidos']
                partido = f"{partido_info['equipo_a']} vs {partido_info['equipo_b']}"
                marcador_pred = f"{r['goles_a_pred']} - {r['goles_b_pred']}"
                
                # Extraemos los goles reales cargados por el administrador
                g_a_real = partido_info.get('goles_a_real')
                g_b_real = partido_info.get('goles_b_real')
                
                # Lógica matemática en vivo (Regla: 1 por resultado general + 1 por marcador exacto)
                puntos = 0
                if g_a_real is not None and g_b_real is not None:
                    # Desglosamos las condiciones para evitar el uso de barras "\" que rompen el servidor
                    acerto_gana_a = (r['goles_a_pred'] > r['goles_b_pred']) and (g_a_real > g_b_real)
                    acerto_gana_b = (r['goles_a_pred'] < r['goles_b_pred']) and (g_a_real < g_b_real)
                    acerto_empate = (r['goles_a_pred'] == r['goles_b_pred']) and (g_a_real == g_b_real)
                    
                    # 1. ¿Acertó el resultado general? -> 1 punto
                    if acerto_gana_a or acerto_gana_b or acerto_empate:
                        puntos = 1
                        
                        # 2. ¿Además el marcador fue EXACTO? -> Sube a 2 puntos total
                        if r['goles_a_pred'] == g_a_real and r['goles_b_pred'] == g_b_real:
                            puntos = 2

                # Estructuramos la fila para el reporte visual
                data_audit.append({
                    "Partido": partido, 
                    "Predicción": marcador_pred, 
                    "Resultado Real": f"{g_a_real} - {g_b_real}" if g_a_real is not None else "Pendiente",
                    "Pts Ganados": puntos
                })
            
            # Renderizamos la tabla formateada en Streamlit
            st.table(pd.DataFrame(data_audit))
        else:
            st.info("Este usuario aún no ha realizado predicciones.")
    else:
        st.warning("No hay datos de usuarios disponibles para mostrar el ranking o la auditoría.")
        
        
 
