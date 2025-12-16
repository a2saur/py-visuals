import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta

def get_values_by_key(dictArr, key) -> list:
    '''
    Takes in a list dictionaries and returns the values for the given key for each dictionary
    
    :param dictArr: the list of dictionaries
    :param key: the key to get the values for
    :return: the values for the key for each dictionary in the list
    :rtype: list
    '''
    arr = []
    for vals in dictArr:
        arr.append(vals[key])
    return arr

def convert_to_int(arr):
    newArr = []
    for val in arr:
        newArr.append(int(val))
    return newArr

def convert_to_date(arr):
    newArr = []
    for val in arr:
        newArr.append(datetime.fromisoformat(val))
    return newArr


file = open("./f1-data/m1208_s9078_drivers.txt", "r")
drivers = eval(file.read())
file.close()

driverPositions = {}
driverTimes = {}
for dNum in get_values_by_key(drivers, "driver_number"):
    file = open("./f1-data/m1208_s9078_d"+str(dNum)+"_positions.txt", "r")
    data = eval(file.read())
    driverPositions[dNum] = convert_to_int(get_values_by_key(data, "position"))
    driverTimes[dNum] = convert_to_date(get_values_by_key(data, "date"))
    file.close()

for dNum in get_values_by_key(drivers, "driver_number"):
    plt.scatter(driverTimes[dNum], driverPositions[dNum], label=str(dNum))

plt.savefig("temp.png")