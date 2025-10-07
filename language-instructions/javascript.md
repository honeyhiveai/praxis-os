# JavaScript Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing Agent OS in a JavaScript project, use these instructions to generate language-specific standards by applying universal CS fundamentals to JavaScript-specific contexts.**

---

## Instructions Overview

You will generate 5 JavaScript-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Analyzing the target JavaScript project
3. Applying JavaScript-specific context (event loop, promises, npm, etc.)
4. Integrating project-specific patterns (detected frameworks, tools)

## File 1: `javascript-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/deadlocks.md`
- `universal/standards/concurrency/locking-strategies.md`

### JavaScript-Specific Context to Add

#### The Event Loop
Explain:
- JavaScript is single-threaded (no true parallelism)
- Event loop handles asynchronous operations
- Non-blocking I/O through callbacks, promises, async/await
- Worker threads for CPU-intensive tasks

#### JavaScript Concurrency Models

| Universal Concept | JavaScript Implementation | When to Use |
|-------------------|---------------------------|-------------|
| Async I/O | Callbacks (legacy) | Legacy code only |
| Async I/O | Promises | Modern async code |
| Async I/O | `async`/`await` | **Recommended** (cleanest) |
| Multi-threading | Web Workers (browser) | CPU-intensive in browser |
| Multi-threading | Worker Threads (Node.js) | CPU-intensive in Node.js |
| Event-driven | Event emitters | Pub/sub patterns |
| Mutex | Not needed (single-threaded) | Use atomic operations |

#### Code Examples

```javascript
// Promises
function fetchUser(userId) {
    return fetch(`/api/users/${userId}`)
        .then(response => response.json())
        .then(user => processUser(user))
        .catch(error => console.error('Failed:', error));
}

// Async/await (preferred)
async function fetchUser(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const user = await response.json();
        return processUser(user);
    } catch (error) {
        console.error('Failed:', error);
        throw error;
    }
}

// Promise.all for parallel operations
async function fetchMultipleUsers(userIds) {
    const promises = userIds.map(id => fetchUser(id));
    return Promise.all(promises);  // Executes in parallel
}

// Worker threads for CPU-intensive work
const { Worker } = require('worker_threads');

function runHeavyComputation(data) {
    return new Promise((resolve, reject) => {
        const worker = new Worker('./compute-worker.js');
        worker.postMessage(data);
        worker.on('message', resolve);
        worker.on('error', reject);
    });
}

// Event emitters for pub/sub
const EventEmitter = require('events');
class UserService extends EventEmitter {
    createUser(userData) {
        const user = saveToDatabase(userData);
        this.emit('userCreated', user);  // Notify listeners
        return user;
    }
}

const userService = new UserService();
userService.on('userCreated', user => {
    console.log('New user:', user.email);
});
```

### Project Context Integration

Analyze the target project and add:
- **If Node.js**: Add Node.js-specific patterns (streams, cluster)
- **If Express detected**: Add middleware patterns, async route handlers
- **If React detected**: Add useState, useEffect, async state management
- **If Vue detected**: Add reactive data, watchers, async computed
- **If Angular detected**: Add RxJS observables, async pipes
- **If Electron detected**: Add IPC, renderer/main process communication

---

## File 2: `javascript-testing.md`

### Source Materials
Read:
- `universal/standards/testing/test-pyramid.md`
- `universal/standards/testing/test-doubles.md`

### JavaScript-Specific Context to Add

#### Testing Frameworks

| Framework | Use Case | Usage |
|-----------|----------|-------|
| Jest | React, modern Node.js | **Recommended** for most projects |
| Mocha | Flexible, customizable | With Chai for assertions |
| Jasmine | BDD style | Built-in assertions |
| Vitest | Vite projects | Jest-compatible, faster |
| Cypress | E2E testing | Browser automation |
| Playwright | E2E testing | Multi-browser |

#### Testing Patterns

```javascript
// Jest example
describe('UserService', () => {
    let userService;
    
    beforeEach(() => {
        userService = new UserService();
    });
    
    afterEach(() => {
        jest.clearAllMocks();
    });
    
    test('creates user with valid data', async () => {
        const userData = { email: 'test@example.com', name: 'Test' };
        const user = await userService.create(userData);
        
        expect(user).toBeDefined();
        expect(user.email).toBe('test@example.com');
    });
    
    test('throws error with invalid email', async () => {
        const userData = { email: 'invalid', name: 'Test' };
        
        await expect(userService.create(userData))
            .rejects
            .toThrow('Invalid email format');
    });
});

// Mocking with Jest
jest.mock('./database');
const database = require('./database');

test('fetches user from database', async () => {
    database.query.mockResolvedValue({ id: 1, name: 'Alice' });
    
    const user = await fetchUser(1);
    
    expect(user.name).toBe('Alice');
    expect(database.query).toHaveBeenCalledWith('SELECT * FROM users WHERE id = ?', 1);
});

// Testing async code
test('handles API errors gracefully', async () => {
    fetch.mockRejectedValue(new Error('Network error'));
    
    const result = await fetchUserWithFallback(1);
    
    expect(result).toEqual({ id: 1, name: 'Unknown' });  // Fallback
});

// Snapshot testing (React)
test('renders user profile correctly', () => {
    const tree = renderer
        .create(<UserProfile user={{ name: 'Alice', email: 'alice@example.com' }} />)
        .toJSON();
    expect(tree).toMatchSnapshot();
});
```

### Project Context Integration
- **If Jest**: Add Jest-specific patterns, snapshot testing
- **If React**: Add React Testing Library patterns
- **If Cypress detected**: Add E2E test patterns
- **If Playwright detected**: Add cross-browser test patterns

---

## File 3: `javascript-dependencies.md`

### Source Materials
Read:
- `universal/standards/architecture/dependency-injection.md`

### JavaScript-Specific Context

#### Package Managers

| Manager | Use Case | Lock File |
|---------|----------|-----------|
| npm | Default, standard | `package-lock.json` |
| yarn | Faster, workspaces | `yarn.lock` |
| pnpm | Disk-efficient | `pnpm-lock.yaml` |

#### Version Pinning (package.json)

| Specifier | Meaning | When to Use | Example |
|-----------|---------|-------------|---------|
| `1.2.3` | Exact version | **Recommended** | `"react": "18.2.0"` |
| `~1.2.3` | Patch updates OK | Patch-level updates | `"lodash": "~4.17.0"` |
| `^1.2.3` | Minor updates OK | **Default npm behavior** | `"express": "^4.18.0"` |
| `*` or `latest` | Any version | **Never** (non-deterministic) | ❌ Don't use |

#### Example package.json

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.2",
    "react": "18.2.0",
    "lodash": "~4.17.21"
  },
  "devDependencies": {
    "jest": "^29.5.0",
    "eslint": "^8.40.0"
  },
  "scripts": {
    "test": "jest",
    "lint": "eslint src/",
    "build": "webpack --mode production"
  }
}
```

#### Dependency Injection Patterns

```javascript
// Constructor injection
class UserService {
    constructor(database, logger, cache) {
        this.database = database;
        this.logger = logger;
        this.cache = cache;
    }
    
    async getUser(userId) {
        this.logger.info(`Fetching user ${userId}`);
        const cached = await this.cache.get(userId);
        if (cached) return cached;
        
        const user = await this.database.query('SELECT * FROM users WHERE id = ?', userId);
        await this.cache.set(userId, user);
        return user;
    }
}

// Factory pattern
function createUserService({ database, logger, cache }) {
    return new UserService(database, logger, cache);
}

// Dependency injection with TypeScript (InversifyJS)
import { injectable, inject } from 'inversify';

@injectable()
class UserService {
    constructor(
        @inject('Database') private database: Database,
        @inject('Logger') private logger: Logger
    ) {}
}
```

### Project Context Integration
- **If `package-lock.json`**: Using npm
- **If `yarn.lock`**: Using Yarn
- **If `pnpm-lock.yaml`**: Using pnpm
- **If monorepo**: Add workspace patterns
- **If TypeScript**: Add TypeScript DI patterns

---

## File 4: `javascript-code-quality.md`

### JavaScript-Specific Tools

#### Formatting
- **Prettier**: Opinionated formatter (**recommended**)
  - Config: `.prettierrc` or `package.json` → `"prettier"`
  - Integrates with ESLint

#### Linting
- **ESLint**: Standard linter (**mandatory**)
  - Config: `.eslintrc.json` or `eslintConfig` in `package.json`
  - Plugins: React, Vue, Angular, etc.

#### Type Checking
- **JSDoc**: Type annotations in comments
- **TypeScript**: Full type system (**recommended for large projects**)
- **Flow**: Facebook's type checker (less common now)

#### Code Examples

```javascript
// ESLint configuration
// .eslintrc.json
{
  "extends": ["eslint:recommended", "plugin:react/recommended"],
  "env": {
    "browser": true,
    "node": true,
    "es2021": true
  },
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "prefer-const": "error"
  }
}

// JSDoc type annotations
/**
 * Process user data.
 * @param {Object} user - User object
 * @param {string} user.email - User email
 * @param {number} user.age - User age
 * @param {Object} config - Configuration options
 * @param {number} [config.timeout=30] - Timeout in seconds (optional)
 * @returns {Promise<Object>} Processed user data
 * @throws {ValidationError} If user data is invalid
 */
async function processUser(user, config = {}) {
    const timeout = config.timeout || 30;
    // Implementation
}

// Modern JavaScript best practices
// Use const by default, let when reassignment needed
const user = await fetchUser(userId);
let retryCount = 0;

// Destructuring
const { email, name } = user;
const [first, ...rest] = items;

// Template literals
console.log(`User ${name} has email ${email}`);

// Arrow functions
const double = x => x * 2;
const add = (a, b) => a + b;

// Optional chaining
const userEmail = user?.profile?.email;

// Nullish coalescing
const timeout = config.timeout ?? 30;

// Async/await over .then()
// ❌ BAD
fetch(url).then(res => res.json()).then(data => process(data));

// ✅ GOOD
const response = await fetch(url);
const data = await response.json();
process(data);
```

### Project Context Integration
- **If `.eslintrc.*`**: Reference existing ESLint config
- **If `.prettierrc`**: Reference Prettier config
- **If TypeScript**: Add TypeScript-specific patterns
- **If React**: Add React-specific linting rules
- **If Vue**: Add Vue-specific linting rules

---

## File 5: `javascript-documentation.md`

### JavaScript-Specific Documentation

#### JSDoc (Standard)
- **Format**: Comment blocks with `@` tags
- **Tools**: `jsdoc` generates HTML docs
- **Integration**: VSCode IntelliSense, TypeScript

#### Documentation Example

```javascript
/**
 * User management service.
 * 
 * Handles user creation, authentication, and profile management.
 * All methods return Promises and should be used with async/await.
 * 
 * @class
 * @example
 * const userService = new UserService(database);
 * const user = await userService.create({ email: 'test@example.com' });
 */
class UserService {
    /**
     * Create a new UserService instance.
     * 
     * @param {Object} database - Database connection
     * @param {Object} [options] - Optional configuration
     * @param {number} [options.timeout=30] - Query timeout in seconds
     * @throws {TypeError} If database is not provided
     */
    constructor(database, options = {}) {
        if (!database) {
            throw new TypeError('Database is required');
        }
        this.database = database;
        this.timeout = options.timeout || 30;
    }
    
    /**
     * Create a new user.
     * 
     * @async
     * @param {Object} userData - User data
     * @param {string} userData.email - User email (must be unique)
     * @param {string} userData.name - User full name
     * @param {number} [userData.age] - User age (optional)
     * @returns {Promise<Object>} Created user object with ID
     * @throws {ValidationError} If email is invalid or already exists
     * @throws {DatabaseError} If database operation fails
     * @example
     * const user = await userService.create({
     *     email: 'alice@example.com',
     *     name: 'Alice Smith'
     * });
     * console.log(user.id); // Auto-generated ID
     */
    async create(userData) {
        // Implementation
    }
}

/**
 * Calculate total price with tax.
 * 
 * @param {number[]} prices - Array of item prices
 * @param {number} taxRate - Tax rate (0.1 for 10%)
 * @returns {number} Total price including tax
 * @example
 * const total = calculateTotal([10, 20, 30], 0.1);
 * // Returns 66 (60 + 10% tax)
 */
function calculateTotal(prices, taxRate) {
    const subtotal = prices.reduce((sum, price) => sum + price, 0);
    return subtotal * (1 + taxRate);
}
```

#### README.md Structure

```markdown
# Project Name

Brief description

## Installation
```bash
npm install project-name
```

## Quick Start
```javascript
const { Client } = require('project-name');
const client = new Client({ apiKey: 'your_key' });
```

## API Reference
See [API Documentation](./docs/API.md)

## Examples
See [examples/](./examples/) directory
```

### Project Context Integration
- **If TypeScript**: Reference `.d.ts` type definitions
- **If API server**: Add OpenAPI/Swagger documentation
- **If React**: Add component documentation (Storybook)
- **If JSDoc config**: Reference existing JSDoc setup

---

## Installation Steps You Should Follow

1. **Analyze target JavaScript project**
   - Detect package manager (npm, yarn, pnpm)
   - Detect runtime (Node.js, browser, both)
   - Detect framework (React, Vue, Angular, Express)
   - Detect testing framework (Jest, Mocha, Cypress)
   - Detect TypeScript usage
   - Detect build tools (Webpack, Vite, Rollup)

2. **Read universal standards**
   - Read all relevant files from `universal/standards/`

3. **Generate JavaScript-specific standards**
   - Use templates above
   - Apply JavaScript idioms (async/await, promises)
   - Integrate project-specific patterns
   - Include code examples

4. **Create files**
   - `.agent-os/standards/development/javascript-concurrency.md`
   - `.agent-os/standards/development/javascript-testing.md`
   - `.agent-os/standards/development/javascript-dependencies.md`
   - `.agent-os/standards/development/javascript-code-quality.md`
   - `.agent-os/standards/development/javascript-documentation.md`

5. **Cross-reference universal standards**
   - Link back to `../../universal/standards/` files
   - Show relationship between universal and JavaScript-specific

6. **Include project context sections**
   - "Your Project Context" sections showing detected patterns
   - Examples from actual codebase (if available)

---

**Result:** JavaScript-specific standards that reference universal CS fundamentals while providing JavaScript-specific implementations (promises, async/await, event loop) tailored to the target project.
