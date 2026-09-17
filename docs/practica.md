# Práctica — El mismo producto, otro problema

Construiste un producto de datos en tres sesiones. Esta práctica comprueba si lo que
construiste era **un producto de precios de casas** o **un producto**.

La diferencia se mide de una sola forma: cambia el problema y cuenta cuánto código tienes que
reescribir.

```
   Entregas un producto completo --tablero, modelo, API e interfaz--
   sobre un dataset que NO es el de casas, y un documento corto
   explicando qué tuviste que tocar y por qué.
```

Se hace en equipo, y es el ensayo general del reto.

---

## Lo que ya sabes de la respuesta

Antes de empezar, una cifra. El boilerplate de esta práctica está adaptado al dataset de
vinos que usamos como ejemplo, y para llegar ahí desde el producto de casas hubo que editar
**15 líneas**, todas de configuración, en dos archivos:

| Archivo | Líneas | Qué son |
|---|---|---|
| `backend/s1_tablero.py` | 8 | el archivo, el target, la columna que agrupa, las features |
| `notebooks/entrenar.py` | 7 | el target, las features, cuáles son categóricas, el umbral |

Y esto es lo que **no** se tocó:

```
   frontend/src/vistas/ModelCard.jsx     0 líneas
   frontend/src/vistas/Predecir.jsx      0 líneas
   frontend/src/vistas/Tablero.jsx       0 líneas
   frontend/src/vistas/Historial.jsx     0 líneas
   backend/app.py                        0 líneas
```

El formulario se rearmó solo. La Model Card se llenó sola. Las gráficas cambiaron de etiquetas
solas. Ninguno de esos archivos sabe que existen las casas ni que existen los vinos: leen el
contrato.

**Tu trabajo es reproducir eso con tu propio dataset.** Si al terminar tocaste 15 líneas,
entendiste el módulo. Si tocaste 300, hay algo que no está derivado del contrato, y encontrarlo
es la mitad del aprendizaje.

---

## Qué entregas

1. **El repositorio funcionando**, con tu dataset. Las cuatro pestañas vivas.
2. **`BITACORA.md`**, de una página, con:
   - qué dataset elegiste y por qué
   - la tabla de qué archivos tocaste y cuántas líneas en cada uno
   - tu umbral y **por qué ese** (ver la etapa 2)
   - una cosa que tuviste que ajustar y no esperabas
3. **Una captura** de cada pestaña.

---

## Elegir el dataset

**No uses Spaceship Titanic ni el de casas.** Ya los trabajaste.

Requisitos, y cada uno existe por una razón:

| Requisito | Por qué |
|---|---|
| **Clasificación** (2 clases) | Es lo que vas a hacer en el reto |
| Entre 500 y 50,000 filas | Menos no da métricas creíbles; más tarda en clase |
| Entre 5 y 15 features | Menos es trivial; más hace un formulario inusable |
| **Al menos una columna categórica** | El tablero agrupa por ella |
| Una columna ordinal o de pocos valores | Es la segunda gráfica |
| Un target que **signifique algo** | Vas a tener que explicar el umbral |

Sitios donde buscar: [OpenML](https://www.openml.org/search?type=data), el
[UCI ML Repository](https://archive.ics.uci.edu/datasets), Kaggle Datasets, o datos abiertos
de gobierno (INEGI, datos.gob.mx).

> **Si tu target no es binario de origen, derívalo** — y entonces la columna de la que salió
> **tiene que irse de las features**. Es el error más caro y más silencioso que existe: el
> modelo saca 99% y no aprendió nada. Vuelvo a esto en la etapa 2.

---

## El boilerplate

Está en [template/](../template/). No es una copia del proyecto: son **solo los archivos que
cambian**, ya genéricos.

```
template/
├── backend/
│   ├── s1_tablero.py        AJUSTA 1  ← el bloque de configuración
│   ├── s2_modelo.py         AJUSTA 4  ← predict_proba y el umbral
│   └── s4_producto.py       AJUSTA 6  ← la frase de la explicación
├── frontend/src/
│   ├── main.jsx             AJUSTA 7  ← el título
│   ├── api.js                         (un nombre de parámetro)
│   └── vistas/                        (los cuatro, genéricos: no los tocas)
├── notebooks/
│   ├── preparar-datos.py              cómo se armó el CSV de ejemplo
│   └── entrenar.py          AJUSTA 2 y 3
└── data/datos.csv                     el ejemplo: 6,497 vinos
```

Para empezar, **en tu computadora**:

```bash
git checkout -b practica
cp -r template/backend/* backend/
cp -r template/frontend/src/* frontend/src/
cp template/notebooks/entrenar.py notebooks/
cp tu-dataset.csv data/datos.csv
```

Antes de cambiar nada, **córrelo con los vinos** para ver el destino:

```bash
./setup/run test
./setup/run start
```

---

## Etapa 1 — El tablero (40 min)

Abre `backend/s1_tablero.py`. Todo lo que ese archivo sabe de tu problema vive en un bloque:

```python
ARCHIVO = "datos.csv"
TARGET = "bueno"
TIPO_TARGET = "categoria"      # "numero" si fuera regresión
CLASE_POSITIVA = 1
GRUPO = "color"                # la categórica que agrupa el tablero
CORTE = "nivel_alcohol"        # la segunda gráfica, ordinal
FEATURES = [...]
ID = None
```

Llénalo con tus columnas. Si te equivocas en un nombre, el servicio **no arranca** y te dice
cuál falló y cuáles sí existen — a propósito: un error de configuración tiene que doler al
arrancar, no en la primera petición.

```
AJUSTA 1: estas columnas no existen en datos.csv: ['colr'].
    Las que si existen: ['acidez_volatil', ..., 'color', ...]
```

### Lo que pasa sin que lo pidas

Arranca y abre el tablero. Las gráficas ya dicen los nombres de **tus** columnas, el filtro
tiene **tus** categorías, la tabla tiene **tus** campos.

Eso es porque `/api/stats` ahora devuelve un bloque `meta`:

```json
"meta": {
  "target": "bueno", "tipo_target": "categoria", "clase_positiva": 1,
  "grupo": "color", "corte": "nivel_alcohol"
}
```

y `Tablero.jsx` lee de ahí sus etiquetas. **Es la misma idea del contrato del modelo, aplicada
a los datos.** En la sesión 1 escribimos "Colonia" y "Precio medio" a mano por todo el JSX;
ahora ves lo que costaba.

### Lo que tienes que mirar antes de seguir

La segunda gráfica es tu primera lectura del problema. En el ejemplo de vinos:

```
   nivel_alcohol 1   →   6.3% buenos
   nivel_alcohol 2   →  20.3% buenos
   nivel_alcohol 3   →  47.8% buenos
```

Eso es señal, y se ve antes de entrenar nada. **Si tus dos gráficas salen planas, tu modelo
probablemente también va a salir plano** — y es mejor descubrirlo ahora que después de entrenar.
Cambia de `GRUPO` o de `CORTE`, o plantéate si elegiste bien el target.

---

## Etapa 2 — El modelo (50 min)

Abre `notebooks/entrenar.py`. Otro bloque de configuración:

```python
TARGET = "bueno"
CLASE_POSITIVA = 1
FEATURES = [...]           # las MISMAS que en AJUSTA 1
CATEGORICAS = ["color"]
UMBRAL = 0.5               # ← lee lo de abajo antes de dejarlo así
```

```bash
./.venv/bin/python notebooks/entrenar.py
```

Produce los tres archivos de siempre: `pipeline.joblib`, `metadata.json`, `example.json`. El
contrato tiene **la misma forma** que el de regresión, y por eso el frontend no se entera del
cambio. Gana tres campos: `task`, `classes` y `umbral`.

### La fuga de datos

Si derivaste el target de otra columna, **esa columna tiene que salir de `FEATURES`**. En el
ejemplo de vinos, `bueno = calidad >= 7`, así que `calidad` se elimina del CSV entero — puedes
verlo en `template/notebooks/preparar-datos.py`.

Cómo lo detectas: **si tu modelo saca más de 0.98 de accuracy, sospecha.** Los problemas reales
no son tan fáciles. Busca qué columna le está contando la respuesta.

### `AJUSTA 3` — el umbral, que es la parte que importa

Tu modelo no devuelve una clase: devuelve una **probabilidad**. Convertirla en un sí/no exige
elegir dónde cortar, y esa elección **no es del modelo, es tuya**.

Con el modelo de vinos, sobre el mismo conjunto de prueba:

| umbral | precision | recall | f1 | vinos marcados como buenos |
|---:|---:|---:|---:|---:|
| 0.20 | 0.508 | **0.853** | 0.637 | 321 |
| 0.30 | 0.619 | 0.733 | **0.671** | 226 |
| 0.40 | 0.728 | 0.602 | 0.659 | 158 |
| 0.50 | **0.855** | 0.524 | 0.649 | 117 |
| 0.70 | 0.941 | 0.335 | 0.494 | 68 |

*(191 vinos buenos reales de 975)*

Mira el renglón de 0.50, que es el que sale por no elegir: **precisión de 0.855 y recall de
0.524.** De cada 100 vinos buenos, se te escapan 48. Y el accuracy dice 0.89, que suena
estupendo.

> **0.5 no es el valor por defecto correcto. Es el que sale de no haber decidido.**

Para elegir el tuyo, contesta una pregunta y solo una:

```
   ¿Qué error te cuesta más caro:
   marcar como positivo algo que no lo era,
   o dejar pasar un positivo de verdad?
```

- Detectar fraude, enfermedad, deserción escolar → **te duele más dejarlo pasar** → umbral bajo
- Enviar una promoción cara, acusar a alguien, bloquear una cuenta → **te duele más la falsa
  alarma** → umbral alto

En regresión este punto **no existe**: un precio es un precio. Es lo primero que aparece al
cambiar de tipo de problema, y en el reto vas a tener que defenderlo.

**Escribe tu umbral y tu razón en `BITACORA.md`.** Esa frase es lo que se califica, no el
número.

### Verifica la costura

```bash
./setup/run test
```

El test de paridad sigue funcionando: compara `example.json` contra lo que responde tu servicio.
Si falla, el artefacto y el código no están hablando del mismo modelo.

---

## Etapa 3 — El backend (20 min)

Aquí casi no hay trabajo, y ese es el punto.

`backend/s2_modelo.py` ya viene adaptado a clasificación. Lee el `AJUSTA 4` y fíjate en lo que
hace:

```python
probas = pipeline.predict_proba(entrada)[0]
umbral = float(contrato.get("umbral", 0.5))
clase = positiva if p_positiva >= umbral else negativa
```

**El umbral sale del contrato, no está escrito en el servicio.** Cambiarlo es reentrenar —o
editar `metadata.json`— y no tocar el backend. Es la misma regla de siempre: lo que depende del
modelo viaja con el modelo.

La respuesta gana tres campos:

```json
{
  "prediction": 0,
  "probabilities": {"0": 0.96, "1": 0.04},
  "confidence": 0.04,
  "threshold": 0.5,
  "prediction_id": "...", "model_version": "1.0.0", "warnings": []
}
```

Devolver solo la clase esconde la diferencia entre 0.51 y 0.99, que para quien decide no es lo
mismo en absoluto.

**Lo que no cambió:** la validación contra el contrato, los avisos de fuera de rango, el 400 que
nombra el campo, el 500 genérico, el registro de predicciones. Nada de eso sabía de precios.

Compruébalo:

```bash
curl -s -X POST http://localhost:8080/api/predict \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c "import json;print(json.dumps(json.load(open('artifacts/example.json'))['input']))")"
```

Y con una categoría inventada, para ver que el mensaje sigue siendo útil:

```
{"error": "'color' no acepta el valor 'rosado'. Valores validos: blanco, tinto"}
```

---

## Etapa 4 — El frontend (20 min)

**Las cuatro vistas no se tocan.** Ábrelas y compruébalo:

| Vista | Qué hizo sola |
|---|---|
| **Tablero** | Tomó sus etiquetas de `meta` |
| **Predecir** | Armó el formulario desde `features`, y al ver `task: "clasificacion"` presentó clase y barras de probabilidad en lugar de un número |
| **Historial** | Sacó las columnas del input guardado |
| **Model Card** | Sacó las columnas de métricas de las claves del contrato: donde había RMSE/MAE/R² ahora hay accuracy/precision/recall/f1/roc_auc |

Lo único que ajustas son dos textos:

- `AJUSTA 7` en `frontend/src/main.jsx` — el título de tu producto
- `AJUSTA 6` en `backend/s4_producto.py` — la frase de la explicación

### El ejercicio de esta etapa

No es escribir código. Es **encontrar lo que se rompió**, si algo se rompió.

Abre las cuatro pestañas y busca cualquier cosa que siga hablando del problema anterior, o que
se vea mal con tus datos: una etiqueta cortada, un formato de número absurdo, una columna que no
cabe. Anótalo en la bitácora, arréglalo si puedes, y **di en qué archivo estaba**.

Si lo que encontraste está en una vista, es que esa vista tenía algo escrito a mano que
debíamos haber derivado del contrato. Eso es un hallazgo, no un fracaso: es exactamente el tipo
de deuda que vas a tener que ver en tu reto.

---

## Cómo se evalúa

Esta práctica no tiene calificación propia: es preparación para el reto, y cada punto mapea a
un renglón de su rúbrica.

| Lo que se revisa | Renglón del reto |
|---|---|
| El dataset elegido cumple los requisitos y lo justificas | Datos |
| El target y las features no tienen fuga | Datos · Refinamiento |
| El modelo entrena y el contrato se exporta completo | Modelo |
| Los tres conjuntos y las métricas están en la Model Card | Evaluación |
| **El umbral está elegido y justificado** | Evaluación · Refinamiento |
| Las cuatro pestañas funcionan con tu dataset | Solución: genera una interfaz |
| La bitácora dice qué tocaste y por qué | Todos |

La pregunta que se hace al revisar es siempre la misma:

> ¿Cuántas líneas tuviste que cambiar, y eran las que debías cambiar?

---

## Si te atoras

```bash
./setup/run doctor
curl -s http://localhost:8080/api/health
```

Tres fallas que vas a tener, en orden de probabilidad:

1. **El servicio no arranca y habla de columnas.** Es `AJUSTA 1`: un nombre mal escrito. El
   mensaje te dice cuáles sí existen.
2. **El formulario sale vacío.** `/api/model` no responde: falta el artefacto, o `entrenar.py`
   no terminó. Míralo con `curl`.
3. **El tablero no muestra gráficas.** Tu `GRUPO` tiene demasiadas categorías, o `CORTE` es una
   columna continua. Los dos necesitan pocos valores distintos.

Y si dejaste el repositorio en un estado del que no sabes salir, la red de seguridad sigue ahí
— estás en una rama, así que tu trabajo de las sesiones está intacto en `main`:

```bash
git checkout main
```
