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
    "ShowOnlySuccessfulPlaces": cfg.settings["ShowOnlySuccessfulPlaces"],
}


reqVars = {
    "attempts": 0,
    "searchMode": 0
}



sys.path.append("../include")
import requests



def requestUniverseID(placeID):
    print("Requesting Universe ID for " + str(placeID))
    uid = requests.get("https://apis.roblox.com/universes/v1/places/" + str(placeID) + "/universe")
    
    if uid.status_code == 200:
        return uid
    else:
        return None



def search():
    
    searchFailed = False
    placeID = createPlaceID()

    session = requests.Session()
    cookies = {'.ROBLOSECURITY': myRobloSecurityKey}

    print("Connecting to Universes API...")

    getUniverseID = requestUniverseID(placeID)

    if getUniverseID == None:
        searchFailed = True
    else:

        getUniverseID = getUniverseID.json()
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
                            print("Skipping starter places...")
                            searchFailed = True

                    if settings["ShowOnlySuccessfulPlaces"]:

                        print("Searching for places that were popular...")

                        placeVisits = pInfo["data"][0]["visits"]
                        #print("Visits: " + str(placeVisits))
                        if int(placeVisits) < 15000:
                            searchFailed = True,


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

                        basicDetails = [
                            pInfo["data"][0]["rootPlaceId"],
                            pInfo["data"][0]["name"],
                            pInfo["data"][0]["creator"]["name"]
                        ]
                        storeBasicPlaceDetails(basicDetails[0], basicDetails[1], basicDetails[2])

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






def addToFavs():

    basicPlaceInfo = getBasicPlaceDetails()

    favs = open("favs.txt", 'a') # a for append
    favs.write("\n{0},{1},{2}".format(basicPlaceInfo["id"], basicPlaceInfo["placeName"], basicPlaceInfo["creator"]))

    favs.close()



basicPlaceDetails = {
    "placeName": "Crossroads",
    "creator": "Roblox",
    "id": "0",
}


def storeBasicPlaceDetails(PlaceID, PlaceName, Creator):
    
    # place title and ID leaves paranthesis and quotation marks for some reason. Let's clean them out.
    #placeID_clean = PlaceID.split("'")
    #placeName_clean = PlaceName.split('"')
    
    basicPlaceDetails["id"] = PlaceID,
    basicPlaceDetails["placeName"] = PlaceName,
    basicPlaceDetails["creator"] = Creator
    
    #print(str(basicPlaceDetails["id"]) + ", " + str(basicPlaceDetails["placeName"]) + ", " + str(basicPlaceDetails["creator"]))




def getBasicPlaceDetails():
    return basicPlaceDetails




def viewPlaceInWebBrowser(pID):
        webbrowser.open("https://www.roblox.com/games/" + str(pID))


def createPlaceID():
    print("\nCreating a random ID...")
    placeID = random.randint(cfg.settings["minID"], random.randint(cfg.settings["minID"], cfg.settings["maxID"]))
    print("[OK]")
    return placeID





def performSearch():

    searchFailed = None


    if reqVars["searchMode"] == 1:
        searchFailed = search()
    elif reqVars["searchMode"] == 2:
        searchFailed = fastSearch()

    

    if searchFailed:
        clearScreen()
        title()
        loadingbar()

        print("Retries: " + str(reqVars["attempts"]))

        if reqVars["attempts"] < 500:
            
            reqVars["attempts"] += 1

            performSearch()
        else:
            reqVars["attempts"] = 0
            print("Too many requests. Wait for a few minutes then try again.")


            prompt = input("\x1b[38;5;110;1m" + "Enter" + "\033[0m" + " Retry  " + "\x1b[38;5;110;1m" + "E" + "\033[0m" + " Quit.\n")
            if prompt == 'e':
                exit()
            else:
                performSearch()


    else:
        reqVars["attempts"] = 0
        searchResultsPrompt()



def searchResultsPrompt(addedToFavStatus=False):
    
    addToFavText = "(wip)"
    if addedToFavStatus:
        addToFavText = " Added to favorites."

    prompt = input("\n" + "\33[33;1m" + "F" + "\033[0m" + addToFavText + "\n" +"\x1b[38;5;110;1m" + "Enter" + "\033[0m" + " New Search  " + "\x1b[38;5;110;1m" + "E" + "\033[0m" + " Quit.\n")
    
    if prompt != 'e' and prompt != 'f':
        performSearch()

    elif prompt == 'f' and prompt != 'e':
        addToFavs()
        searchResultsPrompt(addedToFavStatus=True)





def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')


def title():
    print("\n\n" + '\033[1m' + "PyPlaceRoulette" + "\033[0;0m" + " by splatert" )




def getPlaceAvailability(universeID):

    placeStatusParams = {'universeIds': universeID}
    cookies = {'.ROBLOSECURITY': myRobloSecurityKey}

    getPlaceStatus = requests.get("https://games.roblox.com/v1/games/multiget-playability-status", params=placeStatusParams, cookies=cookies)
    
    if getPlaceStatus.status_code == 200:          
        placeStatus = getPlaceStatus.json()
        playability = placeStatus[0]["playabilityStatus"]
        
        if playability == "Playable":
            return True
        else:
            return False



def multigetPlaceInfo(placeID):
    
    print("Reading place details...")

    session = requests.Session()
    cookies = {'.ROBLOSECURITY': myRobloSecurityKey}
    params = {'placeIds': placeID}

    getPlaceInfo = requests.get("https://games.roblox.com/v1/games/multiget-place-details", cookies=cookies, params=params)
    

    placeInfoTemplate = {
        "placeId":	0,
        "name": "Loading...",
        "sourceName": "Loading...",
        "description": "Loading...",
        "sourceDescription": "Loading...",
        "url": "https://www.roblox.com/games/1844238/Fjorkavills-Hellgate",
        "builder": "Loading...",
        "builderId": 0,
        "isPlayable": True,
        "reasonProhibited": "None",
        "universeId": 420602,
        "universeRootPlaceId": 1844238,
    }


    if getPlaceInfo.status_code == 200:

        placeInfo = getPlaceInfo.json()

        if len(placeInfo) > 0:
            # fill in array with place details
            keysToTake = ["placeId", "name", "description", "builder", "isPlayable"]
        
            for key in keysToTake:
                if placeInfo[0][key]:
                    placeInfoTemplate[key] = placeInfo[0][key]
                else:
                    placeInfoTemplate[key] = "Could not fetch."

            print("[OK]", end=" ")
            return placeInfoTemplate

        else:
            return "ErrNotValidPlace"

    else:
        print("[Error] Not a place. Performing new search...")
        return "ErrNotValidPlace"
    

        

def placeIsNotTemplate(placeName):

    valid = False

    if placeName.endswith("'s Place"):
        valid = False
    else:
        valid = True

    return valid




def fastSearch():

    searchFailed = False

    placeID = createPlaceID()
    place = multigetPlaceInfo(placeID)

    if place == "ErrNotValidPlace":
        searchFailed = True
    else:

        placeDetails = place

        if settings["SkipStarterPlaces"]:
            notAStarterPlace = placeIsNotTemplate(placeDetails["name"])
            if notAStarterPlace == False:
                searchFailed = True


        if settings["SkipPrivatePlaces"]:
            if placeDetails["isPlayable"] == "true":
                searchFailed = False
            elif placeDetails["isPlayable"] == "false":
                searchFailed = True

        
        if not searchFailed:
            print("\n" + '\033[1m' + placeDetails["name"] + "\033[0;0m" + " [ " + placeDetails["url"] + " ] " )
            print("Created by: " + placeDetails["builder"])
            
            if settings["ViewPlaceInWebBrowser"]:
                if not searchFailed:
                    viewPlaceInWebBrowser(placeID)


    

    return searchFailed





def main():   
    
    title()
    
    print("\nChoose randomizer.")
    print("A. Standard")
    print("D. Fast\n\n")

    prompt = input("\x1b[38;5;110;1m" + "A/D" + "\033[0m" + " Choose  " + "\x1b[38;5;110;1m" + "E" + "\033[0m" + " Quit.\n")
    if prompt == "a" or prompt == "d":
        
        if prompt == "a":
            reqVars["searchMode"] = 1
        elif prompt == "d":
            reqVars["searchMode"] = 2

        #print("mode: " + str(reqVars["searchMode"]))
        performSearch()

    elif prompt == "e":
        
        clearScreen()
        exit()


main()