"""
Educational Content Seeding Script
Populates the database with actual learning materials for concepts
"""

import sys
import os
from datetime import datetime
import uuid

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import DATABASE_URL
from database.models import Base, Concept, ConceptContent, UserContentProgress, User


def create_sample_content():
    """Create sample educational content for various concepts"""
    
    content_data = [
        # Programming Fundamentals
        {
            "concept_name": "variables",
            "contents": [
                {
                    "title": "Introduction to Variables",
                    "content_type": "lesson",
                    "order_index": 1,
                    "content": """# What are Variables?

Variables are containers for storing data values. Think of them as labeled boxes where you can put different types of information.

## Key Concepts:

### 1. Declaration
Variables need to be declared before use:
- **Python**: `name = "John"`
- **JavaScript**: `let name = "John";`
- **Java**: `String name = "John";`

### 2. Naming Rules
- Must start with a letter, underscore, or dollar sign
- Cannot contain spaces or special characters
- Case-sensitive (Name vs name are different)

### 3. Data Types
- **Strings**: Text data ("Hello World")
- **Numbers**: 42, 3.14
- **Booleans**: true/false
- **Arrays**: [1, 2, 3]
- **Objects**: {key: value}

## Real-World Example:
```
# Shopping cart total
cart_total = 0.00
item_price = 19.99
quantity = 3

# Calculate total
cart_total = item_price * quantity
print(f"Total: ${cart_total}")  # Output: Total: $59.97
```

Variables make your code flexible and reusable. Instead of hardcoding values, you can use variables that can be changed as needed.""",
                    "summary": "Learn the basics of variables - how to declare, name, and use them to store data in your programs.",
                    "learning_objectives": [
                        "Understand what variables are and why they're used",
                        "Learn variable naming conventions",
                        "Recognize different data types",
                        "Practice declaring and using variables"
                    ],
                    "estimated_duration": 25,
                    "difficulty_level": "beginner"
                },
                {
                    "title": "Variables Practice Exercise",
                    "content_type": "exercise",
                    "order_index": 2,
                    "content": """# Variables Practice Exercise

Complete the following exercises to practice working with variables:

## Exercise 1: Basic Declaration
Create variables for:
- Your name (string)
- Your age (number)
- Whether you're a student (boolean)

## Exercise 2: Temperature Converter
Write a program that:
1. Stores a temperature in Celsius
2. Converts it to Fahrenheit using the formula: F = (C * 9/5) + 32
3. Prints both temperatures

## Exercise 3: Shopping Calculator
Create a shopping cart calculator that:
1. Stores prices of 3 items
2. Calculates subtotal
3. Adds 8% tax
4. Calculates final total

## Exercise 4: String Manipulation
Given these variables:
```
first_name = "Alice"
last_name = "Smith"
```

Create a variable called `full_name` that combines them with a space between.

## Solution Template:
```python
# Your code here
```

## Expected Output Examples:
- Temperature: 25°C = 77°F
- Shopping total: $32.97
- Full name: Alice Smith""",
                    "practice_questions": [
                        {
                            "question": "What happens if you try to use a variable before declaring it?",
                            "answer": "You'll get a NameError in Python or ReferenceError in JavaScript"
                        },
                        {
                            "question": "Can you change the type of data stored in a variable?",
                            "answer": "In dynamic languages like Python and JavaScript, yes. In static languages like Java, no."
                        }
                    ],
                    "estimated_duration": 30,
                    "difficulty_level": "beginner"
                }
            ]
        },
        
        # Data Structures
        {
            "concept_name": "arrays",
            "contents": [
                {
                    "title": "Understanding Arrays and Lists",
                    "content_type": "lesson",
                    "order_index": 1,
                    "content": """# Arrays and Lists: Ordered Collections

Arrays (or lists) are data structures that store multiple values in a single variable, organized in a specific order.

## What is an Array?

An array is like a row of numbered boxes where each box can hold a value:
```
Index:    0     1     2     3     4
Array:   [10]  [25]  [37]  [42]  [58]
```

## Key Features:

### 1. Indexed Access
- Each element has an index (position number)
- First element is at index 0
- Last element is at index (length - 1)

### 2. Fixed vs Dynamic Arrays
- **Fixed**: Size determined at creation (C, Java)
- **Dynamic**: Can grow/shrink (Python lists, JavaScript arrays)

### 3. Common Operations

#### Creating Arrays:
```python
# Python
numbers = [1, 2, 3, 4, 5]
fruits = ["apple", "banana", "orange"]
empty = []

# JavaScript
let numbers = [1, 2, 3, 4, 5];
let fruits = ["apple", "banana", "orange"];
```

#### Accessing Elements:
```python
first_fruit = fruits[0]    # "apple"
last_fruit = fruits[-1]    # "orange" (Python only)
```

#### Modifying Elements:
```python
fruits[1] = "grape"        # Change second element
```

#### Array Methods:
```python
fruits.append("mango")     # Add to end
fruits.insert(1, "pear")   # Insert at position
fruits.remove("banana")    # Remove by value
fruits.pop()              # Remove last element
```

## Real-World Example: Todo List
```python
todo_list = ["Buy groceries", "Call mom", "Finish project"]
print(f"You have {len(todo_list)} tasks:")

for i, task in enumerate(todo_list, 1):
    print(f"{i}. {task}")

# Add new task
todo_list.append("Review code")
print(f"Updated list: {todo_list}")
```

## Why Use Arrays?
- **Organization**: Keep related data together
- **Iteration**: Easy to loop through all elements
- **Indexing**: Quick access to any element
- **Methods**: Built-in functions for common operations""",
                    "summary": "Learn how arrays and lists work as ordered collections of data, including creation, access, and modification.",
                    "learning_objectives": [
                        "Understand what arrays and lists are",
                        "Learn about indexing and how it works",
                        "Practice basic array operations",
                        "Apply arrays to real-world scenarios"
                    ],
                    "estimated_duration": 35,
                    "difficulty_level": "beginner"
                },
                {
                    "title": "Array Operations Lab",
                    "content_type": "exercise",
                    "order_index": 2,
                    "content": """# Array Operations Lab

Practice working with arrays through these hands-on exercises:

## Exercise 1: Student Grades
Create an array of student grades and calculate:
- Average grade
- Highest grade
- Lowest grade
- Number of students who passed (grade >= 70)

```python
grades = [85, 92, 78, 65, 90, 88, 74, 96, 82]

# Your code here
```

## Exercise 2: Shopping Cart
Build a shopping cart system:
1. Create arrays for item names and prices
2. Calculate total cost
3. Find the most expensive item
4. Add a new item to the cart
5. Remove an item

```python
items = ["Bread", "Milk", "Eggs", "Cheese"]
prices = [2.50, 3.25, 1.80, 4.75]

# Your code here
```

## Exercise 3: Text Analysis
Given a sentence, count:
- Total number of words
- Average word length
- Longest word
- Shortest word

```python
sentence = "The quick brown fox jumps over the lazy dog"

# Your code here
```

## Exercise 4: Array Filtering
Create a function that:
1. Takes an array of numbers
2. Returns only even numbers
3. Returns only numbers greater than 10

```python
numbers = [5, 12, 8, 15, 3, 20, 7, 18, 11]

def filter_even(numbers):
    # Your code here
    pass

def filter_greater_than_10(numbers):
    # Your code here
    pass

print("Even numbers:", filter_even(numbers))
print("Greater than 10:", filter_greater_than_10(numbers))
```

## Challenge: Array Methods Practice
Use array methods (push, pop, shift, unshift, splice) to:
1. Start with an empty array
2. Add 5 numbers to the end
3. Add 2 numbers to the beginning
4. Remove the last number
5. Remove the first number
6. Insert a number at position 2

Track the array after each operation!""",
                    "estimated_duration": 45,
                    "difficulty_level": "beginner"
                }
            ]
        },

        # Web Development
        {
            "concept_name": "html_basics",
            "contents": [
                {
                    "title": "HTML Fundamentals",
                    "content_type": "lesson",
                    "order_index": 1,
                    "content": """# HTML Fundamentals: Building Web Pages

HTML (HyperText Markup Language) is the standard language for creating web pages. It provides the structure and content of web documents.

## What is HTML?

HTML uses elements (tags) to structure content. Think of HTML as the skeleton of a web page - it defines what content goes where.

## Basic HTML Structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My First Web Page</title>
</head>
<body>
    <h1>Welcome to My Website</h1>
    <p>This is a paragraph of text.</p>
</body>
</html>
```

## Essential HTML Elements:

### 1. Headings (h1-h6)
```html
<h1>Main Title (Largest)</h1>
<h2>Subtitle</h2>
<h3>Section Header</h3>
<h4>Sub-section</h4>
<h5>Minor Header</h5>
<h6>Smallest Header</h6>
```

### 2. Text Elements
```html
<p>This is a paragraph of text.</p>
<strong>Bold text</strong>
<em>Italic text</em>
<br> <!-- Line break -->
<hr> <!-- Horizontal rule -->
```

### 3. Lists
```html
<!-- Unordered list -->
<ul>
    <li>First item</li>
    <li>Second item</li>
    <li>Third item</li>
</ul>

<!-- Ordered list -->
<ol>
    <li>First step</li>
    <li>Second step</li>
    <li>Third step</li>
</ol>
```

### 4. Links and Images
```html
<!-- Link to another page -->
<a href="about.html">About Us</a>

<!-- Link to external website -->
<a href="https://google.com" target="_blank">Google</a>

<!-- Image -->
<img src="photo.jpg" alt="Description of image">
```

### 5. Containers
```html
<!-- Division (block-level container) -->
<div>
    <h2>Section Title</h2>
    <p>Section content...</p>
</div>

<!-- Span (inline container) -->
<p>This text has a <span style="color: red;">red word</span> in it.</p>
```

## Attributes:
HTML elements can have attributes that provide additional information:

```html
<img src="image.jpg" width="300" height="200" alt="A beautiful landscape">

<a href="mailto:contact@example.com">Email Us</a>

<div class="header" id="main-header">
```

## Common Attributes:
- `class`: CSS styling groups
- `id`: Unique identifier
- `src`: Source for images/media
- `href`: Link destination
- `alt`: Alternative text for images
- `width/height`: Element dimensions

## Real-World Example: Personal Profile Page
```html
<!DOCTYPE html>
<html>
<head>
    <title>John Doe - Web Developer</title>
</head>
<body>
    <header>
        <h1>John Doe</h1>
        <p>Full Stack Web Developer</p>
    </header>
    
    <nav>
        <ul>
            <li><a href="#about">About</a></li>
            <li><a href="#skills">Skills</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    
    <main>
        <section id="about">
            <h2>About Me</h2>
            <p>I'm a passionate web developer with 5 years of experience creating modern, responsive websites.</p>
        </section>
        
        <section id="skills">
            <h2>Skills</h2>
            <ul>
                <li>HTML5 & CSS3</li>
                <li>JavaScript & React</li>
                <li>Python & Django</li>
                <li>Database Design</li>
            </ul>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 John Doe. All rights reserved.</p>
    </footer>
</body>
</html>
```

## Best Practices:
1. **Semantic HTML**: Use meaningful tags (header, nav, main, section, article)
2. **Accessibility**: Always include alt text for images
3. **Valid HTML**: Use proper nesting and closing tags
4. **Clean Code**: Indent properly for readability
5. **Comments**: Use `<!-- comment -->` for documentation""",
                    "summary": "Learn the fundamentals of HTML including basic structure, essential elements, and how to create well-structured web pages.",
                    "learning_objectives": [
                        "Understand HTML's role in web development",
                        "Learn essential HTML elements and their uses",
                        "Practice creating structured web pages",
                        "Understand HTML attributes and their purposes"
                    ],
                    "estimated_duration": 40,
                    "difficulty_level": "beginner"
                }
            ]
        },

        # Mathematics
        {
            "concept_name": "linear_equations",
            "contents": [
                {
                    "title": "Introduction to Linear Equations",
                    "content_type": "lesson",
                    "order_index": 1,
                    "content": """# Linear Equations: The Foundation of Algebra

Linear equations are mathematical expressions that show a straight line when graphed. They're fundamental to algebra and appear everywhere in mathematics, science, and engineering.

## What is a Linear Equation?

A linear equation is an equation where the highest power of any variable is 1. The general form is:

**ax + b = c**

Where:
- `a`, `b`, and `c` are constants (numbers)
- `x` is the variable we want to solve for
- `a` cannot be zero

## Simple Examples:

### Example 1: x + 5 = 12
```
x + 5 = 12
x = 12 - 5    (Subtract 5 from both sides)
x = 7
```

### Example 2: 3x = 15
```
3x = 15
x = 15 ÷ 3    (Divide both sides by 3)
x = 5
```

### Example 3: 2x + 3 = 11
```
2x + 3 = 11
2x = 11 - 3   (Subtract 3 from both sides)
2x = 8
x = 8 ÷ 2     (Divide both sides by 2)
x = 4
```

## Step-by-Step Solving Process:

1. **Identify the equation**: Write down what you're solving
2. **Simplify both sides**: Combine like terms if possible
3. **Isolate the variable**: Use inverse operations
4. **Check your answer**: Substitute back into the original equation

## Inverse Operations:
- Addition ↔ Subtraction
- Multiplication ↔ Division
- Powers ↔ Roots

## Real-World Applications:

### 1. Budget Planning
```
If you have $100 and spend $25 on lunch, how much money do you have left?
100 - 25 = x
x = 75
```

### 2. Speed and Distance
```
If you drive at 60 mph for 3 hours, how far do you travel?
60 × 3 = x
x = 180 miles
```

### 3. Temperature Conversion
```
Convert 25°C to Fahrenheit: F = (9/5)C + 32
F = (9/5)(25) + 32
F = 45 + 32
F = 77°F
```

## Common Mistakes to Avoid:
1. **Sign errors**: Remember to change signs when moving terms
2. **Order of operations**: Follow PEMDAS (Parentheses, Exponents, Multiplication/Division, Addition/Subtraction)
3. **Arithmetic errors**: Double-check your calculations
4. **Not checking answers**: Always verify by substituting back

## Practice Tips:
- Start with simple equations
- Draw pictures or use graphs when helpful
- Work step-by-step slowly
- Practice regularly with varied problems""",
                    "summary": "Learn the basics of linear equations, including how to solve them step-by-step and apply them to real-world problems.",
                    "learning_objectives": [
                        "Understand what linear equations are",
                        "Learn the step-by-step process for solving equations",
                        "Practice solving various types of linear equations",
                        "Apply linear equations to real-world scenarios"
                    ],
                    "estimated_duration": 35,
                    "difficulty_level": "intermediate"
                }
            ]
        },

        # Science
        {
            "concept_name": "photosynthesis",
            "contents": [
                {
                    "title": "The Process of Photosynthesis",
                    "content_type": "lesson",
                    "order_index": 1,
                    "content": """# Photosynthesis: How Plants Make Food

Photosynthesis is the process by which plants convert light energy into chemical energy (food). It's one of the most important biological processes on Earth.

## What is Photosynthesis?

Photosynthesis is the process where green plants use sunlight, carbon dioxide, and water to produce glucose (sugar) and oxygen.

## The Photosynthesis Equation:

**6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂**

In words:
**Carbon dioxide + Water + Light energy → Glucose + Oxygen**

## Where Does Photosynthesis Happen?

### In Plant Cells:
- **Chloroplasts**: Specialized organelles containing chlorophyll
- **Chlorophyll**: Green pigment that captures light energy
- **Thylakoids**: Membrane structures where light reactions occur
- **Stroma**: Fluid-filled space where dark reactions occur

## Two Main Stages:

### 1. Light-Dependent Reactions (Photo Reactions)
**Location**: Thylakoid membranes

**What happens**:
- Chlorophyll absorbs light energy
- Water molecules are split (photolysis)
- Oxygen is released as a byproduct
- Energy carriers (ATP and NADPH) are produced

**Equation**: 2H₂O → 4H⁺ + 4e⁻ + O₂

### 2. Light-Independent Reactions (Calvin Cycle)
**Location**: Stroma

**What happens**:
- CO₂ is "fixed" into organic molecules
- ATP and NADPH from light reactions provide energy
- Glucose is produced

**Equation**: 3CO₂ + 9ATP + 6NADPH + 6H₂O → C₃H₆O₃ + 9ADP + 8Pi + 6NADP⁺ + 6H⁺

## Factors Affecting Photosynthesis:

### 1. Light Intensity
- More light = faster photosynthesis (up to a point)
- Too much light can damage chlorophyll

### 2. Carbon Dioxide Concentration
- Higher CO₂ = faster photosynthesis (up to a point)
- Plants need CO₂ from the atmosphere

### 3. Temperature
- Optimal temperature range: 15-25°C for most plants
- Too cold: enzymes work slowly
- Too hot: enzymes denature (break down)

### 4. Water Availability
- Essential for photosynthesis
- Water stress can close stomata, reducing CO₂ intake

## Why is Photosynthesis Important?

### 1. Produces Oxygen
- Releases oxygen that all animals need to breathe
- Maintains atmospheric oxygen levels

### 2. Creates Food
- Produces glucose for plant growth
- Forms the base of most food chains

### 3. Removes Carbon Dioxide
- Takes CO₂ from the atmosphere
- Helps regulate Earth's climate

### 4. Stores Energy
- Converts light energy into chemical energy
- Stores energy in organic molecules

## Real-World Applications:

### Agriculture:
- Understanding photosynthesis helps optimize crop yields
- Greenhouse management for optimal growing conditions
- Developing more efficient crop varieties

### Environmental Science:
- Monitoring photosynthesis to assess forest health
- Understanding climate change impacts
- Carbon sequestration strategies

### Technology:
- Artificial photosynthesis for renewable energy
- Solar panel efficiency improvements
- Bioproduction of fuels and chemicals

## Common Misconceptions:
1. **"Plants breathe in carbon dioxide and breathe out oxygen"**
   - *Reality*: Plants do both photosynthesis AND cellular respiration

2. **"Photosynthesis only happens during the day"**
   - *Reality*: Light-dependent reactions need light, but dark reactions can continue

3. **"All parts of a plant can photosynthesize"**
   - *Reality*: Only green parts containing chlorophyll can photosynthesize""",
                    "summary": "Learn how photosynthesis works, including its two main stages, factors that affect it, and its importance to life on Earth.",
                    "learning_objectives": [
                        "Understand the process and importance of photosynthesis",
                        "Learn the two main stages of photosynthesis",
                        "Identify factors that affect photosynthesis rate",
                        "Apply knowledge of photosynthesis to real-world scenarios"
                    ],
                    "estimated_duration": 45,
                    "difficulty_level": "intermediate"
                }
            ]
        }
    ]
    
    return content_data


def seed_content_to_database():
    """Seed educational content to the database"""
    
    # Get database session
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Get all concepts
        concepts = db.query(Concept).all()
        concept_map = {concept.name: concept for concept in concepts}
        
        print(f"Found {len(concepts)} concepts in database")
        
        # Create sample content data
        content_data = create_sample_content()
        
        created_count = 0
        
        for concept_data in content_data:
            concept_name = concept_data["concept_name"]
            
            # Check if concept exists
            if concept_name not in concept_map:
                print(f"⚠️  Concept '{concept_name}' not found in database, skipping...")
                continue
            
            concept = concept_map[concept_name]
            print(f"📝 Creating content for concept: {concept.display_name}")
            
            # Create content for this concept
            for i, content_item in enumerate(concept_data["contents"]):
                # Check if content already exists
                existing_content = db.query(ConceptContent).filter(
                    ConceptContent.concept_id == concept.concept_id,
                    ConceptContent.title == content_item["title"]
                ).first()
                
                if existing_content:
                    print(f"   ✓ Content '{content_item['title']}' already exists, skipping...")
                    continue
                
                # Create new content
                content = ConceptContent(
                    concept_id=concept.concept_id,
                    title=content_item["title"],
                    content_type=content_item["content_type"],
                    order_index=content_item.get("order_index", i + 1),
                    content=content_item["content"],
                    summary=content_item.get("summary"),
                    learning_objectives=content_item.get("learning_objectives", []),
                    multimedia_resources=content_item.get("multimedia_resources", []),
                    external_links=content_item.get("external_links", []),
                    code_examples=content_item.get("code_examples", []),
                    interactive_elements=content_item.get("interactive_elements", []),
                    difficulty_level=content_item["difficulty_level"],
                    estimated_duration=content_item.get("estimated_duration", 30),
                    prerequisites=content_item.get("prerequisites", []),
                    practice_questions=content_item.get("practice_questions", []),
                    examples=content_item.get("examples", []),
                    exercises=content_item.get("exercises", []),
                    author="Cavin Otieno",
                    ai_generated=True
                )
                
                db.add(content)
                created_count += 1
                print(f"   ✅ Created: {content_item['title']} ({content_item['content_type']})")
        
        # Commit all changes
        db.commit()
        print(f"\n🎉 Successfully seeded {created_count} educational content pieces!")
        
        # Show summary
        print("\n📊 Content Summary:")
        for concept_data in content_data:
            concept_name = concept_data["concept_name"]
            if concept_name in concept_map:
                concept = concept_map[concept_name]
                content_count = db.query(ConceptContent).filter(
                    ConceptContent.concept_id == concept.concept_id
                ).count()
                print(f"   • {concept.display_name}: {content_count} content pieces")
        
    except Exception as e:
        print(f"❌ Error seeding content: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Starting educational content seeding...")
    seed_content_to_database()
    print("✅ Content seeding completed!")