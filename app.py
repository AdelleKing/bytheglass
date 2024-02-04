import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

#inital conection to the database to bring through the enteries to the webpage.
@app.route("/")
@app.route("/get_wine")
def get_wine():
    wines = mongo.db.wine.find()
    user = mongo.db.users.find()
    return render_template("wine.html", wines=wines, user=user)


#functionality to enable the user to register for a profile. 
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
    # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "name": request.form.get("name"),
            "location": request.form.get("location"),
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for(
                            "profile", username=session["user"]))

    return render_template("register.html")


#functionality for the user to login back into their account
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")



@app.route("/profile/", methods=["GET", "POST"])
def profile():
    wines = mongo.db.wine.find()
    profileDetails=mongo.db.users.find()

    return render_template("profile.html", wines=wines,  profileDetails=profileDetails)

    

@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_wine", methods=["GET", "POST"])
def add_wine():
    if request.method == "POST":
        recommend = "yes" if request.form.get("recommend") else "no"
        wine = {
            "wine_colour": request.form.get("category_name"),
            "grape_variety": request.form.get("grape_variety"),
            "producer": request.form.get("producer"),
            "region": request.form.get("region"),
            "vintage": request.form.get("vintage"),
            "ABV": request.form.get("ABV"),
            "price": request.form.get("price"),
            "review": request.form.get("review"), 
            "recommend": recommend, 
            "added_by": session["user"]
                    
        }
        mongo.db.wine.insert_one(wine)
        flash("Wine Successfully Added")
        return redirect(url_for("profile"))

    
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_wine.html", categories=categories)



@app.route("/edit_wine/<wine_id>", methods=["GET", "POST"])
def edit_wine(wine_id):
    if request.method == "POST":
        recommend = "yes" if request.form.get("recommend") else "no"
        submit = {
            "wine_colour": request.form.get("category_name"),
            "grape_variety": request.form.get("grape_variety"),
            "producer": request.form.get("producer"),
            "region": request.form.get("region"),
            "vintage": request.form.get("vintage"),
            "ABV": request.form.get("ABV"),
            "price": request.form.get("price"),
            "review": request.form.get("review"),
            "recommend": recommend,
            "added_by": session["user"]
           
        }
        mongo.db.wine.replace_one({"_id": ObjectId(wine_id)}, submit)
        flash("Wine Successfully Updated") 
        return redirect(url_for('profile'))

    wine = mongo.db.wine.find_one({"_id": ObjectId(wine_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_wine.html", wine=wine, categories=categories)




@app.route("/update/<users_id>", methods=["GET", "POST"])
def update(users_id):
    if request.method == "POST":
        submit = {
            "name": request.form.get("name"),
            "location": request.form.get("location"),
            "gender": request.form.get("gender"),
            "favourite": request.form.get("category_name"),
            "wine_region": request.form.get("wine_region"),
            "sweetness": request.form.get("sweetness"),
            "icon": request.form.get("icon"),

         }
        mongo.db.users.update_one({"_id": ObjectId(users_id)}, {"$set":submit})
        flash("Details Successfully Updated") 
        return redirect(url_for('profile'))


    users = mongo.db.users.find_one({"_id": ObjectId(users_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("update.html", users=users, categories=categories)
    

@app.route("/delete_wine/<wine_id>")
def delete_wine(wine_id):
    mongo.db.wine.delete_one({"_id": ObjectId(wine_id)})
    flash("Wine Successfully Deleted")
    return redirect(url_for("profile"))



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)