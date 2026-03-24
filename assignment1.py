# #Getting User input
# username = input("Enter your username: ")
# password = input("Enter your password: ")
# email = input("Enter your email: ")
# id = int(input("Enter your id: "))


# #String formatting in Python
# print(f"Username: {username}")
# print(f"Password: {password}")
# print(f"Email: {email}")
# print(f"ID: {id:.2f}, Type: {type(id)}")

# #String Assignment
# password = "********"
# print(f"Password: {password}")

# #String Assignment Solution Together
# greeting, desgination = "Hello", "World!"
# print(f"Greeting: {greeting}, Designation: {desgination}")
# concated_string = greeting + " " + desgination
# print(f"Concatenated String: {concated_string}")
# print(f"Sliced string: {concated_string[:3]}")
# print(f"Escaped string: {greeting}\n{desgination}")


# #Lists in python
# numbers = [1,2,3,4,5,6,7,8,9,10]

# #Sets and Tuples
# numbers_set = {1,2,3,4,5,6,7,8,9,10}
# numbers_tuple = (1,2,3,4,5,6,7,8,9,10)

# print(f"Numbers List: {numbers}")
# print(f"Numbers Set: {numbers_set}")
# print(f"Numbers Tuple: {numbers_tuple}")

# #List Assignment
# fruits = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
# print(f"Fruits: {fruits}")

# #List Assignment Solution 
# fruits[3] = "Dragonfruit"
# print(f"Updated Fruits: {fruits}")

# #Boolean and Operators
# num1 = 10   
# num2 = 20
# print(num1 > num2)  # False
# print(num1 < num2)  # True
# print(f"Arithimetic Operators: ")
# print(f"Addition: {num1 + num2}")
# print(f"Subtraction: {num1 - num2}")
# print(f"Multiplication: {num1 * num2}")
# print(f"Division: {num1 / num2}")

# print(f"Assignment Operators: ")
# print(f"Addition Assignment (+=): {num1 + num2}")
# print(f"Subtraction Assignment (-=): {num1 - num2}")
# print(f"Multiplication Assignment (*=): {num1 * num2}")
# print(f"Division Assignment (/=): {num1 / num2}")

# print(f"Comparison Operators: ")
# print(f"Equal to: {num1 == num2}")
# print(f"Not equal to: {num1 != num2}")
# print(f"Greater than: {num1 > num2}")
# print(f"Less than: {num1 < num2}")
# print(f"Greater than or equal to: {num1 >= num2}")
# print(f"Less than or equal to: {num1 <= num2}")

# print(f"Logical Operators: ")
# print(f"Logical AND: {num1 > 5 and num2 > 15}")
# print(f"Logical OR: {num1 > 5 or num2 > 25}")
# print(f"Logical NOT: {not(num1 > 5)}")

# print(f"Identity Operators: ")
# print(f"Is same object: {num1 is num2}")
# print(f"Is not same object: {num1 is not num2}")

# print(f"Membership Operators: ")
# numbers= [1,2,3,4,5,6,7,8,9,10]
# print(f"Is num1 in numbers list: {num1 in numbers}")
# print(f"Is num2 not in numbers list: {num2 not in numbers}")

# print(f"Operators Precedence: ")
# print(f"The order or precedence of operators is: () > ** > * / // % > + - > < <= > >= == != > and > or > not")

# #If else statement
# if 10 > 5:
#     print("10 is greater than 5")
# else:
#     print("10 is not greater than 5")

# #If else assignment
# num1 = 10
# num2 = 20
# if num1 > num2:
#     greater_num = num1
#     print(f"{greater_num}")
# else :
#     greater_num = num2
#     print(f"{greater_num}")

# #If-else assignment solution
# is_working = False
# is_updated = False
# print(f"Is working: {is_working}, Is updated: {is_updated}")
# if is_working and is_updated:
#     print("The system is working and updated successfully to the latest version.")
# elif is_working and not is_updated:
#     print("The system is working but not updated to the latest version.")
# elif not is_working and is_updated:
#     print("The system is not working but updated to the latest version.")
# else:
#     print("The system is not working and not updated to the latest version.")

# #Loops in Python
# a = 0
# while a < 5:
#     print(f"Value of a: {a}")
#     a += 1

# for i in range(1, 11):
#     print(f"Number: {i}")
