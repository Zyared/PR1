import random
import time
import xml.etree.ElementTree as ET
import dearpygui.dearpygui as dpg
# Глобальные переменные
users_data = []              # Список пользователей (каждый – dict с ключами: name, password, role, resources, editing)
selected_user_index = None   # Выбранный пользователь из Table1 (для логина)
selected_edit_user_index = None  # Выбранный пользователь из Table2, для которого редактируются ресурсы
# Для детекции двойного клика в Table2
_last_click_user = None
_last_click_time = 0
_DOUBLE_CLICK_THRESHOLD = 0.3  # секунды
# Функция обновления текста текущего авторизованного пользователя
def update_current_user_text():
    if selected_user_index is not None:
        current = f"Авторизованный пользователь: {users_data[selected_user_index]['name']}"
    else:
        current = "Авторизованный пользователь: None"
    dpg.set_value("current_user_text", current)
# ---------------------------
# Table1: Выбор пользователя для логина
# ---------------------------
def select_user_callback(sender, app_data, user_data):
    global selected_user_index
    selected_user_index = user_data
    print("Table1: выбран пользователь:", users_data[selected_user_index]["name"])
    update_current_user_text()
# ---------------------------
# Генерация пользователей
# ---------------------------
def generate_users_callback():
    global users_data, selected_user_index
    user_count = dpg.get_value("user_count_input")
    users_data = []
    selected_user_index = None
    clear_table("Table1")
    roles = ["Пользователь", "Гость", "Администратор"]
    access_options = ["Чтение", "Запись", "Изменение"]
    names = ["toxic", "Drakess", "fenix", "jebac", "Prass ALT F4", "zvR", "FoXy", "Insanity",
             "Монстер", "K3n4", "xx_x_xx", "LiMoH4iK", "pik", "l0vin", "matthew",
             "maybach", "swta", "Drakess", "stizzy", "Zyared", "Zitrex", "Scrapyard", "AwP_Only^^", "Fearless"]
    for i in range(user_count):
        role = random.choice(roles)
        name = f"{random.choice(names)} {random.randint(1, 9999)}"
        password = "123"
        res_count = random.randint(1, 10)
        resources = []
        for j in range(1, res_count + 1):
            resources.append({"name": f"Ресурс {j}", "access": random.choice(access_options)})
        # Флаг редактирования имени (False по умолчанию)
        user = {"name": name,
                "password": password,
                "role": role,
                "resources": resources,
                "editing": False}
        users_data.append(user)
        row_id = dpg.add_table_row(parent="Table1")
        dpg.add_selectable(label=name, callback=select_user_callback, user_data=i, parent=row_id)
        dpg.add_text(role, parent=row_id)
        print(f"Сгенерирован пользователь: {name}, роль: {role}, пароль: {password}, ресурсов: {len(resources)}")
    update_current_user_text()
# ---------------------------
# Логин
# ---------------------------
def login_callback():
    if selected_user_index is None:
        print("Пользователь не выбран!")
        return
    dpg.configure_item("password_popup", show=True)
def check_password_callback(sender, app_data, user_data):
    if selected_user_index is None:
        return
    input_password = dpg.get_value("password_input")
    if input_password == users_data[selected_user_index]["password"]:
        print("Пароль верный, вход выполнен!")
        dpg.configure_item("password_popup", show=False)
        clear_table("Table2")
        update_table2()
        update_current_user_text()
    else:
        print("Неверный пароль!")
# ---------------------------
# Очистка таблицы (удаляет только строки)
# ---------------------------
def clear_table(table_tag):
    children = dpg.get_item_children(table_tag)
    if children is not None and 1 in children:
        for row in list(children[1]):
            dpg.delete_item(row)
# ---------------------------
# Обновление Table2 – список пользователей
# Если авторизованный пользователь (из Table1) – администратор, то при двойном клике по имени включается режим редактирования,
# где вместо selectable отображается поле ввода с уникальным тегом.
# ---------------------------
def update_table2():
    clear_table("Table2")
    admin_mode = (selected_user_index is not None and users_data[selected_user_index]["role"] == "Администратор")
    for i, user in enumerate(users_data):
        row_id = dpg.add_table_row(parent="Table2")
        if admin_mode:
            if user.get("editing", False):
                tag_name = f"edit_user_name_{i}"
                dpg.add_input_text(default_value=user["name"],
                                   callback=update_user_name_callback,
                                   user_data=i,
                                   parent=row_id,
                                   tag=tag_name)
                dpg.add_button(label="Подтвердить изменения",
                               callback=confirm_user_name_change,
                               user_data=i,
                               parent=row_id)
            else:
                dpg.add_selectable(label=user["name"],
                                   callback=user_select_table2_callback,
                                   user_data=i,
                                   parent=row_id)
            dpg.add_text(user["role"], parent=row_id)
            dpg.add_button(label="Ресурсы",
                           callback=select_user_from_table2_callback,
                           user_data=i,
                           parent=row_id)
        else:
            dpg.add_selectable(label=user["name"],
                               callback=select_user_from_table2_callback,
                               user_data=i,
                               parent=row_id)
            dpg.add_text(user["role"], parent=row_id)
    print("Table2 обновлена, пользователей:", len(users_data))
# ---------------------------
# Обработка одиночного/двойного клика для имени в Table2
# ---------------------------
def user_select_table2_callback(sender, app_data, user_data):
    global _last_click_user, _last_click_time, selected_edit_user_index
    current_time = time.time()
    if _last_click_user == user_data and (current_time - _last_click_time) < _DOUBLE_CLICK_THRESHOLD:
        # Двойной клик — включаем режим редактирования имени
        users_data[user_data]["editing"] = True
        update_table2()
    else:
        selected_edit_user_index = user_data
        update_table3(user_data)
    _last_click_user = user_data
    _last_click_time = current_time
# ---------------------------
# Обновление имени пользователя (при редактировании в Table2)
# Эта функция не сохраняет значение сразу, ожидая нажатия кнопки подтверждения.
# ---------------------------
def update_user_name_callback(sender, app_data, user_data):
    pass
# ---------------------------
# Подтверждение изменения имени пользователя
# Извлекаем значение из поля ввода с уникальным тегом.
# ---------------------------
def confirm_user_name_change(sender, app_data, user_data):
    idx = user_data
    tag_name = f"edit_user_name_{idx}"
    new_name = dpg.get_value(tag_name)
    users_data[idx]["name"] = new_name
    users_data[idx]["editing"] = False
    print(f"Имя пользователя подтверждено -> {new_name}")
    update_table2()
    update_current_user_text()
# ---------------------------
# Кнопка "Ресурсы" в Table2
# ---------------------------
def select_user_from_table2_callback(sender, app_data, user_data):
    global selected_edit_user_index
    selected_edit_user_index = user_data
    print("Table2: выбран пользователь для ресурсов:", users_data[user_data]["name"])
    update_table3(user_data)
# ---------------------------
# Обновление Table3 – ресурсы выбранного пользователя
# Для администраторов доступны редактирование, добавление и удаление ресурсов.
# Для обычных пользователей – только просмотр.
# ---------------------------
def update_table3(user_index):
    if user_index is None:
        print("update_table3: user_index is None")
        return
    clear_table("Table3")
    user = users_data[user_index]
    admin_mode = (selected_user_index is not None and users_data[selected_user_index]["role"] == "Администратор")
    for i, res in enumerate(user["resources"]):
        row_id = dpg.add_table_row(parent="Table3")
        if admin_mode:
            dpg.add_input_text(default_value=res["name"],
                               callback=resource_name_callback,
                               user_data=(user_index, i),
                               parent=row_id)
            dpg.add_combo(items=["Чтение", "Запись", "Изменение"],
                          default_value=res["access"],
                          callback=resource_access_callback,
                          user_data=(user_index, i),
                          parent=row_id)
        else:
            dpg.add_text(res["name"], parent=row_id)
            dpg.add_text(res["access"], parent=row_id)
        if admin_mode:
            dpg.add_button(label="Удалить",
                           callback=delete_resource_wrapper,
                           user_data=(user_index, i),
                           parent=row_id)
    if admin_mode:
        row_id = dpg.add_table_row(parent="Table3")
        dpg.add_button(label="Добавить ресурс",
                       callback=add_resource_wrapper,
                       user_data=user_index,
                       parent=row_id)
    print(f"Table3 обновлена для пользователя {user['name']}, ресурсов: {len(user['resources'])}")
# ---------------------------
# Обёртки для редактирования ресурсов в Table3 (без inline lambda)
# ---------------------------
def resource_name_callback(sender, app_data, user_data):
    ui, idx = user_data
    update_resource_name(ui, idx, app_data)
def resource_access_callback(sender, app_data, user_data):
    ui, idx = user_data
    update_resource_access(ui, idx, app_data)
def delete_resource_wrapper(sender, app_data, user_data):
    ui, idx = user_data
    delete_resource_callback(ui, idx)
def add_resource_wrapper(sender, app_data, user_data):
    add_resource_callback(user_data)
# ---------------------------
# Основные функции редактирования ресурсов
# ---------------------------
def update_resource_name(user_index, resource_index, new_value):
    users_data[user_index]["resources"][resource_index]["name"] = new_value
    print(f"Обновлено имя ресурса {resource_index} для пользователя {users_data[user_index]['name']}: {new_value}")
def update_resource_access(user_index, resource_index, new_value):
    users_data[user_index]["resources"][resource_index]["access"] = new_value
    print(f"Обновлён доступ ресурса {resource_index} для пользователя {users_data[user_index]['name']}: {new_value}")
def delete_resource_callback(user_index, resource_index):
    if user_index is None:
        return
    del users_data[user_index]["resources"][resource_index]
    print(f"Удалён ресурс {resource_index} у пользователя {users_data[user_index]['name']}")
    update_table3(user_index)
def add_resource_callback(user_index):
    if user_index is None:
        return
    new_index = len(users_data[user_index]["resources"]) + 1
    users_data[user_index]["resources"].append({"name": f"Ресурс {new_index}", "access": "Чтение"})
    print(f"Добавлен новый ресурс для пользователя {users_data[user_index]['name']}")
    update_table3(user_index)
# ---------------------------
# Функции сохранения и загрузки XML с выбором файла
# ---------------------------
def save_to_xml(file_path):
    root = ET.Element("users")
    for user in users_data:
        user_el = ET.SubElement(root, "user")
        user_el.set("name", user["name"])
        user_el.set("password", user["password"])
        user_el.set("role", user["role"])
        resources_el = ET.SubElement(user_el, "resources")
        for res in user["resources"]:
            res_el = ET.SubElement(resources_el, "resource")
            res_el.set("name", res["name"])
            res_el.set("access", res["access"])
    tree = ET.ElementTree(root)
    try:
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print("Данные сохранены в", file_path)
    except Exception as e:
        print("Ошибка сохранения в XML:", e)
def load_from_xml(file_path):
    global users_data, selected_user_index, selected_edit_user_index
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        users_data = []
        for user_el in root.findall("user"):
            name = user_el.get("name")
            password = user_el.get("password")
            role = user_el.get("role")
            resources = []
            resources_el = user_el.find("resources")
            if resources_el is not None:
                for res_el in resources_el.findall("resource"):
                    res_name = res_el.get("name")
                    res_access = res_el.get("access")
                    resources.append({"name": res_name, "access": res_access})
            user = {"name": name, "password": password, "role": role, "resources": resources, "editing": False}
            users_data.append(user)
        selected_user_index = None
        selected_edit_user_index = None
        clear_table("Table1")
        for i, user in enumerate(users_data):
            row_id = dpg.add_table_row(parent="Table1")
            dpg.add_selectable(label=user["name"], callback=select_user_callback, user_data=i, parent=row_id)
            dpg.add_text(user["role"], parent=row_id)
        update_table2()
        update_current_user_text()
        print("Данные загружены из", file_path)
    except Exception as e:
        print("Ошибка загрузки из XML:", e)
# ---------------------------
# Функции открытия файловых диалогов
# ---------------------------
def open_save_dialog(sender, app_data, user_data):
    dpg.configure_item("save_file_dialog", show=True)
def open_load_dialog(sender, app_data, user_data):
    dpg.configure_item("load_file_dialog", show=True)
def save_file_callback(sender, app_data, user_data):
    file_path = app_data["file_path_name"]
    if file_path:
        save_to_xml(file_path)
def load_file_callback(sender, app_data, user_data):
    file_path = app_data["file_path_name"]
    if file_path:
        load_from_xml(file_path)
def save_button_callback(sender, app_data, user_data):
    open_save_dialog(sender, app_data, user_data)
def load_button_callback(sender, app_data, user_data):
    open_load_dialog(sender, app_data, user_data)
# ---------------------------
# Интерфейс и тема
# ---------------------------
dpg.create_context()
with dpg.font_registry():
    with dpg.font("C:/Windows/Fonts/times.ttf", 14) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
dpg.bind_font(default_font)
# Создадим простую тему для Selectable, чтобы выделение было более заметным
with dpg.theme() as selectable_theme:
    with dpg.theme_component(dpg.mvSelectable):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [60, 60, 60, 255])
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, [80, 80, 80, 255])
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, [120, 120, 120, 255])
        dpg.add_theme_color(dpg.mvThemeCol_Text, [220, 220, 220, 255])
dpg.bind_theme(selectable_theme)
dpg.create_viewport(title="Пример интерфейса Dear PyGui", width=900, height=600)
with dpg.window(label="Главное окно", tag="MainWindow", width=900, height=600):
    # Верхняя панель с информацией о текущем авторизованном пользователе
    with dpg.group(horizontal=True):
        dpg.add_text("Поле ввода кол-ва пользователей:")
        dpg.add_input_int(tag="user_count_input", width=100, default_value=3)
        dpg.add_button(label="Сгенерировать", callback=generate_users_callback)
    dpg.add_spacer(height=10)
    dpg.add_separator()
    dpg.add_spacer(height=10)
    # Отображение текущего авторизованного пользователя
    dpg.add_text("Авторизованный пользователь: None", tag="current_user_text")
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        with dpg.group():
            with dpg.child_window(width=400, height=200, tag="LeftPanel"):
                dpg.add_text("Table1")
                with dpg.table(header_row=True, borders_innerH=True, borders_innerV=True,
                               borders_outerH=True, borders_outerV=True, row_background=True,
                               resizable=True, policy=dpg.mvTable_SizingFixedFit, scrollY=True, tag="Table1"):
                    dpg.add_table_column(label="Имя")
                    dpg.add_table_column(label="Роль")
            with dpg.child_window(width=400, height=200, tag="UnderPanel"):
                dpg.add_text("Table2")
                with dpg.table(header_row=True, borders_innerH=True, borders_innerV=True,
                               borders_outerH=True, borders_outerV=True, row_background=True,
                               resizable=True, policy=dpg.mvTable_SizingStretchProp, scrollY=True, tag="Table2"):
                    dpg.add_table_column(label="Имя")
                    dpg.add_table_column(label="Роль")
        with dpg.child_window(width=400, height=400, tag="RightPanel"):
            dpg.add_text("Table3")
            with dpg.table(header_row=True, borders_innerH=True, borders_innerV=True,
                           borders_outerH=True, borders_outerV=True, row_background=True,
                           resizable=True, policy=dpg.mvTable_SizingFixedFit, scrollY=True, tag="Table3"):
                dpg.add_table_column(label="Ресурс")
                dpg.add_table_column(label="Доступ")
                dpg.add_table_column(label="Действие")
    dpg.add_spacer(height=10)
    dpg.add_separator()
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Войти", callback=login_callback)
        dpg.add_button(label="Сохранить", callback=save_button_callback)
        dpg.add_button(label="Загрузить", callback=load_button_callback)
with dpg.window(label="Ввод пароля", modal=True, show=False, tag="password_popup", no_title_bar=True, no_resize=True):
    dpg.add_text("Введите пароль:")
    dpg.add_input_text(tag="password_input", password=True)
    dpg.add_button(label="Подтвердить", callback=check_password_callback)
with dpg.file_dialog(directory_selector=False, show=False, callback=save_file_callback, tag="save_file_dialog", modal=True):
    dpg.add_file_extension(".xml")
with dpg.file_dialog(directory_selector=False, show=False, callback=load_file_callback, tag="load_file_dialog", modal=True):
    dpg.add_file_extension(".xml")
dpg.bind_font(default_font)
dpg.setup_dearpygui()
dpg.show_viewport()  # Правильный вызов для показа окна
dpg.start_dearpygui()
dpg.destroy_context()

