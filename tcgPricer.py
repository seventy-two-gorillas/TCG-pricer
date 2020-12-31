'''
This script is written to pull prices by set from tcgplayer.com
base url = https://shop.tcgplayer.com/price-guide/pokemon/

This requires current inventory to be provided as a csv input
This script uses card number and set name to look up prices (everything else is optional)
'''

from bs4 import BeautifulSoup
import requests
import os, sys
import urllib.parse as parse
import csv 
base_url = "https://shop.tcgplayer.com/price-guide/pokemon/"

def getCardDetail(card, set):
	cardDict = {}
	productDetail = card.find_all(attrs={'class':'productDetail'})[0]
	number = card.find_all(attrs={'class':'number'})[0]
	rarity = card.find_all(attrs={'class':'rarity'})[0]
	marketPrice = card.find_all(attrs={'class':'marketPrice'})[0]
	medianPrice = card.find_all(attrs={'class':'medianPrice'})[0]
	cardDict['name'] = productDetail.find('a').contents[0].strip()
	cardDict['number'] = number.find('div').contents[0].strip()
	cardDict['set'] = set
	cardDict['rarity'] = rarity.find('div').contents[0].strip()
	cardDict['market_price'] = marketPrice.find('div').contents[0].strip().replace('$','')
	cardDict['median_price'] = medianPrice.find('div').contents[0].strip().replace('$','')
	return(cardDict)



def getCards(page, set):
	cardList = []
	cards = page.find_all('tr', attrs={'class':'even'})
	for card in cards:
		cardList.append(getCardDetail(card, set))
		
	cards = page.find_all('tr', attrs={'class':'odd'})
	for card in cards:
		cardList.append(getCardDetail(card, set))
	
	return (cardList)

def readCardCsv(csvPath):
	cardInventory = []
	with open(csvPath, 'r') as f:
		reader = csv.reader(f)
		next(reader, None) #skip header row
		for line in reader:
			cardDict = {}
			cardDict['name'] = line[0]
			cardDict['number'] = line[1]
			cardDict['set'] = line[2]
			cardDict['comment'] = line[3]
			cardInventory.append(cardDict)
	return(cardInventory)
	
if __name__ == '__main__':
	#First lets get a list of cards
	if len(sys.argv) <=1:
		print ("Must provide an inventory of cards as CSV")
		sys.exit()
	csvPath = sys.argv[1]
	cardInventory = readCardCsv(csvPath)

	#now lets get a list of associated values
	cardValues = {}
	for card in cardInventory:
		if card['set'] not in cardValues.keys() and card['set'] != 'Set':
			set_url = card['set'].replace(' ','-')
			set_url = set_url.lower()
			set_url = set_url.replace('(','')
			set_url = set_url.replace(')','')
			set_url = set_url.replace(':','')
			url = parse.urljoin(base_url, set_url)
			try:
				page = requests.get(url)
				soup = BeautifulSoup(page.content, features="lxml")
				setList = getCards(soup, card['set'])
				cardValues[card['set']]=setList
			except:
				print("Unable to fetch price page from tcgplayer for set %s", card['set'])
	#print(cardValues)
	
	#Now that we have a card inventory and a list of values, lets build a value list based on the input inventory
	inventoryValue = []
	for card in cardInventory:
		cardDetail = list(filter(lambda i: i['number']==card['number'],cardValues[card['set']]))
		if cardDetail != []:
			inventoryValue.append(cardDetail[0])
		else:
			print("Unable to find card value for {} in set {}".format(card['number'], card['set']))
	#print(inventoryValue)
	
	#Create a CSV with full inventory value
	inventory_total = 0
	with open("./tcg_inventory.csv",'w', newline='') as csv_file:
		fieldNames = ['name', 'set', 'number', 'rarity', 'market_price', 'median_price']
		writer = csv.DictWriter(csv_file, fieldnames=fieldNames, dialect='excel')
		writer.writeheader()
		for card in inventoryValue:
			writer.writerow(card)
			inventory_total+=float(card['market_price'])
	
	print("\n\nUsing Market Price Data from tcgplayer.com, total inventory value is calculated as: $" + str(round(inventory_total,2)) + "\n\n")
				