import re
import datetime


def main():

	#last day     YYYY/MM/DD
	SCHOOL_END = "2022/06/29".replace("/","")

	# Your year level
	YEAR = 13

	# Week A = 1, Week B = 2
	CURRENT_WEEK = 1

	# Period        1       2       3       4       6       7       8
	PERIOD_START = ["0815", "0915", "1035", "1135", "1335", "1435", "1535"]
	PERIOD_END   = ["0910", "1010", "1130", "1230", "1430", "1530", "1630"]

	# Daily events eg breaks
	DAILY = [
	#   ["start", "end", "name", "teacher", "location"]
		["0800", "0810", "Registration", "", ""], 
		["1015", "1030", "Break", "", ""], 
		["1235", "1330", "Lunch", "", ""]
	]

	STAFF = {
	#   "Last Name": "(INITIALS)"
		"Bastyan": "(DB)"
	}

	# Class name replacements
	CLASS = {
		"Super Curricular Activity": "SCA",
	}


	#default starting of ics file
	lines = """
BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Asia/Hong_Kong
TZURL:http://tzurl.org/zoneinfo-outlook/Asia/Hong_Kong
X-LIC-LOCATION:Asia/Hong_Kong
BEGIN:STANDARD
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
TZNAME:CST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
"""

	# Input data copied from isams
	week = 0
	week_a = []
	week_b = []
	while True:
		temp = input()
		if temp.startswith("Printed by"):
			break
		if temp == "":
			continue
		if "Timetable Week 1" in temp:
			week = 1
			continue
		elif "Timetable Week 2" in temp:
			week = 2
			continue
		if week == 1:
			week_a.append(temp)
		if week == 2:
			week_b.append(temp)

	week_a = [i for i in week_a[1:] if not i.startswith("Period") and "Registration" not in i and "\t" not in i]
	week_b = [i for i in week_b[1:] if not i.startswith("Period") and "Registration" not in i and "\t" not in i]

	weeks = []
	if CURRENT_WEEK == 1:
		weeks.extend([week_a, week_b])
	else:
		weeks.extend([week_b, week_a])

	#loop for Week A and B
	for week in range(2):
		data = [[[], [], [], [], [], [], []], [[], [], [], [], [], [], []], [[], [], [], [], [], [], []], [[], [], [], [], [], [], []], [[], [], [], [], [], [], []]]
		
		# converting to 2d array
		count = -1
		for line in weeks[week][1:]:
			if line.startswith(str(YEAR)):
				count += 1
				if count > 0:
					data[count%5][count//5].append(data[(count-1)%5][(count-1)//5].pop())
				else:
					data[0][0].append(weeks[week][0])
			data[count%5][count//5].append(line)

		today = datetime.date.today()
		start_day = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=week*7)

		#finding all other lessons
		for day_count in range(5):
			skip = False

			current_day = start_day + datetime.timedelta(days=day_count)
			day = str(current_day.day).zfill(2)
			month = str(current_day.month).zfill(2)
			year = str(current_day.year).zfill(4)

			for period_count in range(7):
				if skip:
					skip = False
					continue

				lesson = data[day_count][period_count][0]
				lesson = CLASS.get(lesson, lesson)
				lesson_code1 = data[day_count][period_count][1]
				start = PERIOD_START[period_count]
				end = PERIOD_END[period_count]

				if len(data[day_count][period_count]) == 3:
					if data[day_count][period_count][2].count(" ") == 0:
						teacher = ""
						location = data[day_count][period_count][2]
					else:
						teacher = data[day_count][period_count][2]
						location = ""
				else:
					teacher = data[day_count][period_count][2]
					location = data[day_count][period_count][3]

				if period_count < 6:
					lesson_code2 = data[day_count][period_count+1][1]
					if lesson_code1 == lesson_code2:
						skip = True
						end = PERIOD_END[period_count+1]

				initials = STAFF.get(teacher.split(" ")[-1], "")

				lines += f"""
BEGIN:VEVENT
DTSTART;TZID=Asia/Hong_Kong:{year}{month}{day}T{start}00
DTEND;TZID=Asia/Hong_Kong:{year}{month}{day}T{end}00
RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL={SCHOOL_END}T080000Z
SUMMARY:{lesson} {initials}
DESCRIPTION:{lesson_code1}\\n{teacher}
LOCATION:{location}
END:VEVENT
"""

			# Add registration/breaks/lunch
			for event in DAILY:
				lines += f"""
BEGIN:VEVENT
DTSTART;TZID=Asia/Hong_Kong:{year}{month}{day}T{event[0]}00
DTEND;TZID=Asia/Hong_Kong:{year}{month}{day}T{event[1]}00
RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL={SCHOOL_END}T080000Z
SUMMARY:{event[2]}
DESCRIPTION:{event[3]}
LOCATION:{event[4]}
END:VEVENT
"""

	lines += "\nEND:VCALENDAR"

	#creates ics file
	with open("Timetable.ics", "w") as ics_file:
		ics_file.writelines(lines)


if __name__ == "__main__":
	main()