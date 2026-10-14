from flask import Flask, render_template, request, redirect, url_for
import database

# remember to $ pip install flask
# remember to $ pip install mongita

database.setup_database("pets")

app = Flask(__name__)


def error_page(message, status=400):
    # Simple text response page, as requested.
    return message, status, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/", methods=["GET"])
@app.route("/list", methods=["GET"])
def get_list():
    pets = database.get_pets()
    for pet in pets:
        pet['owner'] = database.get_owner(pet['owner_id'])['name']
        pet['food'] = database.get_food(pet['food_id'])['name']
    return render_template("list.html", pets=pets)


@app.route("/create", methods=["GET"])
def get_create():
    owners = database.get_owners()
    foods = database.get_foods()
    return render_template("create.html", owners=owners, foods=foods)


@app.route("/create", methods=["POST"])
def post_create():
    data = dict(request.form)
    try:
        database.create_pet(data)
        return redirect(url_for("get_list"))
    except (ValueError, database.ConstraintError) as e:
        return error_page(f"Error: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error creating pet: {e}", 500)


@app.route("/delete/<id>", methods=["GET"])
def get_delete(id):
    try:
        database.delete_pet(id)
        return redirect(url_for("get_list"))
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except database.NotFoundError as e:
        return error_page(f"Error: {e}", 404)
    except Exception as e:
        return error_page(f"Unexpected error deleting pet: {e}", 500)


@app.route("/update/<id>", methods=["GET"])
def get_update(id):
    try:
        data = database.get_pet(id)
        if data is None:
            return error_page("Error: pet not found.", 404)
        owners = database.get_owners()
        foods = database.get_foods()
        return render_template("update.html", data=data, owners=owners, foods=foods)
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error loading pet: {e}", 500)


@app.route("/update/<id>", methods=["POST"])
def post_update(id):
    data = dict(request.form)
    try:
        database.update_pet(id, data)
        return redirect(url_for("get_list"))
    except (ValueError, database.ConstraintError) as e:
        return error_page(f"Error: {e}", 400)
    except database.NotFoundError as e:
        return error_page(f"Error: {e}", 404)
    except Exception as e:
        return error_page(f"Unexpected error updating pet: {e}", 500)


@app.route("/owners", methods=["GET"])
def get_owners_list():
    owners = database.get_owners()
    return render_template("owner_list.html", owners=owners)


@app.route("/owner/create", methods=["GET"])
def get_owner_create():
    return render_template("owner_create.html")


@app.route("/owner/create", methods=["POST"])
def post_owner_create():
    data = dict(request.form)
    try:
        database.create_owner(data)
        return redirect(url_for("get_owners_list"))
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error creating owner: {e}", 500)


@app.route("/owner/delete/<id>", methods=["GET"])
def get_owner_delete(id):
    try:
        database.delete_owner(id)
        return redirect(url_for("get_owners_list"))
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except database.NotFoundError as e:
        return error_page(f"Error: {e}", 404)
    except database.ConstraintError as e:
        return error_page(f"Error: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error deleting owner: {e}", 500)


@app.route("/owner/update/<id>", methods=["GET"])
def get_owner_update(id):
    try:
        data = database.get_owner(id)
        if data is None:
            return error_page("Error: owner not found.", 404)
        return render_template("owner_update.html", data=data)
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error loading owner: {e}", 500)


@app.route("/owner/update/<id>", methods=["POST"])
def post_owner_update(id):
    data = dict(request.form)
    try:
        database.update_owner(id, data)
        return redirect(url_for("get_owners_list"))
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except database.NotFoundError as e:
        return error_page(f"Error: {e}", 404)
    except Exception as e:
        return error_page(f"Unexpected error updating owner: {e}", 500)


@app.route("/foods", methods=["GET"])
def get_foods_list():
    return render_template("food_list.html", foods=database.get_foods())


@app.route("/food/create", methods=["GET"])
def get_food_create():
    return render_template("food_create.html")


@app.route("/food/create", methods=["POST"])
def post_food_create():
    try:
        database.create_food(dict(request.form))
        return redirect(url_for("get_foods_list"))
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error creating food: {e}", 500)


@app.route("/food/delete/<id>", methods=["GET"])
def get_food_delete(id):
    try:
        database.delete_food(id)
        return redirect(url_for("get_foods_list"))
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except database.NotFoundError as e:
        return error_page(f"Error: {e}", 404)
    except database.ConstraintError as e:
        return error_page(f"Error: {e}", 400)
    except Exception as e:
        return error_page(f"Unexpected error deleting food: {e}", 500)


@app.route("/food/update/<id>", methods=["GET"])
def get_food_update(id):
    try:
        data = database.get_food(id)
        if data is None:
            return error_page("Error: food not found.", 404)
        return render_template("food_update.html", data=data)
    except ValueError as e:
        return error_page(f"Error: {e}", 400)


@app.route("/food/update/<id>", methods=["POST"])
def post_food_update(id):
    try:
        database.update_food(id, dict(request.form))
        return redirect(url_for("get_foods_list"))
    except ValueError as e:
        return error_page(f"Error: {e}", 400)
    except database.NotFoundError as e:
        return error_page(f"Error: {e}", 404)
    except Exception as e:
        return error_page(f"Unexpected error updating food: {e}", 500)


@app.route("/health", methods=["GET"])
def health():
    try:
        database.get_pets()
        database.get_owners()
        database.get_foods()
        return error_page("ok", 200)
    except Exception as e:
        return error_page(f"Error checking health: {e}", 500)
