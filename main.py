import pygame
import sys
import datetime
import json

pygame.init()

#Display
WIDTH = 800
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chore Board")
clock = pygame.time.Clock()

#Colors
BG = (10, 14, 10)
GREEN = (50, 255, 50)
DIM_GREEN = (20, 120, 20)
DARK_GREEN = (10, 60, 10)
AMBER = (255, 176, 0)
DIM_AMBER = (120, 84, 0)
BLACK = (0, 0, 0)

#Fonts
title_font = pygame.font.SysFont("courier", 40)
label_font = pygame.font.SysFont("courier", 22)
date_font = pygame.font.SysFont("courier", 20)
small_font = pygame.font.SysFont("courier", 16)

#Layout
title_y = 28
box_x = 50
box_size = 24
init_y = 150
spacing = 45

#Buttons
next_button_hitbox = pygame.Rect(735, 75, 35, 40)
prev_button_hitbox = pygame.Rect(30,75,35,40)
add_button_hitbox = pygame.Rect(750, 425, 30, 30)
add_back_button_hitbox = pygame.Rect(20, 20, 35, 40)
daily_button_hitbox = pygame.Rect(50, 200, 120, 40)
weekly_button_hitbox = pygame.Rect(190, 200, 120, 40)
once_button_hitbox = pygame.Rect(330, 200, 120, 40)
save_button_hitbox = pygame.Rect(750, 425, 30, 30)
edit_button_hitbox = pygame.Rect(20, 425, 30, 30)

#State
current_screen = "main"
selected_date = datetime.date.today()
chores = [
    {"name": "Take out trash", "type": "weekly", "days": [3]},
    {"name": "Fold laundry", "type": "weekly", "days": [5]},
    {"name": "Take husker to vet", "type": "once", "date": "2026-08-20"},
    {"name": "Write Paper", "type": "daily"},
]
checked = {}
recurrence_button_select = ""
input_text = ""
add_selected_days = []
edit_mode = False
add_once_date = datetime.date.today()
keyboard_visible = False

# Keyboard stuff 
key_rows = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM") + ["BACK"],
    ["SPACE"],
]
key_width = 55
key_height = 35
key_gap = 5
keyboard_y = 310

def get_key_rects():
    rects = {}
    for row_index, row in enumerate(key_rows):
        y = keyboard_y + row_index * (key_height + key_gap)
        if row == ["SPACE"]:
            total_width = 10 * key_width + 9 * key_gap
            x = (WIDTH - total_width) // 2
            rects["SPACE"] = pygame.Rect(x, y, total_width, key_height)
        else:
            total_width = len(row) * key_width + (len(row) - 1) * key_gap
            start_x = (WIDTH - total_width) // 2
            for key_index, key in enumerate(row):
                x = start_x + key_index * (key_width + key_gap)
                w = key_width
                if key == "BACK":
                    w = key_width + 20
                rects[key] = pygame.Rect(x, y, w, key_height)
    return rects

def draw_keyboard():
    rects = get_key_rects()
    for key, rect in rects.items():
        pygame.draw.rect(screen, DIM_GREEN, rect, 2)
        if key == "SPACE":
            label = small_font.render("SPACE", True, GREEN)
        elif key == "BACK":
            label = small_font.render("DEL", True, AMBER)
        else:
            label = small_font.render(key, True, GREEN)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

def handle_keyboard_tap(pos):
    global input_text
    rects = get_key_rects()
    for key, rect in rects.items():
        if rect.collidepoint(pos):
            if key == "BACK":
                input_text = input_text[:-1]
            elif key == "SPACE":
                input_text += " "
            else:
                input_text += key.lower()
            return True
    return False

# Scanline surface for CRT effect - **Written by Claude** 
scanline_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 3):
    pygame.draw.line(scanline_surface, (0, 0, 0, 30), (0, y), (WIDTH, y))

def draw_border():
    pygame.draw.rect(screen, DIM_GREEN, (4, 4, WIDTH - 8, HEIGHT - 8), 2)
    pygame.draw.rect(screen, DARK_GREEN, (8, 8, WIDTH - 16, HEIGHT - 16), 1)

def save_data():
    data = {
        "chores": chores,
        "checked": checked,
    }

    with open("data.json", "w") as f:
        json.dump(data, f)

def load_data():
    global chores
    global checked
    try:
        with open("data.json", "r") as f:
            chore_data = json.load(f)
        chores = chore_data["chores"]
        checked = chore_data["checked"]
    except:
        pass


def get_chores_for_date(date):
    result = []
    for chore in chores:
        if chore["type"] == "daily":
            result.append(chore)
        elif chore["type"] == "weekly":
            if date.weekday() in chore["days"]:
                result.append(chore)
        elif chore["type"] == "once":
            if str(date) == chore["date"]:
                result.append(chore)
    return result

def get_checked(date):
    date_key = str(date)
    if date_key not in checked:
        checked[date_key]= {}
    for chore in get_chores_for_date(date):
        chore_name = chore["name"]
        if chore_name not in checked[date_key]:
            checked[date_key][chore_name] = False
    return checked[date_key]


def draw_main_screen():
    global edit_mode
    screen.fill(BG)
    draw_border()

    # Title
    title_surface = title_font.render("CHORE BOARD", True, GREEN)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, title_y))
    screen.blit(title_surface, title_rect)

    # Line under title
    pygame.draw.line(screen, DIM_GREEN, (50, 52), (750, 52), 1)

    # Date
    time_string = selected_date.strftime("%A  %B %d  %Y").upper()
    date_surface = date_font.render(time_string, True, AMBER)
    date_rect = date_surface.get_rect(center=(WIDTH // 2, 85))
    screen.blit(date_surface, date_rect)

    # Navigation arrows
    pygame.draw.polygon(screen, GREEN, [(740, 75), (740, 100), (765, 87)])
    pygame.draw.polygon(screen, GREEN, [(60, 75), (60, 100), (35, 87)])

    # Separaton line
    pygame.draw.line(screen, DIM_GREEN, (50, 120), (750, 120), 1)

    # Add button
    pygame.draw.rect(screen, DIM_GREEN, (750, 425, 30, 30), 2)
    pygame.draw.line(screen, GREEN, (756, 440), (774, 440), 2)
    pygame.draw.line(screen, GREEN, (765, 431), (765, 449), 2)
    add_button_surface = small_font.render("ADD", True, GREEN)
    screen.blit(add_button_surface, (700, 430))

    # Chore list
    day_chores = get_chores_for_date(selected_date)
    day_checked = get_checked(selected_date)
    for i in range(len(day_chores)):
        box_y = init_y + (i * spacing)

        # Checkboxes
        if day_checked[day_chores[i]["name"]]:
            pygame.draw.rect(screen, GREEN, (box_x, box_y, box_size, box_size))
            pygame.draw.line(screen, BG, (box_x + 4, box_y + 12), (box_x + 9, box_y + 19), 3)
            pygame.draw.line(screen, BG, (box_x + 9, box_y + 19), (box_x + 20, box_y + 4), 3)
            # Dim for checked chores
            label_surface = label_font.render(day_chores[i]["name"], True, DIM_GREEN)
        else:
            pygame.draw.rect(screen, DIM_GREEN, (box_x, box_y, box_size, box_size), 2)
            label_surface = label_font.render(day_chores[i]["name"], True, GREEN)

        screen.blit(label_surface, (box_x + box_size + 15, box_y + 5))

        # Edit mode X buttons
        if edit_mode:
            x_pos = box_x + box_size + 15 + label_surface.get_width() + 15
            pygame.draw.line(screen, AMBER, (x_pos + 3, box_y + 3), (x_pos + 19, box_y + 19), 3)
            pygame.draw.line(screen, AMBER, (x_pos + 19, box_y + 3), (x_pos + 3, box_y + 19), 3)

    # Edit Button
        pygame.draw.rect(screen, DIM_GREEN, (20, 425, 30, 30), 2)
        pygame.draw.line(screen, AMBER if edit_mode else GREEN, (26, 440), (44, 440), 2)
        edit_label_surface = small_font.render("EDIT", True, AMBER if edit_mode else GREEN)
        screen.blit(edit_label_surface, (55, 430))

    # Scanline overlay
    screen.blit(scanline_surface, (0, 0))

def draw_add_screen():
    global add_selected_days
    screen.fill(BG)
    draw_border()

    # Title
    title_surface = title_font.render("NEW CHORE", True, GREEN)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, title_y))
    screen.blit(title_surface, title_rect)

    # Line under title
    pygame.draw.line(screen, DIM_GREEN, (50, 52), (750, 52), 1)

    # Back button
    pygame.draw.polygon(screen, GREEN, [(50, 25), (50, 50), (25, 37)])
    back_label = small_font.render("BACK", True, GREEN)
    screen.blit(back_label, (60, 30))

    # Input field label
    input_label_surface = small_font.render("CHORE NAME:", True, DIM_GREEN)
    screen.blit(input_label_surface, (50, 85))

    # Input box
    pygame.draw.rect(screen, DIM_GREEN, (50, 110, 500, 40), 2)
    # Blinking line for add box
    cursor = "_" if pygame.time.get_ticks() % 1000 < 500 else ""
    input_surface = label_font.render(input_text + cursor, True, GREEN)
    screen.blit(input_surface, (58, 120))

    # Recurrence label
    recurrence_label = small_font.render("RECURRENCE:", True, DIM_GREEN)
    screen.blit(recurrence_label, (50, 170))

    # Daily button
    daily_label_rect = label_font.render("DAILY", True, GREEN).get_rect(center=(110, 220))
    if recurrence_button_select == "daily":
        pygame.draw.rect(screen, GREEN, (50, 200, 120, 40))
        daily_label = label_font.render("DAILY", True, BG)
    else:
        pygame.draw.rect(screen, DIM_GREEN, (50, 200, 120, 40), 2)
        daily_label = label_font.render("DAILY", True, GREEN)
    screen.blit(daily_label, daily_label_rect)

    # Weekly button
    weekly_label_rect = label_font.render("WEEKLY", True, GREEN).get_rect(center=(250, 220))
    if recurrence_button_select == "weekly":
        pygame.draw.rect(screen, GREEN, (190, 200, 120, 40))
        weekly_label = label_font.render("WEEKLY", True, BG)
    else:
        pygame.draw.rect(screen, DIM_GREEN, (190, 200, 120, 40), 2)
        weekly_label = label_font.render("WEEKLY", True, GREEN)
    screen.blit(weekly_label, weekly_label_rect)

    # Day select
    if recurrence_button_select == "weekly":
        day_labels = ["M", "T", "W", "R", "F", "S", "U"]
        day_full = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for day in range(len(day_labels)):
            day_box_x = 50 + (day * 100)
            day_box_y = 260
            if day in add_selected_days:
                pygame.draw.rect(screen, AMBER, (day_box_x, day_box_y, 28, 28))
                day_label = small_font.render(day_labels[day], True, BG)
            else:
                pygame.draw.rect(screen, DIM_GREEN, (day_box_x, day_box_y, 28, 28), 2)
                day_label = small_font.render(day_labels[day], True, GREEN)
            screen.blit(day_label, (day_box_x + 34, day_box_y + 8))

    # Once button
    once_label_rect = label_font.render("ONCE", True, GREEN).get_rect(center=(390, 220))
    if recurrence_button_select == "once":
        pygame.draw.rect(screen, GREEN, (330, 200, 120, 40))
        once_label = label_font.render("ONCE", True, BG)
    else:
        pygame.draw.rect(screen, DIM_GREEN, (330, 200, 120, 40), 2)
        once_label = label_font.render("ONCE", True, GREEN)
    screen.blit(once_label, once_label_rect)

    # Date picker select
    if recurrence_button_select == "once":
        once_date_surface = date_font.render(add_once_date.strftime("%b %d %Y").upper(), True, AMBER)
        once_date_rect = once_date_surface.get_rect(center=(390, 262))
        screen.blit(once_date_surface, once_date_rect)
        pygame.draw.polygon(screen, GREEN, [(once_date_rect.left - 25, 255), (once_date_rect.left - 25, 270), (once_date_rect.left - 40, 262)])
        pygame.draw.polygon(screen, GREEN, [(once_date_rect.right + 25, 255), (once_date_rect.right + 25, 270), (once_date_rect.right + 40, 262)])

    # Save button
    pygame.draw.rect(screen, DIM_GREEN, (750, 425, 30, 30), 2)
    pygame.draw.line(screen, GREEN, (755, 440), (762, 447), 3)
    pygame.draw.line(screen, GREEN, (762, 447), (775, 433), 3)
    save_label = small_font.render("SAVE", True, GREEN)
    screen.blit(save_label, (693, 430))

    if keyboard_visible:
        draw_keyboard()

    # Scanline overlay
    screen.blit(scanline_surface, (0, 0))


def handle_events(event):
    global current_screen
    global running
    global selected_date
    global input_text
    global recurrence_button_select
    global add_selected_days
    global edit_mode
    global add_once_date
    global keyboard_visible
    if event.type == pygame.QUIT:
                running = False

    if current_screen == "main":

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Builds daily chore dict and hitboxes 
            day_chores = get_chores_for_date(selected_date)
            day_checked = get_checked(selected_date)
            for i in range(len(day_chores)):
                box_y = init_y + (i * spacing)

                if(mouse_x > box_x and mouse_x < box_x + box_size and
                mouse_y > box_y and mouse_y < box_y + box_size):
                    chore_name = day_chores[i]["name"]
                    day_checked[chore_name] = not day_checked[chore_name]
            # Change day on chore screen
            if(next_button_hitbox.collidepoint(event.pos)):
                selected_date = selected_date + datetime.timedelta(days=1)
            if(prev_button_hitbox.collidepoint(event.pos)):
                selected_date = selected_date + datetime.timedelta(days=-1)
            # Move to add screen
            if(add_button_hitbox.collidepoint(event.pos)):
                current_screen = "add"
            if(edit_button_hitbox.collidepoint(event.pos)):
                edit_mode = not edit_mode

            # X hitboxes in edit mode 
            if edit_mode:
                for i in range(len(day_chores)):
                    box_y = init_y + (i * spacing)
                    label_surface = label_font.render(day_chores[i]["name"], True, GREEN)
                    x_pos = box_x + box_size + 15 + label_surface.get_width() + 15
                    x_hitbox = pygame.Rect(x_pos, box_y, 24, 24)
                    if x_hitbox.collidepoint(event.pos):
                        chores.remove(day_chores[i])
                        break

    elif current_screen == "add":
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos


            # Toggle keyboard when input box is tapped
            input_box_rect = pygame.Rect(50, 110, 500, 40)
            if input_box_rect.collidepoint(event.pos):
                keyboard_visible = not keyboard_visible

            if keyboard_visible:
                handle_keyboard_tap(event.pos)

            # If Back button is clicked 
            if(add_back_button_hitbox.collidepoint(event.pos)):
                current_screen = "main"
                recurrence_button_select = ""
                input_text = ""
                add_once_date = datetime.date.today()

            # Recurrence button select
            if(once_button_hitbox.collidepoint(event.pos)):
               recurrence_button_select = "once"
            if(daily_button_hitbox.collidepoint(event.pos)):
                recurrence_button_select = "daily"
            if(weekly_button_hitbox.collidepoint(event.pos)):
                recurrence_button_select = "weekly"

            # Hitboxes for weekly day select
            day_labels = ["M", "T", "W", "R", "F", "S", "U"]
            for day in (range(len(day_labels))):
                day_box_x = 50 + (day * 100)
                day_select_hitbox_rect = pygame.Rect(day_box_x, 260, 28, 28)
                if (day_select_hitbox_rect.collidepoint(event.pos)):
                    if day in add_selected_days:
                        add_selected_days.remove(day)
                    else:
                        add_selected_days.append(day)

            # Save button 
            if(save_button_hitbox.collidepoint(event.pos)):
                if input_text == "" or recurrence_button_select == "":
                    pass
                else:
                    if(recurrence_button_select == "daily"):
                        new_chore = {"name": input_text, "type": "daily"}
                        chores.append(new_chore)
                    if(recurrence_button_select == "weekly"):
                        new_chore = {"name": input_text, "type": "weekly", "days": add_selected_days}
                        chores.append(new_chore)
                    if(recurrence_button_select == "once"):
                        new_chore = {"name": input_text, "type": "once", "date": str(add_once_date)}
                        chores.append(new_chore)
                    save_data()
                    input_text, recurrence_button_select, add_selected_days = "", "", []
                    add_once_date = datetime.date.today()
                    keyboard_visible = False
                    current_screen = "main"

            #Once date select moving hitboxes based on width of date text 
            once_date_surface = date_font.render(add_once_date.strftime("%b %d %Y").upper(), True, AMBER)
            once_date_rect = once_date_surface.get_rect(center=(390, 262))
            once_date_prev_hitbox = pygame.Rect(once_date_rect.left - 45, 250, 25, 25)
            once_date_next_hitbox = pygame.Rect(once_date_rect.right + 20, 250, 25, 25)
            if(once_date_prev_hitbox.collidepoint(event.pos)):
                add_once_date = add_once_date - datetime.timedelta(days=1)
            if(once_date_next_hitbox.collidepoint(event.pos)):
                add_once_date = add_once_date + datetime.timedelta(days=1)

        # Text input handling 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode



load_data()
running = True
while running:
    for event in pygame.event.get():
       handle_events(event)
    if current_screen == "main":
        draw_main_screen()
    elif current_screen == "add":
        draw_add_screen()
    pygame.display.flip()
    clock.tick(30)

save_data()
pygame.quit()
