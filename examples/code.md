# Code Examples

## Inline Code

Use backticks for `inline code` like variables, functions, or short snippets.

Mix with text: The `width` parameter accepts pixels, and `style` takes a Style object.

## Code Blocks

Use triple backticks with an optional language for syntax hints:

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

```javascript
const greet = (name) => `Hello, ${name}!`;
console.log(greet("World"));
```

```sql
SELECT name, email
FROM users
WHERE active = true;
```

## Long Lines

Long lines demonstrate overflow handling. The `code_block_overflow` style controls behavior:

| Option | Behavior |
|--------|----------|
| `wrap` | Wrap long lines (default) |
| `show` | Let content overflow visible |
| `hide` | Clip hidden content |
| `ellipsis` | Truncate with `...` |

Here's a long line:

```python
result = calculate_something(first_argument, second_argument, third_argument, fourth_argument, fifth_arg)
```

## Empty & Short Blocks

```
Single line
```

```
Line one
Line two
Line three
```
