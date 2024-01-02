#!/usr/bin/env python3


import os
import sys
import io
import random
import webbrowser


import cfg

myRobloSecurityKey = cfg.settings["SecurityKey"]

#print(cfg.settings["SkipStarterPlaces"])
#print(cfg.settings["SkipR15Only"])

settings = {
    "SkipStarterPlaces": cfg.settings["SkipStarterPlaces"],
    "SkipPrivatePlaces": cfg.settings["SkipPrivatePlaces"],
    "ViewPlaceInWebBrowser": cfg.settings["ViewPlaceInWebBrowser"],
}



sys.path.append("../include")
import requests



def findValidPlace():
    
    searchFailed = False
    placeID = createPlaceID()

    session = requests.Session()
    cookies = {'.ROBLOSECURITY': myRobloSecurityKey}
    

    print("Connecting to Universes API...")
    print("https://apis.roblox.com/universes/v1/places/" + str(placeID) + "/universe")


    getUniverseID = requests.get("https://apis.roblox.com/universes/v1/places/" + str(placeID) + "/universe").json()
    universeID = getUniverseID["universeId"]

    if universeID == None:
        print("\nItem for ID is not a place.") # No universe ID = not a place.
        searchFailed = True


    if not searchFailed:
        print("Connecting to Games API...")
        params = {'universeIds': universeID}
        getPlaceInfo = requests.get("https://games.roblox.com/v1/games", params=params, cookies=cookies)
        

        if (getPlaceInfo.status_code != 200):
            searchFailed = True
            print("\nError " + str(getPlaceInfo.status_code)) 
        else:

            if not searchFailed:

                pInfo = getPlaceInfo.json()

                if len(pInfo) != 0:
                    
                    placeName = pInfo["data"][0]["name"]

                    if settings["SkipStarterPlaces"]:
                        if placeName.endswith("'s Place"):
                            searchFailed = True


                    if settings["SkipPrivatePlaces"]:
                        print("Checking place availability...")
                        
                        placeStatusParams = {'universeIds': universeID}

                        getPlaceStatus = requests.get("https://games.roblox.com/v1/games/multiget-playability-status", params=placeStatusParams, cookies=cookies)
                        if getPlaceStatus.status_code == 200:
                            
                            placeStatus = getPlaceStatus.json()
                            isPlayable = placeStatus[0]["playabilityStatus"]

                            print(str(universeID) + " -> " + placeStatus[0]["playabilityStatus"])

                            if isPlayable != "Playable":
                                searchFailed = True
                        else:
                            searchFailed = True
                    

                    if not searchFailed:
                        place = {
                            "name": pInfo["data"][0]["name"],
                            "desc": pInfo["data"][0]["description"],
                            "creator": pInfo["data"][0]["creator"]["name"],
                            "visits": pInfo["data"][0]["visits"],
                            "id": str(pInfo["data"][0]["rootPlaceId"]),
                            "created": pInfo["data"][0]["created"],
                            "url": '\033[94m' + "https://www.roblox.com/games/" + str(pInfo["data"][0]["rootPlaceId"]) + '\033[0;0m',
                        }

                        print("\n" + '\033[1m' + place["name"] + "\033[0;0m" + " [ " + place["url"] + " ] " )
                        print("Created by: " + place["creator"] + " | " + place["created"][0:10])
                    

                else:
                    print("\nNo data found.")
                    searchFailed = True

    if settings["ViewPlaceInWebBrowser"]:
        if not searchFailed:
            viewPlaceInWebBrowser(placeID)


    return searchFailed

        

loadBarProperties = {
    "pos": 0,
    "width": 3,
}

def loadingbar():

    # awesome loading bar thingy I made

    outer = "▫"
    inner = "▪"

    toDraw = "none"

    if loadBarProperties["pos"] < loadBarProperties["width"]:
        loadBarProperties["pos"] += 1
    else:
        loadBarProperties["pos"] = 0

    for i in range(loadBarProperties["width"]):
        if i != loadBarProperties["pos"]:
            print(outer, end =" ")
        else:
            print(inner, end =" ")

    print("\n")




def viewPlaceInWebBrowser(pID):
        webbrowser.open("https://www.roblox.com/games/" + str(pID))


def createPlaceID():
    print("\nCreating a random ID...")
    placeID = random.randint(cfg.settings["minID"], random.randint(cfg.settings["minID"], cfg.settings["maxID"]))
    return placeID



def performSearch():
    searchFailed = findValidPlace()

    if searchFailed:
        clearScreen()
        title()

        loadingbar()
        performSearch()

    else:
        prompt = input("Press Enter to search again. Type 'e' to quit.\n")
        if prompt != 'e':
            performSearch()


def clearScreen():
    os.system('cls' if os.name=='nt' else 'clear')


def title():
    print("\n\n" + '\033[1m' + "PyPlaceRoulette" + "\033[0;0m" + " by splatert" )



def main():   
    
    title()
    
    prompt = input("Press Enter to begin. Type 'e' to exit.\n")
    if prompt == 'e':
        exit()
    else:
        performSearch()




main()