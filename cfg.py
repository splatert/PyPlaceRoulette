
# PyPlaceRoulette Settings file

settings = {
   
    # Replace COOKIE with your ROBLOSECURITY key for PyPlaceRoulette to make web requests. Do NOT share the key with anyone.
    # It is required so that you don't end up getting 'Unauthorized' errors.

    "SecurityKey": "COOKIE", 
    # Skip starter (new user) places
    "SkipStarterPlaces": True,

    # View place webpage in your browser
    "ViewPlaceInWebBrowser": True,
    
    # Skip places that you cannot access
    "SkipPrivatePlaces": True,

   # Skip any place that doesn't have more than 15,000 place visits (slow).
    "ShowOnlySuccessfulPlaces": False,

    # Smallest ID in random ID generation (Default: 250000)
    "minID": 250000,

    # Largest ID in random ID generation (Default: 90123456)
    "maxID": 90123456,

}
