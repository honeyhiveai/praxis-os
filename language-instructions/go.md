# Go Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing Agent OS in a Go project, use these instructions to generate language-specific standards by applying universal CS fundamentals to Go-specific contexts.**

---

## Instructions Overview

You will generate 5 Go-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Analyzing the target Go project
3. Applying Go-specific context (goroutines, channels, go mod, etc.)
4. Integrating project-specific patterns (detected frameworks, tools)

## File 1: `go-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/deadlocks.md`
- `universal/standards/concurrency/locking-strategies.md`

### Go-Specific Context to Add

#### Goroutines and Channels
Explain:
- Goroutines are lightweight threads (cheap to create)
- Channels are Go's primary synchronization primitive
- "Do not communicate by sharing memory; share memory by communicating"

#### Go Concurrency Models

| Universal Concept | Go Implementation | When to Use |
|-------------------|-------------------|-------------|
| Multi-threading | `go func()` (goroutines) | Almost always (very cheap) |
| Message passing | `chan T` (channels) | Preferred over locking |
| Mutex | `sync.Mutex` | When channels are awkward |
| Read-Write Lock | `sync.RWMutex` | Read-heavy workloads |
| Wait Group | `sync.WaitGroup` | Waiting for goroutines |
| Once | `sync.Once` | One-time initialization |
| Pool | `sync.Pool` | Object reuse (avoid allocations) |
| Context | `context.Context` | Cancellation, timeouts |

#### Code Examples

```go
// Example: Proper channel usage
func worker(jobs <-chan int, results chan<- int) {
    for job := range jobs {
        results <- processJob(job)
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)
    
    // Start 3 workers
    for w := 1; w <= 3; w++ {
        go worker(jobs, results)
    }
    
    // Send jobs
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)
    
    // Collect results
    for a := 1; a <= 9; a++ {
        <-results
    }
}

// Example: Mutex for shared state
type SafeCounter struct {
    mu    sync.Mutex
    count map[string]int
}

func (c *SafeCounter) Inc(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()  // Always use defer for unlock
    c.count[key]++
}

// Example: select for multiple channels
select {
case msg := <-ch1:
    fmt.Println("Received from ch1:", msg)
case msg := <-ch2:
    fmt.Println("Received from ch2:", msg)
case <-time.After(1 * time.Second):
    fmt.Println("Timeout")
}
```

### Project Context Integration

Analyze the target project and add:
- **If `context` package used**: Add context patterns, cancellation
- **If worker pools detected**: Add worker pool patterns
- **If gRPC detected**: Add gRPC concurrency patterns
- **If database/sql**: Add connection pooling patterns
- **If net/http**: Add concurrent request handling patterns

---

## File 2: `go-testing.md`

### Source Materials
Read:
- `universal/standards/testing/test-pyramid.md`
- `universal/standards/testing/test-doubles.md`

### Go-Specific Context to Add

#### Testing Framework (Built-in)

| Tool | Use Case | Usage |
|------|----------|-------|
| `go test` | Built-in testing | `go test ./...` |
| `testing` package | Test framework | `import "testing"` |
| `testing/quick` | Property-based testing | Random input generation |
| `httptest` | HTTP testing | Test HTTP handlers |
| `testify/assert` | Assertions (optional) | Cleaner test assertions |
| `-race` flag | Race detector | `go test -race ./...` |

#### Testing Patterns

```go
// Table-driven tests (idiomatic Go)
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, -2, -3},
        {"zero", 0, 5, 5},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d",
                    tt.a, tt.b, result, tt.expected)
            }
        })
    }
}

// Mocking with interfaces
type Database interface {
    Get(key string) (string, error)
}

type MockDatabase struct {
    data map[string]string
}

func (m *MockDatabase) Get(key string) (string, error) {
    if val, ok := m.data[key]; ok {
        return val, nil
    }
    return "", errors.New("not found")
}

func TestUserService(t *testing.T) {
    mockDB := &MockDatabase{
        data: map[string]string{"user:1": "Alice"},
    }
    service := NewUserService(mockDB)
    // Test with mock
}

// Testing HTTP handlers
func TestHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/users/1", nil)
    w := httptest.NewRecorder()
    
    handler(w, req)
    
    if w.Code != http.StatusOK {
        t.Errorf("Expected status 200, got %d", w.Code)
    }
}
```

### Project Context Integration
- **If `testify` detected**: Add testify assertion patterns
- **If gRPC**: Add gRPC test client patterns
- **If Gin/Echo detected**: Add framework test patterns
- **If database/sql**: Add database testing with transactions

---

## File 3: `go-dependencies.md`

### Source Materials
Read:
- `universal/standards/architecture/dependency-injection.md`

### Go-Specific Context

#### Go Modules (go.mod)

```go
module github.com/user/project

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/lib/pq v1.10.9
)

require (
    // Indirect dependencies
    github.com/gin-contrib/sse v0.1.0 // indirect
)
```

#### Version Pinning Strategies

| Specifier | Meaning | When to Use | Example |
|-----------|---------|-------------|---------|
| `v1.2.3` | Exact version | **Recommended** | `github.com/pkg v1.2.3` |
| `v1.2` | Latest patch | Patch updates OK | `github.com/pkg v1.2` |
| `v1` | Latest minor | **Avoid** (too broad) | ❌ Don't use |
| `latest` | Latest version | **Never** (non-deterministic) | ❌ Never |

#### Go Commands

```bash
# Initialize module
go mod init github.com/user/project

# Add dependency
go get github.com/gin-gonic/gin@v1.9.1

# Update dependencies
go get -u ./...

# Tidy dependencies (remove unused)
go mod tidy

# Verify dependencies
go mod verify

# Vendor dependencies (optional)
go mod vendor
```

#### Dependency Injection in Go

```go
// Interface-based DI (idiomatic Go)
type UserService struct {
    db     Database
    logger Logger
    cache  Cache
}

func NewUserService(db Database, logger Logger, cache Cache) *UserService {
    return &UserService{
        db:     db,
        logger: logger,
        cache:  cache,
    }
}

// Wire (compile-time DI)
// +build wireinject

func InitializeUserService() *UserService {
    wire.Build(
        NewDatabase,
        NewLogger,
        NewCache,
        NewUserService,
    )
    return nil
}
```

### Project Context Integration
- **If `go.mod`**: Reference existing module configuration
- **If `vendor/`**: Note vendored dependencies
- **If Wire detected**: Add Wire DI patterns
- **If Fx detected**: Add Fx DI patterns

---

## File 4: `go-code-quality.md`

### Go-Specific Tools

#### Formatting (Mandatory)
- **gofmt**: Standard formatter (built-in)
  - Usage: `gofmt -w .`
  - **Non-negotiable**: Code must be gofmt'd

- **goimports**: Adds/removes imports
  - Usage: `goimports -w .`
  - Superset of gofmt

#### Linting
- **golangci-lint**: Meta-linter (recommended)
  - Config: `.golangci.yml`
  - Runs multiple linters

- **go vet**: Built-in static analysis
  - Usage: `go vet ./...`
  - Catches common mistakes

- **staticcheck**: Advanced static analysis
  - Usage: `staticcheck ./...`

#### Code Standards

```go
// Exported functions MUST have doc comments
// Calculate computes the sum of two numbers.
// It returns an error if the operation would overflow.
func Calculate(a, b int) (int, error) {
    // Check overflow
    if a > 0 && b > math.MaxInt-a {
        return 0, errors.New("integer overflow")
    }
    return a + b, nil
}

// Error handling (idiomatic Go)
result, err := operation()
if err != nil {
    return nil, fmt.Errorf("operation failed: %w", err)  // Wrap errors
}

// Defer for cleanup
f, err := os.Open("file.txt")
if err != nil {
    return err
}
defer f.Close()  // Always defer cleanup

// Struct initialization with named fields
user := User{
    Name:  "Alice",
    Email: "alice@example.com",
    Age:   30,
}
```

#### Naming Conventions
- Packages: lowercase, single word (`http`, `json`)
- Variables: camelCase (`userCount`)
- Constants: camelCase or ALL_CAPS for exported (`MaxRetries`)
- Interfaces: -er suffix (`Reader`, `Writer`, `Logger`)
- Getters: no "Get" prefix (`user.Name()`, not `user.GetName()`)

### Project Context Integration
- **If `.golangci.yml`**: Reference existing linter config
- **If Makefile**: Add linting targets
- **If pre-commit detected**: Add pre-commit hooks

---

## File 5: `go-documentation.md`

### Go-Specific Documentation

#### godoc (Built-in)
- **Format**: Comments directly above declarations
- **Tool**: `go doc` or `godoc -http=:6060`

#### Doc Comment Format

```go
// Package user provides user management functionality.
//
// This package handles user creation, authentication, and profile management.
// All functions are safe for concurrent use unless otherwise noted.
package user

// User represents a registered user in the system.
//
// Email must be unique and is used for authentication.
// CreatedAt is automatically set on user creation.
type User struct {
    ID        int
    Name      string
    Email     string
    CreatedAt time.Time
}

// NewUser creates a new user with the given email and name.
//
// It returns an error if:
//   - email is invalid format
//   - email already exists in the database
//   - name is empty
//
// Example:
//
//	user, err := NewUser("alice@example.com", "Alice")
//	if err != nil {
//	    log.Fatal(err)
//	}
func NewUser(email, name string) (*User, error) {
    // Implementation
}
```

#### Package Documentation
Create `doc.go` for package-level docs:

```go
// Package myproject provides ...
//
// # Overview
//
// This package implements...
//
// # Usage
//
// Basic usage:
//
//	client := myproject.NewClient(apiKey)
//	result, err := client.DoSomething()
//
// # Configuration
//
// The client can be configured with:
//   - API key (required)
//   - Timeout (default: 30s)
//   - Retry count (default: 3)
//
// # Concurrency
//
// All exported functions are safe for concurrent use.
package myproject
```

### Project Context Integration
- **If README.md**: Reference README for getting started
- **If examples/**: Reference example code
- **If complex package**: Emphasize package documentation

---

## Installation Steps You Should Follow

1. **Analyze target Go project**
   - Detect `go.mod` version
   - Detect testing frameworks (testify, etc.)
   - Detect web frameworks (Gin, Echo, Chi)
   - Detect gRPC usage
   - Detect DI frameworks (Wire, Fx)
   - Detect database libraries

2. **Read universal standards**
   - Read all relevant files from `universal/standards/`

3. **Generate Go-specific standards**
   - Use templates above
   - Apply Go idioms and best practices
   - Integrate project-specific patterns
   - Include code examples

4. **Create files**
   - `.praxis-os/standards/development/go-concurrency.md`
   - `.praxis-os/standards/development/go-testing.md`
   - `.praxis-os/standards/development/go-dependencies.md`
   - `.praxis-os/standards/development/go-code-quality.md`
   - `.praxis-os/standards/development/go-documentation.md`

5. **Cross-reference universal standards**
   - Link back to `../../universal/standards/` files
   - Show relationship between universal and Go-specific

6. **Include project context sections**
   - "Your Project Context" sections showing detected patterns
   - Examples from actual codebase (if available)

---

**Result:** Go-specific standards that reference universal CS fundamentals while providing Go-specific implementations (channels, goroutines, interfaces) tailored to the target project.
