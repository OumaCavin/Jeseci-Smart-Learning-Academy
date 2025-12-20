# JAC Language Syntax Research for Version 0.9.3

**Research Date:** December 20, 2025  
**Target Version:** JAC Language 0.9.3  
**Research Scope:** Complete syntax analysis for Object-Spatial Programming (OSP)

## Executive Summary

This document provides a comprehensive analysis of JAC language syntax for version 0.9.3, based on official documentation from jac-lang.org and docs.jaseci.org. The research covers core language constructs including nodes, edges, walkers, abilities, functions, control flow, and Object-Spatial Programming paradigms.

**Key Finding:** The original `app.jac` file contains significant syntax errors that prevent compilation, primarily due to Python-like syntax being used instead of proper JAC syntax.

## Research Sources

The following official sources were analyzed:

1. **JAC Syntax Quick Reference** - https://docs.jaseci.org/learn/syntax_quick_reference/
2. **Functions and Abilities Guide** - https://jac-lang.org/learn/jac_ref/functions_and_abilities/
3. **Object-Spatial Programming Concepts** - https://docs.jaseci.org/jac_book/chapter_8/
4. **Walkers and Abilities** - https://docs.jaseci.org/jac_book/chapter_10/
5. **Getting Started Guide** - https://jac-lang.org/learn/getting_started/

## Core JAC Language Constructs

### 1. Object-Spatial Programming (OSP) Fundamentals

**Paradigm Shift:** OSP inverts traditional programming by bringing computation to data rather than data to computation.

**Core Components:**
- **Nodes**: Stateful entities that hold data and react to visitors
- **Edges**: First-class relationships between nodes
- **Walkers**: Mobile computational units that traverse graphs
- **Graph**: Persistent, spatial environment where all computation occurs

### 2. Node Definitions

**Correct Syntax:**
```jac
node NodeName {
    has property_name: type;
    has optional_property: type = default_value;
}

# Example
node LearningConcept {
    has title: str;
    has description: str;
    has difficulty_level: int;
}
```

**Key Points:**
- Use `node` keyword (not `class` or `obj`)
- Properties declared with `has` keyword
- Type annotations required
- Default values optional

### 3. Edge Definitions and Connections

**Connection Operators:**
```jac
# Forward connection: a -> b
node_a ++> node_b;

# Backward connection: b <- a  
node_b <++ node_a;

# Bidirectional: a <-> b
node_a <++> node_b;

# Typed edges
edge EdgeType {
    has property: type;
}

node_a +>:EdgeType(property=value):+> node_b;
```

**Key Points:**
- Use `++>` for forward edges
- Use `<++` for backward edges
- Use `<++>` for bidirectional edges
- Edges can have their own properties

### 4. Walker Definitions

**Correct Syntax:**
```jac
walker WalkerName {
    has walker_property: type;
    
    # Entry ability - triggers when walker spawns
    can start_ability with `root entry {
        # initialization logic
        visit[-->];  # Move to connected nodes
    }
    
    # Node-specific ability
    can handle_node with NodeType entry {
        # 'here' refers to current node
        # 'self' refers to walker
        print(f"Visiting {here.node_property}");
        visit[-->];  # Continue traversal
    }
    
    # Exit ability - triggers when walker completes
    can finish_ability with exit {
        # cleanup logic
    }
}
```

**Key Points:**
- Use `walker` keyword
- Properties declared with `has` keyword
- Abilities use `can` (not `def`)
- Event clauses required (`with entry`, `with NodeType entry`, etc.)
- `here` refers to current node, `self` refers to walker

### 5. Function vs Ability Distinction

**Functions (`def`):**
- Traditional callable operations
- Explicit invocation required
- Used for general computation

**Abilities (`can`):**
- Event-driven methods
- Automatic execution during graph traversal
- Essential for OSP
- Require event clauses (`with entry`, `with NodeType entry`)

### 6. Control Flow Syntax

**Conditionals (REQUIRED brackets):**
```jac
if condition {
    # code
} elif other_condition {
    # code  
} else {
    # code
}
```

**Loops:**
```jac
# For loops
for i = 10 to i <= 20 by i += 2 {
    print(i);
}

for item in collection {
    print(item);
}

# While loops
while condition {
    # code
}
```

**Match Statements:**
```jac
match value {
    case pattern1: action1;
    case pattern2 if condition: action2;
    case _: default_action;
}
```

### 7. Walker Traversal

**Spawning Walkers:**
```jac
# Spawn walker at specific node
node_instance spawn WalkerName(parameters);

# Spawn at root
root spawn WalkerName(parameters);
```

**Visit Statements:**
```jac
visit[-->];        # Visit all outgoing connections
visit[<--];        # Visit all incoming connections  
visit[-->edge_type]; # Visit specific edge type
visit[-->-->];     # Visit two hops away
```

**Control Flow:**
```jac
disengage;         # Stop walker execution immediately
report value;      # Return value without stopping
```

### 8. Node and Edge Abilities

**Node Abilities:**
```jac
node InteractiveNode {
    has property: type;
    
    # Triggers when specific walker type visits
    can react with WalkerType entry {
        # 'self' refers to node
        # 'visitor' refers to walker
        print(f"Node reacting to {visitor.walker_property}");
    }
}
```

## Common Syntax Errors to Avoid

### 1. Python-like Function Definitions
**❌ Wrong:**
```python
def my_function():
    return value
```

**✅ Correct:**
```jac
def my_function -> type {
    return value;
}
```

### 2. Python-like Class Definitions  
**❌ Wrong:**
```python
class MyClass:
    def method(self):
        pass
```

**✅ Correct:**
```jac
obj MyClass {
    def method {
        # code
    }
}
```

### 3. Python-like Conditional Syntax
**❌ Wrong:**
```python
if condition:
    code
```

**✅ Correct:**
```jac
if condition {
    code
}
```

### 4. Python-like List/Dict Syntax in Wrong Context
**❌ Wrong:**
```python
my_list = [1, 2, 3]
my_dict = {"key": "value"}
```

**✅ Correct:**
```jac
my_list = [1, 2, 3];  # This is valid in JAC
my_dict = {"key": "value"};  # This is valid in JAC
```

### 5. Missing Event Clauses in Abilities
**❌ Wrong:**
```jac
walker MyWalker {
    can my_ability {
        # missing event clause
    }
}
```

**✅ Correct:**
```jac
walker MyWalker {
    can my_ability with entry {
        # proper event clause
    }
}
```

### 6. Incorrect Node Property Declaration
**❌ Wrong:**
```jac
node MyNode {
    property: str;  # Missing 'has' keyword
}
```

**✅ Correct:**
 MyNode {
   ```jac
node has property: str;
}
```

## Version 0.9.3 Specific Features

Based on the research, JAC 0.9.3 includes:

1. **Enhanced OSP Support**: Improved walker and node interaction patterns
2. **Async Abilities**: Support for `async can` abilities in async walkers
3. **Advanced Edge Filtering**: More sophisticated edge selection in visit statements
4. **Improved Type System**: Better type annotations and generic support
5. **Enhanced Error Messages**: Better compilation error reporting

## Compilation and Execution Workflow

**Required Steps:**
1. **Build**: `jac build filename.jac` (compiles to bytecode)
2. **Serve**: `jac serve filename.jir` (starts web server)

**Note**: The `.jac` source must be compiled to `.jir` bytecode before serving.

## Best Practices

1. **Use Descriptive Names**: Clear node, edge, and walker names
2. **Keep Abilities Focused**: Single purpose per ability
3. **Handle Edge Cases**: Check for empty connections before visiting
4. **Control Traversal**: Use conditions to avoid infinite loops
5. **Document Intent**: Use comments to explain OSP patterns

## Conclusion

JAC 0.9.3 is a sophisticated language that requires understanding of Object-Spatial Programming concepts. The syntax is distinct from Python, with specific requirements for:

- Node and edge definitions using OSP constructs
- Walker abilities with mandatory event clauses
- Control flow using curly brackets
- Graph traversal using visit statements

The original `app.jac` file will require significant syntax corrections to compile successfully under JAC 0.9.3.

---

**Research Compiled by:** MiniMax Agent  
**Documentation Version:** 1.0  
**Last Updated:** December 20, 2025