from database import mongo

class Analytics:
    @staticmethod
    def get_adherence_data():
        # Return medication adherence data
        return list(mongo.db.adherence.find({}, {"_id": 0}))

    @staticmethod
    def add_adherence_data(data):
        # Insert adherence data
        mongo.db.adherence.insert_one(data)

    @staticmethod
    def update_adherence_data(date, data):
        # Update adherence data for a specific date
        mongo.db.adherence.update_one({"date": date}, {"$set": data})
