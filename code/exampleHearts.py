import pandas as pd
import numpy as np
import scipy.stats as ss  
import glob
import sys
import os

outdir="data/"
f2u = glob.glob(outdir + '*.csv') #files2use

fbp = [] #filter by player(s)
if len(sys.argv) > 1:
    fbp =sys.argv[1:]


# DECEMBER HEARTS LEAGUE
# I want to look in dir if there is already a rpy with the stats, if there is we want to load it.
    # https://stackoverflow.com/a/63778654
def replace(d):
    if isinstance(d, dict):
        for k in d:
            if d[k] is None:
                d[k] = []
            else:
                replace(d[k])
    elif isinstance(d, list):
        for v in d:
            replace(v)   

players = ("TK", "GB", "BS", "AK", "PB", "FC", "OB", "AB", "JK", "DB", "TK_backup")
threemanstats = dict.fromkeys(players) # dict of dict, will have players, and then all the interesting stats.
thestats = dict.fromkeys(players)
stats2record = [ "GP3", "R3", "BP3", "SM3", "TP3", "GP4", "R4", "BP4", "SM4", "TP4"]
for i in thestats:
    thestats[i] = dict.fromkeys(stats2record)
replace(thestats)

scoredict={}

for csvfichier in f2u:
    print(csvfichier)

    heartsting = pd.read_csv(csvfichier, header=None)
    heartsting= heartsting.transpose() 

    new_header = heartsting.iloc[0] #grab the first row for the header
    new_header = new_header.to_list()
    heartsting = heartsting[1:] #take the data less the header row
    heartsting.columns = new_header  #set the header row as the df header

    if len(fbp) > 0: #filterbyplayer
        if all(x in new_header for x in fbp) is False: # this bit of code means, if someone is not in your player filter, it will move onto next file.
            print("skipped")
            continue


    # checking if 3man or 4man.
    if len(new_header) == 3:
        fourppl = False
        # pts = [2,0,-1]
        bpThresh = 10
    elif len(new_header) == 4:
        fourppl = True
        # pts = [3,1,0,-2]
        bpThresh = 20
    else:
        print("Not four or three-person hearts.") # raise an error instead.


    # look at last row to determine: winners (if two people )
    finalscores=heartsting.iloc[[-1]].to_numpy()
    gameranking = ss.rankdata(finalscores)
    bonusptwnrz = np.where(finalscores <= bpThresh)[1]  # people who get bonus points
    bonusptwnrz = [new_header[i] for i in bonusptwnrz]

    for i,name in enumerate(new_header):
        if fourppl is True:
            thestats[name]["R4"].append(int(np.ceil(gameranking[i]))) # if two people come fourth, they both come fourth. if two people come second they come second.
            thestats[name]["GP4"].append(1)
        elif fourppl is False:
            thestats[name]["R3"].append(int(np.ceil(gameranking[i])))
            thestats[name]["GP3"].append(1)

    for name in bonusptwnrz:
        if fourppl is True:
            thestats[name]["BP4"].append(1)
        elif fourppl is False:
            thestats[name]["BP3"].append(1)

    for i,name in enumerate(new_header):
        if fourppl is True:
            thestats[name]["TP4"].append(finalscores[0][i]) 
        elif fourppl is False:
            thestats[name]["TP3"].append(finalscores[0][i])

    scoredict[os.path.basename(csvfichier)] = {'Players': new_header, "Scores": finalscores}

    # for i, row in heartsting.head().iterrows():
    #     print(i)
    #     if i != 1:
    #         print(heartsting.loc[i].to_numpy() - heartsting.loc[i-1].to_numpy())

    # detect STM and then add a + 1 to their stats.
    for i in range(2, len(heartsting) + 1):
        ptincrease = heartsting.loc[i].to_numpy() - heartsting.loc[i-1].to_numpy()
        if 26 in ptincrease:
            shotthemoon=new_header[np.where((ptincrease >= -5) & (ptincrease <= 0))[0][0]] # tells you who shot the moon. I am doing [0][0] because there should only be one person who shot the moon.
            if fourppl is True:
                thestats[shotthemoon]["SM4"].append(1)
            elif fourppl is False:
                thestats[shotthemoon]["SM3"].append(1)
            
        # idxSTM =  #https://stackoverflow.com/a/16343791
        # print("{} shot the moon!".format(new_header[ptincrease[np.where((ptincrease >= -5) & (ptincrease <= 0))]))

# new_header[(ptincrease >= -5) & (ptincrease <= 0)]
# for colheader in heartsting:


# Cannot do JoD stats because:
# 13 8 0 0
# could be 13 and 13 - 5
# or could be 8 and 18 - 5

# store CSV's that have been analysed in directory already, so they aren't redone.
# we want to know if it was 3-man or 4-man
# we want to know what position people came, and give them points accordingly.
# we want to store all these dictionaries and then consequently a .rpy so that can be read in.

# END results


# stats2record = ["GP", "W", "S", "T", "L", "BP", "SM", "PT"]
# after I fill this out, I then calculate the Pts.
# Pos Nme GP3 W3  S3  L3  PT3 BP3 SM3 GP4 W4  S4  T4 L4  PT4 BP4 SM4 GPt  Wt  Lt  PTt BPt SMt PPG
# 1   TK  4   3   1   0   7   1   3   10  10  0   0   0   38  8   6   14  13  0   45  9   9   3.21             
# 2   BS
# 3   GB
# 4   AK
# 5   PB

#### DO NOT LOOP BELOW#
stattbl = pd.DataFrame.from_dict(thestats) 

stattbl = stattbl.transpose()

stattbl2 = stattbl.applymap(sum)

stattbl2 = stattbl2.drop(columns=['R3', 'R4'])

tblLn = len(stattbl2)

# def weird_division(n, d):
#     return n / d if d else 0





stattbl2.insert(1, "PT3", [0] * tblLn, False)
stattbl2.insert(4, "AS3", round(stattbl2["TP3"]/ stattbl2["GP3"],2) , False)
stattbl2.insert(1, "L3", [0] * tblLn, False)
stattbl2.insert(1, "S3", [0] * tblLn, False)
stattbl2.insert(1, "W3", [0] * tblLn, False)


stattbl2.insert(10, "PT4", [0] * tblLn, False)
stattbl2.insert(13, "AS4", round(stattbl2["TP4"]/ stattbl2["GP4"],2) , False)
stattbl2.insert(10, "L4", [0] * tblLn, False)
stattbl2.insert(10, "T4", [0] * tblLn, False)
stattbl2.insert(10, "S4", [0] * tblLn, False)
stattbl2.insert(10, "W4", [0] * tblLn, False)

for index, row in stattbl.iterrows():
    stattbl2.loc[index,"W4"] = stattbl.loc[index,"R4"].count(1)# * 3
    stattbl2.loc[index,"S4"] = stattbl.loc[index,"R4"].count(2)# * 1
    stattbl2.loc[index,"T4"] = stattbl.loc[index,"R4"].count(3)# * 0
    stattbl2.loc[index,"L4"] = stattbl.loc[index,"R4"].count(4)# * -2
    stattbl2.loc[index,"W3"] = stattbl.loc[index,"R3"].count(1)# * 2
    stattbl2.loc[index,"S3"] = stattbl.loc[index,"R3"].count(2)# * 0
    stattbl2.loc[index,"L3"] = stattbl.loc[index,"R3"].count(3)# * -1


for index, row in stattbl2.iterrows():
    stattbl2.loc[index,"PT4"] = (stattbl2.loc[index,"W4"] * 3) + (stattbl2.loc[index,"S4"]) + (stattbl2.loc[index,"L4"] * -2) + (stattbl2.loc[index,"BP4"])
    stattbl2.loc[index,"PT3"] = (stattbl2.loc[index,"W3"] * 2) - (stattbl2.loc[index,"L3"]) + (stattbl2.loc[index,"BP3"])


stattbl2.insert(0, "Lt", stattbl2["L3"] + stattbl2["L4"], False)
stattbl2.insert(0, "Wt", stattbl2["W3"] + stattbl2["W4"], False)
stattbl2.insert(0, "GPt", stattbl2["GP3"] + stattbl2["GP4"], False)
stattbl2.insert(1, "ASt", round((stattbl2["TP3"] + stattbl2["TP4"]) / stattbl2["GPt"],2), False) #average points
stattbl2.insert(1, "PTt", stattbl2["PT3"] + stattbl2["PT4"], False)
stattbl2.insert(1, "PPG", round((stattbl2["PTt"] / stattbl2["GPt"]),2), False)

stattbl2 = stattbl2.replace(np.nan,0)
stattbl2 = stattbl2.drop(columns=['TP3', 'TP4'])

# sorting

# sort table by ppg
stattbl2 = stattbl2.sort_values(["PPG","ASt","PT4","AS4","PT3","AS3","GPt"], ascending = [False,True,False,True,False,True,False]) # sorts by PPG and then ties.
# move everyone with less than 5 games to the bottom of the able. https://stackoverflow.com/a/30947021
# if you have played less than 5 games, you move to bottom regardless of PPG.

move2bottomg = stattbl2["GPt"] < 5
target_rows = [i for i, x in enumerate(move2bottomg) if x] 
target_rows = move2bottomg[target_rows]
target_rows = target_rows.index
a = stattbl2.loc[[i for i in stattbl2.index if i not in target_rows], :]
b = stattbl2.loc[target_rows, :]
stattbl2 = pd.concat([a, b])


stattbl2.to_csv(outdir + "finalstats.txt") # not .csv or will be in the loop above.
np.save(outdir + "scoretable.npy", scoredict)

# f = open(outdir + "scoretable.txt","w")
# f.write( str(scoredict) )
# f.close()
# stattbl2.insert(0, "BPt", [0] * tblLn, True)
# stattbl2.insert(0, "SMt", [0] * tblLn, True)

# def div0(x,y):
#     try:
#         return x/y
#     except ZeroDivisionError:
#         return 0


#https://community.plotly.com/t/multivalue-dropdown-selected-values-color/35058/7