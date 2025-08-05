import datetime

user_data = {}

def is_trial_active(user_id):
    data = user_data.get(user_id)
    if data and 'start_date' in data:
        delta = datetime.datetime.now() - data['start_date']
        return delta.days < 7
    return False

def start_trial(user_id):
    user_data[user_id] = {
        'start_date': datetime.datetime.now(),
        'is_active': True
    }

def is_subscription_active(user_id):
    return user_data.get(user_id, {}).get("is_active", False)

def activate_subscription(user_id):
    user_data[user_id]["is_active"] = True
