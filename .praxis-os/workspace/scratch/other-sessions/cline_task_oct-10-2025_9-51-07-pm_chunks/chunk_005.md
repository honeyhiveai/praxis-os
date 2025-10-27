* refactor(telemetry): remove unnecessary addProperties method and improve type safety
- Remove addProperties helper method that used 'any' types
- Replace with inline typed spread operations in capture(), captureRequired(), and identifyAccount()
- Fix type errors in captureConversationTurnEvent and captureBrowserError
- All telemetry properties now properly typed as TelemetryProperties
- Ensures OpenTelemetry compatibility through type system enforcement
* refactor: remove dotenv dependency and use launch.json envFile
- Remove dotenv import and config() call from esbuild.mjs
- Add envFile parameter to all launch.json configurations to load .env
- Remove dotenv from package.json devDependencies
Environment variables are now loaded via VSCode's envFile feature for local
development, while CI/production continues to inject via GitHub Actions.
This provides cleaner separation between build-time and runtime environment
handling.
* feat(telemetry): add browser telemetry properties and improve typing
- Add remoteBrowserHost and endpoint fields to browser telemetry events
- Replace generic Record<string, unknown> with TelemetryObject type in EventHandlerBase for better type safety
- Import TelemetryObject type from ITelemetryProvider
These changes enhance browser telemetry tracking capabilities and improve type consistency across the telemetry service.")

Oct 6, 2025

[.mocharc.json](/cline/cline/blob/main/.mocharc.json ".mocharc.json")

[.mocharc.json](/cline/cline/blob/main/.mocharc.json ".mocharc.json")

[Refactor posthog service providers and centralize distinct ID managem…](/cline/cline/commit/2c866c9265c737ee01ff144c193c772953e4a512 "Refactor posthog service providers and centralize distinct ID management (#5705)
* Refactor services architecture with provider pattern and factory classes
- Extract telemetry, error handling, and feature flags into separate service modules
- Implement provider pattern with factory classes for better abstraction
- Move PostHog-specific implementations to dedicated provider classes
- Add interfaces for telemetry, error, and feature flags providers
- Update imports across codebase to use new service structure
- Add unit tests for telemetry service
* Refactor service providers and centralize distinct ID management
- Move provider interfaces to dedicated providers/ subdirectories
- Extract distinct ID management to shared logging/distinctId module
- Simplify PostHogClientProvider by removing distinct ID parameter
- Update service factories to use centralized distinct ID
- Reorganize test files to __tests__/ directories
- Remove redundant distinct ID handling across services
* merge main
* clean up
* add grok coder free model to cline provider (#5808)
* add free grok-coder-free model to cline provider
* add changeset
* fix typo
* v3.26.6 Release Notes (#5788)
* changeset version bump
* Updating CHANGELOG.md format
* Update CHANGELOG.md for version 3.26.6 with user-friendly descriptions
---------
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: github-actions <github-actions@github.com>
Co-authored-by: pashpashpash <nik@cline.bot>
* Remove top padding from ActionButtons component (#5806)
Eliminate unnecessary top padding in the chat view.
* removing middle out from params to or / cline providers (#5811)
* Dify.ai integration (#5761)
* add focus chain settings to statemanager initialize function (#5798)
* add custom gpt-5 system prompt (#5757)
* gpt-5 system prompt
* add changeset
* Focus chain telemetry tweaks (#5810)
Co-authored-by: Kevin Bond <kevin@Kevins-MacBook-Pro.local>
* Remove eslint-rules test patterns from Mocha spec configuration (#5812)
Update the \"spec\" array in .mocharc.json to exclude \"eslint-rules/__tests__/**/*.test.ts\",
as that directory has been removed.
* Increase horizontal margin in AutoApproveBar component (#5813)
Update the mx-[5px] to mx-[15px] in the div's className to adjust horizontal spacing for improved layout alignment.
* fix: remove hardcoded Ollama host from options (#5816)
* fix: remove hardcoded Ollama host from options
Updates the Ollama handler to remove the hardcoded \"http://localhost:11434\" as the `ollamaBaseUrl` fallback option for the host to allow the Ollama SDK to handle the default endpoint configured on users' machine.
Reason: Ollama allows cross-origin requests from 127.0.0.1 and 0.0.0.0 by default. However, when we use localhost, the browser would resolve it through DNS, which can result in different IP addresses.
Docs: https://github.com/ollama/ollama/blob/main/docs/faq.md#how-can-i-expose-ollama-on-my-network
* add changeset
* deep-planning prompt PowerShell (#5699)
* Windows/Powershell specific deep planning prompt changes
* Prompt adjustments
---------
Co-authored-by: Kevin Bond <kevin@Kevins-MacBook-Pro.local>
* Changes to condenseToolResponse & summarizeTask prompting (#5817)
* Condense & deep planning prompt adjustments
* Removed ps prompting ready for PR
* rebase
* Fixed typo on one word
---------
Co-authored-by: Kevin Bond <kevin@Kevins-MacBook-Pro.local>
* rename CacheService to StateManager (#5681)
* rename CacheService to StateManager
* fix types
* infer state key types from existing interfaces (#5815)
* fix: AutoApproveModal positioning and scrolling behavior (#5819)
* fix: AutoApproveModal positioning and scrolling behavior
- Add dynamic positioning calculation to prevent modal overflow
- Implement proper flex layout with scrollable content container
- Ensure minimum usable height and top margin constraints
- Fix modal positioning when button is near viewport edges
* Add changeset
* clean up
* template-based system prompt (#5731)
* Refactor system prompt architecture with new template-based system
- Move existing system prompt files to legacy directory
- Implement new modular system with PromptBuilder, PromptRegistry, and TemplateEngine
- Add component-based prompt structure with reusable parts (capabilities, rules, tool_use, etc.)
- Create variant-specific templates for generic and next-gen models
- Add comprehensive test suite with snapshots for different model configurations
- Introduce template engine with placeholder support for dynamic prompt generation
* Refactor system prompt architecture with modular tool definitions
- Extract tool specifications into dedicated modules under tools/
- Add ClineToolSet class for managing tool variants by model family
- Restructure prompt components with centralized index exports
- Update prompt builder and registry to support new tool architecture
- Reorganize shared utilities and type definitions
- Update all test snapshots to reflect new prompt structure
* Update snapshots
* reorg
* Update template format
* clean up
* typos
* focus chain section
* fix task progress in attempt_completion
* Implement tool retrieval with fallback options in PromptBuilder
- Added `getToolByNameWithFallback` and `getToolsForVariantWithFallback` methods to `ClineToolSet` for improved tool resolution.
- Updated `getToolsPrompts` in `PromptBuilder` to utilize these new methods, allowing for better handling of tool requests with fallback to generic tools.
- Enhanced sorting and filtering of tools based on context requirements and requested order.
* update fild structure
* clean up
* fix static test string
* Update snapshot names
* Update unit test
* Remove unused placeholders and update docs
* Update README on how to add new tool
* Remove task_progress reference from attempt_completion tool description when focus chain is disabled
* Upgrade posthog-node to v5.8.0 and add exception filtering
- Update posthog-node from v4.8.1 to v5.8.0
- Add EventMessage import for type safety
- Implement posthogEventFilter to only capture exceptions from Cline extension
- Filter exceptions by checking for \"cline\" in error messages or \"saoudrizwan\" in stack frames
* Use env var keys
- Add PostHogClientConfig to ErrorProviderFactory with proper validation
- Update PostHogErrorProvider to use dedicated client instead of shared one
- Add API key validation in PostHogFeatureFlagsProvider before client creation
- Enhance error handling with fallback to NoOpErrorProvider instead of throwing
- Standardize configuration passing across telemetry, error, and feature flag services
* Upadte filter
* update filter
* update imports
* use secret
* disable enableExceptionAutocapture
* removes vscode.env.machineId
* initializeDistinctId
* use get trap as workaround
* on exit
---------
Co-authored-by: pashpashpash <nik@cline.bot>
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: github-actions <github-actions@github.com>
Co-authored-by: Toshii <94262432+0xToshii@users.noreply.github.com>
Co-authored-by: Yunus Emre AYHAN <ayhanyunusemre@gmail.com>
Co-authored-by: celestial-vault <58194240+celestial-vault@users.noreply.github.com>
Co-authored-by: canvrno <46584286+canvrno@users.noreply.github.com>
Co-authored-by: Kevin Bond <kevin@Kevins-MacBook-Pro.local>")

Aug 29, 2025

[.nvmrc](/cline/cline/blob/main/.nvmrc ".nvmrc")

[.nvmrc](/cline/cline/blob/main/.nvmrc ".nvmrc")

[Add .nvmrc, .prettierignore, icon; Remove vsc quickstart guide](/cline/cline/commit/fafdfe30a45e7819bdcb087aa23e768ac43bf090 "Add .nvmrc, .prettierignore, icon; Remove vsc quickstart guide")

Jul 20, 2024

[.nycrc.unit.json](/cline/cline/blob/main/.nycrc.unit.json ".nycrc.unit.json")

[.nycrc.unit.json](/cline/cline/blob/main/.nycrc.unit.json ".nycrc.unit.json")

[Setup QLTY Initial Coverage Metrics (](/cline/cline/commit/dfc660e73c1d6940681ca0b07a6a80b50eb3fc39 "Setup QLTY Initial Coverage Metrics (#6167)
Setup QLTY Initial Coverage Metrics")[#6167](https://github.com/cline/cline/pull/6167)[)](/cline/cline/commit/dfc660e73c1d6940681ca0b07a6a80b50eb3fc39 "Setup QLTY Initial Coverage Metrics (#6167)
Setup QLTY Initial Coverage Metrics")

Sep 16, 2025

[.vscode-test.mjs](/cline/cline/blob/main/.vscode-test.mjs ".vscode-test.mjs")

[.vscode-test.mjs](/cline/cline/blob/main/.vscode-test.mjs ".vscode-test.mjs")

[Set up E2E tests with Playwright (](/cline/cline/commit/b6f6358d4a04f89f397e6c319372dd2081ae7cb6 "Set up E2E tests with Playwright (#4721)
* Add Playwright E2E tests
Adding end-to-end (E2E) testing capabilities using Playwright. It also updates the `@vscode/test-electron` dependency.
The changes include:
- Adding Playwright as a dev dependency.
- Adding `e2e` and `e2e:build` scripts to `package.json` for running E2E tests.
- Adding `@playwright/test` to the list of dependencies.
- Updating `@vscode/test-electron` from `2.4.1` to `2.5.2`.
- Adding `test-results` to `.gitignore` to exclude test result files.
* wip: github workflow
Adding a new GitHub Actions workflow for running end-to-end (E2E) tests using Playwright. The workflow is triggered on push to the main branch, pull requests, and manual workflow dispatch.
The workflow defines a matrix strategy to run tests on different runners (Ubuntu and Windows) and shards. It also uploads Playwright recordings as artifacts if the tests fail.
* add @vscode/vsce as dev dep
* update workflow
* apply feedback
* fix test workflows
* add command palette helper
This commit improves the reliability and efficiency of the end-to-end tests by:
- Adding a delay to the \"Let's go!\" button click in the auth test to ensure the action is properly registered.
- Adding an expectation to ensure the \"Get Started for Free\" button is no longer visible after API key submission.
- Caching the \"Use your own API key\" button to avoid redundant lookups.
- Introducing a `runCommandPalette` helper function to streamline command execution within the VS Code environment.
- Disabling notifications before running the tests to prevent interference.
* state change
* set TEMP_PROFILE
* v3.18.7 Release Notes
* changeset version bump
* Updating CHANGELOG.md format
* Update CHANGELOG.md for version 3.18.7
---------
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: github-actions <github-actions@github.com>
Co-authored-by: pashpashpash <nik@cline.bot>
* Remove optimistic loading from organization dropdown (#4746)
* update build script to javascript
* fix match
* Add mode switching to chat test
* expected
---------
Co-authored-by: abeatrix <beatrix@cline.bot>
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: github-actions <github-actions@github.com>
Co-authored-by: pashpashpash <nik@cline.bot>
Co-authored-by: canvrno <46584286+canvrno@users.noreply.github.com>")[#4721](https://github.com/cline/cline/pull/4721)[)](/cline/cline/commit/b6f6358d4a04f89f397e6c319372dd2081ae7cb6 "Set up E2E tests with Playwright (#4721)
* Add Playwright E2E tests
Adding end-to-end (E2E) testing capabilities using Playwright. It also updates the `@vscode/test-electron` dependency.
The changes include:
- Adding Playwright as a dev dependency.
- Adding `e2e` and `e2e:build` scripts to `package.json` for running E2E tests.
- Adding `@playwright/test` to the list of dependencies.
- Updating `@vscode/test-electron` from `2.4.1` to `2.5.2`.
- Adding `test-results` to `.gitignore` to exclude test result files.
* wip: github workflow
Adding a new GitHub Actions workflow for running end-to-end (E2E) tests using Playwright. The workflow is triggered on push to the main branch, pull requests, and manual workflow dispatch.
The workflow defines a matrix strategy to run tests on different runners (Ubuntu and Windows) and shards. It also uploads Playwright recordings as artifacts if the tests fail.
* add @vscode/vsce as dev dep
* update workflow
* apply feedback
* fix test workflows
* add command palette helper
This commit improves the reliability and efficiency of the end-to-end tests by:
- Adding a delay to the \"Let's go!\" button click in the auth test to ensure the action is properly registered.
- Adding an expectation to ensure the \"Get Started for Free\" button is no longer visible after API key submission.
- Caching the \"Use your own API key\" button to avoid redundant lookups.
- Introducing a `runCommandPalette` helper function to streamline command execution within the VS Code environment.
- Disabling notifications before running the tests to prevent interference.
* state change
* set TEMP_PROFILE
* v3.18.7 Release Notes
* changeset version bump
* Updating CHANGELOG.md format
* Update CHANGELOG.md for version 3.18.7
---------
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: github-actions <github-actions@github.com>
Co-authored-by: pashpashpash <nik@cline.bot>
* Remove optimistic loading from organization dropdown (#4746)
* update build script to javascript
* fix match
* Add mode switching to chat test
* expected
---------
Co-authored-by: abeatrix <beatrix@cline.bot>
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: github-actions <github-actions@github.com>
Co-authored-by: pashpashpash <nik@cline.bot>
Co-authored-by: canvrno <46584286+canvrno@users.noreply.github.com>")

Jul 15, 2025

[.vscodeignore](/cline/cline/blob/main/.vscodeignore ".vscodeignore")

[.vscodeignore](/cline/cline/blob/main/.vscodeignore ".vscodeignore")

[feat: add Storybook configuration (](/cline/cline/commit/e8ba3c34fb980b119bdebd41b614f1c0eba9108d "feat: add Storybook configuration (#6256)
* feat: add Storybook configuration
- Bump package version from 3.28.3 to 3.28.4
- Add comprehensive Storybook setup with React-Vite framework and TypeScript support
- Configure Storybook with custom viewport settings and environment variables
- Add extensive story files for chat components, MCP displays, and browser automation
- Update gitignore files to exclude Storybook build artifacts and logs
* Add docs and changeset
* feat: refactor Storybook decorator to support state overrides and custom styling
- Extract ExtensionStateProviderWithOverrides component to safely use useExtensionState within provider context
- Add optional classNames parameter to createStorybookDecorator for custom styling
- Import cn utility from @heroui/react for className merging
- Fix margin class from m-x-auto to mx-auto
* Add message to mock history
---------
Co-authored-by: Jose R. Perez <trupix@gmail.com>")[#6256](https://github.com/cline/cline/pull/6256)[)](/cline/cline/commit/e8ba3c34fb980b119bdebd41b614f1c0eba9108d "feat: add Storybook configuration (#6256)
* feat: add Storybook configuration
- Bump package version from 3.28.3 to 3.28.4
- Add comprehensive Storybook setup with React-Vite framework and TypeScript support
- Configure Storybook with custom viewport settings and environment variables
- Add extensive story files for chat components, MCP displays, and browser automation
- Update gitignore files to exclude Storybook build artifacts and logs
* Add docs and changeset
* feat: refactor Storybook decorator to support state overrides and custom styling
- Extract ExtensionStateProviderWithOverrides component to safely use useExtensionState within provider context
- Add optional classNames parameter to createStorybookDecorator for custom styling
- Import cn utility from @heroui/react for className merging
- Fix margin class from m-x-auto to mx-auto
* Add message to mock history
---------
Co-authored-by: Jose R. Perez <trupix@gmail.com>")

Sep 16, 2025

[CHANGELOG.md](/cline/cline/blob/main/CHANGELOG.md "CHANGELOG.md")

[CHANGELOG.md](/cline/cline/blob/main/CHANGELOG.md "CHANGELOG.md")

[v3.32.7 Release Notes (](/cline/cline/commit/2292cafbb3827fda78a682520d079e0ab8032e35 "v3.32.7 Release Notes (#6616)
* Add JP and Global inference profile options to AWS BedrockAdd a comment on lines R5 to R7Add diff commentMarkdown input:  edit mode selected.WritePreviewAdd a suggestionHeadingBoldItalicQuoteCodeLinkUnordered listNumbered listTask listMentionReferenceSaved repliesAdd FilesPaste, drop, or click to add filesCancelCommentStart a reviewReturn to code
* Adding Improvements to VSCode multi root workspaces
* Added markdown support to focus chain text, allowing the model to display more interesting focus chains
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>")[#6616](https://github.com/cline/cline/pull/6616)[)](/cline/cline/commit/2292cafbb3827fda78a682520d079e0ab8032e35 "v3.32.7 Release Notes (#6616)
* Add JP and Global inference profile options to AWS BedrockAdd a comment on lines R5 to R7Add diff commentMarkdown input:  edit mode selected.WritePreviewAdd a suggestionHeadingBoldItalicQuoteCodeLinkUnordered listNumbered listTask listMentionReferenceSaved repliesAdd FilesPaste, drop, or click to add filesCancelCommentStart a reviewReturn to code
* Adding Improvements to VSCode multi root workspaces
* Added markdown support to focus chain text, allowing the model to display more interesting focus chains
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>")

Oct 8, 2025

[CODE\_OF\_CONDUCT.md](/cline/cline/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md")

[CODE\_OF\_CONDUCT.md](/cline/cline/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md")

[Fix formatting](/cline/cline/commit/860d315d7df8c7c10fe15ef300129a9d99e84c77 "Fix formatting")

Dec 21, 2024

[CONTRIBUTING.md](/cline/cline/blob/main/CONTRIBUTING.md "CONTRIBUTING.md")

[CONTRIBUTING.md](/cline/cline/blob/main/CONTRIBUTING.md "CONTRIBUTING.md")

[Reduce Test Workflow Time by 45% and Enable Qlty Coverage on Main (](/cline/cline/commit/d1fc59758e87e829b80cb604c6edc617bdd21ac0 "Reduce Test Workflow Time by 45% and Enable Qlty Coverage on Main (#6374)
* improving test workflow
* testing pipeline improvement
* testing new run
* adding missing protos
* adding previous cache + restoring dev dep version
* restoring webview package lock
* scripts update
* fixing old flaky test
* fixing old flaky test
* changeset update
* adding test-platform-integration again
* adding quality check for integration platform")[#6374](https://github.com/cline/cline/pull/6374)

Sep 29, 2025

[LICENSE](/cline/cline/blob/main/LICENSE "LICENSE")

[LICENSE](/cline/cline/blob/main/LICENSE "LICENSE")

[Update copyright year (](/cline/cline/commit/650854958421193955688b2a9f90a515a8bc5c33 "Update copyright year (#1637)
* Update copyright year
* Update LICENSE")[#1637](https://github.com/cline/cline/pull/1637)[)](/cline/cline/commit/650854958421193955688b2a9f90a515a8bc5c33 "Update copyright year (#1637)
* Update copyright year
* Update LICENSE")

Feb 4, 2025

[README.md](/cline/cline/blob/main/README.md "README.md")

[README.md](/cline/cline/blob/main/README.md "README.md")

[Update copy in README (](/cline/cline/commit/553b56336c8d0fb70f2f8a932029baffc8ff22e4 "Update copy in README (#5871)")[#5871](https://github.com/cline/cline/pull/5871)[)](/cline/cline/commit/553b56336c8d0fb70f2f8a932029baffc8ff22e4 "Update copy in README (#5871)")

Aug 28, 2025

[biome.jsonc](/cline/cline/blob/main/biome.jsonc "biome.jsonc")

[biome.jsonc](/cline/cline/blob/main/biome.jsonc "biome.jsonc")

[Adding initial integration spec files based on e2e playwright tests (](/cline/cline/commit/ddd03243f4116c44d352f60870f8e50c36566538 "Adding initial integration spec files based on e2e playwright tests (#6136)
Adding initial integration spec files based on e2e playwright tests")[#…](https://github.com/cline/cline/pull/6136)

Sep 12, 2025

[buf.yaml](/cline/cline/blob/main/buf.yaml "buf.yaml")

[buf.yaml](/cline/cline/blob/main/buf.yaml "buf.yaml")

[refactor(proto): Align proto directory structure with package names t…](/cline/cline/commit/a1bf1f95a30ca95581d9811488636aec42dd2f80 "refactor(proto): Align proto directory structure with package names to follow best practices (#5171)
* Reorganized proto directory structure to match package naming convention
Moved cline package protos from the proto directory to proto/cline/ directory
Host package protos remain in proto/host/ directory
Updated all import statements across codebase to reflect new proto paths
Removed proto linter exception for package/directory mismatch rule
Fix Vscode proto indexing errors by setting the proto path in the Vscode settings.
* Update imports to use new package
Update imports from @shared/proto/<thing> to @share/proto/cline/<thing>")

Jul 25, 2025

[esbuild.mjs](/cline/cline/blob/main/esbuild.mjs "esbuild.mjs")

[esbuild.mjs](/cline/cline/blob/main/esbuild.mjs "esbuild.mjs")

[refactor: Support Multiple Telemetry providers (](/cline/cline/commit/529bb3a26c0ff030204bd473e03917c075a2a4a4 "refactor: Support Multiple Telemetry providers (#6582)
* feat: Modular telemetry architecture with Jitsu provider support
- Add dual-provider telemetry architecture supporting both Jitsu and PostHog
- Implement JitsuTelemetryProvider with full API compatibility
- Add required telemetry bypass for critical system health events
- Create modular event handler base class for future extensibility
- Add Jitsu configuration with environment variable controls
- Update TelemetryService to support multiple providers with error isolation
- Add .env.example template for development setup
- Maintain backward compatibility with existing PostHog integration
- Enable easy PostHog removal via POSTHOG_TELEMETRY_ENABLED=false
- Install dotenv for local development environment support
Key benefits:
- Dual tracking during transition period
- Error isolation between providers
- Memory efficient static method architecture
- Easy provider enable/disable via environment variables
- Wednesday deployment ready for Jitsu migration
* fix(build): Load environment variables from .env file during development builds
- Add dotenv.config() to esbuild.mjs to load .env variables
- Include all telemetry-related environment variables in build injection:
- TELEMETRY_SERVICE_API_KEY (PostHog)
- ERROR_SERVICE_API_KEY (PostHog error tracking)
- JITSU_WRITE_KEY (Jitsu telemetry)
- JITSU_HOST (Jitsu host URL)
- JITSU_ENABLED (Jitsu provider control)
- POSTHOG_TELEMETRY_ENABLED (PostHog provider control)
This ensures telemetry services work correctly in development builds
by properly injecting API keys and configuration from .env file.
Also updates TelemetryService tests to support multi-provider architecture.
* fix(telemetry): Replace Record<string, unknown> with proper JSON-serializable types
- Add TelemetryPrimitive, TelemetryValue, TelemetryObject, and TelemetryProperties types to ITelemetryProvider
- Update JitsuTelemetryProvider to use TelemetryProperties instead of Record<string, unknown>
- Update PostHogTelemetryProvider to use TelemetryProperties instead of Record<string, unknown>
- Update TelemetryService to use TelemetryProperties for type-safe telemetry data
- Ensures all telemetry properties are JSON-serializable, preventing runtime errors
- Fixes TypeScript compatibility issue between Jitsu's JSONObject type and Record<string, unknown>
* moved and organized the telemetry files and updated the example env file to be more descriptive
* refactor: remove Jitsu telemetry provider
- Remove Jitsu provider implementation and config files
- Remove Jitsu environment variables from .env.example
- Remove Jitsu build configuration from esbuild.mjs
- Update TelemetryProviderFactory to only support PostHog
- Uninstall @jitsu/js dependency
- Add .env to .gitignore to prevent committing local env files
* chore: add changeset for Jitsu removal
* removed jitsu
* fix: update import paths after PostHogClientProvider relocation
* fix: remove race condition in captureToProviders and reorganize PostHog providers
- Changed captureToProviders from async to synchronous method
- Removed unnecessary Promise.allSettled overhead since provider.log() and provider.logRequired() are synchronous
- Changed from .map() to .forEach() for better clarity
- Moved PostHog provider files into posthog/ subdirectory for better organization
- Updated all import paths to reflect new folder structure
* refactor(telemetry): remove unnecessary addProperties method and improve type safety
- Remove addProperties helper method that used 'any' types
- Replace with inline typed spread operations in capture(), captureRequired(), and identifyAccount()
- Fix type errors in captureConversationTurnEvent and captureBrowserError
- All telemetry properties now properly typed as TelemetryProperties
- Ensures OpenTelemetry compatibility through type system enforcement
* refactor: remove dotenv dependency and use launch.json envFile
- Remove dotenv import and config() call from esbuild.mjs
- Add envFile parameter to all launch.json configurations to load .env
- Remove dotenv from package.json devDependencies
Environment variables are now loaded via VSCode's envFile feature for local
development, while CI/production continues to inject via GitHub Actions.
This provides cleaner separation between build-time and runtime environment
handling.
* feat(telemetry): add browser telemetry properties and improve typing
- Add remoteBrowserHost and endpoint fields to browser telemetry events
- Replace generic Record<string, unknown> with TelemetryObject type in EventHandlerBase for better type safety
- Import TelemetryObject type from ITelemetryProvider
These changes enhance browser telemetry tracking capabilities and improve type consistency across the telemetry service.")[#6582](https://github.com/cline/cline/pull/6582)[)](/cline/cline/commit/529bb3a26c0ff030204bd473e03917c075a2a4a4 "refactor: Support Multiple Telemetry providers (#6582)
* feat: Modular telemetry architecture with Jitsu provider support
- Add dual-provider telemetry architecture supporting both Jitsu and PostHog
- Implement JitsuTelemetryProvider with full API compatibility
- Add required telemetry bypass for critical system health events
- Create modular event handler base class for future extensibility
- Add Jitsu configuration with environment variable controls
- Update TelemetryService to support multiple providers with error isolation
- Add .env.example template for development setup
- Maintain backward compatibility with existing PostHog integration
- Enable easy PostHog removal via POSTHOG_TELEMETRY_ENABLED=false
- Install dotenv for local development environment support
Key benefits:
- Dual tracking during transition period
- Error isolation between providers
- Memory efficient static method architecture
- Easy provider enable/disable via environment variables
- Wednesday deployment ready for Jitsu migration
* fix(build): Load environment variables from .env file during development builds
- Add dotenv.config() to esbuild.mjs to load .env variables
- Include all telemetry-related environment variables in build injection:
- TELEMETRY_SERVICE_API_KEY (PostHog)
- ERROR_SERVICE_API_KEY (PostHog error tracking)
- JITSU_WRITE_KEY (Jitsu telemetry)
- JITSU_HOST (Jitsu host URL)
- JITSU_ENABLED (Jitsu provider control)
- POSTHOG_TELEMETRY_ENABLED (PostHog provider control)
This ensures telemetry services work correctly in development builds
by properly injecting API keys and configuration from .env file.
Also updates TelemetryService tests to support multi-provider architecture.
* fix(telemetry): Replace Record<string, unknown> with proper JSON-serializable types
- Add TelemetryPrimitive, TelemetryValue, TelemetryObject, and TelemetryProperties types to ITelemetryProvider
- Update JitsuTelemetryProvider to use TelemetryProperties instead of Record<string, unknown>
- Update PostHogTelemetryProvider to use TelemetryProperties instead of Record<string, unknown>
- Update TelemetryService to use TelemetryProperties for type-safe telemetry data
- Ensures all telemetry properties are JSON-serializable, preventing runtime errors
- Fixes TypeScript compatibility issue between Jitsu's JSONObject type and Record<string, unknown>
* moved and organized the telemetry files and updated the example env file to be more descriptive
* refactor: remove Jitsu telemetry provider
- Remove Jitsu provider implementation and config files
- Remove Jitsu environment variables from .env.example
- Remove Jitsu build configuration from esbuild.mjs
- Update TelemetryProviderFactory to only support PostHog
- Uninstall @jitsu/js dependency
- Add .env to .gitignore to prevent committing local env files
* chore: add changeset for Jitsu removal
* removed jitsu
* fix: update import paths after PostHogClientProvider relocation
* fix: remove race condition in captureToProviders and reorganize PostHog providers
- Changed captureToProviders from async to synchronous method
- Removed unnecessary Promise.allSettled overhead since provider.log() and provider.logRequired() are synchronous
- Changed from .map() to .forEach() for better clarity
- Moved PostHog provider files into posthog/ subdirectory for better organization
- Updated all import paths to reflect new folder structure
* refactor(telemetry): remove unnecessary addProperties method and improve type safety
- Remove addProperties helper method that used 'any' types
- Replace with inline typed spread operations in capture(), captureRequired(), and identifyAccount()
- Fix type errors in captureConversationTurnEvent and captureBrowserError
- All telemetry properties now properly typed as TelemetryProperties
- Ensures OpenTelemetry compatibility through type system enforcement
* refactor: remove dotenv dependency and use launch.json envFile
- Remove dotenv import and config() call from esbuild.mjs
- Add envFile parameter to all launch.json configurations to load .env
- Remove dotenv from package.json devDependencies
Environment variables are now loaded via VSCode's envFile feature for local
development, while CI/production continues to inject via GitHub Actions.
This provides cleaner separation between build-time and runtime environment
handling.
* feat(telemetry): add browser telemetry properties and improve typing
- Add remoteBrowserHost and endpoint fields to browser telemetry events
- Replace generic Record<string, unknown> with TelemetryObject type in EventHandlerBase for better type safety
- Import TelemetryObject type from ITelemetryProvider
These changes enhance browser telemetry tracking capabilities and improve type consistency across the telemetry service.")

Oct 6, 2025

[go.work](/cline/cline/blob/main/go.work "go.work")

[go.work](/cline/cline/blob/main/go.work "go.work")

[cline cli super alpha (](/cline/cline/commit/097f8e62394d4b82f188d68aa0276b19d955e467 "cline cli super alpha (#6644)
* super sketchy big merge with main
* gitignore
* gitignore
* Delete cli/bin/air
* Delete cli/bin directory
* Delete cli/cline-host
* Fix missing package.json in cli
Copy the package JSON into the dist-standalone dir during compilation.
Remove workaround for missing package.json
* Update scripts/build-cli.sh
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Remove reference to watchservice, it has been removed
* Update scripts/build-go-proto.mjs
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>
* Fix timestamp to string conversion
* diff.go ellipsis fix
* COMMON_TYPES
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>")[#6644](https://github.com/cline/cline/pull/6644)[)](/cline/cline/commit/097f8e62394d4b82f188d68aa0276b19d955e467 "cline cli super alpha (#6644)
* super sketchy big merge with main
* gitignore
* gitignore
* Delete cli/bin/air
* Delete cli/bin directory
* Delete cli/cline-host
* Fix missing package.json in cli
Copy the package JSON into the dist-standalone dir during compilation.
Remove workaround for missing package.json
* Update scripts/build-cli.sh
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Remove reference to watchservice, it has been removed
* Update scripts/build-go-proto.mjs
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>
* Fix timestamp to string conversion
* diff.go ellipsis fix
* COMMON_TYPES
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>")

Oct 3, 2025

[go.work.sum](/cline/cline/blob/main/go.work.sum "go.work.sum")

[go.work.sum](/cline/cline/blob/main/go.work.sum "go.work.sum")

[CLI Auth Wizard 🧙 (](/cline/cline/commit/a670c1efa2a84bea70e9c74ffdedcde94f12675d "CLI Auth Wizard 🧙 (#6742)
* CLI auth wizard
Default Cline model, better menu UX, display active provider and model at main menu
Model switcher for BYO providers
Provider switching, UI changes
List configured providers now shows all providers user has configured
Added remove provider feature
Changes to model picker for BYO providers
Model fetch filtering tweaks
Only update model fields for provider when possible
Consolidated provider field mapping
Change to not set provider as active when updating model
Dont set Cline as active provider when setting Cline model
Added model fetching for OpenAI provider (req API key)
Added model fetching for Ollama provider
Added support for model listing from providers.go for models without remote fetch
Moved auth specific code out of manager
Bedrock fields, OpenAI Native BaseURL
More graceful fetch failure
Fixed auth callback issue
* Added model list feature for AWS
AWS - Profile only support in CLI for now, UX changes (WIP
Remove Save and Exit option
Auto enable filtering/search in model lists
Added cancel option for some menus")[#6742](https://github.com/cline/cline/pull/6742)[)](/cline/cline/commit/a670c1efa2a84bea70e9c74ffdedcde94f12675d "CLI Auth Wizard 🧙 (#6742)
* CLI auth wizard
Default Cline model, better menu UX, display active provider and model at main menu
Model switcher for BYO providers
Provider switching, UI changes
List configured providers now shows all providers user has configured
Added remove provider feature
Changes to model picker for BYO providers
Model fetch filtering tweaks
Only update model fields for provider when possible
Consolidated provider field mapping
Change to not set provider as active when updating model
Dont set Cline as active provider when setting Cline model
Added model fetching for OpenAI provider (req API key)
Added model fetching for Ollama provider
Added support for model listing from providers.go for models without remote fetch
Moved auth specific code out of manager
Bedrock fields, OpenAI Native BaseURL
More graceful fetch failure
Fixed auth callback issue
* Added model list feature for AWS
AWS - Profile only support in CLI for now, UX changes (WIP
Remove Save and Exit option
Auto enable filtering/search in model lists
Added cancel option for some menus")

Oct 10, 2025

[knip.json](/cline/cline/blob/main/knip.json "knip.json")

[knip.json](/cline/cline/blob/main/knip.json "knip.json")

[refactor to hostbridge: route @mentions search via WorkspaceService.s…](/cline/cline/commit/1997ee3e806516cd14dc17b5c10f381b979ded1f "refactor to hostbridge: route @mentions search via WorkspaceService.searchWorkspaceItems (#5655)")

Aug 20, 2025

[package-lock.json](/cline/cline/blob/main/package-lock.json "package-lock.json")

[package-lock.json](/cline/cline/blob/main/package-lock.json "package-lock.json")

[v3.32.7 Release Notes (](/cline/cline/commit/2292cafbb3827fda78a682520d079e0ab8032e35 "v3.32.7 Release Notes (#6616)
* Add JP and Global inference profile options to AWS BedrockAdd a comment on lines R5 to R7Add diff commentMarkdown input:  edit mode selected.WritePreviewAdd a suggestionHeadingBoldItalicQuoteCodeLinkUnordered listNumbered listTask listMentionReferenceSaved repliesAdd FilesPaste, drop, or click to add filesCancelCommentStart a reviewReturn to code
* Adding Improvements to VSCode multi root workspaces
* Added markdown support to focus chain text, allowing the model to display more interesting focus chains
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>")[#6616](https://github.com/cline/cline/pull/6616)[)](/cline/cline/commit/2292cafbb3827fda78a682520d079e0ab8032e35 "v3.32.7 Release Notes (#6616)
* Add JP and Global inference profile options to AWS BedrockAdd a comment on lines R5 to R7Add diff commentMarkdown input:  edit mode selected.WritePreviewAdd a suggestionHeadingBoldItalicQuoteCodeLinkUnordered listNumbered listTask listMentionReferenceSaved repliesAdd FilesPaste, drop, or click to add filesCancelCommentStart a reviewReturn to code
* Adding Improvements to VSCode multi root workspaces
* Added markdown support to focus chain text, allowing the model to display more interesting focus chains
Co-authored-by: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>")

Oct 8, 2025

[package.json](/cline/cline/blob/main/package.json "package.json")

[package.json](/cline/cline/blob/main/package.json "package.json")

[Standalone CLI Installation (](/cline/cline/commit/3472e6068c8f9f1a2b2172659608b972cffe7518 "Standalone CLI Installation  (#6689)
* Phase 1 download node binary
* Phase 2 include cli binaries
* Phase 3 add scripts
* Phase 4 bug fix
* Phase 5: adding install script
* Phase 6: pushing github actions
* Phase 7: fixing redundancy
* Phase 7: fixing redundancy
* Temporary commit for workspace stuff
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Adding JB fixes
* Adding JB fixes
* Adding CLI-JB fixes
* Refactor
* Refactor
* refactor
* Update release-standalone.yml
Remove VSCode packaging env vars from CLI workflow.
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>")[#6689](https://github.com/cline/cline/pull/6689)[)](/cline/cline/commit/3472e6068c8f9f1a2b2172659608b972cffe7518 "Standalone CLI Installation  (#6689)
* Phase 1 download node binary
* Phase 2 include cli binaries
* Phase 3 add scripts
* Phase 4 bug fix
* Phase 5: adding install script
* Phase 6: pushing github actions
* Phase 7: fixing redundancy
* Phase 7: fixing redundancy
* Temporary commit for workspace stuff
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Adding JB fixes
* Adding JB fixes
* Adding CLI-JB fixes
* Refactor
* Refactor
* refactor
* Update release-standalone.yml
Remove VSCode packaging env vars from CLI workflow.
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>")

Oct 10, 2025

[playwright.config.ts](/cline/cline/blob/main/playwright.config.ts "playwright.config.ts")

[playwright.config.ts](/cline/cline/blob/main/playwright.config.ts "playwright.config.ts")

[Configure Playwright to retain videos on failure and simplify teardown (](/cline/cline/commit/0fd1c0a3aae8089fcf84d6a20e5d94b1ab6e2b61 "Configure Playwright to retain videos on failure and simplify teardown (#5542)
* Close page to stop e2e test on teardown
* Configure Playwright to retain videos on failure and simplify teardown
- Enable video recording that only saves on test failures
- Remove complex cleanup logic from global teardown
- Streamline server shutdown to not block teardown process
* change build.js to build.mjs which fixes ES module load error
* speed up
---------
Co-authored-by: Brian Pierce <brian@cline.bot>")

Aug 13, 2025

[test-setup.js](/cline/cline/blob/main/test-setup.js "test-setup.js")

[test-setup.js](/cline/cline/blob/main/test-setup.js "test-setup.js")

[move api folder to core (](/cline/cline/commit/803574e7f35ef8b9185fc526d8ff77dfac03c73d "move api folder to core (#5539)
* move api folder to core
* fix incorrect import path mock in test setup
* fix import in zai.ts
* fix additional import errors")[#5539](https://github.com/cline/cline/pull/5539)[)](/cline/cline/commit/803574e7f35ef8b9185fc526d8ff77dfac03c73d "move api folder to core (#5539)
* move api folder to core
* fix incorrect import path mock in test setup
* fix import in zai.ts
* fix additional import errors")

Aug 19, 2025

[tsconfig.json](/cline/cline/blob/main/tsconfig.json "tsconfig.json")

[tsconfig.json](/cline/cline/blob/main/tsconfig.json "tsconfig.json")

[Setup Raw Structure for implementing multi-workspace support with Wor…](/cline/cline/commit/e3bc5f01439d0a0fe3283e9fcc1e9ec9aef8e0d8 "Setup Raw Structure for implementing multi-workspace support with WorkspaceRoot (#5849)
* Setup Raw Structure for implementing multi-workspace support with WorkspaceRoot
* Remove Shortcut of Cline from its title")

Sep 2, 2025

[tsconfig.test.json](/cline/cline/blob/main/tsconfig.test.json "tsconfig.test.json")

[tsconfig.test.json](/cline/cline/blob/main/tsconfig.test.json "tsconfig.test.json")

[Apply biome rules: noUnusedVariables, noUnusedFunctionParameters, noU…](/cline/cline/commit/06e0973c041a03b56b4d575335ea566f1dfbe4c6 "Apply biome rules: noUnusedVariables, noUnusedFunctionParameters, noUnusedImports (#5545)
* Enable biome rules: noUnusedVariables, noUnusedFunctionParameters, noUnusedImports
* Apply new rules with format
* remove unused currentReplaceContent
* update nextTerminalId
* fix all format issues
* update biome config
* add back applyContextOptimizations and killAllChromeBrowsers")

Aug 19, 2025

[tsconfig.unit-test.json](/cline/cline/blob/main/tsconfig.unit-test.json "tsconfig.unit-test.json")

[tsconfig.unit-test.json](/cline/cline/blob/main/tsconfig.unit-test.json "tsconfig.unit-test.json")

[template-based system prompt (](/cline/cline/commit/0ba45084a07108aec16c8c7fe64cd24ca8c5df62 "template-based system prompt (#5731)
* Refactor system prompt architecture with new template-based system
- Move existing system prompt files to legacy directory
- Implement new modular system with PromptBuilder, PromptRegistry, and TemplateEngine
- Add component-based prompt structure with reusable parts (capabilities, rules, tool_use, etc.)
- Create variant-specific templates for generic and next-gen models
- Add comprehensive test suite with snapshots for different model configurations
- Introduce template engine with placeholder support for dynamic prompt generation
* Refactor system prompt architecture with modular tool definitions
- Extract tool specifications into dedicated modules under tools/
- Add ClineToolSet class for managing tool variants by model family
- Restructure prompt components with centralized index exports
- Update prompt builder and registry to support new tool architecture
- Reorganize shared utilities and type definitions
- Update all test snapshots to reflect new prompt structure
* Update snapshots
* reorg
* Update template format
* clean up
* typos
* focus chain section
* fix task progress in attempt_completion
* Implement tool retrieval with fallback options in PromptBuilder
- Added `getToolByNameWithFallback` and `getToolsForVariantWithFallback` methods to `ClineToolSet` for improved tool resolution.
- Updated `getToolsPrompts` in `PromptBuilder` to utilize these new methods, allowing for better handling of tool requests with fallback to generic tools.
- Enhanced sorting and filtering of tools based on context requirements and requested order.
* update fild structure
* clean up
* fix static test string
* Update snapshot names
* Update unit test
* Remove unused placeholders and update docs
* Update README on how to add new tool
* Remove task_progress reference from attempt_completion tool description when focus chain is disabled")[#5731](https://github.com/cline/cline/pull/5731)[)](/cline/cline/commit/0ba45084a07108aec16c8c7fe64cd24ca8c5df62 "template-based system prompt (#5731)
* Refactor system prompt architecture with new template-based system
- Move existing system prompt files to legacy directory
- Implement new modular system with PromptBuilder, PromptRegistry, and TemplateEngine
- Add component-based prompt structure with reusable parts (capabilities, rules, tool_use, etc.)
- Create variant-specific templates for generic and next-gen models
- Add comprehensive test suite with snapshots for different model configurations
- Introduce template engine with placeholder support for dynamic prompt generation
* Refactor system prompt architecture with modular tool definitions
- Extract tool specifications into dedicated modules under tools/
- Add ClineToolSet class for managing tool variants by model family
- Restructure prompt components with centralized index exports
- Update prompt builder and registry to support new tool architecture
- Reorganize shared utilities and type definitions
- Update all test snapshots to reflect new prompt structure
* Update snapshots
* reorg
* Update template format
* clean up
* typos
* focus chain section
* fix task progress in attempt_completion
* Implement tool retrieval with fallback options in PromptBuilder
- Added `getToolByNameWithFallback` and `getToolsForVariantWithFallback` methods to `ClineToolSet` for improved tool resolution.
- Updated `getToolsPrompts` in `PromptBuilder` to utilize these new methods, allowing for better handling of tool requests with fallback to generic tools.
- Enhanced sorting and filtering of tools based on context requirements and requested order.
* update fild structure
* clean up
* fix static test string
* Update snapshot names
* Update unit test
* Remove unused placeholders and update docs
* Update README on how to add new tool
* Remove task_progress reference from attempt_completion tool description when focus chain is disabled")

Aug 26, 2025

View all files

Repository files navigation
---------------------------

English | [Español](https://github.com/cline/cline/blob/main/locales/es/README.md) | [Deutsch](https://github.com/cline/cline/blob/main/locales/de/README.md) | [日本語](https://github.com/cline/cline/blob/main/locales/ja/README.md) | [简体中文](https://github.com/cline/cline/blob/main/locales/zh-cn/README.md) | [繁體中文](https://github.com/cline/cline/blob/main/locales/zh-tw/README.md) | [한국어](https://github.com/cline/cline/blob/main/locales/ko/README.md)

Cline – #1 on OpenRouter
========================

[](#cline--1-on-openrouter)

 [![](https://media.githubusercontent.com/media/cline/cline/main/assets/docs/demo.gif)](https://media.githubusercontent.com/media/cline/cline/main/assets/docs/demo.gif) [![demo.gif](https://media.githubusercontent.com/media/cline/cline/main/assets/docs/demo.gif)

](https://media.githubusercontent.com/media/cline/cline/main/assets/docs/demo.gif)[](https://media.githubusercontent.com/media/cline/cline/main/assets/docs/demo.gif)

[**Download on VS Marketplace**](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)

[**Discord**](https://discord.gg/cline)

[**r/cline**](https://www.reddit.com/r/cline/)

[**Feature Requests**](https://github.com/cline/cline/discussions/categories/feature-requests?discussions_q=is%3Aopen+category%3A%22Feature+Requests%22+sort%3Atop)

[**Getting Started**](https://docs.cline.bot/getting-started/for-new-coders)

Meet Cline, an AI assistant that can use your **CLI** a**N**d **E**ditor.

Thanks to [Claude Sonnet's agentic coding capabilities](https://www.anthropic.com/claude/sonnet), Cline can handle complex software development tasks step-by-step. With tools that let him create & edit files, explore large projects, use the browser, and execute terminal commands (after you grant permission), he can assist you in ways that go beyond code completion or tech support. Cline can even use the Model Context Protocol (MCP) to create new tools and extend his own capabilities. While autonomous AI scripts traditionally run in sandboxed environments, this extension provides a human-in-the-loop GUI to approve every file change and terminal command, providing a safe and accessible way to explore the potential of agentic AI.

1.  Enter your task and add images to convert mockups into functional apps or fix bugs with screenshots.
2.  Cline starts by analyzing your file structure & source code ASTs, running regex searches, and reading relevant files to get up to speed in existing projects. By carefully managing what information is added to context, Cline can provide valuable assistance even for large, complex projects without overwhelming the context window.
3.  Once Cline has the information he needs, he can:
    *   Create and edit files + monitor linter/compiler errors along the way, letting him proactively fix issues like missing imports and syntax errors on his own.
    *   Execute commands directly in your terminal and monitor their output as he works, letting him e.g., react to dev server issues after editing a file.
    *   For web development tasks, Cline can launch the site in a headless browser, click, type, scroll, and capture screenshots + console logs, allowing him to fix runtime errors and visual bugs.
4.  When a task is completed, Cline will present the result to you with a terminal command like `open -a "Google Chrome" index.html`, which you run with a click of a button.

Tip

Use the `CMD/CTRL + Shift + P` shortcut to open the command palette and type "Cline: Open In New Tab" to open the extension as a tab in your editor. This lets you use Cline side-by-side with your file explorer, and see how he changes your workspace more clearly.

* * *

[![](https://private-user-images.githubusercontent.com/7799382/374832520-3cf21e04-7ce9-4d22-a7b9-ba2c595e88a4.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMjUyMC0zY2YyMWUwNC03Y2U5LTRkMjItYTdiOS1iYTJjNTk1ZTg4YTQucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ODllMmI1OTM2YWYwMzFiMmZlZTkyZGQ0NmJmMzdlNTFjOTFkMWFjMzAwOWFiNDkyMzlmYjZlM2Y4N2FlZDNlYSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.VXMgAOtSTtEGDZuXdbQvW1fzSLFasSKxAH9e0HTwTMI)](https://private-user-images.githubusercontent.com/7799382/374832520-3cf21e04-7ce9-4d22-a7b9-ba2c595e88a4.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMjUyMC0zY2YyMWUwNC03Y2U5LTRkMjItYTdiOS1iYTJjNTk1ZTg4YTQucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ODllMmI1OTM2YWYwMzFiMmZlZTkyZGQ0NmJmMzdlNTFjOTFkMWFjMzAwOWFiNDkyMzlmYjZlM2Y4N2FlZDNlYSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.VXMgAOtSTtEGDZuXdbQvW1fzSLFasSKxAH9e0HTwTMI)

### Use any API and Model

[](#use-any-api-and-model)

Cline supports API providers like OpenRouter, Anthropic, OpenAI, Google Gemini, AWS Bedrock, Azure, GCP Vertex, Cerebras and Groq. You can also configure any OpenAI compatible API, or use a local model through LM Studio/Ollama. If you're using OpenRouter, the extension fetches their latest model list, allowing you to use the newest models as soon as they're available.

The extension also keeps track of total tokens and API usage cost for the entire task loop and individual requests, keeping you informed of spend every step of the way.

[![](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)  

[![](https://private-user-images.githubusercontent.com/7799382/374832624-81be79a8-1fdb-4028-9129-5fe055e01e76.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMjYyNC04MWJlNzlhOC0xZmRiLTQwMjgtOTEyOS01ZmUwNTVlMDFlNzYucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NjhmMjE0MWEzYWRlMzZjNWMyYTQ4Zjc5NmVmYmUwMWQ3OWRkZTZhZDVkMzM1NWM1Yjg5M2JiNzU4ODQ5N2Q3ZCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.fSbRABc_k_jGYyukTQrCdIMy5DR1IVf8QjLWLAxtPqQ)](https://private-user-images.githubusercontent.com/7799382/374832624-81be79a8-1fdb-4028-9129-5fe055e01e76.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMjYyNC04MWJlNzlhOC0xZmRiLTQwMjgtOTEyOS01ZmUwNTVlMDFlNzYucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NjhmMjE0MWEzYWRlMzZjNWMyYTQ4Zjc5NmVmYmUwMWQ3OWRkZTZhZDVkMzM1NWM1Yjg5M2JiNzU4ODQ5N2Q3ZCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.fSbRABc_k_jGYyukTQrCdIMy5DR1IVf8QjLWLAxtPqQ)

### Run Commands in Terminal

[](#run-commands-in-terminal)

Thanks to the new [shell integration updates in VSCode v1.93](https://code.visualstudio.com/updates/v1_93#_terminal-shell-integration-api), Cline can execute commands directly in your terminal and receive the output. This allows him to perform a wide range of tasks, from installing packages and running build scripts to deploying applications, managing databases, and executing tests, all while adapting to your dev environment & toolchain to get the job done right.

For long running processes like dev servers, use the "Proceed While Running" button to let Cline continue in the task while the command runs in the background. As Cline works he’ll be notified of any new terminal output along the way, letting him react to issues that may come up, such as compile-time errors when editing files.

[![](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)  

[![](https://private-user-images.githubusercontent.com/7799382/374832939-c5977833-d9b8-491e-90f9-05f9cd38c588.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMjkzOS1jNTk3NzgzMy1kOWI4LTQ5MWUtOTBmOS0wNWY5Y2QzOGM1ODgucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZWNkY2IzMTM5MGUyZmYxMzg2MjY3ZTIyNTJjMWQ0YTI4OWEwMWYzZTY4YWE3ZmY5NDNjY2JhM2YxMDZhMWNkYSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.1Y4u-RiqOy06vj6N00Sz0T7D9O3gw1CGw3gR-68cCYk)](https://private-user-images.githubusercontent.com/7799382/374832939-c5977833-d9b8-491e-90f9-05f9cd38c588.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMjkzOS1jNTk3NzgzMy1kOWI4LTQ5MWUtOTBmOS0wNWY5Y2QzOGM1ODgucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZWNkY2IzMTM5MGUyZmYxMzg2MjY3ZTIyNTJjMWQ0YTI4OWEwMWYzZTY4YWE3ZmY5NDNjY2JhM2YxMDZhMWNkYSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.1Y4u-RiqOy06vj6N00Sz0T7D9O3gw1CGw3gR-68cCYk)

### Create and Edit Files

[](#create-and-edit-files)

Cline can create and edit files directly in your editor, presenting you a diff view of the changes. You can edit or revert Cline's changes directly in the diff view editor, or provide feedback in chat until you're satisfied with the result. Cline also monitors linter/compiler errors (missing imports, syntax errors, etc.) so he can fix issues that come up along the way on his own.

All changes made by Cline are recorded in your file's Timeline, providing an easy way to track and revert modifications if needed.

[![](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)  

[![](https://private-user-images.githubusercontent.com/7799382/382169997-bc2e85ba-dfeb-4fe6-9942-7cfc4703cbe5.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM4MjE2OTk5Ny1iYzJlODViYS1kZmViLTRmZTYtOTk0Mi03Y2ZjNDcwM2NiZTUucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NzUzMDg0Y2E4MjEzNGUwYjYyMTk3NWZiYzdkM2M2M2I3OTY5NTI5OTlkNTUxMTRiOTAxODNkNGY3ZTA2MjRkNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.YTKKsGj-qkQKUm4YR80PvPSKmd2Xr93X-VkiqNrPnlw)](https://private-user-images.githubusercontent.com/7799382/382169997-bc2e85ba-dfeb-4fe6-9942-7cfc4703cbe5.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM4MjE2OTk5Ny1iYzJlODViYS1kZmViLTRmZTYtOTk0Mi03Y2ZjNDcwM2NiZTUucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NzUzMDg0Y2E4MjEzNGUwYjYyMTk3NWZiYzdkM2M2M2I3OTY5NTI5OTlkNTUxMTRiOTAxODNkNGY3ZTA2MjRkNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.YTKKsGj-qkQKUm4YR80PvPSKmd2Xr93X-VkiqNrPnlw)

### Use the Browser

[](#use-the-browser)

With Claude Sonnet's new [Computer Use](https://www.anthropic.com/news/3-5-models-and-computer-use) capability, Cline can launch a browser, click elements, type text, and scroll, capturing screenshots and console logs at each step. This allows for interactive debugging, end-to-end testing, and even general web use! This gives him autonomy to fixing visual bugs and runtime issues without you needing to handhold and copy-pasting error logs yourself.

Try asking Cline to "test the app", and watch as he runs a command like `npm run dev`, launches your locally running dev server in a browser, and performs a series of tests to confirm that everything works. [See a demo here.](https://x.com/sdrzn/status/1850880547825823989)

[![](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)  

[![](https://private-user-images.githubusercontent.com/7799382/395310099-ac0efa14-5c1f-4c26-a42d-9d7c56f5fadd.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM5NTMxMDA5OS1hYzBlZmExNC01YzFmLTRjMjYtYTQyZC05ZDdjNTZmNWZhZGQucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NjE3YzE3MDQxNTY2YmIxNDdhNmNjZTJiYzc4YTJlOTYxZTU5NTQ3ZmFjMTU3MDE5ZGQ3YTEzZTdhMWI3ODE2ZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.oQHpPI01P6jkFLGx1tH6l9mUA8eanmIpv02CYqHJmJA)](https://private-user-images.githubusercontent.com/7799382/395310099-ac0efa14-5c1f-4c26-a42d-9d7c56f5fadd.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM5NTMxMDA5OS1hYzBlZmExNC01YzFmLTRjMjYtYTQyZC05ZDdjNTZmNWZhZGQucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NjE3YzE3MDQxNTY2YmIxNDdhNmNjZTJiYzc4YTJlOTYxZTU5NTQ3ZmFjMTU3MDE5ZGQ3YTEzZTdhMWI3ODE2ZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.oQHpPI01P6jkFLGx1tH6l9mUA8eanmIpv02CYqHJmJA)

### "add a tool that..."

[](#add-a-tool-that)

Thanks to the [Model Context Protocol](https://github.com/modelcontextprotocol), Cline can extend his capabilities through custom tools. While you can use [community-made servers](https://github.com/modelcontextprotocol/servers), Cline can instead create and install tools tailored to your specific workflow. Just ask Cline to "add a tool" and he will handle everything, from creating a new MCP server to installing it into the extension. These custom tools then become part of Cline's toolkit, ready to use in future tasks.

*   "add a tool that fetches Jira tickets": Retrieve ticket ACs and put Cline to work
*   "add a tool that manages AWS EC2s": Check server metrics and scale instances up or down
*   "add a tool that pulls the latest PagerDuty incidents": Fetch details and ask Cline to fix bugs

[![](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)  

[![](https://private-user-images.githubusercontent.com/7799382/374833204-7fdf41e6-281a-4b4b-ac19-020b838b6970.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMzIwNC03ZmRmNDFlNi0yODFhLTRiNGItYWMxOS0wMjBiODM4YjY5NzAucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MTcxZGMzMzNkZDljOTZkN2VkODY5NmJlMDA0NWUzOTQxNzEwOTZlMzllYTFiNDZmNzQwNzkwMzA1ZDQyZGExNCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.Fwel17xcrYmmKHrCiVuCl87sMusdLO0i8hwZHuE3chs)](https://private-user-images.githubusercontent.com/7799382/374833204-7fdf41e6-281a-4b4b-ac19-020b838b6970.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDgzMzIwNC03ZmRmNDFlNi0yODFhLTRiNGItYWMxOS0wMjBiODM4YjY5NzAucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MTcxZGMzMzNkZDljOTZkN2VkODY5NmJlMDA0NWUzOTQxNzEwOTZlMzllYTFiNDZmNzQwNzkwMzA1ZDQyZGExNCZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.Fwel17xcrYmmKHrCiVuCl87sMusdLO0i8hwZHuE3chs)

### Add Context

[](#add-context)

**`@url`:** Paste in a URL for the extension to fetch and convert to markdown, useful when you want to give Cline the latest docs

**`@problems`:** Add workspace errors and warnings ('Problems' panel) for Cline to fix

**`@file`:** Adds a file's contents so you don't have to waste API requests approving read file (+ type to search files)

**`@folder`:** Adds folder's files all at once to speed up your workflow even more

[![](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)  
