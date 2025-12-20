#!/usr/bin/env python3
"""
JAC Programming Lesson Content Population Script
Populates the lesson_content column with rich tutorial content for each JAC programming concept
"""

import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from database.models.sqlite_models import Concept, LearningPath, LearningPathConcept

def populate_lesson_content(db: Session):
    """Populate JAC concepts with rich lesson content"""
    print("📚 Populating JAC Concepts with Rich Lesson Content...")
    
    # Check if concepts exist
    concepts = db.query(Concept).filter(Concept.category == "JAC Programming").all()
    if not concepts:
        print("❌ No JAC concepts found. Run seed_jac_concepts.py first!")
        return
    
    print(f"Found {len(concepts)} JAC concepts to populate with content")
    
    # Define rich lesson content for each concept
    lesson_contents = {
        "jac_programming_fundamentals": """
# JAC Programming Fundamentals

## What is JAC?

JAC (Java-like Architecture for Computation) is a revolutionary programming language that introduces **Object-Spatial Programming (OSP)** - a paradigm where computation moves to data instead of data moving to computation.

## Key Concepts

### Dual Programming Paradigm
JAC offers two complementary approaches:
1. **Traditional Programming**: Familiar sequential, procedural code
2. **Object-Spatial Programming**: Graph-based, distributed computation

### Object-Spatial Programming (OSP)
OSP is built on three fundamental concepts:
- **Nodes**: Stateful entities that hold data
- **Edges**: Typed relationships between nodes
- **Walkers**: Mobile computation that traverses graphs

## Why JAC?

### Traditional Programming Problems
- **Scalability**: Hard to scale from single-user to millions
- **Persistence**: Manual database integration required
- **Distribution**: Complex distributed system development
- **State Management**: Difficult to manage application state

### JAC Solutions
- **Scale-Agnostic**: Code works for 1 user or 1 million without changes
- **Automatic Persistence**: Data persists automatically
- **Natural Distribution**: Built for distributed applications
- **Spatial Computation**: Computation moves to data

## Development Environment Setup

### Installation
```bash
# Install JAC compiler
pip install jac-lang

# Create new JAC project
jac new my_jac_app
cd my_jac_app
```

### Basic Project Structure
```
my_jac_app/
├── main.jac          # Main application entry point
├── models/           # Object definitions
├── walkers/          # Walker implementations
└── utils/            # Utility functions
```

## Your First JAC Program

```jac
# Traditional programming approach
def main() -> int:
    name: str = "JAC Developer"
    age: int = 25
    
    print(f"Hello, {name}! You are {age} years old.")
    return 0

# Run the program
if __name__ == "__main__":
    result = main()
```

## Next Steps

In the next lesson, we'll explore JAC's type system and variable declarations.
""",

        "jac_variables_data_types": """
# JAC Variables and Data Types

## Type System Overview

JAC uses **strong typing** with explicit type annotations for all variables and collections. This ensures type safety and prevents runtime errors.

## Primitive Data Types

### String Type
```jac
name: str = "Alice Johnson"
message: str = "Welcome to JAC programming!"
multiline: str = \"\"\"This is a
multi-line
string.\"\"\"
```

### Numeric Types
```jac
# Integer
count: int = 42
negative: int = -17
large_number: int = 1_000_000

# Float
price: float = 19.99
temperature: float = -5.5
scientific: float = 1.5e-3
```

### Boolean Type
```jac
is_active: bool = True
has_permission: bool = False
is_empty: bool = len("") == 0
```

## Collection Types

### Lists
```jac
# Typed lists
names: list[str] = ["Alice", "Bob", "Charlie"]
scores: list[int] = [95, 87, 92, 88]
mixed: list = ["text", 42, True]  # Less common

# List operations
numbers: list[int] = []
numbers.append(1)
numbers.extend([2, 3, 4])
```

### Dictionaries
```jac
# Typed dictionaries
user: dict[str, str] = {
    "name": "Alice",
    "email": "alice@example.com"
}

config: dict[str, int] = {
    "port": 8080,
    "timeout": 30,
    "retries": 3
}
```

### Sets
```jac
# Unique collections
tags: set[str] = {"python", "programming", "tutorial"}
numbers: set[int] = {1, 2, 3, 3, 4}  # {1, 2, 3, 4}
```

### Tuples
```jac
# Immutable collections
coordinates: tuple[int, int] = (10, 20)
rgb_color: tuple[int, int, int] = (255, 128, 0)
person: tuple[str, int, str] = ("Alice", 25, "Engineer")
```

## Type Annotations Best Practices

### Always Specify Types
```jac
# Good - explicit typing
user_count: int = get_user_count()
messages: list[str] = process_messages()

# Avoid - implicit typing
user_count = get_user_count()  # Less clear
```

### Collection Type Annotations
```jac
# Always specify element types for collections
scores: list[int] = [95, 87, 92]      # Clear intent
users: dict[str, User] = {}           # Strong typing
valid_emails: set[str] = set()        # Initialize empty set
```

## String Formatting

### F-Strings
```jac
name: str = "Alice"
age: int = 25

# Basic f-string
greeting: str = f"Hello, {name}! You are {age} years old."

# Expressions in f-strings
message: str = f"Total: ${price * quantity:.2f}"
status: str = f"Progress: {completed}/{total} ({completed/total*100:.1f}%)"
```

### String Methods
```jac
text: str = "  JAC Programming  "

# Common string operations
cleaned: str = text.strip()           # "JAC Programming"
uppercase: str = text.upper()         # "  JAC PROGRAMMING  "
lowercase: str = text.lower()         # "  jac programming  "
replaced: str = text.replace("JAC", "Java")  # "  Java Programming  "
```

## Practice Exercises

### Exercise 1: Student Grade Calculator
```jac
def calculate_letter_grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

# Test the function
student_scores: list[int] = [95, 87, 73, 58, 42]
for score in student_scores:
    letter = calculate_letter_grade(score)
    print(f"Score {score}: Grade {letter}")
```

### Exercise 2: User Profile
```jac
def create_user_profile(name: str, age: int, email: str) -> dict[str, str]:
    return {
        "name": name,
        "age": str(age),
        "email": email,
        "status": "active" if age >= 18 else "minor"
    }

# Create user profiles
profiles: list[dict[str, str]] = [
    create_user_profile("Alice", 25, "alice@example.com"),
    create_user_profile("Bob", 17, "bob@example.com"),
    create_user_profile("Charlie", 30, "charlie@example.com")
]

for profile in profiles:
    print(f"User: {profile}")
```

## Common Mistakes to Avoid

1. **Forgetting Type Annotations**
   ```jac
   # Bad
   name = "Alice"  # Type unclear
   
   # Good
   name: str = "Alice"
   ```

2. **Incorrect Collection Types**
   ```jac
   # Bad - unclear element types
   data: list = [1, "text", True]
   
   # Good - explicit types
   data: list[int] = [1, 2, 3]
   ```

3. **Mutable Default Arguments**
   ```jac
   # Bad
   def add_item(item: str, items: list[str] = []):
       items.append(item)
   
   # Good
   def add_item(item: str, items: list[str] = None):
       if items is None:
           items = []
       items.append(item)
   ```

## Next Steps

In the next lesson, we'll explore JAC's control flow structures including conditionals, loops, and pattern matching.
""",

        "jac_control_flow": """
# JAC Control Flow

## Conditional Statements

JAC uses curly braces `{}` for code blocks, similar to C-style languages.

### Basic If-Else
```jac
def check_temperature(temp: int) -> str:
    if temp > 30:
        return "Hot"
    elif temp > 20:
        return "Warm"
    elif temp > 10:
        return "Cool"
    else:
        return "Cold"

# Test the function
temperatures: list[int] = [35, 25, 15, 5]
for temp in temperatures:
    result = check_temperature(temp)
    print(f"Temperature {temp}°C: {result}")
```

### Nested Conditionals
```jac
def classify_number(num: int) -> str:
    if num > 0:
        if num > 100:
            return "Large Positive"
        else:
            return "Small Positive"
    elif num < 0:
        if num < -100:
            return "Large Negative"
        else:
            return "Small Negative"
    else:
        return "Zero"

# Test with various numbers
test_numbers: list[int] = [150, 25, -25, -150, 0]
for num in test_numbers:
    classification = classify_number(num)
    print(f"{num}: {classification}")
```

## Loops

### While Loops
```jac
# Basic while loop
def count_to_n(n: int) -> int:
    count: int = 0
    while count < n:
        print(f"Count: {count}")
        count = count + 1
    return count

# User input simulation
def simulate_user_input() -> str:
    attempts: int = 0
    max_attempts: int = 3
    
    while attempts < max_attempts:
        print(f"Attempt {attempts + 1}/{max_attempts}")
        # Simulate user input
        user_input: str = "correct" if attempts == 2 else "wrong"
        print(f"User entered: {user_input}")
        
        if user_input == "correct":
            return "Success!"
        attempts = attempts + 1
    
    return "Failed after maximum attempts"
```

### For Loops

#### Counting Loops
```jac
# Count from 0 to 4
for i: int in range(5):
    print(f"Count: {i}")

# Count from 2 to 7
for i: int in range(2, 8):
    print(f"Count: {i}")

# Count with step
for i: int in range(0, 10, 2):
    print(f"Even number: {i}")
```

#### Iterating Collections
```jac
# Iterate over list
names: list[str] = ["Alice", "Bob", "Charlie"]
for name: str in names:
    print(f"Hello, {name}!")

# Iterate over dictionary
user: dict[str, str] = {
    "name": "Alice",
    "email": "alice@example.com",
    "role": "Developer"
}

for key: str in user:
    value: str = user[key]
    print(f"{key}: {value}")

# Iterate over dictionary items
for key: str, value: str in user.items():
    print(f"{key}: {value}")
```

#### Enumerate with Index
```jac
# Get both index and value
programming_languages: list[str] = ["Python", "JAC", "JavaScript", "Go"]

for index: int, language: str in enumerate(programming_languages):
    print(f"{index + 1}. {language}")
```

## Break and Continue

### Break Statement
```jac
def find_first_negative(numbers: list[int]) -> int:
    for num: int in numbers:
        if num < 0:
            print(f"Found first negative number: {num}")
            break
        else:
            print(f"Checking {num}: positive")
    
    return -1  # No negative found

# Test the function
positive_list: list[int] = [1, 2, 3, 4, 5]
mixed_list: list[int] = [1, 2, -3, 4, 5]

find_first_negative(positive_list)
find_first_negative(mixed_list)
```

### Continue Statement
```jac
def process_scores(scores: list[int]) -> list[int]:
    valid_scores: list[int] = []
    
    for score: int in scores:
        if score < 0 or score > 100:
            print(f"Invalid score {score}, skipping...")
            continue
        
        print(f"Processing valid score: {score}")
        valid_scores.append(score)
    
    return valid_scores

# Test with mixed data
all_scores: list[int] = [95, -5, 87, 105, 73, 0, 88]
valid_scores = process_scores(all_scores)
print(f"Valid scores: {valid_scores}")
```

## Pattern Matching

JAC supports advanced pattern matching for complex conditional logic.

### Basic Pattern Matching
```jac
def handle_http_status(status_code: int) -> str:
    match status_code:
        case 200:
            return "OK - Success"
        case 201:
            return "Created - Resource created"
        case 400:
            return "Bad Request - Invalid input"
        case 401:
            return "Unauthorized - Authentication required"
        case 403:
            return "Forbidden - Access denied"
        case 404:
            return "Not Found - Resource not found"
        case 500:
            return "Internal Server Error"
        case _:
            return f"Unknown status code: {status_code}"

# Test different status codes
status_codes: list[int] = [200, 404, 500, 999]
for code: int in status_codes:
    message: str = handle_http_status(code)
    print(f"Status {code}: {message}")
```

### Pattern Matching with Guards
```jac
def classify_age(age: int) -> str:
    match age:
        case age if age < 13:
            return "Child"
        case age if age < 18:
            return "Teenager"
        case age if age < 65:
            return "Adult"
        case age:
            return "Senior"

# Pattern matching with multiple conditions
def process_shape(shape_type: str, sides: int) -> str:
    match shape_type, sides:
        case "triangle", 3:
            return "Equilateral triangle"
        case "square", 4:
            return "Perfect square"
        case "pentagon", 5:
            return "Regular pentagon"
        case _, sides if sides < 3:
            return "Invalid shape - too few sides"
        case _:
            return f"Unknown {sides}-sided shape"
```

## Practical Examples

### Game Score Calculator
```jac
def calculate_grade(percentage: float) -> tuple[str, float]:
    match percentage:
        case percentage if percentage >= 90:
            return ("A", 4.0)
        case percentage if percentage >= 80:
            return ("B", 3.0)
        case percentage if percentage >= 70:
            return ("C", 2.0)
        case percentage if percentage >= 60:
            return ("D", 1.0)
        case _:
            return ("F", 0.0)

# Calculate grades for students
students: dict[str, float] = {
    "Alice": 95.5,
    "Bob": 87.3,
    "Charlie": 73.1,
    "Diana": 58.7
}

for name: str, score: float in students.items():
    letter: str, gpa: float = calculate_grade(score)
    print(f"{name}: {score}% → {letter} (GPA: {gpa})")
```

### Shopping Cart Validation
```jac
def validate_cart_item(item: dict[str, str]) -> tuple[bool, str]:
    name: str = item.get("name", "")
    price: str = item.get("price", "")
    quantity: str = item.get("quantity", "")
    
    # Validate name
    if len(name) == 0:
        return (False, "Item name is required")
    
    # Validate price
    try:
        price_float: float = float(price)
        if price_float <= 0:
            return (False, "Price must be positive")
    except ValueError:
        return (False, "Invalid price format")
    
    # Validate quantity
    try:
        quantity_int: int = int(quantity)
        if quantity_int <= 0:
            return (False, "Quantity must be positive")
        if quantity_int > 100:
            return (False, "Quantity too large")
    except ValueError:
        return (False, "Invalid quantity format")
    
    return (True, "Valid item")

# Test cart validation
cart: list[dict[str, str]] = [
    {"name": "Laptop", "price": "999.99", "quantity": "1"},
    {"name": "", "price": "50.00", "quantity": "2"},
    {"name": "Mouse", "price": "invalid", "quantity": "1"},
    {"name": "Keyboard", "price": "75.00", "quantity": "150"}
]

for item: dict[str, str] in cart:
    is_valid: bool, message: str = validate_cart_item(item)
    status: str = "✓" if is_valid else "✗"
    print(f"{status} {item}: {message}")
```

## Common Pitfalls

### Off-by-One Errors
```jac
# Common mistake
for i: int in range(1, 10):  # 1 to 9, missing 10
    print(i)

# Correct
for i: int in range(10):     # 0 to 9
    print(i)

# Or
for i: int in range(1, 11):  # 1 to 10
    print(i)
```

### Infinite Loops
```jac
# Dangerous - infinite loop
count: int = 0
while count < 10:
    print(count)
    # Forgot to increment count!

# Safe - proper loop
count: int = 0
while count < 10:
    print(count)
    count = count + 1  # Important!
```

## Best Practices

1. **Use Meaningful Variable Names**
   ```jac
   # Bad
   for i in range(10):
       print(i)
   
   # Good
   for student_index in range(student_count):
       print(f"Student {student_index + 1}")
   ```

2. **Keep Loops Simple**
   ```jac
   # Bad - complex nested logic
   for user in users:
       if user.active:
           for post in user.posts:
               if post.published:
                   for comment in post.comments:
                       if comment.approved:
                           process_comment(comment)
   
   # Good - break into functions
   def process_approved_comments(user: User):
       for post in user.posts:
           if post.published:
               for comment in post.comments:
                   if comment.approved:
                       process_comment(comment)
   ```

3. **Use Pattern Matching for Complex Conditions**
   ```jac
   # Instead of deeply nested if-else
   def handle_user_action(action: str, user_role: str) -> str:
       match action, user_role:
           case "delete", "admin":
               return "Permission granted"
           case "delete", _:
               return "Permission denied"
           case "edit", "admin" | "editor":
               return "Permission granted"
           case "edit", _:
               return "Permission denied"
   ```

## Next Steps

In the next lesson, we'll explore JAC functions and how to create reusable code blocks.
""",

        "jac_functions": """
# JAC Functions

## What are Functions?

Functions are reusable blocks of code that perform specific tasks. They help organize code, avoid repetition, and make programs more maintainable and readable.

## Function Syntax

### Basic Function Definition
```jac
def greet_user(name: str) -> str:
    \"\"\"Return a greeting message for the user.\"\"\"
    message: str = f"Hello, {name}! Welcome to JAC programming."
    return message

# Call the function
greeting = greet_user("Alice")
print(greeting)  # Output: Hello, Alice! Welcome to JAC programming.
```

### Function with Multiple Parameters
```jac
def calculate_area(length: float, width: float) -> float:
    \"\"\"Calculate the area of a rectangle.\"\"\"
    area: float = length * width
    return area

# Calculate area
room_area = calculate_area(12.5, 8.3)
print(f"Room area: {room_area} square meters")
```

## Function Components

### Function Signature
- **def**: Keyword to define a function
- **Function name**: Descriptive name following naming conventions
- **Parameters**: Input values in parentheses
- **Return type**: Type annotation after arrow (->)
- **Function body**: Code block in curly braces

### Documentation Strings (Docstrings)
```jac
def calculate_bmi(weight: float, height: float) -> float:
    \"\"\"
    Calculate Body Mass Index (BMI).
    
    Args:
        weight: Weight in kilograms
        height: Height in meters
    
    Returns:
        BMI value as a float
        
    Example:
        bmi = calculate_bmi(70, 1.75)
        print(f"BMI: {bmi}")
    \"\"\"
    if height <= 0:
        raise ValueError("Height must be positive")
    
    bmi: float = weight / (height * height)
    return bmi
```

## Parameters and Arguments

### Default Parameters
```jac
def create_user(username: str, email: str = "", is_active: bool = True) -> dict[str, str]:
    \"\"\"Create a user dictionary with optional parameters.\"\"\"
    user: dict[str, str] = {
        "username": username,
        "email": email if email else f"{username}@example.com",
        "status": "active" if is_active else "inactive",
        "created_at": "2024-01-01"
    }
    return user

# Using default parameters
user1 = create_user("alice")
user2 = create_user("bob", "bob@company.com")
user3 = create_user("charlie", is_active=False)
```

### Named Parameters
```jac
def configure_application(port: int, host: str = "localhost", debug: bool = False) -> dict[str, str]:
    \"\"\"Configure application settings.\"\"\"
    return {
        "port": port,
        "host": host,
        "debug": debug,
        "ssl": port == 443
    }

# Using named parameters
config1 = configure_application(8080, debug=True)
config2 = configure_application(host="0.0.0.0", port=3000)
config3 = configure_application(port=443, host="secure.example.com", debug=False)
```

## Return Values

### Single Return Value
```jac
def get_square(number: int) -> int:
    return number * number

result = get_square(5)  # 25
```

### Multiple Return Values (Tuples)
```jac
def divide_numbers(dividend: float, divisor: float) -> tuple[float, str]:
    \"\"\"Divide two numbers and return result with status.\"\"\"
    if divisor == 0:
        return (0.0, "Cannot divide by zero")
    
    result: float = dividend / divisor
    status: str = "Success"
    return (result, status)

# Use multiple return values
quotient, message = divide_numbers(10, 2)
print(f"{message}: {quotient}")

quotient, message = divide_numbers(10, 0)
print(f"{message}: {quotient}")
```

### Early Returns
```jac
def find_maximum(numbers: list[int]) -> int:
    \"\"\"Find the maximum number in a list.\"\"\"
    if len(numbers) == 0:
        return 0  # Early return for empty list
    
    if len(numbers) == 1:
        return numbers[0]  # Early return for single element
    
    max_num: int = numbers[0]
    for num: int in numbers[1:]:
        if num > max_num:
            max_num = num
    
    return max_num
```

## Function Types and Patterns

### Pure Functions
```jac
def add_numbers(a: int, b: int) -> int:
    \"\"\"Pure function - same input always gives same output.\"\"\"
    return a + b

# No side effects, deterministic
result1 = add_numbers(5, 3)  # Always 8
result2 = add_numbers(5, 3)  # Always 8
```

### Functions with Side Effects
```jac
# Global variable (generally avoid)
total_score: int = 0

def add_to_total(score: int) -> None:
    \"\"\"Function that modifies external state.\"\"\"
    global total_score
    total_score = total_score + score
    print(f"Added {score}. New total: {total_score}")

# Better approach - return new state
def add_to_score(score: int, current_total: int) -> int:
    \"\"\"Function that returns new state.\"\"\"
    new_total: int = current_total + score
    return new_total
```

### Higher-Order Functions
```jac
def apply_operation(numbers: list[int], operation: def(int) -> int) -> list[int]:
    \"\"\"Apply a function to each number in a list.\"\"\"
    result: list[int] = []
    for num: int in numbers:
        result.append(operation(num))
    return result

# Define operations
def square(x: int) -> int:
    return x * x

def double(x: int) -> int:
    return x * 2

# Use higher-order function
numbers: list[int] = [1, 2, 3, 4, 5]
squared = apply_operation(numbers, square)      # [1, 4, 9, 16, 25]
doubled = apply_operation(numbers, double)      # [2, 4, 6, 8, 10]
```

## Advanced Function Patterns

### Recursive Functions
```jac
def factorial(n: int) -> int:
    \"\"\"Calculate factorial of a number recursively.\"\"\"
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

# Calculate factorials
for i: int in range(1, 6):
    result: int = factorial(i)
    print(f"{i}! = {result}")
```

### Generator Functions
```jac
def fibonacci_sequence(count: int) -> list[int]:
    \"\"\"Generate Fibonacci sequence.\"\"\"
    if count <= 0:
        return []
    if count == 1:
        return [0]
    if count == 2:
        return [0, 1]
    
    sequence: list[int] = [0, 1]
    for i: int in range(2, count):
        next_num: int = sequence[i-1] + sequence[i-2]
        sequence.append(next_num)
    
    return sequence

# Generate Fibonacci sequence
fib_sequence = fibonacci_sequence(10)
print(f"Fibonacci: {fib_sequence}")
```

### Functions with Error Handling
```jac
def safe_divide(numerator: float, denominator: float) -> tuple[float, str]:
    \"\"\"Safely divide two numbers with error handling.\"\"\"
    try:
        if denominator == 0:
            return (0.0, "Error: Division by zero")
        
        result: float = numerator / denominator
        return (result, "Success")
    except Exception as e:
        return (0.0, f"Error: {str(e)}")

# Test safe division
test_cases: list[tuple[float, float]] = [
    (10, 2),
    (10, 0),
    (5.5, 2.2),
    (100, -5)
]

for num, denom in test_cases:
    result, message = safe_divide(num, denom)
    print(f"{num} / {denom} = {result} ({message})")
```

## Practical Examples

### Data Processing Functions
```jac
def process_student_data(students: list[dict[str, str]]) -> dict[str, float]:
    \"\"\"Process student data and return statistics.\"\"\"
    if len(students) == 0:
        return {"average_grade": 0.0, "pass_rate": 0.0}
    
    total_grade: float = 0.0
    passed_count: int = 0
    
    for student: dict[str, str] in students:
        try:
            grade: float = float(student["grade"])
            total_grade = total_grade + grade
            
            if grade >= 60:
                passed_count = passed_count + 1
        except (ValueError, KeyError):
            continue  # Skip invalid data
    
    average_grade: float = total_grade / len(students)
    pass_rate: float = (passed_count / len(students)) * 100
    
    return {
        "average_grade": round(average_grade, 2),
        "pass_rate": round(pass_rate, 1)
    }

# Test with sample data
students_data: list[dict[str, str]] = [
    {"name": "Alice", "grade": "95"},
    {"name": "Bob", "grade": "78"},
    {"name": "Charlie", "grade": "55"},
    {"name": "Diana", "grade": "82"}
]

stats = process_student_data(students_data)
print(f"Class Statistics: {stats}")
```

### Utility Functions
```jac
def format_currency(amount: float, currency: str = "USD") -> str:
    \"\"\"Format a number as currency.\"\"\"
    symbols: dict[str, str] = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    
    symbol: str = symbols.get(currency, currency)
    formatted: str = f"{symbol}{amount:,.2f}"
    return formatted

def validate_email(email: str) -> bool:
    \"\"\"Simple email validation.\"\"\"
    if "@" not in email:
        return False
    
    parts: list[str] = email.split("@")
    if len(parts) != 2:
        return False
    
    username, domain = parts
    return len(username) > 0 and len(domain) > 2

# Test utility functions
prices: list[float] = [19.99, 1500.00, 75.5]
for price in prices:
    print(f"Price: {format_currency(price)}")

emails: list[str] = ["user@example.com", "invalid", "test@domain"]
for email in emails:
    print(f"{email}: {'Valid' if validate_email(email) else 'Invalid'}")
```

## Best Practices

### Function Design Principles

1. **Single Responsibility**: Each function should do one thing well
2. **Descriptive Names**: Use clear, descriptive function names
3. **Small Functions**: Keep functions short and focused
4. **Pure When Possible**: Prefer pure functions over those with side effects
5. **Proper Documentation**: Include docstrings for all public functions

### Parameter Guidelines
```jac
# Good - clear parameters
def calculate_circle_area(radius: float) -> float:
    return 3.14159 * radius * radius

# Bad - unclear what parameters do
def calc(r: float) -> float:
    return 3.14159 * r * r
```

### Error Handling
```jac
# Good - proper error handling
def parse_positive_integer(value: str) -> tuple[int, str]:
    try:
        number: int = int(value)
        if number <= 0:
            return (0, "Value must be positive")
        return (number, "Success")
    except ValueError:
        return (0, "Invalid integer format")

# Bad - no error handling
def parse_number(value: str) -> int:
    return int(value)  # Can crash with invalid input
```

## Common Mistakes to Avoid

1. **Forgetting Return Statements**
   ```jac
   # Bad
   def greet(name: str):
       message = f"Hello, {name}!"
       # Missing return statement
   
   # Good
   def greet(name: str) -> str:
       return f"Hello, {name}!"
   ```

2. **Modifying Parameters Unnecessarily**
   ```jac
   # Bad - modifying input list
   def add_item_buggy(item: str, items: list[str]):
       items.append(item)  # Side effect
   
   # Good - return new list
   def add_item_good(item: str, items: list[str]) -> list[str]:
       new_items = items.copy()
       new_items.append(item)
       return new_items
   ```

3. **Complex Parameter Lists**
   ```jac
   # Bad - too many parameters
   def create_user_complex(name: str, email: str, age: int, city: str, country: str, is_active: bool) -> dict:
       # ...
   
   # Good - use configuration objects
   def create_user_good(config: dict[str, str]) -> dict:
       # ...
   ```

## Next Steps

In the next lesson, we'll explore JAC collections and data structures, learning how to work with lists, dictionaries, sets, and more advanced data organization techniques.
""",

        "jac_collections": """
# JAC Collections and Data Structures

## Overview of Collections

Collections are data structures that store multiple values. JAC provides several types of collections, each with specific characteristics and use cases.

## List Operations

### Creating and Initializing Lists
```jac
# Empty list
empty_list: list[int] = []

# List with initial values
numbers: list[int] = [1, 2, 3, 4, 5]
names: list[str] = ["Alice", "Bob", "Charlie"]
mixed: list = [1, "hello", True, 3.14]

# List comprehension
squares: list[int] = [x * x for x in range(1, 6)]  # [1, 4, 9, 16, 25]
evens: list[int] = [x for x in range(1, 11) if x % 2 == 0]
```

### Adding and Removing Elements
```jac
# Adding elements
items: list[str] = []
items.append("first")      # ["first"]
items.extend(["second", "third"])  # ["first", "second", "third"]
items.insert(1, "inserted")  # ["first", "inserted", "second", "third"]

# Removing elements
items.remove("inserted")   # Removes first occurrence
popped: str = items.pop()  # Removes and returns last item
deleted: str = items.pop(0)  # Removes and returns first item

# Clearing list
items.clear()
```

### List Methods and Operations
```jac
# List methods
numbers: list[int] = [3, 1, 4, 1, 5, 9, 2, 6]

# Sorting
numbers.sort()             # [1, 1, 2, 3, 4, 5, 6, 9]
numbers.sort(reverse=True)  # [9, 6, 5, 4, 3, 2, 1, 1]

# Counting and finding
count_of_ones: int = numbers.count(1)  # 2
index_of_four: int = numbers.index(4)  # 3

# List operations
list1: list[int] = [1, 2, 3]
list2: list[int] = [4, 5, 6]
combined: list[int] = list1 + list2    # [1, 2, 3, 4, 5, 6]
repeated: list[str] = ["x"] * 3        # ["x", "x", "x"]
```

### Slicing Lists
```jac
fruits: list[str] = ["apple", "banana", "cherry", "date", "elderberry"]

# Basic slicing
first_three: list[str] = fruits[0:3]    # ["apple", "banana", "cherry"]
last_two: list[str] = fruits[-2:]       # ["date", "elderberry"]
middle: list[str] = fruits[1:4]         # ["banana", "cherry", "date"]

# Advanced slicing
every_other: list[str] = fruits[::2]     # ["apple", "cherry", "elderberry"]
reverse: list[str] = fruits[::-1]       # ["elderberry", "date", "cherry", "banana", "apple"]
```

## Dictionary Operations

### Creating and Accessing Dictionaries
```jac
# Empty dictionary
user_profile: dict[str, str] = {}

# Dictionary with initial values
user: dict[str, str] = {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "role": "Developer"
}

# Accessing values
name: str = user["name"]                # "Alice Johnson"
role: str = user.get("role", "User")    # "Developer" (with default)

# Adding and updating
user["age"] = 25                        # Add new key-value pair
user.update({"city": "New York", "active": True})  # Update multiple values
```

### Dictionary Methods
```jac
user: dict[str, str] = {"name": "Alice", "email": "alice@example.com", "active": True}

# Getting keys, values, and items
keys: list[str] = list(user.keys())     # ["name", "email", "active"]
values: list = list(user.values())      # ["Alice", "alice@example.com", True]
items: list[tuple[str, str]] = list(user.items())  # [("name", "Alice"), ...]

# Dictionary methods
has_email: bool = "email" in user       # True
name_exists: bool = user.pop("name", None) is not None  # Remove and check

# Dictionary comprehensions
squared_numbers: dict[int, int] = {x: x*x for x in range(1, 6)}  # {1:1, 2:4, 3:9, 4:16, 5:25}
```

### Nested Dictionaries
```jac
# Complex nested structure
company: dict[str, str | dict] = {
    "name": "TechCorp",
    "founded": 2020,
    "location": {
        "city": "San Francisco",
        "state": "CA",
        "country": "USA"
    },
    "employees": {
        "Alice": {"role": "Engineer", "level": "Senior"},
        "Bob": {"role": "Designer", "level": "Junior"}
    }
}

# Accessing nested values
city: str = company["location"]["city"]  # "San Francisco"
alice_role: str = company["employees"]["Alice"]["role"]  # "Engineer"
```

## Set Operations

### Creating and Using Sets
```jac
# Creating sets
empty_set: set[int] = set()                    # Empty set (not {})
numbers_set: set[int] = {1, 2, 3, 4, 5}        # Set with values
from_list: set[str] = set(["apple", "banana"])  # Convert list to set

# Set operations
set1: set[int] = {1, 2, 3, 4}
set2: set[int] = {3, 4, 5, 6}

# Mathematical operations
union: set[int] = set1 | set2                  # {1, 2, 3, 4, 5, 6}
intersection: set[int] = set1 & set2           # {3, 4}
difference: set[int] = set1 - set2             # {1, 2}
symmetric_diff: set[int] = set1 ^ set2         # {1, 2, 5, 6}

# Set methods
set1.add(6)                                    # Add element
set1.remove(1)                                 # Remove element (raises error if not found)
set1.discard(1)                                # Remove element (no error if not found)
```

### Set Comprehensions and Use Cases
```jac
# Set comprehension
evens: set[int] = {x for x in range(1, 11) if x % 2 == 0}  # {2, 4, 6, 8, 10}

# Practical uses
# Remove duplicates from list
data: list[int] = [1, 2, 2, 3, 3, 3, 4, 5]
unique_data: list[int] = list(set(data))       # [1, 2, 3, 4, 5]

# Membership testing (very fast)
allowed_emails: set[str] = {"admin@example.com", "user@example.com"}
user_email: str = "user@example.com"
is_allowed: bool = user_email in allowed_emails  # True (O(1) lookup)
```

## Tuple Operations

### Creating and Using Tuples
```jac
# Creating tuples
empty_tuple: tuple = ()
single_item: tuple[int] = (42,)
coordinates: tuple[int, int] = (10, 20)
rgb_color: tuple[int, int, int] = (255, 128, 0)

# Tuple unpacking
x: int
y: int
x, y = coordinates                          # x = 10, y = 20

# Multiple assignment
name: str
age: int
city: str
name, age, city = ("Alice", 25, "New York")

# Tuple methods
numbers: tuple[int, ...] = (1, 2, 3, 2, 4, 2)
count_twos: int = numbers.count(2)         # 3
index_of_four: int = numbers.index(4)      # 4
```

## Collection Best Practices

### Type Annotations
```jac
# Always specify types for collections
names: list[str] = ["Alice", "Bob"]                    # List of strings
user_scores: dict[str, int] = {"Alice": 95, "Bob": 87}  # String to int mapping
unique_ids: set[int] = {1, 2, 3, 4, 5}                # Set of integers
coordinates: tuple[float, float] = (10.5, 20.3)        # Tuple of floats

# For complex nested structures
company_data: dict[str, str | int | list[str]] = {
    "name": "TechCorp",
    "employees": 150,
    "departments": ["Engineering", "Marketing", "Sales"]
}
```

### Performance Considerations
```jac
# Lists - good for ordered data, indexing
names: list[str] = ["Alice", "Bob", "Charlie"]
first_name: str = names[0]              # O(1) - very fast
last_name: str = names[-1]              # O(1) - very fast

# Sets - good for uniqueness and membership testing
allowed_users: set[str] = {"alice", "bob", "charlie"}
is_allowed: bool = "alice" in allowed_users  # O(1) - very fast

# Dictionaries - good for key-value lookups
user_scores: dict[str, int] = {"alice": 95, "bob": 87}
alice_score: int = user_scores["alice"]        # O(1) - very fast
```

### Common Patterns

#### Filtering Collections
```jac
# Filter list using list comprehension
scores: list[int] = [95, 87, 73, 58, 92, 45]
high_scores: list[int] = [score for score in scores if score >= 80]

# Filter dictionary
user_data: dict[str, int] = {"alice": 95, "bob": 87, "charlie": 73, "diana": 58}
passing_students: dict[str, int] = {name: score for name, score in user_data.items() if score >= 70}
```

#### Transforming Collections
```jac
# Map operation using list comprehension
names: list[str] = ["alice", "bob", "charlie"]
capitalized: list[str] = [name.title() for name in names]

# Transform dictionary values
user_scores: dict[str, int] = {"alice": 95, "bob": 87, "charlie": 73}
letter_grades: dict[str, str] = {name: "A" if score >= 90 else "B" if score >= 80 else "C" for name, score in user_scores.items()}
```

#### Grouping Data
```jac
# Grouping by using dictionaries
students: list[dict[str, str]] = [
    {"name": "Alice", "grade": "A", "subject": "Math"},
    {"name": "Bob", "grade": "B", "subject": "Math"},
    {"name": "Charlie", "grade": "A", "subject": "Science"},
    {"name": "Diana", "grade": "C", "subject": "Science"}
]

# Group by subject
by_subject: dict[str, list[dict]] = {}
for student in students:
    subject: str = student["subject"]
    if subject not in by_subject:
        by_subject[subject] = []
    by_subject[subject].append(student)
```

## Practical Examples

### Student Grade Management System
```jac
def create_gradebook() -> dict[str, list[dict]]:
    \"\"\"Create a student grade management system.\"\"\"
    gradebook: dict[str, list[dict]] = {}
    
    # Add students with multiple grades
    students: list[dict[str, str | list[int]]] = [
        {
            "name": "Alice Johnson",
            "id": "S001",
            "grades": [95, 87, 92, 88]
        },
        {
            "name": "Bob Smith",
            "id": "S002", 
            "grades": [78, 85, 79, 82]
        },
        {
            "name": "Charlie Brown",
            "id": "S003",
            "grades": [92, 96, 94, 98]
        }
    ]
    
    for student in students:
        name: str = student["name"]
        grades: list[int] = student["grades"]
        
        # Calculate statistics
        average: float = sum(grades) / len(grades)
        highest: int = max(grades)
        lowest: int = min(grades)
        
        # Determine letter grade
        if average >= 90:
            letter: str = "A"
        elif average >= 80:
            letter = "B"
        elif average >= 70:
            letter = "C"
        else:
            letter = "F"
        
        student_record: dict = {
            "name": name,
            "id": student["id"],
            "grades": grades,
            "average": round(average, 2),
            "highest": highest,
            "lowest": lowest,
            "letter_grade": letter
        }
        
        gradebook[name] = [student_record]
    
    return gradebook

# Test the gradebook system
book = create_gradebook()
for name, records in book.items():
    for record in records:
        print(f"{record['name']} ({record['id']}): Average {record['average']} ({record['letter_grade']})")
```

### Inventory Management
```jac
def manage_inventory() -> dict[str, dict]:
    \"\"\"Manage product inventory with categories.\"\"\"
    inventory: dict[str, dict] = {}
    
    # Product data
    products: list[dict] = [
        {
            "id": "P001",
            "name": "Laptop",
            "category": "Electronics",
            "price": 999.99,
            "stock": 15,
            "suppliers": ["TechCorp", "ElectroSupply"]
        },
        {
            "id": "P002",
            "name": "Office Chair",
            "category": "Furniture",
            "price": 199.99,
            "stock": 8,
            "suppliers": ["FurnitureCo"]
        },
        {
            "id": "P003",
            "name": "Monitor",
            "category": "Electronics", 
            "price": 299.99,
            "stock": 0,
            "suppliers": ["TechCorp", "DisplayPro"]
        }
    ]
    
    for product in products:
        product_id: str = product["id"]
        category: str = product["category"]
        
        # Add to inventory
        inventory[product_id] = product
        
        # Track categories
        if category not in inventory:
            inventory[category] = {"products": [], "total_value": 0.0}
        
        inventory[category]["products"].append(product_id)
        inventory[category]["total_value"] += product["price"] * product["stock"]
    
    return inventory

# Test inventory management
inv = manage_inventory()

# Show low stock items
print("Low Stock Alert:")
for product_id, product in inv.items():
    if isinstance(product, dict) and "stock" in product:
        if product["stock"] < 10:
            print(f"- {product['name']}: {product['stock']} units")

# Show category totals
print("\\nCategory Totals:")
for category, data in inv.items():
    if isinstance(data, dict) and "total_value" in data:
        print(f"- {category}: ${data['total_value']:.2f}")
```

### Social Network Friend System
```jac
def create_social_network() -> dict[str, set]:
    \"\"\"Create a simple social network with friend connections.\"\"\"
    network: dict[str, set] = {}
    
    # Friend connections (bidirectional)
    connections: list[tuple[str, str]] = [
        ("Alice", "Bob"),
        ("Alice", "Charlie"),
        ("Bob", "Diana"),
        ("Charlie", "Diana"),
        ("Diana", "Eve")
    ]
    
    # Initialize user sets
    all_users: set[str] = set()
    for user1, user2 in connections:
        all_users.add(user1)
        all_users.add(user2)
    
    for user in all_users:
        network[user] = set()
    
    # Add connections
    for user1, user2 in connections:
        network[user1].add(user2)
        network[user2].add(user1)  # Bidirectional
    
    return network

def find_mutual_friends(network: dict[str, set], user1: str, user2: str) -> set:
    \"\"\"Find mutual friends between two users.\"\"\"
    if user1 not in network or user2 not in network:
        return set()
    
    friends1: set = network[user1]
    friends2: set = network[user2]
    return friends1 & friends2  # Intersection

def suggest_friends(network: dict[str, set], user: str) -> set:
    \"\"\"Suggest friends based on friend-of-friend logic.\"\"\"
    if user not in network:
        return set()
    
    friends: set = network[user]
    suggestions: set = set()
    
    for friend in friends:
        friend_of_friends: set = network[friend]
        # Add friends of friends (excluding self and existing friends)
        suggestions.update(friend_of_friends - friends - {user})
    
    return suggestions

# Test social network
network = create_social_network()

print("Social Network Connections:")
for user, friends in network.items():
    print(f"{user}: friends with {list(friends)}")

# Find mutual friends
mutual = find_mutual_friends(network, "Alice", "Diana")
print(f"\\nMutual friends between Alice and Diana: {list(mutual)}")

# Suggest friends
suggestions = suggest_friends(network, "Alice")
print(f"\\nFriend suggestions for Alice: {list(suggestions)}")
```

## Common Mistakes to Avoid

### 1. Modifying Collections While Iterating
```jac
# Bad - modifying list while iterating
numbers: list[int] = [1, 2, 3, 4, 5]
for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)  # Dangerous!

# Good - create new list
numbers: list[int] = [1, 2, 3, 4, 5]
even_numbers: list[int] = [num for num in numbers if num % 2 != 0]
```

### 2. Dictionary Key Errors
```jac
# Bad - accessing non-existent key
user: dict[str, str] = {"name": "Alice"}
age: int = user["age"]  # KeyError!

# Good - use get() method
age: int = user.get("age", 0)  # Returns 0 if key doesn't exist
```

### 3. Set vs Dictionary Confusion
```jac
# Bad - using {} for empty set
empty_set: set = {}  # This creates an empty dictionary!

# Good - use set() constructor
empty_set: set = set()

# Good - set with values
my_set: set = {1, 2, 3}  # This is correct
```

### 4. Mutable Default Arguments
```jac
# Bad - mutable default argument
def add_item(item: str, items: list[str] = []):
    items.append(item)

# Good - use None and create new list
def add_item(item: str, items: list[str] = None):
    if items is None:
        items = []
    items.append(item)
```

## Memory and Performance Tips

### Choose the Right Collection
- **List**: When order matters and you need indexing
- **Dictionary**: When you need key-value lookups
- **Set**: When you need to test membership or remove duplicates
- **Tuple**: When data shouldn't be modified

### Efficient Operations
```jac
# Use set for membership testing (O(1))
large_list: list[int] = list(range(1000000))
large_set: set[int] = set(large_list)

# Check membership
is_in_list: bool = 999999 in large_list      # O(n) - slow
is_in_set: bool = 999999 in large_set        # O(1) - fast

# Use dictionary for frequency counting
text: str = "hello world hello python world"
word_counts: dict[str, int = {}
for word in text.split():
    word_counts[word] = word_counts.get(word, 0) + 1
```

## Next Steps

In the next lesson, we'll explore JAC's Object-Oriented Programming features, learning how to create classes, objects, and implement the unique interface/implementation separation that JAC provides.
""",

        "jac_oop": """
# JAC Object-Oriented Programming

## Introduction to JAC Objects

JAC's Object-Oriented Programming uses the `obj` keyword to define classes, which is different from traditional class-based languages. Objects in JAC are designed to work seamlessly with the Object-Spatial Programming paradigm.

## Basic Object Definition

### Creating Objects with `obj`
```jac
# Define a Person object
obj Person {
    name: str
    age: int
    email: str
    
    def greet(self) -> str:
        return f"Hello, I'm {self.name}"
    
    def is_adult(self) -> bool:
        return self.age >= 18
}

# Create and use objects
person: Person = Person()
person.name = "Alice Johnson"
person.age = 25
person.email = "alice@example.com"

greeting: str = person.greet()  # "Hello, I'm Alice Johnson"
is_adult: bool = person.is_adult()  # True
```

## Interface and Implementation Separation

JAC encourages separating interface (`.jac` files) from implementation (`.impl.jac` files).

### Interface File (`person.jac`)
```jac
# Interface definition
obj Person {
    name: str
    age: int
    email: str
    
    def greet(self) -> str
    def is_adult(self) -> bool
    def update_email(self, new_email: str) -> bool
}
```

### Implementation File (`person.impl.jac`)
```jac
# Implementation
impl Person {
    def greet(self) -> str:
        return f"Hello, I'm {self.name}"
    
    def is_adult(self) -> bool:
        return self.age >= 18
    
    def update_email(self, new_email: str) -> bool:
        if "@" in new_email and "." in new_email:
            self.email = new_email
            return True
        return False
}
```

## Object Attributes and Methods

### Attribute Management
```jac
obj Student {
    student_id: str
    name: str
    grades: list[float]
    gpa: float
    
    def calculate_gpa(self) -> float:
        if len(self.grades) == 0:
            return 0.0
        
        total: float = sum(self.grades)
        self.gpa = total / len(self.grades)
        return self.gpa
    
    def add_grade(self, grade: float) -> None:
        if 0.0 <= grade <= 4.0:
            self.grades.append(grade)
            self.calculate_gpa()
    
    def get_letter_grade(self) -> str:
        if self.gpa >= 3.5:
            return "A"
        elif self.gpa >= 3.0:
            return "B"
        elif self.gpa >= 2.5:
            return "C"
        elif self.gpa >= 2.0:
            return "D"
        else:
            return "F"
}

# Create student and manage grades
student: Student = Student()
student.student_id = "S001"
student.name = "Alice Johnson"

student.add_grade(3.8)  # A
student.add_grade(3.2)  # B
student.add_grade(3.5)  # A

print(f"Student: {student.name}")
print(f"GPA: {student.gpa:.2f}")
print(f"Letter Grade: {student.get_letter_grade()}")
```

## Object Relationships

### Composition
```jac
obj Address {
    street: str
    city: str
    state: str
    zip_code: str
    
    def format_address(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"
}

obj Person {
    name: str
    age: int
    home_address: Address  # Composition
    
    def get_full_info(self) -> str:
        return f"{self.name}, {self.age}, lives at {self.home_address.format_address()}"
}

# Create objects with composition
address: Address = Address()
address.street = "123 Main St"
address.city = "Springfield"
address.state = "IL"
address.zip_code = "62701"

person: Person = Person()
person.name = "John Doe"
person.age = 30
person.home_address = address

info: str = person.get_full_info()
print(info)
```

## Inheritance in JAC

### Basic Inheritance
```jac
# Base class
obj Animal {
    name: str
    species: str
    
    def make_sound(self) -> str:
        return "Some generic sound"
    
    def describe(self) -> str:
        return f"{self.name} is a {self.species}"
}

# Derived class
obj Dog {
    extends Animal  # Inheritance
    breed: str
    
    def make_sound(self) -> str:
        return "Woof! Woof!"
    
    def describe(self) -> str:
        base_description: str = super().describe()
        return f"{base_description}, breed: {self.breed}"
}

obj Cat {
    extends Animal
    indoor: bool
    
    def make_sound(self) -> str:
        return "Meow!"
    
    def describe(self) -> str:
        base_description: str = super().describe()
        lifestyle: str = "indoor" if self.indoor else "outdoor"
        return f"{base_description}, lifestyle: {lifestyle}"
}

# Test inheritance
dog: Dog = Dog()
dog.name = "Buddy"
dog.species = "Canine"
dog.breed = "Golden Retriever"

cat: Cat = Cat()
cat.name = "Whiskers"
cat.species = "Feline"
cat.indoor = True

print(dog.describe())  # "Buddy is a Canine, breed: Golden Retriever"
print(dog.make_sound())  # "Woof! Woof!"

print(cat.describe())  # "Whiskers is a Feline, lifestyle: indoor"
print(cat.make_sound())  # "Meow!"
```

## Practical Examples

### Bank Account System
```jac
obj BankAccount {
    account_number: str
    account_holder: str
    balance: float
    transaction_history: list[dict[str, str]]
    
    def __init__(self, account_number: str, account_holder: str, initial_balance: float = 0.0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = initial_balance
        self.transaction_history = []
    
    def deposit(self, amount: float) -> bool:
        if amount > 0:
            self.balance += amount
            self.add_transaction("deposit", amount)
            return True
        return False
    
    def withdraw(self, amount: float) -> bool:
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            self.add_transaction("withdrawal", amount)
            return True
        return False
    
    def add_transaction(self, transaction_type: str, amount: float) -> None:
        transaction: dict[str, str] = {
            "type": transaction_type,
            "amount": f"${amount:.2f}",
            "balance": f"${self.balance:.2f}",
            "timestamp": "2024-01-01 12:00:00"
        }
        self.transaction_history.append(transaction)
    
    def get_statement(self) -> str:
        statement: str = f"Account: {self.account_number}\\nHolder: {self.account_holder}\\nBalance: ${self.balance:.2f}\\n\\nRecent Transactions:\\n"
        for transaction in self.transaction_history[-5:]:  # Last 5 transactions
            statement += f"- {transaction['type']}: {transaction['amount']} (Balance: {transaction['balance']})\\n"
        return statement
}

# Test bank account
account: BankAccount = BankAccount("123456789", "Alice Johnson", 1000.0)

account.deposit(500.0)
account.withdraw(200.0)
account.deposit(100.0)

print(account.get_statement())
```

### Inventory Management with Objects
```jac
obj Product {
    product_id: str
    name: str
    price: float
    stock_quantity: int
    category: str
    
    def __init__(self, product_id: str, name: str, price: float, stock_quantity: int, category: str):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock_quantity = stock_quantity
        self.category = category
    
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0
    
    def reduce_stock(self, quantity: int) -> bool:
        if quantity <= self.stock_quantity:
            self.stock_quantity -= quantity
            return True
        return False
    
    def get_value(self) -> float:
        return self.price * self.stock_quantity
    
    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.product_id,
            "name": self.name,
            "price": f"${self.price:.2f}",
            "stock": str(self.stock_quantity),
            "category": self.category,
            "in_stock": str(self.is_in_stock())
        }
}

obj Inventory {
    products: dict[str, Product]
    
    def __init__(self):
        self.products = {}
    
    def add_product(self, product: Product) -> None:
        self.products[product.product_id] = product
    
    def find_products_by_category(self, category: str) -> list[Product]:
        return [product for product in self.products.values() if product.category == category]
    
    def get_low_stock_products(self, threshold: int = 10) -> list[Product]:
        return [product for product in self.products.values() if product.stock_quantity <= threshold]
    
    def get_total_inventory_value(self) -> float:
        return sum(product.get_value() for product in self.products.values())
    
    def generate_report(self) -> str:
        report: str = "=== INVENTORY REPORT ===\\n"
        report += f"Total Products: {len(self.products)}\\n"
        report += f"Total Value: ${self.get_total_inventory_value():.2f}\\n\\n"
        
        for product in self.products.values():
            report += f"{product.name} ({product.product_id}):\\n"
            report += f"  Price: ${product.price:.2f}\\n"
            report += f"  Stock: {product.stock_quantity}\\n"
            report += f"  Category: {product.category}\\n"
            report += f"  Value: ${product.get_value():.2f}\\n\\n"
        
        return report
}

# Test inventory system
inventory: Inventory = Inventory()

# Add products
laptop: Product = Product("P001", "Gaming Laptop", 1299.99, 15, "Electronics")
mouse: Product = Product("P002", "Wireless Mouse", 29.99, 8, "Electronics")
chair: Product = Product("P003", "Office Chair", 199.99, 25, "Furniture")

inventory.add_product(laptop)
inventory.add_product(mouse)
inventory.add_product(chair)

print(inventory.generate_report())

# Check low stock
low_stock: list[Product] = inventory.get_low_stock_products(10)
print("Low Stock Items:")
for product in low_stock:
    print(f"- {product.name}: {product.stock_quantity} units")
```

## Best Practices

### Object Design Principles

1. **Single Responsibility**: Each object should have one clear purpose
2. **Encapsulation**: Keep internal state private, provide public methods
3. **Clear Interfaces**: Make object methods intuitive and well-documented
4. **Composition over Inheritance**: Prefer composition when possible

### JAC-Specific Guidelines

```jac
# Good - clear object design
obj User {
    username: str
    email: str
    created_at: str
    
    def validate_email(self) -> bool:
        return "@" in self.email and "." in self.email
    
    def get_display_name(self) -> str:
        return self.username.title()
}

# Avoid - overly complex objects
obj UserManagerAuthenticatorValidator {  # Too many responsibilities!
    # This should be split into multiple objects
}
```

### Error Handling in Objects
```jac
obj Calculator {
    def divide(self, a: float, b: float) -> tuple[float, str]:
        if b == 0:
            return (0.0, "Error: Division by zero")
        return (a / b, "Success")
    
    def sqrt(self, value: float) -> tuple[float, str]:
        if value < 0:
            return (0.0, "Error: Cannot calculate square root of negative number")
        import math
        return (math.sqrt(value), "Success")
}

# Use error handling
calc: Calculator = Calculator()
result, message = calc.divide(10, 2)
print(f"{message}: {result}")

result, message = calc.sqrt(-4)
print(f"{message}: {result}")
```

## Common Mistakes to Avoid

### 1. Forgetting Object Initialization
```jac
# Bad - uninitialized object
person: Person
print(person.name)  # Error!

# Good - proper initialization
person: Person = Person()
person.name = "Alice"
```

### 2. Mixing Interface and Implementation
```jac
# Bad - mixing concerns
obj BadObject {
    def complex_method(self) -> str:
        # Implementation mixed with interface
        data = self.fetch_data()
        processed = self.process_data(data)
        return self.format_output(processed)

# Good - separate interface and implementation
obj GoodObject {
    def complex_method(self) -> str

# In implementation file (.impl.jac)
impl GoodObject {
    def complex_method(self) -> str:
        data = self.fetch_data()
        processed = self.process_data(data)
        return self.format_output(processed)
```

### 3. Inadequate Error Handling
```jac
# Bad - no error handling
obj BankAccount {
    balance: float
    
    def withdraw(self, amount: float) -> None:
        self.balance -= amount  # Could go negative!

# Good - proper error handling
obj SafeBankAccount {
    balance: float
    
    def withdraw(self, amount: float) -> bool:
        if amount <= self.balance:
            self.balance -= amount
            return True
        return False
```

## Next Steps

In the next lesson, we'll explore JAC's revolutionary Object-Spatial Programming (OSP) paradigm, where computation moves to data through nodes, edges, and walkers.
""",

        "jac_object_spatial_programming": """
# JAC Object-Spatial Programming (OSP)

## What is Object-Spatial Programming?

Object-Spatial Programming (OSP) is JAC's revolutionary paradigm where **computation moves to data** instead of data moving to computation. This paradigm enables truly scalable, distributed applications without architectural changes.

## Core OSP Concepts

### The Three Pillars of OSP

1. **Nodes**: Stateful entities that hold data
2. **Edges**: Typed relationships between nodes  
3. **Walkers**: Mobile computation that traverses graphs

## Understanding the OSP Paradigm

### Traditional Programming vs OSP

#### Traditional Approach (Data Moves to Computation)
```jac
# Traditional - data is processed centrally
def process_user_data(users: list[User]) -> dict:
    results: dict = {}
    for user in users:
        # Computation happens here, data comes to computation
        analysis = analyze_user_behavior(user)
        results[user.id] = analysis
    return results
```

#### OSP Approach (Computation Moves to Data)
```jac
# OSP - computation travels to where data lives
def analyze_user_behavior(user: User) -> Analysis:
    # Analysis logic moves to the user node
    # Data stays in place, computation comes to it
    return Analysis(...)
```

## Nodes in Detail

### Creating Nodes
```jac
# Define a User node
node User {
    username: str
    email: str
    friends: list[User]  # Relationships to other User nodes
    posts: list[Post]    # Relationship to Post nodes
    created_at: str
    
    def get_friend_count(self) -> int:
        return len(self.friends)
    
    def is_active_user(self) -> bool:
        return len(self.posts) > 0
}

# Create user nodes
alice: User = User()
alice.username = "alice_dev"
alice.email = "alice@example.com"
alice.created_at = "2024-01-01"

bob: User = User()
bob.username = "bob_coder"
bob.email = "bob@example.com"
bob.created_at = "2024-01-02"

# Create relationship (edge) between users
alice.friends.append(bob)
bob.friends.append(alice)
```

### Node Properties and Methods
```jac
node Product {
    product_id: str
    name: str
    price: float
    category: str
    reviews: list[Review]
    average_rating: float
    
    def calculate_average_rating(self) -> float:
        if len(self.reviews) == 0:
            return 0.0
        
        total_rating: float = sum(review.rating for review in self.reviews)
        self.average_rating = total_rating / len(self.reviews)
        return self.average_rating
    
    def get_top_reviews(self, limit: int = 3) -> list[Review]:
        sorted_reviews: list[Review] = sorted(
            self.reviews, 
            key=lambda r: r.rating, 
            reverse=True
        )
        return sorted_reviews[:limit]
    
    def is_highly_rated(self) -> bool:
        return self.average_rating >= 4.0
}
```

## Edges in Detail

### Creating Typed Relationships
```jac
# Define relationship types
edge FriendOf {
    strength: float  # How strong the friendship is (0.0 to 1.0)
    since: str       # When the friendship started
    mutual: bool     # Whether it's mutual
}

edge Purchased {
    quantity: int
    purchase_date: str
    price_paid: float
}

edge Reviewed {
    rating: int      # 1-5 stars
    comment: str
    review_date: str
    helpful_votes: int
}

# Create nodes
user1: User = User()
user2: User = User()
product1: Product = Product()

# Create relationships
user1 -- FriendOf {strength: 0.8, since: "2024-01-15", mutual: true} --> user2
user1 -- Purchased {quantity: 2, purchase_date: "2024-02-01", price_paid: 199.98} --> product1
user1 -- Reviewed {rating: 5, comment: "Great product!", review_date: "2024-02-02", helpful_votes: 12} --> product1
```

### Edge Properties and Navigation
```jac
node SocialMediaUser {
    username: str
    posts: list[Post]
    followers: list[SocialMediaUser]
    following: list[SocialMediaUser]
    
    def get_mutual_followers(self, other_user: SocialMediaUser) -> list[SocialMediaUser]:
        # Find users that both follow
        mutual: list[SocialMediaUser] = []
        for follower in self.followers:
            if follower in other_user.following:
                mutual.append(follower)
        return mutual
    
    def get_engagement_rate(self) -> float:
        if len(self.posts) == 0:
            return 0.0
        
        total_engagement: float = sum(post.likes + post.comments for post in self.posts)
        follower_count: float = len(self.followers)
        
        if follower_count == 0:
            return 0.0
        
        return total_engagement / follower_count
}
```

## Walkers in Detail

### Creating Walkers
```jac
# Define a walker that finds popular content
walker PopularContentFinder {
    min_likes: int
    found_content: list[Post]
    
    can find_popular_posts(post: Post) -> None:
        if post.likes >= self.min_likes:
            self.found_content.append(post)
    
    can analyze_user_activity(user: SocialMediaUser) -> dict:
        stats: dict = {
            "user": user.username,
            "post_count": len(user.posts),
            "follower_count": len(user.followers),
            "engagement_rate": user.get_engagement_rate()
        }
        return stats
}

# Create and use walker
finder: PopularContentFinder = PopularContentFinder()
finder.min_likes = 100

# Walker automatically visits nodes and executes appropriate abilities
finder.spawn()  # Starts traversing the graph
```

### Walker Abilities and Traversal
```jac
# Walker for friend recommendation
walker FriendRecommender {
    target_user: SocialMediaUser
    recommendations: list[SocialMediaUser]
    
    can visit_social_media_user(user: SocialMediaUser) -> None:
        # Skip the target user
        if user == self.target_user:
            return
        
        # Check if user is not already a friend
        if user not in self.target_user.following:
            # Calculate similarity score
            similarity: float = self.calculate_similarity(self.target_user, user)
            
            if similarity > 0.3:  # Threshold for recommendation
                self.recommendations.append(user)
    
    def calculate_similarity(user1: SocialMediaUser, user2: SocialMediaUser) -> float:
        # Simple similarity based on mutual followers
        common_followers: int = len(set(user1.followers) & set(user2.followers))
        total_followers: int = len(set(user1.followers) | set(user2.followers))
        
        if total_followers == 0:
            return 0.0
        
        return common_followers / total_followers
}

# Use friend recommender
recommender: FriendRecommender = FriendRecommender()
recommender.target_user = current_user
recommender.spawn()

print(f"Friend recommendations for {current_user.username}:")
for user in recommender.recommendations:
    print(f"- {user.username}")
```

## Graph Traversal Patterns

### Depth-First Search
```jac
walker DepthFirstExplorer {
    visited: set[User]
    path: list[User]
    max_depth: int
    
    can visit_user(user: User) -> None:
        if user in self.visited or len(self.path) > self.max_depth:
            return
        
        self.visited.add(user)
        self.path.append(user)
        
        # Visit friends of current user
        for friend in user.friends:
            self.visit_user(friend)
        
        # Backtrack
        self.path.pop()

# Find all users within 3 degrees of separation
explorer: DepthFirstExplorer = DepthFirstExplorer()
explorer.max_depth = 3
explorer.visit_user(start_user)
```

### Breadth-First Search
```jac
walker NetworkAnalyzer {
    levels: dict[int, list[User]]
    
    can visit_social_media_user(user: SocialMediaUser) -> None:
        # This walker processes nodes level by level
        # Implementation depends on graph structure
        pass
```

## Practical OSP Examples

### Social Network Analysis
```jac
# Complete social network system
node Person {
    name: str
    age: int
    interests: list[str]
    friends: list[Person]
    posts: list[SocialPost]
    
    def get_mutual_friends(self, other: Person) -> list[Person]:
        return list(set(self.friends) & set(other.friends))
    
    def suggest_activity(self) -> str:
        # OSP: Computation moves to data
        common_interests: list[str] = []
        for interest in self.interests:
            if any(interest in friend.interests for friend in self.friends):
                common_interests.append(interest)
        
        if common_interests:
            return f"Suggested activity based on friends' interests: {common_interests[0]}"
        return "No common interests found with friends"
}

walker SocialActivityRecommender {
    person: Person
    recommendations: list[str]
    
    can visit_person(p: Person) -> None:
        if p == self.person:
            return
        
        # OSP: Analysis happens at each node
        activity: str = p.suggest_activity()
        if activity not in self.recommendations:
            self.recommendations.append(activity)
    
    can finish() -> list[str]:
        return self.recommendations
}

# Use the recommender
recommender: SocialActivityRecommender = SocialActivityRecommender()
recommender.person = alice
recommender.spawn()

for recommendation in recommender.recommendations:
    print(f"Activity suggestion: {recommendation}")
```

### E-commerce Recommendation System
```jac
node Customer {
    customer_id: str
    purchase_history: list[Product]
    preferences: list[str]
    similar_customers: list[Customer]
    
    def get_purchase_categories(self) -> list[str]:
        categories: set[str] = set()
        for product in self.purchase_history:
            categories.add(product.category)
        return list(categories)
}

node Product {
    product_id: str
    name: str
    category: str
    price: float
    customers_who_bought: list[Customer]
    
    def get_customer_similarity(self, other_product: Product) -> float:
        common_customers: int = len(set(self.customers_who_bought) & set(other_product.customers_who_bought))
        total_customers: int = len(set(self.customers_who_bought) | set(other_product.customers_who_bought))
        
        if total_customers == 0:
            return 0.0
        
        return common_customers / total_customers
}

walker ProductRecommender {
    customer: Customer
    recommendations: list[Product]
    
    can visit_customer(c: Customer) -> None:
        if c == self.customer:
            return
        
        # Find products that similar customers bought
        for product in c.purchase_history:
            if product not in self.customer.purchase_history:
                if product not in self.recommendations:
                    self.recommendations.append(product)
    
    can visit_product(p: Product) -> None:
        # Also recommend based on product similarity
        for customer_product in self.customer.purchase_history:
            similarity: float = p.get_customer_similarity(customer_product)
            if similarity > 0.5 and p not in self.recommendations:
                self.recommendations.append(p)
}

# Generate recommendations
recommender: ProductRecommender = ProductRecommender()
recommender.customer = current_customer
recommender.spawn()

print("Recommended products:")
for product in recommender.recommendations[:5]:  # Top 5
    print(f"- {product.name} (${product.price:.2f})")
```

## Scale-Agnostic Programming

### The Magic of OSP
```jac
# This same code works for 1 user or 1 million users
walker SimpleActivityTracker {
    activity_count: int
    
    can visit_user(user: User) -> None:
        self.activity_count += len(user.posts)
        self.activity_count += len(user.friends)
    
    can visit_social_media_user(user: SocialMediaUser) -> None:
        self.activity_count += len(user.posts)
        self.activity_count += len(user.followers)
    
    def get_final_count(self) -> int:
        return self.activity_count
}

# Works the same whether you have 10 users or 10 million users!
tracker: SimpleActivityTracker = SimpleActivityTracker()
tracker.spawn()
total_activity: int = tracker.get_final_count()
```

## Best Practices for OSP

### 1. Design Nodes with Local Intelligence
```jac
# Good - nodes have smart behavior
node SmartUser {
    def get_relevant_content(self) -> list[Content]:
        # Node knows how to find its own relevant content
        return [content for content in self.feed if content.matches_interests(self.interests)]
}

# Avoid - centralized intelligence
node DumbUser {
    # All intelligence should be in the node, not in external functions
}
```

### 2. Use Walkers for Cross-Node Analysis
```jac
# Good - walkers handle cross-node logic
walker NetworkAnalyzer {
    def analyze_network_health(self) -> dict:
        # Walker traverses the graph and analyzes relationships
        return analysis_results
}

# Avoid - putting analysis logic in individual nodes
```

### 3. Leverage Edge Properties
```jac
# Good - use edge properties for relationship metadata
user1 -- FriendOf {strength: 0.9, since: "2020-01-01", mutual: true} --> user2

# This enables sophisticated relationship analysis
walker RelationshipAnalyzer {
    can visit_friendship(friendship: FriendOf) -> None:
        if friendship.strength > 0.8:
            # Strong relationships have different behavior
            pass
}
```

## Common OSP Patterns

### 1. Network Effects
```jac
# The value increases as more nodes are added
walker ViralContentDetector {
    viral_threshold: int
    viral_content: list[Content]
    
    can visit_content(content: Content) -> None:
        if content.shares >= self.viral_threshold:
            self.viral_content.append(content)
```

### 2. Emergent Behavior
```jac
# Complex behavior emerges from simple node rules
walker GroupFormationAnalyzer {
    def analyze_groups(self) -> list[list[User]]:
        # Groups form naturally from friendship patterns
        # No central coordination needed
        return discovered_groups
```

### 3. Distributed Processing
```jac
# Processing happens where data lives
walker DataProcessor {
    can visit_large_dataset(dataset: DataNode) -> None:
        # Heavy processing happens at the data location
        # Results are aggregated back
        processed_data = dataset.process_locally()
        self.aggregate_results(processed_data)
```

## Performance Considerations

### 1. Walker Optimization
```jac
# Use efficient traversal patterns
walker OptimizedWalker {
    visited: set[Node]
    
    can visit_node(node: Node) -> None:
        if node in self.visited:
            return  # Avoid revisiting
        self.visited.add(node)
        # Process node...
```

### 2. Batching Operations
```jac
# Batch operations to reduce network overhead
walker BatchProcessor {
    batch_size: int
    current_batch: list[Node]
    
    can visit_node(node: Node) -> None:
        self.current_batch.append(node)
        if len(self.current_batch) >= self.batch_size:
            self.process_batch()
            self.current_batch.clear()
```

## Next Steps

In the next lesson, we'll dive deeper into JAC's Nodes and Edges, exploring advanced relationship modeling and graph structures that enable sophisticated OSP applications.
""",

        "jac_nodes_edges": """
# JAC Nodes and Edges

## Introduction to Graph Structures in JAC

JAC's Object-Spatial Programming is built on graph structures where nodes represent entities and edges represent relationships. Understanding how to create and manage these structures is fundamental to building scalable OSP applications.

## Node Creation and Management

### Basic Node Definition
```jac
# Define a simple node
node Person {
    name: str
    age: int
    email: str
    friends: list[Person]  # Relationships to other Person nodes
}

# Create and connect nodes
alice: Person = Person()
alice.name = "Alice Johnson"
alice.age = 28
alice.email = "alice@example.com"

bob: Person = Person()
bob.name = "Bob Smith"
bob.age = 30
bob.email = "bob@example.com"

# Create friendship relationship
alice.friends.append(bob)
bob.friends.append(alice)
```

### Advanced Node Properties
```jac
node Employee {
    employee_id: str
    name: str
    department: str
    salary: float
    manager: Employee    # Self-referential relationship
    direct_reports: list[Employee]
    projects: list[Project]
    skills: list[str]
    
    def get_team_size(self) -> int:
        return len(self.direct_reports)
    
    def is_manager(self) -> bool:
        return len(self.direct_reports) > 0
    
    def get_reports_count(self) -> int:
        total: int = len(self.direct_reports)
        for report in self.direct_reports:
            total += report.get_reports_count()
        return total
    
    def get_salary_band(self) -> str:
        if self.salary >= 100000:
            return "Senior"
        elif self.salary >= 70000:
            return "Mid-level"
        else:
            return "Junior"
}

node Project {
    project_id: str
    name: str
    description: str
    budget: float
    start_date: str
    end_date: str
    status: str
    team_lead: Employee
    team_members: list[Employee]
    
    def is_active(self) -> bool:
        return self.status.lower() in ["active", "in-progress", "ongoing"]
    
    def get_team_size(self) -> int:
        return len(self.team_members)
    
    def get_budget_utilization(self, spent_amount: float) -> float:
        if self.budget == 0:
            return 0.0
        return (spent_amount / self.budget) * 100
    
    def get_project_duration(self) -> int:
        # Calculate project duration in days
        # This is a simplified calculation
        return 90  # Placeholder
}
```

## Edge Types and Relationships

### Defining Custom Edge Types
```jac
# Define relationship edge types with properties
edge Manages {
    since: str          # When the management relationship started
    performance_rating: float  # 1.0 to 5.0
    feedback_score: float      # Manager feedback rating
}

edge WorksOn {
    role: str           # Employee's role in the project
    allocation: float   # Percentage of time allocated (0.0 to 1.0)
    start_date: str
    end_date: str
}

edge ReportsTo {
    relationship_type: str  # "direct", "dotted-line", "functional"
    effective_date: str
    termination_date: str
}

edge CollaboratesWith {
    collaboration_type: str  # "peer", "cross-functional", "vendor"
    intensity: float         # Level of collaboration (0.0 to 1.0)
    last_interaction: str
}
```

### Creating Typed Relationships
```jac
# Create organizational structure
ceo: Employee = Employee()
ceo.employee_id = "EMP001"
ceo.name = "Sarah Wilson"
ceo.department = "Executive"
ceo.salary = 150000

cto: Employee = Employee()
cto.employee_id = "EMP002"
cto.name = "Mike Johnson"
cto.department = "Engineering"
cto.salary = 120000

# Create management relationship
cto -- Manages {since: "2023-01-15", performance_rating: 4.5, feedback_score: 4.8} --> ceo

# Create development team
dev1: Employee = Employee()
dev1.employee_id = "EMP003"
dev1.name = "Alice Developer"
dev1.department = "Engineering"
dev1.salary = 85000

dev2: Employee = Employee()
dev2.employee_id = "EMP004"
dev2.name = "Bob Coder"
dev2.department = "Engineering"
dev2.salary = 78000

# Team structure
dev1 -- Manages {since: "2023-03-01", performance_rating: 4.2, feedback_score: 4.0} --> cto
dev2 -- Manages {since: "2023-03-01", performance_rating: 3.8, feedback_score: 4.2} --> cto

# Create projects
website_project: Project = Project()
website_project.project_id = "PRJ001"
website_project.name = "Company Website Redesign"
website_project.description = "Modernize company website"
website_project.budget = 50000
website_project.status = "Active"
website_project.team_lead = dev1

# Project assignments
dev1 -- WorksOn {role: "Lead Developer", allocation: 0.8, start_date: "2024-01-01", end_date: "2024-06-30"} --> website_project
dev2 -- WorksOn {role: "Frontend Developer", allocation: 0.6, start_date: "2024-01-15", end_date: "2024-05-31"} --> website_project
```

## Complex Graph Structures

### Hierarchical Organizations
```jac
node Organization {
    org_id: str
    name: str
    type: str  # "company", "department", "team"
    parent_org: Organization
    child_orgs: list[Organization]
    employees: list[Employee]
    
    def get_employee_count(self) -> int:
        count: int = len(self.employees)
        for child in self.child_orgs:
            count += child.get_employee_count()
        return count
    
    def get_total_salary_budget(self) -> float:
        total: float = sum(emp.salary for emp in self.employees)
        for child in self.child_orgs:
            total += child.get_total_salary_budget()
        return total
    
    def find_employee(self, employee_id: str) -> Employee:
        # Search in current organization
        for emp in self.employees:
            if emp.employee_id == employee_id:
                return emp
        
        # Search in child organizations
        for child in self.child_orgs:
            found_emp = child.find_employee(employee_id)
            if found_emp:
                return found_emp
        
        return None  # Not found
    
    def get_organization_chart(self) -> str:
        chart: str = f"{self.name} ({self.get_employee_count()} employees)\\n"
        
        for emp in self.employees:
            chart += f"  - {emp.name} ({emp.get_salary_band()})\\n"
        
        for child in self.child_orgs:
            chart += f"  {child.get_organization_chart()}"
        
        return chart
}

# Build organization hierarchy
main_company: Organization = Organization()
main_company.org_id = "ORG001"
main_company.name = "TechCorp Inc."
main_company.type = "company"

engineering_dept: Organization = Organization()
engineering_dept.org_id = "ORG002"
engineering_dept.name = "Engineering Department"
engineering_dept.type = "department"
engineering_dept.parent_org = main_company

frontend_team: Organization = Organization()
frontend_team.org_id = "ORG003"
frontend_team.name = "Frontend Team"
frontend_team.type = "team"
frontend_team.parent_org = engineering_dept

backend_team: Organization = Organization()
frontend_team.org_id = "ORG004"
frontend_team.name = "Backend Team"
frontend_team.type = "team"
frontend_team.parent_org = engineering_dept

# Set up relationships
main_company.child_orgs = [engineering_dept]
engineering_dept.child_orgs = [frontend_team, backend_team]
engineering_dept.employees = [cto]
frontend_team.employees = [dev1]
backend_team.employees = [dev2]
```

### Network Topologies
```jac
node NetworkDevice {
    device_id: str
    name: str
    device_type: str  # "router", "switch", "server", "firewall"
    ip_address: str
    connections: list[NetworkDevice]
    bandwidth: float  # Mbps
    status: str
    
    def get_connection_count(self) -> int:
        return len(self.connections)
    
    def is_online(self) -> bool:
        return self.status.lower() == "online"
    
    def get_bandwidth_usage(self, current_usage: float) -> float:
        if self.bandwidth == 0:
            return 0.0
        return (current_usage / self.bandwidth) * 100
}

edge NetworkConnection {
    connection_type: str  # "ethernet", "fiber", "wireless"
    speed: float          # Mbps
    latency: float        # milliseconds
    reliability: float    # 0.0 to 1.0
    last_tested: str
}

# Build network topology
core_router: NetworkDevice = NetworkDevice()
core_router.device_id = "RTR001"
core_router.name = "Core Router"
core_router.device_type = "router"
core_router.ip_address = "192.168.1.1"
core_router.bandwidth = 1000
core_router.status = "Online"

distribution_switch: NetworkDevice = NetworkDevice()
distribution_switch.device_id = "SWT001"
distribution_switch.name = "Distribution Switch"
distribution_switch.device_type = "switch"
distribution_switch.ip_address = "192.168.1.10"
distribution_switch.bandwidth = 100
distribution_switch.status = "Online"

web_server: NetworkDevice = NetworkDevice()
web_server.device_id = "SRV001"
web_server.name = "Web Server"
web_server.device_type = "server"
web_server.ip_address = "192.168.1.100"
web_server.bandwidth = 1000
web_server.status = "Online"

# Create network connections
core_router -- NetworkConnection {
    connection_type: "fiber",
    speed: 1000,
    latency: 1.0,
    reliability: 0.999,
    last_tested: "2024-01-01"
} --> distribution_switch

distribution_switch -- NetworkConnection {
    connection_type: "ethernet",
    speed: 100,
    latency: 0.5,
    reliability: 0.995,
    last_tested: "2024-01-01"
} --> web_server
```

## Graph Traversal and Analysis

### Finding Paths
```jac
walker PathFinder {
    start_node: NetworkDevice
    target_node: NetworkDevice
    found_path: list[NetworkDevice]
    max_hops: int
    
    can visit_network_device(device: NetworkDevice) -> None:
        if len(self.found_path) > self.max_hops:
            return
        
        if device == self.target_node:
            return  # Found target
        
        if device in self.found_path:
            return  # Already visited
        
        self.found_path.append(device)
        
        # Continue traversal
        for connected_device in device.connections:
            self.visit_network_device(connected_device)
```

### Network Analysis
```jac
walker NetworkAnalyzer {
    analysis_results: dict
    visited_devices: set[NetworkDevice]
    
    can visit_network_device(device: NetworkDevice) -> None:
        if device in self.visited_devices:
            return
        
        self.visited_devices.add(device)
        
        # Analyze device
        if device.device_type not in self.analysis_results:
            self.analysis_results[device.device_type] = {
                "count": 0,
                "total_bandwidth": 0.0,
                "online_count": 0
            }
        
        device_stats = self.analysis_results[device.device_type]
        device_stats["count"] += 1
        device_stats["total_bandwidth"] += device.bandwidth
        
        if device.is_online():
            device_stats["online_count"] += 1
    
    def get_network_summary(self) -> str:
        summary: str = "=== NETWORK ANALYSIS SUMMARY ===\\n"
        
        for device_type, stats in self.analysis_results.items():
            summary += f"{device_type.title()}:\\n"
            summary += f"  Total Devices: {stats['count']}\\n"
            summary += f"  Online Devices: {stats['online_count']}\\n"
            summary += f"  Average Bandwidth: {stats['total_bandwidth']/stats['count']:.1f} Mbps\\n"
            summary += f"  Availability: {(stats['online_count']/stats['count']*100):.1f}%\\n\\n"
        
        return summary
```

## Graph Algorithms

### Shortest Path Finding
```jac
walker ShortestPathFinder {
    start: NetworkDevice
    target: NetworkDevice
    shortest_path: list[NetworkDevice]
    distances: dict[NetworkDevice, float]
    
    can visit_network_device(device: NetworkDevice) -> None:
        # Dijkstra's algorithm implementation
        pass  # Simplified for brevity
```

### Community Detection
```jac
walker CommunityDetector {
    communities: list[list[NetworkDevice]]
    visited: set[NetworkDevice]
    
    can visit_network_device(device: NetworkDevice) -> None:
        if device in self.visited:
            return
        
        # Find connected component
        community: list[NetworkDevice] = []
        self.explore_community(device, community)
        self.communities.append(community)
    
    def explore_community(self, device: NetworkDevice, community: list[NetworkDevice]) -> None:
        if device in self.visited:
            return
        
        self.visited.add(device)
        community.append(device)
        
        for connected_device in device.connections:
            self.explore_community(connected_device, community)
```

## Real-World Applications

### Supply Chain Management
```jac
node Supplier {
    supplier_id: str
    name: str
    location: str
    rating: float
    supplied_parts: list[Part]
    lead_time: int  # days
}

node Manufacturer {
    manufacturer_id: str
    name: str
    location: str
    capacity: int
    current_orders: list[Order]
}

node Part {
    part_id: str
    name: str
    category: str
    unit_cost: float
    suppliers: list[Supplier]
    used_in: list[Product]
}

node Product {
    product_id: str
    name: str
    price: float
    components: list[Part]
    manufacturing_time: int  # days
}

edge Supplies {
    quantity: int
    unit_price: float
    contract_start: str
    contract_end: str
    quality_rating: float
}

edge Uses {
    quantity_required: int
    alternative_parts: list[Part]
}

edge Manufactures {
    batch_size: int
    priority: str  # "high", "medium", "low"
    scheduled_date: str
}

# Build supply chain network
# Suppliers -> Parts -> Products -> Manufacturers
```

### Social Media Influence Network
```jac
node Influencer {
    influencer_id: str
    username: str
    follower_count: int
    engagement_rate: float
    content_topics: list[str]
    brand_partnerships: list[Brand]
}

node Brand {
    brand_id: str
    name: str
    industry: str
    marketing_budget: float
    target_demographics: list[str]
}

node Content {
    content_id: str
    title: str
    content_type: str  # "post", "video", "story"
    engagement_metrics: dict[str, float]
    topics: list[str]
    creator: Influencer
    brand_mentions: list[Brand]
}

edge Creates {
    publish_date: str
    reach: int
    engagement_score: float
}

edge Mentions {
    mention_type: str  # "tag", "hashtag", "sponsored"
    sentiment_score: float
}

edge PartnersWith {
    partnership_type: str  # "sponsored", "ambassador", "collaboration"
    contract_value: float
    start_date: str
    end_date: str
}
```

## Graph Optimization Techniques

### Memory-Efficient Storage
```jac
# Use adjacency lists for sparse graphs
node OptimizedNode {
    node_id: str
    data: dict
    neighbors: dict[str, float]  # neighbor_id -> edge_weight
    cache: dict  # Cache computed values
}
```

### Lazy Loading
```jac
walker LazyGraphWalker {
    loaded_nodes: set[str]
    
    can visit_node(node_id: str) -> None:
        if node_id not in self.loaded_nodes:
            # Load node data from storage only when needed
            node = self.load_node_from_storage(node_id)
            self.loaded_nodes.add(node_id)
```

### Incremental Updates
```jac
node DynamicNode {
    node_id: str
    last_updated: str
    version: int
    
    def update_data(self, new_data: dict) -> None:
        self.data = new_data
        self.last_updated = get_current_timestamp()
        self.version += 1
```

## Performance Best Practices

### 1. Optimize Traversal
```jac
# Use bidirectional search for path finding
walker BidirectionalPathFinder {
    forward_visited: set[Node]
    backward_visited: set[Node]
    
    can visit_node(node: Node) -> None:
        # Search from both ends
        pass
```

### 2. Batch Operations
```jac
# Process multiple nodes together
walker BatchProcessor {
    batch_size: int
    current_batch: list[Node]
    
    def process_batch(self) -> None:
        # Process batch of nodes together
        pass
```

### 3. Use Indexes
```jac
# Maintain indexes for fast lookups
class GraphIndex {
    node_index: dict[str, Node]
    edge_index: dict[tuple[str, str], Edge]
    
    def find_node(self, node_id: str) -> Node:
        return self.node_index.get(node_id)
```

## Next Steps

In the next lesson, we'll explore Walkers and Graph Traversal, learning how to implement mobile computation that efficiently traverses these node and edge structures to perform complex analysis and processing tasks.
""",

        "jac_walkers": """
# JAC Walkers and Graph Traversal

## Introduction to Walkers

Walkers are the mobile computation units in JAC's Object-Spatial Programming paradigm. They traverse graphs of nodes and edges, performing tasks and analysis where the data resides, enabling truly distributed and scalable applications.

## Basic Walker Creation

### Simple Walker Definition
```jac
# Define a basic walker
walker Counter {
    count: int
    
    can visit_person(person: Person) -> None:
        self.count += 1
        print(f"Visited {person.name}")
    
    can visit_employee(emp: Employee) -> None:
        self.count += 1
        print(f"Visited employee {emp.name}")
    
    def get_final_count(self) -> int:
        return self.count
}

# Create and use walker
counter: Counter = Counter()
counter.spawn()  # Start traversing the graph

print(f"Total nodes visited: {counter.get_final_count()}")
```

### Walker with State Management
```jac
walker StatisticsCollector {
    total_people: int
    total_age: int
    average_age: float
    age_distribution: dict[str, int]  # "young", "middle", "senior"
    
    can visit_person(person: Person) -> None:
        self.total_people += 1
        self.total_age += person.age
        
        # Categorize by age
        if person.age < 30:
            category = "young"
        elif person.age < 60:
            category = "middle"
        else:
            category = "senior"
        
        if category not in self.age_distribution:
            self.age_distribution[category] = 0
        self.age_distribution[category] += 1
    
    def calculate_statistics(self) -> dict:
        if self.total_people == 0:
            return {"error": "No people found"}
        
        self.average_age = self.total_age / self.total_people
        
        return {
            "total_people": self.total_people,
            "average_age": round(self.average_age, 2),
            "age_distribution": self.age_distribution,
            "youngest_person": min(person.age for person in all_people),
            "oldest_person": max(person.age for person in all_people)
        }
}
```

## Walker Abilities and Method Dispatch

### Ability Definition and Overriding
```jac
# Base walker with default behavior
walker DataProcessor {
    processed_count: int
    errors: list[str]
    
    can visit_node(node: Node) -> None:
        # Default processing for any node type
        self.processed_count += 1
        print(f"Processed generic node: {node.node_id}")
    
    can visit_person(person: Person) -> None:
        # Specialized processing for Person nodes
        self.processed_count += 1
        print(f"Processed person: {person.name}, age {person.age}")
    
    can visit_employee(emp: Employee) -> None:
        # More specialized processing for Employee nodes
        self.processed_count += 1
        print(f"Processed employee: {emp.name}, dept {emp.department}")
    
    can visit_organization(org: Organization) -> None:
        # Organization-specific processing
        self.processed_count += 1
        print(f"Processed organization: {org.name}, {org.get_employee_count()} employees")
```

### Conditional Ability Execution
```jac
walker ConditionalProcessor {
    processed_nodes: list[Node]
    
    can visit_person(person: Person) -> None:
        # Only process adults
        if person.age >= 18:
            self.processed_nodes.append(person)
            print(f"Adult processed: {person.name}")
        else:
            print(f"Minor skipped: {person.name}")
    
    can visit_employee(emp: Employee) -> None:
        # Only process senior employees
        if emp.salary >= 100000:
            self.processed_nodes.append(emp)
            print(f"Senior employee processed: {emp.name}")
        else:
            print(f"Junior employee skipped: {emp.name}")
    
    can visit_organization(org: Organization) -> None:
        # Only process large organizations
        if org.get_employee_count() >= 10:
            self.processed_nodes.append(org)
            print(f"Large organization processed: {org.name}")
        else:
            print(f"Small organization skipped: {org.name}")
```

## Graph Traversal Strategies

### Depth-First Search Walker
```jac
walker DepthFirstExplorer {
    visited: set[Node]
    exploration_path: list[Node]
    max_depth: int
    
    can visit_node(node: Node) -> None:
        if node in self.visited or len(self.exploration_path) > self.max_depth:
            return
        
        self.visited.add(node)
        self.exploration_path.append(node)
        
        print(f"DFS: Visiting {node.node_id} at depth {len(self.exploration_path)}")
        
        # Get connected nodes (depends on node type)
        if hasattr(node, 'connections'):
            connected_nodes = node.connections
        elif hasattr(node, 'friends'):
            connected_nodes = node.friends
        elif hasattr(node, 'neighbors'):
            connected_nodes = node.neighbors
        else:
            connected_nodes = []
        
        # Recursively visit connected nodes
        for connected_node in connected_nodes:
            self.visit_node(connected_node)
        
        # Backtrack
        self.exploration_path.pop()
    
    def get_exploration_summary(self) -> dict:
        return {
            "nodes_visited": len(self.visited),
            "max_depth_reached": len(self.exploration_path),
            "exploration_complete": True
        }
}
```

### Breadth-First Search Walker
```jac
walker BreadthFirstExplorer {
    visited: set[Node]
    current_level: list[Node]
    next_level: list[Node]
    level_count: int
    
    can visit_node(node: Node) -> None:
        if node in self.visited:
            return
        
        self.visited.add(node)
        self.next_level.append(node)
        print(f"BFS: Visiting {node.node_id} at level {self.level_count}")
    
    def advance_to_next_level(self) -> bool:
        if not self.current_level:
            return False
        
        self.current_level = self.next_level
        self.next_level = []
        self.level_count += 1
        
        # Visit all nodes at current level
        for node in self.current_level:
            self.visit_node(node)
        
        return len(self.next_level) > 0
    
    def start_exploration(self, start_node: Node) -> None:
        self.current_level = [start_node]
        self.level_count = 0
        
        while self.advance_to_next_level():
            pass  # Continue until no more levels
```

### Priority-Based Traversal
```jac
walker PriorityExplorer {
    visited: set[Node]
    priority_queue: list[tuple[float, Node]]  # (priority, node)
    
    can visit_node(node: Node) -> None:
        # Calculate priority based on node properties
        priority: float = self.calculate_priority(node)
        
        # Add to priority queue
        import heapq
        heapq.heappush(self.priority_queue, (priority, node))
    
    def calculate_priority(self, node: Node) -> float:
        # Example: prioritize by node importance
        if hasattr(node, 'importance_score'):
            return -node.importance_score  # Negative for max-heap behavior
        elif hasattr(node, 'follower_count'):
            return -node.followlower_count
        else:
            return 0.0  # Default priority
    
    def process_high_priority_nodes(self, count: int) -> list[Node]:
        processed: list[Node] = []
        
        import heapq
        while self.priority_queue and len(processed) < count:
            priority, node = heapq.heappop(self.priority_queue)
            if node not in self.visited:
                self.visited.add(node)
                processed.append(node)
        
        return processed
```

## Advanced Walker Patterns

### Aggregation Walker
```jac
walker AggregationWalker {
    aggregations: dict[str, dict]
    
    can visit_person(person: Person) -> None:
        age_group: str = "young" if person.age < 30 else "senior"
        
        if age_group not in self.aggregations:
            self.aggregations[age_group] = {
                "count": 0,
                "total_age": 0,
                "names": []
            }
        
        agg = self.aggregations[age_group]
        agg["count"] += 1
        agg["total_age"] += person.age
        agg["names"].append(person.name)
    
    can visit_employee(emp: Employee) -> None:
        if emp.department not in self.aggregations:
            self.aggregations[emp.department] = {
                "count": 0,
                "total_salary": 0.0,
                "avg_salary": 0.0
            }
        
        agg = self.aggregations[emp.department]
        agg["count"] += 1
        agg["total_salary"] += emp.salary
    
    def finalize_aggregations(self) -> None:
        # Calculate final statistics
        for category, agg in self.aggregations.items():
            if "avg_salary" in agg and agg["count"] > 0:
                agg["avg_salary"] = agg["total_salary"] / agg["count"]
            
            if "total_age" in agg and "count" in agg and agg["count"] > 0:
                avg_age = agg["total_age"] / agg["count"]
                agg["average_age"] = round(avg_age, 2)
    
    def get_summary_report(self) -> str:
        self.finalize_aggregations()
        
        report: str = "=== AGGREGATION SUMMARY ===\\n"
        
        for category, data in self.aggregations.items():
            report += f"\\n{category.title()}:\\n"
            for key, value in data.items():
                report += f"  {key}: {value}\\n"
        
        return report
}
```

### Pattern Matching Walker
```jac
walker PatternMatcher {
    patterns: list[dict]
    matches: list[dict]
    
    can visit_person(person: Person) -> None:
        # Check if person matches any patterns
        for pattern in self.patterns:
            if self.matches_pattern(person, pattern):
                match_result: dict = {
                    "node": person,
                    "pattern": pattern,
                    "matched_attributes": self.get_matched_attributes(person, pattern)
                }
                self.matches.append(match_result)
    
    def matches_pattern(self, person: Person, pattern: dict) -> bool:
        # Simple pattern matching logic
        for attribute, expected_value in pattern.items():
            if hasattr(person, attribute):
                actual_value = getattr(person, attribute)
                if isinstance(expected_value, list):
                    if actual_value not in expected_value:
                        return False
                else:
                    if actual_value != expected_value:
                        return False
            else:
                return False
        return True
    
    def get_matched_attributes(self, person: Person, pattern: dict) -> dict:
        matched: dict = {}
        for attribute, expected_value in pattern.items():
            if hasattr(person, attribute):
                matched[attribute] = getattr(person, attribute)
        return matched
    
    def analyze_matches(self) -> dict:
        if not self.matches:
            return {"message": "No matches found"}
        
        # Analyze pattern matching results
        pattern_success_rate: dict = {}
        for match in self.matches:
            pattern = str(match["pattern"])
            if pattern not in pattern_success_rate:
                pattern_success_rate[pattern] = 0
            pattern_success_rate[pattern] += 1
        
        return {
            "total_matches": len(self.matches),
            "pattern_usage": pattern_success_rate,
            "most_successful_pattern": max(pattern_success_rate.items(), key=lambda x: x[1])
        }
```

### Filtering and Transformation Walker
```jac
walker FilterTransformWalker {
    filters: list[callable]
    transformations: list[callable]
    filtered_results: list[Node]
    transformed_data: list[dict]
    
    can visit_node(node: Node) -> None:
        # Apply filters
        if self.passes_all_filters(node):
            self.filtered_results.append(node)
            
            # Apply transformations
            transformed_data: dict = self.apply_transformations(node)
            self.transformed_data.append(transformed_data)
    
    def passes_all_filters(self, node: Node) -> bool:
        for filter_func in self.filters:
            if not filter_func(node):
                return False
        return True
    
    def apply_transformations(self, node: Node) -> dict:
        result: dict = {"original_node": node}
        
        for transform_func in self.transformations:
            transform_result = transform_func(node)
            result.update(transform_result)
        
        return result
    
    def get_filtered_and_transformed_data(self) -> dict:
        return {
            "filtered_count": len(self.filtered_results),
            "transformed_data": self.transformed_data,
            "filter_summary": {
                "applied_filters": len(self.filters),
                "applied_transformations": len(self.transformations)
            }
        }
```

## Distributed Processing with Walkers

### Parallel Walker Execution
```jac
walker ParallelProcessor {
    thread_results: list[dict]
    
    can visit_node(node: Node) -> None:
        # Simulate parallel processing
        result: dict = self.process_node_parallel(node)
        self.thread_results.append(result)
    
    def process_node_parallel(self, node: Node) -> dict:
        # This would typically spawn threads or use async processing
        import time
        import random
        
        # Simulate processing time
        processing_time: float = random.uniform(0.1, 1.0)
        time.sleep(processing_time)
        
        return {
            "node_id": node.node_id,
            "processing_time": processing_time,
            "thread_id": "worker_thread_1"
        }
    
    def execute_parallel_processing(self, nodes: list[Node]) -> dict:
        # Distribute nodes across parallel workers
        # This is a simplified example
        total_processing_time: float = 0.0
        for result in self.thread_results:
            total_processing_time += result["processing_time"]
        
        return {
            "total_nodes_processed": len(self.thread_results),
            "parallel_efficiency": len(self.thread_results) / total_processing_time,
            "results": self.thread_results
        }
```

### Incremental Processing Walker
```jac
walker IncrementalProcessor {
    processed_nodes: set[str]
    last_processed_timestamp: str
    new_nodes: list[Node]
    updated_nodes: list[Node]
    
    can visit_node(node: Node) -> None:
        node_id: str = node.node_id
        node_timestamp: str = getattr(node, 'last_updated', '')
        
        if node_id not in self.processed_nodes:
            # New node
            self.new_nodes.append(node)
            self.processed_nodes.add(node_id)
        elif node_timestamp > self.last_processed_timestamp:
            # Updated node
            self.updated_nodes.append(node)
        
        # Update timestamp
        if node_timestamp > self.last_processed_timestamp:
            self.last_processed_timestamp = node_timestamp
    
    def process_incremental_changes(self) -> dict:
        return {
            "new_nodes": len(self.new_nodes),
            "updated_nodes": len(self.updated_nodes),
            "total_processed": len(self.processed_nodes),
            "last_timestamp": self.last_processed_timestamp
        }
```

## Real-World Walker Applications

### Social Network Analysis Walker
```jac
walker SocialNetworkAnalyzer {
    network_metrics: dict
    communities: list[list[Person]]
    influencers: list[Person]
    
    can visit_person(person: Person) -> None:
        # Calculate network metrics for each person
        metrics: dict = {
            "degree_centrality": len(person.friends),
            "clustering_coefficient": self.calculate_clustering_coefficient(person),
            "influence_score": self.calculate_influence_score(person)
        }
        
        self.network_metrics[person.name] = metrics
        
        # Track potential influencers
        if metrics["influence_score"] > 5.0:
            self.influencers.append(person)
    
    def calculate_clustering_coefficient(self, person: Person) -> float:
        if len(person.friends) < 2:
            return 0.0
        
        # Count triangles in the network
        triangles: int = 0
        possible_triangles: int = 0
        
        for friend1 in person.friends:
            for friend2 in person.friends:
                if friend1 != friend2:
                    possible_triangles += 1
                    if friend2 in friend1.friends:
                        triangles += 1
        
        return triangles / possible_triangles if possible_triangles > 0 else 0.0
    
    def calculate_influence_score(self, person: Person) -> float:
        # Simplified influence calculation
        friend_count: int = len(person.friends)
        follower_count: int = getattr(person, 'follower_count', 0)
        engagement_rate: float = getattr(person, 'engagement_rate', 0.0)
        
        return (friend_count * 0.3) + (follower_count * 0.5) + (engagement_rate * 20)
    
    def get_network_insights(self) -> dict:
        return {
            "total_people_analyzed": len(self.network_metrics),
            "influencers_found": len(self.influencers),
            "avg_degree_centrality": sum(m["degree_centrality"] for m in self.network_metrics.values()) / len(self.network_metrics),
            "top_influencers": [{"name": inf.name, "score": self.calculate_influence_score(inf)} for inf in self.influencers[:5]]
        }
```

### Supply Chain Optimization Walker
```jac
walker SupplyChainOptimizer {
    bottlenecks: list[dict]
    recommendations: list[dict]
    cost_analysis: dict
    
    can visit_supplier(supplier: Supplier) -> None:
        # Analyze supplier performance
        performance_score: float = self.calculate_supplier_performance(supplier)
        
        if performance_score < 3.0:
            bottleneck: dict = {
                "type": "supplier",
                "entity": supplier.name,
                "issue": "low_performance",
                "score": performance_score
            }
            self.bottlenecks.append(bottleneck)
    
    can visit_manufacturer(manufacturer: Manufacturer) -> None:
        # Analyze manufacturer capacity utilization
        utilization: float = len(manufacturer.current_orders) / manufacturer.capacity
        
        if utilization > 0.9:
            bottleneck: dict = {
                "type": "manufacturer",
                "entity": manufacturer.name,
                "issue": "capacity_constraint",
                "utilization": utilization
            }
            self.bottlenecks.append(bottleneck)
    
    def calculate_supplier_performance(self, supplier: Supplier) -> float:
        # Consider multiple factors
        quality_score: float = getattr(supplier, 'quality_rating', 3.0)
        delivery_score: float = 5.0 - (supplier.lead_time / 30.0)  # Shorter lead time = better score
        
        return (quality_score + delivery_score) / 2.0
    
    def generate_optimization_recommendations(self) -> list[dict]:
        recommendations: list[dict] = []
        
        for bottleneck in self.bottlenecks:
            if bottleneck["type"] == "supplier":
                recommendations.append({
                    "action": "diversify_suppliers",
                    "entity": bottleneck["entity"],
                    "priority": "high",
                    "description": "Consider adding backup suppliers to reduce dependency"
                })
            elif bottleneck["type"] == "manufacturer":
                recommendations.append({
                    "action": "increase_capacity",
                    "entity": bottleneck["entity"],
                    "priority": "medium",
                    "description": "Consider expanding manufacturing capacity or outsourcing"
                })
        
        return recommendations
    
    def get_optimization_report(self) -> dict:
        return {
            "bottlenecks_identified": len(self.bottlenecks),
            "recommendations": self.generate_optimization_recommendations(),
            "total_suppliers": len([b for b in self.bottlenecks if b["type"] == "supplier"]),
            "capacity_constraints": len([b for b in self.bottlenecks if b["type"] == "manufacturer"])
        }
```

## Walker Performance Optimization

### Memory-Efficient Walkers
```jac
walker MemoryEfficientWalker {
    processed_count: int
    max_memory_nodes: int
    
    can visit_node(node: Node) -> None:
        self.processed_count += 1
        
        # Process node immediately to avoid memory buildup
        self.process_node_immediately(node)
        
        # Periodically clean up
        if self.processed_count % 1000 == 0:
            self.cleanup_memory()
    
    def process_node_immediately(self, node: Node) -> None:
        # Process and discard data immediately
        result: dict = {"node_id": node.node_id, "processed": True}
        # Send result to external system or write to file
        self.write_result(result)
    
    def cleanup_memory(self) -> None:
        # Force garbage collection
        import gc
        gc.collect()
    
    def write_result(self, result: dict) -> None:
        # Write to external storage to avoid memory buildup
        pass  # Implementation depends on storage system
```

### Caching Walker Results
```jac
walker CachingWalker {
    cache: dict[str, dict]
    cache_hits: int
    cache_misses: int
    
    can visit_node(node: Node) -> None:
        node_id: str = node.node_id
        
        if node_id in self.cache:
            self.cache_hits += 1
            cached_result = self.cache[node_id]
            self.use_cached_result(cached_result)
        else:
            self.cache_misses += 1
            result = self.process_node(node)
            self.cache[node_id] = result
    
    def process_node(self, node: Node) -> dict:
        # Expensive computation
        import time
        time.sleep(0.1)  # Simulate expensive operation
        return {"node_id": node.node_id, "result": "processed"}
    
    def use_cached_result(self, cached_result: dict) -> None:
        # Use cached result
        pass
    
    def get_cache_statistics(self) -> dict:
        total_requests: int = self.cache_hits + self.cache_misses
        hit_rate: float = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_size": len(self.cache)
        }
```

## Best Practices for Walker Development

### 1. Clear Ability Definitions
```jac
# Good - clear and specific abilities
walker DataValidator {
    can visit_person(person: Person) -> None:
        # Validates person-specific data
        pass
    
    can visit_employee(emp: Employee) -> None:
        # Validates employee-specific data
        pass

# Avoid - vague abilities
walker GenericProcessor {
    can visit_node(node: Node) -> None:
        # Too generic, unclear what processing is done
        pass
```

### 2. Efficient State Management
```jac
# Good - minimal state, efficient operations
walker EfficientCounter {
    count: int  # Only essential state
    
    can visit_node(node: Node) -> None:
        self.count += 1

# Avoid - unnecessary state
walker InefficientProcessor {
    visited_nodes: list[Node]  # Could be set for efficiency
    processing_history: list[dict]  # May not be needed
    debug_logs: list[str]  # Should be external
```

### 3. Error Handling
```jac
# Good - robust error handling
walker RobustWalker {
    errors: list[dict]
    
    can visit_node(node: Node) -> None:
        try:
            self.process_node_safely(node)
        except Exception as e:
            error_info: dict = {
                "node_id": node.node_id,
                "error": str(e),
                "timestamp": get_current_timestamp()
            }
            self.errors.append(error_info)
    
    def process_node_safely(self, node: Node) -> None:
        # Safe processing logic
        pass
```

## Next Steps

In the next lesson, we'll explore JAC's AI Integration with byLLM, learning how to combine Object-Spatial Programming with Large Language Models to create intelligent, adaptive applications.
""",

        "jac_ai_integration": """
# JAC AI Integration with byLLM

## Introduction to AI in JAC

JAC provides native AI integration through byLLM annotations, allowing developers to seamlessly incorporate Large Language Model capabilities into their Object-Spatial Programming applications. This enables dynamic content generation, intelligent responses, and adaptive behavior.

## Basic byLLM Integration

### Setting Up LLM Configuration
```jac
# Configure LLM model for JAC application
config LLMConfig {
    model_name: str = "gpt-4"
    api_key: str = "your-api-key"
    temperature: float = 0.7
    max_tokens: int = 1000
    base_url: str = "https://api.openai.com/v1"
}

# Global LLM configuration
global_llm_config: LLMConfig = LLMConfig()
```

### Basic byLLM Function Annotation
```jac
# Simple AI-powered function
@byllm(
    model="gpt-4",
    temperature=0.7,
    prompt_template="Generate a friendly greeting for a user named {name} in the context of {context}"
)
def generate_greeting(name: str, context: str) -> str:
    \"\"\"Generate personalized greeting using AI\"\"\"
    pass  # Implementation generated by LLM

# Usage
greeting = generate_greeting("Alice", "educational tutoring")
print(greeting)  # AI-generated personalized greeting
```

### Advanced byLLM Configuration
```jac
# More complex AI function with custom prompts
@byllm(
    model="gpt-4",
    temperature=0.5,
    max_tokens=500,
    system_prompt="You are an expert programming tutor. Provide clear, concise explanations with practical examples.",
    prompt_template='''
    Explain the concept of {concept} in programming to a {skill_level} learner.
    Include:
    1. Simple definition
    2. Practical example
    3. Common use cases
    4. Best practices
    ''',
    response_format="markdown"
)
def explain_programming_concept(concept: str, skill_level: str) -> str:
    \"\"\"Generate educational content about programming concepts\"\"\"
    pass

# Generate explanation
explanation = explain_programming_concept("recursion", "beginner")
print(explanation)
```

## Object-Spatial Programming with AI

### AI-Enhanced Nodes
```jac
# Node with AI capabilities
node AIEnhancedUser {
    username: str
    preferences: list[str]
    learning_history: list[dict]
    ai_recommendations: list[str]
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        Based on the user's preferences {preferences} and learning history {history},
        recommend 3 personalized learning activities.
        Consider their skill level and interests.
        ''',
        temperature=0.8
    )
    def generate_personalized_recommendations(self) -> list[str]:
        \"\"\"Generate AI-powered learning recommendations\"\"\"
        pass
    
    @byllm(
        model="gpt-4",
        system_prompt="You are a helpful learning assistant. Analyze the user's progress and provide constructive feedback.",
        prompt_template='''
        Analyze this learning progress: {progress}
        Provide:
        1. Achievement summary
        2. Areas of strength
        3. Areas for improvement
        4. Next steps recommendation
        ''',
        temperature=0.6
    )
    def analyze_learning_progress(self, progress: dict) -> str:
        \"\"\"Provide AI-powered progress analysis\"\"\"
        pass
    
    def get_ai_insights(self) -> dict:
        return {
            "recommendations": self.generate_personalized_recommendations(),
            "progress_analysis": self.analyze_learning_progress(self.learning_history[-1]) if self.learning_history else "No progress data"
        }
}
```

### AI-Powered Walker
```jac
# Walker with AI capabilities
walker AIAnalysisWalker {
    analysis_results: list[dict]
    ai_insights: list[str]
    
    can visit_ai_enhanced_user(user: AIEnhancedUser) -> None:
        # Analyze user data with AI
        insights: dict = user.get_ai_insights()
        self.ai_insights.extend(insights["recommendations"])
        
        # Store analysis
        analysis: dict = {
            "user": user.username,
            "insights": insights,
            "timestamp": get_current_timestamp()
        }
        self.analysis_results.append(analysis)
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        Based on the user analysis data: {user_data}
        Provide strategic recommendations for:
        1. Learning path optimization
        2. Engagement improvement
        3. Skill development focus
        ''',
        temperature=0.7
    )
    def generate_strategic_recommendations(self, user_data: dict) -> str:
        \"\"\"Generate high-level strategic recommendations\"\"\"
        pass
    
    def get_comprehensive_analysis(self) -> dict:
        return {
            "individual_insights": self.ai_insights,
            "strategic_recommendations": self.generate_strategic_recommendations(self.analysis_results),
            "total_users_analyzed": len(self.analysis_results)
        }
}
```

## Dynamic Content Generation

### AI Content Creation System
```jac
node ContentCreator {
    creator_id: str
    content_type: str  # "lesson", "exercise", "quiz", "explanation"
    difficulty_level: str
    topic: str
    
    @byllm(
        model="gpt-4",
        system_prompt="You are an expert educator creating engaging learning content.",
        prompt_template='''
        Create a {difficulty_level} level {content_type} about {topic}.
        Requirements:
        - Age appropriate content
        - Clear learning objectives
        - Practical examples
        - Interactive elements where possible
        - Assessment opportunities
        ''',
        temperature=0.8,
        max_tokens=1500
    )
    def create_learning_content(self) -> dict:
        \"\"\"Generate AI-powered learning content\"\"\"
        pass
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        Create assessment questions for: {content}
        Include:
        1. Multiple choice questions (3-5)
        2. Short answer questions (2-3)
        3. Practical application questions (1-2)
        Provide answer keys.
        ''',
        temperature=0.6
    )
    def create_assessment_questions(self, content: dict) -> dict:
        \"\"\"Generate AI-powered assessment content\"\"\"
        pass
    
    def generate_complete_lesson(self) -> dict:
        content: dict = self.create_learning_content()
        assessment: dict = self.create_assessment_questions(content)
        
        return {
            "lesson": content,
            "assessment": assessment,
            "metadata": {
                "creator_id": self.creator_id,
                "topic": self.topic,
                "difficulty": self.difficulty_level,
                "generated_at": get_current_timestamp()
            }
        }
}
```

### Adaptive Learning System
```jac
node AdaptiveLearningSystem {
    student_id: str
    current_skill_level: str
    learning_style: str  # "visual", "auditory", "kinesthetic", "reading"
    progress_data: list[dict]
    ai_tutor_responses: list[str]
    
    @byllm(
        model="gpt-4",
        system_prompt="You are an adaptive AI tutor that adjusts teaching methods based on student needs.",
        prompt_template='''
        Student Profile:
        - Skill Level: {skill_level}
        - Learning Style: {learning_style}
        - Recent Progress: {progress}
        
        Adapt the next learning activity to match the student's needs.
        Consider their strengths, weaknesses, and preferred learning methods.
        ''',
        temperature=0.7
    )
    def generate_adaptive_activity(self, skill_level: str, learning_style: str, progress: dict) -> dict:
        \"\"\"Generate personalized learning activities\"\"\"
        pass
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        Analyze this student response: {response}
        Provide feedback that:
        1. Corrects misconceptions gently
        2. Reinforces correct understanding
        3. Suggests next steps
        4. Maintains motivation
        Student learning style: {learning_style}
        ''',
        temperature=0.6
    )
    def provide_adaptive_feedback(self, response: str, learning_style: str) -> str:
        \"\"\"Provide personalized feedback\"\"\"
        pass
    
    def process_student_interaction(self, student_response: str) -> dict:
        feedback: str = self.provide_adaptive_feedback(student_response, self.learning_style)
        
        # Store interaction
        interaction: dict = {
            "response": student_response,
            "feedback": feedback,
            "timestamp": get_current_timestamp()
        }
        self.progress_data.append(interaction)
        
        return {
            "feedback": feedback,
            "next_activity": self.generate_adaptive_activity(
                self.current_skill_level, 
                self.learning_style, 
                interaction
            )
        }
}
```

## AI-Powered Graph Analysis

### Intelligent Network Analysis
```jac
walker IntelligentNetworkAnalyzer {
    network_insights: list[str]
    ai_recommendations: list[dict]
    
    can visit_ai_enhanced_user(user: AIEnhancedUser) -> None:
        # Collect network data for AI analysis
        user_data: dict = {
            "username": user.username,
            "preferences": user.preferences,
            "recent_activity": getattr(user, 'recent_activity', []),
            "learning_goals": getattr(user, 'learning_goals', [])
        }
        
        # Store for AI processing
        self.network_insights.append(str(user_data))
    
    @byllm(
        model="gpt-4",
        system_prompt="You are a network analysis expert. Identify patterns and provide actionable insights.",
        prompt_template='''
        Analyze this learning network data: {network_data}
        
        Identify:
        1. Learning patterns and trends
        2. Collaboration opportunities
        3. Knowledge gaps
        4. Optimal peer matching
        5. Community building strategies
        
        Provide specific, actionable recommendations.
        ''',
        temperature=0.7
    )
    def analyze_learning_network(self, network_data: list[str]) -> dict:
        \"\"\"Generate AI-powered network analysis\"\"\"
        pass
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        Based on network analysis: {analysis}
        Create specific action items for:
        1. Individual learners
        2. Learning communities
        3. Platform optimization
        4. Content recommendations
        ''',
        temperature=0.6
    )
    def generate_action_recommendations(self, analysis: dict) -> list[dict]:
        \"\"\"Generate specific action recommendations\"\"\"
        pass
    
    def get_intelligent_analysis(self) -> dict:
        if not self.network_insights:
            return {"message": "No network data available"}
        
        analysis: dict = self.analyze_learning_network(self.network_insights)
        recommendations: list[dict] = self.generate_action_recommendations(analysis)
        
        return {
            "network_analysis": analysis,
            "action_recommendations": recommendations,
            "users_analyzed": len(self.network_insights)
        }
}
```

## Real-Time AI Interactions

### Conversational AI System
```jac
node ConversationalAI {
    conversation_id: str
    user_id: str
    conversation_history: list[dict]
    context_memory: dict
    
    @byllm(
        model="gpt-4",
        system_prompt="You are a helpful learning assistant. Provide accurate, encouraging responses that promote learning.",
        prompt_template='''
        Conversation Context:
        {context}
        
        User Message: {message}
        
        Respond helpfully while maintaining conversation flow.
        If the user asks about learning topics, provide educational value.
        ''',
        temperature=0.8,
        max_tokens=300
    )
    def generate_response(self, message: str, context: str) -> str:
        \"\"\"Generate contextual AI response\"\"\"
        pass
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        Analyze this conversation: {conversation}
        Determine if the user needs:
        1. Educational support
        2. Technical help
        3. Motivation/encouragement
        4. Resource recommendations
        
        Provide analysis and suggested response strategy.
        ''',
        temperature=0.6
    )
    def analyze_conversation_intent(self, conversation: list[dict]) -> dict:
        \"\"\"Analyze conversation for intent and needs\"\"\"
        pass
    
    def process_message(self, user_message: str) -> dict:
        # Prepare context
        context: str = "\\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history[-5:]  # Last 5 messages
        ])
        
        # Generate AI response
        ai_response: str = self.generate_response(user_message, context)
        
        # Update conversation history
        self.conversation_history.extend([
            {"role": "user", "content": user_message, "timestamp": get_current_timestamp()},
            {"role": "assistant", "content": ai_response, "timestamp": get_current_timestamp()}
        ])
        
        # Analyze intent
        intent_analysis: dict = self.analyze_conversation_intent(self.conversation_history)
        
        return {
            "response": ai_response,
            "intent_analysis": intent_analysis,
            "conversation_id": self.conversation_id
        }
}
```

### AI-Powered Recommendation Engine
```jac
node AIRecommendationEngine {
    user_id: str
    preference_model: dict
    interaction_history: list[dict]
    
    @byllm(
        model="gpt-4",
        system_prompt="You are a recommendation system. Suggest relevant learning content based on user preferences and behavior.",
        prompt_template='''
        User Profile:
        - Preferences: {preferences}
        - Interaction History: {history}
        - Current Context: {context}
        
        Recommend 5 learning resources that match the user's needs and interests.
        Consider difficulty progression and learning path optimization.
        ''',
        temperature=0.7,
        max_tokens=800
    )
    def generate_personalized_recommendations(self, preferences: dict, history: list[dict], context: str) -> list[dict]:
        \"\"\"Generate AI-powered personalized recommendations\"\"\"
        pass
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        User feedback: {feedback}
        Content recommendation: {recommendation}
        
        Explain why this recommendation is relevant and how it helps the user achieve their learning goals.
        Provide reasoning to build user trust.
        ''',
        temperature=0.6
    )
    def explain_recommendation(self, feedback: str, recommendation: dict) -> str:
        \"\"\"Provide explanation for recommendations\"\"\"
        pass
    
    def get_recommendations_with_explanations(self, context: str = "") -> dict:
        recommendations: list[dict] = self.generate_personalized_recommendations(
            self.preference_model, 
            self.interaction_history, 
            context
        )
        
        explanations: list[str] = []
        for rec in recommendations:
            explanation: str = self.explain_recommendation("", rec)
            explanations.append(explanation)
        
        return {
            "recommendations": recommendations,
            "explanations": explanations,
            "confidence_score": self.calculate_confidence_score()
        }
    
    def calculate_confidence_score(self) -> float:
        # Calculate confidence based on interaction history and preference matches
        if not self.interaction_history:
            return 0.5  # Default confidence
        
        recent_interactions: list[dict] = self.interaction_history[-10:]  # Last 10 interactions
        positive_feedback: int = sum(1 for interaction in recent_interactions if interaction.get("feedback_score", 0) > 3)
        
        return positive_feedback / len(recent_interactions)
}
```

## AI Model Management and Optimization

### Multi-Model AI System
```jac
# AI model configuration manager
config AIModelManager {
    models: dict[str, dict] = {
        "gpt-4": {
            "provider": "openai",
            "max_tokens": 4000,
            "cost_per_token": 0.00003,
            "best_for": ["complex_reasoning", "creative_content", "detailed_explanations"]
        },
        "gpt-3.5-turbo": {
            "provider": "openai", 
            "max_tokens": 2000,
            "cost_per_token": 0.000002,
            "best_for": ["quick_responses", "simple_tasks", "high_volume"]
        },
        "claude-3": {
            "provider": "anthropic",
            "max_tokens": 3000,
            "cost_per_token": 0.000025,
            "best_for": ["analysis", "summarization", "factual_content"]
        }
    }
    
    def select_optimal_model(self, task_type: str, complexity: str, cost_budget: float) -> str:
        \"\"\"Select the best model for a given task\"\"\"
        suitable_models: list[str] = []
        
        for model_name, model_info in self.models.items():
            if task_type in model_info["best_for"]:
                suitable_models.append(model_name)
        
        # Select based on complexity and cost
        if complexity == "high" and cost_budget > 0.01:
            return "gpt-4" if "gpt-4" in suitable_models else suitable_models[0]
        elif complexity == "medium" and cost_budget > 0.001:
            return "claude-3" if "claude-3" in suitable_models else suitable_models[0]
        else:
            return "gpt-3.5-turbo" if "gpt-3.5-turbo" in suitable_models else suitable_models[0]
}

# Dynamic model selection in functions
@byllm(
    model="dynamic",  # Will be selected based on context
    prompt_template='''
    Task: {task_description}
    Complexity: {complexity_level}
    Budget: {cost_budget}
    
    Provide appropriate response based on available resources.
    ''',
    temperature=0.7
)
def dynamic_ai_function(task_description: str, complexity_level: str, cost_budget: float) -> str:
    \"\"\"AI function with dynamic model selection\"\"\"
    pass
```

### AI Performance Monitoring
```jac
node AIPerformanceMonitor {
    model_usage_stats: dict
    response_quality_scores: list[float]
    cost_tracking: dict
    
    @byllm(
        model="gpt-4",
        prompt_template='''
        Evaluate the quality of this AI response: {response}
        Criteria:
        1. Accuracy (1-10)
        2. Relevance (1-10) 
        3. Clarity (1-10)
        4. Usefulness (1-10)
        
        Provide detailed feedback and suggestions for improvement.
        ''',
        temperature=0.3
    )
    def evaluate_response_quality(self, response: str) -> dict:
        \"\"\"Use AI to evaluate AI response quality\"\"\"
        pass
    
    def track_ai_performance(self, model_name: str, response: str, cost: float) -> dict:
        # Track usage
        if model_name not in self.model_usage_stats:
            self.model_usage_stats[model_name] = {"count": 0, "total_cost": 0.0, "avg_response_time": 0.0}
        
        self.model_usage_stats[model_name]["count"] += 1
        self.model_usage_stats[model_name]["total_cost"] += cost
        
        # Evaluate quality
        quality_evaluation: dict = self.evaluate_response_quality(response)
        
        # Store quality score
        overall_score: float = sum(
            quality_evaluation[criterion] for criterion in ["accuracy", "relevance", "clarity", "usefulness"]
        ) / 4.0
        self.response_quality_scores.append(overall_score)
        
        return {
            "model": model_name,
            "cost": cost,
            "quality_score": overall_score,
            "quality_details": quality_evaluation
        }
    
    def get_performance_summary(self) -> dict:
        if not self.response_quality_scores:
            return {"message": "No performance data available"}
        
        return {
            "average_quality_score": sum(self.response_quality_scores) / len(self.response_quality_scores),
            "total_api_calls": sum(stats["count"] for stats in self.model_usage_stats.values()),
            "total_cost": sum(stats["total_cost"] for stats in self.model_usage_stats.values()),
            "model_breakdown": self.model_usage_stats,
            "quality_trend": "improving" if len(self.response_quality_scores) > 10 and 
                          sum(self.response_quality_scores[-10:]) / 10 > sum(self.response_quality_scores[:10]) / 10 
                          else "stable"
        }
```

## Best Practices for AI Integration

### 1. Prompt Engineering
```jac
# Good - clear, specific prompts
@byllm(
    model="gpt-4",
    system_prompt="You are a professional programming instructor with 10+ years of experience.",
    prompt_template='''
    Explain the concept of {concept} to a {skill_level} programmer.
    
    Structure your response:
    1. Simple definition (2-3 sentences)
    2. Practical example with code
    3. Common use cases
    4. Best practices
    5. Common pitfalls to avoid
    
    Keep explanations concise but comprehensive.
    ''',
    temperature=0.6
)
def explain_concept_effectively(concept: str, skill_level: str) -> str:
    \"\"\"Generate clear, structured explanations\"\"\"
    pass

# Avoid - vague prompts
@byllm(
    model="gpt-4",
    prompt_template="Explain {concept}"  # Too vague
)
def explain_concept_vague(concept: str) -> str:
    pass
```

### 2. Error Handling and Fallbacks
```jac
# Good - robust error handling
@byllm(
    model="gpt-4",
    temperature=0.7,
    fallback_model="gpt-3.5-turbo",
    max_retries=3
)
def robust_ai_function(input_data: str) -> str:
    \"\"\"AI function with fallback mechanisms\"\"\"
    pass

# Implement fallback logic
def ai_function_with_fallback(input_data: str) -> str:
    try:
        return robust_ai_function(input_data)
    except AIAPIError as e:
        # Fallback to simpler model or cached response
        return get_cached_response(input_data) or "I'm having trouble processing your request right now."
```

### 3. Cost Optimization
```jac
# Good - cost-aware AI usage
def cost_optimized_ai_function(task: str, complexity: str, budget: float) -> str:
    # Select appropriate model based on task and budget
    if complexity == "simple" and budget < 0.001:
        model = "gpt-3.5-turbo"
    elif complexity == "complex" and budget >= 0.01:
        model = "gpt-4"
    else:
        model = "claude-3"
    
    @byllm(model=model, temperature=0.6)
    def optimized_function() -> str:
        pass
    
    return optimized_function()
```

### 4. Context Management
```jac
# Good - proper context management
class AIContextManager:
    def __init__(self):
        self.context_window: list[dict] = []
        self.max_context_length: int = 10
    
    def add_interaction(self, role: str, content: str) -> None:
        self.context_window.append({"role": role, "content": content})
        
        # Maintain context window size
        if len(self.context_window) > self.max_context_length:
            self.context_window.pop(0)
    
    def get_context_string(self) -> str:
        return "\\n".join([f"{item['role']}: {item['content']}" for item in self.context_window])

# Use context manager in AI functions
@byllm(
    model="gpt-4",
    prompt_template='''
    Conversation context: {context}
    User query: {query}
    
    Provide helpful response maintaining conversation continuity.
    ''',
    temperature=0.7
)
def contextual_ai_response(query: str, context_manager: AIContextManager) -> str:
    \"\"\"AI function with proper context management\"\"\"
    pass
```

## Next Steps

In the final lesson, we'll explore JAC's Scale-Agnostic Programming capabilities, learning how to build applications that seamlessly scale from single users to millions of users without architectural changes.
""",

        "jac_scale_agnostic_programming": """
# JAC Scale-Agnostic Programming

## Introduction to Scale-Agnostic Programming

Scale-agnostic programming is JAC's revolutionary approach where applications work seamlessly from a single user to millions of users without requiring architectural changes, code modifications, or infrastructure scaling decisions.

## Core Scale-Agnostic Principles

### The Magic of Automatic Scaling

```jac
# This exact same code works for 1 user or 1 million users!
node User {
    user_id: str
    name: str
    preferences: dict
    activity_log: list[dict]
    
    def get_personalized_content(self) -> list[dict]:
        # No scaling logic needed - JAC handles it automatically
        return self.filter_content_by_preferences()
    
    def filter_content_by_preferences(self) -> list[dict]:
        # Scalable filtering - works the same at any scale
        filtered: list[dict] = []
        for activity in self.activity_log:
            if activity.get("type") in self.preferences.get("interested_types", []):
                filtered.append(activity)
        return filtered
}

# Scale-agnostic walker - same behavior at any scale
walker ActivityAnalyzer {
    user_activities: list[dict]
    
    can visit_user(user: User) -> None:
        # Collect user data - automatic scaling
        user_data: dict = {
            "user_id": user.user_id,
            "activity_count": len(user.activity_log),
            "preferences": user.preferences
        }
        self.user_activities.append(user_data)
    
    def analyze_all_users(self) -> dict:
        # Analysis works the same whether you have 10 users or 10 million
        total_activities: int = sum(data["activity_count"] for data in self.user_activities)
        avg_activities: float = total_activities / len(self.user_activities) if self.user_activities else 0.0
        
        return {
            "total_users": len(self.user_activities),
            "total_activities": total_activities,
            "average_activities_per_user": round(avg_activities, 2),
            "scale_level": self.determine_scale_level()
        }
    
    def determine_scale_level(self) -> str:
        user_count: int = len(self.user_activities)
        if user_count < 100:
            return "small"
        elif user_count < 10000:
            return "medium"
        elif user_count < 1000000:
            return "large"
        else:
            return "massive"
}
```

## Automatic Persistence System

### Zero-Configuration Data Persistence
```jac
# Data automatically persists without any database code
node BlogPost {
    post_id: str
    title: str
    content: str
    author: User
    comments: list[Comment]
    likes: list[User]
    created_at: str
    updated_at: str
    
    def add_comment(self, user: User, comment_text: str) -> Comment:
        # Comments automatically persist
        comment: Comment = Comment()
        comment.user = user
        comment.content = comment_text
        comment.created_at = get_current_timestamp()
        
        self.comments.append(comment)
        self.updated_at = get_current_timestamp()
        
        # No database code needed - automatic persistence!
        return comment
    
    def toggle_like(self, user: User) -> bool:
        # Like/unlike functionality with automatic persistence
        if user in self.likes:
            self.likes.remove(user)
            return False  # Unliked
        else:
            self.likes.append(user)
            return True  # Liked
    
    def get_engagement_score(self) -> float:
        # Calculate engagement - works at any scale
        comment_score: float = len(self.comments) * 2.0
        like_score: float = len(self.likes) * 1.0
        
        # Time decay factor
        age_in_days: float = self.get_age_in_days()
        time_factor: float = max(0.1, 1.0 / (1.0 + age_in_days / 30.0))
        
        return (comment_score + like_score) * time_factor
}

# Scale-agnostic comment system
node Comment {
    comment_id: str
    content: str
    user: User
    post: BlogPost
    replies: list[Comment]
    created_at: str
    
    def add_reply(self, user: User, reply_text: str) -> Comment:
        # Nested replies with automatic persistence
        reply: Comment = Comment()
        reply.user = user
        reply.content = reply_text
        reply.created_at = get_current_timestamp()
        
        self.replies.append(reply)
        # All relationships automatically maintained
        
        return reply
```

## Multi-User Isolation System

### Automatic Data Isolation
```jac
# Each user's data is automatically isolated
node PersonalDashboard {
    user: User
    widgets: list[dict]
    layout_config: dict
    private_notes: list[str]
    
    def add_widget(self, widget_type: str, config: dict) -> dict:
        # Widgets are automatically private to the user
        widget: dict = {
            "id": generate_unique_id(),
            "type": widget_type,
            "config": config,
            "position": len(self.widgets),
            "created_at": get_current_timestamp()
        }
        
        self.widgets.append(widget)
        # Automatic persistence and user isolation
        return widget
    
    def share_widget(self, widget_id: str, target_user: User) -> bool:
        # Explicit sharing mechanism
        widget: dict = next((w for w in self.widgets if w["id"] == widget_id), None)
        
        if widget:
            # Create shared copy for target user
            shared_widget: dict = widget.copy()
            shared_widget["shared_by"] = self.user.user_id
            shared_widget["shared_at"] = get_current_timestamp()
            
            # Add to target user's dashboard
            target_user.dashboard.widgets.append(shared_widget)
            return True
        
        return False
    
    def get_dashboard_summary(self) -> dict:
        # Personal dashboard summary - works for any user count
        return {
            "user": self.user.name,
            "widget_count": len(self.widgets),
            "private_notes": len(self.private_notes),
            "last_updated": self.layout_config.get("last_updated", "Never")
        }
}
```

## Distributed Processing Architecture

### Automatic Load Distribution
```jac
# Heavy processing automatically distributed across the graph
walker DataProcessingEngine {
    processed_items: list[dict]
    processing_stats: dict
    
    can visit_user(user: User) -> None:
        # Heavy data processing - automatically distributed
        user_insights: dict = self.process_user_data(user)
        self.processed_items.append(user_insights)
    
    def process_user_data(self, user: User) -> dict:
        # Complex processing that automatically scales
        insights: dict = {
            "user_id": user.user_id,
            "activity_patterns": self.analyze_activity_patterns(user.activity_log),
            "preference_evolution": self.track_preference_changes(user.preferences),
            "engagement_metrics": self.calculate_engagement_metrics(user),
            "recommendations": self.generate_recommendations(user)
        }
        
        return insights
    
    def analyze_activity_patterns(self, activities: list[dict]) -> dict:
        # Pattern analysis - works the same for 100 or 100,000 activities
        if not activities:
            return {"pattern": "no_activity", "frequency": 0}
        
        # Analyze temporal patterns
        hourly_distribution: dict = {}
        daily_distribution: dict = {}
        
        for activity in activities:
            timestamp: str = activity.get("timestamp", "")
            hour: int = self.extract_hour(timestamp)
            day: str = self.extract_day(timestamp)
            
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            daily_distribution[day] = daily_distribution.get(day, 0) + 1
        
        # Determine dominant pattern
        peak_hour: int = max(hourly_distribution.items(), key=lambda x: x[1])[0]
        most_active_day: str = max(daily_distribution.items(), key=lambda x: x[1])[0]
        
        return {
            "peak_hour": peak_hour,
            "most_active_day": most_active_day,
            "activity_frequency": len(activities),
            "consistency_score": self.calculate_consistency_score(hourly_distribution)
        }
    
    def calculate_engagement_metrics(self, user: User) -> dict:
        # Engagement metrics that scale automatically
        total_interactions: int = len(user.activity_log)
        
        if total_interactions == 0:
            return {"engagement_score": 0.0, "interaction_rate": 0.0}
        
        # Calculate engagement over time
        recent_activity: list[dict] = user.activity_log[-30:]  # Last 30 activities
        engagement_trend: float = self.calculate_trend(recent_activity)
        
        # Interaction rate (interactions per day)
        days_active: int = self.calculate_active_days(user.activity_log)
        interaction_rate: float = total_interactions / max(days_active, 1)
        
        return {
            "engagement_score": min(10.0, engagement_trend * 10),
            "interaction_rate": round(interaction_rate, 2),
            "consistency": "high" if engagement_trend > 0.8 else "medium" if engagement_trend > 0.5 else "low"
        }
```

## Global State Management

### Automatic State Synchronization
```jac
# Global state that automatically synchronizes across all instances
global GlobalConfig {
    total_users: int = 0
    active_sessions: dict[str, str] = {}  # session_id -> user_id
    system_metrics: dict = {}
    feature_flags: dict[str, bool] = {}
    
    def increment_user_count(self) -> None:
        # Thread-safe global counter that works across all instances
        self.total_users += 1
        self.update_system_metrics()
    
    def update_system_metrics(self) -> None:
        # Update metrics based on current scale
        self.system_metrics = {
            "scale_level": self.determine_scale_level(),
            "performance_tier": self.get_performance_tier(),
            "auto_scaling_status": self.get_scaling_status()
        }
    
    def determine_scale_level(self) -> str:
        user_count: int = self.total_users
        if user_count < 1000:
            return "small"
        elif user_count < 100000:
            return "medium"
        elif user_count < 10000000:
            return "large"
        else:
            return "massive"
    
    def get_performance_tier(self) -> str:
        scale: str = self.determine_scale_level()
        tier_mapping: dict = {
            "small": "basic",
            "medium": "standard", 
            "large": "premium",
            "massive": "enterprise"
        }
        return tier_mapping.get(scale, "basic")
}

# Scale-aware feature management
node FeatureManager {
    feature_flags: dict[str, bool]
    rollout_strategies: dict[str, dict]
    
    def is_feature_enabled(self, feature_name: str, user_id: str) -> bool:
        # Feature flags that automatically scale
        if feature_name not in self.feature_flags:
            return False
        
        # Gradual rollout based on scale
        strategy: dict = self.rollout_strategies.get(feature_name, {"type": "all_users"})
        
        if strategy["type"] == "all_users":
            return self.feature_flags[feature_name]
        elif strategy["type"] == "percentage":
            user_hash: int = hash(user_id) % 100
            return user_hash < strategy["percentage"]
        elif strategy["type"] == "scale_based":
            scale: str = GlobalConfig.determine_scale_level()
            return scale in strategy["enabled_scales"]
        
        return False
    
    def rollout_feature(self, feature_name: str, strategy: dict) -> None:
        # Gradual feature rollout that adapts to scale
        self.rollout_strategies[feature_name] = strategy
        
        if strategy.get("automatic_scaling", True):
            # Automatically adjust rollout based on system scale
            self.adjust_rollout_by_scale(feature_name)
    
    def adjust_rollout_by_scale(self, feature_name: str) -> None:
        # Adjust rollout strategy based on current system scale
        scale: str = GlobalConfig.determine_scale_level()
        
        if scale == "small":
            # Fast rollout for small scale
            self.rollout_strategies[feature_name]["percentage"] = 100
        elif scale == "medium":
            # Gradual rollout for medium scale
            self.rollout_strategies[feature_name]["percentage"] = 50
        elif scale == "large":
            # Conservative rollout for large scale
            self.rollout_strategies[feature_name]["percentage"] = 10
        else:  # massive
            # Very conservative for massive scale
            self.rollout_strategies[feature_name]["percentage"] = 1
```

## Performance Optimization at Scale

### Automatic Performance Tuning
```jac
# Performance monitoring that adapts to scale
walker PerformanceMonitor {
    performance_metrics: dict
    optimization_suggestions: list[dict]
    
    can visit_user(user: User) -> None:
        # Monitor performance at user level
        user_metrics: dict = self.collect_user_metrics(user)
        self.performance_metrics[user.user_id] = user_metrics
    
    def collect_user_metrics(self, user: User) -> dict:
        # Collect performance data - scales automatically
        activity_count: int = len(user.activity_log)
        response_time: float = self.measure_response_time(user)
        memory_usage: float = self.estimate_memory_usage(user)
        
        return {
            "activity_count": activity_count,
            "response_time": response_time,
            "memory_usage": memory_usage,
            "efficiency_score": self.calculate_efficiency_score(activity_count, response_time, memory_usage)
        }
    
    def optimize_for_scale(self) -> dict:
        # Automatic optimization based on scale
        scale: str = GlobalConfig.determine_scale_level()
        total_users: int = len(self.performance_metrics)
        
        optimizations: list[dict] = []
        
        if scale == "small" and total_users < 100:
            # Optimize for small scale
            optimizations.append({
                "type": "caching",
                "description": "Implement aggressive caching for better response times",
                "priority": "low"
            })
        elif scale == "medium" and total_users < 10000:
            # Optimize for medium scale
            optimizations.append({
                "type": "database_indexing",
                "description": "Add database indexes for frequently queried fields",
                "priority": "medium"
            })
            optimizations.append({
                "type": "load_balancing",
                "description": "Implement load balancing for better distribution",
                "priority": "medium"
            })
        elif scale == "large" and total_users < 1000000:
            # Optimize for large scale
            optimizations.append({
                "type": "distributed_caching",
                "description": "Implement distributed caching system",
                "priority": "high"
            })
            optimizations.append({
                "type": "read_replicas",
                "description": "Add read replicas for improved read performance",
                "priority": "high"
            })
        else:  # massive scale
            # Optimize for massive scale
            optimizations.append({
                "type": "microservices",
                "description": "Consider microservices architecture",
                "priority": "critical"
            })
            optimizations.append({
                "type": "cdn_integration",
                "description": "Implement CDN for global content delivery",
                "priority": "critical"
            })
        
        return {
            "current_scale": scale,
            "total_users": total_users,
            "optimizations": optimizations,
            "performance_tier": GlobalConfig.get_performance_tier()
        }
```

## Real-World Scale-Agnostic Applications

### Social Media Platform
```jac
# Social media platform that scales from 10 to 10 million users seamlessly
node SocialMediaUser {
    username: str
    posts: list[SocialPost]
    followers: list[SocialMediaUser]
    following: list[SocialMediaUser]
    messages: list[Message]
    notifications: list[Notification]
    
    def create_post(self, content: str, media_urls: list[str] = []) -> SocialPost:
        # Create post - works the same for 1 follower or 1 million followers
        post: SocialPost = SocialPost()
        post.author = self
        post.content = content
        post.media_urls = media_urls
        post.created_at = get_current_timestamp()
        
        self.posts.append(post)
        
        # Automatic notification distribution
        self.notify_followers(post)
        
        return post
    
    def notify_followers(self, post: SocialPost) -> None:
        # Notification system that scales automatically
        notification: Notification = Notification()
        notification.type = "new_post"
        notification.content = f"{self.username} posted: {post.content[:50]}..."
        notification.post = post
        notification.created_at = get_current_timestamp()
        
        # Distribute to all followers - automatic scaling
        for follower in self.followers:
            follower.notifications.append(notification)
    
    def send_message(self, recipient: SocialMediaUser, message_text: str) -> Message:
        # Direct messaging with automatic scaling
        message: Message = Message()
        message.sender = self
        message.recipient = recipient
        message.content = message_text
        message.created_at = get_current_timestamp()
        message.is_read = False
        
        self.messages.append(message)
        recipient.messages.append(message)
        
        return message
    
    def get_social_feed(self) -> list[SocialPost]:
        # Social feed aggregation - scale-agnostic
        feed_posts: list[SocialPost] = []
        
        # Get posts from followed users
        for followed_user in self.following:
            feed_posts.extend(followed_user.posts)
        
        # Add own posts
        feed_posts.extend(self.posts)
        
        # Sort by creation time (newest first)
        feed_posts.sort(key=lambda p: p.created_at, reverse=True)
        
        # Return top 50 posts (or adapt based on scale)
        max_posts: int = self.get_optimal_feed_size()
        return feed_posts[:max_posts]
    
    def get_optimal_feed_size(self) -> int:
        # Adapt feed size based on scale
        follower_count: int = len(self.followers)
        
        if follower_count < 100:
            return 50  # Small scale - show more posts
        elif follower_count < 10000:
            return 30  # Medium scale
        elif follower_count < 100000:
            return 20  # Large scale
        else:
            return 10  # Massive scale - show fewer posts
}
```

### E-commerce Platform
```jac
# E-commerce platform with automatic scaling
node EcommerceUser {
    user_id: str
    shopping_cart: list[CartItem]
    order_history: list[Order]
    wishlist: list[Product]
    recommendations: list[Product]
    
    def add_to_cart(self, product: Product, quantity: int = 1) -> CartItem:
        # Shopping cart that scales automatically
        existing_item: CartItem = next(
            (item for item in self.shopping_cart if item.product.product_id == product.product_id), 
            None
        )
        
        if existing_item:
            existing_item.quantity += quantity
            return existing_item
        else:
            cart_item: CartItem = CartItem()
            cart_item.product = product
            cart_item.quantity = quantity
            cart_item.added_at = get_current_timestamp()
            
            self.shopping_cart.append(cart_item)
            return cart_item
    
    def checkout(self) -> Order:
        # Checkout process - works the same at any scale
        if not self.shopping_cart:
            return None  # Empty cart
        
        # Calculate totals
        subtotal: float = sum(item.product.price * item.quantity for item in self.shopping_cart)
        tax: float = subtotal * 0.08  # 8% tax
        shipping: float = self.calculate_shipping_cost()
        total: float = subtotal + tax + shipping
        
        # Create order
        order: Order = Order()
        order.user = self
        order.items = self.shopping_cart.copy()
        order.subtotal = subtotal
        order.tax = tax
        order.shipping = shipping
        order.total = total
        order.created_at = get_current_timestamp()
        order.status = "pending"
        
        # Update user data
        self.order_history.append(order)
        self.shopping_cart.clear()  # Clear cart
        
        # Process payment (simplified)
        payment_result: dict = self.process_payment(total)
        order.status = "confirmed" if payment_result["success"] else "failed"
        
        return order
    
    def calculate_shipping_cost(self) -> float:
        # Shipping calculation that adapts to scale
        total_items: int = sum(item.quantity for item in self.shopping_cart)
        
        if total_items <= 2:
            return 5.99  # Standard shipping
        elif total_items <= 5:
            return 9.99  # Heavy shipping
        else:
            return 14.99  # Bulk shipping
    
    def get_personalized_recommendations(self) -> list[Product]:
        # Recommendation engine that scales automatically
        if not self.order_history:
            # Cold start - show popular items
            return self.get_popular_products()
        
        # Analyze purchase patterns
        purchased_categories: set[str] = set()
        for order in self.order_history:
            for item in order.items:
                purchased_categories.add(item.product.category)
        
        # Find similar products
        recommendations: list[Product] = []
        for category in purchased_categories:
            category_products: list[Product] = self.get_products_by_category(category)
            # Remove already purchased items
            purchased_product_ids: set[str] = set(
                item.product.product_id for order in self.order_history for item in order.items
            )
            
            filtered_products: list[Product] = [
                p for p in category_products if p.product_id not in purchased_product_ids
            ]
            
            recommendations.extend(filtered_products[:3])  # Top 3 per category
        
        # Limit recommendations based on scale
        max_recommendations: int = self.get_recommendation_limit()
        return recommendations[:max_recommendations]
    
    def get_recommendation_limit(self) -> int:
        # Adapt recommendation count based on scale
        total_users: int = GlobalConfig.total_users
        
        if total_users < 1000:
            return 20  # Show more recommendations for small scale
        elif total_users < 100000:
            return 15  # Medium scale
        elif total_users < 1000000:
            return 10  # Large scale
        else:
            return 5  # Massive scale - show fewer recommendations
```

## Scale Monitoring and Management

### Automatic Scaling Insights
```jac
# System that monitors and adapts to scale changes
walker ScaleMonitor {
    scale_metrics: dict
    adaptation_strategies: list[dict]
    
    can visit_social_media_user(user: SocialMediaUser) -> None:
        # Monitor user engagement patterns
        engagement_data: dict = self.collect_engagement_data(user)
        self.update_scale_metrics(engagement_data)
    
    def collect_engagement_data(self, user: SocialMediaUser) -> dict:
        return {
            "follower_count": len(user.followers),
            "post_count": len(user.posts),
            "avg_engagement_rate": self.calculate_engagement_rate(user),
            "response_time": self.measure_response_time(user)
        }
    
    def update_scale_metrics(self, engagement_data: dict) -> None:
        # Update global scale metrics
        if "follower_distribution" not in self.scale_metrics:
            self.scale_metrics["follower_distribution"] = {"small": 0, "medium": 0, "large": 0, "mega": 0}
        
        followers: int = engagement_data["follower_count"]
        if followers < 1000:
            self.scale_metrics["follower_distribution"]["small"] += 1
        elif followers < 10000:
            self.scale_metrics["follower_distribution"]["medium"] += 1
        elif followers < 100000:
            self.scale_metrics["follower_distribution"]["large"] += 1
        else:
            self.scale_metrics["follower_distribution"]["mega"] += 1
    
    def generate_scale_adaptation_plan(self) -> dict:
        # Generate automatic adaptation strategies
        total_users: int = sum(self.scale_metrics["follower_distribution"].values())
        scale_distribution: dict = self.scale_metrics["follower_distribution"]
        
        strategies: list[dict] = []
        
        # Analyze distribution and suggest optimizations
        large_user_percentage: float = scale_distribution["large"] / total_users
        mega_user_percentage: float = scale_distribution["mega"] / total_users
        
        if large_user_percentage > 0.1:  # More than 10% are large users
            strategies.append({
                "type": "performance_optimization",
                "description": "Optimize for high-follower-count users",
                "priority": "high",
                "actions": [
                    "Implement efficient feed algorithms",
                    "Add content delivery optimization",
                    "Implement follower count-based caching"
                ]
            })
        
        if mega_user_percentage > 0.01:  # More than 1% are mega users
            strategies.append({
                "type": "mega_user_support",
                "description": "Special handling for mega users",
                "priority": "critical",
                "actions": [
                    "Implement dedicated mega user infrastructure",
                    "Add real-time analytics",
                    "Implement priority processing"
                ]
            })
        
        return {
            "current_scale_level": GlobalConfig.determine_scale_level(),
            "total_users_monitored": total_users,
            "scale_distribution": scale_distribution,
            "adaptation_strategies": strategies,
            "recommended_actions": self.prioritize_actions(strategies)
        }
    
    def prioritize_actions(self, strategies: list[dict]) -> list[str]:
        # Prioritize actions based on impact and urgency
        high_priority: list[str] = []
        medium_priority: list[str] = []
        
        for strategy in strategies:
            if strategy["priority"] == "critical" or strategy["priority"] == "high":
                high_priority.extend(strategy["actions"])
            else:
                medium_priority.extend(strategy["actions"])
        
        return high_priority + medium_priority
```

## Best Practices for Scale-Agnostic Development

### 1. Embrace Automatic Scaling
```jac
# Good - write code that works at any scale
def process_user_data(user: User) -> dict:
    # No scaling logic needed - JAC handles it automatically
    return {
        "user_id": user.user_id,
        "activities": len(user.activity_log),
        "preferences": user.preferences
    }

# Avoid - hardcoded scaling logic
def process_user_data_with_scaling(user: User, scale_level: str) -> dict:
    if scale_level == "small":
        # Different logic for different scales
        pass
    elif scale_level == "large":
        # More complex logic for large scale
        pass
```

### 2. Design for Automatic Persistence
```jac
# Good - let JAC handle persistence automatically
node BlogPost {
    title: str
    content: str
    author: User
    comments: list[Comment]
    
    def add_comment(self, user: User, text: str) -> Comment:
        comment: Comment = Comment()
        comment.user = user
        comment.content = text
        self.comments.append(comment)
        # Automatic persistence - no database code needed
        return comment

# Avoid - manual persistence logic
def save_blog_post(title: str, content: str, author_id: str) -> str:
    # Manual database operations - not scale-agnostic
    post_id = generate_id()
    db.execute("INSERT INTO posts VALUES (?, ?, ?, ?)", post_id, title, content, author_id)
    return post_id
```

### 3. Trust the Automatic Systems
```jac
# Good - trust JAC's automatic scaling
walker UserAnalyzer {
    def analyze_all_users(self) -> dict:
        self.spawn()  # Let JAC handle the scaling
        return self.get_results()

# Avoid - manual scaling attempts
def analyze_users_manual_scaling(user_list: list[User]) -> dict:
    # Manual scaling logic - unnecessary with JAC
    if len(user_list) > 1000:
        # Use threading or multiprocessing
        pass
    else:
        # Sequential processing
        pass
```

## Conclusion

JAC's scale-agnostic programming paradigm represents a fundamental shift in how we build applications. By automatically handling persistence, distribution, isolation, and performance optimization, JAC enables developers to focus on business logic rather than infrastructure concerns.

The key insight is that **the same code works at any scale** - from a prototype with 10 users to a production system serving millions. This eliminates the traditional trade-offs between development speed, scalability, and code complexity.

With JAC, you write the application once, and it automatically scales to meet whatever demands your users place upon it.
"""
    }
    
    # Update concepts with lesson content
    updated_count = 0
    for concept in concepts:
        concept_name = concept.name
        if concept_name in lesson_contents:
            # Set lesson content to the dedicated lesson_content column
            lesson_content = lesson_contents[concept_name]
            
            concept.lesson_content = lesson_content
            concept.updated_at = datetime.utcnow()
            
            updated_count += 1
            print(f"✅ Set lesson content for: {concept.display_name}")
        else:
            print(f"⚠️  No lesson content found for: {concept.display_name}")
    
    # Commit all changes
    db.commit()
    print(f"\n🎉 Successfully populated lesson content for {updated_count} concepts!")
    
    # Show summary
    print(f"📊 Summary:")
    print(f"   • Total JAC Concepts: {len(concepts)}")
    print(f"   • Concepts with Lesson Content: {updated_count}")
    print(f"   • Concepts missing content: {len(concepts) - updated_count}")

def main():
    """Main function to populate lesson content"""
    print("📚 Starting JAC Lesson Content Population...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        populate_lesson_content(db)
        
        print("\n🎉 JAC Lesson Content population completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during lesson content population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
