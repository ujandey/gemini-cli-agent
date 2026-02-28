from functions import run_python_file
from functions import write_file


def print_separator():
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":

    # Overwrite existing file
    print("Test 1: Overwriting lorem.txt")
    print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))

    print_separator()

    # Write new file inside subdirectory
    print("Test 2: Writing pkg/morelorem.txt")
    print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))

    print_separator()

    # Attempt to escape working directory
    print("Test 3: Writing /tmp/temp.txt")
    print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))