import streamlit as st
from ui import match_card, page_header, section_title

def mostrar_carteleras_partidos(supabase, user_id):
    page_header(
        "Mis Predicciones",
        "Elige tus marcadores antes de que ruede el balon. Cada acierto suma en la tabla general.",
        "Cartelera oficial",
    )
    
    # 1. Traer todos los partidos
    res_partidos = supabase.table("partidos").select("*").order("id").execute()
    partidos = res_partidos.data
    
    # 2. Traer las predicciones que ya hizo ESTE usuario
    res_preds = supabase.table("predicciones").select("*").eq("user_id", user_id).execute()
    predicciones_usuario = res_preds.data
    
    # Diccionario para buscar rápido si el partido ya está bloqueado
    mapa_predicciones = {p["partido_id"]: p for p in predicciones_usuario}
    
    if not partidos:
        st.info("La FIFA aún no ha cargado los partidos en la Matrix.")
        return

    section_title("Partidos disponibles", "Guarda cada marcador una sola vez; despues queda bloqueado para auditoria.")

    # 3. Dibujar la cuadrícula (2 columnas para desktop; Streamlit las apila en movil)
    col1, col2 = st.columns(2)
    
    for index, partido in enumerate(partidos):
        partido_id = partido["id"]
        equipo_a = partido["equipo_a"]
        equipo_b = partido["equipo_b"]
        
        # Alternar entre la columna 1 y 2
        col_actual = col1 if index % 2 == 0 else col2
        
        with col_actual:
            esta_guardado = partido_id in mapa_predicciones
            match_card(
                equipo_a,
                equipo_b,
                meta=partido.get("grupo", "Fase de grupos"),
                status="Guardado" if esta_guardado else "Por jugar",
            )

            # --- CONDICIÓN: ¿YA LO JUGÓ? ---
            if esta_guardado:
                pred = mapa_predicciones[partido_id]
                st.success("Marcador guardado")

                c1, c2 = st.columns(2)
                c1.number_input(equipo_a, value=pred["goles_a_pred"], disabled=True, key=f"dis_a_{partido_id}")
                c2.number_input(equipo_b, value=pred["goles_b_pred"], disabled=True, key=f"dis_b_{partido_id}")

            else:
                # --- MODO ACTIVO (Formulario) ---
                with st.form(key=f"form_partido_{partido_id}"):
                    c1, c2 = st.columns(2)
                    goles_a = c1.number_input(equipo_a, min_value=0, step=1, key=f"a_{partido_id}")
                    goles_b = c2.number_input(equipo_b, min_value=0, step=1, key=f"b_{partido_id}")

                    if st.form_submit_button("Guardar prediccion", type="primary", use_container_width=True):
                        resultado = "Gana A" if goles_a > goles_b else ("Gana B" if goles_b > goles_a else "Empate")

                        payload = {
                            "user_id": user_id,
                            "partido_id": partido_id,
                            "goles_a_pred": goles_a,
                            "goles_b_pred": goles_b,
                            "resultado_pred": resultado
                        }

                        try:
                            supabase.table("predicciones").insert(payload).execute()
                            st.rerun()
                        except Exception as e:
                            st.error("Error al guardar la predicción.")
