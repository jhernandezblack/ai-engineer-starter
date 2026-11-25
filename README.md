# AI Engineer Starter

[Español](README.md) · [English](README.en.md)

Tres plantillas pequeñas y originales en Python para aprender herramientas, control humano y respuestas con fuentes. Código MIT de BlackBox Big Data; no contiene soluciones de cursos privados.

| Plantilla | Aprendes | Relación con la ruta |
|---|---|---|
| `agent` | Bucle acotado, herramienta `stock`, argumentos validados | Primeros agentes y Python |
| `workflow` | Borrador persistente, pausa y aprobación humana explícita | Base conceptual para workflows con estado |
| `qa` | Recuperación léxica, citas permitidas y abstención | Base de consulta documental |

Son ejemplos stdlib: no implementan LangGraph, embeddings ni GraphRAG. El curso gratuito puede usar Claude/API; este repositorio usa Ollama local como alternativa independiente.

## Inicio sin modelo (reproducible)

Requiere Python 3.12+ (referencia fijada: 3.12.12). No requiere pip, credenciales ni cuenta de API. Desde una terminal:

```sh
git clone https://github.com/jhernandezblack/ai-engineer-starter.git
cd ai-engineer-starter
python3 -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m starter agent --offline --lang es
python -m starter qa --offline --question devoluciones --lang es
python -m starter qa --offline --question volcanes --lang es
```

`--offline` imprime `OFFLINE FIXTURE` en stderr: usa respuestas predefinidas, **no ejecuta inferencia ni demuestra calidad del modelo**. El agente consulta notebook y responde 12; Q&A cita `[policy.txt]`. Una pregunta sin coincidencias produce `abstained: true`. Los fixtures usan frases bilingües para que su naturaleza sea evidente.

## Aprobación y reanudación

```sh
python -m starter workflow --offline --workspace output/caso-1 --question 'Confirmar recepción de consulta'
cat output/caso-1/state.json
python -m starter workflow --workspace output/caso-1 --decision APPROVE
cat output/caso-1/reply.txt
```

Primero revisa el campo `draft`. Solo `APPROVE` escribe `reply.txt`; `REJECT` cierra sin escribirlo. La segunda orden carga el estado sin invocar un modelo. Cada caso necesita una carpeta nueva; no se sobrescriben borradores ni respuestas existentes. La acción es guardar una muestra local, nunca enviar correo. Conserva la carpeta privada: el archivo es estado local confiable, no una frontera de seguridad multiusuario. No ejecutes decisiones concurrentes sobre el mismo caso.

## Modelo local real

Instala [Ollama](https://ollama.com/download), inicia su servicio y descarga explícitamente un modelo:

```sh
ollama serve  # solo si la aplicación no inició ya el servicio
ollama pull qwen3:4b
python -m starter agent --model qwen3:4b --question 'Consulta el inventario de notebook' --lang es
python -m starter workflow --model qwen3:4b --workspace output/caso-real --question 'Un cliente consulta por su pedido' --lang es
python -m starter qa --model qwen3:4b --question '¿Cuántos días para devoluciones?' --lang es
```

Usamos `POST /api/chat`, JSON y `stream:false` según la [API oficial](https://docs.ollama.com/api/chat). [qwen3:4b](https://ollama.com/library/qwen3:4b) es una opción de unos 2.5 GB de descarga; requiere memoria adicional para ejecución y contexto. Reserva varios GB libres y reduce el modelo si tu equipo no tiene capacidad. El tag de modelo puede cambiar: registra `ollama list` para reproducibilidad. Licencia y términos del modelo son independientes de MIT. No se descarga nada automáticamente.

El plazo HTTP total incluye conexión, envío, cabeceras y cuerpo, incluso si el servidor entrega bytes lentamente. La generación tiene hasta 30 segundos por llamada, hasta 512 tokens de salida, 64 KiB por respuesta HTTP; el agente tiene máximo cuatro pasos y 30 segundos totales. Un equipo lento puede necesitar precargar el modelo con `ollama run qwen3:4b`; las plantillas fallan de forma visible en lugar de ampliar límites solas. Solo se conecta a `127.0.0.1:11434` y no requiere claves.

## Límites y solución de problemas

- `Connection refused`: inicia Ollama. Modelo ausente: ejecuta `ollama pull` conscientemente. JSON inválido o timeout: prueba otro modelo local o precárgalo; no confundir el fixture con una solución del modelo.
- Herramienta o argumentos inválidos: se rechazan; no se ejecuta shell, código generado ni solicitudes arbitrarias.
- Q&A usa palabras compartidas y hasta tres textos de `data/`; no es búsqueda semántica. Reformula con palabras del documento. Puede recuperar evidencia irrelevante.
- Las citas se validan contra documentos recuperados y deben aparecer en la respuesta. Esto verifica procedencia estructural, **no prueba que cada afirmación sea correcta**. Revisa los textos; un modelo puede alucinar incluso con una cita válida. La abstención cubre ausencia de coincidencias y respuestas/citas inválidas.
- Los documentos y solicitudes del modelo se tratan como datos no confiables. No añadas archivos sensibles. Los límites no sustituyen aislamiento del sistema operativo para código ajeno.
- Las pruebas son deterministas y no descargan modelos; incluyen un servidor HTTP local efímero. Un sandbox debe permitir loopback para esa prueba.

## Siguiente paso

[Explora la Ruta AI Engineer y empieza gratis](https://blackboxbigdata.com/ruta-ai-engineer?utm_source=github&utm_medium=referral&utm_campaign=ruta-ai-engineer&utm_content=readme_es). La inscripción al primer curso es gratuita; proveedores externos del curso pueden cobrar por uso. El paquete completo se anuncia próximamente en la web.
