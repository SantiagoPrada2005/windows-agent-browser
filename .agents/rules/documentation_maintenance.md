# Regla: Mantenimiento, Sincronización y Navegación Escalonada por Índices

## 1. Principio Rector: Documentación como Código Vivo y Guía de Navegación
- **Sincronización Continua**: Toda alteración funcional, adición de nuevos módulos, modificación de esquemas de datos o refactorización arquitectónica **debe actualizar de forma inmediata y atómica la documentación escalonada del proyecto**. Ningún desarrollo se considera completo si introduce discrepancias con la documentación.
- **Navegación Obligatoria Primero por Índices (*Index-First Navigation*)**: Al explorar, investigar o ubicar componentes y responsabilidades en el repositorio, **está estrictamente ordenado leer primero los archivos `index.md` pertinentes en lugar de inspeccionar archivos de código directamente**.
  - Se debe comenzar consultando el `index.md` del nivel superior o del módulo de interés para entender responsabilidades, flujos y arquitectura.
  - Solo se deben abrir y leer los archivos fuente (`.py`, etc.) puntuales **cuando sea estrictamente necesario** (para implementar un cambio, editar código, verificar una línea específica o realizar debugging concreto).
  - Queda prohibido inspeccionar archivos de código a ciegas o hacer barridos masivos de código fuente sin haber consultado primero el mapa de los `index.md`.

---

## 2. Jerarquía Escalonada de Índices (`index.md`)
El proyecto mantiene un sistema de documentación piramidal con enlaces relativos navegables:

```text
├── index.md                                # Índice Maestro del Proyecto
├── README.md                               # Presentación del repositorio
├── src/
│   ├── index.md                            # Arquitectura global del código
│   └── asistente_guiador/
│       ├── config/index.md                 # Variables y configuraciones
│       ├── core/index.md                   # Modelos, contratos y orquestador
│       ├── ai/index.md                     # Prompts y proveedores de IA
│       ├── audio/index.md                  # Wakeword, VAD, STT y TTS
│       └── vision/index.md                 # Captura de pantalla y detección de cambios
└── tests/
    └── index.md                            # Estrategia de testing y suite
```

---

## 3. Protocolo Obligatorio ante Cambios de Código

### A. Al crear un nuevo módulo o paquete
1. Crear un archivo `index.md` dentro de dicho directorio explicando su propósito, contratos y componentes.
2. Registrar el nuevo módulo en el `index.md` del directorio padre.
3. Si el módulo altera el flujo principal, actualizar [`src/index.md`](file:///Users/santiago/proyectos/windows-agent-browser/src/index.md) y [`index.md`](file:///Users/santiago/proyectos/windows-agent-browser/index.md).

### B. Al modificar clases, funciones, contratos o esquemas existentes
1. Identificar el módulo correspondiente y actualizar su `index.md` local.
2. Si se modifican variables de entorno en `Settings`, actualizar inmediatamente [`src/asistente_guiador/config/index.md`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/config/index.md).
3. Si se agregan modelos o cambian interfaces en `core`, reflejar los cambios en [`src/asistente_guiador/core/index.md`](file:///Users/santiago/proyectos/windows-agent-browser/src/asistente_guiador/core/index.md).

### C. Al agregar o modificar tests
1. Mantener sincronizado [`tests/index.md`](file:///Users/santiago/proyectos/windows-agent-browser/tests/index.md) con los nuevos casos de prueba, comportamientos testeados y comandos recomendados.

---

## 4. Estilo y Formato de Documentación
- **Enlaces clicables siempre**: Usar enlaces markdown relativos o enlaces directos de archivo a símbolos y clases.
- **Diagramas explicativos**: Usar diagramas Mermaid cuando se modifiquen flujos de control o arquitecturas multicapa.
- **Tablas de configuración claras**: Mantener descripciones de parámetros con tipo, valor por defecto y efecto.
- **Sin jerga desactualizada**: La documentación debe reflejar con precisión la versión de Python, dependencias de `uv` y modelos actualmente soportados.
