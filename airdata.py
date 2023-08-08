
from airtable import airtable

at = airtable.Airtable('appXIFWhwVPzuREVT', 'keygZbOIcuGE438MX')
data = at.get('tweet_metrics')
print (data)
