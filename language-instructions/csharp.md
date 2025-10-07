# C# Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing Agent OS in a C# project, use these instructions to generate language-specific standards by applying universal CS fundamentals to C#-specific contexts.**

---

## Instructions Overview

You will generate 5 C#-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Analyzing the target C# project
3. Applying C#-specific context (.NET, async/await, LINQ, etc.)
4. Integrating project-specific patterns (detected frameworks, tools)

## File 1: `csharp-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/deadlocks.md`
- `universal/standards/concurrency/locking-strategies.md`

### C#-Specific Context to Add

#### C# Concurrency Model
Explain:
- .NET runtime (CLR) manages threads
- `async`/`await` is the primary concurrency model
- Task Parallel Library (TPL) for parallel operations
- `lock` keyword for mutual exclusion

#### C# Concurrency Models

| Universal Concept | C# Implementation | When to Use |
|-------------------|-------------------|-------------|
| Async I/O | `async`/`await` | **Recommended** for I/O operations |
| Multi-threading | `Thread` class | Legacy (avoid) |
| Thread pool | `Task.Run()` | CPU-bound work |
| Parallel operations | `Parallel.For/ForEach` | Data parallelism |
| Mutex | `lock` keyword | Simple mutual exclusion |
| Semaphore | `SemaphoreSlim` | Resource pooling, throttling |
| Read-Write Lock | `ReaderWriterLockSlim` | Read-heavy workloads |
| Concurrent collections | `ConcurrentDictionary<>` | Thread-safe collections |
| Channels | `System.Threading.Channels` | Producer-consumer patterns |

#### Code Examples

```csharp
using System;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;

// Example: async/await (recommended)
public class UserService
{
    public async Task<User> GetUserAsync(string userId)
    {
        var response = await _httpClient.GetAsync($"/api/users/{userId}");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsAsync<User>();
    }
    
    // Multiple async operations in parallel
    public async Task<UserProfile> GetFullProfileAsync(string userId)
    {
        var userTask = GetUserAsync(userId);
        var ordersTask = GetOrdersAsync(userId);
        
        await Task.WhenAll(userTask, ordersTask);
        
        return new UserProfile
        {
            User = await userTask,
            Orders = await ordersTask
        };
    }
}

// Example: lock keyword
public class Counter
{
    private readonly object _lock = new object();
    private int _count = 0;
    
    public void Increment()
    {
        lock (_lock)
        {
            _count++;
        }
    }
    
    public int GetCount()
    {
        lock (_lock)
        {
            return _count;
        }
    }
}

// Example: SemaphoreSlim for throttling
public class RateLimiter
{
    private readonly SemaphoreSlim _semaphore = new SemaphoreSlim(5); // Max 5 concurrent
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> operation)
    {
        await _semaphore.WaitAsync();
        try
        {
            return await operation();
        }
        finally
        {
            _semaphore.Release();
        }
    }
}

// Example: ReaderWriterLockSlim
public class Cache
{
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    private readonly Dictionary<string, string> _data = new Dictionary<string, string>();
    
    public string Get(string key)
    {
        _lock.EnterReadLock();
        try
        {
            return _data.TryGetValue(key, out var value) ? value : null;
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }
    
    public void Set(string key, string value)
    {
        _lock.EnterWriteLock();
        try
        {
            _data[key] = value;
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
}

// Example: ConcurrentDictionary (thread-safe)
public class UserCache
{
    private readonly ConcurrentDictionary<string, User> _cache = new ConcurrentDictionary<string, User>();
    
    public User GetOrAdd(string userId)
    {
        return _cache.GetOrAdd(userId, id => _database.GetUser(id));
    }
}

// Example: Parallel.ForEach for data parallelism
public void ProcessItems(List<Item> items)
{
    Parallel.ForEach(items, new ParallelOptions { MaxDegreeOfParallelism = 4 }, item =>
    {
        ProcessItem(item);
    });
}

// Example: Channels for producer-consumer
public class DataPipeline
{
    private readonly Channel<Data> _channel = Channel.CreateUnbounded<Data>();
    
    public async Task ProduceAsync(CancellationToken cancellationToken)
    {
        await foreach (var data in FetchDataAsync(cancellationToken))
        {
            await _channel.Writer.WriteAsync(data, cancellationToken);
        }
        _channel.Writer.Complete();
    }
    
    public async Task ConsumeAsync(CancellationToken cancellationToken)
    {
        await foreach (var data in _channel.Reader.ReadAllAsync(cancellationToken))
        {
            await ProcessDataAsync(data);
        }
    }
}

// Example: CancellationToken for cancellation
public async Task<User> FetchUserAsync(string userId, CancellationToken cancellationToken)
{
    using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
    cts.CancelAfter(TimeSpan.FromSeconds(30)); // Timeout
    
    return await _httpClient.GetFromJsonAsync<User>($"/api/users/{userId}", cts.Token);
}
```

### Project Context Integration
- **If ASP.NET Core**: Add async middleware, controller patterns
- **If Entity Framework**: Add async database operations
- **If SignalR**: Add real-time communication patterns
- **If Blazor**: Add async UI updates

---

## File 2: `csharp-testing.md`

### Source Materials
Read:
- `universal/standards/testing/test-pyramid.md`
- `universal/standards/testing/test-doubles.md`

### C#-Specific Context to Add

#### Testing Frameworks

| Framework | Use Case | Usage |
|-----------|----------|-------|
| xUnit | Modern, recommended | **Recommended** for new projects |
| NUnit | Alternative, mature | Still widely used |
| MSTest | Microsoft's framework | Built into Visual Studio |
| Moq | Mocking framework | **Standard** for mocks |
| FluentAssertions | Fluent assertions | Readable assertions |
| AutoFixture | Test data generation | Reduces boilerplate |
| Testcontainers | Integration testing | Docker containers |

#### Testing Patterns

```csharp
using Xunit;
using Moq;
using FluentAssertions;
using AutoFixture;

// xUnit example
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _userRepositoryMock;
    private readonly Mock<IEmailService> _emailServiceMock;
    private readonly UserService _sut; // System Under Test
    private readonly IFixture _fixture;
    
    public UserServiceTests()
    {
        _userRepositoryMock = new Mock<IUserRepository>();
        _emailServiceMock = new Mock<IEmailService>();
        _sut = new UserService(_userRepositoryMock.Object, _emailServiceMock.Object);
        _fixture = new Fixture();
    }
    
    [Fact]
    public async Task CreateAsync_ValidData_ReturnsUser()
    {
        // Arrange
        var userData = _fixture.Create<CreateUserDto>();
        var expectedUser = _fixture.Build<User>()
            .With(u => u.Email, userData.Email)
            .Create();
        
        _userRepositoryMock
            .Setup(r => r.SaveAsync(It.IsAny<User>()))
            .ReturnsAsync(expectedUser);
        
        // Act
        var result = await _sut.CreateAsync(userData);
        
        // Assert
        result.Should().NotBeNull();
        result.Email.Should().Be(userData.Email);
        
        _userRepositoryMock.Verify(r => r.SaveAsync(It.IsAny<User>()), Times.Once);
        _emailServiceMock.Verify(e => e.SendWelcomeEmailAsync(userData.Email), Times.Once);
    }
    
    [Theory]
    [InlineData("")]
    [InlineData(" ")]
    [InlineData("invalid-email")]
    public async Task CreateAsync_InvalidEmail_ThrowsValidationException(string email)
    {
        // Arrange
        var userData = new CreateUserDto { Email = email, Name = "Test" };
        
        // Act
        Func<Task> act = async () => await _sut.CreateAsync(userData);
        
        // Assert
        await act.Should().ThrowAsync<ValidationException>()
            .WithMessage("*email*");
    }
}

// Integration test with WebApplicationFactory
public class UserControllerIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;
    
    public UserControllerIntegrationTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = _factory.CreateClient();
    }
    
    [Fact]
    public async Task CreateUser_ValidData_Returns201()
    {
        // Arrange
        var userData = new { Email = "alice@example.com", Name = "Alice" };
        
        // Act
        var response = await _client.PostAsJsonAsync("/api/users", userData);
        
        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var user = await response.Content.ReadFromJsonAsync<User>();
        user.Email.Should().Be("alice@example.com");
    }
}

// Testcontainers example
public class UserRepositoryTests : IAsyncLifetime
{
    private PostgreSqlContainer _postgres;
    private UserRepository _repository;
    
    public async Task InitializeAsync()
    {
        _postgres = new PostgreSqlBuilder()
            .WithDatabase("testdb")
            .WithUsername("test")
            .WithPassword("test")
            .Build();
        
        await _postgres.StartAsync();
        
        var connectionString = _postgres.GetConnectionString();
        _repository = new UserRepository(connectionString);
    }
    
    public async Task DisposeAsync()
    {
        await _postgres.DisposeAsync();
    }
    
    [Fact]
    public async Task SaveAsync_ValidUser_ReturnsUserWithId()
    {
        // Arrange
        var user = new User { Email = "alice@example.com", Name = "Alice" };
        
        // Act
        var saved = await _repository.SaveAsync(user);
        
        // Assert
        saved.Id.Should().BeGreaterThan(0);
    }
}
```

### Project Context Integration
- **If ASP.NET Core**: Add `WebApplicationFactory` patterns
- **If Entity Framework**: Add in-memory database testing
- **If Testcontainers**: Add container patterns

---

## File 3: `csharp-dependencies.md`

### Source Materials
Read:
- `universal/standards/architecture/dependency-injection.md`

### C#-Specific Context

#### Package Management (NuGet)

```xml
<!-- .csproj file -->
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  
  <ItemGroup>
    <!-- Exact version -->
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    
    <!-- Version range -->
    <PackageReference Include="Serilog" Version="3.*" />
    
    <!-- Latest stable (not recommended) -->
    <PackageReference Include="Newtonsoft.Json" Version="*" />
  </ItemGroup>
</Project>
```

#### Dependency Injection (Built-in .NET)

```csharp
// Program.cs (ASP.NET Core)
var builder = WebApplication.CreateBuilder(args);

// Register services
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();
builder.Services.AddTransient<IEmailService, SendGridEmailService>();

// Configuration
builder.Services.Configure<EmailSettings>(builder.Configuration.GetSection("Email"));

// HTTP clients
builder.Services.AddHttpClient<IGitHubService, GitHubService>(client =>
{
    client.BaseAddress = new Uri("https://api.github.com");
});

var app = builder.Build();

// Service with constructor injection
public class UserService : IUserService
{
    private readonly IUserRepository _userRepository;
    private readonly IEmailService _emailService;
    private readonly ILogger<UserService> _logger;
    
    public UserService(
        IUserRepository userRepository,
        IEmailService emailService,
        ILogger<UserService> logger)
    {
        _userRepository = userRepository;
        _emailService = emailService;
        _logger = logger;
    }
    
    public async Task<User> CreateAsync(CreateUserDto userData)
    {
        _logger.LogInformation("Creating user {Email}", userData.Email);
        
        var user = new User { Email = userData.Email, Name = userData.Name };
        await _userRepository.SaveAsync(user);
        await _emailService.SendWelcomeEmailAsync(user.Email);
        
        return user;
    }
}

// Options pattern
public class EmailSettings
{
    public string ApiKey { get; set; }
    public string FromAddress { get; set; }
}

public class EmailService
{
    private readonly EmailSettings _settings;
    
    public EmailService(IOptions<EmailSettings> settings)
    {
        _settings = settings.Value;
    }
}
```

### Project Context Integration
- **If .NET Framework**: Add legacy DI patterns (Autofac, Ninject)
- **If .NET Core/5+**: Use built-in DI
- **If MediatR**: Add CQRS patterns

---

## File 4: `csharp-code-quality.md`

### C#-Specific Tools

#### Formatting
- **dotnet format**: Built-in formatter
  - Usage: `dotnet format`
  - Config: `.editorconfig`

#### Linting
- **StyleCop**: Style rules
  - Enforces C# style guidelines
  
- **Roslynator**: Code analysis
  - 500+ analyzers and refactorings

#### Code Standards

```csharp
// Naming conventions
public class UserService {}  // PascalCase for classes
private string _firstName;   // _camelCase for private fields
public string FirstName { get; set; }  // PascalCase for properties
private const int MaxRetries = 3;  // PascalCase for constants
public async Task ProcessDataAsync() {}  // Async suffix for async methods

// Nullable reference types (C# 8+) - MANDATORY
#nullable enable

public class UserService
{
    public User? FindUser(string userId)  // ? = nullable
    {
        return _repository.Get(userId);
    }
    
    public User GetUser(string userId)  // No ? = non-null
    {
        return _repository.Get(userId) ?? throw new NotFoundException();
    }
}

// XML documentation (MANDATORY for public API)
/// <summary>
/// Creates a new user in the system.
/// </summary>
/// <param name="userData">The user data for creation.</param>
/// <returns>The created user with generated ID.</returns>
/// <exception cref="ValidationException">
/// Thrown when the email is invalid.
/// </exception>
/// <exception cref="DuplicateEmailException">
/// Thrown when the email already exists.
/// </exception>
public async Task<User> CreateAsync(CreateUserDto userData)
{
    // Implementation
}

// Modern C# features (C# 8+)
// Pattern matching
public string GetUserStatus(User user) => user.Status switch
{
    UserStatus.Active => "Active",
    UserStatus.Inactive => "Inactive",
    UserStatus.Suspended => "Suspended",
    _ => throw new ArgumentException("Unknown status")
};

// Records for immutable data
public record CreateUserDto(string Email, string Name);

public record User
{
    public int Id { get; init; }
    public string Email { get; init; }
    public string Name { get; init; }
}

// Init-only properties
public class User
{
    public int Id { get; init; }
    public string Email { get; init; }
}

// Using declarations (auto-dispose)
public async Task<string> ReadFileAsync(string path)
{
    using var reader = new StreamReader(path);
    return await reader.ReadToEndAsync();
}

// LINQ (language integrated query)
var activeUsers = users
    .Where(u => u.IsActive)
    .OrderBy(u => u.Name)
    .Select(u => u.Name)
    .ToList();

// Async enumerable (C# 8+)
public async IAsyncEnumerable<User> GetUsersAsync()
{
    await foreach (var user in _repository.GetAllAsync())
    {
        yield return user;
    }
}
```

#### .editorconfig

```ini
root = true

[*.cs]
# Formatting
indent_style = space
indent_size = 4
end_of_line = crlf

# Naming conventions
dotnet_naming_rule.private_fields_should_be_camelcase.severity = warning
dotnet_naming_rule.private_fields_should_be_camelcase.symbols = private_fields
dotnet_naming_rule.private_fields_should_be_camelcase.style = camelcase_underscore

# Nullable reference types
dotnet_diagnostic.CS8600.severity = error
dotnet_diagnostic.CS8601.severity = error
dotnet_diagnostic.CS8602.severity = error
dotnet_diagnostic.CS8603.severity = error
```

### Project Context Integration
- **If .editorconfig**: Reference existing config
- **If StyleCop**: Add StyleCop patterns
- **If ASP.NET Core**: Add ASP.NET Core best practices

---

## File 5: `csharp-documentation.md`

### C#-Specific Documentation

#### XML Documentation

```csharp
/// <summary>
/// Service for managing user accounts.
/// </summary>
/// <remarks>
/// <para>
/// This service handles user creation, authentication, and profile management.
/// All methods are async and return <see cref="Task"/> or <see cref="Task{TResult}"/>.
/// </para>
/// <para>
/// <strong>Thread Safety:</strong> This class is thread-safe when used with
/// ASP.NET Core's default scoped lifetime.
/// </para>
/// <example>
/// <code>
/// var userService = serviceProvider.GetService&lt;IUserService&gt;();
/// var user = await userService.CreateAsync(new CreateUserDto("alice@example.com", "Alice"));
/// </code>
/// </example>
/// </remarks>
public class UserService : IUserService
{
    /// <summary>
    /// Creates a new user.
    /// </summary>
    /// <param name="userData">The user data for creation.</param>
    /// <param name="cancellationToken">Cancellation token for the operation.</param>
    /// <returns>
    /// A <see cref="Task{User}"/> representing the asynchronous operation,
    /// containing the created user with generated ID.
    /// </returns>
    /// <exception cref="ValidationException">
    /// Thrown when <paramref name="userData"/> is invalid.
    /// </exception>
    /// <exception cref="DuplicateEmailException">
    /// Thrown when the email in <paramref name="userData"/> already exists.
    /// </exception>
    /// <exception cref="ArgumentNullException">
    /// Thrown when <paramref name="userData"/> is <c>null</c>.
    /// </exception>
    public async Task<User> CreateAsync(
        CreateUserDto userData,
        CancellationToken cancellationToken = default)
    {
        // Implementation
    }
}
```

#### Generating Documentation

```bash
# Using DocFX
dotnet tool install -g docfx
docfx init
docfx build
docfx serve

# Visual Studio XML documentation
# Enable in .csproj:
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <NoWarn>$(NoWarn);1591</NoWarn>
</PropertyGroup>
```

#### README.md Structure

```markdown
# Project Name

[![NuGet](https://img.shields.io/nuget/v/MyPackage.svg)](https://www.nuget.org/packages/MyPackage/)
[![Build](https://github.com/user/repo/actions/workflows/build.yml/badge.svg)](https://github.com/user/repo/actions)

Brief description

## Installation

```bash
dotnet add package MyPackage
```

## Quick Start

```csharp
var client = new MyClient("api_key");
var result = await client.DoSomethingAsync();
```

## Documentation
See [Documentation Site](https://docs.example.com)
```

### Project Context Integration
- **If library project**: Emphasize public API documentation
- **If NuGet package**: Add NuGet packaging guidelines
- **If DocFX**: Reference DocFX configuration

---

## Installation Steps You Should Follow

1. **Analyze target C# project**
   - Detect .NET version (.NET Framework, .NET Core, .NET 5+)
   - Detect project type (ASP.NET Core, Console, Library)
   - Detect testing framework (xUnit, NUnit, MSTest)
   - Detect ORM (Entity Framework, Dapper)
   - Detect nullable reference types enabled
   - Check .editorconfig

2. **Read universal standards**
   - Read all relevant files from `universal/standards/`

3. **Generate C#-specific standards**
   - Use templates above
   - Emphasize async/await, LINQ, records
   - Apply C# idioms and conventions
   - Integrate project-specific patterns
   - Include code examples

4. **Create files**
   - `.agent-os/standards/development/csharp-concurrency.md`
   - `.agent-os/standards/development/csharp-testing.md`
   - `.agent-os/standards/development/csharp-dependencies.md`
   - `.agent-os/standards/development/csharp-code-quality.md`
   - `.agent-os/standards/development/csharp-documentation.md`

5. **Cross-reference universal standards**
   - Link back to `../../universal/standards/` files
   - Show relationship between universal and C#-specific

6. **Include project context sections**
   - "Your Project Context" sections showing detected patterns
   - Examples from actual codebase (if available)

---

**Result:** C#-specific standards that reference universal CS fundamentals while providing C#-specific implementations (async/await, LINQ, dependency injection, nullable reference types) tailored to the target project.
