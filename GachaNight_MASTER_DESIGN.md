# GachaNight — Documento maestro de diseño y desarrollo

> **Fuente de verdad del proyecto para Codex y colaboradores.**
>
> **Versión de especificación:** 2.0 · **Fecha:** 11 de octubre de 2026 · **Idioma de este documento:** español · **Idioma de la interfaz del juego:** inglés.
>
> **Estado:** diseño principal consolidado; balance, arte definitivo y algunos detalles de implementación se ajustarán mediante pruebas. Este documento **describe el producto deseado**, no garantiza que el prototipo existente ya lo implemente.
>
> **Regla de precedencia:** si un documento anterior, un script heredado o un prototipo contradice las decisiones aquí marcadas como **CONFIRMADAS**, prevalece este documento. No sobrescribir el código a ciegas: primero inspeccionar y migrar.

---

## 0. Instrucciones para Codex: leer antes de programar

1. Leer **este archivo completo** y después `README.md`, `AGENTS.md`, `project.godot`, escenas y scripts existentes.
2. Inventariar qué está implementado, qué es provisional y qué contradice la especificación. **No declarar implementadas funciones solo porque estén descritas aquí.**
3. Tratar como inalterables las reglas etiquetadas **CONFIRMADO**. Las cifras y sugerencias etiquetadas **EJEMPLO DE BALANCE** o **PROPUESTA TÉCNICA** se pueden ajustar sin modificar el concepto.
4. Trabajar en tareas pequeñas, versionables y comprobables. No reconstruir el juego desde cero ni sustituir archivos completos sin necesidad demostrada.
5. Tras cada tarea informar: archivos modificados, comportamiento obtenido, pruebas ejecutadas, errores, riesgos, decisiones pendientes y siguiente paso concreto.
6. Mantener este Markdown actualizado cuando el creador apruebe cambios. Registrar cambios en la sección «Historial y decisiones» y no reinterpretar conversaciones antiguas como decisiones nuevas.
7. El objetivo es un **videojuego jugable y divertido**, no únicamente pantallas o sistemas de datos. Priorizar el bucle jugable, la sensación física de las máquinas, la economía y la progresión del prestigio.
8. Si falta una decisión que impide implementar con seguridad un sistema central, consultarla; si es un número de balance o detalle cosmético, crear un valor inicial editable, documentarlo y seguir.

**Convención de certeza:**

- **CONFIRMADO:** decisión expresa del creador; no cambiar sin autorización.
- **PROPUESTA TÉCNICA:** arquitectura o UX recomendada para implementar una decisión, ajustable si hay razones técnicas.
- **EJEMPLO DE BALANCE:** cifras iniciales no aprobadas como definitivas, sujetas a métricas y playtests.
- **PENDIENTE:** diseño todavía abierto; nunca inventar como hecho.

## 1. Identidad, género y promesa

| Campo | Estado y definición |
|---|---|
| Nombre | **GachaNight** — CONFIRMADO. No usar «Gachapon Night» como nombre comercial definitivo. |
| Género | Incremental / idle progresivo, coleccionismo de figuras, máquinas de premios y sistema de prestigio. |
| Cámara | **2D en vista oblicua elevada («3/4 desde arriba»)**: se ve el frente y la parte superior de cada objeto y el suelo es un plano profundo por el que el personaje camina en dos ejes. La tienda sigue siendo una tira de salas. (Decisión del creador del 2026-10-11; ver sección 25.) |
| Fantasía | Despertar atrapado en una tienda japonesa nocturna y convertir unas pocas monedas en una red de máquinas y robots hasta poder escapar. |
| Ambientación | **Japón, jugueterías y máquinas de los años 80 y 90**; nostálgico, acogedor, levemente extraño. |
| Dirección visual | **Pixel art con estética «rubber hose»** (dibujos animados de los años 20-30: extremidades de goma negras, guantes blancos, zapatones, ojos ovalados) mezclada con **gráfica japonesa Showa de los 80-90**. Las máquinas son personajes vivos. Referencias del creador en `diseños/`. |
| Modo | Un jugador, sin combate ni multijugador previstos. |
| Plataformas | Steam: Windows y macOS. |
| Motor | Godot 4 + GDScript; usar renderizador Compatibility como línea base mientras funcione correctamente. |
| Arte | Sprites y hojas de animación en PNG a resolución de píxel (el mundo se ve a unos 427 × 240 y se escala ×3 sin suavizado). |
| Interfaz | **Solo inglés** en la primera versión. Este documento y comentarios de desarrollo pueden estar en español. |
| Duración de la historia | **2–3 horas** aproximadamente, **incluyendo varios renacimientos**; validar con jugadores reales. |
| Cantidad inicial de máquinas jugables | **6–10**, no más por obligación; las seis primeras tienen tipología definida. |
| Final | Comprar la **llave de la tienda** como última mejora en el ordenador de recepción, usarla en la puerta, salir, escena final y créditos. |
| Después de los créditos | **Modo libre** para seguir jugando; la historia puede darse por completada. |
| Monetización | **PROPUESTA heredada:** juego premium, sin microtransacciones, sin compras de fichas con dinero real; precio comercial pendiente. |

### 1.1. Pilares de diseño — CONFIRMADOS

1. **Progresión visible en un lugar físico.** El espacio parece grande, con pasillos llenos de máquinas de diferentes precios. Al principio casi ninguna es asequible.
2. **Decisiones sencillas y frecuentes.** Cada premio se **vende ahora** para conseguir monedas o se **conserva** para avanzar su colección; ambas rutas tienen ventajas claras.
3. **Colecciones por tipo de figura.** Completar varias copias del **mismo tipo de figura** desbloquea una bonificación temporal y genera puntos de prestigio pendientes **una vez por ciclo**.
4. **Dos economías separadas.** Las **monedas** se gastan en la **recepción** y las máquinas durante el ciclo. Los **puntos de prestigio** solo se gastan al **dormir/renacer en el sofá** y generan mejoras permanentes.
5. **Automatización progresiva.** Se empieza insertando monedas y girando manivelas; más adelante robots comprados en recepción realizan tareas, y el prestigio acelera los ciclos sucesivos.
6. **Tensión amable, sin castigos irreversibles.** La economía puede obligar a regresar a máquinas baratas, pero nunca debe dejar al jugador sin manera de ganar dinero.
7. **Misterio ambiental con final.** No se explica de inmediato cómo llegó el jugador. La motivación última es poder abrir la puerta y salir.

### 1.2. Qué NO es GachaNight

- No es pixel art ni un juego voxel: **ni el local ni las figuras** deben verse deliberadamente pixelados.
- No es un gacha de dinero real ni un sistema de monetización con tiradas pagadas externamente.
- No es un simulador complejo de gestión empresarial, un juego de combate ni un arcade exigente de precisión.
- No requiere NPC físicos ni largos diálogos para explicar la historia.
- No obliga al jugador a ir a un cambiador de monedas cada vez que venda una figura.
- No permite gastar puntos de prestigio desde un menú abierto en cualquier lugar.
- El **personaje llorando creado a partir de pixel art en una prueba de Blender no pertenece al juego**; jamás usarlo como referencia de su catálogo ni dirección artística oficial.

## 2. Resumen de la experiencia completa

**Primera partida:** el protagonista despierta en el baño de una tienda apagada. Encuentra tres monedas, localiza un interruptor y enciende todo el local de golpe. Las máquinas iluminadas parecen caras; descubre un gachapón de una moneda. Aprende a girar, recibir una cápsula, ver la figura y venderla o guardarla. El jugador ahorra hasta poder probar la segunda máquina, de 50 monedas, y tras usarla por primera vez se habilita el sistema de renacimiento.

**Partidas intermedias:** las colecciones completas proporcionan habilidades temporales y puntos pendientes. El jugador vende premios para financiar tiradas y compras en el ordenador de recepción, donde un vendedor digital exageradamente entusiasta ofrece mejoras, robots y automatización. Renace en el sofá en varias ocasiones, comprando habilidades permanentes que hacen más rápidas las partidas posteriores y abren posibilidades de estrategia.

**Partida de resolución:** con las habilidades acumuladas y los robots de ese ciclo, alcanza las máquinas más caras, compra las mejoras necesarias en la recepción y finalmente adquiere la llave de salida. Se dirige a la puerta de la tienda, la abre y ve el final y los créditos. Queda disponible el modo libre.

**Bucle:** `explorar → pagar tirada → obtener figura → vender o conservar → avanzar colección y/o dinero → comprar mejoras y robots en recepción → completar colecciones → acumular prestigio → sofá/renacimiento → repetir más rápido → comprar llave → escapar`.

## 3. Tutorial interactivo e inicio de ciclo

### 3.1. Primer ciclo — CONFIRMADO

1. El jugador aparece en **el baño**, dentro de un local oscuro y vacío. La puesta en escena dura poco y entrega rápidamente el control.
2. Ve **tres monedas físicas en el suelo** y aprende a recogerlas. El saldo inicial base es **3 monedas**.
3. Encuentra el **interruptor general**. Al activarlo, el local entero se enciende con una secuencia breve de luces, motores, carteles iluminados y sonido de máquinas arrancando.
4. Observa la escala del establecimiento y máquinas visibles con precios muy superiores a su dinero.
5. Descubre el **gachapón 001**, que cuesta **1 moneda**.
6. Hace una tirada manual: insertar/pagar, mover manivela o accionar la máquina, abrir/revelar cápsula y resolver el premio. Las animaciones completas pueden añadirse por hitos, pero el flujo de decisiones debe funcionar desde el primer prototipo.
7. El panel de resultado enseña figura, rareza, valor de venta, progreso de su **colección particular** y los botones **Sell** y **Keep**.
8. Vender da monedas **inmediatamente en la misma interacción**. Guardar aumenta el contador del tipo de figura y consume irrevocablemente esa copia.
9. Se enseña el álbum de figuras con siluetas desconocidas y cómo se revelan al encontrar una figura, aunque luego se venda.
10. Con esfuerzo, llega a **50 monedas** y prueba **el gachapón 002**.
11. **Después de utilizar la máquina 002 por primera vez**, se desbloquea el prestigio en el sofá y se presenta su funcionamiento mediante una indicación contextual breve. Este momento marca el final del tutorial principal.
12. Desde entonces el jugador decide cuándo acumular más colecciones, utilizar recepción o acudir al sofá a renacer.

**No adelantar el desbloqueo del prestigio:** completar una colección antes de usar la máquina 002 puede generar puntos pendientes, pero **no habilita** su gasto anticipadamente.

### 3.2. Renacimientos posteriores — CONFIRMADO + PROPUESTA DE UX

- **CONFIRMADO:** cada renacimiento devuelve al jugador al baño y reinicia el ciclo económico.
- **CONFIRMADO:** solo persisten habilidades de prestigio, puntos no gastados, catálogo descubierto y el metaprogreso necesario para reconocer el final/modo libre.
- **PROPUESTA TÉCNICA:** abreviar la introducción en ciclos repetidos, conservar una interacción reconocible con el interruptor salvo si una habilidad permanente la automatiza, y permitir mejoras para comenzar con las tres monedas recogidas.
- **PROPUESTA TÉCNICA:** el tutorial de desbloqueo del sofá se muestra una única vez; el acceso a la mecánica en ciclos posteriores permanece habilitado como parte del conocimiento adquirido por el jugador. No repetir la exigencia de usar de nuevo la máquina 002 para reabrir el sofá, pues frustraría el prestigio. Persistir el indicador de tutorial completado como metadato, no como bonificación de juego.

## 4. Diseño del espacio y recorrido

La tienda debe sentirse **grande, recargada en cantidad de máquinas y sorprendentemente profunda**, sin ser laberíntica ni difícil de navegar. Inspiración: tiendas recreativas y jugueterías japonesas de los **80–90**, no un salón de neón cyberpunk moderno.

**Zonas funcionales:**

| Zona | Función |
|---|---|
| Baño | Spawn inicial y de cada renacimiento; primeras monedas y apertura narrativa. |
| Pasillo de interruptor | Secuencia de encendido y primera revelación del local. |
| Gachapones accesibles | Máquina 001, enseñanza del bucle, acceso visual a la 002–004. |
| Galería de máquinas | Otras filas, aparatos decorativos y sensación de escala; no confundir decoración con máquinas utilizables. |
| Sección de grúas | Máquina 005 de gancho y premios visibles. |
| Sección de juegos de bolas | Máquina 006 de plinko. |
| **Recepción** | Mostrador y **ordenador vendedor con personalidad** para mejoras, robots y llave final, pagados con monedas. |
| Sala de empleados | **Sofá**: único lugar de selección y confirmación de habilidades de prestigio. |
| Puerta principal | Permanece cerrada hasta comprar la llave; interacción final para salir. |
| Almacén/vitrinas/carteles | Ambientación y oportunidades de expansión, sin mecánicas obligatorias inventadas. |

**Normas de circulación:** el jugador debe identificar la máquina 001 y la recepción con facilidad; las animaciones repetidas y ventas no deben imponer desplazamientos innecesarios. La sala del sofá debe ser localizable, pero físicamente distinta del ordenador de recepción. La puerta de salida debe ser reconocible desde temprano como objetivo narrativo sin revelar al principio el precio de la llave, si ello estropea el descubrimiento.

**Propuesta:** utilizar señales discretas en inglés, indicadores interactivos al acercarse, composición de luz por zonas y un mapa simplificado opcional si los playtests detectan desorientación.

## 5. Máquinas: orden, reglas y costes

### 5.1. Orden inicial — CONFIRMADO

| Orden | Tipo | Coste/tirada | Regla especial |
|---|---|---:|---|
| `machine_001` | Gachapón clásico | **1 moneda** | **Exactamente cinco tipos de figuras.** El premio más barato se vende por **1 moneda** como mínimo. |
| `machine_002` | Gachapón | **50 monedas** | Su premio menos valioso se vende por **30 monedas**. La primera utilización desbloquea prestigio. |
| `machine_005` | Máquina de gancho/grúa | EJEMPLO DE BALANCE | Interacción propia, pero decisión común **Sell / Keep**. |
| `machine_006` | Plinko | EJEMPLO DE BALANCE | Bola/ficha y resultado legible, con **Sell / Keep**. |
| Más máquinas | **PENDIENTE** | EJEMPLO DE BALANCE | Se añadirán **solo si aportan valor**; la tienda se ampliará cuando haga falta. |

**Decisión del creador (2026-10-12):** la tienda empieza con **cuatro máquinas** (gachapones 001 y 002, grúa 005 y plinko 006) y una sala más pequeña. Los gachapones 003 y 004 del plan inicial se retiraron; el segundo gachapón conserva las reglas confirmadas (50 monedas, venta mínima 30, desbloquea el prestigio).

Los costes a partir de la tercera máquina **no están confirmados**. Codex creará tablas de ejemplo y permitirá editarlas como datos, no lógica rígida.

### 5.2. Flujo universal de premio — CONFIRMADO

1. Validar que no hay otra recompensa pendiente y que el coste es pagable.
2. Pagar exactamente una vez; registrar la tirada.
3. Elegir un premio utilizando la tabla de probabilidades del aparato, con efectos de suerte válidos y pesos normalizados.
4. Marcar el ID de la figura como **descubierto permanentemente en el catálogo al revelarla**, incluso si más tarde se vende.
5. Abrir la elección de premio con valor, rareza, progreso de colección y advertencias apropiadas.
6. Si **Sell**: entregar dinero directamente y consumir esa instancia de premio. Sin caminar a una máquina de cambio.
7. Si **Keep**: consumir esa instancia y aumentar en 1 el contador de **esa figura concreta** del ciclo. Si llega al umbral, completar la colección de ese tipo y otorgar **un único premio de prestigio pendiente** y **una única bonificación temporal**.
8. La resolución es atómica. Pulsar dos veces no vende dos veces ni permite vender y guardar simultáneamente.

**Nunca generar una recompensa vendible ilimitadamente sin pagar una nueva tirada.** La venta, colección, puntos y bonificaciones deben estar protegidos de reentradas.

### 5.2 bis. Escenas de máquina y sala como lobby — CONFIRMADO (2026-10-12)

- La sala de máquinas es el **lobby**: el jugador camina entre máquinas y con `E` **entra** en una. No sale la figura directamente.
- Dentro, la máquina se ve de frente, como en primera persona, y se **juega a mano**: gachapón (mantener `E` para girar la manivela), grúa (`A`/`D` mueve la garra, `E` la suelta), plinko (`A`/`D` elige columna, `E` suelta la bola).
- Desde dentro se puede **saltar directamente a otra máquina** (`Q`/`R`, `1`–`4` o las pestañas) o **salir al pasillo** (`Esc`). Al salir, el personaje queda delante de la última máquina usada.
- El flujo de premio de 5.2 no cambia: se paga al meter la moneda, el premio queda decidido y guardado en ese momento, y termina en Sell/Keep. **Pendiente de decisión:** si la habilidad del jugador debe influir en el premio; hoy no influye.
- Primera versión con formas simples; el arte de estas escenas es provisional.

### 5.3. Una figura ya completada no puede guardarse más — CONFIRMADO

Si el contador de una figura es igual a su requisito (`copies_held >= copies_required`):

- **Keep** se deshabilita u oculta para premios nuevos de ese mismo tipo.
- Debe indicarse en inglés por qué: `Collection completed — sell this duplicate.`
- Se permite **Sell** y la figura puede seguir saliendo según su probabilidad; **no eliminarla de las tablas de azar** para que el sistema siga equilibrado.
- **No** se ganan más puntos, copias ni bonificaciones por ese tipo en el ciclo actual.
- No aplicar «colección completa» por obtener una sola figura aislada, a menos que su umbral configurado sea 1 (posible para rarezas altas).

### 5.4. Regla económica anti-bloqueo — CONFIRMADO

- Si tras pagar la tirada el dinero restante es **≤ 1 moneda**, no se permite **Keep** en esa recompensa y debe ofrecerse **Sell** con una advertencia en inglés equivalente a: `If I run out of money, I'll be stuck here forever.`
- La máquina 001 cuesta 1 y **cualquier figura de esa máquina se puede vender por al menos 1 moneda** (incluso con modificadores: limitar valores efectivos para evitar 0).
- Debe existir una ruta garantizada para volver a la máquina 001 y ganar monedas; no bloquear su uso por desbloqueos arbitrarios ni por robots.
- Si el jugador inicia con tres monedas y después de pagar le quedan dos, puede guardar. Si le queda una o ninguna, debe vender.
- El saldo después de pagar se evalúa para la decisión **de ese premio**; vender no reabre retroactivamente **Keep**.
- **PROPUESTA TÉCNICA:** detector de estados imposibles y recuperación discreta únicamente como defensa frente a fallos de software. Evitar regalos constantes de moneda que permitan abusar de la economía.
- Las automatizaciones no pueden ejecutar una acción que viole esta regla o consuma dinero que el jugador no tiene.

### 5.5. Gancho y plinko — alcance

**Gancho:** minijuego ligero, breve, táctil y visual; no se exige habilidad extrema. Puede incorporarse azar controlado y luego automatizarse. Si un intento puede fallar sin premio, **esa regla no está aprobada** y debe discutirse: preferir un diseño de resultado con premio garantizado para preservar el mismo bucle económico, al menos en el primer prototipo.

**Plinko:** caída visible de bola y premio resultante, con pesos claros y consistencia entre cálculo y animación. No simular físicamente miles de bolas simultáneas para generar ingresos automatizados.

## 6. Rareza: exactamente cinco niveles

**CONFIRMADO:** hay **cinco rarezas**, de común a la máxima categoría legendaria/secreta. Las colecciones escalan en requisito y recompensa según rareza. El número de copias definitivo se afinará con pruebas.

**PROPUESTA DE NOMBRES EN INGLÉS E IDs INTERNOS ESTABLES** (no se ha fijado aún si la última se mostrará como `Legendary` o `Secret`):

| ID interno | Nombre de UI propuesto | Función |
|---|---|---|
| `common` | Common | Muy frecuente, precio y prestigio bajos. |
| `uncommon` | Uncommon | Frecuente, un escalón por encima. |
| `rare` | Rare | Figura notable. |
| `epic` | Epic | Muy escasa. |
| `legendary` | Legendary / Secret | Rareza máxima. **No crear una sexta rareza** solo por mostrar «Secret». |

**Ejemplo de curva editable, NO valores cerrados:**

| Rareza | Probabilidad orientativa dentro de una máquina con 5 tipos, uno de cada rareza | Copias para completar **una figura de ese tipo** | Puntos de prestigio por completar | Idea de bonificación temporal de colección |
|---|---:|---:|---:|---|
| Common | 50 % | 5 | 1 | +5 % a ventas. |
| Uncommon | 28 % | 4 | 2 | -5 % al coste de tiradas, con suelo seguro. |
| Rare | 14 % | 3 | 4 | +10 % a velocidad de automatización. |
| Epic | 6 % | 2 | 8 | +5 % a probabilidad relativa de rarezas altas. |
| Legendary / Secret | 2 % | 1 | 16 | +10 % a venta o ventaja destacada temporal. |

**Importante:** raras requieren **menos copias** en esta propuesta porque aparecen con menor frecuencia; su completar sigue siendo más difícil estadísticamente. Se considera **una colección independiente por ID de figura**, no «conseguir las cinco rarezas» ni «conseguir todas las figuras de una máquina». Una máquina puede tener una distribución de rarezas distinta a este ejemplo; la 001 sí tiene cinco tipos de figuras, pero no es obligatorio que exista exactamente una de cada rareza si el balance posterior recomienda otra distribución.

Una bonificación pertenece a **la colección completada de ese tipo**, no a un individuo suelto. Dos colecciones diferentes pueden otorgar efectos diferentes, incluso de la misma rareza. Evitar buffs multiplicativos sin límite que rompan el tiempo de juego; explicitar reglas de acumulación.

## 7. Figuras, copias, álbum y colecciones

### 7.1. Distinción entre cuatro conceptos — CRÍTICA

1. **Definición de figura (`figure_id`):** tipo de figura, con ID estable, nombre, modelo, rareza, precio de venta, máquina(s), requisito de copias y bonificación de colección.
2. **Descubrimiento histórico:** booleano permanente por tipo. Se activa en la **primera revelación** del premio y no se borra nunca por renacer. No exige guardarlo.
3. **Copias guardadas en ciclo:** contador temporal por `figure_id`; sube exclusivamente al usar **Keep**, hasta el umbral. Las copias guardadas no se pueden vender después.
4. **Colección de ese tipo completada en ciclo:** `copies_held == copies_required`; se ha otorgado una sola vez su prestigio pendiente y su bonificación temporal. El flag desaparece al renacer.

**Ejemplo:** la máquina tiene gato, perro, conejo, rana y oso. Conseguir **5 conejos** (si el conejo requiere 5) completa **la colección de conejo** aunque no hayas conservado un gato. No hace falta conseguir una unidad de cada uno de los cinco para completar una «colección de máquina».

### 7.2. Catálogo siempre visible — CONFIRMADO

- El catálogo/álbum puede abrirse **desde el inicio**, sin comprar habilidad.
- Incluye las entradas de **todas las figuras planificadas en los datos del juego**; el jugador ve que existen, aunque todavía no las haya descubierto. La capacidad de mostrar siluetas no debe revelar premios secretos mediante textos que los identifiquen.
- Si `discovered == false`: mostrar **la silueta del sprite o miniatura de esa figura oscurecida/en negro**, sin sus colores, rostro ni detalles del material; nombre como `???` u otro placeholder en inglés. No usar un cuadro idéntico para todas las figuras: la **silueta debe corresponder a cada forma real**.
- Si `discovered == true`: mostrar figura/miniatura, nombre, rareza y otros datos autorizados; mantenerla revelada **para siempre, incluso después de renacer**.
- Se descubre al **verla salir de la máquina**, aunque se elija venderla. No confundir `discovered` con el contador de copias guardadas.
- El catálogo **no otorga automáticamente puntos, monedas ni bonificaciones permanentes** por consultar o revelar figuras.
- **PROPUESTA TÉCNICA:** la miniatura es el propio sprite de la figura; la silueta es ese mismo sprite teñido de oscuro conservando su alpha. Debe ser legible y barato.
- **Bases por rareza — CONFIRMADO (2026-10-11):** toda figura descubierta se muestra sobre una base que identifica su rareza; cuanto más rara, más compleja y reconocible (de un disco liso en Common a un trofeo dorado animado en Legendary). La silueta de una figura no descubierta **nunca** muestra base, para no delatar su rareza.
- **PROPUESTA DE UX:** vista del álbum con pestañas por máquina, filtros por rareza, `Discovered X/Y`, progreso temporal `X/N` y marca `Completed this run` cuando proceda. Las figuras vendidas siguen descubiertas.

### 7.3. Completar una colección de figura — CONFIRMADO

Cuando se acumulan las copias requeridas de un tipo durante un ciclo:

1. Registrar `completed_this_run[figure_id] = true` antes de aplicar cualquier otro efecto.
2. Agregar puntos de prestigio a `pending_prestige` **exactamente una vez en ese ciclo**, de acuerdo con la rareza y cualquier mejora permanente pertinente.
3. Activar **la bonificación temporal específica de ese tipo de figura**, con efecto visible y duración hasta el siguiente renacimiento.
4. Mostrar una notificación breve y satisfactoria con nombre, recompensa, bonificación y marca del álbum.
5. Desactivar la posibilidad de **Keep** para futuros duplicados del mismo tipo, dejando disponible **Sell**.
6. Guardar el estado para que cerrar el juego no conceda la recompensa por segunda vez.

**Estas dos recompensas ocurren juntas, pero son conceptos diferentes:**

- **Puntos de prestigio:** quedan pendientes hasta el sofá; no se gastan en la tienda.
- **Bonificación de colección:** afecta a la **partida actual**; se **pierde totalmente al renacer**.

Esto **sustituye** expresamente la regla antigua de prototipos que decía «las figuras coleccionadas nunca generan pasivas». La regla vigente es: **ninguna copia aislada otorga mejoras; solo completar el umbral de cada figura da una bonificación temporal y prestigio**.

### 7.4. Casos de borde

- Obtener una figura que aún no se conoce siempre la registra en el catálogo antes de venderla.
- Si `copies_required = 1`, una única copia guardada completa esa **colección individual**; válido para un legendario si el balance lo decide.
- Si se consigue una copia adicional de un tipo terminado, **solo vender**; no reiniciar el contador ni volver a otorgar recompensas.
- Si el jugador tiene exactamente la cantidad necesaria y pulsa repetidas veces **Keep**, solo puede finalizar una vez.
- Si se cancela el panel de premio, debe poder retomarse sin perder el premio ni obtenerlo dos veces.
- La lógica de suerte o descuentos no modifica inadvertidamente si una colección está completada.
- El catálogo puede conservar imágenes/vistas históricas, pero el contador visible de copias siempre refleja el ciclo actual, no el total acumulado en todos los renacimientos.

## 8. Dos sistemas de progresión que NO deben confundirse

| Elemento | **Ordenador de recepción** | **Sofá / prestigio** |
|---|---|---|
| Moneda | Monedas del ciclo. | Puntos de prestigio (pendientes del ciclo + ahorrados). |
| Cuándo | Durante el juego normal, al interactuar con recepción. | Únicamente al preparar y **confirmar** dormir/renacer en el sofá. |
| Qué ofrece | Mejoras de economía, máquinas, comodidad local, robots, automatizaciones y **llave final**. | Mejoras **permanentes** de progreso, eficiencia, calidad de vida, suerte o apoyo a automatización. |
| Duración | **Temporal, solo el ciclo actual.** | **Permanente**, afecta a ciclos siguientes. |
| Interfaz | PC retro japonés de vendedor comercial absurdo. | Árbol de habilidades y confirmación de renacimiento. |
| Se conserva al renacer | **No**: ni mejoras ni robots ni llave comprada en el ciclo anterior. | **Sí**: habilidades ya aplicadas y puntos no gastados. |
| Excepción | La **finalización de la historia y el desbloqueo del modo libre** son metaprogreso persistente. | La colección de puntos no gastados también es persistente. |

**Regla central:** mientras se juega se puede comprar en **recepción**, pero **no** se puede comprar ninguna mejora de **prestigio**. No añadir botón de gastar prestigio a HUD, inventario ni ordenador. Ningún robot ni bonificación de colección permite vulnerar esto.

## 9. El ordenador de recepción — CONFIRMADO

### 9.1. Localización y personalidad

- **Ubicación fija:** mostrador de recepción del establecimiento.
- **Objeto:** ordenador con estética **electrónica japonesa comercial de finales de los 80 y los 90**; monitor CRT estilizado, botones/pegatinas, carcasa de plástico, interfaz animada sencilla.
- **Personalidad elegida por el creador: C — vendedor comercial exagerado y absurdo.** Habla como un dependiente o mascota de ventas obsesionado con vender mejoras, robots y ofertas. Puede ser cómico y ligeramente sospechoso, pero no adoptar una personalidad siniestra como rasgo dominante.
- No es un NPC físico. Su personalidad se expresa con texto breve, sonidos, carita en pantalla e intervenciones ocasionales (no bloquear la interacción por diálogos largos).
- **Idioma:** todos sus mensajes para el jugador en **inglés**.

**Ejemplos de tono, no diálogos definitivos:** `Fantastic choice!`, `Your productivity is my happiness!`, `Just one more upgrade!`, `Today's special: more money!`, `No refunds! Probably!`.

### 9.2. Tienda interna del ordenador

Categorías iniciales propuestas, sujetas a economía:

- **Income:** subir valores de venta, multiplicadores suaves y ganancias de máquinas.
- **Machines:** acelerar tiradas, reducir tiempos, mejoras o descuentos locales.
- **Automation:** comprar **robots** que accionen máquinas, recojan resultados y sigan reglas de venta/colección.
- **Convenience:** reducción de animaciones e interacción repetida, mejoras de organización.
- **Exit / Special:** la **llave de la puerta**, **última mejora de recepción**, con requisitos de progresión y precio ajustados para completar la historia tras 2–3 h.

Los precios, niveles, efectos exactos y prerrequisitos **no están cerrados**. Codex debe construir un esquema de configuración y una tabla inicial de ejemplo, dejando etiquetas de datos provisionales.

**Confirmado:** todo lo comprado con monedas, incluidos los robots, se pierde al renacer. No añadir compras eternas con monedas ni «robots permanentes» desde recepción.

### 9.3. La llave: última mejora y condición final — CONFIRMADO

- La última compra relevante de la ruta principal en recepción es `store_exit_key`.
- Al poder comprarla, debe requerir monedas suficientes, y puede comprobar requisitos de progreso definidos por la tabla de balance (no inventar condiciones narrativas adicionales permanentes sin aprobación).
- Comprar la llave **no teletransporta inmediatamente al final**. El jugador **debe ir físicamente a la puerta de la misma tienda y abrirla**.
- Tras la apertura: escena final, salida del establecimiento y **créditos**.
- La compra de la llave debe tener validación atómica y un estado claro `key_owned_this_run`.
- El coste debe funcionar como meta económica alcanzable tras varios renacimientos y compras estratégicas, no como un muro de espera artificial.
- **PROPUESTA TÉCNICA:** no permitir comprar la llave antes de disponer de las mejoras de progreso acordadas para el final; representar esos requisitos en datos, visibles en inglés. El orden de compra de mejoras previas es de balance, no una verdad cerrada.

## 10. Robots y automatización — CONFIRMADO + PROPUESTAS

### 10.1. Intención

Al principio cada tirada es física; posteriormente el jugador compra robots de estilo **juguete mecánico japonés retro**, simpáticos y sencillos, que le ahorran operaciones. La fantasía es ver progresar la tienda hacia una pequeña red de máquinas activas sin convertirla en un simulador de fábricas complejo.

### 10.2. Comportamientos de ejemplo — EJEMPLO DE BALANCE

| Robot/mejora de recepción | Comportamiento orientativo |
|---|---|
| Auto Crank | Acciona automáticamente un gachapón seleccionado cuando hay monedas. |
| Toy Sorter | Decide **Keep** cuando falta completar la colección del tipo y **Sell** cuando está terminada, respetando protección económica. |
| Seller Bot | Vende premios según filtros; no vende los reservados explícitamente para colección. |
| Floor Supervisor | Gestiona varias máquinas desbloqueadas con prioridades y presupuesto. |
| Faster Servos | Aumenta operaciones automáticas por segundo dentro de límites seguros. |

**Estos nombres y números son propuestas**, no un catálogo aprobado de robots. Las habilidades permanentes de prestigio pueden mejorar velocidad, inteligencia, precio o número máximo de robots comprables en los ciclos siguientes, **pero no crear gratis un robot de recepción salvo si esa habilidad está explícitamente diseñada y aprobada**.

### 10.3. Reglas obligatorias de automatización

- Respetar presupuesto, coste de tiradas y regla anti-bloqueo.
- No crear monedas, copias ni prestigio por doble resolución del mismo premio.
- Si se usa un filtro «coleccionar hasta completar», **no** intentar guardar una figura completada.
- Permitir pausar/desactivar robots y consultar en UI qué hacen.
- Distinguir acción de fondo (**simulación numérica barata**) de efectos visuales: no instanciar miles de cápsulas, partículas o colisiones.
- Limitar ritmo y complejidad para rendimiento en equipos modestos.
- No establecer ganancias offline/AFK con el juego cerrado de forma automática: **producción offline está PENDIENTE y fuera del alcance inicial**.
- Al renacer detener robots, cancelar tareas en vuelo de forma segura, borrar sus compras y reiniciar las máquinas.

## 11. Prestigio, sofá y renacimiento — CONFIRMADO

### 11.1. Desbloqueo

**No está disponible durante el tutorial inicial.** Se desbloquea **después de usar por primera vez la máquina 002 de 50 monedas**. Mostrar indicación diegética o UI breve que guíe al sofá; evitar interrupción larga. Los puntos pendientes obtenidos antes siguen contando, pero no pudieron gastarse antes de este evento.

### 11.2. Cómo se ganan los puntos

- Cada **colección de tipo de figura** completada en el ciclo genera prestigio **solo una vez**.
- Cuanto más rara sea la figura, más puntos debería generar. Cantidades concretas ajustables en tablas.
- Tener copias incompletas **no da puntos parciales**.
- Revelar una figura en el catálogo, por sí solo, **no da prestigio**.
- La recompensa se añade automáticamente a `pending_prestige` en el momento de completar la colección. **No puede gastarse hasta el sofá.**
- Un mismo tipo puede volver a otorgar puntos **en otro ciclo**, una vez completado de nuevo su contador desde cero.

### 11.3. Flujo de menú de sofá

1. Interactuar físicamente con el **sofá** de la sala de empleados.
2. Mostrar un menú especial con puntos **ahorrados** (`banked_prestige`) + puntos **pendientes** (`pending_prestige`) y el árbol de habilidades.
3. Elegir provisionalmente mejoras **permanentes** y niveles. Mostrar coste total, prerrequisitos, saldo resultante y descripción de efectos.
4. Si el jugador pulsa **Cancel / Back / Esc**, cerrar sin comprar, sin descontar, sin renacer y sin perder el ciclo.
5. Si pulsa **Sleep & Rebirth**, volver a validar puntos y requisitos; en una transacción atómica convertir pendientes en banco, descontar **solo** lo gastado, aplicar habilidades permanentemente, reiniciar el estado del ciclo y empezar en el baño.
6. Reproducir una transición visual breve de dormir/negro/despertar.

**No son válidas** compras inmediatas desde el menú sin renacimiento, ni compras fuera del sofá, ni consumos de puntos al seleccionar opciones preliminares.

### 11.4. Los puntos restantes se guardan — CONFIRMADO

**Ejemplo:** el jugador llega al sofá con 20 puntos totales, compra habilidades por 15 y renace. Los **5 puntos sobrantes** se conservan para el siguiente ciclo, además de los puntos que gane en él. Los puntos pendientes y el banco no se duplican al renacer ni al cargar un guardado.

**Fórmula en confirmación:** `new_banked_prestige = old_banked_prestige + pending_prestige - approved_spend` con `approved_spend <= old_banked_prestige + pending_prestige` y no negativo. Tras confirmar: `pending_prestige = 0` y contadores temporales reiniciados.

### 11.5. Qué se reinicia y qué se conserva

| Estado | Tras renacer | Justificación |
|---|---|---|
| Monedas y dinero acumulado | **Se reinicia.** | Ciclo económico. |
| Copias guardadas de cada figura | **Se reinician a 0.** | Colecciones repetibles por run. |
| `completed_this_run` | **Se vacía.** | Permite volver a generar prestigio por colección en el siguiente ciclo. |
| Bonificaciones concedidas por completar figuras | **Se eliminan.** | Ventajas temporales. |
| Mejoras compradas con monedas en recepción | **Se pierden.** | Economía temporal. |
| Robots comprados en recepción, sus niveles y asignaciones | **Se pierden.** | Automatización temporal. |
| Progreso y estados temporales de las máquinas | **Se reinician.** | Inicio de un nuevo ciclo. |
| Llave comprada en recepción, si se renace antes de salir | **Se pierde como objeto de ciclo.** | Debe comprarla en el ciclo final para escapar. |
| Habilidades de prestigio ya confirmadas | **Se conservan.** | Progresión permanente. |
| Puntos de prestigio sin gastar | **Se conservan.** | Ahorro permanente. |
| Catálogo de figuras descubiertas | **Se conserva.** | Metacolección visual permanente. |
| Desbloqueo/tutorial del prestigio | **Se conserva.** | No repetir artificialmente el tutorial en cada run. |
| Historia completada y modo libre desbloqueado | **Se conservan.** | Metaprogreso narrativo. |
| Opciones de audio, controles, resolución | **Se conservan.** | Preferencias del usuario, no ventajas de juego. |

Esto interpreta «todo se reinicia salvo habilidades permanentes» con las **excepciones expresamente confirmadas** del catálogo, puntos no gastados y modo libre. No confundir historial de descubrimientos con figuras poseídas actualmente.

## 12. Árbol de habilidades permanentes — propuesta de arquitectura

**CONFIRMADO:** mezcla de mejoras únicas y por niveles, compradas exclusivamente con prestigio al renacer; ofrecen aceleración de runs, economía, suerte, calidad de vida y ayuda a la automatización.

**EJEMPLO DE CONTENIDO** (nombres, costes, rangos y dependencias provisionales):

| Rama | Habilidad ejemplo | Tipo | Efecto previsto |
|---|---|---|---|
| Comodidad | Ready Pockets | Única | Empieza los ciclos con las 3 monedas iniciales directamente en el saldo. |
| Comodidad | Quick Capsules | Única | Acelera apertura/revelación de cápsulas. |
| Comodidad | Bulk Interaction | Por niveles | Reduce la fricción de tiradas manuales repetidas. |
| Economía | Starting Tip | Por niveles | Agrega monedas al inicio, sin permitir un bucle infinito trivial. |
| Economía | Better Appraisal | Por niveles | Incrementa valores de venta. |
| Economía | Efficient Spending | Por niveles | Descuento moderado en máquinas, sin bajar de los mínimos económicos seguros. |
| Suerte | Lucky Bearings | Por niveles | Incrementa la probabilidad relativa de rarezas superiores sin eliminar las comunes. |
| Colecciones | Efficient Collector | Por niveles | Puede reducir requisitos de copias con suelo >=1, manteniendo balance. |
| Colecciones | Prestige Knowledge | Por niveles | Puede aumentar puntos por colección, con límites. |
| Automatización | Robot Training | Por niveles | Mejora rendimiento de robots que aún deben comprarse con monedas en recepción. |
| Automatización | Automation Presets | Única | Permite recordar preferencias de selección, pero se reinician robots y compras. |

El **catálogo base está siempre disponible** y no debe aparecer como habilidad bloqueada. Tampoco convertir el acceso al sofá, obtenido con la máquina 002, en una compra permanente adicional.

**Criterios de diseño del árbol:** varias rutas viables, beneficios apreciables desde los primeros prestigios, ninguna compra obligatoria que resulte inútil, costes editables, UI clara en inglés y sin pérdida de puntos por cancelar.

## 13. Bonificaciones temporales de colecciones

**CONFIRMADO:** hay una bonificación **por cada colección de tipo de figura completada**; no por simple obtención individual ni por completar todas las figuras de una máquina.

**Ejemplos modificables de efectos:** incremento moderado de valor de venta; tiradas un poco más rápidas; descuentos pequeños; mejora limitada de suerte; eficiencia de robots; menor duración de animaciones; multiplicador de recompensa contextual. Deben ser lo bastante útiles como para competir con la venta directa de premios.

**PROPUESTA TÉCNICA:**

- Guardar el efecto en la definición de cada figura como `collection_bonus_id` + parámetros.
- Activar un efecto solo en la transición `incomplete → completed` del ciclo.
- Mantener en el estado de ciclo un listado de efectos activos para recomputar estadísticas sin alterar irreversiblemente los valores base.
- Al renacer, eliminarlos y recalcular atributos exclusivamente desde habilidades permanentes + mejoras de recepción que existan en el **nuevo** ciclo.
- Definir un orden estable de aplicación de modificadores, por ejemplo `base → prestigio permanente → mejora de recepción → bonus de colección`, con límites para evitar costes 0 y probabilidad >100 %.
- Mostrar en UI las bonificaciones activas y su procedencia. No dejar poderes ocultos imposibles de entender.

**No inventar qué figura exacta da qué efecto definitivo:** eso requiere tablas iniciales y playtests.

## 14. Economía: qué cifras son fijas y cuáles se pueden cambiar

### 14.1. Invariantes cerradas

- Comienzo del primer ciclo: **3 monedas**.
- Primera máquina: **coste 1**, **5 tipos** de figuras, **venta mínima 1**.
- Segunda máquina: **coste 50**, **venta mínima 30**.
- Monedas no negativas; venta inmediata; protección anti-bloqueo con saldo post-tirada ≤1.
- Prestigio solo por **colección completa de un tipo**, una vez por run, con más puntos para rarezas mayores.
- La recepción consume monedas; el sofá consume puntos de prestigio **solo al confirmar renacimiento**.
- La llave final se compra en recepción y debe ser alcanzable tras aproximadamente **120–180 minutos** de juego normal en varios ciclos.

### 14.2. Ejemplo de tabla de figuras de la primera máquina — NO DEFINITIVO

La siguiente tabla es un **punto de partida para implementar datos y probar**, no un acuerdo sobre nombres ni economía final:

| ID de prueba | Rareza | Peso | Venta base | Copias para colección | Prestigio por completar |
|---|---|---:|---:|---:|---:|
| `g001_toy_01` | Common | 50 % | 1 | 5 | 1 |
| `g001_toy_02` | Uncommon | 28 % | 2 | 4 | 2 |
| `g001_toy_03` | Rare | 14 % | 4 | 3 | 4 |
| `g001_toy_04` | Epic | 6 % | 8 | 2 | 8 |
| `g001_toy_05` | Legendary | 2 % | 16 | 1 | 16 |

**Esta tabla sustituye a los números provisionales de prototipos anteriores**, que también eran ejemplos. Los cinco tipos de la primera máquina y los mínimos económicos **sí son definitivos**; la curva propuesta se evaluará por tiempo medio de completar un tipo y por capacidad de financiar nuevas tiradas.

### 14.3. Ejemplo de arranque para máquina 002 — NO DEFINITIVO

- Precio: **50** (**fijo**).
- Venta mínima: **30** (**fija**).
- Otros premios, rarezas, probabilidades y multiplicadores: definir configurables, procurando que un resultado común fuerce a veces volver a la primera máquina, sin convertir el progreso en espera frustrante.
- **No** fijar 5 figuras en todas las máquinas: solo la máquina 001 tiene 5 confirmadas.

### 14.4. Procedimiento de balance para Codex

1. Crear datos editables por máquina, figura, coste de mejora, nivel, robot, umbral y probabilidad.
2. Registrar durante pruebas: tiempo a primera tirada, a 50 monedas, a primera colección completa, a primera mejora de prestigio, a primer robot, a cada máquina nueva y a llave final.
3. Simular miles de tiradas con semilla fija y comprobar retornos esperados, distribución de rarezas, umbrales, riesgo de estancamiento y escalabilidad de robots.
4. Probar manualmente el tutorial y al menos un recorrido con varios prestigios.
5. Ajustar curvas para que las decisiones **Sell/Keep** y la necesidad de renacer tengan valor durante todas las fases.
6. Documentar cada cambio numérico en una tabla/changelog. No modificar reglas cerradas para compensar un mal equilibrio.

**PENDIENTE:** precios 003–010, costes de robots, requisitos de desbloqueo de la llave, fórmula final de suerte, bonus de cada figura, árbol definitivo y ratio exacto de ingresos. La falta de esos números **no bloquea** la construcción de sistemas configurables.

## 15. Dirección artística y producción de recursos

### 15.1. Identidad visual — CONFIRMADO

- Inspiración: **juguetes, coleccionables, gachapones, aparatos, pegatinas, mostradores y salones japoneses de finales de los 80 y 90**.
- Juego **2D en pixel art «rubber hose»**: formas redondas y elásticas, contorno casi negro y grueso, color plano con una sombra y un brillo, extremidades de goma, guantes blancos, ojos ovalados, objetos con vida propia. Paleta Showa: rojo, crema, azul marino, mostaza. Lectura clara a pequeña escala.
- **Mucha vida en pantalla:** las máquinas respiran y parpadean, y la tienda tiene animaciones de ambiente (gato de la suerte, reloj, neón, ventilador, ratón, polilla, televisor…). Nunca deben tapar ni distraer de las máquinas.
- El local también debe parecer de esa época: carteles impresos, pantallas retro, tapas de plástico, botones grandes, molduras simples, luminarias cálidas, cajitas y máquinas repetidas con variaciones.
- El espacio es **acogedor**, no un escenario de terror. Hay misterio por ausencia de personas, noche y extrañeza del encierro; evitar sangre, sustos obligatorios y oscuridad que impida interactuar.
- Sin 3D, vóxeles, render hiperrealista, suavizado o degradados que rompan el píxel, ni estética cyberpunk saturada.
- No copiar personajes, marcas ni diseños protegidos. Crear figuras originales inspiradas en la **sensación** de los juguetes japoneses antiguos.
- El **personaje llorando de la prueba pixel-art→3D es un ejercicio externo y no forma parte del universo, colecciones ni referencias oficiales**.

### 15.2. Materiales, color, luz y cámara — guía de arte

| Elemento | Objetivo |
|---|---|
| Máquinas | Plásticos envejecidos suaves, metal pintado discreto, ventanas transparentes solo donde hagan falta, cartelas retro originales. |
| Figuras | Sofubi/vinilo japonés: grandes formas, cabezas expresivas, ojos y detalles simples, acabado entre satinado y semibrillante. |
| Entorno | Madera o laminado antiguo, baldosas, pintura pastel gastada, juguetes y merchandising original. |
| Paleta | Marfil, mostaza suave, coral, verde menta, turquesa apagado, azul oscuro nocturno, amarillos cálidos. |
| Luz inicial | Tienda apagada pero navegable; interruptor provoca encendido memorable. |
| Luz en funcionamiento | Muy legible, cálida, acogedora, con pequeñas fuentes coloreadas en máquinas; sombras económicas. |
| UI | Inglés legible, carteles impresos retro, pegatinas y paneles inspirados en CRT/plástico; accesible a resoluciones bajas. |
| Animaciones | Breves, claras, jugueteras; evitar físicas complejas de cápsulas si no aportan diversión. |

### 15.3. Pipeline de pixel art → Godot

1. Resolución de mundo fija: la cámara muestra unos 427 × 240 píxeles, escalados ×3 con filtro «nearest». Un píxel de sprite es un píxel de mundo.
2. Tamaños de referencia: figura 40 × 40 sobre base de 56 × 30; personaje 40 × 56; gachapón 48 × 84; grúa y plinko 72 × 104. Lo que se apoya en el suelo se ancla abajo y centrado. Vista oblicua: un círculo tumbado es una elipse de alto ≈ 0,4 × ancho.
3. Contorno casi negro, un tono de brillo y uno de sombra por color, alpha solo 0 o 255.
4. Las máquinas son hojas de animación (despertar, reposo, jugar/reaccionar); cápsula, garra y bola son sprites aparte que el juego mueve según un archivo de anclajes.
5. Las animaciones son tiras horizontales de fotogramas iguales, descritas en un manifiesto (`anims.json`) con tamaño, número de fotogramas, velocidad y bucle.
6. Importar en Godot sin filtrado ni mipmaps; revisar a escala de juego, no ampliado.
7. La miniatura del álbum y su silueta salen del mismo sprite de la figura.
8. Reutilizar el mismo sprite en premio revelado, catálogo y vitrina.

**Material de versiones anteriores:** los modelos 3D y GLB de prototipos previos no son «canon» y no se usan. El personaje llorando no pertenece al juego.

## 16. Audio, atmósfera y narrativa ambiental

**Audio objetivo:** ambiente nocturno suave; clic de moneda, manivela, cápsula, premio, campanilla por completar colección, monedero, zumbido de máquinas, pequeñas melodías retro inspiradas en jugueterías, tonos comerciales cómicos del ordenador. El encendido inicial debe ser un momento audiovisual reconocible.

**Narrativa:** el jugador no sabe inicialmente por qué está atrapado. Las máquinas, la decoración y el PC vendedor dan pistas indirectas, sin misiones secundarias obligatorias ni diálogos que frenen un incremental. El desenlace conocido es salir usando la llave; la explicación exacta del misterio **queda pendiente** y no debe añadirse como revelación argumental definitiva sin aprobación.

**Recepción:** diálogos cortos en inglés, con humor de vendedor insistente; ofrecer opción de saltar/minimizar texto repetido. No generar contenido con texto japonés sin revisar su significado.

## 17. Interfaz y experiencia de usuario

**Idioma de todo lo visible al jugador:** **inglés**. Localizar el texto en archivos reutilizables; no es necesario traducir ahora a otros idiomas.

### 17.1. Pantallas principales

| Pantalla | Información necesaria |
|---|---|
| HUD de exploración | Dinero del ciclo, objetivo/contexto cercano, pista de interacción, resumen discreto de prestigio pendiente y progreso principal sin saturar. |
| UI de máquina | Precio de intento, saldo, tipo de máquina, estado de operación, indicación de input. |
| Panel de premio | Sprite grande de la figura, nombre si descubierto, rareza, venta, `X/N` para ese tipo, bonus por colección, **Sell** y **Keep** (si procede). |
| Catálogo | Accesible siempre; todos los slots, siluetas para no descubiertas, reveladas de forma permanente, filtros y progreso del ciclo. |
| Ordenador de recepción | Personalidad comercial, categorías, precios con monedas, robots/mejoras, requisitos y llave final. |
| Sofá / rebirth | `Saved prestige`, `Pending prestige`, `Available`, árbol, selecciones provisionales, coste y botones **Cancel** / **Sleep & Rebirth**. |
| Bonificaciones activas | Lista accesible que permita conocer efectos de colecciones y compras temporales. |
| Final | Abrir puerta con llave, escena, créditos y retorno a modo libre. |
| Menú pausa/opciones | Continuar, audio, ratón, gráficos, salir, controles, persistencia segura. |

### 17.2. Textos de ejemplo (en inglés)

- `Insert 1 coin` · `Spin` · `Prize obtained!`
- `Sell for 4 coins` · `Keep (2/5)` · `Collection completed!`
- `Already completed — sell this duplicate.`
- `If I run out of money, I'll be stuck here forever.`
- `Prestige unlocked! The staff room sofa looks inviting...`
- `Banked prestige` · `Pending this run` · `Sleep & Rebirth`.
- `Welcome, valued customer!` · `You've got GREAT taste in upgrades!`
- `Store Exit Key` · `Use key` · `Free Play unlocked`.

**Evitar saturación:** respetar texto legible a 720p, contraste, remapeo de controles si es viable, opción de reducir parpadeos, volumen por categorías y control de duración de animaciones.

### 17.3. Controles propuestos

- `WASD` o flechas: caminar por el suelo en dos ejes; `Shift`: correr. El ratón solo se usa en los menús.
- `E`: interactuar con máquinas, recepción, sofá, interruptor y puerta.
- `Esc`: cancelar menú o pausa según contexto, sin operaciones financieras accidentales.
- `Tab` o tecla configurable: catálogo accesible desde el inicio. **No exigir habilidad de prestigio para ver el catálogo**.
- Botones de UI para confirmar venta/colección; soporte básico de teclado y foco. Atajos del prototipo se pueden reorganizar si no rompen la lógica.

## 18. Final, créditos y modo libre

### 18.1. Final principal — CONFIRMADO

1. Reunir monedas mediante máquinas, colecciones, automatizaciones y varios prestigios.
2. Comprar la **última mejora de recepción**, `Store Exit Key`, en el ordenador vendedor.
3. El jugador, con llave propia del ciclo, se dirige a **la puerta de salida de la tienda**.
4. Interactúa con ella para abrirla y **salir del establecimiento**.
5. Se reproduce una escena final breve y aparecen **créditos**.
6. Se registra permanentemente `story_completed = true` y `free_play_unlocked = true`.
7. Se habilita **Free Play** para continuar jugando y completar máquinas, colecciones o mejoras. No borrar por obligación el progreso que permitió llegar al final.

### 18.2. Modo libre — CONFIRMADO + PROPUESTA TÉCNICA

**CONFIRMADO:** tras créditos se puede seguir jugando.

**PROPUESTA:** ofrecer `Continue in Free Play` tras los créditos y permitir volver al mismo estado de juego, o cargar una instantánea segura inmediatamente posterior al final. La historia no vuelve a dispararse sin una acción explícita de repetición. Los prestigios posteriores pueden continuar funcionando, y el flag de historia completada permanece guardado aunque el jugador renazca. No iniciar Nueva Partida ni borrar automáticamente habilidades, dinero, catálogo o metaprogreso al ver créditos.

## 19. Arquitectura Godot: datos separados del código

**PROPUESTA TÉCNICA** para implementar de forma progresiva con Godot 4 + GDScript:

### 19.1. Proyecto existente y advertencia de migración

Se dispone de un **prototipo anterior 0.2** de «Gachapon Night» con escenas `main.tscn`, `player.tscn` y scripts `main.gd`, `player.gd`, `game_state.gd`, además de un `AGENTS.md` antiguo. **Ese prototipo NO implementa necesariamente estas nuevas decisiones.** En su documentación se indica que venta directa, sofá y máquina 002 están prototipados, pero el catálogo, colección-bonificación, recepción/robots y final necesitan cambios. El prototipo histórico se documentó sin pruebas reales de ejecución en Godot. **Codex debe inspeccionar y ejecutar primero**.

En el prototipo 0.2 el archivo de guardado histórico se describe como `user://gachapon_night_save.json`. Proteger el guardado existente, usar versión de esquema y preparar migración. Conservar temporalmente su carpeta/ruta si es necesario para importar partidas; **no** cambiar el nombre del proyecto y asumir que `user://` migra solo.

### 19.2. Organización sugerida

```text
project.godot
AGENTS.md                          # Instrucciones breves para Codex, subordinadas a este archivo
GachaNight_MASTER_DESIGN.md         # Fuente de verdad
README.md
scenes/
  main.tscn
  player.tscn
  machines/                       # Escenas base y variaciones
  interactions/
  ui/
  environment/
scripts/
  game_state.gd                   # Estado o fachada: no concentrar todo el juego en un script
  services/
    economy_service.gd
    machine_service.gd
    collection_service.gd
    prestige_service.gd
    reception_service.gd
    automation_service.gd
    save_service.gd
  ui/
  data/
resources/
  machines/                      # .tres u otros recursos por máquina
  figures/                       # Definiciones por ID de figura
  upgrades/
  robots/
  balance/
assets/
  sprites/                       # figuras, máquinas, props, tiles y hojas de animación en PNG
  textures/
  icons/                         # Incluye siluetas del álbum
  audio/
tests/
```

No es obligatorio copiar literalmente esta estructura: **adaptar el proyecto existente** en lugar de reescribirlo innecesariamente.

### 19.3. Esquemas de datos recomendados

**FigureDefinition** — datos estáticos, nunca editar como estado de partida:

```text
id: StringName                       # ejemplo: g001_toy_01; inmutable en guardados
machine_ids: Array[StringName]       # figura normalmente asociada a una máquina
name_en: String
rarity_id: StringName               # common/uncommon/rare/epic/legendary
base_sell_value: int
copies_required: int                 # >=1, configurable
prestige_reward: int                 # >0, por colección completa
collection_bonus_id: StringName      # efecto temporal único por tipo
collection_bonus_params: Dictionary
model_path: String                   # glb o escena Godot
portrait_path: String                # miniatura revelada
silhouette_path: String              # silueta negra, legible
```

**MachineDefinition:**

```text
id: StringName
machine_type: StringName             # gacha, claw, plinko, ...
price_per_attempt: int
prize_table: Array                   # figure_id + weight/probability
scene_path: String
unlock_rules: Dictionary             # no esconder máquinas físicamente por defecto
```

**ReceptionUpgradeDefinition:**

```text
id, category, display_name_en, description_en
coin_cost_curve, max_level, prerequisites
upgrade_effects
is_store_exit_key: bool
```

**PrestigeUpgradeDefinition:**

```text
id, category, display_name_en, description_en
prestige_cost_curve, max_level, prerequisites
permanent_effects
```

**RobotDefinition:**

```text
id, display_name_en, cost_in_coins
supported_machine_types, automation_behaviors, upgrade_curve
```

### 19.4. División entre `PermanentState` y `RunState`

**PermanentState (persistente entre renacimientos):**

```text
save_schema_version
unlocked_discoveries: Set[figure_id]       # catálogo histórico
prestige_upgrade_levels: Map[upgrade_id, int]
banked_prestige: int                        # puntos no gastados
total_rebirths: int
tutorial_m2_used: bool                     # desbloqueo del sofá sin reset repetido
story_completed: bool
free_play_unlocked: bool
settings: Dictionary
```

**RunState (se guarda al cerrar, se reinicia SOLO al renacer):**

```text
coins: int
power_switch_on: bool
figure_copies_held: Map[figure_id, int]
figure_collections_completed: Set[figure_id]
pending_prestige: int
active_collection_bonuses: Set[figure_id]
reception_upgrade_levels: Map[upgrade_id, int]
owned_robots: Map[robot_id, robot_instance_state]
machine_run_states: Map[machine_id, data]
pending_prize: Optional[prize_instance_with_unique_transaction_id]
key_owned_this_run: bool
run_playtime_seconds: float
```

**Nota:** el catálogo puede mostrar el universo completo de figuras leyendo definiciones estáticas, pero únicamente `unlocked_discoveries` decide cuáles están reveladas. No guardar a ciegas nodos de escena ni rutas absolutas de sistema. El premio pendiente debe serializarse para evitar perder moneda si se cierra el juego en mitad de una elección.

### 19.5. Servicios y eventos

Separar claramente:

- `MachineService`: valida coste y estado, ejecuta tirada, genera transacción única, revela figura.
- `CollectionService`: `can_keep`, incrementos de copias, completado por umbral, recompensa de prestigio y bonus temporal una vez por run.
- `EconomyService`: saldo y operaciones seguras, modficadores y mínimos económicos.
- `ReceptionService`: compras con **monedas**, requisitos, robots, llave.
- `PrestigeService`: menú de compra diferida y transacción de renacimiento.
- `AutomationService`: colas/temporizadores, preferencias, decisión Keep/Sell respetando límites.
- `SaveService`: guardado atómico de ambas capas y migraciones.
- UI: observa señales y presenta datos, **no** escribe directamente contadores de prestigio o dinero.

**Eventos/signals recomendados:** `coins_changed`, `figure_discovered`, `prize_pending`, `prize_resolved`, `figure_collection_completed`, `collection_bonus_activated`, `prestige_available_changed`, `reception_upgrade_bought`, `robot_state_changed`, `prestige_unlocked`, `rebirth_confirmed`, `store_key_bought`, `story_completed`.

## 20. Guardado, transacciones y prevención de errores

**Recomendación fuerte:** guardado automático de **estado permanente y del ciclo actual**. Es necesario para un objetivo de 2–3 horas y para no perder una colección por cerrar el programa.

- Guardar tras acciones críticas: compra de recepción, premio vendido/conservado, colección completada, compra de llave, confirmación de renacimiento, final, y además periódicamente.
- Implementar escritura segura: archivo temporal, comprobación, reemplazo atómico cuando sea posible; versión del esquema y copia de seguridad antes de migrar.
- Cada tirada tiene ID único y estado: `PAID → REVEALED → RESOLVED`. Un mismo `prize_instance_id` se resuelve una vez.
- Evitar duplicaciones si el usuario pulsa E/Enter/clic simultáneamente o un robot intenta actuar sobre un panel humano abierto.
- Al cerrar/reabrir con un premio pendiente, reaparecer en la decisión con ese mismo premio, o reestablecer de forma equivalente y segura sin dar un premio extra.
- Comprar mejoras valida saldo y prerequisitos de nuevo al confirmar; no confiar en valores mostrados en UI como autoridad.
- Confirmación de renacimiento: cobrar mejoras y reiniciar juntos, sin riesgo de doble cobro por error/crash. Si la operación falla, conservar estado anterior recuperable.
- El flag `story_completed` se registra de forma persistente. `free_play_unlocked` no se elimina en siguientes prestigios.
- Ajustes del usuario sobreviven a renacimiento y reinicio.

**PENDIENTE (técnico):** migración precisa del esquema de guardado del prototipo 0.2. No borrar un guardado anterior silenciosamente.

## 21. Rendimiento y compatibilidad

**Prioridad confirmada:** el juego debe ser viable en portátiles y equipos Windows/macOS modestos; medir requisitos reales antes de publicarlos.

- Godot 4, preferir **Compatibility renderer** durante el prototipado.
- Sprites reutilizados; máquinas construidas con las mismas piezas; sin efectos de pantalla costosos.
- Texturas pequeñas, atlas donde aporten, materiales sencillos, pocas superficies transparentes solapadas.
- Iluminación ambiental con pocas luces dinámicas costosas; evitar postprocesado dependiente de hardware moderno.
- Física simplificada para cápsulas/grúa/plinko y desactivada cuando no se necesita.
- Automatización lógica: cálculos agregados y representación visual de pocas máquinas visibles, no una bola/cápsula por cada operación de fondo.
- Culling/distancia de render y desactivación de animaciones fuera de cámara.
- Medir tiempos de carga, FPS y memoria en tienda llena y tras muchas automatizaciones.
- Opciones de calidad/ventana/resolución, sensibilidad, audio y accesibilidad básica.
- Exportaciones para Windows/macOS con verificación real de apertura, entrada/salida y guardado. No afirmar compatibilidad comercial sin pruebas.

## 22. Plan de desarrollo recomendado para Codex

No son fechas. Cada etapa debe producir un **proyecto Godot ejecutable** con pruebas verificables antes de añadir contenido.

| Fase | Entregables prioritarios | Aceptación |
|---|---|---|
| **0. Auditoría/migración** | Leer proyecto 0.2, inventario de reglas obsoletas, guardado seguro, actualizar `AGENTS.md` al nombre y requisitos nuevos. | Lista precisa de lo que funciona y de lo que falta, sin perder el proyecto. |
| **1. Colecciones y rarezas** | Cinco rarezas, colecciones por tipo y requisitos variables, bonus temporal por colección, Keep desactivado al completarse. | Una colección completa da prestigio una vez y un bonus hasta renacer; no se puede guardar una copia más. |
| **2. Catálogo permanente** | Catálogo abierto desde inicio, siluetas oscuras, revelación al obtener figura aun al vender, persistencia. | La figura descubierta queda visible tras salir y renacer; desconocidas siguen oscuras. |
| **3. Tutorial y prestigio** | Desbloqueo exacto tras primer uso de 002, sofá exclusivamente, puntos no gastados conservados, reinicios. | No gastar antes de 002; Cancel no modifica; Rebirth transaccional. |
| **4. Ordenador de recepción** | PC vendedor retro en mostrador, UI de compras con monedas, mejoras temporales, separación respecto del sofá. | Compras de recepción se reinician; el árbol de prestigio no aparece en el PC. |
| **5. Robots y automatización** | Al menos un robot comprado con monedas, procesamiento seguro de premios, filtros de venta/colección y rendimiento. | No duplica recompensas ni colecciona figuras completas; se reinicia. |
| **6. Máquinas 003–006** | Dos gachapones adicionales, máquina de gancho, plinko; tablas de balance configurables. | Los seis respetan bucle, rendimiento y economía; gancho/plinko se distinguen visualmente. |
| **7. Arte y sonido** | Tienda 80–90, figuras de vinilo originales, miniaturas y siluetas, PC con personalidad, iluminación de inicio, SFX. | Estilo consistente, legibilidad y rendimiento aceptables. |
| **8. Final y modo libre** | Llave como última mejora de recepción, interacción con puerta, créditos y continuación. | No se termina solo al comprar llave; tras créditos Free Play permanece desbloqueado. |
| **9. Balance y Steam** | Varias runs completas medidas, 2–3 horas de historia, guardado probado, optimización y builds. | Progresión fluida y pruebas reales en equipos objetivos. |

**Preferencia de implementación:** empezar con un corte vertical pequeño y robusto (baño, 001, 002, sofá, recepción mínima, colecciones) y ampliar, en vez de construir diez máquinas vacías antes de tener economía válida.

## 23. Casos de prueba obligatorios

Codex deberá crear pruebas automatizadas cuando sea viable y **guion de QA manual** para escenas e interfaz:

**Premios/economía**

1. `001` cuesta 1; tiene **exactamente 5 figuras** y su venta mínima nunca baja de 1 moneda.
2. `002` cuesta 50 y tiene venta mínima 30; tras venta pobre el jugador puede regresar a 001.
3. Al quedar saldo post-tirada `<= 1`, Keep aparece deshabilitado y la advertencia se ve en inglés.
4. Ninguna acción manual o automatizada deja al jugador en un estado económico irrecuperable.
5. Sell acredita el valor correcto **directamente** y no mueve al jugador a un cambiador.
6. Un premio puede resolverse **una vez**: doble clic no duplica dinero, copias, descubrimientos ni bonificaciones.
7. Cancelar/cerrar el panel no destruye el premio ni lo duplica al cargar.

**Colecciones/rareza/álbum**

8. Guardar `N` copias de **la misma figura** completa únicamente su propia colección, no la de otras figuras de la máquina.
9. Antes de N copias no hay prestigio ni bonificación parcial por copias individuales.
10. Al alcanzar N copias: una bonificación temporal y una recompensa de prestigio pendiente **una sola vez**.
11. Para copias nuevas del mismo tipo terminado, Keep queda prohibido y Sell sigue funcionando.
12. Después de renacer puede completarse de nuevo el tipo y cobrar una vez más en ese nuevo ciclo.
13. El catálogo se abre con 0 descubrimientos; cada entrada desconocida muestra **su propia silueta** oscurecida.
14. Revelar y **vender** una figura también la descubre; al renacer y reiniciar el juego queda revelada.
15. El catálogo nunca restaura copias guardadas de un ciclo anterior.
16. Los cinco niveles de rareza son válidos; la UI no introduce una sexta rareza porque una figura se llame Secret.

**Prestigio y recepción**

17. Antes de usar `002` por primera vez, el sofá no permite renacer ni comprar habilidades.
18. El primer uso de `002` habilita el sofá y activa el tutorial; el acceso continúa disponible en runs posteriores.
19. La recepción solo cobra **monedas**; sus compras no afectan al banco de prestigio.
20. El árbol de prestigio solo está disponible en el sofá; seleccionar habilidades y **cancelar** no gasta ni aplica nada.
21. Confirmar con puntos ahorrados + pendientes aplica mejoras, descuenta lo gastado, conserva el resto y reinicia.
22. Tras renacer desaparecen robots, compras de recepción, bonificaciones de colecciones, monedas y contadores de copias; permanecen habilidades, puntos, descubrimientos y tutorial/meta.
23. Prestigio no gastado: con 20 puntos y compra de 15 quedan 5, que persisten entre reinicios del juego.
24. Una mejora permanente de suerte/economía modifica la siguiente run sin saltarse límites de validación.
25. El ordenador tiene textos de vendedor comercial absurdo, en inglés; no aparece como personaje llorando ni como NPC físico.

**Automatización/final/sistema**

26. Un robot configurado para Keep respeta el tope de colección y vende duplicados completados según su configuración.
27. Ningún robot gasta monedas inexistentes ni evade la advertencia de saldo bajo.
28. Comprar la llave no acaba la historia: hay que interactuar con la **puerta**.
29. La puerta sin llave no permite terminar. Con llave: secuencia final y créditos reproducidos una vez de forma normal.
30. Después de los créditos, Free Play es accesible; completar la historia no elimina catálogo, prestigio ni partida.
31. Guardar/cargar en mitad de una run conserva economía, colecciones, robots, recepción y premio pendiente sin duplicar efectos.
32. Un renacimiento interrumpido/cierre forzado no permite clonación de puntos o compras.
33. La configuración visible del juego está en inglés; controles y volumen funcionan.
34. Las escenas se cargan con renderizador elegido; medir FPS en tienda y con robots activos en Windows/macOS cuando haya máquinas para ello.
35. El gatito y el personaje llorando de pruebas anteriores **no aparecen automáticamente** en el catálogo final sin aprobación del creador.

## 24. Restricciones, prioridades y temas abiertos

### 24.1. No modificar sin consulta — decisiones cerradas

- Nombre **GachaNight**; **2D en vista lateral**; Japón juguetes/tiendas **80–90**; estética **vinilo japonés en pixel art**.
- Interfaz del juego **solo inglés** inicialmente.
- Primer ciclo: baño, 3 monedas, interruptor, tienda enciende, gachapón 001 de 1, máquina 002 de 50.
- Primera máquina con **5 tipos de figuras**; mínimo de venta 1; segunda con mínimo de venta 30.
- Máquinas 001–004 gachapones; 005 gancho; 006 plinko; total inicial 6–10.
- Sell directo / Keep irreversible; protección económica con saldo post-tirada <=1.
- Exactamente **cinco rarezas**, requisitos escalados de colección por tipo, rarezas superiores más prestigio.
- **Colección completa por tipo de figura**, no por máquina; prestigio y bonus temporal al completar; no guardar más duplicados de tipo completado; recompensa una vez por ciclo.
- Catálogo siempre visible con **siluetas negras** de no descubiertas y revelación **permanente** desde primera obtención, incluso vendida.
- Prestigio solo en el sofá, desbloqueado **después del primer uso de máquina 002**; comprar habilidades solo al **confirmar dormir y renacer**.
- Banco de prestigio no gastado **persistente**; habilidades de prestigio **permanentes**.
- Recepción con ordenador vendedor **exageradamente comercial y absurdo**, mejoras y robots por monedas y **todas temporales por run**.
- Última mejora de recepción: **llave**; hay que ir a la puerta para salir; **créditos y modo libre**.
- Historia principal orientada a **2–3 horas incluyendo varios prestigios**.
- El personaje llorando de prueba **no pertenece** a GachaNight.

### 24.2. Datos que Codex debe proponer y medir, no tratar como cerrados

- Costes de máquinas 003+, probabilidades, valores de todas las figuras y requisitos exactos de copias por rareza.
- Bonificación concreta que concede cada colección; nombres y modelos finales de figuras.
- Costes, requisitos, efectos y límites del árbol de prestigio.
- Costes, modelos, personalidades y tipos de robots de recepción; ritmo de automatización.
- Precio y prerrequisitos finales de la llave, ajustados a la duración objetivo.
- Tipos de máquinas 007–010, si se incluyen.
- Distribución y dimensiones definitivas de la tienda y contenido decorativo.
- Balance entre multiplicadores de venta, descuentos, suerte, requisitos de colección y velocidad de robots.
- Sentido exacto de la palabra pública de rareza máxima: **Legendary** o **Secret**; mantener **cinco niveles**, con un ID estable `legendary` y etiqueta de UI configurable.
- Detalles concretos de la historia ambiental, plano de la sala de empleados, música definitiva y escena de créditos.
- Requisitos mínimos oficiales de hardware, metas FPS y precio de Steam: definir tras pruebas.
- Gancho con resultado garantizado vs posibilidad de fallo: implementar por defecto un premio garantizado, pedir confirmación si se propone cambiarlo.
- Guardado del 0.2: migración precisa y versionado; diseñar antes de introducir datos nuevos.

### 24.3. No introducir por iniciativa propia

- Premios por guardar una sola copia cuando no está completada su colección.
- Bonificaciones de colección permanentes o puntos por cada unidad suelta.
- Dinero persistente entre runs; robots comprados con monedas que sobreviven al renacimiento.
- Gastar prestigio desde recepción, álbum, pausa o HUD; adelantar acceso al sofá al primer gachapón.
- Sistema de colección «obtener una de cada figura de máquina» como requisito principal.
- Ocultar/reiniciar álbum de descubrimientos al renacer; siluetas genéricas que no representen la figura.
- Sexta rareza Secret separada de Legendary sin aprobación.
- Eliminar de los premios aleatorios una figura solo porque su colección esté completa.
- Premios de microtransacción, multijugador, combate, NPC obligatorios o gran árbol narrativo.
- Ganancias offline automáticas, publicidad o tienda de monetización real.
- Final automático al comprar llave; final sin puerta física; modo libre bloqueado tras créditos.
- Incorporar automáticamente el personaje llorando del experimento de modelado.

## 25. Historial de decisiones y sustituciones

Esta sección evita que Codex lea el viejo `Gachapon_Night_Documento_Maestro.md` como si fuera actual:

| Tema | Antes / documento 1.0 | Decisión vigente |
|---|---|---|
| Nombre | `Gachapon Night` provisional. | **GachaNight**, confirmado. |
| Arte | Cozy plastilina japonés 80; después vinilo retro en 3D estilizado, «no pixel art». | **Juguetes japoneses de 80–90 en pixel art** (decisión del creador del 2026-10-11, tras probar el prototipo 3D). |
| Cámara | Primera persona, tienda 3D explorable; después 2D en vista lateral. | **2D en vista oblicua elevada**, suelo profundo y movimiento en dos ejes. Reglas, economía y progresión no cambian. |
| Estilo | Vinilo retro; después pixel art neutro. | **Rubber hose en pixel art** con gráfica Showa, según las referencias de `diseños/` (2026-10-11). |
| Bases de figura | Sin base. | **Base por rareza**, más elaborada cuanto más rara; nunca en siluetas. |
| Modelo llorando | Experimento reciente de arte 3D. | **No es parte del juego.** |
| Copias y prestigio | Hitos por copia; algunos prototipos concedían puntos con 2–3 copias. | **Completar un contador por tipo**; solo al completar se concede recompensa una vez/run. Umbrales variables por rareza. |
| Bonificaciones de figuras | «Figuras nunca conceden pasivas». | **Cada colección de tipo completada da bonificación temporal**, que se reinicia al renacer. |
| Duplicados tras completar | Antes se podían guardar sin prestigio extra. | **No se pueden seguir guardando**; se permite venderlos. |
| Álbum | Descubrimientos permanentes. | Además, **visible desde el principio** con siluetas oscuras de todas las figuras no descubiertas. |
| Rarezas | Distribución provisional sin taxonomía cerrada. | **Exactamente cinco niveles**, Common a Legendary/Secret; curva editable. |
| Prestigio | Menú de sofá sin puerta de desbloqueo definida. | Se desbloquea al **usar la 002 por primera vez**; gasto solo al confirmar renacimiento. |
| Recepción | Solo decorativa; cambiador opcional. | **Sistema central de mejoras y robots por monedas**, PC vendedor absurdo, llave final. |
| Permanencia | Prestigio y catálogo. | Prestigio + catálogo + **puntos no gastados**; recepción/robots/bonus se pierden. Modo libre y final persisten como metadatos. |
| Duración | «2–3 h de recorrido» ambiguo. | **2–3 h para historia principal con varios prestigios.** |
| Final | Pendiente. | **Comprar llave como última mejora de recepción → abrir puerta → créditos → modo libre.** |
| Idioma | No fijado. | **Inglés solamente** en interfaz inicial. |
| Máquinas | Evolución futura indefinida; después 6–10 al inicio con cuatro gachapones. | **Cuatro al inicio** (2026-10-12): gachapones 001 y 002, grúa 005, plinko 006; sala más pequeña y vista algo más en picado. Se ampliará si hace falta. |

### Primera tarea recomendada a Codex, lista para copiar

> «Lee completo `GachaNight_MASTER_DESIGN.md` y audita el proyecto Godot existente antes de editar. Compara las reglas de colección, rareza, sofá y guardado con esta especificación, registra las incompatibilidades y prepara el primer cambio incremental: colecciones individuales por tipo con umbrales configurables para cinco rarezas, una bonificación temporal y prestigio pendiente al completar, Keep deshabilitado después del umbral y catálogo abierto desde el inicio con siluetas oscuras y descubrimientos permanentes. Conserva el bucle Sell/Keep, coste 1/mínimo 1 de máquina 001, coste 50/mínimo 30 de máquina 002, y protección económica. No implementes aún diez máquinas ni rehagas el proyecto. Ejecuta las pruebas disponibles; si Godot no está instalado, indícalo y deja un procedimiento de comprobación manual.»

---

**Regla final del proyecto:** GachaNight debe ser un incremental de juguetería japonesa retro en 2D y pixel art, con **dos mercados diferenciados** (recepción por monedas y sofá por prestigio), **colecciones por figura completadas con copias**, **álbum histórico de siluetas**, **bonificaciones temporales**, **robots reiniciables** y un objetivo narrativo inequívoco: **comprar la llave, abrir la tienda, salir y seguir después en modo libre**.
