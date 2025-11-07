# Social Net System

Aplicación interactiva desarrollada en Python para demostrar el uso integrado de múltiples estructuras de datos dentro de una red social. La interfaz fue creada con **Pygame** y permite gestionar usuarios, amistades, publicaciones, reacciones y notificaciones en tiempo real.

## Características principales

- **Gestión de usuarios:** alta de nuevos perfiles con nombre, usuario, biografía y contraseña.
- **Inicio de sesión seguro:** autenticación con contraseñas cifradas (SHA-256), cambio entre sesiones y formularios guiados para registro.
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
python run_social_net.py
```

También puedes lanzar el módulo directamente:

```bash
python -m social_net.app
```

Se abrirá una ventana con la interfaz gráfica:

- Al iniciar se mostrará el formulario de inicio de sesión; puedes usar las credenciales demo `alice/alice123`, `bob/bob123` o `carol/carol123`.
- Utiliza los botones superiores para iniciar/cerrar sesión, registrarte, crear publicaciones, agregar amistades, reaccionar y buscar usuarios o posts.
- Cada formulario se despliega como un diálogo sobre la interfaz principal y refleja de inmediato los cambios, incluyendo la actualización del feed y el panel del usuario activo.
- La cabecera muestra un *ticker* de actividad reciente: cada pocos segundos la red social genera nuevas publicaciones, reacciones y comentarios, además de registrar tus propias acciones en tiempo real.

## Documentación adicional

- `social_net/data_structures.py`: contiene la implementación de la lista ligada utilizada por los usuarios.
- `social_net/network.py`: núcleo lógico de la red social (usuarios, posts, notificaciones y búsquedas).
- `social_net/app.py`: interfaz gráfica completa con Pygame.

## Licencia

Este proyecto se entrega como material académico para el tercer parcial.
