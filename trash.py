import os

# $Env:MY_NAME="Kiran Khayamli" # Set the environment variable MY_NAME to "Kiran Khayamli" in PowerShell
name = os.getenv("MY_NAME", "Kiran Khayamli") # Default value is "Kiran Khayamli" if MY_NAME is not set

print(f"Hello, I am {name} and I am accessing the name variable from the environment variable MY_NAME")