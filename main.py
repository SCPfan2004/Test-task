import requests
import datetime
from time import sleep

NOTION_TOKEN = "secret_8s8Niot8QDd4dWuH5DivDgGi41S389GqnFjef5V82iE"
base_id = "64c02262-1892-4ce5-9c4c-1467ae9d3047"

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_pages():

	url = f"https://api.notion.com/v1/databases/{base_id}/query"

	response = requests.post(url, headers=headers)

	data = response.json()
	a = data["results"]
	b = 0

	spisok = {}

	delta = datetime.timedelta(hours=3, minutes=0)
	today_date = str(datetime.datetime.now(datetime.timezone.utc) + delta)[0:10]
	today_time = str(datetime.datetime.now())[11:16]
	print(today_time)

	for i in a:
		# Preparing for script
		try:
			status = i["properties"]["Status"]["select"]["name"]

			if(status == "Backlog" or status == "TO DO"):
				continue
			else:
				spisok[b + 1] = i

		except Exception as ex:
			continue

		today_time = str(datetime.now())[11:16]

		b += 1

		set_date = spisok[b]["properties"]["Set date"]["date"]["start"]
		set_time = set_date[11:16]
		set_date = set_date[0:10]

		due_date = spisok[b]["properties"]["Due Date"]["date"]["start"]
		due_time = due_date[11:16]
		due_date = due_date[0:10]

		periodicity = [str(spisok[b]["properties"]["Periodicity"]["multi_select"][0]["name"])]

		try:
			periodicity.append(str(spisok[b]["properties"]["Periodicity"]["multi_select"][1]["name"]))
		except:
			pass

		if(len(periodicity) > 1):
			try:
				int(periodicity[0][0:1])
			except:
				periodicity[0], periodicity[1] = periodicity[1], periodicity[0]

			if(len(periodicity[0][3:]) > 1):
				coefficient = periodicity[0][3:][0]

				if(periodicity[0][3:][1] == "w"):
					value = 70
				elif(periodicity[0][3:][1] == "m"):
					value = 300

				output_value = int((int(coefficient) * value) / int(periodicity[0][0:1]))

			elif(len(periodicity[0][3:]) == 1):
				if(periodicity[0][3:][0] == "w"):
					value = 70
				elif(periodicity[0][3:][0] == "m"):
					value = 300

				output_value = int(value / int(periodicity[0][0:1]))

		elif(len(periodicity) == 1):
			if(periodicity[0] == "Daily"):
				output_value = 10
			else:
				if(len(periodicity[0][3:]) > 1):
					coefficient = periodicity[0][3:][0]

					if(periodicity[0][3:][1] == "w"):
						value = 70
					elif(periodicity[0][3:][1] == "m"):
						value = 300

					output_value = int(coefficient) * value

				elif(len(periodicity[0][3:]) == 1):
					if(periodicity[0][3:][0] == "w"):
						value = 70
					elif(periodicity[0][3:][0] == "m"):
						value = 300
					output_value = value

		# Script work

		set_time = (int(set_time.split(":")[0]) * 60) + int(set_time.split(":")[1])
		due_time = (int(due_time.split(":")[0]) * 60) + int(due_time.split(":")[1])

		today_time = (int(today_time.split(":")[0]) * 60) + int(today_time.split(":")[1])


		set_pdate = datetime.strptime(set_date, "%Y-%m-%d")
		today_pdate = datetime.strptime(today_date, "%Y-%m-%d")

		if(set_pdate < today_pdate):
			month = today_date[5:7]

			iterator = 1
			set_date = set_date[0:5] + month + f"-0{iterator}"

			while(set_pdate < today_pdate):
				due_time += output_value
				if(due_time // 60 >= 24):
					due_time -= 60 * 24
					iterator += 1
					set_date = set_date[0:8] + f"0{iterator}"
					set_pdate = datetime.strptime(set_date, "%Y-%m-%d")

			if(output_value == 10):
				set_time = due_time
			elif(output_value <= 300):
				set_time = due_time - 10
			elif(output_value < 600 and output_value > 300):
				set_time = due_time - 70
			elif(output_value >= 600):
				set_time = due_time - 140

		print(set_time < today_time)
		if(set_time < today_time):

			due_time += output_value
			if(due_time // 60 >= 24):
				due_time -= 60 * 24

			if(output_value == 10):
				set_time = due_time
			elif(output_value <= 300):
				set_time = due_time - 10
			elif(output_value < 600 and output_value > 300):
				set_time = due_time - 70
			elif(output_value >= 600):
				set_time = due_time - 140

			# Script end

			# Date formatting

			set_time = str(set_time // 60) + ":" + str(set_time % 60)
			if(len(set_time.split(":")[0]) == 1):
				first_piece = "0" + set_time.split(":")[0]
				second_piece = set_time.split(":")[1]
				set_time = first_piece + ":" + second_piece

			if(len(set_time.split(":")[1]) == 1):
				first_piece = set_time.split(":")[0]
				second_piece = "0" + set_time.split(":")[1]
				set_time = first_piece + ":" + second_piece

			due_time = str(due_time // 60) + ":" + str(due_time % 60)
			if(len(due_time.split(":")[0]) == 1):
				first_piece = "0" + due_time.split(":")[0]
				second_piece = due_time.split(":")[1]
				due_time = first_piece + ":" + second_piece

			if(len(due_time.split(":")[1]) == 1):
				first_piece = due_time.split(":")[0]
				second_piece = "0" + due_time.split(":")[1]
				due_time = first_piece + ":" + second_piece

			set_date = today_date + "T" + set_time + set_date[16:]
			due_date = today_date + "T" + due_time + due_date[16:]


			# Make a query

			page_id = spisok[b]["id"]

			changing_properties = {"Set date": {"date": {"start": set_date}}, "Due Date": {"date": {"start": due_date}}}
			payload = {"properties": changing_properties}
			url2 = f"https://api.notion.com/v1/pages/{page_id}"
			response = requests.patch(url2, json=payload, headers=headers)

			print(response)

		elif(set_time == today_time):
			stat = "TO DO"
			page_id = spisok[b]["id"]

			# Make a query
			changing_properties = {"Status": {"select": {"name": stat}}}
			payload = {"properties": changing_properties}
			url2 = f"https://api.notion.com/v1/pages/{page_id}"
			response = requests.patch(url2, json=payload, headers=headers)

			print(response)

o = 0
while(True):
	o += 1
	get_pages()
	print("Iter: ", o)

	sleep(60)


input("Enter...")
