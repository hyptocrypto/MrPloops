# MrPloops

## Abstract
The idea here is to create a alert system for when my dog is pooping in the house.

## Cam/Monitoring
I have a Raspberry pi zero w with a camera mounted in the corner of our dining room. It will be running a rtsp server via [Mediamtx](https://github.com/bluenviron/mediamtx) on the local network. This could easy be extended to multiple cams to cover all possible angles.

## Detection/Inference
The data set comprised of dogs just chillin and dogs pooping. These images have been scraped from google, along with a few that I took personally. [FastAI](https://www.fast.ai/) was used to train a simple classification model.

The Pi does not have enough ram or cpu to confidently run any ML inference/predictions. So on a more stout piece of hardware, there is a web server running that will do a few things.
    1. Consume the stream and run predictions
    2. Save footage of positive predictions
    3. Expose cam stream via simple webpage

## TODO
Alert whe poopin. Sending a text seams slow, sounding and alarm seams excessive. Something in the middle would be nice
