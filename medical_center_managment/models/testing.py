import datetime
from pytz import timezone
d = datetime.datetime.now()
sd = d.time()
datetime.time.
v=d.replace(tzinfo=timezone('GMT'))
print(v)