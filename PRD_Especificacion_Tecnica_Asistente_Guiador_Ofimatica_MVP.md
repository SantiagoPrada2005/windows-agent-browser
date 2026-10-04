**PRD Y ESPECIFICACIÓN TÉCNICA**

**Asistente Guiador de Ofimática para Adultos Mayores**

*MVP funcional para Windows · Arquitectura local-first con IA visual bajo demanda*

| Documento | Versión | Estado | Objetivo |
| :---- | :---- | :---- | :---- |
| PRD \+ Especificación técnica | 2.0 | MVP definido | Construir un prototipo funcional, económico y técnicamente sólido para una sola persona |

Nota: este documento consolida el PRD original y las decisiones posteriores del proyecto. El objetivo no es definir un producto comercial terminado, sino una implementación MVP completa y demostrable.

# **1\. Resumen ejecutivo**

El proyecto consiste en una aplicación de escritorio para Windows que actúa como tutor interactivo de ofimática para adultos mayores y usuarios con baja alfabetización digital. El sistema escucha mediante una palabra de activación local, convierte la voz a texto, interpreta la intención y, cuando es necesario, analiza el estado visual de la pantalla para explicar al usuario qué debe hacer. El usuario conserva siempre el control físico: el sistema no mueve el ratón ni ejecuta clics de forma autónoma.

La estrategia del MVP es local-first: wake word, captura de pantalla, STT y TTS se ejecutan localmente siempre que sea práctico. La nube se utiliza principalmente para razonamiento lingüístico y visión cuando el problema requiere comprender la interfaz. La pantalla puede capturarse continuamente en memoria, pero la inferencia remota se realiza de forma adaptativa para controlar costes.

# **2\. Objetivos y no objetivos**

## **2.1 Objetivos**

* Construir un asistente completamente funcional para Windows como MVP individual.  
* Permitir interacción natural mediante voz sin enviar audio de espera continuamente a la nube.  
* Guiar al usuario paso a paso sin quitarle el control del computador.  
* Comprender el contexto visual de la aplicación activa mediante screenshots.  
* Reducir llamadas de IA mediante detección local de cambios y reutilización del contexto visual.  
* Mantener la arquitectura sencilla y modular para poder sustituir proveedores/modelos.  
* Priorizar Word y Bloc de Notas; incorporar Excel en una segunda etapa del MVP.  
* Medir latencia, consumo y coste real durante pruebas antes de optimizar prematuramente.

## **2.2 No objetivos del MVP**

* No controlar el ratón ni ejecutar acciones destructivas automáticamente.  
* No construir un agente autónomo de computer-use con bucles complejos.  
* No depender de UI Automation como requisito para que el producto funcione.  
* No soportar inicialmente todas las aplicaciones de Windows.  
* No desarrollar un sistema comercial completo de instalación, telemetría, cuentas, facturación o administración.  
* No exigir una precisión perfecta de coordenadas para poder considerar el MVP exitoso; si el resaltado resulta inestable, se puede degradar a instrucciones espaciales por voz o una ventana flotante.

# **3\. Usuario objetivo y principios UX**

Público objetivo: adultos mayores, jubilados y personas no nativas digitales que utilizan Word, Excel, PowerPoint, correo electrónico, navegadores y aplicaciones básicas.

| Principio | Requisito |
| :---- | :---- |
| Control del usuario | El asistente nunca hace clic, mueve el cursor ni ejecuta acciones inesperadas. |
| Lenguaje cotidiano | Evitar tecnicismos; utilizar referencias como “arriba a la izquierda”, “botón con forma de disquete” o el nombre visible del botón. |
| Paciencia | Aceptar pausas y silencios prolongados. No interrumpir prematuramente al usuario. |
| Accesibilidad | Texto y señales visuales grandes, contraste alto, animaciones suaves y explicaciones cortas. |
| Confirmación | Después de una acción del usuario, explicar o confirmar el siguiente paso sin asumir que la acción ocurrió si no hay evidencia. |
| Aprendizaje | El objetivo es enseñar al usuario, no sustituirlo. |

# **4\. Alcance funcional del MVP**

| ID | Funcionalidad | Prioridad | Criterio de aceptación |
| :---- | :---- | :---- | :---- |
| RF-01 | Wake word local | P0 | La aplicación permanece en espera sin enviar audio y se activa con la palabra configurada. |
| RF-02 | STT | P0 | Convierte la orden del usuario a texto con suficiente precisión en español. |
| RF-03 | Interpretación de intención | P0 | Convierte una petición natural en una intención estructurada. |
| RF-04 | Estado visual de pantalla | P0 | Puede mantener una captura reciente de la pantalla activa en memoria. |
| RF-05 | Detección de cambios | P0 | Evita llamadas visuales remotas cuando la pantalla no ha cambiado de forma relevante. |
| RF-06 | Análisis visual bajo demanda | P0 | Cuando la intención requiere contexto espacial, obtiene elementos relevantes y/o coordenadas mediante un modelo visual. |
| RF-07 | Respuesta guiada | P0 | Explica al usuario qué debe hacer en lenguaje cotidiano. |
| RF-08 | TTS | P0 | La respuesta se reproduce con una voz comprensible en español. |
| RF-09 | Overlay opcional | P1 | Si la detección de coordenadas es fiable, muestra un halo/flecha sin bloquear el mouse. |
| RF-10 | Fallback visual | P0 | Si el overlay no es fiable, la aplicación continúa funcionando con instrucciones espaciales o ventana flotante. |
| RF-11 | Historial de contexto corto | P1 | Mantiene contexto suficiente de la conversación y del estado visual reciente. |
| RF-12 | Configuración básica | P1 | Permite pausar escucha, probar audio y ajustar volumen. |

# **5\. Arquitectura propuesta**

Arquitectura local-first, con inferencia remota adaptativa:

1. Micrófono → openWakeWord local.  
2. Wake word → captura de voz → Whisper/whisper.cpp local.  
3. Texto → router de intención → modelo rápido y económico (Groq u otro proveedor configurable).  
4. Si la petición no necesita contexto visual → responder directamente.  
5. Si necesita contexto visual → utilizar la captura más reciente; si está obsoleta o hubo un cambio relevante, capturar una nueva.  
6. Screenshot → modelo multimodal económico mediante DeepSeek directo u OpenRouter.  
7. Resultado → JSON estructurado con intención, elementos, coordenadas opcionales y confianza.  
8. Python/PyQt6 → renderizar overlay opcional.  
9. Respuesta → Piper TTS local.

# **6\. Componentes y tecnologías**

| Componente | Tecnología inicial | Motivo |
| :---- | :---- | :---- |
| Lenguaje | Python 3.11 | Velocidad de desarrollo y ecosistema de IA/Windows. |
| Entorno | uv | Entorno reproducible y gestión rápida de dependencias. |
| GUI/overlay | PyQt6 | Ventana transparente, always-on-top y control de eventos. |
| Wake word | openWakeWord | Inferencia local y continua. |
| STT | whisper.cpp | Reconocimiento de voz local, sin coste por minuto. |
| Captura | mss | Capturas rápidas de pantalla. |
| Procesamiento | OpenCV/Pillow | Detección de cambios, redimensionado y preparación de imágenes. |
| LLM rápido | Groq (modelo económico disponible) | Interpretación de intención con baja latencia. |
| Vision | DeepSeek Vision directo u OpenRouter | Comprensión visual económica y proveedor intercambiable. |
| TTS | Piper | Síntesis local en español. |
| Empaquetado | PyInstaller | Distribución como aplicación Windows. |
| Configuración | JSON/TOML/.env | Configuración sencilla y separada de secretos. |

# **7\. Pipeline de voz**

## **7.1 Estado de espera**

* El micrófono puede permanecer abierto localmente para detectar el wake word.  
* No se transmite audio a servicios externos durante la espera.  
* Debe existir un indicador claro cuando comienza la escucha activa.  
* El usuario puede pausar completamente la escucha desde la bandeja del sistema.

## **7.2 Captura y STT**

* Después del wake word, grabar la intervención del usuario.  
* Permitir pausas de aproximadamente 1.5–2.0 segundos antes de considerar finalizada la frase.  
* No cortar una frase por titubeos o silencios cortos.  
* El texto transcrito se entrega al router de intención.  
* Si el STT local falla repetidamente, se podrá añadir Groq Whisper como fallback opcional, no como dependencia inicial.

# **8\. Router de intención**

El LLM no debe funcionar como agente autónomo. Su función inicial es clasificar y estructurar la petición.

Ejemplo de salida:

{  
  "intent": "locate\_element",  
  "target": "guardar",  
  "requires\_visual\_context": true,  
  "response\_style": "short\_guidance"  
}  
Intenciones iniciales:

* general\_question  
* locate\_element  
* explain\_action  
* guide\_multistep\_task  
* confirm\_action  
* repeat\_instruction  
* cancel  
* unknown

# **9\. Sistema de contexto visual**

## **9.1 Captura local continua**

La captura continua no implica envío continuo a la nube. MSS puede mantener un frame reciente en memoria y utilizar un muestreo bajo, por ejemplo 2–5 FPS, durante el estado activo.

## **9.2 Detección local de cambios**

* Comparar frames consecutivos o muestreados mediante diferencia de imagen.  
* Ignorar cambios mínimos que no alteren la interfaz relevante.  
* Detectar cambios significativos como apertura de menús, diálogos, cambio de pestaña o modificación importante de la ventana.  
* Actualizar el screenshot remoto únicamente cuando sea necesario.

## **9.3 Política de inferencia visual**

| Situación | Acción |
| :---- | :---- |
| Pregunta conceptual | No enviar screenshot. |
| Pregunta sobre ubicación | Usar screenshot reciente o capturar uno nuevo. |
| Pantalla sin cambios | Reutilizar estado visual reciente. |
| Cambio significativo | Enviar nuevo screenshot al modelo visual. |
| Modelo no encuentra objetivo | Solicitar una segunda interpretación o pedir aclaración. |
| Confianza baja | No mostrar un halo preciso; utilizar instrucción espacial. |

# **10\. Visión y salida estructurada**

El modelo visual debe recibir una instrucción estricta para minimizar texto y producir datos utilizables por Python.

{  
  "found": true,  
  "application": "Microsoft Word",  
  "target": "Guardar",  
  "confidence": 0.94,  
  "bbox": {"x": 120, "y": 48, "width": 32, "height": 32},  
  "spatial\_description": "parte superior izquierda",  
  "reason": "icono de guardado visible"  
}  
Las coordenadas deben documentarse como coordenadas de píxel del screenshot o como coordenadas normalizadas; el MVP debe elegir un único formato internamente y convertirlo en un solo punto del pipeline.

# **11\. Overlay y degradación funcional**

El overlay es deseable, pero no debe convertirse en un punto único de fallo.

| Nivel | Comportamiento |
| :---- | :---- |
| A | Halo sobre el elemento detectado con coordenadas fiables. |
| B | Flecha/ventana flotante señalando la zona aproximada. |
| C | Instrucción verbal precisa: “arriba a la izquierda, junto al botón Abrir”. |
| D | Solicitud de aclaración: “¿Puedes decirme qué botones ves cerca?” |

La aplicación debe seguir siendo útil en los niveles B–D.

# **12\. TTS y experiencia de respuesta**

* TTS local mediante Piper.  
* Frases cortas, pausadas y sin terminología técnica.  
* Una instrucción principal por turno.  
* Cuando una tarea tiene varios pasos, presentar uno a la vez.  
* No reproducir una explicación larga mientras el usuario está intentando realizar el clic.  
* Permitir repetir la última instrucción mediante voz.

# **13\. Memoria y estado**

El MVP debe mantener memoria temporal, no una plataforma de memoria compleja.

| Dato | Retención inicial |
| :---- | :---- |
| Aplicación activa | Sesión |
| Último screenshot relevante | Mientras sea útil o hasta cambio significativo |
| Última intención | Sesión |
| Última instrucción | Sesión |
| Preferencia de velocidad de voz | Configuración local opcional |
| Datos personales del usuario | No requeridos para MVP |

# **14\. Privacidad y seguridad**

* El audio de espera debe permanecer local.  
* No almacenar audio salvo que se implemente explícitamente una función de diagnóstico.  
* Las capturas enviadas a un proveedor externo deben limitarse a las necesarias para resolver la petición.  
* No enviar capturas si la petición no requiere contexto visual.  
* No registrar credenciales, contraseñas, contenido sensible o documentos completos deliberadamente.  
* El sistema no debe ejecutar acciones destructivas.  
* Las API keys deben almacenarse fuera del código fuente y nunca en el cliente distribuido.  
* La versión final debe informar claramente cuando una captura sale del equipo para análisis.

# **15\. Requisitos no funcionales**

| ID | Requisito | Objetivo MVP |
| :---- | :---- | :---- |
| RNF-01 | Latencia | Objetivo: primer feedback en ≤4 s; optimizar posteriormente hacia ≤2.5 s. |
| RNF-02 | CPU en espera | Objetivo inicial \<3% promedio; validar en hardware real. |
| RNF-03 | RAM | Objetivo inicial \<300 MB en reposo, sujeto a modelo STT/TTS cargado. |
| RNF-04 | DPI | Soportar 100%, 125%, 150% y 200% en pruebas prioritarias. |
| RNF-05 | Resoluciones | Validar desde 1366×768 hasta 4K. |
| RNF-06 | Accesibilidad | Contraste alto y elementos visuales suficientemente grandes. |
| RNF-07 | Robustez | No bloquear Word/Excel ni impedir clics normales. |
| RNF-08 | Disponibilidad | Si la nube no está disponible, conservar funciones locales básicas y explicar la limitación. |
| RNF-09 | Coste | Evitar inferencia visual innecesaria y monitorizar tokens/coste por sesión. |

# **16\. Aplicaciones objetivo**

| Fase | Aplicaciones | Alcance |
| :---- | :---- | :---- |
| POC | Word \+ Bloc de Notas | Localización de elementos y guía básica. |
| MVP | Word \+ Bloc de Notas \+ Excel | Tareas frecuentes y preguntas visuales. |
| Posterior | PowerPoint \+ navegador | Ampliación sin rediseñar el núcleo. |
| Futuro | Correo y otras apps | Requiere validación adicional de privacidad y UI. |

# **17\. Casos de uso prioritarios**

* “¿Dónde guardo este documento?”  
* “¿Cómo pongo la letra más grande?”  
* “¿Dónde está negrita?”  
* “¿Cómo inserto una imagen?”  
* “¿Dónde está la opción para imprimir?”  
* “No encuentro el botón para deshacer.”  
* “¿Cómo hago una tabla?”  
* “Repíteme el paso.”  
* “¿Qué debo hacer ahora?”  
* “Ya hice clic, ¿qué sigue?”

# **18\. Manejo de tareas multistep**

Para acciones complejas, el modelo debe producir un pequeño plan y ejecutar una sola instrucción por turno.

Ejemplo:  
1\. Resaltar “Insertar”.  
2\. Esperar al clic del usuario.  
3\. Capturar/actualizar contexto.  
4\. Resaltar “Tabla”.  
5\. Esperar.  
6\. Guiar la selección de filas y columnas.  
El sistema no debe avanzar asumiendo que el usuario realizó el paso si no existe evidencia o confirmación.

# **19\. Control de costes**

* Wake word, STT y TTS deben ser locales inicialmente.  
* El LLM de intención debe ser pequeño, rápido y barato.  
* La visión debe utilizarse solamente cuando aporta información espacial o contextual.  
* Mantener un screenshot reciente en memoria para evitar capturas/API redundantes.  
* Detectar cambios localmente antes de volver a analizar una pantalla.  
* Utilizar imágenes redimensionadas y el nivel de detalle mínimo suficiente.  
* Solicitar JSON corto al modelo visual.  
* Registrar tokens de entrada/salida y cantidad de llamadas para conocer el coste real.  
* Mantener el proveedor visual detrás de una interfaz para poder cambiar entre DeepSeek directo y OpenRouter.

# **20\. Abstracción de proveedores**

La aplicación no debe acoplarse directamente a un único proveedor.

Interfaces conceptuales:  
LLMProvider.generate\_intent(text, context)  
VisionProvider.analyze(image, prompt)  
STTProvider.transcribe(audio)  
TTSProvider.speak(text)  
WakeWordProvider.listen()

Implementaciones iniciales: GroqLLMProvider, DeepSeekVisionProvider/OpenRouterVisionProvider, WhisperLocalProvider, PiperTTSProvider y OpenWakeWordProvider.

# **21\. Arquitectura de módulos**

asistente\_guiador/  
├── app/  
│   ├── main.py  
│   ├── config/  
│   ├── audio/  
│   │   ├── wakeword.py  
│   │   ├── stt.py  
│   │   └── tts.py  
│   ├── vision/  
│   │   ├── capture.py  
│   │   ├── change\_detector.py  
│   │   └── vision\_provider.py  
│   ├── ai/  
│   │   ├── intent\_router.py  
│   │   ├── prompts.py  
│   │   └── providers/  
│   ├── overlay/  
│   │   ├── overlay.py  
│   │   └── fallback\_hint.py  
│   ├── context/  
│   │   └── session\_state.py  
│   └── ui/  
│       └── tray.py  
├── assets/  
├── models/  
├── tests/  
├── pyproject.toml  
└── README.md

# **22\. Fases de desarrollo**

| Fase | Duración objetivo | Resultado |
| :---- | :---- | :---- |
| Fase 0 — POC técnico | 2–4 días | Wake word → STT → respuesta TTS local. |
| Fase 1 — Motor visual | 3–5 días | Screenshot → modelo visual → JSON con elemento/coordenadas. |
| Fase 2 — Router IA | 2–4 días | Clasificación de intención y decisión de si necesita visión. |
| Fase 3 — Overlay | 2–4 días | Halo/flecha/fallback sin bloquear el mouse. |
| Fase 4 — Integración | 4–7 días | Flujo completo en Word y Bloc de Notas. |
| Fase 5 — Excel | 3–5 días | Pruebas y tareas frecuentes. |
| Fase 6 — Robustez | 4–7 días | DPI, errores, latencia, coste, empaquetado. |

# **23\. Pruebas obligatorias**

| Categoría | Pruebas mínimas |
| :---- | :---- |
| Voz | Silencios, titubeos, ruido moderado, distintas velocidades de habla. |
| Wake word | Falsos positivos y falsos negativos. |
| Visión | Word claro, Word con menú abierto, Excel, diálogos, pantallas con mucho contenido. |
| Coordenadas | 100/125/150/200% DPI, ventana maximizada/no maximizada. |
| Overlay | No interceptar clics ni teclado. |
| Red | API lenta, API caída, timeout, respuesta inválida. |
| IA | JSON incompleto, confianza baja, elemento no encontrado. |
| Privacidad | Verificar que audio en espera no salga del equipo. |
| Coste | Registrar llamadas, tokens y coste estimado por sesión. |
| Rendimiento | CPU/RAM con aplicación en espera y durante una sesión. |

# **24\. Criterios de éxito del MVP**

* Un usuario puede activar el asistente mediante voz.  
* Puede formular una pregunta natural en español.  
* El sistema comprende la intención en los casos prioritarios.  
* Puede utilizar el contexto visual de Word/Excel cuando sea necesario.  
* Puede proporcionar una instrucción útil incluso si el overlay falla.  
* No ejecuta clics ni acciones destructivas.  
* La experiencia puede completarse sin consola ni comandos.  
* El sistema funciona durante una sesión prolongada sin degradación evidente.  
* El coste de IA de una sesión de prueba queda medido y documentado.  
* El proyecto puede instalarse y ejecutarse en un Windows limpio sin entorno Python visible.

# **25\. Riesgos y mitigaciones**

| Riesgo | Impacto | Mitigación |
| :---- | :---- | :---- |
| Modelo visual identifica mal un botón | Alto | Confianza, segunda consulta, instrucciones espaciales y fallback. |
| Coordenadas desalineadas por DPI | Alto | Manifest Per-Monitor DPI y pruebas sistemáticas. |
| Latencia de API | Medio | Modelo rápido, screenshot reciente, respuestas cortas y degradación verbal. |
| Coste inesperado | Medio | Telemetría de tokens, detección de cambios y límites por sesión. |
| STT local consume demasiados recursos | Medio | Modelo cuantizado y fallback opcional a API. |
| Piper tarda en generar voz | Medio | Voces ligeras y precarga del modelo. |
| Aplicación objetivo no es reconocida | Medio | Visión general y lenguaje espacial; UI Automation futura. |
| Overlay interfiere con usuario | Alto | Mouse-events transparent y fallback sin overlay. |
| Pérdida de Internet | Medio | Conservar STT/TTS locales y mensajes claros cuando el razonamiento visual no esté disponible. |

# **26\. Evolución posterior**

* Añadir UI Automation como fuente primaria de coordenadas cuando exista accesibilidad fiable.  
* Usar visión como fallback para interfaces no estructuradas.  
* Agregar memoria de aprendizaje: acciones conocidas, velocidad de voz y nivel de ayuda.  
* Añadir detección de aplicación activa para adaptar vocabulario y contexto.  
* Añadir modelos visuales locales si el hardware lo permite.  
* Añadir instalador profesional y actualización automática.  
* Incorporar telemetría anónima y opt-in únicamente si el proyecto evoluciona a producto.

# **27\. Decisiones técnicas definitivas del MVP**

| Decisión | Estado |
| :---- | :---- |
| Arquitectura local-first | APROBADA |
| GPT-Live | DESCARTADO para MVP por coste/complexidad |
| Wake word local | APROBADO |
| STT local | APROBADO |
| TTS local | APROBADO |
| Captura local continua | APROBADA |
| Inferencia visual adaptativa | APROBADA |
| DeepSeek Vision | CANDIDATO PRINCIPAL |
| OpenRouter | Capa de proveedor alternativo |
| Groq | Candidato principal para intención rápida |
| UI Automation | FUERA DEL MVP; futura mejora |
| Overlay | DESEABLE, no obligatorio para éxito |
| Computer-use autónomo | DESCARTADO |

# **28\. Principio rector del proyecto**

**“El asistente debe enseñar al usuario dónde y cómo actuar, no actuar en su lugar.”**

Este principio permite mantener el MVP pequeño: si una tecnología avanzada mejora la experiencia pero amenaza el plazo o la estabilidad, debe ser degradable sin romper la función principal.