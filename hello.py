todos = []

def show_todos():
    if len(todos) == 0:
        print("Your list is empty!")
    else:
        for i, item in enumerate(todos):
            print(str(i + 1) + ". " + item)

def add_todo():
    item = input("What do you want to add? ")
    todos.append(item)
    print("Added: " + item)

def remove_todo():
    show_todos()
    number = int(input("Which number do you want to remove? "))
    removed = todos.pop(number - 1)
    print("Removed: " + removed)

print("Welcome to your To-Do List!")

while True:
    print("\nWhat do you want to do?")
    print("1. Show list")
    print("2. Add item")
    print("3. Remove item")
    print("4. Quit")

    choice = input("Enter 1, 2, 3 or 4: ")

    if choice == "1":
        show_todos()
    elif choice == "2":
        add_todo()
    elif choice == "3":
        remove_todo()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid choice, try again.")
