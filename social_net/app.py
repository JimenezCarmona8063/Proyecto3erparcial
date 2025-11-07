"""Pygame visual interface for the social network demo."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import pygame

from .models import Post, User
from .network import SocialNetwork

pygame.init()

AUTO_ACTIVITY_EVENT = pygame.USEREVENT + 1


# -- UI helpers ---------------------------------------------------------


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    callback: Callable[[], None]
    enabled: bool = True

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        if not self.enabled:
            color = (90, 96, 130)
        else:
            color = (70, 90, 160) if hovered else (52, 61, 94)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        text_color = (240, 240, 255) if self.enabled else (200, 205, 225)
        text_surface = font.render(self.label, True, text_color)
        surface.blit(
            text_surface,
            text_surface.get_rect(center=self.rect.center),
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


class InputField:
    def __init__(self, label: str, rect: pygame.Rect, multiline: bool = False, password: bool = False) -> None:
        self.label = label
        self.rect = rect
        self.text = ""
        self.active = False
        self.multiline = multiline
        self.password = password

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.multiline:
                    self.text += "\n"
                else:
                    return "submit"
            elif event.key == pygame.K_TAB:
                return "next"
            elif event.key == pygame.K_ESCAPE:
                return "cancel"
            else:
                if event.unicode:
                    self.text += event.unicode
        return None

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = (255, 255, 255) if self.active else (230, 230, 240)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (120, 120, 150), self.rect, 2, border_radius=5)
        label_surface = font.render(self.label, True, (30, 30, 50))
        surface.blit(label_surface, (self.rect.x, self.rect.y - 22))
        if self.multiline:
            draw_multiline_text(surface, self.text or "", font, self.rect.inflate(-10, -10), (20, 20, 40))
        else:
            display_text = self.text
            if self.password and self.text:
                display_text = "•" * len(self.text)
            text_surface = font.render(display_text, True, (20, 20, 40))
            surface.blit(text_surface, (self.rect.x + 8, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))


class Form:
    def __init__(
        self,
        title: str,
        fields: List[InputField],
        on_submit: Callable[[List[str]], None],
        on_cancel: Callable[[], None],
        submit_label: str = "Guardar",
        cancel_label: str = "Cancelar",
        secondary_action: Optional[Tuple[str, Callable[[], None]]] = None,
        helper_text: str | None = None,
    ) -> None:
        self.title = title
        self.fields = fields
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.active_index = 0 if fields else -1
        if self.fields:
            self.fields[0].active = True
        self.submit_button = Button(pygame.Rect(0, 0, 160, 38), submit_label, self.submit)
        self.cancel_button = Button(pygame.Rect(0, 0, 160, 38), cancel_label, self.cancel)
        self.secondary_button = (
            Button(pygame.Rect(0, 0, 160, 38), secondary_action[0], secondary_action[1])
            if secondary_action
            else None
        )
        self.helper_text = helper_text

    def submit(self) -> None:
        values = [field.text.strip() for field in self.fields]
        self.on_submit(values)

    def cancel(self) -> None:
        self.on_cancel()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.cancel()
            return
        for index, field in enumerate(self.fields):
            response = field.handle_event(event)
            if response == "next":
                self._focus((index + 1) % len(self.fields))
            elif response == "submit":
                self.submit()
            elif response == "cancel":
                self.cancel()
            if response:
                break
        self.submit_button.handle_event(event)
        self.cancel_button.handle_event(event)
        if self.secondary_button is not None:
            self.secondary_button.handle_event(event)

    def _focus(self, index: int) -> None:
        for i, field in enumerate(self.fields):
            field.active = i == index
        self.active_index = index

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, big_font: pygame.font.Font) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((15, 15, 30, 200))
        surface.blit(overlay, (0, 0))

        form_width = surface.get_width() - 200
        form_height = surface.get_height() - 200
        form_rect = pygame.Rect(100, 100, form_width, form_height)
        pygame.draw.rect(surface, (245, 246, 255), form_rect, border_radius=12)
        pygame.draw.rect(surface, (70, 90, 160), form_rect, 3, border_radius=12)

        title_surface = big_font.render(self.title, True, (40, 40, 70))
        surface.blit(title_surface, (form_rect.x + 30, form_rect.y + 20))

        current_y = form_rect.y + 80
        for field in self.fields:
            field.rect.x = form_rect.x + 40
            field.rect.y = current_y
            field.draw(surface, font)
            current_y += field.rect.height + 50

        if self.helper_text:
            helper_surface = font.render(self.helper_text, True, (90, 100, 140))
            surface.blit(helper_surface, (form_rect.x + 40, form_rect.bottom - 120))

        button_y = form_rect.bottom - 70
        if self.secondary_button is None:
            self.submit_button.rect.center = (form_rect.centerx - 100, button_y)
            self.cancel_button.rect.center = (form_rect.centerx + 100, button_y)
        else:
            self.submit_button.rect.center = (form_rect.centerx - 200, button_y)
            self.secondary_button.rect.center = (form_rect.centerx, button_y)
            self.cancel_button.rect.center = (form_rect.centerx + 200, button_y)

        self.submit_button.draw(surface, font)
        self.cancel_button.draw(surface, font)
        if self.secondary_button is not None:
            self.secondary_button.draw(surface, font)


# -- Drawing utilities --------------------------------------------------


def draw_multiline_text(surface: pygame.Surface, text: str, font: pygame.font.Font, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
    lines: List[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            test_line = (line + " " + word).strip()
            if font.size(test_line)[0] <= rect.width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
    y = rect.y
    for line in lines:
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (rect.x, y))
        y += font.get_linesize()


def draw_background(surface: pygame.Surface) -> None:
    width, height = surface.get_size()
    gradient = pygame.Surface((1, height))
    top_color = (24, 27, 51)
    bottom_color = (58, 45, 102)
    for y in range(height):
        ratio = y / max(1, height - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        gradient.set_at((0, y), (r, g, b))
    gradient = pygame.transform.smoothscale(gradient, (width, height))
    surface.blit(gradient, (0, 0))
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((15, 18, 30, 40))
    surface.blit(overlay, (0, 0))


def draw_card(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int], border_color: tuple[int, int, int]) -> None:
    card = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(card, color + (190,), card.get_rect(), border_radius=14)
    surface.blit(card, rect.topleft)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=14)


def draw_header(
    surface: pygame.Surface,
    message: str,
    live_activity: List[str],
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    big_font: pygame.font.Font,
    logged_in_user: Optional[User],
) -> None:
    header_rect = pygame.Rect(20, 10, surface.get_width() - 40, 130)
    draw_card(surface, header_rect, (62, 72, 124), (120, 148, 220))

    title_surface = big_font.render("Social Net System", True, (250, 252, 255))
    surface.blit(title_surface, (header_rect.x + 24, header_rect.y + 16))

    subtitle = small_font.render(
        "Simulación de red social con actividad en tiempo real",
        True,
        (220, 226, 250),
    )
    surface.blit(subtitle, (header_rect.x + 24, header_rect.y + 44))

    session_text = (
        f"Sesión activa: {logged_in_user.full_name} (@{logged_in_user.username})"
        if logged_in_user
        else "Sin sesión activa · inicia sesión para crear publicaciones"
    )
    session_surface = small_font.render(session_text, True, (214, 222, 255))
    surface.blit(session_surface, (header_rect.x + 24, header_rect.y + 66))

    message_surface = font.render(message, True, (253, 255, 255))
    surface.blit(message_surface, (header_rect.x + 24, header_rect.y + 92))

    if live_activity:
        pill_rect = pygame.Rect(header_rect.right - 280, header_rect.y + 20, 260, 88)
        draw_card(surface, pill_rect, (46, 54, 96), (110, 140, 210))
        label = small_font.render("Actividad reciente", True, (216, 222, 255))
        surface.blit(label, (pill_rect.x + 16, pill_rect.y + 8))
        for idx, item in enumerate(reversed(live_activity[-4:])):
            text_surface = small_font.render(f"• {item}", True, (230, 234, 255))
            surface.blit(text_surface, (pill_rect.x + 16, pill_rect.y + 26 + idx * 16))
# -- App ----------------------------------------------------------------


def main() -> None:
    screen = pygame.display.set_mode((1100, 700))
    pygame.display.set_caption("Social Net System")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 20)
    small_font = pygame.font.SysFont("Arial", 16)
    big_font = pygame.font.SysFont("Arial", 28, bold=True)

    network = SocialNetwork()
    network.seed_demo_data()
    pygame.time.set_timer(AUTO_ACTIVITY_EVENT, 5000)

    buttons: List[Button] = []
    message = "Inicia sesión para comenzar"
    notification_log: List[str] = []
    search_posts_results: List[Post] = []
    live_activity: List[str] = []
    active_form: Optional[Form] = None
    selected_user: Optional[User] = None
    logged_in_user: Optional[User] = None

    def set_message(text: str) -> None:
        nonlocal message
        message = text

    def close_form() -> None:
        nonlocal active_form
        active_form = None

    def set_logged_in(user: User) -> None:
        nonlocal logged_in_user, selected_user
        logged_in_user = user
        selected_user = user
        set_message(f"Sesión iniciada como {user.username}")
        update_session_ui()

    def logout() -> None:
        nonlocal logged_in_user, selected_user, search_posts_results
        logged_in_user = None
        selected_user = None
        search_posts_results = []
        set_message("Sesión cerrada. Inicia sesión para participar.")
        update_session_ui()

    def require_session(action: str = "realizar esta acción") -> bool:
        if logged_in_user is None:
            set_message(f"Inicia sesión para {action}")
            open_login_form()
            return False
        return True

    def open_login_form() -> None:
        nonlocal active_form

        def submit(values: List[str]) -> None:
            username, password = values
            if not username or not password:
                set_message("Ingresa usuario y contraseña")
                return
            try:
                user = network.authenticate_user(username, password)
            except ValueError as exc:
                set_message(str(exc))
                return
            set_logged_in(user)
            close_form()

        def go_register() -> None:
            close_form()
            open_register_form()

        fields = [
            InputField("Usuario", pygame.Rect(0, 0, 360, 44)),
            InputField("Contraseña", pygame.Rect(0, 0, 360, 44), password=True),
        ]
        active_form = Form(
            "Iniciar sesión",
            fields,
            submit,
            close_form,
            submit_label="Entrar",
            cancel_label="Cerrar",
            secondary_action=("Crear cuenta", go_register),
            helper_text="Accede con tu cuenta para publicar, reaccionar y gestionar tu red.",
        )

    def open_register_form() -> None:
        nonlocal active_form, live_activity

        def submit(values: List[str]) -> None:
            username, full_name, bio, password, confirm = values
            if not username or not full_name:
                set_message("Completa usuario y nombre")
                return
            if len(password) < 4:
                set_message("La contraseña debe tener al menos 4 caracteres")
                return
            if password != confirm:
                set_message("Las contraseñas no coinciden")
                return
            try:
                user = network.add_user(username, full_name, bio, password)
            except ValueError as exc:
                set_message(str(exc))
                return
            set_logged_in(user)
            set_message(f"Bienvenido {user.full_name}")
            live_activity.append(f"{user.full_name} se unió a la red")
            live_activity[:] = live_activity[-6:]
            close_form()

        def go_login() -> None:
            close_form()
            open_login_form()

        fields = [
            InputField("Usuario", pygame.Rect(0, 0, 380, 44)),
            InputField("Nombre completo", pygame.Rect(0, 0, 380, 44)),
            InputField("Biografía", pygame.Rect(0, 0, 380, 100), multiline=True),
            InputField("Contraseña", pygame.Rect(0, 0, 380, 44), password=True),
            InputField("Confirmar contraseña", pygame.Rect(0, 0, 380, 44), password=True),
        ]
        active_form = Form(
            "Crear cuenta",
            fields,
            submit,
            close_form,
            submit_label="Crear cuenta",
            cancel_label="Cancelar",
            secondary_action=("Ya tengo cuenta", go_login),
            helper_text="Tu contraseña se guarda cifrada solo para esta demostración.",
        )

    def add_friend_form() -> None:
        nonlocal active_form
        if not require_session("agregar amigos"):
            return

        def submit(values: List[str]) -> None:
            friend_username = values[0]
            try:
                assert logged_in_user is not None
                network.add_friend(logged_in_user.username, friend_username)
                set_message(f"Ahora {logged_in_user.username} es amigo de {friend_username}")
            except ValueError as exc:
                set_message(str(exc))
            close_form()

        fields = [InputField("Usuario a agregar", pygame.Rect(0, 0, 400, 40))]
        active_form = Form("Agregar amigo", fields, submit, close_form)

    def create_post_form() -> None:
        nonlocal active_form, live_activity
        if not require_session("crear publicaciones"):
            return

        def submit(values: List[str]) -> None:
            content = values[0]
            if not content:
                set_message("El contenido no puede estar vacío")
                return
            assert logged_in_user is not None
            post = network.create_post(logged_in_user.username, content)
            set_message(f"Publicación #{post.post_id} creada por {logged_in_user.username}")
            live_activity.append(f"{logged_in_user.full_name} publicó #{post.post_id}")
            live_activity[:] = live_activity[-6:]
            close_form()

        fields = [InputField("Contenido de la publicación", pygame.Rect(0, 0, 500, 120), multiline=True)]
        active_form = Form("Crear publicación", fields, submit, close_form)

    def like_post_form() -> None:
        nonlocal active_form, live_activity
        if not require_session("reaccionar a publicaciones"):
            return

        def submit(values: List[str]) -> None:
            try:
                post_id = int(values[0])
            except ValueError:
                set_message("El identificador debe ser un número")
                return
            try:
                assert logged_in_user is not None
                network.like_post(logged_in_user.username, post_id)
                set_message(f"Te gustó la publicación #{post_id}")
                live_activity.append(f"{logged_in_user.full_name} reaccionó a #{post_id}")
                live_activity[:] = live_activity[-6:]
            except ValueError as exc:
                set_message(str(exc))
            close_form()

        fields = [InputField("ID de publicación", pygame.Rect(0, 0, 240, 40))]
        active_form = Form("Dar me gusta", fields, submit, close_form)

    def comment_post_form() -> None:
        nonlocal active_form, live_activity
        if not require_session("comentar publicaciones"):
            return

        def submit(values: List[str]) -> None:
            try:
                post_id = int(values[0])
            except ValueError:
                set_message("El identificador debe ser un número")
                return
            comment = values[1]
            if not comment:
                set_message("Escribe un comentario")
                return
            try:
                assert logged_in_user is not None
                network.comment_post(logged_in_user.username, post_id, comment)
                set_message(f"Comentaste la publicación #{post_id}")
                live_activity.append(f"{logged_in_user.full_name} comentó en #{post_id}")
                live_activity[:] = live_activity[-6:]
            except ValueError as exc:
                set_message(str(exc))
            close_form()

        fields = [
            InputField("ID de publicación", pygame.Rect(0, 0, 240, 40)),
            InputField("Comentario", pygame.Rect(0, 0, 460, 120), multiline=True),
        ]
        active_form = Form("Comentar publicación", fields, submit, close_form)

    def show_notifications() -> None:
        if not require_session("revisar notificaciones"):
            return
        assert logged_in_user is not None
        notifications = network.pop_notifications(logged_in_user.username)
        if notifications:
            notification_log.extend(notifications)
            if len(notification_log) > 24:
                del notification_log[:-24]
            set_message(f"Mostrando {len(notifications)} notificaciones nuevas")
        else:
            set_message("Sin notificaciones nuevas")

    def search_posts_form() -> None:
        nonlocal active_form

        def submit(values: List[str]) -> None:
            nonlocal search_posts_results
            term = values[0]
            if not term:
                search_posts_results = []
                set_message("Se muestran las publicaciones destacadas")
            else:
                search_posts_results = network.search_posts(term)
                set_message(f"{len(search_posts_results)} publicaciones coinciden con '{term}'")
            close_form()

        fields = [InputField("Buscar publicaciones", pygame.Rect(0, 0, 360, 40))]
        active_form = Form("Buscar", fields, submit, close_form)

    def search_users_form() -> None:
        nonlocal active_form

        def submit(values: List[str]) -> None:
            nonlocal selected_user
            term = values[0]
            users = network.search_users(term)
            if users:
                selected_user = users[0]
                if logged_in_user and selected_user.username == logged_in_user.username:
                    set_message("Se seleccionó tu propio perfil")
                else:
                    set_message(f"Se seleccionó a {selected_user.username}")
            else:
                set_message("No se encontraron usuarios")
            close_form()

        fields = [InputField("Buscar usuarios", pygame.Rect(0, 0, 360, 40))]
        active_form = Form("Buscar usuarios", fields, submit, close_form)

    session_button = Button(pygame.Rect(260, 20, 150, 40), "Iniciar sesión", open_login_form)
    register_button = Button(pygame.Rect(420, 20, 150, 40), "Registrarse", open_register_form)
    add_friend_button = Button(pygame.Rect(580, 20, 150, 40), "Agregar amigo", add_friend_form)
    create_post_button = Button(pygame.Rect(740, 20, 150, 40), "Crear post", create_post_form)
    like_post_button = Button(pygame.Rect(900, 20, 150, 40), "Me gusta", like_post_form)
    comment_button = Button(pygame.Rect(260, 70, 150, 36), "Comentar", comment_post_form)
    notifications_button = Button(pygame.Rect(420, 70, 150, 36), "Notificaciones", show_notifications)
    search_posts_button = Button(pygame.Rect(580, 70, 150, 36), "Buscar posts", search_posts_form)
    search_users_button = Button(pygame.Rect(740, 70, 150, 36), "Buscar usuarios", search_users_form)

    buttons = [
        session_button,
        register_button,
        add_friend_button,
        create_post_button,
        like_post_button,
        comment_button,
        notifications_button,
        search_posts_button,
        search_users_button,
    ]

    gated_buttons = [
        add_friend_button,
        create_post_button,
        like_post_button,
        comment_button,
        notifications_button,
    ]

    def update_session_ui() -> None:
        if logged_in_user is None:
            session_button.label = "Iniciar sesión"
            session_button.callback = open_login_form
            register_button.enabled = True
        else:
            session_button.label = "Cerrar sesión"
            session_button.callback = logout
            register_button.enabled = False
        for button in gated_buttons:
            button.enabled = logged_in_user is not None

    update_session_ui()
    open_login_form()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == AUTO_ACTIVITY_EVENT:
                updates = network.simulate_activity()
                if updates:
                    live_activity.extend(updates)
                    live_activity[:] = live_activity[-6:]
                    set_message(updates[-1])
                continue
            if active_form is not None:
                active_form.handle_event(event)
            else:
                for button in buttons:
                    button.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    picked_user = handle_user_click(network, event.pos)
                    if picked_user is not None:
                        selected_user = picked_user
                        if logged_in_user and selected_user.username == logged_in_user.username:
                            set_message("Visualizas tu perfil")
                        else:
                            set_message(f"Explorando a {selected_user.username}")
        render(
            screen,
            network,
            buttons,
            selected_user,
            message,
            notification_log,
            search_posts_results,
            live_activity,
            logged_in_user,
            active_form,
            font,
            small_font,
            big_font,
        )
        pygame.display.flip()
        clock.tick(30)


def handle_user_click(network: SocialNetwork, pos: tuple[int, int]) -> Optional[User]:
    user_area = pygame.Rect(35, 150, 190, 470)
    if not user_area.collidepoint(pos):
        return None
    usernames = list(network.users.keys())
    index = (pos[1] - user_area.y) // 80
    if 0 <= index < len(usernames):
        return network.users[usernames[index]]
    return None


def render(
    screen: pygame.Surface,
    network: SocialNetwork,
    buttons: List[Button],
    selected_user: Optional[User],
    message: str,
    notification_log: List[str],
    search_posts_results: List[Post],
    live_activity: List[str],
    logged_in_user: Optional[User],
    active_form: Optional[Form],
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    big_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    draw_header(screen, message, live_activity, font, small_font, big_font, logged_in_user)

    draw_card(screen, pygame.Rect(20, 130, 210, 520), (54, 63, 110), (110, 138, 210))
    draw_card(screen, pygame.Rect(240, 140, 830, 220), (54, 63, 110), (110, 138, 210))
    draw_card(screen, pygame.Rect(240, 380, 830, 310), (54, 63, 110), (110, 138, 210))

    title_surface = big_font.render("Usuarios", True, (232, 236, 255))
    screen.blit(title_surface, (60, 140))

    for button in buttons:
        button.draw(screen, font)

    draw_user_list(screen, network, selected_user, logged_in_user, font, small_font)
    draw_feed(screen, network, font, small_font, search_posts_results)
    panel_user = selected_user if selected_user is not None else logged_in_user
    draw_user_panel(screen, panel_user, notification_log, font, small_font, logged_in_user)

    if active_form is not None:
        active_form.draw(screen, font, big_font)


def draw_user_list(
    screen: pygame.Surface,
    network: SocialNetwork,
    selected_user: Optional[User],
    session_user: Optional[User],
    font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    area = pygame.Rect(35, 150, 190, 470)
    usernames = list(network.users.keys())
    for idx, username in enumerate(usernames):
        item_rect = pygame.Rect(area.x, area.y + idx * 80, area.width, 68)
        if item_rect.bottom > area.bottom + 60:
            break
        is_selected = selected_user and selected_user.username == username
        is_session = session_user and session_user.username == username
        base_color = (92, 112, 190) if is_selected else (70, 86, 148)
        glow = pygame.Surface(item_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow, base_color + (210,), glow.get_rect(), border_radius=14)
        screen.blit(glow, item_rect.topleft)
        pygame.draw.rect(screen, (180, 198, 255) if is_selected else (120, 140, 210), item_rect, 2, border_radius=14)

        user = network.users[username]
        avatar_rect = pygame.Rect(item_rect.x + 12, item_rect.y + 14, 40, 40)
        pygame.draw.circle(screen, (234, 242, 255) if is_selected else (206, 212, 240), avatar_rect.center, 20)
        initials = user.full_name[:2].upper()
        initials_surface = small_font.render(initials, True, (62, 72, 120))
        initials_rect = initials_surface.get_rect(center=avatar_rect.center)
        screen.blit(initials_surface, initials_rect)

        name_surface = font.render(user.full_name, True, (250, 250, 255))
        screen.blit(name_surface, (item_rect.x + 64, item_rect.y + 14))
        username_surface = small_font.render(f"@{user.username}", True, (220, 226, 250))
        screen.blit(username_surface, (item_rect.x + 64, item_rect.y + 38))

        if is_session:
            tag_rect = pygame.Rect(item_rect.right - 74, item_rect.y + 12, 58, 20)
            pygame.draw.rect(screen, (188, 226, 255), tag_rect, border_radius=10)
            tag_surface = small_font.render("Tú", True, (40, 70, 110))
            screen.blit(tag_surface, tag_surface.get_rect(center=tag_rect.center))


def draw_feed(screen: pygame.Surface, network: SocialNetwork, font: pygame.font.Font, small_font: pygame.font.Font, search_posts_results: List[Post]) -> None:
    area = pygame.Rect(250, 150, 810, 210)
    label = "Resultados de búsqueda" if search_posts_results else "Top publicaciones"
    title = font.render(label, True, (232, 236, 255))
    screen.blit(title, (area.x + 10, area.y - 32))
    posts = search_posts_results if search_posts_results else network.get_top_posts()
    ticks = pygame.time.get_ticks()
    for idx, post in enumerate(posts[:5]):
        item_rect = pygame.Rect(area.x + 14, area.y + idx * 40 + 10, area.width - 28, 36)
        pulse = (ticks // 12 + idx * 18) % 120
        base_color = (
            min(255, 70 + pulse),
            min(255, 80 + idx * 12),
            min(255, 140 + pulse // 2),
        )
        item_surface = pygame.Surface(item_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(item_surface, base_color + (210,), item_surface.get_rect(), border_radius=12)
        screen.blit(item_surface, item_rect.topleft)
        pygame.draw.rect(screen, (210, 220, 255), item_rect, 1, border_radius=12)

        summary = small_font.render(f"#{post.post_id} {post.summary()}", True, (253, 254, 255))
        stats = small_font.render(f"❤ {len(post.likes)}   💬 {len(post.comments)}", True, (250, 210, 234))
        screen.blit(summary, (item_rect.x + 16, item_rect.y + 8))
        screen.blit(stats, (item_rect.right - 150, item_rect.y + 8))


def draw_user_panel(
    screen: pygame.Surface,
    user: Optional[User],
    notification_log: List[str],
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    session_user: Optional[User],
) -> None:
    area = pygame.Rect(250, 390, 810, 290)
    title = font.render("Resumen del usuario", True, (232, 236, 255))
    screen.blit(title, (area.x + 10, area.y - 32))

    if not user and not session_user:
        hint = small_font.render("Inicia sesión o selecciona un usuario para ver detalles", True, (224, 228, 248))
        screen.blit(hint, (area.x + 20, area.y + 20))
        return

    if not user and session_user is not None:
        user = session_user

    if user is None:
        hint = small_font.render("Selecciona un usuario para ver detalles", True, (224, 228, 248))
        screen.blit(hint, (area.x + 20, area.y + 20))
        return

    header_rect = pygame.Rect(area.x + 20, area.y + 16, area.width - 40, 90)
    draw_card(screen, header_rect, (72, 88, 148), (140, 170, 240))
    name_surface = font.render(user.full_name, True, (253, 254, 255))
    screen.blit(name_surface, (header_rect.x + 20, header_rect.y + 14))
    username_surface = small_font.render(f"@{user.username}", True, (216, 224, 248))
    screen.blit(username_surface, (header_rect.x + 20, header_rect.y + 42))
    bio_surface = small_font.render(user.bio or "Sin biografía", True, (216, 224, 248))
    screen.blit(bio_surface, (header_rect.x + 20, header_rect.y + 64))

    is_session_user = session_user is not None and user.username == session_user.username
    pending = len(user.notifications) if not is_session_user else len(session_user.notifications)
    badge_text = "Tus notificaciones pendientes" if is_session_user else "Notificaciones pendientes"
    badge = small_font.render(f"{badge_text}: {pending}", True, (240, 244, 255))
    screen.blit(badge, (header_rect.right - 280, header_rect.y + 20))

    if session_user is not None:
        context_text = (
            "Visualizas tu propio perfil"
            if is_session_user
            else f"Sesión activa: {session_user.full_name} (@{session_user.username})"
        )
        context_surface = small_font.render(context_text, True, (200, 212, 252))
        screen.blit(context_surface, (header_rect.x + 20, header_rect.bottom - 22))

    friends_rect = pygame.Rect(area.x + 20, area.y + 120, 240, 130)
    draw_card(screen, friends_rect, (66, 80, 134), (130, 160, 228))
    friends_title = small_font.render("Amigos", True, (234, 238, 255))
    screen.blit(friends_title, (friends_rect.x + 16, friends_rect.y + 10))
    if user.friends:
        for idx, friend in enumerate(sorted(user.friends)):
            friend_surface = small_font.render(f"• {friend}", True, (224, 230, 255))
            screen.blit(friend_surface, (friends_rect.x + 16, friends_rect.y + 30 + idx * 18))
            if friends_rect.y + 30 + idx * 18 > friends_rect.bottom - 24:
                break
    else:
        screen.blit(small_font.render("Sin amigos todavía", True, (224, 230, 255)), (friends_rect.x + 16, friends_rect.y + 36))

    posts_rect = pygame.Rect(area.x + 280, area.y + 120, 270, 130)
    draw_card(screen, posts_rect, (66, 80, 134), (130, 160, 228))
    posts_title = small_font.render("Publicaciones recientes", True, (234, 238, 255))
    screen.blit(posts_title, (posts_rect.x + 16, posts_rect.y + 10))
    for idx, post in enumerate(list(user.posts)[-3:][::-1]):
        preview = post.content[:60] + ("..." if len(post.content) > 60 else "")
        post_surface = small_font.render(f"#{post.post_id} {preview}", True, (224, 230, 255))
        screen.blit(post_surface, (posts_rect.x + 16, posts_rect.y + 30 + idx * 18))

    notif_rect = pygame.Rect(area.x + 570, area.y + 120, 240, 130)
    draw_card(screen, notif_rect, (66, 80, 134), (130, 160, 228))
    notif_title = small_font.render("Historial de notificaciones", True, (234, 238, 255))
    screen.blit(notif_title, (notif_rect.x + 16, notif_rect.y + 10))
    if session_user is None:
        screen.blit(
            small_font.render("Inicia sesión para revisar tus avisos", True, (224, 230, 255)),
            (notif_rect.x + 16, notif_rect.y + 36),
        )
    elif notification_log:
        for idx, note in enumerate(notification_log[-4:][::-1]):
            note_surface = small_font.render(note, True, (224, 230, 255))
            screen.blit(note_surface, (notif_rect.x + 16, notif_rect.y + 30 + idx * 18))
    else:
        screen.blit(small_font.render("Sin notificaciones", True, (224, 230, 255)), (notif_rect.x + 16, notif_rect.y + 36))


if __name__ == "__main__":
    main()
