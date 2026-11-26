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

Forked by M8GTD (@26uk247) for personal use, to mess around with feeding in Rain Cell positions via FlexibleJSON feed, and displaying as cloud icons, to have Aircraft Scatter prediction and Rain Scatter potential on the same map. (Given that "RainScout" is incomplete). The addition of a new plane wake turbulence Category (5 = RAINCLOUD), is the mechanism for displaying a cloud icon instead of a plane icon. Tooltip shows the speed, direction, bright band height.

A python script obtaining meteo data, and node-red flow converting that to a JSON feed, (neither in this project) provides live data when a FlexibleJSON feed is used in airscout.
The python script obtains rain cells of 30dbZ or above, centered around my location of IO70JG. It also obtains the latest bright band height, windspeed and direction aroud my location to fake the plane path of travel.

<img width="786" height="593" alt="image" src="https://github.com/user-attachments/assets/17e78910-f633-4791-a567-4717d7681ea3" />
<img width="1004" height="741" alt="image" src="https://github.com/user-attachments/assets/91ce2863-ea74-41dc-8331-b14e7bd1e8ca" />
<img width="344" height="265" alt="image" src="https://github.com/user-attachments/assets/51524f45-4393-448f-800f-c7c0d791c127" />
