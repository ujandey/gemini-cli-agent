from functions.get_file_content import get_file_content
from config import MAX_FILE_CHARS


def print_separator():
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":

    # Test large file truncation
    print("Testing lorem.txt truncation...")
    lorem_result = get_file_content("calculator", "lorem.txt")

    print(f"Length returned: {len(lorem_result)}")
    print("Truncation message present:",
          f'truncated at {MAX_FILE_CHARS}' in lorem_result)

    print_separator()

    # Test reading main.py
    print("Testing main.py...")
    print(get_file_content("calculator", "main.py"))

    print_separator()

    # Test reading nested file
    print("Testing pkg/calculator.py...")
    print(get_file_content("calculator", "pkg/calculator.py"))

    print_separator()

    # Should fail (outside working directory)
    print("Testing /bin/cat...")
    print(get_file_content("calculator", "/bin/cat"))

    print_separator()

    # Should fail (non-existent file)
    print("Testing pkg/does_not_exist.py...")
    print(get_file_content("calculator", "pkg/does_not_exist.py"))