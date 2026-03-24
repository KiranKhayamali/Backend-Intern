
# #Dictionaries in Python
# person = {
#     "name": "Kiran", 
#     "age": 23, 
#     "city": "Bhaktapur"
# }

# # print(f"Person Dictionary: {person}")

# #Dictionary Assignment
# person["email"] = "kiran@example.com"

# #Dictionary Assignment Solution
# print(f"{person.items()}")
# print(f"{person.keys()}")
# print(f"{person.values()}")
# for x in person:
#     print(f"{x}: {person[x]}")


# #Assesment from W3school
# num = [print(i) for i in range(5)]
# print(num) #Output: [None, None, None, None, None] because print() function returns None after printing the value of i.

#Funcions in python
def calculator(num1, num2): #Nested function example
    def add():
        return num1 + num2
    def subtract():
        return num1 - num2
    def multiply():
        return num1 * num2
    def divide():
        if num2 != 0:
            return num1 / num2
        else:
            return "Cannot divide by zero"
    return add(), subtract(), multiply(), divide()

result = calculator(10, 5)
print(f"Addition: {result[0]}")
print(f"Subtraction: {result[1]}")
print(f"Multiplication: {result[2]}")
print(f"Division: {result[3]}")