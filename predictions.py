import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from ui import match_card, page_header, section_title

def mostrar_carteleras_partidos(supabase, user_id):
    page_header(
        "Mis Predicciones",
        "Elige tus marcadores antes de que ruede el balón. Cada acierto suma en la tabla general.",
        "Cartelera oficial",
    )
    
    # 1. Traer todos los partidos de la base de datos
    res_partidos = supabase.table("partidos").select("*").order("id").execute()
    partidos = res_partidos.data
    
    # 2. Traer las predicciones que ya hizo ESTE usuario
    res_preds = supabase.table("predicciones").select("*").eq("user_id", user_id).execute()
    predicciones_usuario = res_preds.data
    
    # Diccionario para búsqueda rápida de predicciones hechas
    mapa_predicciones = {p["partido_id"]: p for p in predicciones_usuario}
    
    if not partidos:
        st.info("La FIFA aún no ha cargado los partidos en la Matrix.")
        return

    # 3. CREACIÓN DE LAS PESTAÑAS (TABS)
    tab1, tab2 = st.tabs(["📊 Fase de Grupos", "⚔️ La Arena - Segunda Fase"])

    ahora_utc = datetime.now(timezone.utc)

    # =====================================================================
    # PESTAÑA 1: FASE DE GRUPOS (Intacta)
    # =====================================================================
    with tab1:
        partidos_grupos = [p for p in partidos if p.get("fase") != 2]
        if not partidos_grupos:
            st.info("No hay partidos de fase de grupos registrados.")
        else:
            section_title("Fase Regular", "Marcadores de la ronda de grupos.")
            col1, col2 = st.columns(2)
            for index, partido in enumerate(partidos_grupos):
                partido_id = partido["id"]
                equipo_a = partido["equipo_a"]
                equipo_b = partido["equipo_b"]
                col_actual = col1 if index % 2 == 0 else col2
                with col_actual:
                    esta_guardado = partido_id in mapa_predicciones
                    match_card(equipo_a, equipo_b, meta=partido.get("grupo", "Fase de grupos"), status="Guardado" if esta_guardado else "Por jugar")
                    if esta_guardado:
                        pred = mapa_predicciones[partido_id]
                        st.success("Marcador guardado")
                        c1, c2 = st.columns(2)
                        c1.number_input(equipo_a, value=pred["goles_a_pred"], disabled=True, key=f"dis_a_{partido_id}")
                        c2.number_input(equipo_b, value=pred["goles_b_pred"], disabled=True, key=f"dis_b_{partido_id}")
                    else:
                        with st.form(key=f"form_partido_{partido_id}"):
                            c1, c2 = st.columns(2)
                            goles_a = c1.number_input(equipo_a, min_value=0, step=1, key=f"a_{partido_id}")
                            goles_b = c2.number_input(equipo_b, min_value=0, step=1, key=f"b_{partido_id}")
                            if st.form_submit_button("Guardar prediccion", type="primary", use_container_width=True):
                                resultado = "Gana A" if goles_a > goles_b else ("Gana B" if goles_b > goles_a else "Empate")
                                try:
                                    supabase.table("predicciones").insert({"user_id": user_id, "partido_id": partido_id, "goles_a_pred": goles_a, "goles_b_pred": goles_b, "resultado_pred": resultado}).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    # =====================================================================
    # PESTAÑA 2: THE KNOCKOUT ARENA (VISUAL Y DEBUG REPARADOS)
    # =====================================================================
    with tab2:
        partidos_arena = [p for p in partidos if p.get("fase") == 2]
        
        if not partidos_arena:
            st.info("La Arena se está preparando...")
        else:
            section_title("The Knockout Arena", "Rondas de eliminación directa.")
            col1, col2 = st.columns(2)
            
            for index, partido in enumerate(partidos_arena):
                partido_id = partido["id"]
                equipo_a = partido["equipo_a"]
                equipo_b = partido["equipo_b"]
                col_actual = col1 if index % 2 == 0 else col2
                
                with col_actual:
                    fecha_partido_dt = pd.to_datetime(partido['fecha_partido']).to_pydatetime()
                    tiempo_restante = fecha_partido_dt - ahora_utc
                    un_hora = timedelta(hours=1)
                    
                    bloqueado = tiempo_restante <= un_hora
                    esta_guardado = partido_id in mapa_predicciones
                    
                    # Semáforo de tiempo
                    if bloqueado:
                        st.markdown("<div style='background-color:#ffebeb; color:#d63031; padding:8px; border-radius:8px; font-weight:bold; text-align:center; font-size:0.9rem;'>🔴 CERRADO - PREDICCIONES BLOQUEADAS</div>", unsafe_allow_html=True)
                    else:
                        if tiempo_restante > timedelta(days=1):
                            dias = tiempo_restante.days
                            horas, rem = divmod(tiempo_restante.seconds, 3600)
                            st.markdown(f"<div style='background-color:#e6fffa; color:#006655; padding:8px; border-radius:8px; font-weight:bold; text-align:center; font-size:0.9rem;'>⏳ 🟢 Cierra en: {dias}d {horas}h</div>", unsafe_allow_html=True)
                        else:
                            horas, rem = divmod(tiempo_restante.seconds, 3600)
                            minutos, _ = divmod(rem, 60)
                            st.markdown(f"<div style='background-color:#fff7e6; color:#a16207; padding:8px; border-radius:8px; font-weight:bold; text-align:center; font-size:0.9rem;'>⚠️ 🟠 TIEMPO CRÍTICO: {horas:02d}:{minutos:02d} restantes</div>", unsafe_allow_html=True)
                    
                    st.write("")

                    match_card(
                        equipo_a,
                        equipo_b,
                        meta=partido.get("grupo", "Eliminación Directa"),
                        status="Bloqueado" if bloqueado else ("Guardado" if esta_guardado else "Por jugar"),
                    )

                    if esta_guardado or bloqueado:
                        if bloqueado and not esta_guardado:
                            try:
                                supabase.table("predicciones").insert({"user_id": user_id, "partido_id": partido_id, "goles_a_pred": 0, "goles_b_pred": 0, "resultado_pred": "Empate"}).execute()
                                st.rerun()
                            except Exception: pass
                        
                        pred = mapa_predicciones.get(partido_id, {"goles_a_pred": 0, "goles_b_pred": 0})
                        if esta_guardado and not bloqueado:
                            st.success("Marcador asegurado con éxito")
                        else:
                            st.error("Predicción final sellada por la Matrix")

                        c1, c2 = st.columns(2)
                        c1.number_input(equipo_a, value=int(pred["goles_a_pred"]), disabled=True, key=f"arena_dis_a_{partido_id}", label_visibility="collapsed")
                        c2.number_input(equipo_b, value=int(pred["goles_b_pred"]), disabled=True, key=f"arena_dis_b_{partido_id}", label_visibility="collapsed")

                    # --- MODO FORMULARIO: REPARACIÓN DE SIMETRÍA ---
                    else:
                        with st.form(key=f"form_arena_{partido_id}"):
                            c1, c2 = st.columns(2)
                            # 🎯 Se añade label_visibility="collapsed" para centrar los inputs limpiamente
                            goles_a = c1.number_input(equipo_a, min_value=0, step=1, key=f"arena_a_{partido_id}", label_visibility="collapsed")
                            goles_b = c2.number_input(equipo_b, min_value=0, step=1, key=f"arena_b_{partido_id}", label_visibility="collapsed")

                            if st.form_submit_button("Sellar predicción", type="primary", use_container_width=True):
                                resultado = "Gana A" if goles_a > goles_b else ("Gana B" if goles_b > goles_a else "Empate")
                                payload = {
                                    "user_id": user_id,
                                    "partido_id": partido_id,
                                    "goles_a_pred": int(goles_a),
                                    "goles_b_pred": int(goles_b),
                                    "resultado_pred": resultado
                                }
                                try:
                                    supabase.table("predicciones").insert(payload).execute()
                                    st.toast("¡Predicción guardada en la Arena!")
                                    st.rerun()
                                except Exception as e:
                                    # 🔍 Revelador del secreto de la base de datos
                                    st.error(f"❌ Error de la Matrix: {e}")

        
