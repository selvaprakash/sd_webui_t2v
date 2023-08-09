
from airtable import airtable

at = airtable.Airtable('', '')
data = at.get('tweet_metrics')
print (data)
