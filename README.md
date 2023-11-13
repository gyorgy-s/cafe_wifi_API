# cafe_wifi_API
An implementation to store data of cafes, the data is stored in a db, the information can be accessed through the API.

in console in the folder the main.py is located:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

API endpoints return in JSON format:

Get random cafe:
```
http://localhost:5000/random
```

Get all cafes:
```
http://localhost:5000/all
```

Add a cafe to the db:
```
http://localhost:5000/add
```
details for the POST request:
Keys:

name:  must be uniqe in the DB, necessary, at least 3 chars long
map_url:  necessary, at least 3 chars long
img_url:  necessary, at least 3 chars long
location:  necessary, at least 3 chars long
seats:  necessary
has_toilet:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'
has_wifi:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'
has_sockets:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'
can_take_calls:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'
coffee_price:  not necessary, must be float

