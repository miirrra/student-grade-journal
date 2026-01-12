import sqlite3

DB_NAME = "students.db"


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                subject TEXT NOT NULL,
                grade REAL NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id)
            );
        """)

        conn.commit()
        conn.close()
        print("Таблицы созданы или уже существуют.")


class Student:
    def __init__(self, name):
        self.name = name
        self.grades = {} 

    def add_grade(self, subject, grade):
        self.grades[subject] = grade



class JournalApp:
    def __init__(self):
        self.db = DatabaseManager(DB_NAME)



    def add_student(self):
        name = input("Введите имя студента: ")
        student = Student(name)

        
        while True:
            subject = input("Введите предмет (или 'стоп' для завершения): ")
            if subject.lower() == "стоп":
                break
            grade = float(input(f"Введите оценку по '{subject}': "))
            student.add_grade(subject, grade)

        
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO students (name) VALUES (?)", (student.name,))
        student_id = cursor.lastrowid

        for subject, grade in student.grades.items():
            cursor.execute(
                "INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)",
                (student_id, subject, grade)
            )

        conn.commit()
        conn.close()
        print("Студент и его оценки добавлены.")


    def show_all(self):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

        if not students:
            print("Нет данных.")
            return

        for student_id, name in students:
            print(f"\nСтудент: {name}")

            cursor.execute("SELECT subject, grade FROM grades WHERE student_id=?", (student_id,))
            grades = cursor.fetchall()

            for subject, grade in grades:
                print(f"  {subject}: {grade}")

        conn.close()

    
    def avg_by_student(self):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.name, AVG(g.grade)
            FROM students s
            JOIN grades g ON s.id = g.student_id
            GROUP BY s.id;
        """)

        results = cursor.fetchall()

        for name, avg in results:
            print(f"{name}: средний балл = {avg:.2f}")

        conn.close()

    
    def avg_by_subject(self):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT subject, AVG(grade)
            FROM grades
            GROUP BY subject;
        """)

        results = cursor.fetchall()

        for subject, avg in results:
            print(f"{subject}: средний балл = {avg:.2f}")

        conn.close()

    
    def menu(self):
        while True:
            print("\nМеню:")
            print("1 — Создать таблицы")
            print("2 — Добавить студента")
            print("3 — Показать всех студентов")
            print("4 — Средний балл по студентам")
            print("5 — Средний балл по предметам")
            print("0 — Выход")

            choice = input("Выберите пункт: ")

            if choice == "1":
                self.db.create_tables()
            elif choice == "2":
                self.add_student()
            elif choice == "3":
                self.show_all()
            elif choice == "4":
                self.avg_by_student()
            elif choice == "5":
                self.avg_by_subject()
            elif choice == "0":
                print("Выход.")
                break
            else:
                print("Неверный ввод.")



if __name__ == "__main__":
    app = JournalApp()
    app.menu()
