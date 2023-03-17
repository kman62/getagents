
from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
from google.colab import auth
from oauth2client.client import GoogleCredentials

auth.authenticate_user()
gc = gspread.authorize(GoogleCredentials.get_application_default())

# Get the list of US cities from the US census website
url = 'https://www.census.gov/data/datasets/time-series/demo/popest/2010s-cities-and-towns.html'

# Get the page
r = requests.get(url)

# Create the soup
soup = BeautifulSoup(r.content, 'html.parser')

# Find the table with the list of cities
table = soup.find_all('table')[0]

# Create an empty list to store the cities
cities = []

# Iterate through the table and extract the cities
for row in table.find_all('tr')[1:]:
    cells = row.find_all('td')
    city = cells[0].string
    population = int(cells[3].string)
    if population > 50000:
        cities.append(city)

# Create an empty list to store the real estate agents
agents = []

# Iterate through each city and extract the top 10 real estate agents
for city in cities:
    url = 'https://www.realtor.com/realestateagents/' + city
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    for row in soup.find_all('li', {'class': 'component_agent-card'}):
        agent_name = row.find('h4', {'class': 'agent-name'}).text
        agent_phone = row.find('div', {'class': 'phone'}).text
        agent_email = row.find('a', {'class': 'email'})['href'][7:]
        agent_website = row.find('a', {'class': 'website'})['href']
        agent_reviews = row.find('div', {'class': 'reviews'}).text
        agents.append([agent_name, agent_phone, agent_email, agent_website, agent_reviews])

# Create a Pandas DataFrame
df = pd.DataFrame(agents, columns=['name', 'phone', 'email', 'website', 'reviews'])

# Export the DataFrame to a Google Sheets document
sh = gc.create('Real Estate Agents')
worksheet = gc.open('Real Estate Agents').sheet1
df.to_csv('RealEstateAgents.csv', index=False)
worksheet.set_dataframe(df, 'A1')
