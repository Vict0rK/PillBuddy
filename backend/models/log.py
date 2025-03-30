from database import mongo

class Log:
    @staticmethod
    def get_all():
        return list(mongo.db.logs.find({}, {"_id": 0}))

    @staticmethod
    def add(data):
        # Insert a new log record (e.g., missed dose, unauthorized access)
        mongo.db.logs.insert_one(data)

    @staticmethod
    def delete(log_id):
        # Delete a log by its ID
        mongo.db.logs.delete_one({"_id": log_id})

class NotificationLog:
    @staticmethod
    def get_all():
        return list(mongo.db.notification_logs.find({}, {"_id": 0}))

    @staticmethod
    def add(data):
        mongo.db.notification_logs.insert_one(data)

    @staticmethod
    def clear():
        mongo.db.notification_logs.delete_many({})