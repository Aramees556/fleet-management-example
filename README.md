# Fleet Management Example
Fleet management example using python, MQTT and ThingsBoard

Requirements:
- Docker
- Docker-compose

To start up the example go to project folder and write:
docker-compose up

The command downloads the ThingsBoard image, creates postgresql database, creates the truck simulation image. Finally it starts up containers based on those images.

Note: Thingsboard database is blank so the access tokens need to be registered and dasboard created for visualizing the fleet location.
