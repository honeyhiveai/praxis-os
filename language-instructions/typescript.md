# TypeScript Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing Agent OS in a TypeScript project, use these instructions to generate language-specific standards by applying universal CS fundamentals to TypeScript-specific contexts.**

---

## Instructions Overview

You will generate 5 TypeScript-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Reading JavaScript standards (TypeScript extends JavaScript)
3. Analyzing the target TypeScript project
4. Applying TypeScript-specific context (type system, generics, etc.)
5. Integrating project-specific patterns (detected frameworks, tools)

## File 1: `typescript-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/deadlocks.md`
- `universal/standards/concurrency/locking-strategies.md`
- `.praxis-os/standards/development/javascript-concurrency.md` (if exists)

### TypeScript-Specific Context to Add

**Note:** TypeScript concurrency is identical to JavaScript (same runtime), but with type safety.

#### Typed Async Patterns

```typescript
// Typed promises
async function fetchUser(userId: string): Promise<User> {
    const response = await fetch(`/api/users/${userId}`);
    const data: User = await response.json();
    return data;
}

// Generic async function
async function fetchData<T>(url: string): Promise<T> {
    const response = await fetch(url);
    return response.json() as T;
}

const user = await fetchData<User>('/api/users/1');

// Typed Promise.all
async function fetchMultiple(
    userIds: string[]
): Promise<User[]> {
    const promises = userIds.map(id => fetchUser(id));
    return Promise.all(promises);  // Type: Promise<User[]>
}

// Event emitter with types
import { EventEmitter } from 'events';

interface UserEvents {
    created: (user: User) => void;
    updated: (user: User, changes: Partial<User>) => void;
    deleted: (userId: string) => void;
}

class TypedEventEmitter<T extends Record<string, (...args: any[]) => void>> {
    private emitter = new EventEmitter();
    
    on<K extends keyof T>(event: K, listener: T[K]): void {
        this.emitter.on(event as string, listener);
    }
    
    emit<K extends keyof T>(event: K, ...args: Parameters<T[K]>): void {
        this.emitter.emit(event as string, ...args);
    }
}

class UserService extends TypedEventEmitter<UserEvents> {
    createUser(userData: CreateUserDto): User {
        const user = this.save(userData);
        this.emit('created', user);  // Type-safe!
        return user;
    }
}
```

### Project Context Integration
- **If RxJS detected**: Add typed Observable patterns
- **If React**: Add typed hooks (useState<T>, useEffect)
- **If NestJS**: Add dependency injection with types
- **If GraphQL**: Add typed resolvers

---

## File 2: `typescript-testing.md`

### Source Materials
Read:
- `universal/standards/testing/test-pyramid.md`
- `universal/standards/testing/test-doubles.md`
- `.praxis-os/standards/development/javascript-testing.md` (if exists)

### TypeScript-Specific Context to Add

#### Type-Safe Testing

```typescript
// Jest with TypeScript
describe('UserService', () => {
    let userService: UserService;
    let mockDatabase: jest.Mocked<Database>;
    
    beforeEach(() => {
        mockDatabase = {
            query: jest.fn(),
            execute: jest.fn(),
        } as jest.Mocked<Database>;
        
        userService = new UserService(mockDatabase);
    });
    
    test('creates user with valid data', async () => {
        const userData: CreateUserDto = {
            email: 'test@example.com',
            name: 'Test User',
        };
        
        const expectedUser: User = {
            id: '1',
            ...userData,
            createdAt: new Date(),
        };
        
        mockDatabase.query.mockResolvedValue(expectedUser);
        
        const user = await userService.create(userData);
        
        expect(user).toEqual(expectedUser);
        expect(mockDatabase.query).toHaveBeenCalledWith(
            'INSERT INTO users (email, name) VALUES (?, ?)',
            ['test@example.com', 'Test User']
        );
    });
});

// Type-safe mocks with ts-jest
import { mocked } from 'ts-jest/utils';
import { fetchUser } from './api';

jest.mock('./api');
const mockedFetchUser = mocked(fetchUser);

test('handles API response', async () => {
    mockedFetchUser.mockResolvedValue({
        id: '1',
        name: 'Alice',
        email: 'alice@example.com',
    });
    
    const user = await processUser('1');
    expect(user.name).toBe('Alice');
});

// Testing generics
function testAsyncOperation<T>(
    operation: () => Promise<T>,
    expected: T
): Promise<void> {
    return expect(operation()).resolves.toEqual(expected);
}

test('fetches user data', () => {
    return testAsyncOperation<User>(
        () => fetchUser('1'),
        { id: '1', name: 'Alice', email: 'alice@example.com' }
    );
});
```

### Project Context Integration
- **If React Testing Library**: Add typed render, screen, userEvent
- **If Cypress**: Add typed cy commands
- **If Playwright**: Add typed page objects

---

## File 3: `typescript-dependencies.md`

### Source Materials
Read:
- `universal/standards/architecture/dependency-injection.md`
- `.praxis-os/standards/development/javascript-dependencies.md` (if exists)

### TypeScript-Specific Context

#### Type-Safe Dependency Injection

```typescript
// Interface-based DI
interface Database {
    query<T>(sql: string, params: any[]): Promise<T[]>;
    execute(sql: string, params: any[]): Promise<void>;
}

interface Logger {
    info(message: string, context?: Record<string, any>): void;
    error(message: string, error: Error): void;
}

class UserService {
    constructor(
        private readonly database: Database,
        private readonly logger: Logger
    ) {}
    
    async getUser(userId: string): Promise<User> {
        this.logger.info('Fetching user', { userId });
        const [user] = await this.database.query<User>(
            'SELECT * FROM users WHERE id = ?',
            [userId]
        );
        return user;
    }
}

// Dependency injection with InversifyJS
import { injectable, inject } from 'inversify';
import 'reflect-metadata';

const TYPES = {
    Database: Symbol.for('Database'),
    Logger: Symbol.for('Logger'),
    UserService: Symbol.for('UserService'),
};

@injectable()
class UserService {
    constructor(
        @inject(TYPES.Database) private database: Database,
        @inject(TYPES.Logger) private logger: Logger
    ) {}
}

// Factory pattern with types
type ServiceFactory<T> = (container: Container) => T;

const createUserService: ServiceFactory<UserService> = (container) => {
    return new UserService(
        container.get(TYPES.Database),
        container.get(TYPES.Logger)
    );
};
```

#### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

### Project Context Integration
- **If NestJS**: Add NestJS DI patterns with decorators
- **If TypeDI**: Add TypeDI patterns
- **If tsyringe**: Add tsyringe patterns

---

## File 4: `typescript-code-quality.md`

### TypeScript-Specific Tools

#### Type Checking (Core TypeScript)
- **tsc**: TypeScript compiler
  - Usage: `tsc --noEmit` (type check only)
  - Target: 0 errors (non-negotiable)

#### Strict Mode (MANDATORY)

```json
// tsconfig.json - Enable ALL strict checks
{
  "compilerOptions": {
    "strict": true,  // Enables all below
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    
    // Additional safety
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

#### Type Annotations (MANDATORY)

```typescript
// ✅ GOOD: Full type annotations
function processUser(
    user: User,
    config: ProcessConfig
): ProcessedUser {
    // Implementation
}

// ✅ GOOD: Interface for complex types
interface CreateUserDto {
    email: string;
    name: string;
    age?: number;  // Optional
}

interface User extends CreateUserDto {
    id: string;
    createdAt: Date;
    updatedAt: Date;
}

// ✅ GOOD: Generics for reusable code
function first<T>(array: T[]): T | undefined {
    return array[0];
}

// ✅ GOOD: Union types for multiple possibilities
type Result<T, E = Error> = 
    | { success: true; data: T }
    | { success: false; error: E };

async function fetchUser(id: string): Promise<Result<User>> {
    try {
        const user = await database.getUser(id);
        return { success: true, data: user };
    } catch (error) {
        return { success: false, error: error as Error };
    }
}

// ✅ GOOD: Utility types
type PartialUser = Partial<User>;  // All fields optional
type RequiredUser = Required<User>;  // All fields required
type ReadonlyUser = Readonly<User>;  // All fields readonly
type UserWithoutId = Omit<User, 'id'>;  // Exclude fields
type UserIdAndEmail = Pick<User, 'id' | 'email'>;  // Include only

// ❌ BAD: 'any' type (defeats TypeScript)
function processData(data: any): any {  // Don't do this!
    return data;
}

// ✅ GOOD: Use 'unknown' instead
function processData(data: unknown): ProcessedData {
    if (typeof data !== 'object' || data === null) {
        throw new TypeError('Expected object');
    }
    // Type guard narrows unknown → specific type
    return transform(data as RawData);
}
```

#### ESLint for TypeScript

```json
// .eslintrc.json
{
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking"
  ],
  "parserOptions": {
    "project": "./tsconfig.json"
  },
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

### Project Context Integration
- **If React**: Add React + TypeScript patterns (FC<Props>)
- **If Express**: Add typed route handlers
- **If NestJS**: Add decorator types, DTOs

---

## File 5: `typescript-documentation.md`

### TypeScript-Specific Documentation

#### TSDoc (TypeScript JSDoc)

```typescript
/**
 * User management service.
 * 
 * Handles user creation, authentication, and profile management.
 * All methods are async and return Promises.
 * 
 * @public
 * @example
 * ```typescript
 * const userService = new UserService(database, logger);
 * const user = await userService.create({
 *     email: 'alice@example.com',
 *     name: 'Alice Smith'
 * });
 * ```
 */
export class UserService {
    /**
     * Creates a new user.
     * 
     * @param userData - User data for creation
     * @returns Promise resolving to created user
     * @throws {@link ValidationError} If email is invalid
     * @throws {@link DuplicateError} If email already exists
     * 
     * @example
     * ```typescript
     * const user = await userService.create({
     *     email: 'alice@example.com',
     *     name: 'Alice Smith',
     *     age: 30
     * });
     * console.log(user.id); // Auto-generated
     * ```
     */
    async create(userData: CreateUserDto): Promise<User> {
        // Implementation
    }
}

/**
 * Configuration options for the API client.
 * 
 * @public
 */
export interface ClientConfig {
    /**
     * API key for authentication.
     * @remarks
     * Required for all API requests.
     */
    apiKey: string;
    
    /**
     * Request timeout in milliseconds.
     * @defaultValue 30000
     */
    timeout?: number;
    
    /**
     * Base URL for API requests.
     * @defaultValue 'https://api.example.com'
     */
    baseUrl?: string;
}
```

#### Type Declaration Files (.d.ts)

```typescript
// index.d.ts - Type declarations for library
declare module 'my-library' {
    export interface Config {
        apiKey: string;
        timeout?: number;
    }
    
    export class Client {
        constructor(config: Config);
        request<T>(endpoint: string): Promise<T>;
    }
    
    export function createClient(config: Config): Client;
}

// Augmenting external types
declare module 'express-serve-static-core' {
    interface Request {
        user?: User;  // Add custom property
    }
}
```

#### API Documentation with TypeDoc

```bash
# Generate documentation from types
npx typedoc --out docs src/index.ts
```

### Project Context Integration
- **If library**: Emphasize `.d.ts` and type exports
- **If API server**: Add OpenAPI schema generation from types
- **If TypeDoc**: Reference TypeDoc configuration

---

## Installation Steps You Should Follow

1. **Analyze target TypeScript project**
   - Detect `tsconfig.json` settings
   - Detect framework (React, NestJS, Express)
   - Detect testing framework (Jest, Vitest)
   - Detect DI framework (InversifyJS, TypeDI)
   - Check if `strict: true` enabled
   - Detect documentation tools (TypeDoc)

2. **Read universal standards**
   - Read all relevant files from `universal/standards/`
   - Read JavaScript standards (TypeScript extends JS)

3. **Generate TypeScript-specific standards**
   - Use templates above
   - Emphasize type safety, strict mode
   - Apply TypeScript idioms (generics, utility types)
   - Integrate project-specific patterns
   - Include code examples

4. **Create files**
   - `.praxis-os/standards/development/typescript-concurrency.md`
   - `.praxis-os/standards/development/typescript-testing.md`
   - `.praxis-os/standards/development/typescript-dependencies.md`
   - `.praxis-os/standards/development/typescript-code-quality.md`
   - `.praxis-os/standards/development/typescript-documentation.md`

5. **Cross-reference universal standards**
   - Link back to `../../universal/standards/` files
   - Link to JavaScript standards where applicable
   - Show relationship between universal, JS, and TS-specific

6. **Include project context sections**
   - "Your Project Context" sections showing detected patterns
   - Examples from actual codebase (if available)

---

**Result:** TypeScript-specific standards that reference universal CS fundamentals and JavaScript patterns while providing TypeScript-specific implementations (type safety, generics, strict mode) tailored to the target project.
