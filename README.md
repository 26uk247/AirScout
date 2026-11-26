# AirScout
Aircraft Scatter Prediction

AirScout is a software package useful to predict and supervise radio connections via aircraft scatter propagation.
Is has the following functions:

- hold a global earth elevation model
- get aircraft position data from various sources in real time
- calculate a propagation path between two stations
- calculate the zone of mutual visability of aircraft from both stations
- provide an easy-to-use interface for all users

(c) 2019 by DL2ALF

-----------------------------------------------------------------------------------------------------------------------


Forked by M8GTD (@26uk247) for personal use, to mess around with feeding in Rain Cell positions via FlexibleJSON feed, and displaying as cloud icons, to have Aircraft Scatter prediction and Rain Scatter potential on the same map. (Given that "RainScout" is incomplete). The addition of a new plane wake turbulence Category (5 = RAINCLOUD), is the mechanism for displaying a cloud icon instead of a plane icon. Tooltip shows the speed, direction, bright band height.

A python script obtaining meteo data, and node-red flow converting that to a JSON feed, (now both in the M8GTD folder) provides live data when a FlexibleJSON feed is used in airscout. the Flexible JSON URL value for me is: http://192.168.1.12:1880/rain/AircraftList.json.
The python script obtains rain cells of 30dbZ or above, centered around my location of IO70JG. It also obtains the latest bright band height, windspeed and direction aroud my location to fake the plane path of travel.

Some manual entries in the database aircrafts.db3 are required to convert the aircraft type ("RMxx", where xx = the dbZ reflectivity value of the rain cell) in order to show the dbz value in the tooltip.


<img width="1004" height="741" alt="image" src="https://github.com/user-attachments/assets/91ce2863-ea74-41dc-8331-b14e7bd1e8ca" />
<img width="344" height="265" alt="image" src="https://github.com/user-attachments/assets/51524f45-4393-448f-800f-c7c0d791c127" />
<img width="348" height="293" alt="image" src="https://github.com/user-attachments/assets/2cf4797a-3c41-46dd-b718-cd6cc74f7719" />
<img width="786" height="593" alt="image" src="https://github.com/user-attachments/assets/17e78910-f633-4791-a567-4717d7681ea3" />
<img width="774" height="661" alt="image" src="https://github.com/user-attachments/assets/c2d67423-48dd-487d-98f6-9c094c41d3bf" />

The [unknown] records are added automatically the first time a cloud with a specific dbz is presented in the feed. I then manually update the 2 columns shown so that the tool tip shows me something meaningful:

<img width="1013" height="826" alt="image" src="https://github.com/user-attachments/assets/54f0c0e0-6373-45e1-91de-3b3c1ebf2c87" />


My build process
----------------
My environment is 64 bit Windows 10. To build, i download and unpack the Code zip from Github, then run these commands in a VS basic build tools command window, from the unzipped directory:

nuget restore

msbuild AirScout.sln /p:Configuration=Debug /p:Platform="Any CPU" /clp:ErrorsOnly

corflags /32BITREQ+ E:\Airscout\AirScout-Rain-Clouds\AirScout\bin\Debug\AirScout.exe



Please note, this is a personal project only, and i'm really not a developer. Feel free to have a look yourself, but please don't expect great things or any support, sorry.
