import pygame
import sys
import math
import os

# Initialize Pygame
pygame.init()

# Set up the screen and define origin
Width, Height = 600, 600
Ox, Oy = Width/2, Height/2
O = (Ox, Oy)


#Initial constants
arrow_ht = 20
arrow_angle = 30
RADIAL = 130 #aircraft position
INTERCEPTCOURSE = 280 #desired intercept course
myFont = pygame.font.SysFont("Arial", 15)

#Radialtxt = str(RADIAL)

screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Radio Navigation Intercepts")

#define input rects
w, h = 100, 40
radial_rect = pygame.Rect(50, 50, w, h)

# Colors
white = pygame.Color("white")
black = pygame.Color("black")
red = pygame.Color("red")
green = pygame.Color(0, 155, 0)
blue = pygame.Color("blue")
yellow = pygame.Color("yellow")
cyan = pygame.Color("cyan")
magenta = pygame.Color("magenta")
grey = pygame.Color(224, 224, 224)

def draw_position(radial, distance, heading):
    x = distance * math.sin(math.radians(radial))
    y = distance * math.cos(math.radians(radial))
    pos = (x,y)
    pygame.draw.circle(screen, red, xy(pos), radius = 5, width = 0) 

def draw_text_box(rect, text, active):
    if active:
        col = red
    else:
        col = grey
    pygame.draw.rect(screen, col, rect)
    pygame.draw.rect(screen, black, rect, 2)  # Draw the border of the text box
    img = font.render(text, True, black)
    text_rect = img.get_rect(center = rect.center)
    screen.blit(img, text_rect)

#coordinate transformations from top left with y down to origin with y up
def x(x): return(Ox + x)
def y(y): return(Oy - y)
def xy(xy): return((x(xy[0]),y(xy[1])))

def xcomp(r, theta):
    #x component of polar coords
    return(r*(math.sin(math.radians(theta))))

def ycomp(r, theta):
    #y component of polar coords
    return(r*(math.cos(math.radians(theta))))

def draw_compass_card():
    # Draw a basic compass card
    r = 200
    pygame.draw.line(screen, black, (x(0), y(-r)), (x(0), y(r)), width = 2)  # N/S
    pygame.draw.line(screen, black, (x(-r), y(0)), (x(r), y(0)), width = 2)  # E/W

def rotate(point, origin, rotation):
    #rotation in degrees
    px = point[0]
    py = point[1]
    ox = origin[0]
    oy = origin[1]

    #change to polar coords:
    r = math.sqrt((px-ox)**2+(py-oy)**2)
    theta1 = math.degrees(math.atan2(px-ox, py-oy))

    theta2 = theta1 + rotation

    px2 = ox + xcomp(r, theta2)
    py2 = oy + ycomp(r, theta2)

    point = (px2, py2)
    return(point)

def draw_text(text, font, colour, pt):
    img = font.render(text, True, colour, white)
    text_rect = img.get_rect(center = pt)
    #img = pygame.transform.rotate(img, 30)
    screen.blit(img, text_rect)

def draw_arrow(theta, length, inbound=False, outbound=False, colour=black, label=""):
    #draws an arrow from the origin

    tipx = xcomp(length, theta)
    tipy = ycomp(length, theta)
    tip = (tipx, tipy)

    #draw line (convert to screen coordinates)
    pygame.draw.line(screen, colour, O, xy(tip), 3)

    # Calculate points for arrowhead

    #construct vertical arrow with tip at origin, then rotate and translate

    angle = math.radians(arrow_angle)  #opening angle
    dx = arrow_ht * math.tan(angle/2)

    #OUTBOUND
    if outbound == True:
        p1 = (-dx, -arrow_ht) #normal coords
        p2 = (+dx, -arrow_ht) #normal coords

        #rotate
        p1 = rotate(p1, (0,0), theta)
        p2 = rotate(p2, (0,0), theta)

        #translate
        p1 = (p1[0] + tip[0], p1[1] + tip[1])
        p2 = (p2[0] + tip[0], p2[1] + tip[1])

        # Draw the arrowhead (convert to screen coordinates)
        pygame.draw.polygon(screen, colour, [xy(p1), xy(p2), xy(tip)])

    #INBOUND
    if inbound == True:
        p1 = (-dx, 0) #normal coords
        p2 = (+dx, 0) #normal coords
        p3 = (0, -arrow_ht)

        #rotate
        p1 = rotate(p1, (0,0), theta)
        p2 = rotate(p2, (0,0), theta)
        p3 = rotate(p3, (0,0), theta)

        #translate
        p1 = (p1[0] + tip[0], p1[1] + tip[1])
        p2 = (p2[0] + tip[0], p2[1] + tip[1])
        p3 = (p3[0] + tip[0], p3[1] + tip[1])

        # Draw the arrowhead (convert to screen coordinates)
        pygame.draw.polygon(screen, colour, [xy(p1), xy(p2), xy(p3)])

    if label != "":
        if label == "IN":
            theta = (theta + 180) % 360
            if theta == 0: theta = 360
        text = formatnum(theta) + " " + label
        middle = xy((tip[0]*1.25,tip[1]*1.25))
        draw_text(text, myFont, colour, middle)


def dotproduct(a, b):
    return(a[0]*b[0] + a[1]*b[1])

def norm(a):
    return(math.sqrt(a[0]**2 + a[1]**2))

def unit_vector(a):
    n = norm(a)
    return((a[0]/n, a[1]/n))

def scalar_projection(a, b):
    adotb = dotproduct(a,b)
    normb = norm(b)
    return(adotb/normb)

def a_onto_b(a, b):
    scalar = scalar_projection(a,b)
    bhat = unit_vector(b)
    vector_projection = (scalar * bhat[0], scalar * bhat[1])
    return(vector_projection)

def a_perp_b(a, b):
    aonb = a_onto_b(a, b)
    x = a[0] - aonb[0]
    y = a[1] - aonb[1]
    aperpb = (x,y)
    return(aperpb)

def extend_ab(a, b, extralength):
    #extend vector a --> b extralength beyond b
    ab = (b[0] - a[0], b[1] - a[1])
    ab_hat = unit_vector(ab)
    ab_len = norm(ab)
    ab_longer = ((ab_len + extralength) * ab_hat[0], (ab_len + extralength) * ab_hat[1])
    new_end = (a[0] + ab_longer[0], a[1] + ab_longer[1])
    return(new_end)

def get_intercept(R, theta, course, intercept=90):
    #need to project (R, theta) [a] onto course [b], i.e., a onto b
    a = (xcomp(R, theta), ycomp(R, theta))
    b = (xcomp(1, course), ycomp(1, course))

    #parallel component
    projection = a_onto_b(a, b)
    #90 deg intercept
    #pygame.draw.circle(screen, black, xy(projection), radius = 5, width = 1)

    #perpendicular component
    rejection = a_perp_b(a, b)

    #define a unit vector that is 90 degrees to the right of course
    right_hat = (xcomp(1, course+90), ycomp(1, course+90))

    #if the rejection is parallel to right_hat, intercept left
    #if the rejection is antiparallel to right_hat, intercept right
    #look at sign of scalar projection:

    sp = scalar_projection(rejection, right_hat)

    if sp <= 0:
        hand = "right" #antiparallel
        int_course = course + intercept
    if sp > 0:
        hand = "left" #parallel
        int_course = course - intercept


    # DETERMINE INTERCEPTION PT
    # need to handle infinite slopes using math.inf
    #line 1 (course)
    b1 = 0
    m1 = 1/math.tan(math.radians(course))

    #line 2 (intercept) - use 2 pts
    x1 = a[0]
    y1 = a[1]
    x2 = x1 + xcomp(10, int_course)
    y2 = y1 + ycomp(10, int_course)

    m2 = (y2-y1)/(x2-x1)
    b2 = y1 - m2*x1

    intercept_x = (b2-b1)/(m1-m2)
    intercept_y = m1*intercept_x + b1

    intercept = (intercept_x, intercept_y)

    #extend intercept course beyond the intercept point for plotting purposes
    intercept_ext = extend_ab(a, intercept, 100)

    #plot intercept point
    pygame.draw.circle(screen, blue, xy(intercept), radius = 5, width = 0)
    pygame.draw.line(screen, black, xy(a), xy(intercept_ext), width = 3)

    #draw arrow head
    angle = math.radians(arrow_angle)  #opening angle
    dx = arrow_ht * math.tan(angle/2)

    p1 = (-dx, -arrow_ht) #normal coords
    p2 = (+dx, -arrow_ht) #normal coords

    #rotate
    p1 = rotate(p1, (0,0), int_course)
    p2 = rotate(p2, (0,0), int_course)

    #translate
    p1 = (p1[0] + intercept_ext[0], p1[1] + intercept_ext[1])
    p2 = (p2[0] + intercept_ext[0], p2[1] + intercept_ext[1])

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, black, [xy(p1), xy(p2), xy(intercept_ext)])

    #draw label
    text = formatnum(int_course) + " INT"
    middle = xy(extend_ab(a, intercept_ext, 20))
    draw_text(text, myFont, black, middle)


def formatnum(num):
    return "{:03d}".format(num)

def take_screenshot():
    # Get the path to save the screenshot
    directory = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(directory, "screenshot.png")
    
    # Take the screenshot and save it (press s in game)
    pygame.image.save(screen, screenshot_path)
    print("Screenshot saved as:", screenshot_path)


def main():
    global RADIAL, Radialtxt, Radial_active
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    take_screenshot()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                Radial_active = False

                mos_pos = pygame.mouse.get_pos()
                if radial_rect.collidepoint(mos_pos):
                    print("radial click")
                    Radial_active = True

            if event.type == pygame.KEYDOWN:
                if Radial_active:
                    if event.key == pygame.K_RETURN:
                        Radial_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        Radialtxt = Radialtxt[:-1]
                    else:
                        Radialtxt += event.unicode

                    RADIAL = int(Radialtxt)

        # Clear the screen
        screen.fill(white)

        # Draw compass card
        draw_compass_card()

        # Draw radials
        for i in range(36):
            theta = i * 10
            r1 = 210
            length = 20
            r2 = r1 + length

            start = (xcomp(r1, theta), ycomp(r1, theta))
            end = (xcomp(r2, theta), ycomp(r2, theta))
            pygame.draw.line(screen, black, xy(start), xy(end))

            r3 = r2 + 20 # spacing for text
            textstart = (xcomp(r3, theta), ycomp(r3, theta))

            if theta == 0: theta = 360
            img = myFont.render(formatnum(theta), True, black)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)

        # bearing from/to stn
        draw_arrow(RADIAL, 200, False, True, red, "BFS")
        draw_arrow(RADIAL + 180, 200, False, True, green, "BTS")

        #inbound / outbound course
        draw_arrow(INTERCEPTCOURSE + 180, 200, True, False, blue, "")
        draw_arrow(INTERCEPTCOURSE, 200, False, True, blue, "OUT")
        
        draw_position(RADIAL, 150, 20)
        get_intercept(150, RADIAL, INTERCEPTCOURSE, 40)

        #draw_text_box(radial_rect, Radialtxt)


        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)


if __name__ == "__main__":
    main()
