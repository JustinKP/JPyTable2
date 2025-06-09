import copy, math, os, time, re, csv


### Spreadsheet modifiers
def spreadsheetAddColumns(columnsRequested: int):
    try:
        if len(spreadsheet) == 0:
            rows = 1
        else:
            rows = len(spreadsheet[0])
        
        for i in range(columnsRequested):
            spreadsheet.append([""]*rows)
        res = columnsRequested
    except:
        res = None
    
    return res

def spreadsheetDelColumns(columnsRequested: int):
    try:
        for i in range(columnsRequested):
            spreadsheet.pop()
        res = columnsRequested
    except:
        res = None
    
    return res

def spreadsheetSetColumns(columnsRequested: int):
    if columnsRequested < 0:
        return None
    if spreadsheet:
        columns = len(spreadsheet)
    else:
        columns = 0
    columnsRemoved = columns - columnsRequested
    if columnsRemoved > 0:       #if we need to remove columns
        return spreadsheetDelColumns(columnsRemoved)
    elif columnsRemoved == 0:
        return columnsRemoved
    else: #columnsRemoved < 0    #if we need to add columns
        return spreadsheetAddColumns(-(columnsRemoved))

def spreadsheetAddRows(rowsRequested: int):
    try:
        if len(spreadsheet) == 0:
            spreadsheetAddColumns(1)
            rowsRequested -= 1 #adding 1 column already adds 1 row
        
        for column in range(len(spreadsheet)): #finds each column
            for i in range(rowsRequested): #appends for x times
                spreadsheet[column].append("")
        res = rowsRequested
    except:
        res = None
    
    return res

def spreadsheetDelRows(rowsRequested: int):
    global spreadsheet
    try:
        if rowsRequested >= len(spreadsheet[0]): #req >= rows, if would empty spreadsheet
            spreadsheet = []
        
        for column in range(len(spreadsheet)): #finds each column
            for i in range(rowsRequested): #appends for x times
                spreadsheet[column].pop()
        res = rowsRequested
    except:
        res = None
    
    return res

def spreadsheetSetRows(rowsRequested: int):
    if rowsRequested < 0:
        return None
    if spreadsheet[0]:
        rows = len(spreadsheet[0])
    else:
        rows = 0
    rowsRemoved = rows - rowsRequested
    if rowsRemoved > 0:       #if we need to remove columns
        return spreadsheetDelRows(rowsRemoved)
    elif rowsRemoved == 0:
        return rowsRemoved
    else: #rowsRemoved < 0    #if we need to add columns
        return spreadsheetAddRows(-(rowsRemoved))

def editSpreadsheet(label, func, responseText):
    request = input(label)
    if not request.isdigit():
        return request+" is not a valid number, no changes were made."
    else:
        response = func(int(request))
        if response:
            return str(response)+" "+responseText
        else:
            return "Invalid Request"


#Data modifiers
def getSpreadsheetString(spreadsheet: list, cellLengthMaxOverride = False):
    if not spreadsheet:
        return "No spreadsheet data found!"
    #else,
    
    try:
        spreadsheetDisplay = copy.deepcopy(spreadsheet)
        
        ###Varaible calculation
        cols = len(spreadsheetDisplay)
        rows = len(spreadsheetDisplay[0])
        
        
        def cellFunctionResolver(cell: str, column=None, row=None, cellInit=None, iteration=0):
            if not cell:
                return cell
            if type(cell) != str:
                cell = str(cell)
            if cell[0]== "=":
                cell = cell[1:]
            if not cellInit: #assign cellInit 
                cellInit = cell
            
            def splitter(string, seperator):
                a,b = string.split(seperator)
                #We also have function resolution recursion within aspects of functions like this
                a = cellFunctionResolver(a,
                                        #column,row
                                        )
                b = cellFunctionResolver(b,
                                        #column,row
                                        )
                try:
                    a = float(a)
                    b = float(b)
                    return a,b
                except:
                    return None,None
            
            #(=)SUMROW1:3
            if cell[:3].upper() == "SUM":
                def sumCalc(forColumn = True):
                    if cell[6:]:
                        cellDimStart, cellDimEnd = splitter(cell[6:], ":")
                    else:
                        cellDimStart = 0
                        if forColumn:
                            cellDimEnd = rows
                        else:
                            cellDimEnd = cols
                    if cellDimEnd and cellDimEnd == int(cellDimEnd): #can't be start in case of cellRowStart
                        numList = []
                        for cellSelectDim in range(int(cellDimStart)-1,int(cellDimEnd)):
                            if forColumn:
                                cellSelect = cellFunctionResolver(spreadsheetDisplay[column][cellSelectDim],column,cellSelectDim)
                            else:
                                cellSelect = cellFunctionResolver(spreadsheetDisplay[cellSelectDim][row],cellSelectDim,row)
                            try:
                                numList.append(float(cellSelect))
                            except:
                                return "!SUM-ALPHA"
                        return math.fsum(numList)
                    else:
                        return "!SUM-BADCD"
                match cell[3:6].upper():
                    case "COL" | "COLUMN":
                        return sumCalc(forColumn = True)
                    case "ROW":
                        return sumCalc(forColumn = False)
                    case _: #means improperly formatted, don't parse
                        return cell
            
            while True: #Brackets resolution
                bracketIndex1 = cell.find("(")
                bracketIndex2 = cell.find(")")
                if bracketIndex1 > -1 and bracketIndex1 < bracketIndex2:
                    x = cellFunctionResolver(cell[bracketIndex1+1:bracketIndex2],column,row)
                    cell = cell[:bracketIndex1]+str(x)+cell[bracketIndex2+1:] #the plus one gets rid of the brackets
                else:
                    break
            
            if cell.count(":") == 1: #Assign
                cellRefCol, cellRefRow = splitter(cell, ":")
                if cellRefCol and cellRefCol == int(cellRefCol):
                    if cellRefCol <= cols and cellRefRow <= rows: #if valid request
                        iteration += 1
                        if iteration >= (cols*rows):
                            return "!RECUR-REF"
                        else:
                            return cellFunctionResolver(spreadsheetDisplay[int(cellRefCol)-1][int(cellRefRow)-1],
                                                        #column,row,
                                                        cellInit=cellInit,iteration=iteration) #get value (checked for function) at those coords
                    else:
                        return "!RANGE-REF"
                #else: if invalid don't do anything
            elif cell.count("/") == 1: #Divide
                a,b = splitter(cell, "/")
                if a: 
                    if b>0: return a/b
                    else:   return "!DIV-0-ERR"
            elif cell.count("*") == 1: #Multiply
                a,b = splitter(cell, "*")
                if a: return a*b
            elif cell.count("+") == 1: #Add '20.0+5.0+' '20.0+5.0+5'
                a,b = splitter(cell, "+")
                if a: return a+b
            elif cell.count("-") == 1: #Subtract
                a,b = splitter(cell, "-")
                if a: return a-b
            # elif (cell.count("/")+cell.count("*")+cell.count("+")+cell.count("-")) > (-1+-1+-1+-1):
            
            return cell
            #READABILITY#SEPERATOR#####################################################################################################################################
        
        
        rowLengthMax = len(str(rows))
        if rowLengthMax == 1: #default makes single digits always have a leading 0
            rowLengthMax = 2
        
        #Calculates max length of each cell using the remaining text space
        def getColumnsMax():
            try:
                maxColumns = str(os.get_terminal_size()) #saves maxColumns as the string that shows the terminal size.
                return int(maxColumns[maxColumns.index("columns=") + len("columns="):maxColumns.index(", line")]) #isolates the string that is the max num of columns in the terminal.
            except:
                return 238 
        if cellLengthMaxOverride: 
            cellLengthMax = None
        else:
            cellLengthMax = int((getColumnsMax()-rowLengthMax)/cols)-1 #AKA -len(" ")   
        
        
        ###Varaible calculation AND Function resolution!
        #Calculates min length of each cell using the length of the largest value
        cellLengthMin = len(str(cols+1)) #minimum length minimum, set to fit largest colomn label
        for column in range(cols): #for each column:
            for row in range(rows): #and each row:
                cell = str(spreadsheetDisplay[column][row])
                
                if len(cell) > 3 and cell[0] == "=":
                    cellResolved = str(cellFunctionResolver(cell[1:],column,row))       #resolves cell function if exists
                    if ("="+cellResolved) != cell:                      #if cell had function
                        spreadsheetDisplay[column][row] = cellResolved  #save table cell as resolved cell
                        cell = cellResolved                             #save cell var (for length) as resolved cell as well
                
                lengthMinPotential = len(str(cell)) #saves the canidate for the minLength.
                if cellLengthMin < lengthMinPotential: #if it's the longest string so far:
                    cellLengthMin = lengthMinPotential #save the length as the min.
        del cell, lengthMinPotential
        if cellLengthMax and cellLengthMin > cellLengthMax:
            cellLengthMin = cellLengthMax
        
        def getPadding(padding: str, length: int, text: str):
            if not text: text = ""
            return padding*(length-len(text))
        
        
        
        ###Column label constructor
        colLabel = rowLengthMax*"-"
        for col in range(cols): #for each column in that row (x)
            colString = str(col+1)
            if len(colString) > cellLengthMin: #shortens the column string if the space can be used
                colString = colString[len(colString)-cellLengthMin:]
            colLabel += "-" + getPadding("-",cellLengthMin,colString) + colString
        spreadsheetString = colLabel
        del colString, colLabel
        
        
        
        ###Row label and Cell constructor
        for row in range(rows): #for each row (y)
            #build the row marker by adding leading 0s to match length of largest row text length, then add row text
            rowString = str(row+1)
            rowLabel = getPadding("0",rowLengthMax,rowString) + rowString
            
            rowCells = ""
            for col in range(cols): #for each column in that row (x)            
                cellValue = str(spreadsheetDisplay[col][row])[:cellLengthMax] #add value to currentLine
                rowCells += " "+getPadding(" ",cellLengthMin,cellValue)+cellValue

            spreadsheetString += "\n"+rowLabel+rowCells
        del rowString, rowLabel, rowCells
        
        
        return spreadsheetString
    except:
        return "Unknown Error"
    #READABILITY#SEPERATOR#####################################################################################################################################

def pivotTable(table):
    #THANK YOU Paul Kenjora
    #Pivots 2D list by flipping data stored at X:Y to Y:X
    pivotedData = []
    for row in table:
        for column, cell in enumerate(row):
            if len(pivotedData) == column: pivotedData.append([])
            pivotedData[column].append(cell)
    return pivotedData

def timestampify(filename: str, extention: str):
    #This all assumes the timestamp is being saved at the end of the filename
    timestamp = " "+time.strftime("%Y-%m-%d_%H-%M-%S")+extention
    def isTimestamp(timestampCandidate):
        return re.match(r" [0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}.[a-z]{3}", timestampCandidate) #extention needs to match when saving
    timestampStartPos = len(filename)-len(timestamp) #index of when timestamp starts
    
    if isTimestamp(filename[timestampStartPos:]):            #if filename has timestamp
        for dir in os.listdir():                                        #check each file in folder
            if dir[:timestampStartPos] == filename[:timestampStartPos]: #if filenames match
                if isTimestamp(dir[timestampStartPos:]):     #and actually has real timestamp
                    filename = filename[:timestampStartPos]             #remove old timestamp from filename
                    break
    return filename+timestamp

def validFilename(filename):
    if filename.count("\\") or filename.count("/") or filename.count(":") or filename.count("*") or filename.count("\"") or filename.count("<") or filename.count(">") or filename.count("|"):
        print("File name contains invalid character(s), please try again."+"\n")
        return False
    else:
        return True


#Frequently used text
def clearAndIntro(filename = "", displayHelp = False):
    #Clear function
    if os.name == 'nt': _ = os.system('cls') # for windows
    else: _ = os.system('clear') # for mac and linux(here, os.name is 'posix')
    
    if filename:
        filename = " - "+filename
    print("JPyTable2"+filename+" (Justin Pimentel, 2025)")
    if displayHelp:
        print("Input \"help\" to view manual"+"\n")

while True:
    ###Open or create new spreadsheet
    spreadsheet = []
    clearAndIntro()
    print("CSVs in this directory:")
    for dir in os.listdir():
        if dir.endswith(".csv"):
            print(dir)
    print()
    print("Type \"New\" to create a new spreadsheet or provide the name of the CSV file you'd like to open:")
    while True:
        filename = input()
        if validFilename(filename):
            if filename.upper() == "NEW":
                filenameIsValid = False
                while not filenameIsValid:
                    filename = input("\n"+"New spreadsheet name: ")
                    filenameIsValid = validFilename(filename)
                print()
                spreadsheetAddColumns(columnsRequested=12)
                spreadsheetAddRows(rowsRequested=12-1)
                break
            else:
                if not filename.lower().count(".csv"):
                    filename += ".csv"
                try:
                    with open(filename, newline='') as file:
                        for row in csv.reader(file):
                            spreadsheet.append(row)

                        spreadsheet = pivotTable(spreadsheet) #flips X and Y so they match up between file and software, then saves as spreadsheet
                        break
                except:
                    print("File not found, please try again."+"\n")


    #Refresh actions
    refreshDisplay = True
    cellValue = ""
    output = ""
    
    ###Edit spreadsheet
    while True:
        ###Display result:      (this is implemented weird but it reuses code well)
        if refreshDisplay:      clearAndIntro(filename, displayHelp=True)
        if cellValue:           print("Input:  "+selection+" <- "+cellValue)
        if output:              print("Output: "+output) #if request has a response
        if cellValue or output: print()
        if refreshDisplay:  
            print(getSpreadsheetString(spreadsheet)+"\n")
        
        #Refresh variables
        refreshDisplay = True
        cellValue = ""
        output = ""
        
        ###Get request:
        selection = input("Select: ").upper()
        match selection:
            # Display
            case "HELP": 
                try:
                    with open("JPyTable2 Manual.txt", "r") as file:
                        print("\n"+file.read()+"\n")
                except:
                    output = "ERROR: Manual read error, file may not exist or be in same directory"
                refreshDisplay = False
            case "" | "CLER" | "CLEAR" | "RELOAD" | "REFRESH" | "DISPLAY": #signals to display refresh mode
                output = None 
            case "RENM" | "RENAME" | "NAME":
                newFilename = input("\n"+"Spreadsheet name: ")
                if validFilename(newFilename):
                    filename = newFilename
                del newFilename
            case "EXIT": break #Leaves selected spreadsheet and returns to spreadsheet selection.
            # Table format
            case "+COL" | "+COLS" | "+COLUMN" | "+COLUMNS":         output = editSpreadsheet("Columns:", spreadsheetAddColumns, "Columns Added")
            case "-COL" | "-COLS" | "-COLUMN" | "-COLUMNS":         output = editSpreadsheet("Columns:", spreadsheetDelColumns, "Columns Removed")
            case "=COL" | "=COLS" | "=COLUMN" | "=COLUMNS":         output = editSpreadsheet("Columns:", spreadsheetSetColumns, "Columns Set")
            case "+ROW" | "+ROWS":                                  output = editSpreadsheet("Rows:   ", spreadsheetAddRows, "Rows Added")
            case "-ROW" | "-ROWS":                                  output = editSpreadsheet("Rows:   ", spreadsheetDelRows, "Rows Removed")
            case "=ROW" | "=ROWS":                                  output = editSpreadsheet("Rows:   ", spreadsheetSetRows, "Rows Set")
            # Save table to file
            case "SAVE":
                filename = timestampify(filename, ".csv")
                with open(filename, 'w', newline='') as file:
                    write = csv.writer(file)
                    write.writerows(pivotTable(spreadsheet)) #writes rotated spreadsheet to match actual and expected x and y
                output = "File backup saved to "+filename
                refreshDisplay = False
            case "PRNT" | "PRINT":
                filename = timestampify(filename, ".txt")
                with open(filename, 'w') as file:
                    file.write(getSpreadsheetString(spreadsheet, cellLengthMaxOverride=True))
                output = "File printed to "+filename
                refreshDisplay = False
            # Input using coords or discard selection
            case _:
                errorMessage = ""
                if not spreadsheet:                 #Check spreadsheet
                    errorMessage = "Cannot input values into undefined spreadsheet"
                else:
                    coordsStr = selection.replace(",",":").replace(";",":")
                    if coordsStr.count(":") != 1:   #Check formatting
                        errorMessage = "Coordinates must have only one seperator [:] between X and Y"
                    else:
                        x, y = coordsStr.split(":") #Get coords
                        try:                        #Check coord numbers
                            x = int(x)
                            y = int(y)
                        except:
                            errorMessage = "Coordinates must be whole numbers."
                        if not errorMessage:        #Check table dimentions
                            if x > len(spreadsheet) or y > len(spreadsheet[0]):
                                errorMessage = "Coordinates outside of bounds of table."
                            else:                   #Assign value to cell
                                #convert to base 0 unless user is using negative numbers to wrap around
                                if x > 0: x-=1
                                if y > 0: y-=1
                                cellValue = input("Value:  ") #save cellValue for future display
                                spreadsheet[x][y] = cellValue
                if errorMessage:
                    output = "Invalid command or invalid coordinates ("+errorMessage+")"
                    refreshDisplay = False