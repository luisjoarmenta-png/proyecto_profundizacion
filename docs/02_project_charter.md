# Project Charter — Priorización de canciones para revisión editorial

**Equipo:** Santiago Giraldo, Nicolás Hidalgo, Maiyan Yarce y Luis José Armenta  
**Fecha:** 2026-11-21 · **Versión:** 0.1 · **Etapa:** formulación del proyecto

## 1. Contexto y problema de negocio

En el escenario propuesto, un equipo de programación musical dispone de tiempo para escuchar solo una parte del catálogo. Debe decidir qué canciones revisar primero. ¿Puede una selección basada en atributos disponibles antes del lanzamiento identificar más pistas con la etiqueta `viral` que una selección al azar del mismo tamaño? Mediremos el beneficio en pistas identificadas por cada 100 revisadas.

## 2. Objetivo

| Nivel | Descripción |
|---|---|
| Negocio | Priorizar las canciones que pasan a revisión editorial para aumentar la proporción de pistas etiquetadas como virales dentro de un cupo fijo. |
| Ciencia de datos | Evaluar si atributos como género, duración, tempo, bailabilidad, energía y carácter acústico permiten distinguir las dos clases. Desarrollar un modelo que puntúe y ordene las pistas para su revisión. |
| Tipo de problema | Clasificación binaria supervisada. |
| Variable objetivo | `viral` (1 = pista etiquetada como viral, 0 = pista etiquetada como no viral). Se verificará el criterio de asignación de la etiqueta. |

## 3. Criterios de éxito

| Tipo | Métrica | Umbral propuesto |
|---|---|---|
| Negocio (KPI) | Proporción de pistas con `viral = 1` entre las primeras *k* recomendadas. El equipo fijará *k* según su capacidad de revisión antes de evaluar el modelo. | Superar la tasa global de canciones etiquetadas como virales en el conjunto de prueba, referencia esperada de una selección al azar. |
| Modelo | Exactitud balanceada en prueba: promedio de la proporción de aciertos en cada clase. | Mayor que 0,50. Se fijará el umbral de clasificación con los datos de entrenamiento y validación. |
| Baseline a superar | Clasificador que siempre predice la clase más frecuente en entrenamiento. | Exactitud balanceada de referencia: 0,50 cuando ambas clases están presentes en prueba. |

## 4. Datos

| Fuente | Descripción | Filas × columnas | Acceso |
|---|---|---|---|
| [What Makes a Song Go Viral? 10,000 Tracks](https://www.kaggle.com/datasets/vedauv/what-makes-a-song-go-viral-10000-tracks) | Archivo `viral_songs.csv` con metadatos de las pistas, atributos de audio, reproducciones y etiqueta de viralidad. | La fuente anuncia 10.000 pistas. Se verificará la dimensión exacta al cargar el archivo. | Kaggle, mediante KaggleHub. |

**¿Qué representa una fila?** Una pista musical. Se comprobará si `track_id` identifica cada registro de forma única.

## 5. Alcance

- **Incluye** elaborar el perfil de datos, documentar la limpieza, explorar las características musicales, comparar modelos y entregar una API que devuelva la puntuación y la clase estimada de una pista.
- **Fuera de alcance** quedan determinar causas de viralidad, estimar reproducciones futuras y medir el impacto económico de campañas.

## 6. Riesgos y supuestos

| Riesgo | Probabilidad estimada | Impacto | Mitigación |
|---|---|---|---|
| Definición o ventana de medición de `viral` insuficientemente documentada. | Media | Alto | Consultar la documentación de la fuente y delimitar qué interpretación admite la etiqueta. |
| Representación insuficiente de una clase en la evaluación. | Por determinar | Alto | Comprobar los conteos por clase al diseñar la partición y reportar el desempeño para cada clase. |
| Uso de información posterior al momento de decisión. | Alta si se usan reproducciones acumuladas | Alto | Limitar las entradas de la API a atributos disponibles antes del lanzamiento. Reservar `streams` para el análisis descriptivo. |

## 7. Plan (cronograma del curso)

| Semana | Fase CRISP-DM | Entregable | Responsable propuesto |
|---|---|---|---|
| 1 | Comprensión del negocio y de los datos | Charter, KPIs y perfil inicial. | Todo el equipo acuerda el objetivo. Santiago Giraldo lidera el perfil de datos. |
| 2 | Preparación y exploración | Limpieza documentada y notebook de EDA. | Santiago Giraldo y Nicolás Hidalgo. |
| 3 | Modelado | Baseline, pipeline y comparación de modelos en validación. | Maiyan Yarce lidera el modelado. Luis José Armenta define las entradas y salidas de la API. |
| 4 | Evaluación y despliegue | Evaluación final en prueba, API y presentación con demo. | Maiyan Yarce y Luis José Armenta lideran evaluación y API, respectivamente. Presenta todo el equipo. |

## 8. Stakeholders

| Persona o rol | Interés | Cómo se le comunica |
|---|---|---|
| Programación musical (usuario propuesto) | Elegir qué pistas escuchar primero con el cupo disponible. | Demo de la lista priorizada y comparación de aciertos por cada 100 revisiones. |
| Equipo del proyecto | Coordinar entregables y reproducir el análisis. | Reuniones, WhatsApp y revisión de cambios en GitHub. |
| Docente del curso | Evaluar la aplicación de CRISP-DM y el funcionamiento de la solución. | Repositorio documentado, presentación y demo de la API. |