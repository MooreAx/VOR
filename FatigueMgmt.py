#Split Flight Duty implementation (CAR 700.50)

import datetime as dt

Night = (dt.time(0,0,0), dt.time(6,0,0))

B_StartTime = dt.time(16,0,0) #edit
Break = dt.timedelta(hours = 4, minutes = 0) #edit

B_Start = dt.datetime.combine(dt.date.today(),B_StartTime)
B_End = dt.datetime.combine(dt.date.today(),B_StartTime) + Break

NightStart = dt.datetime.combine(dt.date.today(), Night[0])
NightEnd = dt.datetime.combine(dt.date.today(), Night[1])

if B_Start > NightEnd:
	NightStart = NightStart + dt.timedelta(days=+1)
	NightEnd = NightEnd + dt.timedelta(days=+1)

NightBreak = max(
	dt.timedelta(seconds = 0),
	min(B_End, NightEnd) - max(B_Start, NightStart)
	)

DayBreak = Break - NightBreak

NightBreakHrs = NightBreak/dt.timedelta(hours=1)
DayBreakHrs = DayBreak / dt.timedelta(hours=1)
BreakHrs = Break / dt.timedelta(hours = 1)

if BreakHrs == 0:
	Factor = 0
else:
	Factor = max(0, BreakHrs - 0.75)/ BreakHrs

FDP_Extension_Hrs = Factor*(NightBreakHrs + 0.50 * DayBreakHrs)


if Break >= dt.timedelta(minutes = 60):
	FDP_Extension = dt.timedelta(hours = FDP_Extension_Hrs)
else:
	FDP_Extension = dt.timedelta(hours = 0)


print("Break start: ", B_Start.time())
print("Break: ", Break)
print("Day break: ", DayBreak)
print("Night break: ", NightBreak)
print("Extend FDP by: ", FDP_Extension)



