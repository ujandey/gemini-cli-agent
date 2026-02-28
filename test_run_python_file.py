from functions import run_python_file


def print_separator():
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":

    print("Test 1: main.py (no args)")
    print(run_python_file("calculator", "main.py"))
    print_separator()

    print('Test 2: main.py with "3 + 5"')
    print(run_python_file("calculator", "main.py", ["3 + 5"]))
    print_separator()

    print("Test 3: tests.py")
    print(run_python_file("calculator", "tests.py"))
    print_separator()

    print("Test 4: ../main.py (should error)")
    print(run_python_file("calculator", "../main.py"))
    print_separator()

    print("Test 5: nonexistent.py (should error)")
    print(run_python_file("calculator", "nonexistent.py"))
    print_separator()

    print("Test 6: lorem.txt (should error)")
    print(run_python_file("calculator", "lorem.txt"))