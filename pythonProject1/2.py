# Завдання 2
# Створіть додаток «Музей літератури». Додаток має зберігати
# інформацію про експонати та людей, які мають відношення
# до експонатів. Можливості додатку:
# ■ вхід за логіном і паролем;
# ■ додати експонат;
# Практичнє завдання
# 1
# ■ видалити експонат;
# ■ редагування інформації про експонат;
# ■ перегляд повної інформації про експонат;
# ■ виведення інформації про всі експонати;
# ■ перегляд інформації про людей, які мають відношення
# до певного експонату;
# ■ перегляд інформації про експонати, що мають відношення
# до певної людини;
# ■ перегляд набору експонатів на основі певного критерію.
# Наприклад, показати всі книжкові експонати.
# Зберігайте дані у базі даних NoSQL. Можете використовувати Redis в якості платформи.
import redis
from datetime import datetime

class LiteratureMuseum:
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

    def add_exhibit(self, exhibit_id, title, description, category):
        if self.r.exists(f"exhibit:{exhibit_id}"):
            return "Exhibit already exists"
        self.r.hset(f"exhibit:{exhibit_id}", mapping={"title": title, "description": description, "category": category})
        return "Exhibit added successfully"

    def delete_exhibit(self, exhibit_id):
        if not self.r.exists(f"exhibit:{exhibit_id}"):
            return "Exhibit not found"
        self.r.delete(f"exhibit:{exhibit_id}")
        self.r.delete(f"exhibit_people:{exhibit_id}")
        return "Exhibit deleted"

    def edit_exhibit(self, exhibit_id, title=None, description=None, category=None):
        if not self.r.exists(f"exhibit:{exhibit_id}"):
            return "Exhibit not found"
        if title:
            self.r.hset(f"exhibit:{exhibit_id}", "title", title)
        if description:
            self.r.hset(f"exhibit:{exhibit_id}", "description", description)
        if category:
            self.r.hset(f"exhibit:{exhibit_id}", "category", category)
        return "Exhibit information updated"

    def view_exhibit(self, exhibit_id):
        if not self.r.exists(f"exhibit:{exhibit_id}"):
            return "Exhibit not found"
        return self.r.hgetall(f"exhibit:{exhibit_id}")

    def view_all_exhibits(self):
        exhibit_keys = self.r.keys("exhibit:*")
        exhibits = []
        for key in exhibit_keys:
            exhibits.append(self.r.hgetall(key))
        return exhibits

    def add_person_to_exhibit(self, exhibit_id, person_id, person_name):
        if not self.r.exists(f"exhibit:{exhibit_id}"):
            return "Exhibit not found"
        self.r.hset(f"person:{person_id}", "name", person_name)
        self.r.sadd(f"exhibit_people:{exhibit_id}", person_id)
        self.r.sadd(f"person_exhibits:{person_id}", exhibit_id)
        return "Person added to exhibit"

    def view_people_by_exhibit(self, exhibit_id):
        if not self.r.exists(f"exhibit:{exhibit_id}"):
            return "Exhibit not found"
        person_ids = self.r.smembers(f"exhibit_people:{exhibit_id}")
        people = []
        for pid in person_ids:
            people.append(self.r.hgetall(f"person:{pid.decode()}"))
        return people

    def view_exhibits_by_person(self, person_id):
        if not self.r.exists(f"person:{person_id}"):
            return "Person not found"
        exhibit_ids = self.r.smembers(f"person_exhibits:{person_id}")
        exhibits = []
        for eid in exhibit_ids:
            exhibits.append(self.r.hgetall(f"exhibit:{eid.decode()}"))
        return exhibits

    def view_exhibits_by_category(self, category):
        exhibit_keys = self.r.keys("exhibit:*")
        exhibits = []
        for key in exhibit_keys:
            exhibit = self.r.hgetall(key)
            if exhibit.get(b'category').decode() == category:
                exhibits.append(exhibit)
        return exhibits
if __name__ == "__main__":
    museum = LiteratureMuseum()
    print(museum.add_user("admin", "password123", "Administrator"))

    if museum.login("admin", "password123"):
        print("Login successful")
    else:
        print("Login failed")
    print(museum.add_exhibit("1", "Book of Poetry", "A collection of poems", "book"))
    print(museum.add_exhibit("2", "Literary Manuscript", "Original manuscript of a famous novel", "manuscript"))
    print(museum.edit_exhibit("1", description="A collection of classic poems"))
    print(museum.view_exhibit("1"))
    print(museum.add_person_to_exhibit("1", "1", "John Keats"))
    print(museum.add_person_to_exhibit("1", "2", "Emily Dickinson"))
    print(museum.view_people_by_exhibit("1"))
    print(museum.view_exhibits_by_person("1"))
    print(museum.view_all_exhibits())
    print(museum.view_exhibits_by_category("book"))
    print(museum.delete_exhibit("1"))
