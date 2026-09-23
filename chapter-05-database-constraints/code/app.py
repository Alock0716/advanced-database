from flask import Flask, render_template, request, redirect, url_for

import database, sqlite3

# remember to $ pip install flask

database.initialize("pets.db")

app = Flask(__name__)

def error_page(message, status=400):
    # Simple text response page, as requested.
    return message, status, {"Content-Type": "text/plain; charset=utf-8"}

@app.route("/", methods=["GET"]) 
@app.route("/list", methods=["GET"])
def get_list():
    try:
        foods = database.get_foods()
        print(foods)
        pets = database.get_pets()
        print(pets)
        foods = database.get_foods()
        print(foods)
        for pet in pets:
            pet["food_name"] = "<Unknown>"   
            pet["food_name"] = "<Unknown>"
            for food in foods:
                if food["id"] == pet["food_id"]:
                    pet["food_name"] =  food["FoodName"]
            for food in foods:
                if food["id"] == pet["food_id"]:
                    pet["food_name"] = food["name"]
        return render_template("list.html", pets=pets)
    except sqlite3.Error as e:
        return error_page(f"Database error while listing pets: {e}", 500)        


@app.route("/create", methods=["GET"])
def get_create():
    try:
        foods = database.get_foods()
        return render_template("create.html", foods=foods)     
    except sqlite3.Error as e:
        return error_page(f"Database error while loading foods: {e}", 500)


@app.route("/create", methods=["POST"])
def post_create():
    data = dict(request.form)

    food_id = (data.get("food_id") or "").strip()
    if food_id == "":
        return error_page("Error: You must select an food for the pet.", 400)
    if not food_id.isdigit():
        return error_page("Error: food_id must be a number.", 400)
    food_id = (data.get("food_id") or "").strip()
    if food_id == "":
        return error_page("Error: You must select an food for the pet.", 400)
    if not food_id.isdigit():
        return error_page("Error: food_id must be a number.", 400)

    try:
        database.create_pet(data)
        return redirect(url_for("get_list"))
    except sqlite3.IntegrityError as e:
        return error_page(f"Constraint error creating pet: {e}", 400)
    except sqlite3.OperationalError as e:
        return error_page(f"Database operational error creating pet: {e}", 500)
    except ValueError as e:
        return error_page(f"Bad input creating pet: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error creating pet: {e}", 500)

@app.route("/delete/<id>", methods=["GET"])
def get_delete(id):
    try:
        # Validate id early so ValueError doesn't become a 500.
        int(id)
    except ValueError:
        return error_page("Error: pet id must be an integer.", 400)

    try:
        database.delete_pet(id)
        return redirect(url_for("get_list"))
    except sqlite3.IntegrityError as e:
        return error_page(f"Constraint error deleting pet: {e}", 400)
    except sqlite3.OperationalError as e:
        return error_page(f"Database operational error deleting pet: {e}", 500)
    except Exception as e:
        return error_page(f"Unexpected error deleting pet: {e}", 500)


@app.route("/update/<id>", methods=["GET"])
def get_update(id):
    try:
        int(id)
    except ValueError:
        return error_page("Error: pet id must be an integer.", 400)

    try:
        data = database.get_pet(id)
        if data is None:
            return error_page("Error: pet not found.", 404)
        foods = database.get_foods()
        foods = database.get_foods()
        return render_template("update.html", data=data, foods=foods)
    except sqlite3.Error as e:
        return error_page(f"Database error loading pet for update: {e}", 500)


@app.route("/update/<id>", methods=["POST"])
def post_update(id):
    try:
        int(id)
    except ValueError:
        return error_page("Error: pet id must be an integer.", 400)

    data = dict(request.form)

    food_id = (data.get("food_id") or "").strip()
    if food_id == "":
        return error_page("Error: You must select an food for the pet.", 400)
    if not food_id.isdigit():
        return error_page("Error: food_id must be a number.", 400)
    food_id = (data.get("food_id") or "").strip()
    if food_id == "":
        return error_page("Error: You must select an food for the pet.", 400)
    if not food_id.isdigit():
        return error_page("Error: food_id must be a number.", 400)

    try:
        database.update_pet(id, data)
        return redirect(url_for("get_list"))
    except sqlite3.IntegrityError as e:
        return error_page(f"Constraint error updating pet: {e}", 400)
    except sqlite3.OperationalError as e:
        return error_page(f"Database operational error updating pet: {e}", 500)
    except ValueError as e:
        return error_page(f"Bad input updating pet: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error updating pet: {e}", 500)

@app.route("/foods", methods=["GET"])
def get_foods_list():
    try:
        foods = database.get_foods()
        return render_template("food_list.html", foods=foods)
    except sqlite3.Error as e:
        return error_page(f"Database error while listing foods: {e}", 500)


@app.route("/food/create", methods=["GET"])
def get_food_create():
    return render_template("food_create.html")


@app.route("/food/create", methods=["POST"])
def post_food_create():
    data = dict(request.form)
    FoodName = (data.get("FoodName") or "").strip()
    if FoodName == "":
        return error_page("Error: food name is required.", 400)

    try:
        database.create_food(data)
        return redirect(url_for("get_foods_list"))
    except sqlite3.IntegrityError as e:
        return error_page(f"Constraint error creating food: {e}", 400)
    except sqlite3.OperationalError as e:
        return error_page(f"Database operational error creating food: {e}", 500)
    except Exception as e:
        return error_page(f"Unexpected error creating food: {e}", 500)


@app.route("/food/delete/<id>", methods=["GET"])
def get_food_delete(id):
    try:
        int(id)
    except ValueError:
        return error_page("Error: food id must be an integer.", 400)

    try:
        database.delete_food(id)
        return redirect(url_for("get_foods_list"))
    except sqlite3.IntegrityError as e:
        # Most likely FK RESTRICT due to pets.
        return error_page(
            "Error: Cannot delete this food because they have pets. "
            "Please delete their pets first.\n"
            f"(details: {e})",
            400,
        )
    except sqlite3.OperationalError as e:
        return error_page(f"Database operational error deleting food: {e}", 500)
    except Exception as e:
        return error_page(f"Unexpected error deleting food: {e}", 500)


@app.route("/food/update/<id>", methods=["GET"])
def get_food_update(id):
    try:
        int(id)
    except ValueError:
        return error_page("Error: food id must be an integer.", 400)

    try:
        data = database.get_food(id)
        if data is None:
            return error_page("Error: food not found.", 404)
        return render_template("food_update.html", data=data)
    except AssertionError:
        return error_page("Error: food not found.", 404)
    except sqlite3.Error as e:
        return error_page(f"Database error loading food for update: {e}", 500)


@app.route("/food/update/<id>", methods=["POST"])
def post_food_update(id):
    try:
        int(id)
    except ValueError:
        return error_page("Error: food id must be an integer.", 400)

    data = dict(request.form)
    FoodName = (data.get("FoodName") or "").strip()
    if FoodName == "":
        return error_page("Error: food name is required.", 400)

    try:
        database.update_food(id, data)
        return redirect(url_for("get_foods_list"))
    except sqlite3.IntegrityError as e:
        return error_page(f"Constraint error updating food: {e}", 400)
    except sqlite3.OperationalError as e:
        return error_page(f"Database operational error updating food: {e}", 500)
    except Exception as e:
        return error_page(f"Unexpected error updating food: {e}", 500)


@app.route("/health", methods=["GET"])
def health():
    # Quick check that the DB is reachable and FK enforcement is ON.
    try:
        fk = database.connection.execute("PRAGMA foreign_keys").fetchone()[0]
        if fk != 1:
            return error_page("Error: foreign key constraints are NOT active.", 500)
        return error_page("ok", 200)
    except Exception as e:
        return error_page(f"Error checking health: {e}", 500)
