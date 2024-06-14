# Завдання 1
# Створіть додаток «Соціальна мережа», який зберігає
# інформацію про користувача, його друзів, публікації користувача. Можливості додатку:
# ■ вхід за логіном і паролем;
# ■ додати користувача;
# ■ видалити користувача;
# ■ редагувати інформацію про користувача;
# ■ пошук користувача за ПІБ;
# ■ перегляд інформації про користувача;
# ■ перегляд усіх друзів користувача;
# ■ перегляд усіх публікацій користувача.
# Зберігайте дані у базі даних NoSQL. Можете використовувати Redis в якості платформи.
import redis
from datetime import datetime

class SocialNetwork:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0)

    def login(self, username, password):
        stored_password = self.r.hget(f"user:{username}", "password")
        if stored_password and stored_password.decode() == password:
            return True
        return False

    def add_user(self, username, password, full_name):
        if self.r.exists(f"user:{username}"):
            return "User already exists"
        self.r.hset(f"user:{username}", mapping={"password": password, "full_name": full_name})
        return "User added successfully"

    def delete_user(self, username):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        self.r.delete(f"user:{username}")
        self.r.delete(f"friends:{username}")
        self.r.delete(f"posts:{username}")
        return "User deleted"

    def edit_user(self, username, new_full_name):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        self.r.hset(f"user:{username}", "full_name", new_full_name)
        return "User information updated"

    def search_user(self, full_name):
        users = self.r.keys("user:*")
        for user in users:
            if self.r.hget(user, "full_name").decode() == full_name:
                return user.decode().split(":")[1]
        return "User not found"

    def view_user(self, username):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        return self.r.hgetall(f"user:{username}")

    def add_friend(self, username, friend_username):
        if not self.r.exists(f"user:{friend_username}"):
            return "Friend user not found"
        self.r.sadd(f"friends:{username}", friend_username)
        self.r.sadd(f"friends:{friend_username}", username)
        return "Friend added"

    def view_friends(self, username):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        return self.r.smembers(f"friends:{username}")

    def add_post(self, username, content):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        post_id = self.r.incr(f"posts:{username}:id")
        post_key = f"posts:{username}:{post_id}"
        self.r.hset(post_key, mapping={"content": content, "timestamp": datetime.now().isoformat()})
        self.r.rpush(f"posts:{username}", post_key)
        return "Post added"

    def view_posts(self, username):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        post_keys = self.r.lrange(f"posts:{username}", 0, -1)
        posts = []
        for key in post_keys:
            posts.append(self.r.hgetall(key))
        return posts

if __name__ == "__main__":
    sn = SocialNetwork()
    print(sn.add_user("john_doe", "password123", "John Doe"))
    if sn.login("john_doe", "password123"):
        print("Login successful")
    else:
        print("Login failed")
    print(sn.add_user("jane_smith", "password123", "Jane Smith"))
    print(sn.add_friend("john_doe", "jane_smith"))
    print(sn.add_post("john_doe", "This is my first post"))
    print(sn.add_post("john_doe", "Another post with more information"))
    print(sn.view_posts("john_doe"))
    print(sn.edit_user("john_doe", "Johnathan Doe"))
    print(sn.view_user("john_doe"))
    print(sn.search_user("Johnathan Doe"))
    print(sn.view_friends("john_doe"))
    print(sn.delete_user("john_doe"))
