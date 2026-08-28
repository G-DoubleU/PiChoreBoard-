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
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0,0,255)

#Fonts
title_font = pygame.font.SysFont("arial", 50)
label_font = pygame.font.SysFont("arial", 28)
date_font = pygame.font.SysFont("arial", 28)

#Layout
title_y = 20
box_x = 50
box_size = 30
init_y = 150
spacing = 50

#Buttons
next_button_hitbox = pygame.Rect(735, 75, 35, 40)
prev_button_hitbox = pygame.Rect(30,75,35,40)
add_button_hitbox = pygame.Rect(750, 425, 30, 30)
add_back_button_hitbox = pygame.Rect(20, 20, 35, 40)
daily_button_hitbox = pygame.Rect(50, 160, 120, 40)
weekly_button_hitbox = pygame.Rect(190, 160, 120, 40)
once_button_hitbox = pygame.Rect(330, 160, 120, 40)
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
            chore_data = json.load( f)
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
    # Fill screen and draw title
    title_surface = title_font.render("Chore Board", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, title_y))
    screen.fill(BLACK)
    screen.blit(title_surface, title_rect)
    
    #Draw date 
    time_string = selected_date.strftime("%A, %B %d %Y")
    date_surface = date_font.render(time_string, True, WHITE)
    date_rect = date_surface.get_rect(center=(WIDTH // 2, 95))
    screen.blit(date_surface, date_rect)

    #Draw add button
    pygame.draw.rect(screen, WHITE, (750, 425, 30, 30), 2)
    pygame.draw.line(screen, WHITE, (756, 440), (774, 440), 2)  
    pygame.draw.line(screen, WHITE, (765, 431), (765, 449), 2)  
    add_button_surface = label_font.render("Add", True, WHITE)
    screen.blit(add_button_surface, (690, 425))
    
    #Next and prev buttons
    pygame.draw.polygon(screen, WHITE, [(740, 80), (740, 110), (765, 95)])
    pygame.draw.polygon(screen, WHITE, [(60, 80), (60, 110), (35,95)])
    
    
    #Draws the boxes and evaluate checks
    day_chores = get_chores_for_date(selected_date)
    day_checked = get_checked(selected_date)
    for i in range(len(day_chores)):
        box_y = init_y + (i * spacing)
    
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_size, box_size), 2)

        if day_checked[day_chores[i]["name"]]:
            pygame.draw.line(screen, WHITE, (box_x + 5, box_y + 15), (box_x + 12, box_y +25), 3)
            pygame.draw.line(screen, WHITE, (box_x + 12, box_y +25), (box_x + 25, box_y + 5),3 )
    
        label_surface = label_font.render(day_chores[i]["name"], True, WHITE)
        screen.blit(label_surface, (box_x + box_size + 10, box_y))
        if edit_mode:
            x_pos = box_x + box_size + 10 + label_surface.get_width() + 15
            pygame.draw.line(screen, WHITE, (x_pos + 5, box_y + 5), (x_pos + 25, box_y + 25), 3)
            pygame.draw.line(screen, WHITE, (x_pos + 25, box_y + 5), (x_pos + 5, box_y + 25), 3)

    #Edit Button
        pygame.draw.rect(screen, WHITE, (20, 425, 30, 30), 2)
        pygame.draw.line(screen, WHITE, (26, 440), (44, 440), 2)
        edit_button_surface = label_font.render("Edit", True, WHITE)
        screen.blit(edit_button_surface, (55, 425))

def draw_add_screen():
    global add_selected_days
    #Title and back button
    title_surface = title_font.render("Add Screen", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, title_y))
    screen.fill(BLACK)
    screen.blit(title_surface, title_rect)
    back_label = label_font.render("Back", True, WHITE)
    screen.blit(back_label, (60, 22))
    pygame.draw.polygon(screen, WHITE, [(50, 25), (50, 55), (25, 40)])

    #Input box and label 
    pygame.draw.rect(screen,WHITE, (50,100,400,40), 2)
    input_surface = label_font.render(input_text, True, WHITE)
    screen.blit(input_surface, (55, 105))
    input_label_surface = label_font.render("Chore Name", True, WHITE)
    screen.blit(input_label_surface, (460, 105))

    #Recurrence boxes and label
    # Daily
    daily_label = label_font.render("Daily", True, WHITE)
    daily_label_rect = daily_label.get_rect(center=(110, 180))
    if(recurrence_button_select != "daily"):
        pygame.draw.rect(screen, WHITE, (50, 160, 120, 40), 2)   # Daily
        screen.blit(daily_label,daily_label_rect)
    elif(recurrence_button_select == "daily"):
        pygame.draw.rect(screen, WHITE, (50, 160, 120, 40))
        daily_label = label_font.render("Daily", True, BLACK)
        screen.blit(daily_label, daily_label_rect)

    #Weekly
    weekly_label = label_font.render("Weekly", True, WHITE)
    weekly_label_rect = weekly_label.get_rect(center=(250,180))
    if (recurrence_button_select != "weekly"):
        pygame.draw.rect(screen, WHITE, (190, 160, 120, 40), 2)  # Weekly
        screen.blit(weekly_label, weekly_label_rect)

    elif(recurrence_button_select == "weekly"):
        pygame.draw.rect(screen, WHITE, (190, 160, 120, 40))  # Once
        weekly_label = label_font.render("Weekly", True, BLACK)
        screen.blit(weekly_label,weekly_label_rect)

        day_labels = ["M", "T", "W", "Thu", "F", "S", "Sun"]
        for day in range(len(day_labels)):
            day_box_x = 50 + (day * 100)
            day_box_y = 220
            if(day not in add_selected_days):
                pygame.draw.rect(screen, WHITE, (day_box_x, day_box_y, 30, 30), 2)
                day_label = label_font.render(day_labels[day], True, WHITE)
                screen.blit(day_label, (day_box_x + 35, day_box_y + 2))
            else:
                pygame.draw.rect(screen, WHITE, (day_box_x, day_box_y, 30,30))
                day_label = label_font.render(day_labels[day], True, WHITE)

            screen.blit(day_label, (day_box_x + 35, day_box_y + 2))

    #Save Button
    pygame.draw.rect(screen, WHITE, (750, 425, 30, 30), 2)
    pygame.draw.line(screen, WHITE, (755, 440), (762, 447), 3)
    pygame.draw.line(screen, WHITE, (762, 447), (775, 433), 3)
    save_button_label = label_font.render("Save", True, WHITE)
    screen.blit(save_button_label, (690, 425))





    #Once
    once_label = label_font.render("Once", True, WHITE)
    once_label_rect = once_label.get_rect(center=(390,180))
    if(recurrence_button_select != "once"):
        pygame.draw.rect(screen,WHITE,(330, 160, 120, 40),2)
        screen.blit(once_label,once_label_rect)
    if(recurrence_button_select == "once"):
        pygame.draw.rect(screen, WHITE, (330, 160, 120, 40))
        once_label = label_font.render("Once", True, BLACK)
        screen.blit(once_label,once_label_rect)


def handle_events(event):
    global current_screen
    global running
    global selected_date
    global input_text
    global recurrence_button_select
    global add_selected_days
    global edit_mode
    if event.type == pygame.QUIT:
                
                running = False
    
    if current_screen == "main":
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            day_chores = get_chores_for_date(selected_date)
            day_checked = get_checked(selected_date)
            for i in range(len(day_chores)):
                box_y = init_y + (i * spacing)
    
                #should be able to re-write this with collidepoint()                
                if(mouse_x > box_x and mouse_x < box_x + box_size and
                mouse_y > box_y and mouse_y < box_y + box_size):
                    chore_name = day_chores[i]["name"]
                    day_checked[chore_name] = not day_checked[chore_name]
    
            if(next_button_hitbox.collidepoint(event.pos)):
                selected_date = selected_date + datetime.timedelta(days=1)
            if(prev_button_hitbox.collidepoint(event.pos)):
                selected_date = selected_date + datetime.timedelta(days=-1)

            if(add_button_hitbox.collidepoint(event.pos)):
                current_screen = "add"
            if(edit_button_hitbox.collidepoint(event.pos)):
                edit_mode = not edit_mode 

            #If Edit mode True  
            if edit_mode:
                for i in range(len(day_chores)):
                    box_y = init_y + (i * spacing)
                    label_surface = label_font.render(day_chores[i]["name"], True, WHITE)
                    x_pos = box_x + box_size + 10 + label_surface.get_width() + 15
                    x_hitbox = pygame.Rect(x_pos, box_y, 30, 30)
                    if x_hitbox.collidepoint(event.pos):
                        chores.remove(day_chores[i])
                        break

    elif current_screen == "add":
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos      
            if(add_back_button_hitbox.collidepoint(event.pos)):
                current_screen = "main"
                recurrence_button_select = ""
                input_text = ""
            if(once_button_hitbox.collidepoint(event.pos)):
               recurrence_button_select = "once"
            if(daily_button_hitbox.collidepoint(event.pos)):
                recurrence_button_select = "daily"
            if(weekly_button_hitbox.collidepoint(event.pos)):
                recurrence_button_select = "weekly"

            day_labels = ["M", "T", "W", "Thu", "F", "S", "Sun"]
            for day in (range(len(day_labels))):
                day_box_x = 50 + (day * 100)
                day_select_hitbox_rect = pygame.Rect(day_box_x, 220, 30, 30)
                if (day_select_hitbox_rect.collidepoint(event.pos)):
                    if day in add_selected_days:
                        add_selected_days.remove(day)
                    else:
                        add_selected_days.append(day)
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
                        new_chore = {"name": input_text, "type": "once", "date": str(selected_date)}
                        chores.append(new_chore)
                    save_data()
                    input_text, recurrence_button_select, add_selected_days = "", "", []
                    current_screen = "main"

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
    clock.tick(10)

save_data()
pygame.quit()