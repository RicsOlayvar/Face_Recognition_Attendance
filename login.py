import csv


def login():
    print("=== LOGIN SYSTEM ===")

    username = input("Username: ")
    password = input("Password: ")

    with open("users.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["username"] == username and row["password"] == password:
                print("Login successful!")
                return row["role"]

    print("Invalid credentials!")
    return None


role = login()

if role == "admin":
    print("Welcome Admin Panel")
elif role == "employee":
    print("Welcome Employee Panel")
else:
    print("Access denied")