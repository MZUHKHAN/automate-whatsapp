from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

# Replace YOUR_URL with your mongodb url
cluster = MongoClient("mongodb+srv://fathepur78624:Smile123@cluster0.ie3yd.mongodb.net/")
db = cluster["Bakery"]
users = db["users"]
orders = db["orders"]
tyres  = db["tyres"]

app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        msg = res.message("Hi, thanks for contacting *Sama Al Ramlah Auto Maint*.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *To know our services* \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        msg.media("https://etimg.etb2bimg.com/photo/85364012.cms")  
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message(
                "You can contact us through phone or e-mail.\n\n*Phone*: 971234 56789 \n*E-mail* : contact@carservices.io")
        elif option == 2:
            res.message("You have entered *Enqiry mode*.")
            users.update_one(
                {"number": number}, {"$set": {"status": "enquiry"}})
            res.message(
                "You can select one of the following services to enquire: \n\n1️⃣ Battery Services  \n2️⃣ Car AC Services \n3️⃣ Car Inspection \n"
                "4️⃣ Engine Services \n5️⃣ Oil Change \n6️⃣ Tyre Services \n 0️⃣ Go Back")
        elif option == 3:
            res.message("We work from *9 a.m. to 5 p.m*.")

        elif option == 4:
             res.message(
                "We have branch in bur dubai https://maps.app.goo.gl/kodYwNPtGuLgch7N8 *")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "enquiry":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *To know our services* \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address* \n")
    
        elif 1 <= option <= 5:
            cakes = ["Battery Services", "Car AC Services", "Car Inspection",
                     "Engine Services", "Oil Change", "Tyre Services"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "appointment"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            res.message("Thanks for your service selection😉")
            res.message("Please enter datetime to visit the workshop")
        elif option == 6 :
            users.update_one(
                {"number": number}, {"$set": {"status": "tyre"}})
            try:
                option1 = int(text)
            except:
                res.message("Please enter a valid response")
            return str(res)
            
        res.message(
                "You can select one of the following tyre brand looking for: \n\n1️⃣ Pirelli \n2️⃣ Bridgestone \n3️⃣ Continental \n"
                "4️⃣ Goodyear \n5️⃣ Michelin \n6️⃣ BFGoodrich \n 0️⃣ Go Back")
         
        if option1 == 0:
            users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *To know our services* \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address* \n")
        elif 1 <= option1 <= 6:
                   
                brand = ["Pirelli", "Bridgestone", "Continental",
                "Goodyear", "Michelin", "BFGoodrich","Yokohama","Dunlop"]
            
                select = brand[option1 - 1]
                users.update_one(
                    {"number": number}, {"$set": {"status": "tyre"}})
                users.update_one(
                    {"number": number}, {"$set": {"item": select}})
                price = users.find_one({"price": select})
                res.message("Thanks for your tyre selection😉")
                res.message(f"We have the *{select}* available in our workshop for *{price}*")
                users.update_one(
                    {"number": number}, {"$set": {"status": "appointment"}})

        else:
            res.message("Please enter a valid response")
    elif user["status"] == "appointment":
        selected = user["item"]
        res.message("Appointment done!See you in the workshop 😊")
        res.message(f"Your appointment for *{selected}* has been received and we look forward to see you in the workshop to provide better serivces")
        orders.insert_one({"number": number, "item": selected, "appointment": text, "order_time": datetime.now()})
        users.update_one(
            {"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *To know our services* \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)

if __name__ == "__main__":
    app.run()
