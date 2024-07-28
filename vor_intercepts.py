import pygame
import sys
import math
import os
import re

# Initialize Pygame
pygame.init()

# Set up the screen and define origin
Width, Height = 1300, 650
Ox, Oy = 450, Height/2
O = (Ox, Oy)

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
ANGLE = 40 #intercept angle
TRACK = 0 #place holder
HEADING = RADIAL + 180
myFont = pygame.font.SysFont("Consolas", 15)
INTERCEPT = (0,0) #xy but change to r theta
AC_POS = (0,0) #xy but change to r theta
FROM = True
HEADING = TRACK


#coordinate transformations from origin with y up to top left with y down
#for drawing
def x(x): return(Ox + x)
def y(y): return(Oy - y)
def xy(xy): return((x(xy[0]),y(xy[1])))

#coordinate transformations to origin with y up from top left with y down
def _x(x): return(-Ox + x)
def _y(y): return(Oy -y)
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
Angletxt = str(ANGLE)
Tracktxt = str(TRACK)

screen = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Radio Navigation Intercepts")

#stuff for images
#plane = pygame.image.load('737.png').convert_alpha()
#plane = pygame.transform.scale(plane, (50,50))
#image_rect = plane.get_rect()
#image_rect.topleft = (x(0), y(0))

def get_pos_rect(r, theta):
    left = x(xcomp(r, theta)) - 10
    top = y(ycomp(r, theta)) - 10
    position_rect = pygame.Rect(left, top, 2*10, 2*10)
    return(position_rect)



#define input box rects
w, h = 50, 30
radial_rect = pygame.Rect(50, y(+60) -h/2, w, h)
course_rect = pygame.Rect(50, y(+20) -h/2, w, h)
angle_rect = pygame.Rect(50, y(-20) -h/2, w, h)
track_rect = pygame.Rect(50, y(-60) -h/2, w, h)
POS_rect = get_pos_rect(R, RADIAL)

AC_POS_rect = get_pos_rect(xy_to_rtheta(AC_POS[0], AC_POS[1])[0],xy_to_rtheta(AC_POS[0], AC_POS[1])[1])
print(AC_POS_rect)

# Colors
white = pygame.Color("white")
black = pygame.Color("black")
red = pygame.Color("red")
green = pygame.Color(0, 155, 0)
blue = pygame.Color("blue")
yellow = pygame.Color("yellow")
cyan = pygame.Color("cyan")
magenta = pygame.Color("magenta")
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
    img = font.render(text, True, colour)
    text_rect = img.get_rect(center = pt)
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
    pygame.draw.line(screen, purple, xy((-tipx + HSI_x-Ox, -tipy + HSI_y-Oy)), xy((tipx + HSI_x-Ox, tipy + HSI_y-Oy)), width = 3)
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
    p1 = (p1[0] + tip[0] + HSI_x-Ox, p1[1] + tip[1] +HSI_y-Oy)
    p2 = (p2[0] + tip[0] + HSI_x-Ox, p2[1] + tip[1] +HSI_y-Oy)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, purple, [xy(p1), xy(p2), xy((tipx+HSI_x-Ox, tipy+HSI_y-Oy))])

    #draw XTE
    right_hat = (xcomp(1, theta+90), ycomp(1, theta+90))

    #limit XTE to full scale deflection (5 dots worth)
    dot_space = 10


    XTE = sign(XTE) * min(abs(XTE), 5 * dot_space)
    print(XTE, sign(XTE), abs(XTE))

    xtrackvector = ((XTE * right_hat[0], XTE * right_hat[1]))

    xtrack_length = 30

    xte1 = (xcomp(xtrack_length, theta) - xtrackvector[0], ycomp(xtrack_length, theta) - xtrackvector[1])
    xte2 = (-xcomp(xtrack_length, theta) - xtrackvector[0], -ycomp(xtrack_length, theta) - xtrackvector[1])

    pygame.draw.line(screen, purple, xy((xte1[0] + HSI_x-Ox, xte1[1] + HSI_y-Oy)), xy((xte2[0] + HSI_x-Ox, xte2[1] + HSI_y-Oy)), width = 3)

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
    flagp1 = (flagp1[0] + flagtip[0] + HSI_x-Ox, flagp1[1] + flagtip[1] + HSI_y-Oy)
    flagp2 = (flagp2[0] + flagtip[0] + HSI_x-Ox, flagp2[1] + flagtip[1] + HSI_y-Oy)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, black, [xy(flagp1), xy(flagp2), xy((flagx+HSI_x-Ox, flagy+HSI_y-Oy))])


    #draw the dots
    for i in range(-5, 6):
        if i != 0:
            circlepos = (right_hat[0] * dot_space * i + HSI_x-Ox, right_hat[1] * dot_space * i + HSI_y-Oy)
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
    pygame.draw.line(screen, purple, xy((-tipx + ADF_x-Ox, -tipy + ADF_y-Oy)), xy((tipx + ADF_x-Ox, tipy + ADF_y-Oy)), width = 3)
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
    p1 = (p1[0] + tip[0] + ADF_x-Ox, p1[1] + tip[1] +ADF_y-Oy)
    p2 = (p2[0] + tip[0] + ADF_x-Ox, p2[1] + tip[1] +ADF_y-Oy)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, purple, [xy(p1), xy(p2), xy((tipx+ADF_x-Ox, tipy+ADF_y-Oy))])

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
    pygame.draw.line(screen, purple, xy((-tipx + RMI_x-Ox, -tipy + RMI_y-Oy)), xy((tipx + RMI_x-Ox, tipy + RMI_y-Oy)), width = 3)
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
    p1 = (p1[0] + tip[0] + RMI_x-Ox, p1[1] + tip[1] +RMI_y-Oy)
    p2 = (p2[0] + tip[0] + RMI_x-Ox, p2[1] + tip[1] +RMI_y-Oy)

    # Draw the arrowhead (convert to screen coordinates)
    pygame.draw.polygon(screen, purple, [xy(p1), xy(p2), xy((tipx+RMI_x-Ox, tipy+RMI_y-Oy))])


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
    global TRACK, INTERCEPT
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
        TRACK = course + intercept
    if sp > 0:
        hand = "left" #parallel
        TRACK = course - intercept


    # DETERMINE INTERCEPTION PT
    # need to handle infinite slopes using math.inf
    #line 1 (course)
    b1 = 0
    m1 = 1/math.tan(math.radians(course))

    #line 2 (intercept) - use 2 pts
    x1 = a[0]
    y1 = a[1]
    x2 = x1 + xcomp(10, TRACK)
    y2 = y1 + ycomp(10, TRACK)

    m2 = (y2-y1)/(x2-x1)
    b2 = y1 - m2*x1

    intercept_x = (b2-b1)/(m1-m2)
    intercept_y = m1*intercept_x + b1

    intercept = (intercept_x, intercept_y)
    INTERCEPT = intercept
    #print(INTERCEPT)

    #extend intercept course beyond the intercept point for plotting purposes
    intercept_ext = extend_ab(a, intercept, 100)

    #plot intercept point
    pygame.draw.circle(screen, purple, xy(intercept), radius = 10, width = 2)
    pygame.draw.line(screen, black, xy(a), xy(intercept_ext), width = 3)

    #draw arrowhead
    angle = math.radians(arrow_angle)  #opening angle
    dx = arrow_ht * math.tan(angle/2)

    p1 = (-dx, -arrow_ht) #normal coords
    p2 = (+dx, -arrow_ht) #normal coords

    #rotate
    p1 = rotate(p1, (0,0), TRACK)
    p2 = rotate(p2, (0,0), TRACK)

    #translate
    p1 = (p1[0] + intercept_ext[0], p1[1] + intercept_ext[1])
    p2 = (p2[0] + intercept_ext[0], p2[1] + intercept_ext[1])

    # Draw the arrowhead in screen coordinates
    pygame.draw.polygon(screen, black, [xy(p1), xy(p2), xy(intercept_ext)])

    #draw label
    text = formatnum(mod360(TRACK)) + " TRK"
    middle = xy(extend_ab(a, intercept_ext, 20))
    draw_text(text, myFont, black, middle)

def midpoint():
    p1 = (xcomp(R, RADIAL), ycomp(R, RADIAL))
    p2 = INTERCEPT
    midpt = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2)
    #print(midpt)
    return(midpt)

def formatnum(num):
    return "{:03d}".format(round(num))

def take_screenshot():
    # Get the path to save the screenshot
    directory = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(directory, "screenshot.png")
    

    # Take the screenshot and save it (press s in game)
    pygame.image.save(screen, screenshot_path)
    print("Screenshot saved as:", screenshot_path)

def process_radial_text(s):
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
Angle_active = False

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
    pygame.draw.line(screen, red, xy((HSI_x-Ox,r1+HSI_y-Oy)), xy((HSI_x-Ox,r1+7+HSI_y-Oy)), width = 5)
    for i in range(72):
        theta = mod360(i * 5)

        if theta % 10 == 0: # big tick
            length = 20
        else: 
            length = 10

        r2 = r1 - length

        angle = theta - HEADING
        
        start = (xcomp(r1, angle) + HSI_x - Ox, ycomp(r1, angle) + HSI_y - Oy)
        end = (xcomp(r2, angle) + HSI_x - Ox, ycomp(r2, angle) + HSI_y - Oy)
        pygame.draw.line(screen, black, xy(start), xy(end))

        if theta % 30 == 0:
            r3 = r1 + 10 # spacing for text
            textstart = (xcomp(r3, angle) + HSI_x - Ox, ycomp(r3, angle) + HSI_y - Oy)

            img = myFont.render(str(int(theta/10)), True, black)
            img = pygame.transform.rotate(img, -angle)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)
    title = myFont.render("HSI", True, black)
    title_rect = title.get_rect(center = xy((HSI_x-Ox, HSI_y-Oy + 150)))
    screen.blit(title,title_rect)

#need to draw fixed card adf, which always gives relative bearing to vor/ndb

def draw_fcadf():
    r1 = 120
    pygame.draw.line(screen, red, xy((ADF_x-Ox,r1+ADF_y-Oy)), xy((ADF_x-Ox,r1+7+ADF_y-Oy)), width = 5)
    # draw radials
    for i in range(72):
        theta = mod360(i * 5)

        if theta % 10 == 0: # big tick
            length = 20
        else: 
            length = 10

        r2 = r1 - length

        angle = theta
        
        start = (xcomp(r1, angle) + ADF_x - Ox, ycomp(r1, angle) + ADF_y - Oy)
        end = (xcomp(r2, angle) + ADF_x - Ox, ycomp(r2, angle) + ADF_y - Oy)
        pygame.draw.line(screen, black, xy(start), xy(end))

        if theta % 30 == 0:
            r3 = r1 + 10 # spacing for text
            textstart = (xcomp(r3, angle) + ADF_x - Ox, ycomp(r3, angle) + ADF_y - Oy)

            img = myFont.render(str(int(theta/10)), True, black)
            img = pygame.transform.rotate(img, -angle)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)
    title = myFont.render("F.C. ADF", True, black)
    title_rect = title.get_rect(center = xy((ADF_x-Ox, ADF_y-Oy + 150)))
    screen.blit(title,title_rect)
    

def draw_rmi():
    r1 = 120
    pygame.draw.line(screen, red, xy((RMI_x-Ox,r1+RMI_y-Oy)), xy((RMI_x-Ox,r1+7+RMI_y-Oy)), width = 5)
    # Draw radials
    for i in range(72):
        theta = mod360(i * 5)

        if theta % 10 == 0: # big tick
            length = 20
        else: 
            length = 10

        r2 = r1 - length

        angle = theta - HEADING
        
        start = (xcomp(r1, angle) + RMI_x - Ox, ycomp(r1, angle) + RMI_y - Oy)
        end = (xcomp(r2, angle) + RMI_x - Ox, ycomp(r2, angle) + RMI_y - Oy)
        pygame.draw.line(screen, black, xy(start), xy(end))

        if theta % 30 == 0:
            r3 = r1 + 10 # spacing for text
            textstart = (xcomp(r3, angle) + RMI_x-Ox, ycomp(r3, angle) + RMI_y-Oy)

            img = myFont.render(str(int(theta/10)), True, black)
            img = pygame.transform.rotate(img, -angle)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)
    title = myFont.render("RMI", True, black)
    title_rect = title.get_rect(center = xy((RMI_x-Ox, RMI_y-Oy + 150)))
    screen.blit(title,title_rect)


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

def gameloop():
    global RADIAL, Radialtxt, Radial_active
    global COURSE, Coursetxt, Course_active
    global ANGLE, Angletxt, Angle_active
    global TRACK, Tracktxt
    global R, POS_rect, HEADING, AC_POS, AC_POS_rect

    clock = pygame.time.Clock()
    running = True
    dragging = False
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
                Angle_active = False

                mos_pos = pygame.mouse.get_pos()

                if radial_rect.collidepoint(mos_pos):
                    print("radial click")
                    Radial_active = True
                elif course_rect.collidepoint(mos_pos):
                    print("course click")
                    Course_active = True
                elif angle_rect.collidepoint(mos_pos):
                    print("angle click")
                    Angle_active = True
                elif POS_rect.collidepoint(mos_pos):
                    print("position click")
                    #print(mos_pos)
                    HEADING = TRACK
                    dragging = True
                elif AC_POS_rect.collidepoint(mos_pos):
                    print("AC click")
                    dragging_ac = True

            elif dragging and event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                AC_POS_rect = get_pos_rect(xy_to_rtheta(AC_POS[0], AC_POS[1])[0],xy_to_rtheta(AC_POS[0], AC_POS[1])[1])
                POS_rect = get_pos_rect(R, RADIAL)
                print("unclick")

            elif dragging_ac and event.type == pygame.MOUSEBUTTONUP:
                dragging_ac = False
                AC_POS_rect = get_pos_rect(xy_to_rtheta(AC_POS[0], AC_POS[1])[0],xy_to_rtheta(AC_POS[0], AC_POS[1])[1])
                print("unclick")

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = _xy(event.pos)
                    pos = xy_to_rtheta(mouse_x, mouse_y)
                    R = pos[0]
                    RADIAL = mod360(pos[1])
                    AC_POS = midpoint()
                    print(R, RADIAL)

                elif dragging_ac:
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
                elif Angle_active:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        Angle_active = False
                        ANGLE = get_radial_from_text(Angletxt)
                    elif event.key == pygame.K_BACKSPACE:
                        Angletxt = ""
                    else:
                        if len(Angletxt) == 2:
                            Angletxt = event.unicode
                        else:
                            Angletxt += event.unicode
        
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

        if not Angle_active:
            #update angle
            Angletxt = str(ANGLE)

        Radialtxt = process_radial_text(Radialtxt)
        Coursetxt = process_radial_text(Coursetxt)
        Angletxt = process_radial_text(Angletxt)
        Tracktxt = process_radial_text(str(mod360(TRACK)))

        # Clear the screen
        screen.fill(white)

        # Draw compass card
        draw_compass_card()

        # Draw radials
        for i in range(36):
            theta = mod360(i * 10)
            r1 = 210
            length = 20
            r2 = r1 + length

            start = (xcomp(r1, theta), ycomp(r1, theta))
            end = (xcomp(r2, theta), ycomp(r2, theta))
            pygame.draw.line(screen, black, xy(start), xy(end))

            r3 = r2 + 20 # spacing for text
            textstart = (xcomp(r3, theta), ycomp(r3, theta))

            img = myFont.render(formatnum(theta), True, black)
            text_rect = img.get_rect(center = xy(textstart))
            screen.blit(img, text_rect)


        draw_hsi()
        xte = get_crosstrack_error()
        #print("xte = ",xte)
        draw_arrow_HSI(xte)

        draw_fcadf()
        draw_arrow_fcadf()

        draw_rmi()
        draw_arrow_RMI()


        arrow_len = 200
        line_len = 270

        # bearing from/to stn
        draw_arrow(RADIAL, arrow_len, False, True, red, "BFS", 3)
        draw_arrow(RADIAL, line_len, False, False, red, "", 1)
        draw_arrow(mod360(RADIAL + 180), arrow_len, False, True, green, "BTS", 3)
        draw_arrow(RADIAL + 180, line_len, False, False, green, "", 1)

        #inbound / outbound course
        draw_arrow(COURSE + 180, arrow_len, True, False, purple, "IN", 3)
        draw_arrow(COURSE + 180, line_len, False, False, purple, "", 1)
        draw_arrow(COURSE, arrow_len, False, True, purple, "OUT", 3)
        draw_arrow(COURSE, line_len, False, False, purple, "", 1)

        draw_position(radial = RADIAL, distance = R, heading = 80) #make this dynamic
        get_intercept(R = R, theta = RADIAL, course = COURSE, intercept = ANGLE) #this also plots the intercept

        draw_input_box(radial_rect, Radialtxt, Radial_active, "BFS", red)
        draw_input_box(course_rect, Coursetxt, Course_active, "CRS", purple)
        draw_input_box(angle_rect, Angletxt, Angle_active, "ANG", black)
        draw_input_box(track_rect, Tracktxt, False, "TRK", black)

        draw_plane(HEADING)

        # Update the display
        pygame.display.flip()

        

        # Cap the frame rate
        clock.tick(60)


if __name__ == "__main__":
    gameloop()


#test