# Java Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing Agent OS in a Java project, use these instructions to generate language-specific standards by applying universal CS fundamentals to Java-specific contexts.**

---

## Instructions Overview

You will generate 5 Java-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Analyzing the target Java project
3. Applying Java-specific context (JVM, threads, Spring, etc.)
4. Integrating project-specific patterns (detected frameworks, tools)

## File 1: `java-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/deadlocks.md`
- `universal/standards/concurrency/locking-strategies.md`

### Java-Specific Context to Add

#### Java Concurrency Model
Explain:
- JVM manages threads (not OS threads directly)
- Garbage collector runs concurrently
- `synchronized` keyword for mutual exclusion
- `java.util.concurrent` package for modern concurrency

#### Java Concurrency Models

| Universal Concept | Java Implementation | When to Use |
|-------------------|---------------------|-------------|
| Multi-threading | `Thread`, `Runnable` | Basic threading (legacy) |
| Thread pool | `ExecutorService` | **Recommended** for thread management |
| Async futures | `CompletableFuture` | Async operations, composition |
| Mutex | `synchronized` keyword | Simple mutual exclusion |
| Reentrant Lock | `ReentrantLock` | Advanced locking needs |
| Read-Write Lock | `ReadWriteLock` | Read-heavy workloads |
| Semaphore | `Semaphore` | Resource pooling |
| Atomic operations | `AtomicInteger`, etc. | Lock-free primitives |
| Concurrent collections | `ConcurrentHashMap` | Thread-safe collections |

#### Code Examples

```java
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

// Example: ExecutorService (recommended)
public class ExecutorExample {
    public void processItems(List<Item> items) {
        ExecutorService executor = Executors.newFixedThreadPool(10);
        
        try {
            for (Item item : items) {
                executor.submit(() -> processItem(item));
            }
        } finally {
            executor.shutdown();
            executor.awaitTermination(1, TimeUnit.MINUTES);
        }
    }
}

// Example: synchronized keyword
public class Counter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}

// Example: ReentrantLock (more control)
public class AdvancedCounter {
    private final Lock lock = new ReentrantLock();
    private int count = 0;
    
    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();  // ALWAYS unlock in finally
        }
    }
    
    public boolean tryIncrement(long timeout, TimeUnit unit) 
            throws InterruptedException {
        if (lock.tryLock(timeout, unit)) {
            try {
                count++;
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;
    }
}

// Example: ReadWriteLock
public class Cache {
    private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Lock readLock = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();
    private final Map<String, String> data = new HashMap<>();
    
    public String get(String key) {
        readLock.lock();
        try {
            return data.get(key);
        } finally {
            readLock.unlock();
        }
    }
    
    public void put(String key, String value) {
        writeLock.lock();
        try {
            data.put(key, value);
        } finally {
            writeLock.unlock();
        }
    }
}

// Example: CompletableFuture (async)
public class AsyncExample {
    public CompletableFuture<User> fetchUserAsync(String userId) {
        return CompletableFuture.supplyAsync(() -> {
            return database.getUser(userId);
        });
    }
    
    public CompletableFuture<UserProfile> fetchFullProfile(String userId) {
        CompletableFuture<User> userFuture = fetchUserAsync(userId);
        CompletableFuture<List<Order>> ordersFuture = fetchOrdersAsync(userId);
        
        return userFuture.thenCombine(ordersFuture, (user, orders) -> {
            return new UserProfile(user, orders);
        });
    }
}

// Example: ConcurrentHashMap (thread-safe)
public class UserCache {
    private final ConcurrentHashMap<String, User> cache = new ConcurrentHashMap<>();
    
    public User getOrFetch(String userId) {
        return cache.computeIfAbsent(userId, id -> {
            return database.getUser(id);  // Only fetches if absent
        });
    }
}

// Example: AtomicInteger (lock-free)
public class RequestCounter {
    private final AtomicInteger count = new AtomicInteger(0);
    
    public void increment() {
        count.incrementAndGet();  // Thread-safe, lock-free
    }
    
    public int getCount() {
        return count.get();
    }
}
```

### Project Context Integration
- **If Spring detected**: Add `@Async`, thread pool configuration
- **If Reactor detected**: Add reactive programming patterns
- **If Akka detected**: Add actor model patterns
- **If Kafka detected**: Add consumer thread patterns

---

## File 2: `java-testing.md`

### Source Materials
Read:
- `universal/standards/testing/test-pyramid.md`
- `universal/standards/testing/test-doubles.md`

### Java-Specific Context to Add

#### Testing Frameworks

| Framework | Use Case | Usage |
|-----------|----------|-------|
| JUnit 5 | Modern unit testing | **Recommended** |
| JUnit 4 | Legacy projects | Still widely used |
| TestNG | Alternative to JUnit | Data-driven tests |
| Mockito | Mocking framework | **Standard** for mocks |
| AssertJ | Fluent assertions | Readable assertions |
| Rest Assured | API testing | REST API tests |
| Testcontainers | Integration testing | Docker containers for tests |

#### Testing Patterns

```java
import org.junit.jupiter.api.*;
import org.mockito.*;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

// JUnit 5 example
public class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private EmailService emailService;
    
    @InjectMocks
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }
    
    @Test
    @DisplayName("Should create user with valid data")
    void testCreateUser() {
        // Given
        CreateUserDto userData = new CreateUserDto("alice@example.com", "Alice");
        User expectedUser = new User(1L, "alice@example.com", "Alice");
        
        when(userRepository.save(any(User.class))).thenReturn(expectedUser);
        
        // When
        User createdUser = userService.create(userData);
        
        // Then
        assertThat(createdUser)
            .isNotNull()
            .hasFieldOrPropertyWithValue("email", "alice@example.com")
            .hasFieldOrPropertyWithValue("name", "Alice");
        
        verify(userRepository).save(any(User.class));
        verify(emailService).sendWelcomeEmail("alice@example.com");
    }
    
    @Test
    @DisplayName("Should throw exception for invalid email")
    void testInvalidEmail() {
        // Given
        CreateUserDto userData = new CreateUserDto("invalid-email", "Alice");
        
        // When/Then
        assertThatThrownBy(() -> userService.create(userData))
            .isInstanceOf(ValidationException.class)
            .hasMessageContaining("Invalid email format");
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"", " ", "invalid", "@example.com"})
    @DisplayName("Should reject invalid email formats")
    void testInvalidEmailFormats(String email) {
        assertThatThrownBy(() -> userService.validateEmail(email))
            .isInstanceOf(ValidationException.class);
    }
}

// Integration test with Spring Boot
@SpringBootTest
@AutoConfigureMockMvc
public class UserControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private UserRepository userRepository;
    
    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }
    
    @Test
    void shouldCreateUser() throws Exception {
        String userJson = """
            {
                "email": "alice@example.com",
                "name": "Alice"
            }
            """;
        
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(userJson))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.email").value("alice@example.com"))
            .andExpect(jsonPath("$.id").exists());
    }
}

// Testcontainers for database integration tests
@Testcontainers
public class UserRepositoryTest {
    
    @Container
    private static PostgreSQLContainer<?> postgres = 
        new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("test")
            .withUsername("test")
            .withPassword("test");
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
    
    @Test
    void shouldSaveUser() {
        User user = new User("alice@example.com", "Alice");
        User saved = userRepository.save(user);
        
        assertThat(saved.getId()).isNotNull();
    }
}
```

### Project Context Integration
- **If Spring Boot**: Add `@SpringBootTest`, `@WebMvcTest` patterns
- **If JUnit 4**: Add JUnit 4 syntax
- **If Testcontainers**: Add container patterns
- **If REST API**: Add REST Assured patterns

---

## File 3: `java-dependencies.md`

### Source Materials
Read:
- `universal/standards/architecture/dependency-injection.md`

### Java-Specific Context

#### Build Tools

| Tool | Use Case | Dependency File |
|------|----------|-----------------|
| Maven | Traditional, XML-based | `pom.xml` |
| Gradle | Modern, Groovy/Kotlin DSL | `build.gradle` |

#### Maven Example (pom.xml)

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <java.version>17</java.version>
        <spring.boot.version>3.2.0</spring.boot.version>
    </properties>
    
    <dependencies>
        <!-- Spring Boot -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>${spring.boot.version}</version>
        </dependency>
        
        <!-- Lombok (code generation) -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>1.18.30</version>
            <scope>provided</scope>
        </dependency>
        
        <!-- Test dependencies -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.1</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

#### Gradle Example (build.gradle)

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
}

group = 'com.example'
version = '1.0.0'
sourceCompatibility = '17'

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.projectlombok:lombok:1.18.30'
    
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.1'
    testImplementation 'org.mockito:mockito-core:5.7.0'
}

test {
    useJUnitPlatform()
}
```

#### Dependency Injection (Spring)

```java
// Constructor injection (recommended)
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    // Constructor injection - no @Autowired needed in Spring 4.3+
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}

// Interface-based DI
public interface UserRepository {
    User save(User user);
    Optional<User> findById(Long id);
}

@Repository
public class JpaUserRepository implements UserRepository {
    @PersistenceContext
    private EntityManager entityManager;
    
    @Override
    public User save(User user) {
        entityManager.persist(user);
        return user;
    }
}

// Configuration
@Configuration
public class AppConfig {
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    @Bean
    @Profile("production")
    public EmailService emailService() {
        return new SmtpEmailService();
    }
    
    @Bean
    @Profile("development")
    public EmailService emailService() {
        return new ConsoleEmailService();
    }
}
```

### Project Context Integration
- **If Maven**: Reference existing `pom.xml`
- **If Gradle**: Reference existing `build.gradle`
- **If Spring**: Add Spring DI patterns
- **If Guice**: Add Guice DI patterns

---

## File 4: `java-code-quality.md`

### Java-Specific Tools

#### Formatting
- **Checkstyle**: Style checker
  - Config: `checkstyle.xml`
  - Enforces consistent style

- **google-java-format**: Google's formatter
  - Opinionated, consistent

#### Linting
- **PMD**: Static analysis
  - Finds common bugs, code smells
  
- **SpotBugs**: Bug detection
  - Successor to FindBugs
  - Finds potential bugs

- **SonarQube**: Comprehensive analysis
  - Code quality, security, bugs

#### Code Standards

```java
// Naming conventions
public class UserService {}  // PascalCase for classes
private String firstName;    // camelCase for variables
private static final int MAX_RETRIES = 3;  // ALL_CAPS for constants
public void processData() {} // camelCase for methods

// Documentation (Javadoc - MANDATORY for public API)
/**
 * Creates a new user in the system.
 *
 * <p>This method validates the user data, saves it to the database,
 * and sends a welcome email.</p>
 *
 * @param userData the user data for creation
 * @return the created user with generated ID
 * @throws ValidationException if the email is invalid
 * @throws DuplicateEmailException if the email already exists
 * @see User
 * @since 1.0.0
 */
public User create(CreateUserDto userData) {
    // Implementation
}

// Error handling
// ✅ GOOD: Specific exceptions
public User getUser(Long id) throws UserNotFoundException {
    return userRepository.findById(id)
        .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
}

// ✅ GOOD: Try-with-resources (auto-close)
public String readFile(String path) throws IOException {
    try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
        return reader.lines().collect(Collectors.joining("\n"));
    }
}

// ✅ GOOD: Modern Java features (Java 8+)
// Streams
List<String> names = users.stream()
    .filter(user -> user.isActive())
    .map(User::getName)
    .collect(Collectors.toList());

// Optional instead of null
public Optional<User> findUser(Long id) {
    return userRepository.findById(id);
}

// Lambda expressions
users.forEach(user -> sendEmail(user));

// Method references
users.forEach(this::sendEmail);

// ✅ GOOD: Immutable objects
@Value  // Lombok - generates immutable class
public class User {
    Long id;
    String email;
    String name;
}

// Or manually
public final class User {
    private final Long id;
    private final String email;
    private final String name;
    
    public User(Long id, String email, String name) {
        this.id = id;
        this.email = email;
        this.name = name;
    }
    
    public Long getId() { return id; }
    public String getEmail() { return email; }
    public String getName() { return name; }
}
```

### Project Context Integration
- **If Spring Boot**: Add Spring Boot best practices
- **If Lombok**: Add Lombok annotations
- **If Checkstyle config**: Reference existing config

---

## File 5: `java-documentation.md`

### Java-Specific Documentation

#### Javadoc (Standard)

```java
/**
 * Service for managing user accounts.
 *
 * <p>This service handles user creation, authentication, and profile management.
 * All methods are transactional and will roll back on failure.</p>
 *
 * <p><b>Thread Safety:</b> This class is thread-safe when used with Spring's
 * default singleton scope.</p>
 *
 * @author John Doe
 * @version 1.0.0
 * @since 1.0.0
 * @see User
 * @see UserRepository
 */
@Service
@Transactional
public class UserService {
    
    /**
     * Creates a new user.
     *
     * <p>This method performs the following:
     * <ol>
     *   <li>Validates the user data</li>
     *   <li>Checks for duplicate email</li>
     *   <li>Saves user to database</li>
     *   <li>Sends welcome email</li>
     * </ol>
     *
     * @param userData the user data for creation, must not be {@code null}
     * @return the created user with generated ID, never {@code null}
     * @throws ValidationException if {@code userData} is invalid
     * @throws DuplicateEmailException if the email already exists
     * @throws NullPointerException if {@code userData} is {@code null}
     * @see CreateUserDto
     */
    public User create(@NonNull CreateUserDto userData) {
        // Implementation
    }
    
    /**
     * Finds a user by ID.
     *
     * @param id the user ID to search for
     * @return an {@link Optional} containing the user if found, empty otherwise
     * @apiNote This method will never throw an exception for missing users
     */
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }
}
```

#### Generating Javadoc

```bash
# Maven
mvn javadoc:javadoc

# Gradle
./gradlew javadoc
```

#### Package Documentation (package-info.java)

```java
/**
 * User management domain.
 *
 * <p>This package contains classes for managing user accounts, including:
 * <ul>
 *   <li>User entity and DTOs</li>
 *   <li>User repository interfaces</li>
 *   <li>User service implementations</li>
 * </ul>
 *
 * <p><b>Usage Example:</b>
 * <pre>{@code
 * UserService userService = context.getBean(UserService.class);
 * User user = userService.create(new CreateUserDto("alice@example.com", "Alice"));
 * }</pre>
 *
 * @since 1.0.0
 */
package com.example.myapp.domain.user;
```

### Project Context Integration
- **If Spring**: Add Spring-specific documentation conventions
- **If library project**: Emphasize public API documentation
- **If Maven**: Add Maven site generation

---

## Installation Steps You Should Follow

1. **Analyze target Java project**
   - Detect build tool (Maven, Gradle)
   - Detect Java version
   - Detect framework (Spring Boot, Jakarta EE, Micronaut)
   - Detect testing framework (JUnit 4/5, TestNG)
   - Detect libraries (Lombok, Guava, etc.)
   - Detect code quality tools (Checkstyle, PMD)

2. **Read universal standards**
   - Read all relevant files from `universal/standards/`

3. **Generate Java-specific standards**
   - Use templates above
   - Apply Java idioms (streams, Optional, interfaces)
   - Integrate project-specific patterns
   - Include code examples

4. **Create files**
   - `.agent-os/standards/development/java-concurrency.md`
   - `.agent-os/standards/development/java-testing.md`
   - `.agent-os/standards/development/java-dependencies.md`
   - `.agent-os/standards/development/java-code-quality.md`
   - `.agent-os/standards/development/java-documentation.md`

5. **Cross-reference universal standards**
   - Link back to `../../universal/standards/` files
   - Show relationship between universal and Java-specific

6. **Include project context sections**
   - "Your Project Context" sections showing detected patterns
   - Examples from actual codebase (if available)

---

**Result:** Java-specific standards that reference universal CS fundamentals while providing Java-specific implementations (JVM, Spring, streams, Optional) tailored to the target project.
