class Date:
    def __init__(self, date, form="dd/mm/yyyy"):
        self.form = form.lower()
        characters = {}
        for i in self.form:
            try:
                characters[i] += 1
            except KeyError:
                characters[i] = 1

        acceptedSeperators = [' ', '/', '-', '_', '.',',']
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

        self.date = {} # sets final date in order and as integers
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
        return ((28+self.isLeapYear(y))*(m==2))+(31-((m+(m<8))%2))*(m!=2)

    def isLeapYear(self, year=None):
        if year == None:
            year = int(self.date['y'])
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    # returns date type
    def __add__(self, x: int):
        if x < 0:
            return self.__sub__(abs(x))
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
        if x < 0:
            self.__rsub__(x)
        return self + x

    def __rsub__(self,x:int):
        raise invalidOperator(f"How do I remove a date from {x}, try swapping the values")

    def daysInYear(self, y=None):
        y = self.isLeapYear()
        return 365 + self.isLeapYear(y)

    def daysLeftInMonth(self,d=None, m=None):
        return self.daysInMonth() - self.date['d']

    def __iadd__(self, x):
        return self.__add__(x)

    # if passed two dates returns int, number of days between two dates
    # else if passed date and integer will return date with integer days removed from date.
    def __sub__(self, x:int):
        if isinstance(x,Date):
            if self == x:
                return 0
            if self > x:
                return x.__sub__(self)
            # x is now always larger than self here.
            # hence, always going forward
            tempdate = Date(str(self), self.form)
            d = 0
            if (self+d).date['m'] != x.date['m']: # go to last day of month
                d += self.daysLeftInMonth() + 1
            while (self+d).date['m'] != x.date['m'] and self.date['y'] == (self+d).date['y']:
                d+=(self+d).daysInMonth()
            while x.date['y'] != (self+d).date['y']:# go to year
                d+=(self+d).daysInYear()
            while x.date['m'] != (self+d).date['m']:# go to month
                d+=(self+d).daysInMonth()
            if (self+d).date['m'] == x.date['m'] and (self+d).date['y'] == x.date['y']: # go to day in final month
                d+=(x).date['d'] - (self+d).date['d']
                return d

        if x < 0:
            return self.__add__(abs(x))
        newdate = {}
        for i in self.order:
            newdate[i] = self.date[i]
        newdate['d']-=x
        while newdate['d'] < 1:
            newdate['m'] -= 1
            if newdate['m'] < 1:
                newdate['m'] = 12
                newdate['y'] -= 1
            newdate['d'] += self.daysInMonth(newdate['m'],newdate['y'])
        newdate = self.seperator.join(map(str,list(newdate.values())))
        return Date(newdate, self.form)

    def __eq__(self, x) -> bool:
        if not isinstance(x,Date):
            raise invalidOperator("Trying to compare two values that are not dates.")
        for i in ['d','m','y']:
            if self.date[i] != x.date[i]:
                return False
        return True

    def __ne__(self,x) -> bool:
        return self.__eq__(x) == 0
    
    def __le__(self,x) -> bool:
        return self.__lt__(x) or self.__eq__(x)

    def __lt__(self,x) -> bool:
        for i in ['y', 'm', 'd']:
            if self.date[i] < x.date[i]:
                return True
        return False
    
    def __gt__(self,x) -> bool:
        return self.__le__(x) == 0
    
    def __ge__(self,x) -> bool:
        return self.__lt__(x) == 0

    def __repr__(self):
        return self.seperator.join(map(str,list(self.date.values())))

class invalidFormat(Exception):
    def __init__(self, message):
        super().__init__(message)

class invalidDate(Exception):
    def __init__(self, message):
        super().__init__(message)

class invalidOperator(Exception):
    def __init__(self, message):
        super().__init__(message)
