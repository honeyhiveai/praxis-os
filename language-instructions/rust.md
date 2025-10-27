# Rust Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing prAxIs OS in a Rust project, use these instructions to generate language-specific standards by applying universal CS fundamentals to Rust-specific contexts.**

---

## Instructions Overview

You will generate 5 Rust-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Analyzing the target Rust project
3. Applying Rust-specific context (ownership, borrowing, lifetimes, cargo, etc.)
4. Integrating project-specific patterns (detected crates, tools)

## File 1: `rust-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/deadlocks.md`
- `universal/standards/concurrency/locking-strategies.md`

### Rust-Specific Context to Add

#### Fearless Concurrency
Explain:
- Rust's ownership system prevents data races at compile time
- No garbage collector - deterministic performance
- "If it compiles, it's thread-safe" (mostly)

#### Rust Concurrency Models

| Universal Concept | Rust Implementation | When to Use |
|-------------------|---------------------|-------------|
| Multi-threading | `std::thread` | CPU-bound parallel work |
| Message passing | `std::sync::mpsc` (channels) | Thread communication |
| Shared state | `Arc<Mutex<T>>` | Shared mutable state |
| Read-Write Lock | `Arc<RwLock<T>>` | Read-heavy workloads |
| Atomic operations | `std::sync::atomic` | Lock-free primitives |
| Async I/O | `async`/`await` + Tokio/async-std | High-concurrency I/O |
| Thread pool | `rayon` crate | Data parallelism |

#### Code Examples

```rust
use std::thread;
use std::sync::{Arc, Mutex, mpsc};

// Example: Shared state with Arc<Mutex<T>>
// Arc = Atomic Reference Count (thread-safe)
// Mutex = Mutual exclusion
fn shared_counter() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..10 {
        let counter_clone = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter_clone.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("Result: {}", *counter.lock().unwrap());  // Always 10
}

// Example: Message passing with channels
fn channel_example() {
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        let vals = vec![1, 2, 3, 4, 5];
        for val in vals {
            tx.send(val).unwrap();
        }
    });
    
    for received in rx {
        println!("Got: {}", received);
    }
}

// Example: Async/await with Tokio
use tokio;

#[tokio::main]
async fn main() {
    let handles: Vec<_> = (0..10)
        .map(|i| {
            tokio::spawn(async move {
                fetch_data(i).await
            })
        })
        .collect();
    
    for handle in handles {
        handle.await.unwrap();
    }
}

async fn fetch_data(id: u32) -> Result<String, Error> {
    // Async I/O operation
    let response = reqwest::get(&format!("https://api.example.com/{}", id))
        .await?;
    response.text().await
}

// Example: Data parallelism with Rayon
use rayon::prelude::*;

fn parallel_processing() {
    let numbers: Vec<i32> = (0..1000).collect();
    
    // Parallel iterator - automatically splits work
    let sum: i32 = numbers.par_iter()
        .map(|&x| x * x)
        .sum();
    
    println!("Sum of squares: {}", sum);
}

// Example: RwLock for read-heavy workloads
use std::sync::RwLock;

struct Cache {
    data: Arc<RwLock<HashMap<String, String>>>,
}

impl Cache {
    fn get(&self, key: &str) -> Option<String> {
        // Multiple readers can access simultaneously
        let data = self.data.read().unwrap();
        data.get(key).cloned()
    }
    
    fn set(&self, key: String, value: String) {
        // Exclusive write access
        let mut data = self.data.write().unwrap();
        data.insert(key, value);
    }
}
```

#### Ownership and Borrowing (Prevents Data Races)

```rust
// ❌ Compiler PREVENTS this (data race)
let mut data = vec![1, 2, 3];
let handle = thread::spawn(|| {
    data.push(4);  // Error: cannot move `data` into closure
});

// ✅ CORRECT: Use Arc<Mutex<T>> for shared ownership
let data = Arc::new(Mutex::new(vec![1, 2, 3]));
let data_clone = Arc::clone(&data);
let handle = thread::spawn(move || {
    let mut data = data_clone.lock().unwrap();
    data.push(4);
});
```

### Project Context Integration
- **If Tokio detected**: Add Tokio async runtime patterns
- **If async-std detected**: Add async-std patterns
- **If Rayon detected**: Add data parallelism patterns
- **If Actix detected**: Add actor model patterns

---

## File 2: `rust-testing.md`

### Source Materials
Read:
- `universal/standards/testing/test-pyramid.md`
- `universal/standards/testing/test-doubles.md`

### Rust-Specific Context to Add

#### Testing Framework (Built-in)

| Tool | Use Case | Usage |
|------|----------|-------|
| `cargo test` | Built-in testing | `cargo test` |
| `#[test]` | Unit tests | Built into language |
| `#[cfg(test)]` | Test modules | Compile-time conditional |
| `proptest` | Property-based testing | Random input generation |
| `criterion` | Benchmarking | Performance testing |
| `mockall` | Mocking | Generate mocks from traits |

#### Testing Patterns

```rust
// Unit tests (in same file)
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
    
    #[test]
    #[should_panic(expected = "division by zero")]
    fn test_divide_by_zero() {
        divide(10, 0);
    }
    
    #[test]
    fn test_result() -> Result<(), String> {
        if 2 + 2 == 4 {
            Ok(())
        } else {
            Err(String::from("Math is broken"))
        }
    }
}

// Integration tests (in tests/ directory)
// tests/integration_test.rs
use my_crate::*;

#[test]
fn integration_test() {
    let result = public_api_function();
    assert!(result.is_ok());
}

// Property-based testing with proptest
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_sort_is_sorted(mut vec: Vec<i32>) {
        vec.sort();
        for i in 1..vec.len() {
            assert!(vec[i-1] <= vec[i]);
        }
    }
}

// Mocking with mockall
use mockall::*;
use mockall::predicate::*;

#[automock]
trait Database {
    fn get_user(&self, id: u32) -> Result<User, Error>;
}

#[test]
fn test_user_service() {
    let mut mock_db = MockDatabase::new();
    mock_db.expect_get_user()
        .with(eq(1))
        .times(1)
        .returning(|_| Ok(User { id: 1, name: "Alice".to_string() }));
    
    let service = UserService::new(Box::new(mock_db));
    let user = service.get_user(1).unwrap();
    assert_eq!(user.name, "Alice");
}

// Async testing with Tokio
#[tokio::test]
async fn test_async_function() {
    let result = fetch_data(1).await;
    assert!(result.is_ok());
}

// Benchmarking with Criterion
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

criterion_group!(benches, fibonacci_benchmark);
criterion_main!(benches);
```

### Project Context Integration
- **If Tokio**: Add `#[tokio::test]` patterns
- **If Actix**: Add Actix test server patterns
- **If mockall detected**: Add mocking patterns
- **If criterion detected**: Add benchmark patterns

---

## File 3: `rust-dependencies.md`

### Source Materials
Read:
- `universal/standards/architecture/dependency-injection.md`

### Rust-Specific Context

#### Cargo.toml

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"

[dependencies]
# Exact version (recommended for applications)
serde = "1.0.195"

# Caret (default - semver compatible)
tokio = "^1.35"  # Allows 1.35.0 to <2.0.0

# Tilde (patch updates only)
log = "~0.4.20"  # Allows 0.4.20 to <0.5.0

# Features (opt-in functionality)
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }

[dev-dependencies]
mockall = "0.12"
criterion = "0.5"

[build-dependencies]
cc = "1.0"
```

#### Version Pinning (Cargo.lock)

```bash
# Generate/update Cargo.lock
cargo update

# Build with exact versions from Cargo.lock
cargo build

# Check for outdated dependencies
cargo outdated
```

#### Dependency Injection (Trait-based)

```rust
// Define traits for dependencies
trait Database: Send + Sync {
    fn get_user(&self, id: u32) -> Result<User, Error>;
    fn create_user(&self, user: CreateUserDto) -> Result<User, Error>;
}

trait Logger: Send + Sync {
    fn info(&self, message: &str);
    fn error(&self, message: &str, error: &Error);
}

// Service with injected dependencies
struct UserService {
    database: Box<dyn Database>,
    logger: Box<dyn Logger>,
}

impl UserService {
    fn new(database: Box<dyn Database>, logger: Box<dyn Logger>) -> Self {
        Self { database, logger }
    }
    
    fn get_user(&self, id: u32) -> Result<User, Error> {
        self.logger.info(&format!("Fetching user {}", id));
        self.database.get_user(id)
    }
}

// Or with generics (zero-cost abstraction)
struct UserService<D: Database, L: Logger> {
    database: D,
    logger: L,
}

impl<D: Database, L: Logger> UserService<D, L> {
    fn new(database: D, logger: L) -> Self {
        Self { database, logger }
    }
}
```

### Project Context Integration
- **If workspace detected**: Add workspace patterns
- **If features heavily used**: Add feature flag patterns
- **If Actix**: Add Actix app data/DI patterns

---

## File 4: `rust-code-quality.md`

### Rust-Specific Tools

#### Formatting (MANDATORY)
- **rustfmt**: Standard formatter
  - Usage: `cargo fmt`
  - Config: `rustfmt.toml`
  - **Non-negotiable**: All code must be formatted

#### Linting
- **Clippy**: Rust linter (**mandatory**)
  - Usage: `cargo clippy -- -D warnings`
  - Catches common mistakes and suggests idioms
  - Target: 0 warnings

#### Code Standards

```rust
// Error handling (idiomatic Rust)
// ✅ GOOD: Use Result for recoverable errors
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// ✅ GOOD: Use ? operator for error propagation
fn process_file(path: &str) -> Result<String, std::io::Error> {
    let contents = std::fs::read_to_string(path)?;
    Ok(contents.to_uppercase())
}

// ✅ GOOD: Use thiserror for custom errors
use thiserror::Error;

#[derive(Error, Debug)]
enum UserError {
    #[error("User not found: {0}")]
    NotFound(u32),
    
    #[error("Invalid email: {0}")]
    InvalidEmail(String),
    
    #[error("Database error")]
    Database(#[from] sqlx::Error),
}

// ✅ GOOD: Documentation comments
/// Calculates the sum of two numbers.
///
/// # Arguments
///
/// * `a` - The first number
/// * `b` - The second number
///
/// # Returns
///
/// The sum of `a` and `b`
///
/// # Examples
///
/// ```
/// let result = add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// ✅ GOOD: Use `#[must_use]` for important return values
#[must_use]
fn calculate_important_value() -> i32 {
    42
}

// ✅ GOOD: Implement standard traits
#[derive(Debug, Clone, PartialEq, Eq)]
struct User {
    id: u32,
    name: String,
    email: String,
}

// ✅ GOOD: Use iterators instead of loops
// ❌ BAD
let mut sum = 0;
for i in 0..10 {
    sum += i * i;
}

// ✅ GOOD
let sum: i32 = (0..10).map(|x| x * x).sum();
```

#### Clippy Configuration

```toml
# Cargo.toml
[lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
```

### Project Context Integration
- **If `rustfmt.toml`**: Reference existing config
- **If CI detected**: Add CI linting commands
- **If unsafe code**: Add safety documentation requirements

---

## File 5: `rust-documentation.md`

### Rust-Specific Documentation

#### Rustdoc (Built-in)

```rust
//! This is module-level documentation.
//!
//! It appears at the top of the generated docs for this module.

/// This is item-level documentation for a struct.
///
/// # Examples
///
/// ```
/// use my_crate::User;
///
/// let user = User {
///     id: 1,
///     name: String::from("Alice"),
///     email: String::from("alice@example.com"),
/// };
/// ```
pub struct User {
    /// User's unique identifier
    pub id: u32,
    
    /// User's full name
    pub name: String,
    
    /// User's email address
    pub email: String,
}

/// Creates a new user.
///
/// # Arguments
///
/// * `name` - The user's full name
/// * `email` - The user's email address
///
/// # Returns
///
/// Returns a `Result` containing the created user or an error.
///
/// # Errors
///
/// This function will return an error if:
/// - The email is invalid
/// - The email already exists in the database
///
/// # Examples
///
/// ```
/// # use my_crate::create_user;
/// let user = create_user("Alice", "alice@example.com")?;
/// assert_eq!(user.name, "Alice");
/// # Ok::<(), Box<dyn std::error::Error>>(())
/// ```
///
/// # Panics
///
/// This function panics if the database connection is not initialized.
///
/// # Safety
///
/// This function is safe to call from multiple threads.
pub fn create_user(name: &str, email: &str) -> Result<User, UserError> {
    // Implementation
}
```

#### Generating Documentation

```bash
# Generate and open docs
cargo doc --open

# Include private items
cargo doc --document-private-items

# Test documentation examples
cargo test --doc
```

#### README.md Structure

```markdown
# Project Name

[![Crates.io](https://img.shields.io/crates/v/my_crate.svg)](https://crates.io/crates/my_crate)
[![Documentation](https://docs.rs/my_crate/badge.svg)](https://docs.rs/my_crate)

Brief description

## Installation

```toml
[dependencies]
my_crate = "0.1.0"
```

## Usage

```rust
use my_crate::Client;

let client = Client::new("api_key");
```

## Documentation
See [docs.rs](https://docs.rs/my_crate)
```

### Project Context Integration
- **If library crate**: Emphasize public API documentation
- **If published to crates.io**: Add crates.io badge, docs.rs
- **If README examples**: Reference examples/ directory

---

## Installation Steps You Should Follow

1. **Analyze target Rust project**
   - Detect Cargo.toml dependencies
   - Detect async runtime (Tokio, async-std)
   - Detect web framework (Actix, Axum, Rocket)
   - Detect testing crates (mockall, proptest, criterion)
   - Check for workspace structure
   - Detect unsafe code usage

2. **Read universal standards**
   - Read all relevant files from `universal/standards/`

3. **Generate Rust-specific standards**
   - Use templates above
   - Emphasize ownership, borrowing, lifetimes
   - Apply Rust idioms (iterators, Result, traits)
   - Integrate project-specific patterns
   - Include code examples

4. **Create files**
   - `.praxis-os/standards/development/rust-concurrency.md`
   - `.praxis-os/standards/development/rust-testing.md`
   - `.praxis-os/standards/development/rust-dependencies.md`
   - `.praxis-os/standards/development/rust-code-quality.md`
   - `.praxis-os/standards/development/rust-documentation.md`

5. **Cross-reference universal standards**
   - Link back to `../../universal/standards/` files
   - Show relationship between universal and Rust-specific

6. **Include project context sections**
   - "Your Project Context" sections showing detected patterns
   - Examples from actual codebase (if available)

---

**Result:** Rust-specific standards that reference universal CS fundamentals while providing Rust-specific implementations (ownership, borrowing, traits, fearless concurrency) tailored to the target project.
