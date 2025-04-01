import random
import xml.etree.ElementTree as ET
import dearpygui.dearpygui as dpg

# --- Data Structures ---
users = []
resources = []
current_user = None
selected_user = None

XML_FILE = "users_data.xml"


def generate_users(n):
    global users, resources
    users.clear()
    resources = [f"ресурс{i + 1}" for i in range(n)]
    roles = ["Администратор"] + [random.choice(["Пользователь", "Гость"]) for _ in range(n - 1)]
    random.shuffle(roles)
    for i in range(n):
        res_count = random.randint(1, n)
        assigned = random.sample(resources, res_count)
        perms = {}
        for r in assigned:
            perms[r] = random.choice(["Чтение", "Запись", "Изменение"])
        users.append({
            "name": f"пользователь{i + 1}",
            "password": "123",
            "role": roles[i],
            "resources": perms
        })
    save_to_xml()
    load_from_xml()


def save_to_xml():
    root = ET.Element("users")
    for user in users:
        u = ET.SubElement(root, "user")
        ET.SubElement(u, "name").text = user["name"]
        ET.SubElement(u, "password").text = user["password"]
        ET.SubElement(u, "role").text = user["role"]
        res_elem = ET.SubElement(u, "resources")
        for r, p in user["resources"].items():
            re = ET.SubElement(res_elem, "resource", name=r)
            re.text = p
    ET.ElementTree(root).write(XML_FILE, encoding="utf-8")


def load_from_xml():
    global users, resources
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    users.clear()
    resources = set()
    for u in root.findall("user"):
        name = u.find("name").text
        password = u.find("password").text
        role = u.find("role").text
        res_map = {}
        for r in u.find("resources").findall("resource"):
            res_map[r.attrib["name"]] = r.text
            resources.add(r.attrib["name"])
        users.append({
            "name": name,
            "password": password,
            "role": role,
            "resources": res_map
        })
    resources = list(resources)
    render_user_table()


def render_user_table():
    dpg.delete_item("user_table", children_only=True)
    with dpg.table(header_row=True, parent="user_table"):
        dpg.add_table_column(label="Имя")
        dpg.add_table_column(label="Роль")
        for u in users:
            with dpg.table_row():
                dpg.add_selectable(label=u["name"],
                                   callback=lambda s, a, name=u["name"]: handle_selection_by_name(name, 'select_auth'),
                                   tag=f"select_auth_{u['name']}", span_columns=True)
                dpg.add_text(u["role"])


def select_user(user):
    if user is None:
        return
    global selected_user
    selected_user = user
    dpg.set_value("selected_user_label", user["name"])


def login_window():
    with dpg.window(label="Вход", modal=True, tag="login_win", width=300, height=150):
        dpg.add_input_text(label="Пароль", tag="login_pass", password=True)
        dpg.add_button(label="Войти", callback=login_action)


def login_action():
    global current_user
    password = dpg.get_value("login_pass")
    if not selected_user:
        dpg.configure_item("login_win", label="Ошибка: пользователь не выбран")
        return

    print(
        f"DEBUG: Попытка входа: выбран {selected_user['name']} с паролем {selected_user['password']}, введено: {password}")

    if password == selected_user["password"]:
        current_user = selected_user
        dpg.delete_item("login_win")
        render_secondary_tables()

    else:
        dpg.set_value("login_pass", "")
        dpg.configure_item("login_win", label="Неверный пароль. Повторите ввод")


def handle_selection_by_name(name, prefix):
    user = next((u for u in users if u['name'] == name), None)
    if user:
        handle_selection(user, prefix)


def handle_selection(user, prefix):
    if user is None:
        return
    for u in users:
        dpg.configure_item(f"{prefix}_{u['name']}", default_value=False)
    dpg.set_value(f"{prefix}_{user['name']}", True)
    if prefix == 'select_access':
        show_resources(user)
    elif prefix == 'select_auth':
        select_user(user)


def render_secondary_tables():
    with dpg.group(tag="secondary_tables", parent="main"):
        dpg.add_text(f"Вы вошли как: {current_user['name']} ({current_user['role']})")
        with dpg.group(horizontal=True):
            with dpg.group():
                with dpg.child_window(height=180, width=300):
                    dpg.add_text("Пользователи (Авторизация):")
                    with dpg.table(header_row=True):
                        dpg.add_table_column(label="Имя")
                        dpg.add_table_column(label="Роль")
                        for u in users:
                            if u != current_user:
                                with dpg.table_row():
                                    dpg.add_selectable(label=u["name"],
                                                       callback=lambda s, a, u=u: handle_selection(u, 'select_access'),
                                                       tag=f"select_access_{u['name']}", span_columns=True)
                                    dpg.add_text(u["role"])
                with dpg.child_window(height=200, width=300):
                    dpg.add_text("Пользователи (Доступ):")
                    with dpg.table(header_row=True):
                        dpg.add_table_column(label="Имя")
                        dpg.add_table_column(label="Роль")
                        for u in users:
                            if u != current_user:
                                with dpg.table_row():
                                    dpg.add_text(u["name"])
                                    dpg.add_text(u["role"])
            with dpg.child_window(height=400, width=400):
                dpg.add_text("Ресурсы:")
                with dpg.group(tag="resource_table"):
                    pass
        with dpg.group(horizontal=True):
            dpg.add_button(label="Войти", callback=login_window)
            dpg.add_button(label="Сохранить", callback=save_to_xml)
            dpg.add_button(label="Загрузить", callback=load_from_xml)


def show_resources(user):
    dpg.delete_item("resource_table", children_only=True)
    dpg.add_text(f"Ресурсы пользователя: {user['name']} ({user['role']})", parent="resource_table")
    for r in resources:
        perm = user["resources"].get(r, "-")
        if current_user["role"] == "Администратор":
            dpg.add_combo(["Чтение", "Запись", "Изменение"], default_value=perm, label=r,
                          callback=lambda s, a, r=r, u=user: set_permission(u, r, a), parent="resource_table")
        else:
            dpg.add_text(f"{r}: {perm}", parent="resource_table")


def set_permission(user, resource, access):
    user["resources"][resource] = access


# --- GUI Setup ---
dpg.create_context()

# Поддержка кириллицы
with dpg.font_registry():
    with dpg.font("C:/Windows/Fonts/times.ttf", 14) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

dpg.bind_font(default_font)

dpg.create_viewport(title="Управление доступом", width=1000, height=700)

with dpg.window(label="Управление", tag="main"):
    dpg.add_input_int(label="Кол-во пользователей", tag="user_count", width=150)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Сгенерировать", callback=lambda: generate_users(dpg.get_value("user_count")))
    dpg.add_text("Выбран:", bullet=True)
    dpg.add_text("", tag="selected_user_label")
    with dpg.group(tag="user_table"):
        pass
    with dpg.group(horizontal=True, tag="action_buttons"):
        dpg.add_button(label="Войти", callback=login_window)
        dpg.add_button(label="Сохранить", callback=save_to_xml)
        dpg.add_button(label="Загрузить", callback=load_from_xml)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
