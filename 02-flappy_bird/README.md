# Flappy Bird

Implementación de Flappy Bird desarrollada con Python, Pygame y Gale. El proyecto conserva el funcionamiento clásico del juego y añade un modo de dificultad avanzada con estrategias, troncos móviles y un power-up que permite atravesar obstáculos temporalmente.

## Controles

| Acción | Tecla o control |
|---|---|
| Saltar | clic izquierdo |
| Moverse a la izquierda | Flecha izquierda, solo en modo hard |
| Moverse a la derecha | Flecha derecha, solo en modo hard |
| Seleccionar opción | Flechas arriba y abajo |
| Confirmar | Enter |
| Salir | Escape |

## Modificaciones principales

### Selección de modos

El menú inicial permite elegir entre `normal_mode` y `hard_mode`. La selección se gestiona en `TitleScreenState.py`, que envía el modo elegido al estado de cuenta regresiva y posteriormente al estado de juego.

### Patrón Strategy

`Strategy.py` separa las reglas de cada modo de juego:

- `MenuStrategy`: actualiza el fondo del menú sin generar obstáculos.
- `NormalModeStrategy`: mantiene la experiencia clásica. Genera troncos con una separación fija, actualiza su movimiento y comprueba las colisiones del ave.
- `HardModeStrategy`: aumenta la dificultad con intervalos y separaciones variables, troncos móviles, desplazamiento horizontal y power-ups.

`PlayingState.py` selecciona la estrategia según el modo y delega en ella la generación de troncos, la actualización del mundo, las colisiones y el renderizado de elementos especiales.

### Modo hard

En el modo hard:

- Los troncos aparecen con intervalos variables.
- La separación entre troncos también puede variar.
- Algunos pares de troncos se mueven verticalmente.
- El ave puede moverse horizontalmente con las flechas izquierda y derecha.
- Pueden aparecer power-ups en zonas libres de obstáculos.
- El texto `MODE: HARD` identifica el modo activo durante la partida.

### Power-up fantasma

`PowerUpFactory.py` define el power-up fantasma y su ciclo de vida:

1. `HardModeStrategy` crea el power-up después de cierto tiempo y lo coloca en una posición libre.
2. `GhostPowerUp` se desplaza con el mundo y comprueba si sigue activo.
3. Cuando el ave lo recoge, se activa `ghost_mode` durante seis segundos.
4. `Bird.py` cambia el sprite, controla el tiempo restante y muestra un parpadeo durante los dos últimos segundos.
5. Al terminar el efecto, el ave vuelve automáticamente a su forma normal.

El modo fantasma solo permite atravesar los troncos en modo hard. El ave sigue perdiendo al tocar el suelo.

### Música

La música normal es `marios_way.ogg`. Al recoger el power-up se reproduce `hell.ogg` en bucle. Cuando termina el efecto fantasma, `Bird.py` restaura la música normal.
