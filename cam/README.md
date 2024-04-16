## Abstract
Camera is a raspberry pi zero. Its running mediamtx a rtsp stream.\
For some reason the mediamtx service/process keeps crashing after some time. Maybe there is some issue with the over clocking. If the pi is not overclocked, it cant run at all. Cant be bothered to properly debug this, so there is a service that runs mediamtx (mediamtx.service) and a second service that regularly restarts the mediamtx.service every 5 min to avoid this crash, seams to work. 


## Files
`mediamtx.yaml` is the config file for the mediamtx server\
`mediamtx.service` is the systemctl service to run mediamtx\
`mediamtx_restarter.service` is the systemctl service to restart the mediamtx.service\
`config.txt` is the firmware config for the pi (overclocking)
