# Створіть додаток «Записна книжка», який зберігає інформацію про нотатки користувача. Можливості додатку:
# ■ вхід за логіном і паролем;
# ■ додавати нотатки;
# ■ видаляти нотатки;
# ■ редагувати нотатки;
# ■ переглядати нотатки. Якщо нотаток складається з декількох частин, відобразіть усі частини;
# ■ показ усіх нотаток;
# ■ перегляд нотаток за певний проміжок часу;
# ■ відображення нотаток, що містять набір заданих слів.
# Дані необхідно зберігати у базі даних NoSQL. Можете
# використовувати Redis в якості платформи.
import redis
from datetime import datetime

class Notebook:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0)

    def login(self, username, password):
        stored_password = self.r.hget(f"user:{username}", "password")
        if stored_password and stored_password.decode() == password:
            return True
        return False

    def add_user(self, username, password):
        if self.r.exists(f"user:{username}"):
            return "User already exists"
        self.r.hset(f"user:{username}", mapping={"password": password})
        return "User added successfully"

    def add_note(self, username, note_id, content):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        note_key = f"note:{note_id}"
        self.r.hset(note_key, mapping={"content": content, "timestamp": datetime.now().isoformat()})
        self.r.rpush(f"user_notes:{username}", note_id)
        return "Note added successfully"

    def delete_note(self, username, note_id):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        if not self.r.exists(f"note:{note_id}"):
            return "Note not found"
        self.r.lrem(f"user_notes:{username}", 0, note_id)
        self.r.delete(f"note:{note_id}")
        return "Note deleted"

    def edit_note(self, note_id, new_content):
        if not self.r.exists(f"note:{note_id}"):
            return "Note not found"
        self.r.hset(f"note:{note_id}", "content", new_content)
        self.r.hset(f"note:{note_id}", "timestamp", datetime.now().isoformat())
        return "Note edited successfully"

    def view_note(self, note_id):
        if not self.r.exists(f"note:{note_id}"):
            return "Note not found"
        return self.r.hgetall(f"note:{note_id}")

    def view_all_notes(self, username):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        note_ids = self.r.lrange(f"user_notes:{username}", 0, -1)
        notes = []
        for note_id in note_ids:
            notes.append(self.r.hgetall(f"note:{note_id.decode()}"))
        return notes

    def view_notes_by_time_range(self, username, start_time, end_time):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        note_ids = self.r.lrange(f"user_notes:{username}", 0, -1)
        notes = []
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)
        for note_id in note_ids:
            note = self.r.hgetall(f"note:{note_id.decode()}")
            note_time = datetime.fromisoformat(note[b'timestamp'].decode())
            if start_time <= note_time <= end_time:
                notes.append(note)
        return notes

    def search_notes(self, username, search_words):
        if not self.r.exists(f"user:{username}"):
            return "User not found"
        note_ids = self.r.lrange(f"user_notes:{username}", 0, -1)
        notes = []
        for note_id in note_ids:
            note = self.r.hgetall(f"note:{note_id.decode()}")
            content = note[b'content'].decode()
            if all(word in content for word in search_words):
                notes.append(note)
        return notes

# Приклад використання
if __name__ == "__main__":
    notebook = Notebook()

    print(notebook.add_user("user1", "password123"))
    if notebook.login("user1", "password123"):
        print("Login successful")
    else:
        print("Login failed")
    print(notebook.add_note("user1", "1", "This is the first note"))
    print(notebook.add_note("user1", "2", "This is the second note with more content"))
    print(notebook.edit_note("1", "This is the updated first note"))
    print(notebook.view_note("1"))
    print(notebook.view_all_notes("user1"))
    start_time = "2023-01-01T00:00:00"
    end_time = "2024-01-01T00:00:00"
    print(notebook.view_notes_by_time_range("user1", start_time, end_time))
    search_words = ["first", "updated"]
    print(notebook.search_notes("user1", search_words))
    print(notebook.delete_note("user1", "1"))
