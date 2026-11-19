

Temps =[ 20,21,22,23,24,25,26,27,28,29,30]
print("Temps",Temps[0:5])
print("Temps",Temps[1])

Temps.append(31)
print("Temps",Temps)
Temps.clear()
print("Temps cleared",Temps)

keytemps= { "Nov19th":20 ,"Nov20th":21 }

print("keytemps",keytemps["Nov19th"])
print("keytemps",keytemps.get("Nov20th"))
print("values ",keytemps.values())


files=open("notes.txt","w",encoding="utf-8") 
#files.write("great ai mindset enginer")
datasets=[   " i am great coder ",
             " all is simple " ,
             "all is well ",
           ]

files.writelines( [ i + "\n" for i in datasets ] )
files.close()

files=open("notes.txt","r")
#rets=files.read()
rets=files.readlines()
print(rets,type(rets))
files.close()

'''

     venkatesh - object 
     
      Different Data 
      same variable 
      
      turnover
      teamsize
                             
      100 cr            Hardworking                      
      10                hiregoodpeople 
      
      
      Methodcalling 
      
       || venkatesh Method call 
       
       ||  input 
            outputs 
            DSA 
            Logic 
            Outcome 

'''
 
 
class TrillonDolarCompany:
    
     '''
     turnover = "100cr" # fixed
     teamsize= 10
     '''
     
     def __init__(self): # create common variables  
         self.turnover=0
         self.teamsize=0
         
     def Hardworking(self,target):
        self.turnover = target
      
     def hireteam(self,numbers):
         self.teamsize =numbers
    
     def currentgoal(self):
         print(self.turnover,self.teamsize)
         
venkatesh=TrillonDolarCompany() # create object 
venkatesh.Hardworking(100)      # method call 
venkatesh.hireteam(10)
venkatesh.currentgoal()



import pandas as pd


data = {
    "aircraft_id":      ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"],
    "model":            ["737-800", "A320neo", "787-9", "A350-900", "E195-E2", "ATR 72-600", "777-300ER", "A321XLR"],
    "manufacturer":     ["Boeing", "Airbus", "Boeing", "Airbus", "Embraer", "ATR", "Boeing", "Airbus"],
    "seats":            [189, 180, 296, 315, 146, 72, 396, 220],
    "range_km":         [5436, 6300, 14140, 15000, 4815, 1528, 13650, 8700],
    "cruise_speed_kmh": [842, 833, 903, 903, 833, 510, 892, 833],
    "fuel_burn_kg_hr":  [2530, 2100, 5400, 5800, 1700, 750, 7500, 2400],
    "year":             [2010, 2018, 2016, 2017, 2019, 2014, 2012, 2024],
}

df = pd.DataFrame(data)

pd.set_option("display.max_columns", None)   # show all columns
pd.set_option("display.width", 200)
print(df)



import pandas as pd
df = pd.read_csv("aircraft.csv", encoding="utf-8")

print(df.head(5))

print(df.head(3))
print(df.shape)     # (8, 8) -> 8 rows, 8 columns
print(df.dtypes)

import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression

df = pd.read_csv("aircraft.csv")

# ===== 1. LINEAR REGRESSION (predicts a NUMBER) =====
X = df[["seats"]]                 # INPUT  (parameter)
y = df["fuel_burn_kg_hr"]         # OUTPUT (outcome)

model = LinearRegression()
model.fit(X, y)                   # learn from data

new_input = pd.DataFrame({"seats": [250]})
prediction = model.predict(new_input)
print("Linear  | Input: 250 seats -> Output:", round(prediction[0]), "kg/hr fuel burn")

# ===== 2. LOGISTIC REGRESSION (predicts YES/NO) =====
X = df[["seats"]]                                 # INPUT  (parameter)
y = (df["range_km"] > 10000).astype(int)          # OUTPUT (1 = long-haul, 0 = not)

model = LogisticRegression()
model.fit(X, y)                   # learn from data

new_input = pd.DataFrame({"seats": [350]})
prediction = model.predict(new_input)
print("Logistic| Input: 350 seats -> Output:", "Long-haul" if prediction[0] == 1 else "Not long-haul")



# pip install pdfplumber pandas
import pdfplumber
import pandas as pd

with pdfplumber.open("flights.pdf") as pdf:
    print("Total pages:", len(pdf.pages))

    # ----- Page 1: flight briefing -----
    page1 = pdf.pages[0]
    print("\n===== PAGE 1: TEXT =====")
    print(page1.extract_text())

    fuel_table = page1.extract_table()
    fuel_df = pd.DataFrame(fuel_table[1:], columns=fuel_table[0])
    fuel_df["Fuel (kg)"] = fuel_df["Fuel (kg)"].astype(int)
    print("\n===== PAGE 1: FUEL TABLE =====")
    print(fuel_df)

    # ----- Page 2: fleet data -----
    page2 = pdf.pages[1]
    fleet_table = page2.extract_table()
    fleet_df = pd.DataFrame(fleet_table[1:], columns=fleet_table[0])

    number_cols = ["Seats", "Range km", "Speed km/h", "Fuel kg/hr", "Year"]
    fleet_df[number_cols] = fleet_df[number_cols].astype(int)

    print("\n===== PAGE 2: FLEET TABLE =====")
    print(fleet_df.to_string(index=False))

# ----- Check: does the fuel plan add up? -----
trip = fuel_df.loc[fuel_df["Item"] == "Trip fuel", "Fuel (kg)"].iloc[0]
reserve = fuel_df.loc[fuel_df["Item"] == "Reserve fuel", "Fuel (kg)"].iloc[0]
total = fuel_df.loc[fuel_df["Item"] == "Total fuel", "Fuel (kg)"].iloc[0]
print("\n===== CHECK =====")
print(f"{trip} + {reserve} = {trip + reserve} | PDF says {total} ->", "OK" if trip + reserve == total else "MISMATCH")

# ----- Save the fleet table -----
fleet_df.to_csv("fleet_from_pdf.csv", index=False, encoding="utf-8")
print("Saved fleet_from_pdf.csv")

