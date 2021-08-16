import pygame, sys, pymunk, matplotlib, random, time
import matplotlib.colors as colors
from matplotlib.ticker import FormatStrFormatter

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

class Plot(pygame.sprite.DirtySprite):  # our DirtySprite class

    def __init__(self, center):


        pygame.sprite.DirtySprite.__init__(self) # always need to have this call to super constructor
        self.image = pygame.image.load("null.png")
        self.rect = self.image.get_rect(center=center)  # rect controls target place when copied to screen

    def update(self, surface):  # make changes for this time tick
        surface.convert_alpha()
        self.image = surface
        self.dirty = 1  # force redraw from image, since we moved the sprite rect

    def update0(self):  # make changes for this time tick
        self.dirty = 1  # force redraw from image, since we moved the sprite rect

def coefficient_tireroad(roadtype_choose, tiretype_choose):
    coef = 0
    if roadtype_choose == 1:
        if tiretype_choose == 1:
            coef = 0.015
        elif tiretype_choose == 2:
            coef = 0.011
        elif tiretype_choose == 3:
            coef = 0.02
        else:
            print('ERROR: coefficient_tireroad()')
    elif roadtype_choose == 2:
        if tiretype_choose == 1:
            coef = 0.08
        elif tiretype_choose == 2:
            coef = 0.06
        elif tiretype_choose == 3:
            coef = 0.04
        else:
            print('ERROR: coefficient_tireroad()')
    elif roadtype_choose == 3:
        if tiretype_choose == 1:
            coef = 0.3
        elif tiretype_choose == 2:
            coef = 0.25
        elif tiretype_choose == 3:
            coef = 0.2
        else:
            print('ERROR: coefficient_tireroad()')
    else:
        print('ERROR: coefficient_tireroad()')
    return coef
def coefficient_brake(braketype_choose):
    if braketype_choose == 1:
        return 0.3
    elif braketype_choose == 2:
        return  0.4
    elif braketype_choose == 3:
        return 0.5
    else:
        print('ERROR: coefficient_brake()')

def brake_deceleration(coef_tireroad, coef_brake):
    # mass 1600kg, g 9.8m/s^2
    m = 1600
    g = 9.8
    mg = m * g
    f_tireroad = mg * coef_tireroad
    # force on brake 5000N
    f_brake = 5000 * coef_brake
    f_total = f_brake + f_tireroad
    # dec(m/s^2)
    dec = f_total / m
    return dec

def get_distance(dec_real, time_real):
    # v0(m/s) x(m)
    v0 = 16.67
    time_real = round(time_real, 4)
    time_real2 = round(time_real * time_real, 4)
    x = v0 * time_real + (-dec_real * time_real2)/2
    return x

def get_real_velocity(time, dec_real):
    # real velocity(km/h) 16.7m/s = 60.12km/h
    v0 = 16.7
    v_m = v0 - dec_real * time
    v_km = 3.6 * v_m
    return v_km

def realvel_to_realdec(vel_real):
    c2 = -0.005
    c1 = 0.15
    c0 = 0.5
    return c2 * (vel_real ** 2) + c1 * vel_real + c0

def get_python_deceleration(dec_real):
    #dec real(m/s^2)
    x = dec_real
    m = -0.01382
    k = 1.00545
    return m * x + k

def plot(ax, canvas,vel_real, python_time, title, xlabel, ylabel):
    time = python_time
    ax.yaxis.set_major_formatter(FormatStrFormatter('%g'))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1F'))
    ax.plot(time, vel_real, 'o', markerfacecolor='none', markeredgecolor='k', alpha=0.5, markersize=4)
    ax.set_aspect(1./ax.get_data_ratio())
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    return pygame.image.fromstring(raw_data, size, "RGB")

def plotsetup():
    fig = plt.figure(figsize=[4.5, 4.5], dpi = 95)
    plt.gcf().subplots_adjust(left = 0.3, bottom=0.4)
    ax = fig.add_subplot(111)
    canvas = agg.FigureCanvasAgg(fig)
    return fig, ax, canvas

class Car(pygame.sprite.DirtySprite):  # our DirtySprite class

    def __init__(self, center,space, v0_python):
        pygame.sprite.DirtySprite.__init__(self) # always need to have this call to super constructor
        surf = pygame.image.load("baby-car.png")
        surf.convert_alpha()
        self.image = surf
        self.rect = self.image.get_rect(center=center)  # rect controls target place when copied to screen
        mass = 1
        radius = 50
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.v0_python = v0_python
        self.body = pymunk.Body(mass, moment)
        self.body.velocity = (v0_python, 0)
        self.body.position = center
        self.shape = pymunk.Circle(self.body, radius)
        self.space = space
        self.space.add(self.body, self.shape)

    def update(self, dec_python):  # make changes for this time tick
        self.body.update_velocity(body=self.body, gravity=(0, 0), damping = dec_python, dt=1)
        new_x = int(self.body.position.x)
        new_y = int(self.body.position.y)
        self.rect.center = (new_x, new_y)  # changes where sprite will be copied to buffer
        self.dirty = 1  # force redraw from image, since we moved the sprite rect
        self.vel_python = self.body.velocity[0]

    def update0(self):  # make changes for this time tick
        self.body.velocity = (0, 0)
        self.body.update_velocity(body=self.body, gravity=(0, 0), damping=0.95, dt=1)
        new_x = int(self.body.position.x)
        new_y = int(self.body.position.y)
        self.rect.center = (new_x, new_y)  # changes where sprite will be copied to buffer
        self.dirty = 1  # force redraw from image, since we moved the sprite rect
        self.vel_python = self.body.velocity[0]

def text(surface, fontFace, size, x, y, text, colour):
    fonts = {}
    if size in fonts:
        font = fonts[size]
    else:
        font = pygame.font.Font(fontFace, size)
        fonts[size] = font
    text = font.render(text, True, colour)
    surface.blit(text, (x, y))

def button(screen, fontface, text_display, button_x, button_y, button_width, button_height, textsize, text_x):
    pygame.draw.rect(screen, (100, 100, 100), [button_x, button_y, button_width, button_height])
    # superimposing the text onto our button
    text(screen, fontface, textsize, text_x, button_y, text_display, (255, 255, 255))

class Select():

    def __init__(self, screen, font, x_pos, y_pos, title, text1, text2, text3):
        self.x_pos = x_pos
        self.screen = screen
        self.width = 23
        self.y_pos1 = y_pos
        self.y_pos2 = y_pos + 50
        self.y_pos3 = y_pos + 100
        self.text1 = text1
        self.text2 = text2
        self.text3 = text3
        self.title = title
        self.font = font

    def update(self, choose):
        if choose == 1:
            pygame.draw.rect(self.screen, (100, 100, 100), [self.x_pos, self.y_pos1, self.width, self.width])
            pygame.draw.rect(self.screen, (100, 100, 100), [self.x_pos, self.y_pos2, self.width, self.width], 2)
            pygame.draw.rect(self.screen, (100, 100, 100), [self.x_pos, self.y_pos3, self.width, self.width], 2)
            # label
            text(self.screen, self.font, 30, self.x_pos, 90, self.title, (100, 100, 100))
            # check box text display
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos1, self.text1, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos2, self.text2, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos3, self.text3, (100, 100, 100))
        elif choose == 2:
            pygame.draw.rect(self.screen, (100, 100, 100),
                             [self.x_pos, self.y_pos1, self.width, self.width], 2)
            pygame.draw.rect(self.screen, (100, 100, 100), [self.x_pos, self.y_pos2, self.width, self.width])
            pygame.draw.rect(self.screen, (100, 100, 100), [self.x_pos, self.y_pos3, self.width, self.width], 2)

            # label
            text(self.screen, self.font, 30, self.x_pos, 90, self.title, (100, 100, 100))
            # check box text display
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos1, self.text1, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos2, self.text2, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos3, self.text3, (100, 100, 100))
        elif choose == 3:
            pygame.draw.rect(self.screen, (100, 100, 100),[self.x_pos, self.y_pos1, self.width, self.width], 2)
            pygame.draw.rect(self.screen, (100, 100, 100), [self.x_pos, self.y_pos2, self.width, self.width], 2)
            pygame.draw.rect(self.screen, (100, 100, 100), [self.x_pos, self.y_pos3, self.width, self.width])

            # label
            text(self.screen, self.font, 30, self.x_pos, 90, self.title, (100, 100, 100))
            # check box text display
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos1, self.text1, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos2, self.text2, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos3, self.text3, (100, 100, 100))
        else:
            pygame.draw.rect(self.screen, (100, 100, 100),[self.x_pos, self.y_pos1, self.width, self.width], 2)
            pygame.draw.rect(self.screen, (100, 100, 100),[self.x_pos, self.y_pos2, self.width, self.width], 2)
            pygame.draw.rect(self.screen, (100, 100, 100),[self.x_pos, self.y_pos3, self.width, self.width], 2)

            # label
            text(self.screen, self.font, 30, self.x_pos, 90, self.title, (100, 100, 100))
            # check box text display
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos1, self.text1, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos2, self.text2, (100, 100, 100))
            text(self.screen, self.font, 23, self.x_pos + 42, self.y_pos3, self.text3, (100, 100, 100))





def main():

    # Matrix for Plot
    # [[t], [v]]
    time_result = []
    vel_result = []
    time_result.append(0)
    vel_result.append(60.12)


    # Boolean setup
    carstop = False
    plotstop = True
    start = False
    end = False
    menu = True
    restart = False
    restart_button = False

    # General setup
    v0_python = 500
    v0_real = 16.67 #m/s
    counter = 1
    plot_n = 0
    vel_python = v0_python

    pygame.init()  # initiating pygame
    screen = pygame.display.set_mode((1200, 800))  # Create the display surface
    clock = pygame.time.Clock()  # creating game clock

    # Physics setup
    space = pymunk.Space()  # creating physics space

    # Text setup
    font_corbel = '/Library/Fonts/Microsoft/Corbel.ttf'

    # Plot setup
    fig, ax, canvas = plotsetup()
    fig_a, ax_a, canvas_a = plotsetup()
    fig_x, ax_x, canvas_x = plotsetup()





    # Dirty Sprite
    # Create The Background used to restore sprite previous location
    p = Plot((550, 300))  # add face 1 100 down and to right from center 10 -5 is movement
    p_a = Plot((910, 300))
    p_x = Plot((220,300))
    car1 = Car((50,500), space, v0_python)

    my_sprites = pygame.sprite.LayeredDirty()  # holds sprites to be drawn
    my_sprites.add(p, p_a, p_x, car1)  # add both to our group



    # Main Menu

    select_y = 150

    roadtype_choose = 4
    roadtype_sel_x = 80
    roadtype_sel = Select(screen, font_corbel, roadtype_sel_x, select_y, 'Road Type', 'Concrete', 'Medium Hard Soil', 'Sand')
    tiretype_choose = 4
    tiretype_sel_x = 300
    tiretype_sel = Select(screen, font_corbel, tiretype_sel_x, select_y, 'Tire Type', 'Passenger Car', 'Truck', 'Tractor')

    braketype_choose = 4
    braketype_sel_x = 500
    braketype_sel = Select(screen, font_corbel, braketype_sel_x, select_y, 'Brake Pads Type', 'EE', 'FF',
                          'GG')


    while not end:  # game loop
        button_width = 90
        button_height = 30
        quit_button_x = 1050
        quit_button_y = 250
        restart_button_x = 1050
        restart_button_y = 200
        start_button_x = 900
        start_button_y = 250


        for event in pygame.event.get():  # check for user input
            if event.type == pygame.QUIT:  # input to close the game
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                # if the mouse is clicked on the button the game is terminated
                if quit_button_x <= mouse[0] <= quit_button_x + button_width and quit_button_y <= mouse[
                    1] <= quit_button_y + button_height:
                    pygame.quit()
                    sys.exit()
                elif start_button_x <= mouse[0] <= start_button_x + button_width and start_button_y <= mouse[
                    1] <= start_button_y + button_height and (braketype_choose != 4) and (tiretype_choose != 4) \
                        and (roadtype_choose != 4) and start == False:
                    start = True
                    menu = False
                    car1.body.velocity = (500, 0)
                    t0 = time.time()
                elif restart_button_x <= mouse[0] <= restart_button_x + button_width and restart_button_y <= mouse[
                    1] <= restart_button_y + button_height and restart_button:
                    restart = True
                    start = False

                elif roadtype_sel_x <= mouse[0] <= roadtype_sel_x + size_checkbox and (select_y <= mouse[
                    1] <= select_y + size_checkbox or select_y + 50 <= mouse[
                    1] <= select_y + 50 + size_checkbox or select_y + 100 <= mouse[
                    1] <= select_y + 100 + size_checkbox):
                    if select_y <= mouse[1] <= select_y + size_checkbox:
                        roadtype_choose = 1
                        roadtype_sel.update(roadtype_choose)
                    elif select_y + 50 <= mouse[1] <= select_y + 50 + size_checkbox:
                        roadtype_choose = 2
                        roadtype_sel.update(roadtype_choose)
                    elif select_y + 100 <= mouse[1] <= select_y + 100 + size_checkbox:
                        roadtype_choose = 3
                        roadtype_sel.update(roadtype_choose)
                    else:
                        roadtype_sel.update(roadtype_choose)
                elif tiretype_sel_x <= mouse[0] <= tiretype_sel_x + size_checkbox and (select_y <= mouse[
                    1] <= select_y + size_checkbox or select_y + 50 <= mouse[
                    1] <= select_y + 50 + size_checkbox or select_y + 100 <= mouse[
                    1] <= select_y + 100 + size_checkbox):
                    if select_y <= mouse[1] <= select_y + size_checkbox:
                        tiretype_choose = 1
                        tiretype_sel.update(tiretype_choose)
                    elif select_y + 50 <= mouse[1] <= select_y + 50 + size_checkbox:
                        tiretype_choose = 2
                        tiretype_sel.update(tiretype_choose)
                    elif select_y + 100 <= mouse[1] <= select_y + 100 + size_checkbox:
                        tiretype_choose = 3
                        tiretype_sel.update(tiretype_choose)
                    else:
                        tiretype_sel.update(tiretype_choose)
                elif braketype_sel_x <= mouse[0] <= braketype_sel_x + size_checkbox and (select_y <= mouse[
                    1] <= select_y + size_checkbox or select_y + 50 <= mouse[
                    1] <= select_y + 50 + size_checkbox or select_y + 100 <= mouse[
                    1] <= select_y + 100 + size_checkbox):
                    if select_y <= mouse[1] <= select_y + size_checkbox:
                        braketype_choose = 1
                        tiretype_sel.update(braketype_choose)
                    elif select_y + 50 <= mouse[1] <= select_y + 50 + size_checkbox:
                        braketype_choose = 2
                        braketype_sel.update(braketype_choose)
                    elif select_y + 100 <= mouse[1] <= select_y + 100 + size_checkbox:
                        braketype_choose = 3
                        braketype_sel.update(braketype_choose)
                    else:
                        tiretype_sel.update(tiretype_choose)



        if start:

            t = time.time()

            dec_real = brake_deceleration(coefficient_tireroad(roadtype_choose, tiretype_choose), coefficient_brake(braketype_choose))
            vel_real = get_real_velocity(t - t0, dec_real)
            dec_python = get_python_deceleration(dec_real)

            ####

            screen.fill((255, 255, 255))  # background color


            button(screen, font_corbel, 'Quit', quit_button_x, quit_button_y, button_width, button_height, 25, quit_button_x + 18)




            if vel_real < 0 and carstop == False:
                carstop = True
                plotstop = False

            if not carstop:
                time_result.append(t-t0)
                vel_result.append(vel_real)
                counter += 1
                car1.update(dec_python)
                text(screen, font_corbel, 30, 70, 150, 'Deceleration: ', (100, 100, 100))
                text(screen, font_corbel, 30, 250, 150, str(round(dec_real,2)), (100, 100, 100))
                text(screen, font_corbel, 25, 310, 155, 'm/s^2', (100, 100, 100))
                text(screen, font_corbel, 30, 410, 150, 'Velocity: ', (100, 100, 100))
                text(screen, font_corbel, 30, 530, 150, str(round(vel_real, 1)), (100, 100, 100))
                text(screen, font_corbel, 25, 585, 155, 'km/h', (100, 100, 100))
                text(screen, font_corbel, 30, 680, 150, 'Distance: ', (100, 100, 100))
                text(screen, font_corbel, 30, 810, 150, str(round(get_distance(dec_real, t - t0),2)), (100, 100, 100))
                text(screen, font_corbel, 25, 895, 155, 'm', (100, 100, 100))
                text(screen, font_corbel, 30, 950, 150, 'Time: ', (100, 100, 100))
                text(screen, font_corbel, 30, 1030, 150, str(round(t - t0,2)), (100, 100, 100))
                text(screen, font_corbel, 25, 1099, 155, 's', (100, 100, 100))


            elif not plotstop:

                if plot_n < counter and time_result[plot_n] < v0_real / round(dec_real, 2):
                    if plot_n >= counter - 5 or time_result[plot_n] >= (v0_real / round(dec_real, 2)) - 0.5:
                        text(screen, font_corbel, 20, 1040, 80, 'Please press', (255, 100, 100))
                        text(screen, font_corbel, 20, 1040, 100, '"Restart" or "Quit"', (255, 100, 100))
                        button(screen, font_corbel, 'Restart', restart_button_x, restart_button_y, button_width, button_height, 20, restart_button_x + 10)

                    p.update(plot(ax, canvas, vel_result[plot_n], time_result[plot_n], 'V-T', 'Time(s)', 'Velocity(km/h)'))  # call update on all sprites
                    p_a.update(plot(ax_a, canvas_a, round(dec_real, 2), time_result[plot_n], 'A-T', 'Time(s)', 'Acceleration(m/s^2)'))
                    p_x.update(plot(ax_x, canvas_x, get_distance(dec_real, time_result[plot_n]), time_result[plot_n], 'X-T', 'Time(s)', 'Distance(m)'))
                else:
                    plotstop = True
                    restart_button = True

                plot_n += 5


            #vel_python = car1.vel_python
            # for each dirty sprint, erase previous rect with background copy
            # and then copy new sprite to buffer
            rects = my_sprites.draw(screen)

            space.step(1 / 50)  # space loop (Physics loop, pymunk)
            clock.tick(400)  # limiting the frames per second to 120
            pygame.display.update(rects)  # copy rects from buffer to screen
        elif restart:
            # Matrix for Plot
            # [[t], [v]]
            time_result = []
            vel_result = []
            time_result.append(0)
            vel_result.append(60.12)
            # General setup
            v0_python = 500

            # Boolean setup
            carstop = False
            plotstop = True
            start = False
            end = False
            menu = True

            pygame.init()  # initiating pygame
            screen = pygame.display.set_mode((1200, 800))  # Create the display surface
            clock = pygame.time.Clock()  # creating game clock

            # Physics setup
            space = pymunk.Space()  # creating physics space

            # Text setup
            font_corbel = '/Library/Fonts/Microsoft/Corbel.ttf'

            # Plot setup
            fig, ax, canvas = plotsetup()
            fig_a, ax_a, canvas_a = plotsetup()
            fig_x, ax_x, canvas_x = plotsetup()





            # Dirty Sprite
            # Create The Background used to restore sprite previous location
            p = Plot((550, 300))  # add face 1 100 down and to right from center 10 -5 is movement
            p_a = Plot((910, 300))
            p_x = Plot((220, 300))
            car1 = Car((50, 500), space, v0_python)

            my_sprites = pygame.sprite.LayeredDirty()  # holds sprites to be drawn
            my_sprites.add(p, p_a, p_x, car1)  # add both to our group

            select_y = 150

            roadtype_choose = 4
            roadtype_sel_x = 80
            roadtype_sel = Select(screen, font_corbel, roadtype_sel_x, select_y, 'Road Type', 'Concrete',
                                  'Medium Hard Soil', 'Sand')
            tiretype_choose = 4
            tiretype_sel_x = 300
            tiretype_sel = Select(screen, font_corbel, tiretype_sel_x, select_y, 'Tire Type', 'Passenger Car', 'Truck',
                                  'Tractor')

            braketype_choose = 4
            braketype_sel_x = 500
            braketype_sel = Select(screen, font_corbel, braketype_sel_x, select_y, 'Brake Pads Type', 'EE', 'FF',
                                   'GG')
            counter = 1
            plot_n = 0

            restart = False
        elif menu:
            screen.fill((255, 255, 255))  # background color

            if braketype_choose == 4:
                text(screen, font_corbel, 20, 700, 300, '_______ Brake Pads Friction of Coefficient: ', (100, 100, 100))
            else:
                if braketype_choose == 1:
                    text(screen, font_corbel, 20, 700, 300, 'EE Brake Pads Friction of Coefficient: 0.3',
                         (100, 100, 100))
                elif braketype_choose == 2:
                    text(screen, font_corbel, 20, 700, 300, 'FF Brake Pads Friction of Coefficient: 0.4',
                         (100, 100, 100))
                elif braketype_choose == 3:
                    text(screen, font_corbel, 20, 700, 300, 'GG Brake Pads Friction of Coefficient: 0.5',
                         (100, 100, 100))
                else:
                    print('ERROR: TextDisplay_coefficient_brake')


            if roadtype_choose == 4 or tiretype_choose == 4:
                text(screen, font_corbel, 20, 80, 300, '_______ Road & ________ Tire Friction of Coefficient: ', (100, 100, 100))
            else:
                if roadtype_choose == 1:
                    if tiretype_choose == 1:
                        text(screen, font_corbel, 20, 80, 300, 'Concrete Road & Passenger Car Tire Friction of Coefficient: 0.015',
                             (100, 100, 100))
                    elif tiretype_choose == 2:
                        text(screen, font_corbel, 20, 80, 300, 'Concrete Road & Truck Tire Friction of Coefficient: 0.011',
                             (100, 100, 100))
                    elif tiretype_choose == 3:
                        text(screen, font_corbel, 20, 80, 300, 'Concrete Road & Tractor Tire Friction of Coefficient: 0.02',
                             (100, 100, 100))
                    else:
                        print('ERROR: TextDisplay_coefficient_tireroad')
                elif roadtype_choose == 2:
                    if tiretype_choose == 1:
                        text(screen, font_corbel, 20, 80, 300, 'Medium Hard Soil Road & Passenger Car Tire Friction of Coefficient: 0.08',
                             (100, 100, 100))
                    elif tiretype_choose == 2:
                        text(screen, font_corbel, 20, 80, 300, 'Medium Hard Soil Road & Truck Tire Friction of Coefficient: 0.06',
                             (100, 100, 100))
                    elif tiretype_choose == 3:
                        text(screen, font_corbel, 20, 80, 300, 'Medium Hard Soil Road & Tractor Tire Friction of Coefficient: 0.04',
                             (100, 100, 100))
                    else:
                        print('ERROR: TextDisplay_coefficient_tireroad')
                elif roadtype_choose == 3:
                    if tiretype_choose == 1:
                        text(screen, font_corbel, 20, 80, 300, 'Sand Road & Passenger Car Tire Friction of Coefficient: 0.3',
                             (100, 100, 100))
                    elif tiretype_choose == 2:
                        text(screen, font_corbel, 20, 80, 300, 'Sand Road & Truck Tire Friction of Coefficient: 0.25',
                             (100, 100, 100))
                    elif tiretype_choose == 3:
                        text(screen, font_corbel, 20, 80, 300, 'Sand Road & Tractor Tire Friction of Coefficient: 0.2',
                             (100, 100, 100))
                    else:
                        print('ERROR: TextDisplay_coefficient_tireroad')
                else:
                    print('ERROR: TextDisplay_coefficient_tireroad')


            button(screen, font_corbel, 'Quit', quit_button_x, quit_button_y, button_width, button_height, 25, quit_button_x + 18)
            button(screen, font_corbel, 'Start', start_button_x, start_button_y, button_width, button_height, 25, start_button_x + 18)



            # Dirty Sprite
            t = pygame.time.get_ticks()
            color = random.choice(list(colors.cnames.values()))
            p.update0()  # call update on all sprites
            car1.update0()
            # for each dirty sprint, erase previous rect with background copy
            # and then copy new sprite to buffer
            rects = my_sprites.draw(screen)

            space.step(1 / 50)  # space loop (Physics loop, pymunk)
            clock.tick(400)  # limiting the frames per second to 120


            size_checkbox = roadtype_sel.width
            roadtype_sel.update(roadtype_choose)

            tiretype_sel.update(tiretype_choose)

            braketype_sel.update(braketype_choose)

            pygame.display.update(rects)  # copy rects from buffer to screen
main()