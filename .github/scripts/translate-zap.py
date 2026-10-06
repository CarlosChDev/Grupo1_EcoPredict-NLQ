import json
import sys
from pathlib import Path
from html import unescape
import re


def clean_html(text):
    if not text:
        return ""

    text = unescape(text)
    return re.sub(r"<[^>]+>", "", text).strip()


# Traducciones opcionales de alertas conocidas de OWASP ZAP.
#
# Si aparece una alerta que no está definida aquí,
# se conserva automáticamente el texto original de ZAP.
TRANSLATIONS = {
    "CSP: Failure to Define Directive with No Fallback": {
        "name": "Fallo al definir una directiva CSP sin mecanismo de respaldo",
        "description": (
            "La política Content Security Policy contiene directivas que "
            "no tienen un mecanismo de respaldo mediante default-src. "
            "Se debe revisar la política CSP y definir explícitamente "
            "las directivas necesarias."
        ),
        "solution": (
            "Revisar la política Content Security Policy y configurar "
            "explícitamente las directivas que no utilizan default-src "
            "como mecanismo de respaldo."
        ),
    },

    "Content Security Policy (CSP) Header Not Set": {
        "name": "Cabecera Content Security Policy (CSP) no configurada",
        "description": (
            "La aplicación no define una cabecera Content Security Policy "
            "(CSP). Se recomienda configurar una política CSP adecuada "
            "para restringir los recursos que pueden ser cargados por "
            "la aplicación y reducir el riesgo de ataques como "
            "Cross-Site Scripting (XSS)."
        ),
        "solution": (
            "Configurar una política Content Security Policy adecuada "
            "para la aplicación y definir las directivas necesarias "
            "según los recursos que utiliza."
        ),
    },

    "Missing Anti-clickjacking Header": {
        "name": "Falta la cabecera de protección contra Clickjacking",
        "description": (
            "Los navegadores web modernos admiten las cabeceras HTTP "
            "Content-Security-Policy y X-Frame-Options. Se debe asegurar "
            "que al menos una de ellas esté configurada en todas las "
            "páginas devueltas por la aplicación. Si la página debe ser "
            "cargada únicamente por páginas del propio servidor, se puede "
            "utilizar SAMEORIGIN. Si no debe ser cargada dentro de un "
            "frame, se puede utilizar DENY. Como alternativa, se puede "
            "implementar la directiva frame-ancestors de Content "
            "Security Policy."
        ),
        "solution": (
            "Configurar la cabecera X-Frame-Options o la directiva "
            "frame-ancestors de Content Security Policy para evitar "
            "ataques de Clickjacking."
        ),
    },

    "Cross-Origin-Embedder-Policy Header Missing or Invalid": {
        "name": "Cabecera Cross-Origin-Embedder-Policy ausente o no válida",
        "description": (
            "La aplicación no presenta una cabecera Cross-Origin-Embedder-Policy "
            "válida. Se recomienda revisar la configuración de esta "
            "cabecera para establecer las políticas de aislamiento "
            "entre recursos de diferentes orígenes."
        ),
        "solution": (
            "Revisar y configurar la cabecera Cross-Origin-Embedder-Policy "
            "según los requisitos de aislamiento de la aplicación."
        ),
    },

    "Cross-Origin-Opener-Policy Header Missing or Invalid": {
        "name": "Cabecera Cross-Origin-Opener-Policy ausente o no válida",
        "description": (
            "La aplicación no presenta una cabecera Cross-Origin-Opener-Policy "
            "válida. Esta política permite controlar el aislamiento entre "
            "la ventana de la aplicación y documentos de otros orígenes."
        ),
        "solution": (
            "Revisar y configurar la cabecera Cross-Origin-Opener-Policy "
            "según los requisitos de seguridad y aislamiento de la aplicación."
        ),
    },

    "Cross-Origin-Resource-Policy Header Missing or Invalid": {
        "name": "Cabecera Cross-Origin-Resource-Policy ausente o no válida",
        "description": (
            "La aplicación no presenta una cabecera Cross-Origin-Resource-Policy "
            "válida. Esta política permite controlar qué recursos pueden "
            "ser cargados desde diferentes orígenes."
        ),
        "solution": (
            "Revisar y configurar la cabecera Cross-Origin-Resource-Policy "
            "según los requisitos de seguridad y acceso entre orígenes "
            "de la aplicación."
        ),
    },

    "Permissions Policy Header Not Set": {
        "name": "Cabecera Permissions Policy no configurada",
        "description": (
            "La aplicación no define una cabecera Permissions Policy. "
            "Se recomienda configurar esta política para controlar qué "
            "funcionalidades del navegador pueden utilizar las páginas "
            "de la aplicación."
        ),
        "solution": (
            "Configurar una cabecera Permissions Policy que limite las "
            "funcionalidades del navegador que pueden utilizar las páginas "
            "de la aplicación."
        ),
    },

    "Timestamp Disclosure - Unix": {
        "name": "Divulgación de marcas de tiempo Unix",
        "description": (
            "La aplicación expone marcas de tiempo en formato Unix que "
            "pueden proporcionar información sobre las fechas asociadas "
            "a determinados recursos. Se recomienda revisar si esta "
            "información es necesaria y evitar la exposición de datos "
            "temporales que no sean requeridos."
        ),
        "solution": (
            "Revisar si las marcas de tiempo expuestas son necesarias y, "
            "cuando sea posible, evitar la divulgación de información "
            "temporal que no sea necesaria para el funcionamiento de "
            "la aplicación."
        ),
    },

    "X-Content-Type-Options Header Missing": {
        "name": "Cabecera X-Content-Type-Options no configurada",
        "description": (
            "La respuesta no incluye la cabecera X-Content-Type-Options. "
            "Se recomienda configurar esta cabecera con el valor nosniff "
            "para evitar que los navegadores intenten interpretar el "
            "contenido utilizando un tipo MIME diferente al declarado."
        ),
        "solution": (
            "Configurar la cabecera X-Content-Type-Options con el valor "
            "nosniff para evitar la interpretación del contenido utilizando "
            "un tipo MIME diferente al declarado."
        ),
    },

    "Information Disclosure - Suspicious Comments": {
        "name": "Divulgación de información mediante comentarios sospechosos",
        "description": (
            "Se identificaron comentarios sospechosos dentro de los "
            "recursos de la aplicación. Estos comentarios pueden contener "
            "información útil para comprender la estructura o lógica "
            "interna de la aplicación. Se recomienda revisarlos y eliminar "
            "aquellos que expongan información innecesaria."
        ),
        "solution": (
            "Revisar los comentarios identificados y eliminar aquellos "
            "que contengan información sensible, innecesaria o que pueda "
            "facilitar el análisis de la aplicación."
        ),
    },

    "Modern Web Application": {
        "name": "Aplicación web moderna",
        "description": (
            "La aplicación presenta características de una aplicación "
            "web moderna. Este resultado es informativo y no representa "
            "por sí mismo una vulnerabilidad de seguridad."
        ),
        "solution": (
            "Este resultado es informativo. No se requiere ninguna "
            "acción específica."
        ),
    },

    "Storable and Cacheable Content": {
        "name": "Contenido almacenable y susceptible de caché",
        "description": (
            "La aplicación permite almacenar contenido en caché. Si el "
            "contenido contiene información sensible, personal o específica "
            "de un usuario, podría existir riesgo de exposición mediante "
            "mecanismos de almacenamiento en caché. Se recomienda verificar "
            "la sensibilidad del contenido y utilizar directivas adecuadas "
            "de Cache-Control cuando sea necesario."
        ),
        "solution": (
            "Verificar si el contenido almacenado en caché contiene "
            "información sensible, personal o específica de un usuario. "
            "Cuando sea necesario, utilizar directivas Cache-Control como "
            "no-cache, no-store o private."
        ),
    },
}


def main():
    if len(sys.argv) != 3:
        print(
            "Uso: python translate-zap.py "
            "<entrada.json> <salida.json>"
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    with input_file.open("r", encoding="utf-8") as file:
        report = json.load(file)

    translated_count = 0
    total_alerts = 0

    for site in report.get("site", []):
        for alert in site.get("alerts", []):
            total_alerts += 1

            original_name = alert.get(
                "name",
                "OWASP ZAP Alert"
            )

            translation = TRANSLATIONS.get(original_name)

            if translation:
                alert["name"] = translation.get(
                    "name",
                    original_name
                )

                if "description" in translation:
                    alert["desc"] = translation["description"]

                if "solution" in translation:
                    alert["solution"] = translation["solution"]

                translated_count += 1

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"JSON traducido correctamente: {output_file}"
    )

    print(
        f"Alertas procesadas: {total_alerts}"
    )

    print(
        f"Alertas traducidas: {translated_count}"
    )

    print(
        f"Alertas sin traducción: "
        f"{total_alerts - translated_count}"
    )


if __name__ == "__main__":
    main()