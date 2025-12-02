# Flujo de Procesamiento de Reportes Lighthouse

## Descripción General

El sistema implementa un flujo de 3 etapas para procesar reportes de Google Lighthouse antes de enviarlos al modelo LLM principal, optimizando el uso de tokens y mejorando la eficiencia.

## Etapas del Procesamiento

### 1. Preprocesamiento (`preprocess_lighthouse_report()`)

**Objetivo**: Reducir el tamaño del JSON eliminando datos innecesarios.

**Proceso**:
- Mantiene solo campos esenciales:
  - `categories.*.score`, `title`, `description`
  - `audits.*.score`, `title`, `description`, `displayValue`, `numericValue`
  - `audits.*.details.summary` (sin los arrays de items completos)
  - Métricas principales: `finalUrl`, `requestedUrl`, `timing`, `configSettings`

- Elimina:
  - Arrays grandes: `audits.*.details.items`
  - Screenshots: `full-page-screenshot`, `screenshot`
  - Datos de tracing: `trace`, `traces`
  - Requests de red completos
  - Cualquier string > 5000 caracteres

**Reducción esperada**: 20-95% dependiendo del tamaño original del reporte

### 2. Resumen con LLM (`summarize_preprocessed_report()`)

**Objetivo**: Convertir el JSON preprocesado en un resumen en lenguaje natural conciso.

**Proceso**:
1. Convierte el JSON preprocesado a texto
2. Divide el texto en chunks de 3000 caracteres máximo
3. Cada chunk se envía a `llama-3.1-8b-instant` con el prompt:
   ```
   Resume este fragmento del reporte de Lighthouse manteniendo solo:
   - problemas principales
   - métricas clave (performance, SEO, accesibilidad)
   - oportunidades de mejora
   - puntuaciones relevantes
   Máximo 800 tokens.
   ```
4. Si hay múltiples chunks:
   - Combina los resúmenes parciales
   - Si el combinado > 15000 caracteres (~5000 tokens), hace una fusión final
   - Prompt de fusión limita el resultado a 1500 tokens

**Modelo usado**: `llama-3.1-8b-instant` (rápido y económico)

**Temperatura**: 0.3 (más determinista para resúmenes consistentes)

**Salida**: Texto en lenguaje natural < 5000 tokens

### 3. Análisis Final (`get_model_response()`)

**Objetivo**: Responder las preguntas del usuario usando el resumen del reporte.

**Proceso**:
1. Recibe el resumen en texto (no el JSON)
2. Lo incluye en el system prompt del modelo principal
3. El modelo `llama-3.3-70b-versatile` responde con el resumen como contexto

**Modelo usado**: `llama-3.3-70b-versatile` (modelo principal, más capaz)

**Ventajas**:
- Contexto mucho más pequeño (resumen vs JSON completo)
- Información ya filtrada y organizada
- El modelo grande puede enfocarse en dar respuestas de calidad

## Ventajas del Flujo

1. **Reducción de tokens**: Procesamiento en 2 fases reduce tokens enviados al modelo principal
2. **Optimización de costos**: Usa modelo pequeño (8b-instant) para tareas de resumen
3. **Mejor calidad**: El modelo grande recibe información pre-procesada y estructurada
4. **Escalabilidad**: Puede procesar reportes muy grandes dividiéndolos en chunks
5. **Robustez**: Manejo de errores con fallback a información básica

## Ejemplo de Reducción

```
Reporte Original:        2.5 MB (JSON con screenshots, traces, items)
         ↓ (preprocesamiento)
Reporte Preprocesado:    250 KB (JSON sin datos innecesarios)
         ↓ (resumen con 8b-instant)
Resumen Final:           ~5 KB (texto en lenguaje natural)
         ↓ (contexto para 70b-versatile)
Respuesta al Usuario:    Análisis experto basado en resumen conciso
```

## Configuración de Modelos

### llama-3.1-8b-instant (Resumen)
- **Temperature**: 0.3
- **Max tokens**: 800 por chunk, 1500 para fusión final
- **Uso**: Procesamiento intermedio, resúmenes

### llama-3.3-70b-versatile (Análisis)
- **Temperature**: 0.7
- **Max tokens**: 2000
- **Uso**: Respuestas finales al usuario

## Manejo de Errores

Si la función `summarize_preprocessed_report()` falla:
- Captura la excepción
- Devuelve un resumen básico con las puntuaciones de categorías
- Permite que la aplicación continúe funcionando con información limitada

## Notas de Implementación

- La división en chunks de 3000 caracteres es conservadora para asegurar que caben en el contexto del modelo 8b
- El límite de 15000 caracteres (~5000 tokens) para el resumen combinado está diseñado para no exceder límites de contexto
- El sistema es idempotente: múltiples llamadas con el mismo reporte producen resúmenes similares
