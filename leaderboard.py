import streamlit as st
import pandas as pd
from ui import page_header, section_title

def mostrar_top(supabase):
    page_header(
        "Ranking y Auditoria",
        "Mira quién va arriba y prepara la revisión de jugadas.",
        "Competencia",
    )
    
    # =====================================================================
    # ⚡ MOTOR DE CÁLCULO EN VIVO (CORREGIDO SIN UPDATED_AT)
    # =====================================================================
    # 1. Traemos los perfiles básicos
    res_profiles = supabase.table("profiles").select("id, username").execute()
    df_profiles = pd.DataFrame(res_profiles.data)
    
    # 2. Traemos todos los partidos (QUITAMOS updated_at) y predicciones
    res_partidos_all = supabase.table("partidos").select("id, goles_a_real, goles_b_real, equipo_a, equipo_b, grupo, fecha_partido").execute()
    res_preds_all = supabase.table("predicciones").select("user_id, partido_id, goles_a_pred, goles_b_pred").execute()
    
    df_partidos_all = pd.DataFrame(res_partidos_all.data)
    df_preds_all = pd.DataFrame(res_preds_all.data)
    
    # Filtrar solo partidos que ya tienen resultado cargado
    df_partidos_jugados = df_partidos_all[df_partidos_all['goles_a_real'].notna() & df_partidos_all['goles_b_real'].notna()]
    
    if not df_profiles.empty:
        # Si hay predicciones y partidos jugados, calculamos los puntos reales sobre la marcha
        if not df_preds_all.empty and not df_partidos_jugados.empty:
            # Cruzamos predicciones con partidos jugados
            df_calc = df_preds_all.merge(df_partidos_jugados, left_on="partido_id", right_on="id")
            
            # Función matemática pura para calcular puntos por fila (Evita errores de texto)
            def calcular_puntos_fila(row):
                ga_p, gb_p = row['goles_a_pred'], row['goles_b_pred']
                ga_r, gb_r = row['goles_a_real'], row['goles_b_real']
                
                # Tendencias numéricas puras
                acerto_a = (ga_p > gb_p) and (ga_r > gb_r)
                acerto_b = (ga_p < gb_p) and (ga_r < gb_r)
                acerto_e = (ga_p == gb_p) and (ga_r == gb_r)
                
                if acerto_a or acerto_b or acerto_e:
                    if ga_p == ga_r and gb_p == gb_r:
                        return 2 # Marcador Exacto
                    return 1 # Tendencia
                return 0

            df_calc['pts_reales'] = df_calc.apply(calcular_puntos_fila, axis=1)
            
            # Agrupamos los puntos por usuario
            df_puntos_user = df_calc.groupby('user_id')['pts_reales'].sum().reset_index()
            df_puntos_user.columns = ['id', 'puntos']
            
            # Unimos con todos los perfiles para no dejar a nadie por fuera
            df = df_profiles.merge(df_puntos_user, on='id', how='left').fillna({'puntos': 0})
            df['puntos'] = df['puntos'].astype(int)
            df = df.sort_values(by='puntos', ascending=False).reset_index(drop=True)
        else:
            # Si no hay partidos jugados, todos inician con 0 puntos
            df = df_profiles.copy()
            df['puntos'] = 0

        # =====================================================================
        # 🌟 FLASH DE LA JORNADA
        # =====================================================================
        try:
            partidos_jugados_list = res_partidos_all.data
            partidos_jugados = [p for p in partidos_jugados_list if p.get("goles_a_real") is not None and p.get("goles_b_real") is not None]
            
            if partidos_jugados:
                muestra = partidos_jugados[0]
                if "fecha_partido" in muestra:
                    partidos_jugados.sort(key=lambda x: x.get("fecha_partido", ""), reverse=True)
                else:
                    partidos_jugados.sort(key=lambda x: x.get("id", 0), reverse=True)
                
                ultimo_partido = partidos_jugados[0]
                p_id = ultimo_partido["id"]
                g_a_real = ultimo_partido["goles_a_real"]
                g_b_real = ultimo_partido["goles_b_real"]
                partido_nombre = f"{ultimo_partido['equipo_a']} vs {ultimo_partido['equipo_b']}"
                
                res_preds_match = supabase.table("predicciones").select("user_id, goles_a_pred, goles_b_pred").eq("partido_id", p_id).execute()
                
                ganadores_exactos = []
                if res_preds_match.data:
                    for pred in res_preds_match.data:
                        if pred["goles_a_pred"] == g_a_real and pred["goles_b_pred"] == g_b_real:
                            user_row = df[df["id"] == pred["user_id"]]
                            if not user_row.empty:
                                ganadores_exactos.append(user_row["username"].values[0])
                
                if ganadores_exactos:
                    nombres_ganadores = ", ".join([f"✨ **@{u}**" for u in ganadores_exactos])
                    st.info(f"📢 **Flash de la Jornada:** En el partido **{partido_nombre}** ({g_a_real} - {g_b_real}), nuestros ganadores exactos fueron: {nombres_ganadores} 🎯")
                else:
                    st.write(f"📉 *En el partido **{partido_nombre}** ({g_a_real} - {g_b_real}), nadie logró acertar el marcador exacto.*")
        except Exception as e:
            pass
            
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
        section_title("Tabla general", "Los puntos se calculan en tiempo real tras cada gol oficial.")
        st.dataframe(df[['username', 'puntos']], use_container_width=True, hide_index=True)
        
        st.divider()

        # =====================================================================
        # 2. SECCIÓN DE AUDITORÍA
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

            # --- ESTRELLAS DE LA JORNADA ---
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
        
 
