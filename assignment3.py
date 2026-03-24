# #Imports in Python
# import math
# import random

# def calculator(num1, num2):
#     sum = num1 + num2
#     difference = num1 - num2
#     multiply = num1 * num2
#     product = num1 * num2
#     if num2 != 0:
#         quotient = num1 / num2
#     else:
#         quotient = "Cannot divide by zero"

#     square = math.pow(num1, 2)
#     cube = math.pow(num2, 3)    
#     square_root = math.sqrt(num1)
#     cube_root = math.pow(num2, 1/3)
#     return sum, difference, product, quotient, square, cube, square_root, cube_root

# def random_number():
#     random_num = random.randint(1, 100)
#     print(f"Generated random number: {random_num}")
#     return random_num

# result = calculator(random_number(), random_number())
# print(f"Random Calculator:")
# print(f"Addition: {result[0]}")
# print(f"Subtraction: {result[1]}")
# print(f"Multiplication: {result[2]}")
# print(f"Division: {result[3]:.2f}")
# print(f"Square: {result[4]}")
# print(f"Cube: {result[5]}")
# print(f"Square Root: {result[6]:.2f}")
# print(f"Cube Root: {result[7]:.2f}")

# #Object Oriented Programming in Python
# class F1:
#     def __init__(self, driver, team):
#         self.driver = driver
#         self.team = team

#     def display_info(self):
#         print(f"Driver: {self.driver}, Team: {self.team}")
# driver1 = F1("Lewis Hamilton", "Ferrari")
# driver2 = F1("Max Verstappen", "Red Bull Racing")
# driver3 = F1("Kimi Räikkönen", "Mercedes")
# driver1.display_info()
# driver2.display_info()
# driver3.display_info()

# #Class inheritance in Python
# class vehicles:
#     def __init__(self,):
#         self.type = "Vehicle"
#     def display_type(self):
#         print(f"Type: {self.type}")

# class car(vehicles):
#     def __init__(self, brand, model):
#         super().__init__()
#         self.brand = brand
#         self.model = model
#     def display_info(self):
#         print(f"Brand: {self.brand}, Model: {self.model}")

# car1 = car("Toyota", "Camry")
# car1.display_type() #accessing the attributes of parent class
# car1.display_info() 


#Pillars of OOP in Python
from abc import ABC, abstractmethod

# Abstraction
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

# Inheritance & Encapsulation
class Rectangle(Shape):
    def __init__(self, width, height):
        self.__width = width    # private attribute
        self.__height = height

    # Polymorphism
    def area(self):
        return self.__width * self.__height

r = Rectangle(5, 10)
print(r.area())  # Output: 50