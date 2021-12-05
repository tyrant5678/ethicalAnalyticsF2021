# This program is created to compose larger dataset using data from 2019 only from our 6 datasets
fipsMap = {}
countyFipsMap = {}
laborCSV = open('laborCSV.csv','r')
i = 0
first = True
# extract county name, state, and unemployment rate
for line in laborCSV.readlines():
    if first:
        first = False
        continue
    lineSplit = line.split(',')
    stateCty = (lineSplit[3].replace('"',""),lineSplit[4].replace('"','').replace(' ',''))
    #print(stateCty)
    # extract fips code
    ctyFips = int(lineSplit[1]+lineSplit[2].zfill(3))
    # print(ctyFips)
    countyFipsMap[(stateCty[0].lower(), stateCty[1])] = ctyFips
    # add FIPS code, state-city tuple, and unemployment rate to the county arrays
    fipsMap[ctyFips] = [ctyFips, stateCty]
    # if no value given, we will just append the N.A., otherwise append unempployment
    try:
        fipsMap[ctyFips].append(float(lineSplit[-1]))
    except:
        fipsMap[ctyFips].append("N.A.")
    i += 1
laborCSV.close()
# extract educational categories
education = open('educationTSV.txt','r')
i = 0
first = True
for eduline in education.readlines():
    if first:
        first = False
        continue
    lineSplit = eduline.split('\t')
    # this line skips the county/country summary lines
    if lineSplit[3] != '':
        # this will drop values not found in the labor data, but that's ok because we only care about areas for which we have ALL data atm
        try:
            # grab 2015-2019 vals
            ctyFips = int(lineSplit[0])
            fipsMap[ctyFips].append(float(lineSplit[43]))
            fipsMap[ctyFips].append(float(lineSplit[44]))
            fipsMap[ctyFips].append(float(lineSplit[45]))
            fipsMap[ctyFips].append(float(lineSplit[46]))
        except:
            # do nothing if the try fails
            pass
education.close()
# extract 2019 population estimates (for use in calculating crime rates)
population = open('population.csv','r')
i = 0
first = True
for line in population.readlines():
    if first:
        first = False
        continue
    lineSplit = line.split(',')
    if lineSplit[4] == "000":
        continue
    # grab pop count for this county and try adding it to our fips map, if it doesn't exist there, toss it for now
    popest2019 = int(lineSplit[18])
    try:
        ctyFips = int(lineSplit[3]+lineSplit[4])
        fipsMap[ctyFips].append(popest2019)
    except:
        pass
population.close()
# extract violent crime counts, use to create a violent crime rate later
crime = open('reportedCrimeData.tsv','r')
i = 0
first = True
for line in crime.readlines():
    if first:
        first = False
        continue
    lineSplit = line.split('\t')
    ctyFips = int(lineSplit[4]+lineSplit[5].zfill(3))
    violCrime = lineSplit[11]
    try:
        fipsMap[ctyFips].append(int(violCrime))
    except:
        pass
crime.close()
# extract health data
health = open('health2019.csv','r')
first = True
i = 0
for line in health.readlines():
    if first:
        first = False
        continue
    lineSplit = line.split(',')
    ctyFips = int(lineSplit[0])
    # 14 18
    physUn = float(lineSplit[14])
    mentUn = float(lineSplit[18])
    print(lineSplit[-23])
    airQual = ('No data')
    numAssoc = int(lineSplit[-34])
    sevHous = int(lineSplit[-19])
    try:
        airQual = float(lineSplit[-23])
    except:
        pass
    try:
        fipsMap[ctyFips].append(physUn)
        fipsMap[ctyFips].append(mentUn)
        fipsMap[ctyFips].append(airQual)
        fipsMap[ctyFips].append(numAssoc)
        fipsMap[ctyFips].append(sevHous)
    except:
        pass
    i+=1
health.close()
# extract GPD
gdp = open('gdpCSV.csv','r')
first = True
i = 0
currState = ''
comb = False
# print(countyFipsMap)
for line in gdp.readlines():
    if first:
        first = False
        continue
    if i == 5:
        break
    lineSplit = line.split(',')
    # print(lineSplit)
    # hard code the DC case
    if lineSplit[0] == 'DC':
        fipsMap[11001].append(float(lineSplit[4].replace('"','').replace(',','')))
    elif lineSplit[-1] == '--\n':
        currState = lineSplit[0]
        comb = False
        continue
    elif lineSplit[0] == 'Combination areas1':
        # print("hi")
        comb = True
    else:
        # this deals with virginia's wacky combination areas
        if comb:
            locales = lineSplit[0].replace('"','').split(' + ')
            for locale in locales:
                if not ('city' in locale):
                    pair = (locale.lower()+' county', 'VA')
                else:
                    pair = (locale.lower(), 'VA')
                fipsMap[countyFipsMap[pair]].append(float(lineSplit[4].replace('"','').replace(',','')))
        else:
            try:
                if currState == 'LA':
                    pair = (lineSplit[0].lower()+' parish', currState)
                else:
                    pair = (lineSplit[0].lower()+' county', currState)
                    # print(pair)
                fipsMap[countyFipsMap[pair]].append(float(lineSplit[4].replace('"','').replace(',','')))
            except:
                pair = (lineSplit[0].lower(), currState)
                fipsMap[countyFipsMap[pair]].append(float(lineSplit[4].replace('"','').replace(',','')))
    # i += 1
gdp.close()
data = [['FIPS','(CTY,ST)','%UNEMPLOYED','%LESSHS','%HS','%SOMECOLL','%COLLEGEHIGHER','POPEST2019','VIOLCRIMECT','AVG_PHYS_UNHEALTHY_DAYS','AVG_MENT_UNHEALTHY_DAYS','AVG_DAILY_PM25','NUM_ASSOC','RGDP2019']]
for key in fipsMap:
    if len(fipsMap[key]) == 15:
        data.append(fipsMap[key])
# print(data)
data_out = open('clean_data.txt','w')
for point in data:
    for j in range(len(point)):
        point[j] = str(point[j])
    s = '\t'.join(point)

    data_out.write(s+'\n')
data_out.close()