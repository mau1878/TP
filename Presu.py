import streamlit as st

def generar_presupuesto(fojas, idioma, tipo_documento, tipo_legalizacion, tasa_pagada_por_cliente):
    # Precios por foja, anidados por idioma y luego por tipo de documento
    precios_por_foja = {
        "Alemán": { # Corresponde a la Columna II
            "Partidas, pasaportes, certificados y demás documentos personales": 67800,
            "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación": 81700,
            "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar": 89000,
            "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención": 96800,
        },
        "Inglés": { # Corresponde a la Columna I
            "Partidas, pasaportes, certificados y demás documentos personales": 60800,
            "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación": 69700,
            "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar": 74400,
            "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención": 80800,
        }
    }

    costo_por_foja_actual = precios_por_foja.get(idioma, {}).get(tipo_documento, 0)
    costo_base_traduccion = fojas * costo_por_foja_actual

    tasa_legalizacion_digital = 21000
    tasa_legalizacion_presencial = 24000
    recargo_gestion_presencial = 24000 # Diferencia entre 270.500 y (222.500 + 24.000)

    # Seña
    sena = costo_base_traduccion * 0.5

    texto_presupuesto = f"¡Hola!\n\n"
    texto_presupuesto += f"Necesitás una **traducción pública al {idioma.lower()}** de tu documento \"{tipo_documento}\" ({fojas} fojas).\n\n"
    texto_presupuesto += f"--- \n\n"
    texto_presupuesto += f"## Presupuesto de Traducción Pública al {idioma} \n\n"
    texto_presupuesto += f"El **costo base por la traducción** es de **${costo_base_traduccion:,.0f}**. Este monto es solo por mi trabajo de traducción y mi firma/sello (físico o digital), sin incluir ninguna tasa de legalización del Colegio de Traductores Públicos.\n\n"
    texto_presupuesto += f"Para confirmar el trabajo, te pido una **seña del 50% (${sena:,.0f})** mediante transferencia bancaria.\n\n"
    texto_presupuesto += f"--- \n\n"
    texto_presupuesto += f"## Proceso y Opciones de Legalización \n\n"
    texto_presupuesto += f"Una vez que la traducción esté lista, te voy a avisar. Si la legalización es presencial, vas a tener que acercarte a mi domicilio en Recoleta (zona Alto Palermo) con el **documento original**. Ahí mismo voy a **cosellar** y abrochar tu documento original a la traducción, que ya va a tener mi firma y sello. Este paso es fundamental para que sea una traducción pública válida.\n\n"
    texto_presupuesto += f"Para la **legalización**, que es la certificación del Colegio de Traductores Públicos (CTPCBA) que valida mi firma y matrícula, tenés estas opciones:\n\n"

    # Opción 1: Legalización Digital
    costo_total_digital = costo_base_traduccion + tasa_legalizacion_digital
    texto_presupuesto += f"### Opción 1: Legalización Digital \n\n"
    texto_presupuesto += f"* **Proceso:** Esta es una alternativa ágil si el destinatario del documento acepta este formato. Yo me encargo de todo el proceso y la legalización se emite en formato digital por el Colegio.\n"
    texto_presupuesto += f"* **Costo Total:** **${costo_total_digital:,.0f}**. Este monto incluye mis honorarios (${costo_base_traduccion:,.0f}) y la tasa por la legalización digital del Colegio (${tasa_legalizacion_digital:,.0f}). "

    if tasa_pagada_por_cliente == "Sí, que la pague el cliente":
        texto_presupuesto += f"Vos vas a pagar la tasa de ${tasa_legalizacion_digital:,.0f} directamente al Colegio de Traductores a través de transferencia bancaria.\n"
    else:
        texto_presupuesto += f"Yo me ocupo de gestionar y pagar la tasa de ${tasa_legalizacion_digital:,.0f}.\n"

    texto_presupuesto += f"* **Aclaración:** Con esta opción, no vas a necesitar acercarte a mi domicilio para entregar el original o retirar la traducción, ya que todo el proceso es digital.\n\n---\n\n"

    # Opción 2: Legalización Presencial gestionada por vos
    costo_total_presencial_vos = costo_base_traduccion + tasa_legalizacion_presencial
    texto_presupuesto += f"### Opción 2: Legalización Presencial gestionada por vos \n\n"
    texto_presupuesto += f"* **Proceso:** Yo te voy a entregar la traducción ya abrochada al original. Después, vos o la persona que designes, la van a tener que llevar a legalizar a la sede del Colegio en Av. Corrientes 1834 (atienden de lunes a viernes de 9 a 17 hs). El trámite se hace en el momento y no necesitás turno.\n"
    texto_presupuesto += f"* **Costo Total:** **${costo_total_presencial_vos:,.0f}** (mis honorarios de ${costo_base_traduccion:,.0f} **+** la tasa de legalización del Colegio de ${tasa_legalizacion_presencial:,.0f}, que pagás directamente a ellos con tarjeta o transferencia).\n\n---\n\n"

    # Opción 3: Legalización Presencial gestionada por mí
    costo_total_presencial_mio = costo_base_traduccion + tasa_legalizacion_presencial + recargo_gestion_presencial
    texto_presupuesto += f"### Opción 3: Legalización Presencial gestionada por mí \n\n"
    texto_presupuesto += f"* **Proceso:** Si preferís que yo me ocupe de todo, vas a tener que acercarte a mi domicilio en dos ocasiones:\n"
    texto_presupuesto += f"    1. La primera vez, para entregarme el documento original.\n"
    texto_presupuesto += f"    2. La segunda vez, para retirar el documento original junto con la traducción y la legalización del Colegio.\n"
    texto_presupuesto += f"    Yo mismo voy a llevar el documento a legalizar y te lo voy a entregar listo para que lo uses.\n"
    texto_presupuesto += f"* **Costo Total:** **${costo_total_presencial_mio:,.0f}**. Este monto ya incluye mis honorarios, la tasa del Colegio y el recargo por la gestión.\n\n---\n\n"

    texto_presupuesto += f"Espero que esta información te sea útil para decidir cómo querés seguir. ¡Avisame cualquier consulta!"

    return texto_presupuesto

st.set_page_config(layout="wide")
st.title("Generador de Presupuestos de Traducción Pública")

st.sidebar.header("Configuración del Presupuesto")
fojas = st.sidebar.number_input("Cantidad de fojas del documento:", min_value=1.0, value=2.5, step=0.5)

# Selector de Idioma
idioma = st.sidebar.selectbox(
    "Idioma de la traducción:",
    ("Alemán", "Inglés")
)

# Opciones de tipo de documento basadas en la tabla
opciones_documento = [
    "Partidas, pasaportes, certificados y demás documentos personales",
    "Programas de estudios, certificados analíticos, diplomas y demás documentos relacionados con la educación",
    "Poderes, escrituras, testamentos, actas y demás documentos notariales; sentencias, expedientes judiciales, exhortos, oficios y demás documentos de índole similar",
    "Papeles de comercio, contratos, balances, estatutos, actas de asamblea/directorio y demás documentos societarios; estudios y documentos técnicos y científicos; patentes de invención"
]
tipo_documento = st.sidebar.selectbox("Tipo de documento:", opciones_documento, index=0) # Index 0 selecciona la primera opción por defecto

tipo_legalizacion = st.sidebar.selectbox(
    "¿Qué tipo de legalización preferís?",
    ("Digital", "Presencial gestionada por vos", "Presencial gestionada por mí")
)

tasa_pagada_por_cliente = None
if tipo_legalizacion == "Digital":
    tasa_pagada_por_cliente = st.sidebar.radio(
        "¿Quién paga la tasa de legalización digital del Colegio?",
        ("No, que la gestione el traductor", "Sí, que la pague el cliente")
    )

if st.sidebar.button("Generar Presupuesto"):
    presupuesto_generado = generar_presupuesto(fojas, idioma, tipo_documento, tipo_legalizacion, tasa_pagada_por_cliente)
    st.markdown(presupuesto_generado)

    st.download_button(
        label="Descargar Presupuesto (TXT)",
        data=presupuesto_generado,
        file_name="presupuesto_traduccion.txt",
        mime="text/plain"
    )

st.markdown("---")
st.markdown("### Notas:")
st.markdown("- Los precios por foja corresponden a las Categorías I (Inglés) y II (Alemán) de la tabla provista.")
st.markdown("- Las tasas de legalización son fijas y pueden variar según el Colegio.")
st.markdown("- Recordá que los precios deben ser ajustados a tus tarifas reales y a las actualizaciones del Colegio.")
