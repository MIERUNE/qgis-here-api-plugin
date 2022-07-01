# Here Route API QGIS Plugin
## Overview
QGIS Plugin to match GPS trace to get the most probably path, using the HERE Route Matching API.
<br>
![](./imgs/mov.gif)

## Authentication
- Get an API Key from https://platform.here.com/
- Select Plugin --> HERE API Plugin --> Config from the menu bar and enter your API Key.

![](imgs/config.png)

## Usage
- Select Plugin --> HERE API Plugin --> Route Matching from the menu bar.
- Select a point layer
- Select a sort field (optional, default to `fid`)
- Select a route matching mode from car, bus, bicycle or pedestrian
- Click OK and the trace will be added to the map canvas as a temporary layer

![](imgs/dialog.png)
![](imgs/export.png)

## Note
- This plugin can help you to match the trace of a large dataset, which including more than 400 points. However, The upper limit is 10,000。 
---
### License
GNU GENERAL PUBLIC LICENSE 2
