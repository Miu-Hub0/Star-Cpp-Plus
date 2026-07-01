# CP+* (C-Plus-Plus-Star)

> **Ngôn ngữ lập trình độc lập, khó hơn C++, mạnh ngang Rust.**

CP+* là ngôn ngữ lập trình được thiết kế để vượt qua C++ về độ khó và tính năng, kết hợp:
- Hệ thống ownership/borrowing như Rust
- Pattern matching mạnh mẽ
- Generics + Template metaprogramming
- Concurrency với goroutines và channels
- Full OOP: đa kế thừa, trait, operator overload
- Module system hoàn chỉnh
- Macro system (token & AST level)

---

## So sánh với C++

| Tính năng | C++ | CP+* |
|-----------|-----|------|
| Ownership & Borrowing | ❌ (manual) | ✅ `own<T>`, `share<T>`, `borrow<T>` |
| Pattern Matching | ❌ (switch only) | ✅ `?~` full destructuring |
| Generics / Template | ✅ templates | ✅ `[T: Constraint]` cleaner syntax |
| Macro System | ✅ preprocessor | ✅ `@macro_tok`, `@macro_ast`, `@reflect` |
| Error Handling | ❌ exceptions | ✅ `Result<T,E>`, `??`, `!!` panic |
| Module System | ⚠️ headers | ✅ `+* module`, `+* import`, `+* export` |
| Concurrency | ⚠️ threads | ✅ `go` coroutines, `Channel<T>` |
| OOP | ✅ | ✅ + traits + `@@override` |
| Operator Overload | ✅ | ✅ via named methods |
| Lifetime Annotations | ❌ | ✅ `'a` lifetime |
| Standard Library | ✅ STL | ✅ `std::io`, `std::collections`, `std::math` |
| Syntax Complexity | High | **Extreme** (by design) |

---

## Cài đặt

```bash
# Yêu cầu: Python 3.8+
# Không cần cài thêm gì!

git clone <repo>
cd cpps
python3 cpps.py examples/hello.cpps
```

---

## Hướng dẫn chạy

```bash
# Chạy file mẫu
python3 cpps.py examples/hello.cpps
python3 cpps.py examples/ultimate_test.cpps

# Chạy tất cả examples
python3 cpps.py examples/advanced_ownership.cpps
python3 cpps.py examples/generics.cpps
python3 cpps.py examples/pattern_matching.cpps
python3 cpps.py examples/macros.cpps
python3 cpps.py examples/error_handling.cpps
python3 cpps.py examples/concurrency.cpps
python3 cpps.py examples/full_oop.cpps
python3 cpps.py examples/benchmark.cpps
python3 cpps.py examples/module_demo/main.cpps

# REPL tương tác
python3 cpps.py --repl

# Debug mode
python3 cpps.py --verbose examples/hello.cpps
```

---

## Cú pháp CP+* — Toàn bộ Reference

### Comments

```cpps
-- Đây là comment một dòng

-- [[ Đây là
   comment nhiều dòng ]] 

+* file: hello.cpps — File header *+
```

### Khai báo biến

```cpps
-- Immutable (constant binding)
name := "CP+*"
version := 2.0
count := 42

-- Mutable
items :: mut List = List::new()
score :: mut int = 0

-- Với kiểu tường minh
ratio :: float = 3.14

-- Ownership annotations
own<int>    x := 100        -- sole owner
share<string> s := "hello"  -- shared reference
borrow<float> pi := 3.14    -- temporary borrow
```

### Hàm

```cpps
-- Cú pháp cơ bản:  ++ name <~ (params) -> ReturnType ** { body }
++ add <~ (a: int, b: int) -> int ** {
    <- a + b
}

-- Void function
++ greet <~ (name: string) -> void ** {
    ~> io::println("Hello, {}!", name)
}

-- Generic function
++ identity[T] <~ (x: T) -> T ** {
    <- x
}

-- Generic với constraint
++ max_of[T: Comparable] <~ (a: T, b: T) -> T ** {
    ?? a > b ** { <- a }
    <- b
}

-- Static method (trong class)
static ++ create <~ () -> MyClass ** {
    <- MyClass::new()
}
```

### Gọi hàm

```cpps
-- ~> để gọi như statement
~> greet("World")
~> io::println("Value: {}", 42)

-- Trực tiếp trong expression
result := add(10, 20)
x := identity(42)
```

### Return

```cpps
<- value          -- return với giá trị
<- none           -- return none
```

### Điều kiện

```cpps
-- If / else if / else
?? condition ** {
    -- then branch
} -- elif condition ** {
    -- elif branch
} -- else ** {
    -- else branch
}

-- Ví dụ
?? score >= 90 ** {
    ~> io::println("Xuất sắc!")
} -- elif score >= 70 ** {
    ~> io::println("Khá")
} -- else ** {
    ~> io::println("Cần cố gắng")
}
```

### Vòng lặp For

```cpps
-- For-each: <> var :: iterable ** { body }
<> item :: items ** {
    ~> io::println("{}", item)
}

-- Vòng số:  <> i :: [0, 1, 2, ...] ** { ... }
<> i :: range(10) ** {
    ~> io::println("{}", i)
}

-- Break và Continue
!>   -- break
!>>  -- continue
```

### Vòng lặp While (trong function body)

```cpps
i := 0
?? i < 10 ** {
    ~> io::println("{}", i)
    i = i + 1
}
```

### Pattern Matching

```cpps
-- ?~ value { pattern => body }
?~ n {
    0    => { <- "zero" }
    1    => { <- "one" }
    _    => { <- "other" }
}

-- Guard condition
?~ x {
    n => {
        ?? n > 10 ** { <- "big" }
        <- "small"
    }
}

-- Tuple matching
?~ type_of(val) {
    "int"    => { ~> io::println("Integer: {}", val) }
    "string" => { ~> io::println("String: {}", val) }
    _        => { ~> io::println("Other type") }
}
```

### OOP: Class, Trait, Override

```cpps
-- Trait definition
trait Printable -> {
    ++ print <~ () -> void ** {}
}

-- Class với trait
class Shape impl Printable -> {
    ++ new <~ (name: string) -> Shape ** {
        @.name = name         -- @.field = self.field
    }

    ++ print <~ () -> void ** {
        ~> io::println("Shape: {}", @.name)
    }

    ++ area <~ () -> float ** {
        <- 0.0
    }
}

-- Kế thừa đơn
class Circle : Shape -> {
    ++ new <~ (r: float) -> Circle ** {
        @.name = "Circle"
        @.radius = r
    }

    @@override
    ++ print <~ () -> void ** {
        ~> io::println("Circle r={}", @.radius)
    }

    @@override
    ++ area <~ () -> float ** {
        <- 3.14159 * @.radius * @.radius
    }
}

-- Đa kế thừa
class Square : Rectangle, Shape -> {
    ++ new <~ (side: float) -> Square ** {
        @.side = side
    }
}

-- Khởi tạo
c := Circle::new(5.0)
c:print()
~> io::println("Area: {}", c:area())

-- Static call
default := Shape::create()
```

### Generics

```cpps
-- Generic class
class Stack[T] -> {
    ++ new <~ () -> Stack ** {
        @.data = List::new()
    }
    ++ push <~ (val: T) -> void ** {
        @.data:push(val)
    }
    ++ pop <~ () -> T ** {
        <- @.data:pop()
    }
}

-- Dùng generic class
s := Stack::new()
s:push(42)
s:push("hello")

-- Generic function với constraint
++ sort[T: Comparable] <~ (lst: List) -> List ** {
    lst:sort()
    <- lst
}
```

### Error Handling

```cpps
-- Result<T, E>
++ safe_divide <~ (a: float, b: float) -> Result ** {
    ?? b == 0.0 ** {
        <- Err("Division by zero")
    }
    <- Ok(a / b)
}

-- Kiểm tra result
r := safe_divide(10.0, 2.0)
?? r:is_ok() ** {
    ~> io::println("Result: {}", r:unwrap())
} -- else ** {
    ~> io::println("Error: {}", r:err())
}

-- unwrap_or
val := r:unwrap_or(0.0)

-- Panic (!!): dừng ngay với message
!! "Critical error occurred"

-- try/catch
try ** {
    result := risky_op()
} catch (err) ** {
    ~> io::println("Caught: {}", err)
}
```

### Module System

```cpps
-- Khai báo module
module my_module

-- Import
+* import -> {
    std::io
}

+* import -> {
    std::io,
    std::collections::{List, Map, Set},
    std::math
}

-- Export symbol
export my_function
export MyClass
```

### Concurrency

```cpps
-- go: chạy concurrent
go some_function()
go expensive_computation(data)

-- Channel<T>
ch := Channel(10)        -- buffered channel, capacity 10

ch:send(42)              -- gửi giá trị
val := ch:recv()         -- nhận (blocking)
r := ch:try_recv()       -- nhận non-blocking, returns Result

-- Patterns
-- Producer-Consumer
go producer(ch, data)
val := ch:recv()

-- Select (non-blocking)
ra := ch_a:try_recv()
rb := ch_b:try_recv()
?? ra:is_ok() ** { ~> process(ra:unwrap()) }
```

### Ownership & Borrowing

```cpps
-- Ownership kinds
own<T>    name := value    -- sole owner; value moved when reassigned
share<T>  name := value    -- shared reference (Arc-like)
borrow<T> name := value    -- temporary borrow; cannot outlive owner

-- Lifetime annotations
-- 'a  — marks how long a borrow is valid (documentation & analysis)

-- @system: unsafe raw pointer region
-- In @system blocks, raw pointer arithmetic is permitted
raw_ptr := 0xFF
unsafe_val := raw_ptr + 0x10
```

### Macros & Metaprogramming

```cpps
-- Token-level macro
@macro_tok log("message")
@macro_tok trace("entering function")

-- AST-level macro
@macro_ast derive(Debug, Clone, PartialEq)
@macro_ast generate_tests(MyClass)

-- Compile-time reflection
info := @reflect my_object
~> io::println("Type: {}", info)

-- Inline macros in expressions
x := @reflect some_function      -- reflects function metadata
```

### Standard Library

```cpps
-- std::io
~> io::println("Hello, {}!", name)       -- print with newline
~> io::print("no newline")               -- print without newline
input := io::input("Enter: ")            -- read line

-- std::collections::List
lst :: mut List = List::new()
lst:push(val)          -- append
lst:pop()              -- remove last
lst:pop_front()        -- remove first
lst:get(i)             -- get at index
lst:set(i, val)        -- set at index
lst:insert(i, val)     -- insert at index
lst:remove(val)        -- remove by value
lst:contains(val)      -- check membership
lst:len()              -- length
lst:is_empty()         -- empty check
lst:sort()             -- sort in-place
lst:reverse()          -- reverse in-place
lst:slice(lo, hi)      -- slice
lst:join(sep)          -- join to string
lst:sum()              -- numeric sum
lst:max()              -- maximum
lst:min()              -- minimum
lst:first()            -- first element
lst:last()             -- last element

-- std::collections::Map
m :: mut Map = Map::new()
m:insert(key, val)
m:get(key)
m:get(key, default)
m:remove(key)
m:contains(key)
m:keys()
m:values()
m:entries()
m:len()

-- std::collections::Set
s :: mut Set = Set::new()
s:add(val)
s:remove(val)
s:contains(val)
s:union(other)
s:intersect(other)
s:diff(other)
s:to_list()

-- std::math  (as global functions)
sqrt(x)        abs(x)       pow(x, y)
sin(x)         cos(x)       tan(x)
log(x)         log2(x)      log10(x)
floor(x)       ceil(x)      round(x)
max(a, b)      min(a, b)    random()
randint(lo, hi)

-- std::string  (as string methods)
s:len()            s:to_upper()       s:to_lower()
s:trim()           s:split(delim)     s:replace(a, b)
s:contains(sub)    s:starts_with(p)   s:ends_with(p)
s:index_of(sub)    s:slice(lo, hi)    s:chars()
s:parse_int()      s:parse_float()    s:repeat(n)
s:format(args...)  s:is_empty()

-- Global utilities
len(x)         type_of(x)     str(x)
int(x)         float(x)       bool(x)
range(n)       range(lo, hi)  assert(cond, msg)
```

### Operators

| Operator | Ý nghĩa |
|----------|---------|
| `:=` | Khai báo biến immutable |
| `:: mut` | Khai báo biến mutable |
| `++` | Khai báo hàm |
| `<~` | Tham số hàm |
| `->` | Kiểu trả về / arrow |
| `**` | Mở block |
| `<-` | Return |
| `??` | If condition |
| `-- else` | Else branch |
| `-- elif` | Else-if branch |
| `<>` | For loop |
| `?~` | Pattern match |
| `~>` | Statement pipe / call |
| `!>` | Break |
| `!>>` | Continue |
| `!!` | Panic |
| `@.field` | Self field access |
| `obj:method()` | Method call |
| `Type::method()` | Static / namespace call |
| `@@override` | Override marker |
| `own<T>` | Ownership type |
| `share<T>` | Shared reference type |
| `borrow<T>` | Borrow type |
| `'a` | Lifetime annotation |
| `@macro_tok` | Token macro |
| `@macro_ast` | AST macro |
| `@reflect` | Reflection |
| `@system` | Unsafe region |

---

## Files mẫu

| File | Nội dung |
|------|----------|
| `examples/hello.cpps` | Hello World, cơ bản |
| `examples/advanced_ownership.cpps` | Ownership & Borrowing |
| `examples/generics.cpps` | Generic classes & functions |
| `examples/pattern_matching.cpps` | Pattern matching `?~` |
| `examples/macros.cpps` | Macro & Metaprogramming |
| `examples/error_handling.cpps` | Result, try/catch, panic |
| `examples/module_demo/` | Module system |
| `examples/concurrency.cpps` | go, Channel<T> |
| `examples/full_oop.cpps` | Full OOP |
| `examples/benchmark.cpps` | Performance tests |
| `examples/ultimate_test.cpps` | Tổng hợp tất cả |

---

## Kiến trúc

```
cpps.py                  — Entry point
src/
  __init__.py            — Package marker
  tokens.py              — TokenType enum, Token, KEYWORDS
  lexer.py               — Lexer (source → tokens)
  parser.py              — Parser (tokens → AST nodes)
  interpreter.py         — Interpreter (AST → execution)
examples/
  hello.cpps             — Hello World
  advanced_ownership.cpps
  generics.cpps
  pattern_matching.cpps
  macros.cpps
  error_handling.cpps
  module_demo/
    math_module.cpps
    main.cpps
  concurrency.cpps
  full_oop.cpps
  benchmark.cpps
  ultimate_test.cpps
```

---

## Tại sao CP+* khó hơn C++?

1. **Ownership system bắt buộc** — phải khai báo `own/share/borrow` rõ ràng
2. **No implicit conversions** — mọi chuyển đổi kiểu phải tường minh
3. **Pattern matching exhaustive** — compiler-style checking
4. **Lifetime annotations** — phải suy nghĩ về vòng đời của dữ liệu
5. **Macro hygiene** — macros không leak variables vào scope ngoài
6. **Module isolation** — không có global namespace pollution
7. **Strict error handling** — mọi lỗi phải được xử lý (Result hoặc !!)
8. **Generic constraints** — type params phải có constraint khi cần
9. **Concurrency safety** — channels enforce communication over shared state
10. **Reflection at compile time** — `@reflect` runs at parse-time

---

*CP+* — Designed to make you think harder.*
