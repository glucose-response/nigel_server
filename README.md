# Nigel Server

This is the Python application created using Flask and it is where the API requests are executed when the end point is called in the [Nigel App](https://github.com/glucose-response/Nigel).

The app has been deployed on Heroku and all the data is stored in MongoDB. 

## API Requests
Here are the endpoints that are commonly used in the Nigel App.

### GET Requests
- `GET /profiles` = Sends all the baby profiles in the database

* `GET /bsp` = Sends all the data for feeding, sweat measurements and blood measurements in the database

* `GET /download_template` = Sends the excel template for entering your data

* `GET /download_all_data` = Sends all the data in the database in an excel

### PUT Requests
- `PUT /addBaby` = Receives a JSON file and adds a baby to the database

* `PUT /upload_data` = Receives an excel file and adds all the data to the database

