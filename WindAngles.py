import sys
import math
import numpy as np

def to_vector(v, theta):
	vx = math.sin(math.radians(theta))
	vy = math.cos(math.radians(theta))
	vect = v * np.array([vx, vy])

	return(vect)

def get_norm(v):
	return(np.linalg.norm(v))

def get_angle(v):
	#atan2(x,y) returns angle from x axis. We want angle from y axis. Therefore, swap args: atan2(x,y) --> atan2(y,x)
	return(math.degrees(math.atan2(v[0], v[1])) % 360)

def wind_correction_vectors(wind, trk, tas):
	wind_speed = get_norm(wind)
	wind_angle = get_angle(wind)

	hdg = trk - math.degrees(math.asin((wind_speed * math.sin(math.radians(wind_angle - trk)) / tas)))

	air = to_vector(tas, hdg)
	gnd = air + wind

	return [air, gnd]


# CRITICAL POINT / EQUAL TIME CALCULATIONS:

wind_vel = -to_vector(v = 30, theta = 90) #minus sign b/c wind points towards the origin

total_distance = 1000

TRK_out = 360
TRK_in = TRK_out + 180 % 360

TAS_2engines = 200
TAS_1engine = 150

#compute outbound, 2 engines
[air_vel_out_2e, gnd_vel_out_2e] = wind_correction_vectors(wind_vel, TRK_out, TAS_2engines)

#compute outbound, 1 engine
[air_vel_out_1e, gnd_vel_out_1e] = wind_correction_vectors(wind_vel, TRK_out, TAS_1engine)

#compute inbound, 1 engine
[air_vel_in_1e, gnd_vel_in_1e] = wind_correction_vectors(wind_vel, TRK_in, TAS_1engine)

gnd_speed_out_1e = get_norm(gnd_vel_out_1e)
print("G/S outbound, 1 engine: ", round(gnd_speed_out_1e, 1))

gnd_speed_in_1e = get_norm(gnd_vel_in_1e)
print("G/S home, 1 engine: ", round(gnd_speed_in_1e, 1))

#does the average ground speed equal the TAS? NO
gnd_speed_1e = (gnd_speed_in_1e + gnd_speed_out_1e)/2
print("Avg G/S, 1 engine", gnd_speed_1e)
print("Avg G/S, 1 engine less TAS_1engine =", gnd_speed_1e - TAS_1engine)

gnd_speed_out_2e = get_norm(gnd_vel_out_2e)
print("G/S outbound, 2 engines: ", round(gnd_speed_out_2e, 1))

CP_outbound = total_distance * gnd_speed_in_1e / (gnd_speed_in_1e + gnd_speed_out_1e)
print("Critical Point (distance): ", round(CP_outbound, 1))

def hours_to_hhmmss(decimal_hours):
    hours = int(decimal_hours)
    minutes = int((decimal_hours - hours) * 60)
    seconds = round(((decimal_hours - hours) * 60 - minutes) * 60)
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

time_to_cp_2e = CP_outbound / gnd_speed_out_2e
print("Time to CP on 2 engines: ", hours_to_hhmmss(time_to_cp_2e))

time_in_1e = CP_outbound / gnd_speed_in_1e
print("Time from CP to home on 1 engine: ", hours_to_hhmmss(time_in_1e))

time_in_1e = (total_distance - CP_outbound) / gnd_speed_out_1e
print("Time from CP to destination on 1 engine: ", hours_to_hhmmss(time_in_1e))


