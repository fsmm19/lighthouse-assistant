# Lighthouse Assistant

Asistente inteligente basado en **LLM** y **RAG** que interpreta reportes de **Google Lighthouse** y genera recomendaciones prácticas, priorizadas y accionables para mejorar el rendimiento, la accesibilidad y el SEO de sitios web.

## Objetivo
Desarrollar una aplicación que transforme los reportes JSON de Lighthouse en un plan de optimización claro, priorizado y acompañado de ejemplos prácticos, facilitando la toma de decisiones en equipos de desarrollo web.

## Características principales
- Análisis automático de reportes JSON de Lighthouse.  
- Interpretación de hallazgos mediante **CodeLlama** (ejecutado localmente con **Ollama**).  
- Recuperación aumentada de información (**RAG**) desde una base de buenas prácticas y ejemplos técnicos.  
- Generación de recomendaciones priorizadas con base en impacto, esfuerzo y beneficio.  
- Interfaz sencilla para cargar reportes y visualizar resultados.  

## Tecnologías
- **Frontend:** Next.js, TailwindCSS  
- **Backend:** Node.js / API REST  
- **LLM Runtime:** Ollama  
- **Modelo:** CodeLlama 7B
- **Base de conocimiento (RAG):** Documentos + Embeddings  

## Estructura inicial del proyecto
```bash
lighthouse-assistant/
├── backend/ # API + Procesamiento de informes de Lighthouse
├── frontend/ # Web UI
├── rag/ # Base de conocimientos
├── docs/ # Documentos del proyecto (entregables)
├── tests/ # Pruebas unitarias y de integración
├── .gitignore
├── package.json
└── README.md
```

## Estado
- Actualmente en **etapa de planificación (Fase 1)**. Desarrollo del MVP en curso.
