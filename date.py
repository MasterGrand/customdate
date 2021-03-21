class Date:
    def __init__(self, date, form):
        self.form = form
        characters = {}
        for i in self.form:
            try:
                characters[i] += 1
            except KeyError:
                characters[i] = 1

        acceptedSeperators = [' ', '/', '-']
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

        
        order = [] # gets the order e.g dd/mm/yyyy or mm/dd/yyyy stores as ['m','d','y']
        for i in characters:
            if i in acceptedLetters:
                order.append(i)

        tempdate = date.split(self.seperator)
        self.date = {}
        for num, i in enumerate(order):
            self.date[i] = tempdate[num]
        print(self.date)


# 1  2  3  4  5  6  7  8  9  10  11  12
# 31 28 31 30 31 30 31 31 30 31  30  31
# if leap year then 29

class invalidFormat(Exception):
    def __init__(self, message):
        super().__init__(message)
