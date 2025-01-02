import pygame
import sys
import math
import os
import re

# Initialize Pygame
pygame.init()

# Set up the screen and define origin
Width, Height = 1300, 650
Origin_x, Origin_y = 450, Height/2
O = (Origin_x, Origin_y)

#HSI origin
HSI_x, HSI_y = 900, 170

#fcADF origin
ADF_x, ADF_y = 900, Height-170

#rmi origin
RMI_x, RMI_y = 1150, Height/2

#Initial constants
arrow_ht = 20
arrow_angle = 30
RADIAL = 130 #aircraft position
R = 150 #aircraft position
COURSE = 280 #intercept course
TRACK = 0 #place holder
HEADING = RADIAL + 180
myFont = pygame.font.SysFont("Consolas", 15)
AC_POS = (0,0) #xy but change to r theta
FROM = True
HEADING = TRACK


#coordinate transformations from origin with y up to top left with y down
#for drawing
def x(x): return(Origin_x + x)
def y(y): return(Origin_y - y)
def xy(xy): return((x(xy[0]),y(xy[1])))

#coordinate transformations to origin with y up from top left with y down
def _x(x): return(-Origin_x + x)
def _y(y): return(Origin_y -y)
def _xy(xy): return((_x(xy[0]),_y(xy[1])))

def xcomp(r, theta):
    #x component of polar coords
    return(r*(math.sin(math.radians(theta))))

def ycomp(r, theta):
    #y component of polar coords
    return(r*(math.cos(math.radians(theta))))

def xy_to_rtheta(x,y):
    return(math.sqrt(x**2+y**2), math.degrees(math.atan2(x, y)))

def xy_points(points):
    processed = []
    for point in points:
        processed.append(xy(point))
    return processed

def rotate_pts(points, origin, rotation):
    processed = []
    for point in points:
        processed.append(rotate(point, origin, rotation))
    return(processed)

Radialtxt = str(RADIAL)
Coursetxt = str(COURSE)
Headingtxt = str(HEADING)

screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Radio Navigation Intercepts")

def get_pos_rect(r, theta):
    left = x(xcomp(r, theta)) - 10
    top = y(ycomp(r, theta)) - 10
    position_rect = pygame.Rect(left, top, 2*10, 2*10)
    return(position_rect)

#define input origin_x rects
w, h = 50, 30
radial_rect = pygame.Rect(50, y(+40) -h/2, w, h)
course_rect = pygame.Rect(50, y(0) -h/2, w, h)
heading_rect = pygame.Rect(50, y(-40) -h/2, w, h)
POS_rect = get_pos_rect(R, RADIAL)

AC_POS_rect = get_pos_rect(xy_to_rtheta(AC_POS[0], AC_POS[1])[0],xy_to_rtheta(AC_POS[0], AC_POS[1])[1])

# Colors
white = pygame.Color("white")
black = pygame.Color("black")
red = pygame.Color("red")
green = pygame.Color(0, 155, 0)
blue = pygame.Color("blue")
yellow = pygame.Color("yellow")
cyan = pygame.Color("cyan")
magenta = pygame.Color(255, 0, 250)
purple = pygame.Color("purple")
grey = pygame.Color(224, 224, 224)
lightyellow = pygame.Color(255, 255, 153)

def draw_position(radial, distance, heading):
    pos = (xcomp(distance, radial), ycomp(distance, radial))
    pygame.draw.circle(screen, red, xy(pos), radius = 10, width = 2)

def draw_input_box(rect, text, active, label, textcol):
    if active:
        backgroundcol = lightyellow
    else:
        backgroundcol = grey
    
    pos_center = rect.center

    pygame.draw.rect(screen, backgroundcol, rect)
    pygame.draw.rect(screen, black, rect, 2)  # Draw the border of the text box
    img = myFont.render(text, True, black)
    text_rect = img.get_rect(center = pos_center)
    screen.blit(img, text_rect)

    pos_center_offset = (pos_center[0] - 50, pos_center[1])

    draw_text(label, myFont, textcol, pos_center_offset)


def draw_compass_card():
    # Draw a basic compass card
    r = 200
    pygame.draw.line(screen, black, (x(0), y(-r)), (x(0), y(r)), width = 1)  # N/S
    pygame.draw.line(screen, black, (x(-r), y(0)), (x(r), y(0)), width = 1)  # E/W

def rotate(point, origin, rotation):
    #rotation in degrees
    px = point[0]
    py = point[1]
    Origin_x = origin[0]
    Origin_y = origin[1]

    #change to polar coords:
    r = math.sqrt((px-Origin_x)**2+(py-Origin_y)**2)
    theta1 = math.degrees(math.atan2(px-Origin_x, py-Origin_y))

    theta2 = theta1 + rotation

    px2 = Origin_x + xcomp(r, theta2)
    py2 = Origin_y + ycomp(r, theta2)

    point = (px2, py2)
    return(point)


def draw_text(text, font, colour, pt, background=False):
    img = font.render(text, True, colour)
    text_rect = img.get_rect(center = pt)
    
    if background == True:
        background_rect = text_rect.inflate(10,10)
        pygame.draw.rect(screen, white, background_rect)
        pygame.draw.rect(screen, black, background_rect, width = 1)

    screen.blit(img, text_rect)

def mod360(angle):
    angle = angle % 360
    if angle == 0: angle = 360
    return(angle)

def draw_arrow(theta, length, inbound=False, outbound=False, colour=black, label="", wt=3):
    #draws an arrow from the origin

    tipx = xcomp(length, theta)
    tipy = ycomp(length, theta)
    tip = (tipx, tipy)

    #draw line (convert to screen coordinates)
    pygame.draw.line(screen, colour, O, xy(tip), wt)

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
            theta = mod360(theta + 180)
        text = formatnum(theta) + " " + label
        middle = xy(extend_ab((0,0), tip, 100))
        draw_text(text, myFont, colour, middle)

def draw_arrow_map(theta, length, inbound=False, outbound=False, colour=black, label="", wt=3):
    #draws an arrow from the origin

    tip = theta_int_square(theta, 500)

    #draw line (convert to screen coordinates)
    pygame.draw.line(screen, colour, O, xy(tip), wt)

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
            theta = mod360(theta + 180)
        text = formatnum(theta) # + " " + label
        middle = xy(theta_int_square(theta, 500+60))
        draw_text(text, myFont, colour, middle, True)


def sign(x):
    if x > 0:
        return(1)
    elif x < 0:
        return(-1)
    else:
        return(0)

def draw_arrow_HSI(XTE):
    length = 90
    theta = COURSE - HEADING
    #draws an arrow from the origin

    tipx = xcomp(length, theta)
    tipy = ycomp(length, theta)
    tip = (tipx, tipy)
    start = (0, 0)

    #draw line (convert to screen coordinates)
    pygame.draw.line(screen, magenta, xy((-tipx + HSI_x-Origin_x, -tipy + HSI_y-Origin_y)), xy((tipx + HSI_x-Origin_x, tipy + HSI_y-Origin_y)), width = 3)
    # Calculate points for arrowhead

    #construct vertical arrow with tip at origin, then rotate and translate

    angle = math.radians(arrow_angle)  #opening angle
    dx = arrow_ht * math.tan(angle/2)

    #OUTBOUND
    p1 = (-dx, -arrow_ht) #normal coords
    p2 = (+dx, -arrow_ht) #normal coords

    #rotate
    p1 = rotate(p1, (0,0), theta)
    p2 = rotate(p2, (0,0), theta)

    #translate
    p1 = (p1[0] + tip[0] + HSI_x-Origin_x, p1[1] + tip[1] +HSI_y-Origin_y)
    p2 = (p2[0] + tip[0] + HSI_x-Origin_x, p2[1] + tip[1] +HSI_y-Origin_y)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, magenta, [xy(p1), xy(p2), xy((tipx+HSI_x-Origin_x, tipy+HSI_y-Origin_y))])

    #draw XTE
    right_hat = (xcomp(1, theta+90), ycomp(1, theta+90))

    #limit XTE to full scale deflection (5 dots worth)
    dot_space = 10


    XTE = sign(XTE) * min(abs(XTE), 5 * dot_space)
    #print(XTE, sign(XTE), abs(XTE))

    xtrackvector = ((XTE * right_hat[0], XTE * right_hat[1]))

    xtrack_length = 30

    xte1 = (xcomp(xtrack_length, theta) - xtrackvector[0], ycomp(xtrack_length, theta) - xtrackvector[1])
    xte2 = (-xcomp(xtrack_length, theta) - xtrackvector[0], -ycomp(xtrack_length, theta) - xtrackvector[1])

    pygame.draw.line(screen, magenta, xy((xte1[0] + HSI_x-Origin_x, xte1[1] + HSI_y-Origin_y)), xy((xte2[0] + HSI_x-Origin_x, xte2[1] + HSI_y-Origin_y)), width = 3)

    #to from flag:
    flaglength = 70 #distance above origin

    flagoffsetangle = 15

    if FROM:
        theta = theta + 180
        flagoffsetangle = -flagoffsetangle

    flagx = xcomp(flaglength, theta + flagoffsetangle)
    flagy = ycomp(flaglength, theta + flagoffsetangle)
    flagtip = (flagx, flagy)

    flagp1 = (-(dx+5), -arrow_ht) #normal coords
    flagp2 = (+(dx+5), -arrow_ht) #normal coords

    #rotate
    flagp1 = rotate(flagp1, (0,0), theta)
    flagp2 = rotate(flagp2, (0,0), theta)

    #translate
    flagp1 = (flagp1[0] + flagtip[0] + HSI_x-Origin_x, flagp1[1] + flagtip[1] + HSI_y-Origin_y)
    flagp2 = (flagp2[0] + flagtip[0] + HSI_x-Origin_x, flagp2[1] + flagtip[1] + HSI_y-Origin_y)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, black, [xy(flagp1), xy(flagp2), xy((flagx+HSI_x-Origin_x, flagy+HSI_y-Origin_y))])


    #draw the dots
    for i in range(-5, 6):
        if i != 0:
            circlepos = (right_hat[0] * dot_space * i + HSI_x-Origin_x, right_hat[1] * dot_space * i + HSI_y-Origin_y)
            pygame.draw.circle(screen, black, xy(circlepos), radius = 2)


def draw_arrow_fcadf():
    length = 90
    
    AC_POS_R_THETA = xy_to_rtheta(AC_POS[0], AC_POS[1])
    BEARING_FROM_STATION = AC_POS_R_THETA[1]
    BEARING_TO_STATION = mod360(BEARING_FROM_STATION + 180)

    RELATIVE_BEARING = BEARING_TO_STATION - HEADING  # edit here (was theta)

    #draws an arrow from the origin

    tipx = xcomp(length, RELATIVE_BEARING)
    tipy = ycomp(length, RELATIVE_BEARING)
    tip = (tipx, tipy)
    start = (0, 0)

    #draw line (convert to screen coordinates)
    pygame.draw.line(screen, magenta, xy((-tipx + ADF_x-Origin_x, -tipy + ADF_y-Origin_y)), xy((tipx + ADF_x-Origin_x, tipy + ADF_y-Origin_y)), width = 3)
    # Calculate points for arrowhead

    #construct vertical arrow with tip at origin, then rotate and translate

    angle = math.radians(arrow_angle)  #opening angle
    dx = arrow_ht * math.tan(angle/2)

    #OUTBOUND
    p1 = (-dx, -arrow_ht) #normal coords
    p2 = (+dx, -arrow_ht) #normal coords

    #rotate
    p1 = rotate(p1, (0,0), RELATIVE_BEARING)
    p2 = rotate(p2, (0,0), RELATIVE_BEARING)

    #translate
    p1 = (p1[0] + tip[0] + ADF_x-Origin_x, p1[1] + tip[1] +ADF_y-Origin_y)
    p2 = (p2[0] + tip[0] + ADF_x-Origin_x, p2[1] + tip[1] +ADF_y-Origin_y)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, magenta, [xy(p1), xy(p2), xy((tipx+ADF_x-Origin_x, tipy+ADF_y-Origin_y))])

def draw_arrow_RMI():
    length = 90

    AC_POS_R_THETA = xy_to_rtheta(AC_POS[0], AC_POS[1])
    BEARING_FROM_STATION = AC_POS_R_THETA[1]
    BEARING_TO_STATION = mod360(BEARING_FROM_STATION + 180)

    theta = BEARING_TO_STATION - HEADING
    #draws an arrow from the origin

    tipx = xcomp(length, theta)
    tipy = ycomp(length, theta)
    tip = (tipx, tipy)
    start = (0, 0)

    #draw line (convert to screen coordinates)
    pygame.draw.line(screen, magenta, xy((-tipx + RMI_x-Origin_x, -tipy + RMI_y-Origin_y)), xy((tipx + RMI_x-Origin_x, tipy + RMI_y-Origin_y)), width = 3)
    # Calculate points for arrowhead

    #construct vertical arrow with tip at origin, then rotate and translate

    angle = math.radians(arrow_angle)  #opening angle
    dx = arrow_ht * math.tan(angle/2)

    #OUTBOUND
    p1 = (-dx, -arrow_ht) #normal coords
    p2 = (+dx, -arrow_ht) #normal coords

    #rotate
    p1 = rotate(p1, (0,0), theta)
    p2 = rotate(p2, (0,0), theta)

    #translate
    p1 = (p1[0] + tip[0] + RMI_x-Origin_x, p1[1] + tip[1] +RMI_y-Origin_y)
    p2 = (p2[0] + tip[0] + RMI_x-Origin_x, p2[1] + tip[1] +RMI_y-Origin_y)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, magenta, [xy(p1), xy(p2), xy((tipx+RMI_x-Origin_x, tipy+RMI_y-Origin_y))])


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


def formatnum(num):
    return "{:03d}".format(round(num))

def take_screenshot():
    # Get the path to save the screenshot
    directory = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(directory, "screenshot.png")
    

    # Take the screenshot and save it (press s in game)
    pygame.image.save(screen, screenshot_path)
    print("Screenshot saved as:", screenshot_path)

def process_deg_text(s):
    #return numbers using regex
    pattern = r'\d+'
    match = re.search(pattern, s)

    if match:
        s = match.group()
    else:
        s = ""
    return(s)

def get_radial_from_text(s):
    #s has already been processed to get digits only, as string
    if s == "":
        s = 360
    else:
        s = mod360(int(s))
    return(s)

Radial_active = False
Course_active = False

#the following is a list of points (x,y), relative to origin, that when connected from start to finish will make an airplane
plane_def = [(0,2),(0,-2),(0,1),(-2,1),(2,1),(0,1),(0,-1),(-1,-1),(1,-1)]
scalefactor = 10
plane_def_scaled = [(scalefactor*x, scalefactor*y) for x, y in plane_def]

def draw_plane(rotation):
    #global AC_POS #<- dont need this to be global b/c not modifying AC_POS in this function
    plane = rotate_pts(plane_def_scaled, (0,0), rotation)
    
    plane2 = [(AC_POS[0] + x, AC_POS[1] + y) for x,y in plane]

    #print(AC_POS)
    plane = xy_points(plane2)
    pygame.draw.lines(screen, blue, False, plane, width = 4)


def draw_hsi():
    # Draw radials
    r1 = 120
    pygame.draw.line(screen, red, xy((HSI_x-Origin_x,r1+HSI_y-Origin_y)), xy((HSI_x-Origin_x,r1+7+HSI_y-Origin_y)), width = 5)
    for i in range(72):
        theta = mod360(i * 5)

        if theta % 10 == 0: # big tick
            length = 20
        else: 
            length = 10

        r2 = r1 - length

        angle = theta - HEADING
        
        start = (xcomp(r1, angle) + HSI_x - Origin_x, ycomp(r1, angle) + HSI_y - Origin_y)
        end = (xcomp(r2, angle) + HSI_x - Origin_x, ycomp(r2, angle) + HSI_y - Origin_y)
        pygame.draw.line(screen, black, xy(start), xy(end))

        if theta % 30 == 0:
            r3 = r1 + 10 # spacing for text
            textstart = (xcomp(r3, angle) + HSI_x - Origin_x, ycomp(r3, angle) + HSI_y - Origin_y)

            img = myFont.render(str(int(theta/10)), True, black)
            img = pygame.transform.rotate(img, -angle)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)
    title = myFont.render("HSI", True, black)
    title_rect = title.get_rect(center = xy((HSI_x-Origin_x, HSI_y-Origin_y + 150)))
    screen.blit(title,title_rect)

#need to draw fixed card adf, which always gives relative bearing to vor/ndb

def draw_fcadf():
    r1 = 120
    pygame.draw.line(screen, red, xy((ADF_x-Origin_x,r1+ADF_y-Origin_y)), xy((ADF_x-Origin_x,r1+7+ADF_y-Origin_y)), width = 5)
    # draw radials
    for i in range(72):
        theta = mod360(i * 5)

        if theta % 10 == 0: # big tick
            length = 20
        else: 
            length = 10

        r2 = r1 - length

        angle = theta
        
        start = (xcomp(r1, angle) + ADF_x - Origin_x, ycomp(r1, angle) + ADF_y - Origin_y)
        end = (xcomp(r2, angle) + ADF_x - Origin_x, ycomp(r2, angle) + ADF_y - Origin_y)
        pygame.draw.line(screen, black, xy(start), xy(end))

        if theta % 30 == 0:
            r3 = r1 + 10 # spacing for text
            textstart = (xcomp(r3, angle) + ADF_x - Origin_x, ycomp(r3, angle) + ADF_y - Origin_y)

            img = myFont.render(str(int(theta/10)), True, black)
            img = pygame.transform.rotate(img, -angle)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)
    title = myFont.render("FIXED CARD ADF", True, black)
    title_rect = title.get_rect(center = xy((ADF_x-Origin_x, ADF_y-Origin_y + 150)))
    screen.blit(title,title_rect)
    

def draw_rmi():
    r1 = 120
    pygame.draw.line(screen, red, xy((RMI_x-Origin_x,r1+RMI_y-Origin_y)), xy((RMI_x-Origin_x,r1+7+RMI_y-Origin_y)), width = 5)
    # Draw radials
    for i in range(72):
        theta = mod360(i * 5)

        if theta % 10 == 0: # big tick
            length = 20
        else: 
            length = 10
        
        r2 = r1 - length

        angle = theta - HEADING
        
        start = (xcomp(r1, angle) + RMI_x - Origin_x, ycomp(r1, angle) + RMI_y - Origin_y)
        end = (xcomp(r2, angle) + RMI_x - Origin_x, ycomp(r2, angle) + RMI_y - Origin_y)
        pygame.draw.line(screen, black, xy(start), xy(end))

        if theta % 30 == 0:
            r3 = r1 + 10 # spacing for text
            textstart = (xcomp(r3, angle) + RMI_x-Origin_x, ycomp(r3, angle) + RMI_y-Origin_y)

            img = myFont.render(str(int(theta/10)), True, black)
            img = pygame.transform.rotate(img, -angle)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)
    title = myFont.render("RMI", True, black)
    title_rect = title.get_rect(center = xy((RMI_x-Origin_x, RMI_y-Origin_y + 150)))
    screen.blit(title,title_rect)

def update_position():
    pass

def get_crosstrack_error():
    global FROM
    #i think this is the magnitude of the rejection of the ac pos vector onto the course unit vector 
    
    course_hat = unit_vector((xcomp(1, COURSE), ycomp(1, COURSE)))

    course_reject_position = a_perp_b(AC_POS, course_hat)
    crosstrackerror = norm(course_reject_position)

    #need to get sign: designate + as course is to left, i.e. R XTE
    right_hat = (xcomp(1, COURSE+90), ycomp(1, COURSE+90))

    sp = scalar_projection(course_reject_position, right_hat)
    if sp < 0:
        crosstrackerror = crosstrackerror * - 1

    #need a couple extra defs for plotting purposes
    course_parallel_pos = a_onto_b(AC_POS, course_hat)
    pygame.draw.line(screen, black, xy(course_parallel_pos), xy(AC_POS), width = 1)

    #also for fun, draw the projection vector too (used for to/from flag)
    pygame.draw.line(screen, black, xy(course_reject_position), xy(AC_POS), width = 1)
    
    if scalar_projection(course_parallel_pos, course_hat) > 0:
        FROM = True
    else:
        FROM = False

    return(crosstrackerror)

def draw_map():
    h = w = 500
    MapRect = pygame.Rect(x(-w/2), y(h/2), w, h)
    pygame.draw.rect(screen, black, MapRect, 2)

    for i in range(36):
        theta = mod360(i * 10)

        start = theta_int_square(theta, h)
        end = theta_int_square(theta, h+30)
        pygame.draw.line(screen, black, xy(start), xy(end))

        textstart = theta_int_square(theta, h+60)

        img = myFont.render(formatnum(theta), True, black)
        text_rect = img.get_rect(center = xy(textstart))
        screen.blit(img, text_rect)

def theta_int_square(theta, side_length):
    theta = mod360(theta)
    if theta >= 45 and theta < 135:
        x = side_length/2
        y = x * math.tan(math.radians(90 - theta))
    elif theta >= 135 and theta < 225:
        y = -side_length/2
        x = -y * math.tan(math.radians(180 - theta))
    elif theta >= 225 and theta < 315:
        x = -side_length/2
        y = x * math.tan(math.radians(270 - theta))
    else:
        y = side_length/2
        x = y * math.tan(math.radians(theta))
    return((x,y))


def gameloop():
    global RADIAL, Radialtxt, Radial_active
    global COURSE, Coursetxt, Course_active
    global Tracktxt
    global R, POS_rect, HEADING, AC_POS, AC_POS_rect

    clock = pygame.time.Clock()
    running = True
    dragging_ac = False

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
                Course_active = False

                mos_pos = pygame.mouse.get_pos()

                if radial_rect.collidepoint(mos_pos):
                    print("radial click")
                    Radial_active = True
                elif course_rect.collidepoint(mos_pos):
                    print("course click")
                    Course_active = True
                elif AC_POS_rect.collidepoint(mos_pos):
                    print("AC click")
                    dragging_ac = True

            elif dragging_ac and event.type == pygame.MOUSEBUTTONUP:
                dragging_ac = False
                AC_POS_rect = get_pos_rect(xy_to_rtheta(AC_POS[0], AC_POS[1])[0],xy_to_rtheta(AC_POS[0], AC_POS[1])[1])
                # need to update radial based on AC pos
                #RADIAL = 
                print("unclick")

            elif event.type == pygame.MOUSEMOTION:
                if dragging_ac:
                    AC_POS = _xy(event.pos)

            #need to make this a function
            if event.type == pygame.KEYDOWN:
                if Radial_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        Radial_active = False
                        RADIAL = get_radial_from_text(Radialtxt)
                        POS_rect = get_pos_rect(R, RADIAL)
                    elif event.key == pygame.K_BACKSPACE:
                        Radialtxt = ""
                    else:
                        if len(Radialtxt) == 3:
                            Radialtxt = event.unicode
                        else:
                            Radialtxt += event.unicode
                elif Course_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        Course_active = False
                        COURSE = get_radial_from_text(Coursetxt)
                    elif event.key == pygame.K_BACKSPACE:
                        Coursetxt = ""
                    else:
                        if len(Coursetxt) == 3:
                            Coursetxt = event.unicode
                        else:
                            Coursetxt += event.unicode     

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            HEADING += 0.5
        elif keys[pygame.K_LEFT]:
            HEADING -= 0.5
        if keys[pygame.K_UP]:
            v = 0.5
            dx = v * math.sin(math.radians(HEADING))
            dy = v * math.cos(math.radians(HEADING))
            AC_POS =(AC_POS[0] + dx, AC_POS[1] + dy)
            AC_POS_rect = get_pos_rect(xy_to_rtheta(AC_POS[0], AC_POS[1])[0],xy_to_rtheta(AC_POS[0], AC_POS[1])[1])


        if not Radial_active:
            #update radial
            Radialtxt = str(RADIAL)

        if not Course_active:
            #update course
            Coursetxt = str(COURSE)

        Radialtxt = process_deg_text(Radialtxt)
        Coursetxt = process_deg_text(Coursetxt)
        Headingtxt = process_deg_text(str(mod360(HEADING)))

        # Clear the screen
        screen.fill(white)

        # Draw stuff
        draw_compass_card()
        draw_map()
        draw_hsi()

        xte = get_crosstrack_error()
        draw_arrow_HSI(xte)

        draw_fcadf()
        draw_arrow_fcadf()

        draw_rmi()
        draw_arrow_RMI()

        arrow_len = 200
        line_len = 270

        RADIAL = mod360(math.degrees(math.atan2(AC_POS[0], AC_POS[1])))

        # bearing from/to stn
        draw_arrow_map(RADIAL, arrow_len, False, False, red, "RAD", 3) #RAD
        draw_arrow_map(RADIAL, line_len, False, False, red, "", 1)
        draw_arrow_map(mod360(RADIAL + 180), arrow_len, False, True, green, "BRG", 3) #BRG
        draw_arrow_map(RADIAL + 180, line_len, False, False, green, "", 1)

        #inbound / outbound course
        draw_arrow_map(COURSE + 180, arrow_len, False, False, magenta, "", 3)
        draw_arrow_map(COURSE + 180, line_len, False, False, magenta, "", 1)
        draw_arrow_map(COURSE, arrow_len, False, True, magenta, "CRS", 3)
        draw_arrow_map(COURSE, line_len, False, False, magenta, "", 1)
        
        draw_input_box(radial_rect, Radialtxt, Radial_active, "RAD", red)
        draw_input_box(course_rect, Coursetxt, Course_active, "CRS", magenta)
        draw_input_box(heading_rect, Headingtxt, False, "HDG", black)

        draw_plane(HEADING)

        # Update the display
        pygame.display.flip()

        

        # Cap the frame rate
        clock.tick(60)


if __name__ == "__main__":
    gameloop()


#to do:
# - HSI - cutout XTE and turn whole thing green
# - change RMI needles to look like RMI (double arrow tail, etc.)
# - Make map square, take out intercepts
# - bearing to station, bearing from station, linked to A/C position on map (e.g. as GPS readout)
# - instrument colours = black background (ADF needles are white)

