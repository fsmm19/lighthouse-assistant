# Lighthouse Assistant

Asistente experto especializado en análisis y optimización web basado en Google Lighthouse, potenciado por IA.

## Descripción

Lighthouse Assistant es una aplicación interactiva que te ayuda a analizar y mejorar el rendimiento de tus sitios web. Utiliza inteligencia artificial (Groq/LLaMA 3.3) para proporcionar recomendaciones expertas sobre:

- **Rendimiento Web** (Performance) - Core Web Vitals, optimización de recursos
- **Accesibilidad** (Accessibility) - WCAG 2.1, navegación por teclado, ARIA
- **Mejores prácticas** (Best practices) - Seguridad, validación, estructura de código
- **SEO** - Meta tags, structured data, optimización para motores de búsqueda
- **PWA** - Progressive Web Apps, Service Workers, funcionalidad offline

## Características

- Análisis detallado de reportes de Google Lighthouse en formato JSON
- Interfaz de chat interactiva para consultas sobre optimización web
- Explicaciones técnicas claras y accionables
- Recomendaciones priorizadas por impacto
- Enlaces a documentación oficial y recursos útiles

## Tecnologías

- **Python 3.13+**
- **uv** - Gestor de dependencias y entornos virtuales ultrarrápido
- **Streamlit** - Framework para la interfaz web
- **Groq API** - Modelo LLaMA 3.3 70B Versatile
- **python-dotenv** - Gestión de variables de entorno

## Instalación

### Prerrequisitos

- Python 3.13 o superior
- [uv](https://docs.astral.sh/uv/) - Instalación: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Cuenta en [Groq](https://console.groq.com/) para obtener una API key

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd lighthouse-assistant
   ```

2. **Crear entorno virtual e instalar dependencias**
   ```bash
   uv sync
   ```
   
   Esto creará automáticamente un entorno virtual y instalará todas las dependencias del proyecto.

3. **Configurar variables de entorno**
   
   Crear un archivo `.env` en la raíz del proyecto:
   ```env
   GROQ_API_KEY=<your_api_key_here>
   ```

## Uso

### Ejecutar la aplicación

```bash
uv run streamlit run app/main.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

> **Nota**: `uv run` ejecuta el comando en el entorno virtual gestionado por uv automáticamente.

### Ejemplos de uso

1. **Análisis de reportes Lighthouse**
   - Pega el JSON de un reporte de Google Lighthouse
   - Recibe análisis detallado con recomendaciones priorizadas

2. **Consultas sobre optimización**
   - "¿Cómo mejorar mi LCP?"
   - "¿Qué es el CLS y cómo optimizarlo?"
   - "¿Cómo implementar lazy loading de imágenes?"

3. **Mejores prácticas**
   - "¿Cómo implementar un Service Worker?"
   - "¿Qué son los ARIA labels?"
   - "¿Cómo optimizar para SEO técnico?"

##  Estructura del Proyecto

```
lighthouse-assistant/
├── app/
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── core/
│   │   ├── model.py         # Integración con Groq API
│   │   └── prompts.py       # Sistema de prompts y contexto
│   └── ui/
│       ├── chat.py          # Componente de chat
│       └── layout.py        # Layout de la aplicación
├── docs/
│   └── doc-notebook.ipynb   # Documentación en Jupyter
├── pyproject.toml           # Configuración del proyecto
├── .env                     # Variables de entorno (no incluido en git)
└── README.md                # Este archivo
```

## Modelo de IA

El asistente utiliza **LLaMA 3.3 70B Versatile** a través de Groq API, optimizado con un sistema de prompts especializado en:

- Análisis técnico de métricas web
- Conocimiento actualizado de estándares web (WCAG, Core Web Vitals)
- Recomendaciones basadas en documentación oficial de Google Lighthouse
- Contexto limitado a temas de optimización web para respuestas precisas

## Privacidad y seguridad

- No almacena datos sensibles
- Las consultas se procesan a través de Groq API
- Las API keys se gestionan mediante variables de entorno
- No ejecuta código externo