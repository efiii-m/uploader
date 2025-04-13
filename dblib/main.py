import json
import os

class DataBase:
    def __init__(self, dir):
        self.db_dir = dir
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

    def _get_user_file(self, user_id):
        return os.path.join(self.db_dir, f'{user_id}.json')

    def insert(self, user_id, user_data):
        user_file = self._get_user_file(user_id)

        with open(user_file, 'w') as file:
            json.dump(user_data, file, indent=4)

    def get(self, user_id):
        user_file = self._get_user_file(user_id)

        if not os.path.exists(user_file):
            return None

        with open(user_file, 'r') as file:
            data = json.load(file)

        return data

    def get_all_users(self):
        return [os.path.splitext(f)[0] for f in os.listdir(self.db_dir) if f.endswith('.json')]

    def close(self):
        pass

    def user_exists(self, user_id):
        user_file = self._get_user_file(user_id)
        return os.path.exists(user_file)

    def update(self, user_id, new_data):
        user_file = self._get_user_file(user_id)
        if os.path.exists(user_file):
            with open(user_file, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        data.update(new_data)

        with open(user_file, 'w') as file:
            json.dump(data, file, indent=4)

    def get_by_referral_id(self, referral_id):
        for username in self.get_all_users():
            user_data = self.get(username)
            if user_data and user_data.get('refral_id') == referral_id:
                return user_data
        return None

    def filter_users_by_param(self, param, value):
        filtered_users = []
        for username in self.get_all_users():
            user_data = self.get(username)
            if user_data and user_data.get(param) == value:
                filtered_users.append(user_data)
        return filtered_users