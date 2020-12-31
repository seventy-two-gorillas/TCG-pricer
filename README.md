# TCG-pricer
Used to scrape www.tcgplayer.com for pokemon card values based on an input CSV.  Computes an inventory total and also generates an inventory csv containing market data that can be used for tracking over time. 

The provided CSV can be used as a template to log what cards you own.  

The card number and set name are used to fetch the data.  For set name, the naming convention should mirror whatever is used in the URL for tcgplayer.com.  Spaces will be replaced with hyphons and perenthesis and colons will be removed for you.

Detailed database will be output to ./tcg_inventory.csv

Example Call:
```python
python ./tcgPricer.py <input csv location>
```
