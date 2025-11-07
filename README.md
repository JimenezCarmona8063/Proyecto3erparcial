# Social Net System

Aplicación interactiva desarrollada en Python para demostrar el uso integrado de múltiples estructuras de datos dentro de una red social. La interfaz fue creada con **Pygame** y permite gestionar usuarios, amistades, publicaciones, reacciones y notificaciones en tiempo real.

## Características principales

- **Gestión de usuarios:** alta de nuevos perfiles con nombre, usuario y biografía.
- **Red de amigos:** solicitudes bidireccionales para relacionar usuarios.
- **Publicaciones:** creación de posts almacenados en listas ligadas personalizadas.
- **Reacciones sociales:** registro de comentarios y "me gusta" para cada publicación.
- **Prioridad en el muro:** un *heap* mantiene visibles las publicaciones más relevantes.
- **Notificaciones:** cada usuario dispone de una cola para mensajes de actividad.
- **Búsquedas eficientes:** se usa el algoritmo KMP para localizar usuarios y posts.
- **Visualización gráfica:** paneles para usuarios, feed destacado, historial y formularios emergentes.

## Estructuras de datos empleadas

| Requisito | Implementación |
|-----------|----------------|
| Listas ligadas | `LinkedList` en `social_net/data_structures.py` para almacenar publicaciones por usuario. |
| Colas | `collections.deque` para manejar las notificaciones de cada usuario. |
| Colas de prioridad | `heapq` en `SocialNetwork.get_top_posts` para destacar las publicaciones más relevantes. |
| Conjuntos | Conjuntos de amigos y reacciones ("likes") para evitar duplicados y facilitar consultas. |
| Mapas / Diccionarios | Diccionarios para indexar usuarios, publicaciones y accesos por identificador. |
| Algoritmos de cadenas | Implementación propia del algoritmo KMP en `social_net/search.py` para búsquedas. |

## Requisitos

- Python 3.10+
- [Pygame](https://www.pygame.org/) 2.5 o superior

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del proyecto ejecuta:

```bash
python -m social_net.app
```

Se abrirá una ventana con la interfaz gráfica:

- Selecciona un usuario desde la columna izquierda para activar las acciones.
- Utiliza los botones superiores para crear usuarios, agregar amigos, publicar, reaccionar y realizar búsquedas.
- Cada formulario se despliega como un diálogo sobre la interfaz principal y refleja de inmediato los cambios.

## Documentación adicional

- `social_net/data_structures.py`: contiene la implementación de la lista ligada utilizada por los usuarios.
- `social_net/network.py`: núcleo lógico de la red social (usuarios, posts, notificaciones y búsquedas).
- `social_net/app.py`: interfaz gráfica completa con Pygame.

## Licencia

Este proyecto se entrega como material académico para el tercer parcial.
