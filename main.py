import requests
from bs4 import BeautifulSoup
import pandas as pd

#url = "https://www.battlemetrics.com/players/945098960"

url = input("Please type or paste the url of the battlemetrics player: ")

def get_player_name_cards_firstSeen(url):
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
  response = requests.get(url, headers=headers)

  if not response.ok:
      print('Status Code:', response.status_code)
      raise Exception('Failed to fetch')

  soup = BeautifulSoup(response.text)
  player = soup.find('div', id="PlayerPage")
  name = player.find('h1', class_="css-8uhtka").text.strip()
  name = name.replace("Overview", "")
  cards = player.find_all('div', class_='css-5ens21')

  details_div = soup.find('div', class_='col-md-4')
    
  if details_div:
      first_seen_dt = details_div.find('dt', string='First Seen')
      if first_seen_dt:
          first_seen_dd = first_seen_dt.find_next_sibling('dd')
          if first_seen_dd:
              first_seen = first_seen_dd.text.strip()
  else:
     first_seen=""
  return name, first_seen, cards

_, _, cards = get_player_name_cards_firstSeen(url)

# Function to extract the time played
def get_time_played(s):
    time_played_dt = s.find('dt', string='Time Played')
    if time_played_dt:
        time_played_dd = time_played_dt.find_next('dd')
        if time_played_dd:
            time_played = time_played_dd.find('time').text
            return time_played
    return None

# Function to extract the number from the href attribute
def get_server_number(s):
    h5_tag = s.find('h5')
    if h5_tag:
        a_tag = h5_tag.find_all('a')[1]  # The second <a> tag within <h5>
        href = a_tag.get('href')
        number = href.split('/')[-1]
        return number
    return None

server_numbers = []
for card in cards:
  # Fallback to extracting the number from the href attribute
  server_number = get_server_number(card)
  if server_number:
      server_numbers.append(server_number)
      print("Server Number:", server_number)
  print("-"*20)


# Build the query string
query_string = '?' + '&'.join([f'servers%5B{number}%5D=1M' for number in server_numbers])

# Final URL
final_url = url + query_string

print("Final URL:", final_url)

def convert_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def convert_to_hhmm(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{minutes:02d}"

def calculate_total_time_played(times):
    total_minutes = sum(convert_to_minutes(time) for time in times)
    return convert_to_hhmm(total_minutes)



# Fetch the player's name, first seen date, and cards from the URL
name, firstSeen, cards = get_player_name_cards_firstSeen(final_url)
print(name)
print("- - - - - -")
print(firstSeen)
print("- - - - - -")

# Prepare the data for the Excel file
data = {'Name': [name], 'First Seen': [firstSeen]}
times = []

for card in cards:
    title = card.find('h5').text.strip()
    print(title)
    time_played = get_time_played(card)
    if time_played:
        times.append(time_played)
        data[title] = [time_played]
        print("Time Played:", time_played)
    else:
        data[title] = ["N/A"]
        print("Something went wrong!")
    print("-"*20)

# Calculate the total time played
total_time_played = calculate_total_time_played(times)
data['Total Time Played'] = [total_time_played]
print("Total Time Played:", total_time_played)

if name:
    filename = name + ".xlsx"
else:
    filename = 'player_data.xlsx'
# Create a DataFrame and save it to an Excel file
df = pd.DataFrame(data)
df.to_excel(filename, index=False)

print("Data saved to ", filename)