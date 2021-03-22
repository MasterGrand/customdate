class Date:
    def __init__(self, date, form="dd/mm/yyyy"):
        self.form = form.lower()
        characters = {}
        for i in self.form:
            try:
                characters[i] += 1
            except KeyError:
                characters[i] = 1

        acceptedSeperators = [' ', '/', '-', '_', '.']
        acceptedLetters = ['d', 'm', 'y']
        for i in self.form:
            if i not in acceptedSeperators and i not in acceptedLetters:
                raise invalidFormat(f"Unexpected charcter in format '{i}' ({self.form})")
        found = False
        c = 0

        maxSeperators = 2
        minSeperators = 2

        for i in acceptedSeperators:
            try:
                c += characters[i]
                if found:
                    raise invalidFormat(f"Mismatched seperators, '{self.form}'")
                if c > maxSeperators:
                    raise invalidFormat(f"Too many seperators, got {c}. (max: {maxSeperators})")
                found = True
                self.seperator = i
            except KeyError:
                pass
        if c < minSeperators:
            raise invalidFormat(f'Too few seperators, got {c}. (min: {minSeperators})')

        minmaxs = {
            "ymin": 2,
            "ymax": 4,
            "dmin": 1,
            "dmax": 2,
            "mmin": 1,
            "mmax": 2
        }

        for i in acceptedLetters:
            try:
                if minmaxs[i + 'max'] < characters[i] or minmaxs[i + 'min'] > characters[i]:
                    raise invalidFormat(f"Invalid number of indicators ('{i}'), got {characters[i]}. (Required: {minmaxs[i + 'min']}-{minmaxs[i + 'max']})")
            except KeyError:
                raise invalidFormat(f"Missing indicator from format, '{i}'.")

        let = ""
        for num, i in enumerate(self.form): # validate that all letters are clustered together
            if i in acceptedLetters: # current checking is an accepted letter
                if let in acceptedLetters: # if previous letter is an accepted letter
                    if let == i:
                        continue
                    else:
                        raise invalidFormat(f"Mismatched indicator near indexed position {num}")
            else:
                if num == 0 or num == len(self.form) - 1:
                    raise invalidFormat(f"Invalid starting/ending character, '{i}' must be d,m or y.")
            let = i

        
        self.order = [] # gets the order e.g dd/mm/yyyy or mm/dd/yyyy stores as ['m','d','y']
        for i in characters:
            if i in acceptedLetters:
                self.order.append(i)

        tempdate = date.split(self.seperator)

        if len(tempdate) - 1 > maxSeperators or len(tempdate) - 1 < minSeperators:
            raise invalidDate("The seperator of the format does not match given in date.")

        self.date = {}
        for num, i in enumerate(self.order):
            self.date[i] = int(tempdate[num])

        # days will be lenient but years will be strict.
        for i, d in enumerate(self.date.values()):
            if self.order[i] == "m":
                if d > 12 or d < 1:
                    raise invalidDate(f"Month is invalid, got {d}. (1-12)")
            elif self.order[i] == 'y':
                if d < 1 or d > 9999:
                    raise invalidDate(f"Year is invalid, got {d}. (1-9999)")
            elif self.order[i] == 'd':
                if d < 1 or d > self.daysInMonth():
                    raise invalidDate(f"Date is invalid, got {d}. (1-{self.daysInMonth()} for that month)")

    def daysInMonth(self, m=None, y=None):
        if m==None:
            m = int(self.date['m'])
        l = self.isLeapYear()
        if y!=None:
            l = self.isLeapYear(y)
        return ((28+l)*(m==2))+(31-((m+(m<8))%2))*(m!=2)

    def isLeapYear(self, year=None):
        if year == None:
            year = int(self.date['y'])
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def __add__(self, x: int):
        newdate = {}
        for i in self.order:
            newdate[i] = self.date[i]

        newdate['d'] += x
        while newdate['d'] > self.daysInMonth(newdate['m'],newdate['y']):
            newdate['d'] -= self.daysInMonth(newdate['m'],newdate['y'])
            newdate['m'] += 1
            if newdate['m'] > 12:
                newdate['m'] = 1
                newdate['y'] += 1
            

        newdate = self.seperator.join(map(str,list(newdate.values())))
        return Date(newdate, self.form)
    
    def __radd__(self, x: int):
        return self + x

    def __repr__(self):
        return self.seperator.join(map(str,list(self.date.values())))

# 1  2  3  4  5  6  7  8  9  10  11  12
# 31 28 31 30 31 30 31 31 30 31  30  31
# if leap year then 29

class invalidFormat(Exception):
    def __init__(self, message):
        super().__init__(message)

class invalidDate(Exception):
    def __init__(self, message):
        super().__init__(message)
