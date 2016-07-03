#Written by F Lorton 2016
#https://github.com/florton
#Distribution is fine with attribution
#Just please do not sell this code or use it commercially
import sys
import math
import datetime
import urllib2
import json
import ephem  #pip install pyephem
from ephem import cities

#global vars
lastSunrise = None
lastSunset = None
nextSunrise = None
nextSunset = None
localObserver = None
todayuniversal = None
todaylocal = None
location = None

def timeToString(today):
    result = ''
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    result += days[today.weekday()]
    result += ' the ' + str(today.day) + {'11':'th','12':'th','13':'th'}.get(str(today.day)[-2:],
    {'1':'st', '2':'nd', '3':'rd'}.get(str(today.day)[-1:],'th'))
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    result += ' of ' + months[today.month-1]
    result += ' ' + str(today.year) + ' '
    postfix = ' PM' if 24 > today.hour > 11  else ' AM'
    result += str(today.hour%12) +  ':' if today.hour != 12 else '12:'
    if len(str(today.minute)) == 1:
        result += '0'
    result += str(today.minute)
    result += postfix
    return result

def getMoonPhase(today):
    Moon = ephem.Moon(today)
    condition = 'Waning' if ephem.next_full_moon(today) >= ephem.next_new_moon(today) else 'Waxing'
    quarterCondition = 'First' if condition == 'Waxing' else 'Third'
    MoonDict = {(0,0.01):'New Moon',
                (0.01, .495): condition + ' Crescent',
                (.495, .505): quarterCondition + ' Quarter',
                (.51, .99):condition + ' Gibbous',
                (.99, 1):'Full Moon'}
    for range, phase in MoonDict.iteritems():
        if range[0] <= Moon.moon_phase < range[1]:
            return phase
            
def getPlanetaryHour(today):
    hours = ['The Moon','Saturn','Jupiter','Mars','The Sun','Venus','Mercury']
    isDay = nextSunset < nextSunrise
    timeDifference = nextSunset - lastSunrise if isDay else nextSunrise - lastSunset
    currentHourDelta = ((today - lastSunrise).seconds/3600.0) if isDay else ((today - lastSunset).seconds/3600.0)
    hourLength = timeDifference.seconds/43200.0
    planetaryhour = int(currentHourDelta//hourLength)
    afterSunrise = today.hour > lastSunrise.hour or (today.hour == lastSunrise.hour and today.minute > lastSunrise.minute) 
    day = today.weekday() if afterSunrise else (today.weekday()-1)%7
    planetaryhour = (planetaryhour+(day*3))%7 if isDay else (planetaryhour+12+(day*3))%7
    return hours[planetaryhour]  
    
def getPlanetaryDay(today):
    days = ['The Moon','Mars','Mercury','Jupiter','Venus','Saturn','The Sun']
    if today.hour > lastSunrise.hour or (today.hour == lastSunrise.hour and today.minute > lastSunrise.minute):
        return days[today.weekday()] 
    else:
        return days[today.weekday()-1]

def getLocation():
        my_ip = urllib2.urlopen('http://ip.42.pl/raw').read()
        host ="http://www.geoplugin.net/json.gp?ip="+my_ip
        location = json.loads(urllib2.urlopen(host).read())
        return location

def loadDict():
    results = {}
    loadData()
    results['cheater'] = abs(todayuniversal - ephem.now().datetime()).seconds > 60
    results['city'] = location['geoplugin_city']
    results['region'] = location['geoplugin_regionName']
    results['country'] = location['geoplugin_countryName']
    results['localtime'] = todaylocal.datetime()
    results['planetaryday'] = getPlanetaryDay(todaylocal.datetime())
    results['planetaryhour'] = getPlanetaryHour(todaylocal.datetime())
    results['isday'] = nextSunset < nextSunrise
    results['nextsunrise'] = nextSunrise
    results['nextsunset'] = nextSunset
    results['moonphase'] = getMoonPhase(todaylocal)
    results['moonillumination'] = str(100*round(ephem.Moon(todaylocal).moon_phase,4))
    results['nextfull'] = ephem.localtime(ephem.next_full_moon(todayuniversal))
    results['nextnew'] = ephem.localtime(ephem.next_new_moon(todayuniversal))
    return results
    
def loadData():
    global localObserver 
    global lastSunrise
    global lastSunset
    global nextSunrise
    global nextSunset
    global todayuniversal
    global todaylocal
    global location
    todayuniversal = datetime.datetime.utcnow()
    todaylocal = ephem.Date(datetime.datetime.now())
    Sun = ephem.Sun(todaylocal)
    location = getLocation()
    city = location['geoplugin_city'] +', '+ location['geoplugin_countryName']   
    localObserver =  ephem.cities.lookup(city) 
    lastSunrise = ephem.localtime(localObserver.previous_rising(Sun))
    lastSunset = ephem.localtime(localObserver.previous_setting(Sun))
    nextSunset = ephem.localtime(localObserver.next_setting(Sun))
    nextSunrise = ephem.localtime(localObserver.next_rising(Sun))

     
def printInfo():
    #try:
        loadData()
        print ''
        print (location['geoplugin_city'] +', '+ location['geoplugin_regionName'] +', '+ location['geoplugin_countryName']).encode(sys.stdout.encoding, errors='replace')
        print timeToString(todaylocal.datetime())  
        print ''
        print "The planetary day is: " + getPlanetaryDay(todaylocal.datetime())
        print "The planetary hour is:  " + getPlanetaryHour(todaylocal.datetime())
        print ''
        print "Next sunrise at: " + timeToString(nextSunrise)
        print "Next sunset at: " + timeToString(nextSunset)
        print ''
        print "The current moon phase is: " + getMoonPhase(todaylocal) + ' ' + str(100*round(ephem.Moon(todaylocal).moon_phase,4)) + '% Full'
        print "Next Full Moon on: " + timeToString(ephem.localtime((ephem.next_full_moon(todayuniversal))))
        print "Next New Moon on: " + timeToString(ephem.localtime((ephem.next_new_moon(todayuniversal))))
        if abs(todayuniversal - ephem.now().datetime()).seconds > 60:
            print ''
            print "It looks like you changed your system clock"
    #except:
    #    print''
    #    print "Please connect to the internet for accurate planetary info"    
        
if __name__ == "__main__":
    printInfo()
    raw_input()