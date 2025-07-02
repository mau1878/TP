import streamlit as st

def format_currency(value):
    """
    Formatea un valor numérico como moneda argentina (punto de mil, sin decimales).
    No incluye el signo '$' ni 'ARS'. Devuelve solo el número con el punto de miles.
    """
    int_value = int(value)
    s = str(int_value)
    
    # Revertir el string para insertar los puntos de miles
    s_reversed = s[::-1]
    formatted_parts = []
    
    for i, char in enumerate(s_reversed):
        formatted_parts.append(char)
        if (i + 1) % 3 == 0 and (i + 1) != len(s_reversed):
            formatted_parts.append('.')
            
    # Revertir de nuevo y unir las partes
    formatted_s = "".join(formatted_parts[::-1])
    
    return formatted_s


def generar_presupuesto(lista_documentos, tasa_pagada_por_cliente, domicilio_traductor):
    # --- Precios para TRADUCCIONES PÚBLICAS (por foja) ---
    # Anidados por dirección (Al español / Al idioma extranjero), luego por Categoría (I/II)
    # y finalmente por tipo de documento.
    # Categoría I: Inglés, Categoría II: Alemán (para ambas direcciones)
    precios_por_foja = {
        "Al español": { # Traducción DESDE idioma extranjero HACIA español
            "I": { # Origen Inglés (o similar)
                "Partidas, pasaportes, certificados y demás documentos personales": 49800,
                "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación": 51100,
                "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar": 57700,
                "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención": 62800,
            },
            "II": { # Origen Alemán (o similar)
                "Partidas, pasaportes, certificados y demás documentos personales": 52100,
                "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación": 61900,
                "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar": 67000,
                "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención": 73100,
            }
        },
        "Al idioma extranjero": { # Traducción DESDE español HACIA idioma extranjero
            "I": { # Destino Inglés (o similar)
                "Partidas, pasaportes, certificados y demás documentos personales": 60800,
                "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación": 69700,
                "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar": 74400,
                "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención": 80800,
            },
            "II": { # Destino Alemán (o similar)
                "Partidas, pasaportes, certificados y demás documentos personales": 67800,
                "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación": 81700,
                "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar": 89000,
                "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención": 96800,
            }
        }
    }
    #
    # --- Precios para TRADUCCIONES SIN CARÁCTER PÚBLICO (por palabra) ---
    # Anidados por dirección (Al español / Al idioma extranjero), luego por categoría (I-V)
    precios_por_palabra = {
        "Al español": { # Traducción DESDE idioma extranjero HACIA español
            "I": 101, "II": 103, "III": 127, "IV": 154, "V": 164
        },
        "Al idioma extranjero": { # Traducción DESDE español HACIA idioma extranjero
            "I": 124, "II": 140, "III": 154, "IV": 185, "V": 205
        }
    }
    MINIMO_PALABRAS_NO_PUBLICAS = 250

    costo_base_traduccion_total = 0
    detalles_documentos = ""
    
    # Mapeo de idioma a categoría para precios públicos y no públicos
    LANG_TO_CAT_MAP = {"Inglés": "I", "Alemán": "II"}
    

    if not lista_documentos:
        st.warning("Por favor, agregá al menos un documento para generar el presupuesto.")
        return ""

    for i, doc in enumerate(lista_documentos):
        # Validar la existencia de claves cruciales para evitar errores
        if 'nombre_referencia' not in doc or \
           'idioma_origen' not in doc or \
           'idioma_destino' not in doc or \
           'tipo_traduccion' not in doc:
            st.warning(f"Documento número {i+1} en formato incompleto o antiguo. Por favor, eliminá este documento (o limpiá todos) y volvé a agregarlo con los datos completos.")
            continue # Saltar este documento mal formado

        nombre_referencia = doc['nombre_referencia']
        idioma_origen_doc = doc['idioma_origen']
        idioma_destino_doc = doc['idioma_destino']
        tipo_traduccion_doc = doc['tipo_traduccion'] # Usar el tipo de traducción guardado con el documento

        if tipo_traduccion_doc == "Traducción Pública":
            if 'fojas' not in doc or 'tipo_documento' not in doc:
                st.warning(f"Documento público '{nombre_referencia}' incompleto. Por favor, eliminá este documento y volvé a agregarlo con los datos completos.")
                continue

            fojas_doc = doc['fojas']
            tipo_documento_doc = doc['tipo_documento']

            # Determinar la dirección y la categoría del idioma para precios_por_foja
            direction_key = ""
            lang_cat_key = ""
            
            # Traducción Hacia Español (ej: Inglés > Español)
            if idioma_destino_doc == "Español":
                direction_key = "Al español"
                lang_cat_key = LANG_TO_CAT_MAP.get(idioma_origen_doc)
            # Traducción Desde Español Hacia Extranjero (ej: Español > Inglés)
            elif idioma_origen_doc == "Español":
                direction_key = "Al idioma extranjero"
                lang_cat_key = LANG_TO_CAT_MAP.get(idioma_destino_doc)
            else:
                st.warning(f"Combinación de idiomas '{idioma_origen_doc} > {idioma_destino_doc}' no soportada para traducción pública del documento '{nombre_referencia}'. Saltando este documento.")
                continue 
            
            if not lang_cat_key:
                st.warning(f"Categoría de idioma no definida para '{idioma_origen_doc}' o '{idioma_destino_doc}' en traducción pública de documento '{nombre_referencia}'. Saltando este documento.")
                continue

            costo_por_foja_actual = precios_por_foja.get(direction_key, {}).get(lang_cat_key, {}).get(tipo_documento_doc, 0)
            if costo_por_foja_actual == 0:
                 st.warning(f"No se encontró precio para el tipo de documento '{tipo_documento_doc}' en la combinación '{idioma_origen_doc} > {idioma_destino_doc}' (Cat {lang_cat_key}) para el documento '{nombre_referencia}'. Costo 0 aplicado para este documento.")

            costo_documento = fojas_doc * costo_por_foja_actual
            costo_base_traduccion_total += costo_documento

            detalles_documentos += (
                f"- **{nombre_referencia}** ({idioma_origen_doc} > {idioma_destino_doc}, {fojas_doc} fojas, tipo: \"{tipo_documento_doc}\"): "
                f"${format_currency(costo_documento)} ARS\n"
            )
        else: # Traducción sin carácter público
            if 'palabras' not in doc or 'categoria_idioma_no_publica' not in doc:
                st.warning(f"Documento sin carácter público '{nombre_referencia}' incompleto. Por favor, eliminá este documento y volvé a agregarlo con los datos completos.")
                continue

            palabras_doc = doc['palabras']
            categoria_idioma_no_publica = doc['categoria_idioma_no_publica'] # Esto ya viene como I-V
            
            # Determinar la clave para precios_por_palabra (Al español vs Al idioma extranjero)
            clave_precio_palabra = "Al español" if idioma_destino_doc == "Español" else "Al idioma extranjero"
            
            costo_por_palabra_actual = precios_por_palabra.get(clave_precio_palabra, {}).get(categoria_idioma_no_publica, 0)
            if costo_por_palabra_actual == 0:
                st.warning(f"No se encontró precio para la categoría '{categoria_idioma_no_publica}' en la dirección '{clave_precio_palabra}' para el documento '{nombre_referencia}'. Costo 0 aplicado para este documento.")

            costo_documento_bruto = palabras_doc * costo_por_palabra_actual
            
            # Aplicar mínimo de 250 palabras
            costo_documento = max(costo_documento_bruto, MINIMO_PALABRAS_NO_PUBLICAS * costo_por_palabra_actual)
            
            costo_base_traduccion_total += costo_documento

            detalles_documentos += (
                f"- **{nombre_referencia}** ({idioma_origen_doc} > {idioma_destino_doc}, {palabras_doc} palabras, categoría: \"{categoria_idioma_no_publica}\"): "
                f"${format_currency(costo_documento)} ARS"
            )
            if palabras_doc < MINIMO_PALABRAS_NO_PUBLICAS:
                detalles_documentos += f" (se aplica el mínimo de {MINIMO_PALABRAS_NO_PUBLICAS} palabras)\n"
            else:
                detalles_documentos += "\n"

    tasa_legalizacion_digital = 21000
    tasa_legalizacion_presencial = 24000
    recargo_gestion_presencial = 24000

    # Seña
    sena = costo_base_traduccion_total * 0.5

    texto_presupuesto = f"¡Hola!\n\n"
    texto_presupuesto += f"Necesitás una **traducción de los siguientes documentos**:\n"
    texto_presupuesto += detalles_documentos
    texto_presupuesto += f"\n--- \n\n"
    texto_presupuesto += f"## Presupuesto de Traducción \n\n"
    texto_presupuesto += f"El **costo base por la traducción** es de **${format_currency(costo_base_traduccion_total)} ARS**. Este monto es solo por mi trabajo de traducción y mi firma/sello (físico o digital), sin incluir ninguna tasa de legalización del Colegio de Traductores Públicos.\n\n"
    texto_presupuesto += f"Para confirmar el trabajo, te pido una **seña del 50% (${format_currency(sena)} ARS)** mediante transferencia bancaria.\n\n"
    texto_presupuesto += f"--- \n\n"
    texto_presupuesto += f"## Proceso y Opciones de Legalización \n\n"

    # La sección de legalización solo aplica para traducciones públicas.
    # Chequeamos si al menos UN documento es de tipo "Traducción Pública"
    hay_traduccion_publica = any(doc.get('tipo_traduccion') == "Traducción Pública" for doc in lista_documentos)

    if hay_traduccion_publica:
        # Usamos el domicilio ingresado por el usuario
        texto_presupuesto += f"Una vez que la traducción (o las traducciones públicas) estén listas, te voy a avisar. Si la legalización es presencial, vas a tener que acercarte a mi domicilio en **{domicilio_traductor}** con el **documento original**. Ahí mismo voy a **cosellar** y abrochar tu documento original a la traducción, que ya va a tener mi firma y sello. Este paso es fundamental para que sea una traducción pública válida.\n\n"
        texto_presupuesto += f"Para la **legalización**, que es la certificación del Colegio de Traductores Públicos (CTPCBA) que valida mi firma y matrícula, tenés estas opciones:\n\n"

        # Opción 1: Legalización Digital
        costo_total_digital = costo_base_traduccion_total + tasa_legalizacion_digital
        texto_presupuesto += f"### Opción 1: Legalización Digital \n\n"
        texto_presupuesto += f"* **Proceso:** Esta es una alternativa ágil si el destinatario del documento acepta este formato. Yo me encargo de todo el proceso y la legalización se emite en formato digital por el Colegio.\n"
        texto_presupuesto += f"* **Costo Total:** **${format_currency(costo_total_digital)} ARS**.\n" 

        texto_presupuesto += f"* Este monto incluye mis honorarios (${format_currency(costo_base_traduccion_total)} ARS) y la tasa por la legalización digital del Colegio (${format_currency(tasa_legalizacion_digital)} ARS).\n"

        if tasa_pagada_por_cliente == "Sí, que la pague el cliente":
            texto_presupuesto += f"* Vos vas a pagar la tasa de ${format_currency(tasa_legalizacion_digital)} ARS directamente al Colegio de Traductores a través de transferencia bancaria.\n"
        else:
            texto_presupuesto += f"* Yo me ocupo de gestionar y pagar la tasa de ${format_currency(tasa_legalizacion_digital)} ARS.\n"

        texto_presupuesto += f"* **Aclaración:** Con esta opción, no vas a necesitar acercarte a mi domicilio para entregar el original o retirar la traducción, ya que todo el proceso es digital.\n\n---\n\n"

        # Opción 2: Legalización Presencial gestionada por vos
        costo_total_presencial_vos = costo_base_traduccion_total + tasa_legalizacion_presencial
        texto_presupuesto += f"### Opción 2: Legalización Presencial gestionada por vos \n\n"
        texto_presupuesto += f"* **Proceso:** Yo te voy a entregar la traducción ya abrochada al original. Después, vos o la persona que designes, la van a tener que llevar a legalizar a la sede del Colegio en Av. Corrientes 1834 (atienden de lunes a viernes de 9 a 17 hs). El trámite se hace en el momento y no necesitás turno.\n"
        texto_presupuesto += f"* **Costo Total:** **${format_currency(costo_total_presencial_vos)} ARS**.\n" 

        texto_presupuesto += f"* Este monto incluye mis honorarios (${format_currency(costo_base_traduccion_total)} ARS) y la tasa de legalización del Colegio de ${format_currency(tasa_legalizacion_presencial)} ARS, que pagás directamente a ellos con tarjeta o transferencia.\n\n---\n\n"

        # Opción 3: Legalización Presencial gestionada por mí
        costo_total_presencial_mio = costo_base_traduccion_total + tasa_legalizacion_presencial + recargo_gestion_presencial
        texto_presupuesto += f"### Opción 3: Legalización Presencial gestionada por mí \n\n"
        texto_presupuesto += f"* **Proceso:** Si preferís que yo me ocupe de todo, vas a tener que acercarte a mi domicilio en dos ocasiones:\n"
        texto_presupuesto += f"    * La primera vez, para entregarme el documento original.\n" 
        texto_presupuesto += f"    * La segunda vez, para retirar el documento original junto con la traducción y la legalización del Colegio.\n" 
        texto_presupuesto += f"    * Yo mismo voy a llevar el documento a legalizar y te lo voy a entregar listo para que lo uses.\n" 
        texto_presupuesto += f"* **Costo Total:** **${format_currency(costo_total_presencial_mio)} ARS**.\n" 
        
        texto_presupuesto += f"* Este monto ya incluye mis honorarios, la tasa del Colegio y el recargo por la gestión.\n\n---\n\n"
    else: # Ninguna traducción pública, no aplica legalización del Colegio
        texto_presupuesto += f"Las traducciones sin carácter público no requieren legalización del Colegio de Traductores Públicos. Este presupuesto no incluye traducciones públicas.\n\n---\n\n"

    texto_presupuesto += f"Espero que esta información te sea útil para decidir cómo querés seguir. ¡Avisame cualquier consulta!"

    return texto_presupuesto

st.set_page_config(layout="wide")
st.title("Generador de Presupuestos de Traducción")

st.sidebar.header("Configuración del Presupuesto")

# Inicializar st.session_state para almacenar los documentos
if 'documentos' not in st.session_state:
    st.session_state.documentos = []

# Selector global del tipo de traducción (afecta los inputs del formulario)
tipo_traduccion_global = st.sidebar.radio(
    "Tipo de Traducción para el NUEVO documento a agregar:",
    ("Traducción Pública", "Traducción sin carácter público")
)

st.sidebar.subheader("Agregar Documentos")

# Opciones de idiomas disponibles
opciones_idioma = ["Español", "Inglés", "Alemán"]

# Opciones de tipo de documento para traducciones públicas
opciones_documento_publico = [
    "Partidas, pasaportes, certificados y demás documentos personales",
    "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación",
    "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar",
    "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención"
]

# Opciones de categoría para traducciones no públicas
opciones_categoria_no_publica = ["I", "II", "III", "IV", "V"]


with st.sidebar.form("form_agregar_documento"):
    nombre_referencia_nuevo = st.text_input("Nombre de referencia del documento (ej: 'Partida de Nacimiento', 'Contrato XYZ')")

    # Campos de idioma de origen y destino para cada documento
    idioma_origen_nuevo = st.selectbox("Idioma de origen:", opciones_idioma, key="origen_doc_form")
    idioma_destino_nuevo = st.selectbox("Idioma de destino:", opciones_idioma, key="destino_doc_form")

    if tipo_traduccion_global == "Traducción Pública":
        fojas_nuevo = st.number_input("Cantidad de fojas de este documento:", min_value=1.0, value=1.0, step=0.5)
        tipo_documento_nuevo = st.selectbox("Tipo de documento:", opciones_documento_publico)
        palabras_nuevo = None # No aplica
        categoria_idioma_no_publica_nuevo = None # No aplica
    else: # Traducción sin carácter público
        palabras_nuevo = st.number_input("Cantidad de palabras de este documento:", min_value=1, value=250, step=1)
        
        # Lógica para preseleccionar y deshabilitar la categoría según el idioma de destino
        # para "Al idioma extranjero" (Inglés/Alemán)
        default_categoria_no_publica = None
        disabled_categoria_no_publica = False

        # Solo aplicamos la preselección si la traducción es DESDE español HACIA otro idioma
        if idioma_origen_nuevo == "Español":
            if idioma_destino_nuevo == "Inglés":
                default_categoria_no_publica = "I"
                disabled_categoria_no_publica = True
            elif idioma_destino_nuevo == "Alemán":
                default_categoria_no_publica = "II"
                disabled_categoria_no_publica = True
        
        # Encontrar el índice de la opción por defecto para el selectbox
        default_index_no_publica = 0
        if default_categoria_no_publica:
            try:
                default_index_no_publica = opciones_categoria_no_publica.index(default_categoria_no_publica)
            except ValueError:
                default_index_no_publica = 0 # Si no se encuentra, vuelve al primero

        categoria_idioma_no_publica_nuevo = st.selectbox(
            "Categoría por idioma (I-V):", 
            opciones_categoria_no_publica, 
            index=default_index_no_publica, 
            disabled=disabled_categoria_no_publica
        )
        fojas_nuevo = None # No aplica
        tipo_documento_nuevo = None # No aplica


    col_add, col_clear = st.columns(2)
    with col_add:
        if st.form_submit_button("Agregar Documento"):
            # Validaciones de idioma de origen/destino
            if idioma_origen_nuevo == idioma_destino_nuevo:
                st.error("El idioma de origen no puede ser el mismo que el idioma de destino.")
            elif (idioma_origen_nuevo not in opciones_idioma) or \
                 (idioma_destino_nuevo not in opciones_idioma):
                 st.error("Por favor, seleccioná idiomas válidos (Español, Inglés, Alemán).")
            elif (idioma_origen_nuevo != "Español" and idioma_destino_nuevo != "Español" and tipo_traduccion_global == "Traducción Pública"):
                st.error("Las traducciones públicas solo están cotizadas para combinaciones desde/hacia el español con Inglés o Alemán.")
            elif nombre_referencia_nuevo and \
               ((tipo_traduccion_global == "Traducción Pública" and fojas_nuevo > 0) or \
                (tipo_traduccion_global == "Traducción sin carácter público" and palabras_nuevo > 0)):
                
                doc_data = {
                    'nombre_referencia': nombre_referencia_nuevo,
                    'tipo_traduccion': tipo_traduccion_global, # Guardamos el tipo de traducción con el documento
                    'idioma_origen': idioma_origen_nuevo,
                    'idioma_destino': idioma_destino_nuevo
                }
                if tipo_traduccion_global == "Traducción Pública":
                    doc_data['fojas'] = fojas_nuevo
                    doc_data['tipo_documento'] = tipo_documento_nuevo
                else: # Traducción sin carácter público
                    doc_data['palabras'] = palabras_nuevo
                    doc_data['categoria_idioma_no_publica'] = categoria_idioma_no_publica_nuevo

                st.session_state.documentos.append(doc_data)
                st.success(f"Documento '{nombre_referencia_nuevo}' agregado.")
            else:
                st.error("Por favor, ingresá un nombre de referencia y fojas/palabras válidas para el documento.")
    with col_clear:
        if st.form_submit_button("Limpiar todos los documentos"):
            st.session_state.documentos = []
            st.info("Lista de documentos limpiada.")


st.sidebar.subheader("Documentos Agregados:")
if st.session_state.documentos:
    for idx, doc in enumerate(st.session_state.documentos):
        # Asegurarse de que las claves existen antes de acceder a ellas
        nombre_ref_display = doc.get('nombre_referencia', 'Documento sin nombre')
        tipo_traduccion_display = doc.get('tipo_traduccion', 'Tipo Desconocido')
        idioma_origen_display = doc.get('idioma_origen', 'N/A')
        idioma_destino_display = doc.get('idioma_destino', 'N/A')
        
        idioma_str = f"{idioma_origen_display} > {idioma_destino_display}"

        if tipo_traduccion_display == "Traducción Pública":
            fojas_display = doc.get('fojas', 'N/A')
            tipo_documento_display = doc.get('tipo_documento', 'N/A')
            st.sidebar.write(f"{idx+1}. **{nombre_ref_display}** ({idioma_str}, {fojas_display} fojas, {tipo_documento_display})")
        else:
            palabras_display = doc.get('palabras', 'N/A')
            categoria_display = doc.get('categoria_idioma_no_publica', 'N/A')
            st.sidebar.write(f"{idx+1}. **{nombre_ref_display}** ({idioma_str}, {palabras_display} palabras, Cat. {categoria_display})")
else:
    st.sidebar.write("No hay documentos agregados.")


st.sidebar.markdown("---") # Separador visual

# Nuevo campo para que el usuario ingrese el domicilio
domicilio_traductor = st.sidebar.text_input(
    "Tu domicilio para retiro/entrega de documentos:",
    value="Microcentro" # Valor por defecto
)

# Las opciones de legalización solo se muestran si hay al menos una traducción pública agregada
hay_traduccion_publica_en_lista = any(doc.get('tipo_traduccion') == "Traducción Pública" for doc in st.session_state.documentos)

tipo_legalizacion = None
tasa_pagada_por_cliente = None

if hay_traduccion_publica_en_lista:
    st.sidebar.markdown("### Opciones de Legalización (Para traducciones públicas)")
    tipo_legalizacion = st.sidebar.selectbox(
        "¿Qué tipo de legalización preferís?",
        ("Digital", "Presencial gestionada por vos", "Presencial gestionada por mí")
    )

    if tipo_legalizacion == "Digital":
        tasa_pagada_por_cliente = st.sidebar.radio(
            "¿Quién paga la tasa de legalización digital del Colegio?",
            ("No, que la gestione el traductor", "Sí, que la pague el cliente")
        )

if st.sidebar.button("Generar Presupuesto"):
    presupuesto_generado = generar_presupuesto(st.session_state.documentos, tasa_pagada_por_cliente, domicilio_traductor)
    if presupuesto_generado: # Solo si no hubo un warning por falta de documentos
        st.markdown(presupuesto_generado)

        st.download_button(
            label="Descargar Presupuesto (TXT)",
            data=presupuesto_generado,
            file_name="presupuesto_traduccion.txt",
            mime="text/plain"
        )

st.markdown("---")
st.markdown("### Notas:")
st.markdown("- Los precios por foja para traducciones públicas se basan en la tabla provista, considerando la dirección de la traducción (Al español / Al idioma extranjero) y la categoría I (Inglés) o II (Alemán).")
st.markdown("- Las combinaciones de idioma para traducciones públicas están limitadas a aquellas desde/hacia el español con Inglés o Alemán, según la tabla de precios provista.")
st.markdown("- Los aranceles por palabra para traducciones sin carácter público se basan en la tabla provista, con un mínimo de 250 palabras y la categoría de idioma seleccionada/inferida. La categoría se preselecciona para traducciones desde español a inglés (Cat. I) o alemán (Cat. II).")
st.markdown("- Las tasas de legalización son fijas y pueden variar según el Colegio. Solo aplican para traducciones públicas, y se mostrarán las opciones si al menos un documento agregado es de tipo público.")
st.markdown("- Recordá que los precios deben ser ajustados a tus tarifas reales y a las actualizaciones del Colegio.")
