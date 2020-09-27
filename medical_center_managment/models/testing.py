from datetime import datetime, timedelta


class DateRange:
    """."""

    def __init__(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end
        self.current_date = date_start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_date > self.date_end:
            raise StopIteration
        today = self.current_date
        self.current_date += timedelta(days=1)
        return today

# for date in DateRange(datetime(2020,10,1), datetime(2020,10,3)):
#     print(date)


class DateRangesSequenc:
    def __init__(self, date_s, date_e) -> None:
        self.date_start = date_s
        self.date_end = date_e
        self.range = self._gerenrate_range()

    def _gerenrate_range(self):
        current_date = self.date_start
        days = list()
        while current_date <= self.date_end:
            days.append(current_date)
            current_date += timedelta(days=1)
        return days

    def __getitem__(self, day_no):
        return self.range[day_no]

    def __len__(self):
        return len(self.range)


date_range_sequence = DateRangesSequenc(
    datetime(2020, 12, 12), datetime(2020, 12, 15))

for day in date_range_sequence:
    print(day)


# Containers

class Bounderies:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def __contains__(self, point):
        x, y = point
        return 0 < x < self.width and 0 < y < self.height


boundary = Bounderies(10, 10)
print((11, 3) in boundary)
