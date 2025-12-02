import os
import json
from typing import Any
from groq import Groq
from .prompts import SYSTEM_PROMPT


def preprocess_lighthouse_report(report: dict) -> dict:
    """
    Reduce el tamaño del reporte de Lighthouse manteniendo solo la información esencial.

    Mantiene:
    - categories.*.score
    - audits.*.score, title, description, displayValue
    - audits.*.details.summary (si existe)
    - Métricas principales: runtimeError, configSettings, timing, finalUrl, requestedUrl

    Elimina:
    - audits.*.details.items (arrays grandes de datos)
    - full-page-screenshot
    - traces
    - network-requests completos
    - Cualquier valor cuya longitud como string supere 5000 caracteres
    """
    processed = {}

    # Campos principales a mantener directamente
    top_level_fields = [
        "finalUrl",
        "requestedUrl",
        "fetchTime",
        "userAgent",
        "environment",
        "runtimeError",
        "timing",
    ]

    for field in top_level_fields:
        if field in report:
            processed[field] = report[field]

    # Procesar configSettings (mantener solo configuración básica)
    if "configSettings" in report:
        config = report["configSettings"]
        processed["configSettings"] = {
            "emulatedFormFactor": config.get("emulatedFormFactor"),
            "locale": config.get("locale"),
            "onlyCategories": config.get("onlyCategories"),
        }

    # Procesar categories (mantener scores y títulos)
    if "categories" in report:
        processed["categories"] = {}
        for category_id, category_data in report["categories"].items():
            processed["categories"][category_id] = {
                "id": category_data.get("id"),
                "title": category_data.get("title"),
                "score": category_data.get("score"),
                "description": category_data.get("description"),
            }

    # Procesar audits (mantener solo información esencial)
    if "audits" in report:
        processed["audits"] = {}
        for audit_id, audit_data in report["audits"].items():
            processed_audit = {
                "id": audit_data.get("id"),
                "title": audit_data.get("title"),
                "description": audit_data.get("description"),
                "score": audit_data.get("score"),
                "scoreDisplayMode": audit_data.get("scoreDisplayMode"),
                "displayValue": audit_data.get("displayValue"),
                "numericValue": audit_data.get("numericValue"),
                "numericUnit": audit_data.get("numericUnit"),
            }

            # Mantener solo el summary de details, NO los items completos
            if "details" in audit_data and isinstance(audit_data["details"], dict):
                details = audit_data["details"]
                processed_details = {}

                # Mantener summary si existe
                if "summary" in details:
                    processed_details["summary"] = details["summary"]

                # Mantener type para contexto
                if "type" in details:
                    processed_details["type"] = details["type"]

                # Si hay items, solo contar cuántos hay, no incluir el array completo
                if "items" in details and isinstance(details["items"], list):
                    processed_details["itemsCount"] = len(details["items"])

                if processed_details:
                    processed_audit["details"] = processed_details

            processed["audits"][audit_id] = processed_audit

    # Eliminar cualquier valor que sea demasiado largo
    processed = _remove_large_values(processed, max_length=5000)

    return processed


def _remove_large_values(obj: Any, max_length: int = 5000) -> Any:
    """
    Recursivamente elimina valores cuya representación en string supere max_length.
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Saltar campos que sabemos que son grandes
            if key in [
                "full-page-screenshot",
                "screenshot",
                "screenshots",
                "trace",
                "traces",
                "network-requests",
                "items",  # Ya manejamos items en preprocess
            ]:
                continue

            processed_value = _remove_large_values(value, max_length)

            # Verificar si el valor procesado es demasiado grande
            if isinstance(processed_value, str) and len(processed_value) > max_length:
                result[key] = f"[Valor muy largo - {len(processed_value)} caracteres]"
            elif processed_value is not None:
                result[key] = processed_value

        return result
    elif isinstance(obj, list):
        return [_remove_large_values(item, max_length) for item in obj]
    elif isinstance(obj, str):
        if len(obj) > max_length:
            return f"[Texto muy largo - {len(obj)} caracteres]"
        return obj
    else:
        return obj


def summarize_preprocessed_report(preprocessed: dict) -> str:
    """
    Resume un reporte preprocesado de Lighthouse en texto conciso.

    1. Convierte el JSON preprocesado a texto
    2. Lo divide en trozos de máximo 3000 caracteres
    3. Envía cada trozo al modelo llama-3.1-8b-instant para resumir
    4. Fusiona los resúmenes en un texto final < 5000 tokens

    Returns:
        str: Resumen en texto del reporte para usar como contexto
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Convertir el JSON preprocesado a texto legible
        report_text = json.dumps(preprocessed, indent=2, ensure_ascii=False)

        # Dividir en trozos de máximo 3000 caracteres
        chunk_size = 3000
        chunks = []
        for i in range(0, len(report_text), chunk_size):
            chunks.append(report_text[i : i + chunk_size])

        # Prompt para resumir cada trozo
        summary_prompt = """Resume este fragmento del reporte de Lighthouse manteniendo solo:
- problemas principales
- métricas clave (performance, SEO, accesibilidad)
- oportunidades de mejora
- puntuaciones relevantes
Máximo 800 tokens."""

        # Resumir cada trozo con el modelo pequeño
        chunk_summaries = []
        for idx, chunk in enumerate(chunks):
            messages = [
                {"role": "system", "content": summary_prompt},
                {
                    "role": "user",
                    "content": f"Fragmento {idx + 1} de {len(chunks)}:\n\n{chunk}",
                },
            ]

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.3,
                max_tokens=800,
                top_p=1,
                stream=False,
            )

            chunk_summaries.append(response.choices[0].message.content)

        # Si hay múltiples resúmenes, fusionarlos
        if len(chunk_summaries) == 1:
            final_summary = chunk_summaries[0]
        else:
            # Fusionar todos los resúmenes
            combined_summaries = "\n\n---\n\n".join(chunk_summaries)

            # Si el combinado es muy largo, hacer un resumen final
            if len(combined_summaries) > 15000:  # ~5000 tokens aproximadamente
                fusion_prompt = """Fusiona estos resúmenes del reporte de Lighthouse en un solo resumen coherente.
Mantén:
- Todas las puntuaciones de categorías principales
- Problemas críticos identificados
- Métricas clave de rendimiento
- Oportunidades de mejora más importantes
Máximo 1500 tokens."""

                messages = [
                    {"role": "system", "content": fusion_prompt},
                    {"role": "user", "content": combined_summaries},
                ]

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1500,
                    top_p=1,
                    stream=False,
                )

                final_summary = response.choices[0].message.content
            else:
                final_summary = combined_summaries

        return final_summary

    except Exception as e:
        # Si falla el resumen, devolver una representación básica
        categories_info = ""
        if "categories" in preprocessed:
            categories_info = "\n\nCategorías:\n"
            for cat_id, cat_data in preprocessed["categories"].items():
                score = cat_data.get("score", 0) * 100
                title = cat_data.get("title", cat_id)
                categories_info += f"- {title}: {score:.0f}/100\n"

        return f"Error al resumir reporte: {str(e)}\n\nInformación básica:{categories_info}"


def get_model_response(messages: list[dict], lighthouse_reports: dict = None, temperature: float = 0.7) -> str:
    try:
        # Debug: imprimir temperatura recibida
        print(f"[DEBUG] Temperatura recibida en get_model_response: {temperature}")

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        system_message = {"role": "system", "content": SYSTEM_PROMPT}

        # Si hay reportes cargados, preprocesarlos, resumirlos e incluirlos en el contexto
        if lighthouse_reports:
            reports_context = "\n\n## REPORTES LIGHTHOUSE DISPONIBLES\n\n"
            reports_context += (
                "El usuario ha cargado los siguientes reportes de Google Lighthouse. "
                "A continuación se presenta un resumen de cada reporte:\n\n"
            )

            for file_name, report_data in lighthouse_reports.items():
                # Preprocesar el reporte para reducir su tamaño
                processed_report = preprocess_lighthouse_report(report_data)

                # Generar resumen del reporte preprocesado
                summary = summarize_preprocessed_report(processed_report)

                reports_context += f"### Reporte: {file_name}\n\n"
                reports_context += summary
                reports_context += "\n\n---\n\n"

            reports_context += (
                "\nUsa estos resúmenes para responder las preguntas del usuario. "
                "Si el usuario hace una pregunta que requiere análisis de un reporte "
                "y ya tienes reportes cargados, analízalos automáticamente. "
                "Si el usuario pregunta algo que no requiere un reporte específico, "
                "responde normalmente con tus conocimientos sobre optimización web.\n\n"
                "NOTA: Los resúmenes incluyen las métricas clave, problemas principales "
                "y oportunidades de mejora identificadas en los reportes."
            )

            # Agregar contexto de reportes al system prompt
            enhanced_system_prompt = SYSTEM_PROMPT + "\n\n" + reports_context
            system_message = {"role": "system", "content": enhanced_system_prompt}

        all_messages = [system_message] + messages

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=all_messages,
            temperature=temperature,
            max_tokens=2000,
            top_p=1,
            stream=False,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Lo siento, ha ocurrido un error al procesar tu solicitud: {str(e)}"
