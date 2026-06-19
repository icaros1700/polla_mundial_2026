import streamlit as st
import pandas as pd
from ui import page_header, section_title

def mostrar_top(supabase):
    page_header(
        "Ranking y Auditoria",
        "Mira quién va arriba y prepara la revisión de jugadas.",
        "Competencia",
    )
    
    # 1. Ranking General
    res = supabase.table("profiles").select("id, username, puntos").order("puntos", desc=True).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        
        # =====================================================================
        # 🌟 FLASH DE LA JORNADA (CORREGIDO CRONOLÓGICAMENTE CON FECHA_PARTIDO)
        # =====================================================================
        try:
            # Traemos todos los partidos con '*'
            res_partidos = supabase.table("partidos").select("*").execute()
            if res_partidos.data:
                # Filtramos los partidos que ya tienen un resultado oficial cargado
                partidos_jugados = [p for p in res_partidos.data if p.get("goles_a_real") is not None and p.get("goles_b_real") is not None]
                
                if partidos_jugados:
                    muestra = partidos_jugados[0]
                    
                    # 🎯 REPARACIÓN MÁGICA: Prioridad absoluta a tu columna 'fecha_partido'
                    if "fecha_partido" in muestra:
                        partidos_jugados.sort(key=lambda x: x.get("fecha_partido", ""), reverse=True)
                    elif "updated_at" in muestra:
                        partidos_jugados.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
                    elif "fecha" in muestra:
                        partidos_jugados.sort(key=lambda x: x.get("fecha", ""), reverse=True)
                    else:
                        partidos_jugados.sort(key=lambda x: x.get("id", 0), reverse=True)
                    
                    # Extraemos el partido más reciente en el tiempo real
                    ultimo_partido = partidos_jugados[0]
                    
                    p_id = ultimo_partido["id"]
                    g_a_real = ultimo_partido["goles_a_real"]
                    g_b_real = ultimo_partido["goles_b_real"]
                    partido_nombre = f"{ultimo_partido['equipo_a']} vs {ultimo_partido['equipo_b']}"
                    
                    # Consultamos las predicciones hechas exclusivamente para este partido
                    res_preds_match = supabase.table("predicciones").select("user_id, goles_a_pred, goles_b_pred").eq("partido_id", p_id).execute()
                    
                    ganadores_exactos = []
                    if res_preds_match.data:
                        for pred in res_preds_match.data:
                            # Filtro de Élite: marcador exacto (2 puntos)
                            if pred["goles_a_pred"] == g_a_real and pred["goles_b_pred"] == g_b_real:
                                user_row = df[df["id"] == pred["user_id"]]
                                if not user_row.empty:
                                    ganadores_exactos.append(user_row["username"].values[0])
                    
                    # Desplegamos el banner de honor dinámico
                    if ganadores_exactos:
                        nombres_ganadores = ", ".join([f"✨ **@{u}**" for u in ganadores_exactos])
                        st.info(f"📢 **Flash de la Jornada:** En el partido **{partido_nombre}** ({g_a_real} - {g_b_real}), nuestros ganadores exactos fueron: {nombres_ganadores} 🎯")
                    else:
                        st.write(f"📉 *En el partido **{partido_nombre}** ({g_a_real} - {g_b_real}), nadie logró acertar el marcador exacto.*")
        except Exception as e:
            pass # Evita caídas críticas de la interfaz
            
        st.write("") 

        # --- PODIO DE LA FAMA ---
        st.subheader("👑 El Podio de la Fama")
        col1, col2, col3 = st.columns(3)
        top_3 = df.head(3)

        with col2:
            if len(top_3) >= 1:
                st.markdown(f"### 🥇 {top_3.iloc[0]['username']}")
                st.write(f"**{top_3.iloc[0]['puntos']} pts**")
        with col1:
            if len(top_3) >= 2:
                st.markdown(f"#### 🥈 {top_3.iloc[1]['username']}")
                st.write(f"*{top_3.iloc[1]['puntos']} pts*")
        with col3:
            if len(top_3) >= 3:
                st.markdown(f"#### 🥉 {top_3.iloc[2]['username']}")
                st.write(f"*{top_3.iloc[2]['puntos']} pts*")
        
        st.divider()

        # --- TABLA GENERAL ---
        section_title("Tabla general", "Los puntos se actualizan tras cada jornada oficial.")
        st.dataframe(df[['username', 'puntos']], use_container_width=True, hide_index=True)
        
        st.divider()

        # =====================================================================
        # 2. SECCIÓN DE AUDITORÍA Y ESTRELLAS
        # =====================================================================
        st.subheader("🔍 Verificación de Jugadas")
        st.info("Calcula los aciertos en tiempo real.")

        usuario_a_ver = st.selectbox("Selecciona un usuario para ver sus jugadas:", df['username'].tolist())
        user_id_sel = df[df['username'] == usuario_a_ver]['id'].values[0]

        res_preds = supabase.table("predicciones").select(
            "*, partidos(equipo_a, equipo_b, goles_a_real, goles_b_real)"
        ).eq("user_id", user_id_sel).execute()

        if res_preds.data:
            data_audit = []
            for r in res_preds.data:
                partido_info = r['partidos']
                partido = f"{partido_info['equipo_a']} vs {partido_info['equipo_b']}"
                marcador_pred = f"{r['goles_a_pred']} - {r['goles_b_pred']}"
                
                g_a_real = partido_info.get('goles_a_real')
                g_b_real = partido_info.get('goles_b_real')
                
                puntos = 0
                if g_a_real is not None and g_b_real is not None:
                    acerto_gana_a = (r['goles_a_pred'] > r['goles_b_pred']) and (g_a_real > g_b_real)
                    acerto_gana_b = (r['goles_a_pred'] < r['goles_b_pred']) and (g_a_real < g_b_real)
                    acerto_empate = (r['goles_a_pred'] == r['goles_b_pred']) and (g_a_real == g_b_real)
                    
                    if acerto_gana_a or acerto_gana_b or acerto_empate:
                        puntos = 1
                        if r['goles_a_pred'] == g_a_real and r['goles_b_pred'] == g_b_real:
                            puntos = 2

                data_audit.append({
                    "Partido": partido, 
                    "Predicción": marcador_pred, 
                    "Resultado Real": f"{g_a_real} - {g_b_real}" if g_a_real is not None else "Pendiente",
                    "Pts Ganados": puntos
                })
            
            df_audit = pd.DataFrame(data_audit)
            st.table(df_audit)

            # --- ESTRELLAS DE LA JORNADA (ÉLITE) ---
            maestros_del_marcador = df_audit[df_audit["Pts Ganados"] == 2]
            
            if not maestros_del_marcador.empty:
                st.balloons()
                st.success("🏆 **¡Maestros del Marcador!**")
                st.write(f"Los siguientes partidos fueron leídos a la perfección por {usuario_a_ver}:")
                for _, row in maestros_del_marcador.iterrows():
                    st.markdown(f"✨ **{row['Partido']}**")
            else:
                if df_audit["Pts Ganados"].max() == 1:
                    st.info("¡Cerca de la perfección! Lograste puntos por resultados, pero aún no hay marcadores exactos.")
                else:
                    st.info("Sigue analizando los partidos, ¡la gloria del marcador exacto está cerca!")
        else:
            st.info("Este usuario aún no ha realizado predicciones.")
    else:
        st.warning("No hay usuarios para mostrar.")

        
 
