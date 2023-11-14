import flask
from flask import Flask, jsonify, render_template, request
import flask_sqlalchemy
import sqlalchemy
from sqlalchemy import exc
import sqlalchemy.orm.exc


app = Flask(__name__)

# Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = flask_sqlalchemy.SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def __repr__(self) -> str:
        return f"<[Cafe] OBJECT {self.name}>"

    def to_dict(self):
        dictionary = {
            "cafe": {
                "id": self.id,
                "name": self.name,
                "map_url": self.map_url,
                "img_url": self.img_url,
                "location": self.location,
                "amenities": {
                    "seats": self.seats,
                    "has_toilet": self.has_toilet,
                    "has_wifi": self.has_wifi,
                    "has_sockets": self.has_sockets,
                    "can_take_calls": self.can_take_calls,
                },
                "coffee_price": self.coffee_price,
            }
        }
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    print(type(bool("true")))
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def random_cafe():
    with app.app_context():
        result = db.session.execute(sqlalchemy.select(Cafe).order_by(sqlalchemy.func.random()).limit(1)).scalar()
    return jsonify(
        cafe={
            "id": result.id,
            "name": result.name,
            "map_url": result.map_url,
            "img_url": result.img_url,
            "location": result.location,
            "amenities": {
                "seats": result.seats,
                "has_toilet": result.has_toilet,
                "has_wifi": result.has_wifi,
                "has_sockets": result.has_sockets,
                "can_take_calls": result.can_take_calls,
            },
            "coffee_price": result.coffee_price,
        }
    )


@app.route("/all")
def all_cafes():
    with app.app_context():
        result = db.session.execute(sqlalchemy.select(Cafe), execution_options={"prebuffer_rows": True}).scalars()
    cafes = {"cafes": [row.to_dict() for row in result]}
    return jsonify(cafes)


@app.route("/search")
def search_loc():
    loc = request.args.get("loc")
    print("[LOG] ==loc== ", loc)
    if loc:
        with app.app_context():
            result = db.session.execute(
                sqlalchemy.select(Cafe).where(Cafe.location.like(f"%{loc.capitalize()}%")),
                execution_options={"prebuffer_rows": True},
            ).scalars()
        cafes = {"cafes": [row.to_dict() for row in result]}
        if len(cafes["cafes"]) < 1:
            return jsonify(
                {
                    "error": {"Not Found": f"no cafe found in location: {loc}"},
                }
            )
        return jsonify(cafes)

    return jsonify(
        {
            "error": {
                "No Param given": "no 'loc' given, please add ?loc=[location], where [location] is the search term. Ex. /search?loc=London"
            },
        }
    )


# HTTP POST - Create Record
def validate_new_entry(request: flask.Request) -> bool:
    necessary_args = [
        "name",
        "map_url",
        "img_url",
        "location",
        "seats",
        "has_toilet",
        "has_wifi",
        "has_sockets",
        "can_take_calls",
    ]
    result = True

    for arg in necessary_args:
        if arg not in request.args:
            raise ValueError(f"The value for '{arg}' cannot be NULL.")

    for arg in ("name", "map_url", "img_url", "location"):
        if len(request.args.get(arg)) < 3:
            result = False
            raise ValueError(f"The value for '{arg}' must be at least 3 characters long.")

    for arg in ("has_toilet", "has_wifi", "has_sockets", "can_take_calls"):
        if request.args.get(arg) not in ("True", "False", "true", "false", "1", "0"):
            result = False
            raise ValueError(
                f"The value for '{arg}' is not accepted. The accepted values are: 'True', 'False', 'true', 'false', '1', '0'."
            )

    if request.args.get("coffee_price"):
        try:
            float(request.args.get("coffee_price"))
        except ValueError as err:
            result = False
            raise ValueError("The value for 'coffe_price' must be float.") from err

    return result


def post_to_bool(value: str) -> bool:
    if value in ("True", "true", "1"):
        return True
    else:
        return False


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":
        try:
            if validate_new_entry(request=request):
                price = None
                if "coffee_price" in request.args:
                    price = "\u00a3" + "%.2f" % (float(request.args.get("new_price")))

                new_caffe = Cafe(
                    # id = request.args.get("id"),
                    name=request.args.get("name"),
                    map_url=request.args.get("map_url"),
                    img_url=request.args.get("img_url"),
                    location=request.args.get("location"),
                    seats=request.args.get("seats"),
                    has_toilet=post_to_bool(request.args.get("has_toilet")),
                    has_wifi=post_to_bool(request.args.get("has_wifi")),
                    has_sockets=post_to_bool(request.args.get("has_sockets")),
                    can_take_calls=post_to_bool(request.args.get("can_take_calls")),
                    coffee_price=price,
                )

                with app.app_context():
                    print(new_caffe.to_dict())
                    db.session.add(new_caffe)
                    db.session.commit()
                return jsonify({"response": {"success": "succsessfully added new cafe."}})
            else:
                return flask.make_response(jsonify({"response": {"failed": "failed validation, check required format."}}), 400)

        except exc.IntegrityError as err:
            return flask.make_response(jsonify({"response": {"failed": str(err.orig)}}), 400)

        except ValueError as err:
            return flask.make_response(jsonify({"response": {"failed": str(err)}}), 400)

    return """
            <h1>details for the POST request:</h1>
            <p>Keys:</p>

            <p>
            name:  must be uniqe in the DB, necessary, at least 3 chars long<br>
            map_url:  necessary, at least 3 chars long<br>
            img_url:  necessary, at least 3 chars long<br>
            location:  necessary, at least 3 chars long<br>
            seats:  necessary<br>
            has_toilet:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'<br>
            has_wifi:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'<br>
            has_sockets:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'<br>
            can_take_calls:  necessary, accepted values: 'True', 'False', 'true', 'false', '1', '0'<br>
            coffee_price:  not necessary, must be float<br>
            </p>
            """


# HTTP PATCH - Update Coffe Price
def get_cafe(id: int) -> Cafe:
    with app.app_context():
        result = db.get_or_404(Cafe, id)
        return result


def validate_patch_price(request: flask.Request):
    result = True
    if "new_price" not in request.args:
        result = False
        raise ValueError("The value for 'new_price' cannot be NULL.")
    try:
        float(request.args.get("new_price"))
    except ValueError as err:
        result = False
        raise ValueError("The value for 'new_price' must be float.") from err
    return result


@app.route("/update-price/<cafe_id>", methods=["GET", "PATCH"])
def update_coffe_price(cafe_id):
    if request.method == "PATCH":
        try:
            if validate_patch_price(request=request):
                with app.app_context():
                    db.session.execute(
                        sqlalchemy.update(Cafe),
                        [
                            {"id": cafe_id, "coffee_price": "\u00a3" + "%.2f" % (float(request.args.get("new_price")))}
                        ],
                    )
                    db.session.commit()
                return jsonify({"response": {"success": "succsessfully updated coffee price."}})
            else:
                return flask.make_response(jsonify({"response": {"failed": "failed validation, check required format."}}), 400)
        except ValueError as err:
            return flask.make_response(jsonify({"response": {"failed": str(err)}}), 400)
        except sqlalchemy.orm.exc.StaleDataError as err:
            return flask.make_response(jsonify({"response": {"failed": str(err)}}), 400)
    else:
        return flask.make_response(jsonify({"response": {"failed": "no PATCH method"}}), 400)


if __name__ == "__main__":
    app.run(debug=True)
