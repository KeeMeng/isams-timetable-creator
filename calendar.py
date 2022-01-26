import re
import datetime


def main():
	# last day    YYYY/MM/DD
	SCHOOL_END = "2022/06/29".replace("/", "")

	# year level
	YEAR = 13

	# week a = 1, week b = 2
	CURRENT_WEEK = 2

	# whether or not to have early lunch in study period
	EARLY_LUNCH = True

	LUNCHTIME_CCA = False

	# period        1       2       3       4       5       6       7       8       cca
	PERIOD_START = ["0815", "0915", "1035", "1135", "1235", "1335", "1435", "1535", "1635"]
	PERIOD_END   = ["0910", "1010", "1130", "1230", "1330", "1430", "1530", "1630", "1730"]

	if not LUNCHTIME_CCA:
		PERIOD_START.pop(4)
		PERIOD_END.pop(4)

	# daily events eg breaks
	EXTRA = [
	#   ["start", "end", "name", "teacher", "location", [days]]
		["0730", "0755", "Breakfast", "", "", [1,2,3,4,5]], 
		["0800", "0810", "Registration", "", "", [1,2,3,4,5]], 
		["1015", "1030", "Break", "", "", [1,2,3,4,5]], 
		["1235", "1300", "Registration", "", "", [1,2,3,4,5]], 
		["1305", "1330", "Lunch", "", "", [1,2,3,4,5]], 
		["1830", "1855", "Dinner", "", "", [1,2,3,4]]
	]

	# staff name initials
	STAFF = {
	#   "Last Name": " (INITIALS)"
		"Example": " (EG)"
	}

	# class name replacements
	CLASS = {
		# "Extended Project Qualification": "EPQ",
	}

	# if games location isn't specified, set it here
	GAMES_LOCATION = ""


	# default starting of ics file
	lines = "BEGIN:VCALENDAR"
	lines += """
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
	""".replace("\t", "")

	# input data copied from isams
	week_count = 0
	week_a = []
	week_b = []
	while True:
		temp = input()
		if temp.startswith("Printed by"):
			break
		elif temp == "" or temp == "P\tMonday\tTuesday\tWednesday\tThursday\tFriday":
			continue
		elif "Timetable Week 1" in temp:
			week_count = 1
			continue
		elif "Timetable Week 2" in temp:
			week_count = 2
			continue
		elif not re.search("^(Period|P\d|After School CCA|Registration|REG)", temp) and "\t" not in temp:
			if week_count == 1:
				week_a.append(temp)
			elif week_count == 2:
				week_b.append(temp)

	weeks = []
	if CURRENT_WEEK == 1:
		weeks = [week_a, week_b]
	else:
		weeks = [week_b, week_a]

	# loop for Week A and B
	for week_count in range(2):
		data = [[[] for j in range(len(PERIOD_START))] for i in range(5)]
		
		# converting to 2d array
		line_count = 0
		block_count = 0
		cca = 0
		games = False
		for line in weeks[week_count]:
			if line_count == 0:
				if "CCA" in line:
					cca += 1
				elif cca != 0:
					block_count += 5 - cca
					cca = 0
			data[block_count%5][block_count//5].append(line)
			line_count += 1
			if "Games" in line and GAMES_LOCATION != "":
				games = True
			if line_count == 3 and games:
				line_count += 1
				data[block_count%5][block_count//5].append(GAMES_LOCATION)
				games = False
				line_count = 0
				block_count += 1
			elif line_count == 4:
				line_count = 0
				block_count += 1

		today = datetime.date.today()
		start_day = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=week_count*7)

		# adding classes
		for day_count in range(5):
			skip = False

			current_day = start_day + datetime.timedelta(days=day_count)
			day = str(current_day.day).zfill(2)
			month = str(current_day.month).zfill(2)
			year = str(current_day.year).zfill(4)

			for period_count in range(len(PERIOD_START)):
				if skip or data[day_count][period_count] == []:
					skip = False
					continue
				# if period_count == 4 and not LUNCHTIME_CCA:
				# 	continue
				lesson = data[day_count][period_count][0]
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

				if period_count < len(PERIOD_START) - 1:
					if data[day_count][period_count+1] != []:
						lesson_code2 = data[day_count][period_count+1][1]
						if lesson_code1 == lesson_code2 or ("STP" in lesson_code1 and "STP" in lesson_code2 and period_count != 3):
							skip = True
							end = PERIOD_END[period_count+1]

				initials = STAFF.get(teacher.split(" ")[-1], "")

				if "CCA" in lesson or "SCA" in lesson:
					lesson, lesson_code1 = lesson_code1, lesson

				if lesson == "Extended Project Qualification":
					location = "Sixth Form Zone"

				lesson = CLASS.get(lesson, lesson)

				if period_count == 3 and lesson == "Study Period" and EARLY_LUNCH:
					end = "1200"
					lines += f"""BEGIN:VEVENT
						DTSTART;TZID=Asia/Hong_Kong:{year}{month}{day}T120500
						DTEND;TZID=Asia/Hong_Kong:{year}{month}{day}T123000
						RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL={SCHOOL_END}T080000Z
						SUMMARY:Lunch
						END:VEVENT""".replace("\t", "")


				location = location.replace("SFZ", "Sixth Form Zone")

				lines += f"""
					BEGIN:VEVENT
					DTSTART;TZID=Asia/Hong_Kong:{year}{month}{day}T{start}00
					DTEND;TZID=Asia/Hong_Kong:{year}{month}{day}T{end}00
					RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL={SCHOOL_END}T080000Z
					SUMMARY:{lesson}{initials}
					DESCRIPTION:{lesson_code1}\\n{teacher}
					LOCATION:{location}
					END:VEVENT
				""".replace("\t", "")

			# add daily extra events
			for event in EXTRA:
				if (day_count + 1) in event[5]:
					lines += f"""
						BEGIN:VEVENT
						DTSTART;TZID=Asia/Hong_Kong:{year}{month}{day}T{event[0]}00
						DTEND;TZID=Asia/Hong_Kong:{year}{month}{day}T{event[1]}00
						RRULE:FREQ=WEEKLY;INTERVAL=2;UNTIL={SCHOOL_END}T080000Z
						SUMMARY:{event[2]}
						DESCRIPTION:{event[3]}
						LOCATION:{event[4]}
						END:VEVENT
					""".replace("\t", "")

	lines += "\nEND:VCALENDAR"

	# creates ics file
	with open("Timetable.ics", "w") as ics_file:
		ics_file.writelines(lines)


if __name__ == "__main__":
	main()
