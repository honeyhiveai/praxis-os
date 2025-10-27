- Restore the stash after formatting
This ensures that only intentionally staged changes are included in commits, preventing accidental inclusion of work-in-progress modifications.
### Context
It's been sufficient time since the Prettier → Biome migration that all team members should have the proper tooling installed. The original workaround is no longer needed and is now causing more problems than it solves.")[#6188](https://github.com/cline/cline/pull/6188)[)](/cline/cline/commit/60ddf80e5c8f5e0f2cf7b00778feaaa668781f2d "Remove --no-stash flag from lint-staged in pre-commit hook (#6188)
### Problem
The `--no-stash` flag was originally added to work around issues where teammates hadn't installed Biome after our migration from Prettier. When the formatter failed, lint-staged's default stashing behavior would remove staged changes, causing frustration.
However, this workaround now causes a different problem: lint-staged runs formatters on files containing both staged AND unstaged changes. When Biome formats these files, it inadvertently stages unstaged modifications, effectively merging work-in-progress changes into commits.
### Solution
Remove the `--no-stash` flag to restore lint-staged's default behavior:
- Stash unstaged changes before running formatters
- Run formatters only on staged content
- Restore the stash after formatting
This ensures that only intentionally staged changes are included in commits, preventing accidental inclusion of work-in-progress modifications.
### Context
It's been sufficient time since the Prettier → Biome migration that all team members should have the proper tooling installed. The original workaround is no longer needed and is now causing more problems than it solves.")

Sep 13, 2025

[.vscode](/cline/cline/tree/main/.vscode ".vscode")

[.vscode](/cline/cline/tree/main/.vscode ".vscode")

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

[assets](/cline/cline/tree/main/assets "assets")

[assets](/cline/cline/tree/main/assets "assets")

[New icon](/cline/cline/commit/bbee587cfe57c7fbd82672412259143a9e7ab7af "New icon")

Jan 17, 2025

[cli](/cline/cline/tree/main/cli "cli")

[cli](/cline/cline/tree/main/cli "cli")

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

[docs](/cline/cline/tree/main/docs "docs")

[docs](/cline/cline/tree/main/docs "docs")

[Added multiroot docs (](/cline/cline/commit/feee75b158f2b60153cb20002b01c3f5299a3cc5 "Added multiroot docs (#6597)
Co-authored-by: Kevin Bond <kevin@Kevins-MacBook-Pro.local>")[#6597](https://github.com/cline/cline/pull/6597)[)](/cline/cline/commit/feee75b158f2b60153cb20002b01c3f5299a3cc5 "Added multiroot docs (#6597)
Co-authored-by: Kevin Bond <kevin@Kevins-MacBook-Pro.local>")

Oct 8, 2025

[evals](/cline/cline/tree/main/evals "evals")

[evals](/cline/cline/tree/main/evals "evals")

[Remove open in editor button (](/cline/cline/commit/ba126726005921b2d915d8673d472ad849f8f1ee "Remove open in editor button (#6462)
* first pass of removing all related code
# Conflicts:
#	src/hosts/external/ExternalWebviewProvider.ts
#	src/hosts/vscode/VscodeWebviewProvider.ts
* remove more things
* rename all sidebarWebviews to webview
* remove null from getInstance and remove null checks
* remove client id logic and update RPC subscriptions to match this
* add back extension.test.ts without irrelevant webview panel tests
* Refresh CI cache - fix proto compilation
* add comment to try to invalidate CI cache
* add clean script to test.yml for test-platform-integration
* remove clean script didn't work
* finally found the error in the code - linter wasn't highlighting it
* Don't delete unrelated tests in this PR
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>")[#6462](https://github.com/cline/cline/pull/6462)[)](/cline/cline/commit/ba126726005921b2d915d8673d472ad849f8f1ee "Remove open in editor button (#6462)
* first pass of removing all related code
# Conflicts:
#	src/hosts/external/ExternalWebviewProvider.ts
#	src/hosts/vscode/VscodeWebviewProvider.ts
* remove more things
* rename all sidebarWebviews to webview
* remove null from getInstance and remove null checks
* remove client id logic and update RPC subscriptions to match this
* add back extension.test.ts without irrelevant webview panel tests
* Refresh CI cache - fix proto compilation
* add comment to try to invalidate CI cache
* add clean script to test.yml for test-platform-integration
* remove clean script didn't work
* finally found the error in the code - linter wasn't highlighting it
* Don't delete unrelated tests in this PR
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>")

Sep 29, 2025

[locales](/cline/cline/tree/main/locales "locales")

[locales](/cline/cline/tree/main/locales "locales")

[Fix the Syntax in zh-tw/README.md to Improve Text Rendering (](/cline/cline/commit/14a0c605508112883dfe6d68f3aacd350e28859b "Fix the Syntax in zh-tw/README.md to Improve Text Rendering (#3724)
* Update zh-tw/README.md
Correct the Markdown syntax to properly display bold text.
* Update zh-tw/README.md
Insert line breaks for each item listed under ### 新增上下文.")[#3724](https://github.com/cline/cline/pull/3724)[)](/cline/cline/commit/14a0c605508112883dfe6d68f3aacd350e28859b "Fix the Syntax in zh-tw/README.md to Improve Text Rendering (#3724)
* Update zh-tw/README.md
Correct the Markdown syntax to properly display bold text.
* Update zh-tw/README.md
Insert line breaks for each item listed under ### 新增上下文.")

May 22, 2025

[proto](/cline/cline/tree/main/proto "proto")

[proto](/cline/cline/tree/main/proto "proto")

[Add auto-retry with exponential backof for failed API requests (](/cline/cline/commit/3b636e1a76b346c5ba268a4b79077d806f308712 "Add auto-retry with exponential backof for failed API requests (#6727)
* add first version of auto-retry failed requests
Remove auto-retry as an option and do it by default for all errors that aren't credit issues for cline provider
Fix error retry showing for insufficient credits error
remove lastAutoRetryDelay
Fixes
Fixes
Fix
Fix
remove retrymessage for consistent UI
* Create lucky-mayflies-arrive.md
* Fix autoRetryAttempt counter not getting reset")[#6727](https://github.com/cline/cline/pull/6727)[)](/cline/cline/commit/3b636e1a76b346c5ba268a4b79077d806f308712 "Add auto-retry with exponential backof for failed API requests (#6727)
* add first version of auto-retry failed requests
Remove auto-retry as an option and do it by default for all errors that aren't credit issues for cline provider
Fix error retry showing for insufficient credits error
remove lastAutoRetryDelay
Fixes
Fixes
Fix
Fix
remove retrymessage for consistent UI
* Create lucky-mayflies-arrive.md
* Fix autoRetryAttempt counter not getting reset")

Oct 10, 2025

[scripts](/cline/cline/tree/main/scripts "scripts")

[scripts](/cline/cline/tree/main/scripts "scripts")

[Fix CLI installation script (](/cline/cline/commit/0858ff517af6243427a45ee175f76abd596291ce "Fix CLI installation script (#6760)
* feat(install): improve CLI release detection and error handling
- Redirect error messages to stderr for proper error stream handling
- Filter releases to only match tags ending in '-cli' suffix when fetching latest
- Add explicit .tar.gz extension matching in download URL detection
- Improve error messages to be more specific about missing packages
- Add informative messages about which CLI release is being installed
This ensures the install script correctly identifies CLI-specific releases
and provides better feedback when releases or platform packages are not found.
The stderr redirection prevents error messages from being captured in command
substitutions.
* feat(install): improve shell detection and PATH configuration
- Add support for fish shell and XDG_CONFIG_HOME standard
- Check if bin directory is already in current PATH before modifying config
- Detect shell from $SHELL variable instead of relying on version variables
- Create default config file if none exists for the detected shell
- Use grep -Fq for more reliable PATH entry detection
- Support multiple possible config file locations per shell (zsh, bash, fish)
This improves the installation experience across different shell environments
and prevents duplicate PATH entries when re-running the installer.
* refactor
* better install script
---------
Co-authored-by: pashpashpash <nik@nugbase.com>")[#6760](https://github.com/cline/cline/pull/6760)[)](/cline/cline/commit/0858ff517af6243427a45ee175f76abd596291ce "Fix CLI installation script (#6760)
* feat(install): improve CLI release detection and error handling
- Redirect error messages to stderr for proper error stream handling
- Filter releases to only match tags ending in '-cli' suffix when fetching latest
- Add explicit .tar.gz extension matching in download URL detection
- Improve error messages to be more specific about missing packages
- Add informative messages about which CLI release is being installed
This ensures the install script correctly identifies CLI-specific releases
and provides better feedback when releases or platform packages are not found.
The stderr redirection prevents error messages from being captured in command
substitutions.
* feat(install): improve shell detection and PATH configuration
- Add support for fish shell and XDG_CONFIG_HOME standard
- Check if bin directory is already in current PATH before modifying config
- Detect shell from $SHELL variable instead of relying on version variables
- Create default config file if none exists for the detected shell
- Use grep -Fq for more reliable PATH entry detection
- Support multiple possible config file locations per shell (zsh, bash, fish)
This improves the installation experience across different shell environments
and prevents duplicate PATH entries when re-running the installer.
* refactor
* better install script
---------
Co-authored-by: pashpashpash <nik@nugbase.com>")

Oct 10, 2025

[src](/cline/cline/tree/main/src "src")

[src](/cline/cline/tree/main/src "src")

[Add missing remote config setting for AWS use global inference (](/cline/cline/commit/078f33a285c30b35b45819b35374af03b31f6bb7 "Add missing remote config setting for AWS use global inference (#6758)")[#6758](https://github.com/cline/cline/pull/6758)[)](/cline/cline/commit/078f33a285c30b35b45819b35374af03b31f6bb7 "Add missing remote config setting for AWS use global inference (#6758)")

Oct 10, 2025

[standalone/runtime-files](/cline/cline/tree/main/standalone/runtime-files "This path skips through empty directories")

[standalone/runtime-files](/cline/cline/tree/main/standalone/runtime-files "This path skips through empty directories")

[Support node modules that include binaries in cline-core (](/cline/cline/commit/fc19697fad944a52447f51fb44ada9c4a5cc598c "Support node modules that include binaries in cline-core (#6046)
* Fix check for debug build in package-standalone script
* Support node modules that include binaries
Add support to the scripts/package-standalone.js for node modules that use platform-specific binary modules.
By default the script bundles the module for all platforms, this can be disabled with -s for single platform builds.
The module for each platform will be bundled into standalone.zip in platform specific directories:
```
binaries/linux-arm64/node_modules
binaries/darwin-x64/node_modules
binaries/win32-x64/node_modules
binaries/darwin-arm64/node_modules
binaries/linux-x64/node_modules
```
When running cline-core add the correct directory to the NODE_PATH, e.g.
```
$ export NODE_PATH=./node_modules/:./binaries/darwin-arm64/node_modules/
cline:/tmp/1$ node cline-core.js
Loading stubs...
Finished loading stubs
Loading stub impls...
Finished loading stub impls...
Cline environment: production
XS variant configuration warnings: [
'Component overrides for unused components: TOOL_USE_SECTION, TOOLS_SECTION, MCP_SECTION, TODO_SECTION, FEEDBACK_SECTION',
'Missing recommended components: TOOL_USE_SECTION'
]
[2025-09-05T19:53:00.853] #bot.cline.server.ts Running standalone cline  0.0.1
[2025-09-05T19:53:00.854] #bot.cline.server.ts Using settings dir: /Users/sjf/.cline/data
Finished loading vscode context...
[2025-09-05T19:53:00.858] #bot.cline.server.ts
Starting cline-core service...
sjfsjf created DBBBBBBBBB:  Database {
name: '/tmp/db.sql',
open: true,
inTransaction: false,
readonly: false,
memory: false
}
```
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Support node modules that include binaries
Add support to the scripts/package-standalone.js for node modules that use platform-specific binary modules.
By default the script bundles the module for all platforms, this can be disabled with -s for single platform builds.
The module for each platform will be bundled into standalone.zip in platform specific directories:
```
binaries/linux-arm64/node_modules
binaries/darwin-x64/node_modules
binaries/win32-x64/node_modules
binaries/darwin-arm64/node_modules
binaries/linux-x64/node_modules
```
When running cline-core add the correct directory to the NODE_PATH, e.g.
```
$ export NODE_PATH=./node_modules/:./binaries/darwin-arm64/node_modules/
cline:/tmp/1$ node cline-core.js
Loading stubs...
Finished loading stubs
Loading stub impls...
Finished loading stub impls...
Cline environment: production
XS variant configuration warnings: [
'Component overrides for unused components: TOOL_USE_SECTION, TOOLS_SECTION, MCP_SECTION, TODO_SECTION, FEEDBACK_SECTION',
'Missing recommended components: TOOL_USE_SECTION'
]
[2025-09-05T19:53:00.853] #bot.cline.server.ts Running standalone cline  0.0.1
[2025-09-05T19:53:00.854] #bot.cline.server.ts Using settings dir: /Users/sjf/.cline/data
Finished loading vscode context...
[2025-09-05T19:53:00.858] #bot.cline.server.ts
Starting cline-core service...
sjfsjf created DBBBBBBBBB:  Database {
name: '/tmp/db.sql',
open: true,
inTransaction: false,
readonly: false,
memory: false
}
```
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Remove test code
* Use the correct target directory for the binaries
The directory structure that the JB host expects is does
not exactly match ${arch}-${os}
* Update package-standalone script
Warn if there is module that needs binaries, but it is not being used.
Reset the binaries dir before packaging.
---------
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>")[#6046](https://github.com/cline/cline/pull/6046)[)](/cline/cline/commit/fc19697fad944a52447f51fb44ada9c4a5cc598c "Support node modules that include binaries in cline-core (#6046)
* Fix check for debug build in package-standalone script
* Support node modules that include binaries
Add support to the scripts/package-standalone.js for node modules that use platform-specific binary modules.
By default the script bundles the module for all platforms, this can be disabled with -s for single platform builds.
The module for each platform will be bundled into standalone.zip in platform specific directories:
```
binaries/linux-arm64/node_modules
binaries/darwin-x64/node_modules
binaries/win32-x64/node_modules
binaries/darwin-arm64/node_modules
binaries/linux-x64/node_modules
```
When running cline-core add the correct directory to the NODE_PATH, e.g.
```
$ export NODE_PATH=./node_modules/:./binaries/darwin-arm64/node_modules/
cline:/tmp/1$ node cline-core.js
Loading stubs...
Finished loading stubs
Loading stub impls...
Finished loading stub impls...
Cline environment: production
XS variant configuration warnings: [
'Component overrides for unused components: TOOL_USE_SECTION, TOOLS_SECTION, MCP_SECTION, TODO_SECTION, FEEDBACK_SECTION',
'Missing recommended components: TOOL_USE_SECTION'
]
[2025-09-05T19:53:00.853] #bot.cline.server.ts Running standalone cline  0.0.1
[2025-09-05T19:53:00.854] #bot.cline.server.ts Using settings dir: /Users/sjf/.cline/data
Finished loading vscode context...
[2025-09-05T19:53:00.858] #bot.cline.server.ts
Starting cline-core service...
sjfsjf created DBBBBBBBBB:  Database {
name: '/tmp/db.sql',
open: true,
inTransaction: false,
readonly: false,
memory: false
}
```
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Support node modules that include binaries
Add support to the scripts/package-standalone.js for node modules that use platform-specific binary modules.
By default the script bundles the module for all platforms, this can be disabled with -s for single platform builds.
The module for each platform will be bundled into standalone.zip in platform specific directories:
```
binaries/linux-arm64/node_modules
binaries/darwin-x64/node_modules
binaries/win32-x64/node_modules
binaries/darwin-arm64/node_modules
binaries/linux-x64/node_modules
```
When running cline-core add the correct directory to the NODE_PATH, e.g.
```
$ export NODE_PATH=./node_modules/:./binaries/darwin-arm64/node_modules/
cline:/tmp/1$ node cline-core.js
Loading stubs...
Finished loading stubs
Loading stub impls...
Finished loading stub impls...
Cline environment: production
XS variant configuration warnings: [
'Component overrides for unused components: TOOL_USE_SECTION, TOOLS_SECTION, MCP_SECTION, TODO_SECTION, FEEDBACK_SECTION',
'Missing recommended components: TOOL_USE_SECTION'
]
[2025-09-05T19:53:00.853] #bot.cline.server.ts Running standalone cline  0.0.1
[2025-09-05T19:53:00.854] #bot.cline.server.ts Using settings dir: /Users/sjf/.cline/data
Finished loading vscode context...
[2025-09-05T19:53:00.858] #bot.cline.server.ts
Starting cline-core service...
sjfsjf created DBBBBBBBBB:  Database {
name: '/tmp/db.sql',
open: true,
inTransaction: false,
readonly: false,
memory: false
}
```
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Apply suggestion from @ellipsis-dev[bot]
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>
* Remove test code
* Use the correct target directory for the binaries
The directory structure that the JB host expects is does
not exactly match ${arch}-${os}
* Update package-standalone script
Warn if there is module that needs binaries, but it is not being used.
Reset the binaries dir before packaging.
---------
Co-authored-by: ellipsis-dev[bot] <65095814+ellipsis-dev[bot]@users.noreply.github.com>")

Sep 7, 2025

[testing-platform](/cline/cline/tree/main/testing-platform "testing-platform")

[testing-platform](/cline/cline/tree/main/testing-platform "testing-platform")

[Testing Platform - Support partial response validation via meta.expec…](/cline/cline/commit/5be6ba68a3b158176cd0d3a6b08a0a9d1ae37ce6 "Testing Platform - Support partial response validation via meta.expected (#6399)
Testing Platform - Support partial response validation via meta.expected")

Sep 24, 2025

[tests/specs](/cline/cline/tree/main/tests/specs "This path skips through empty directories")

[tests/specs](/cline/cline/tree/main/tests/specs "This path skips through empty directories")

[Testing Platform - Support partial response validation via meta.expec…](/cline/cline/commit/5be6ba68a3b158176cd0d3a6b08a0a9d1ae37ce6 "Testing Platform - Support partial response validation via meta.expected (#6399)
Testing Platform - Support partial response validation via meta.expected")

Sep 24, 2025

[walkthrough](/cline/cline/tree/main/walkthrough "walkthrough")

[walkthrough](/cline/cline/tree/main/walkthrough "walkthrough")

[Adding Cline Walkthrough (](/cline/cline/commit/47899ac52d7336c4a6cf2c9b8cb76f999dd1ceca "Adding Cline Walkthrough (#3746)
* Show gemini 2.5 flash prompt cache
* Show gemini 2.5 flash prompt cache
* Show gemini 2.5 flash prompt cache
* Show gemini 2.5 flash prompt cache
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* New files
---------
Co-authored-by: Cline Evaluation <cline@example.com>")[#3746](https://github.com/cline/cline/pull/3746)[)](/cline/cline/commit/47899ac52d7336c4a6cf2c9b8cb76f999dd1ceca "Adding Cline Walkthrough (#3746)
* Show gemini 2.5 flash prompt cache
* Show gemini 2.5 flash prompt cache
* Show gemini 2.5 flash prompt cache
* Show gemini 2.5 flash prompt cache
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* Fix Diff edit prompt
* New files
---------
Co-authored-by: Cline Evaluation <cline@example.com>")

Jun 4, 2025

[webview-ui](/cline/cline/tree/main/webview-ui "webview-ui")

[webview-ui](/cline/cline/tree/main/webview-ui "webview-ui")

[Add auto-retry with exponential backof for failed API requests (](/cline/cline/commit/3b636e1a76b346c5ba268a4b79077d806f308712 "Add auto-retry with exponential backof for failed API requests (#6727)
* add first version of auto-retry failed requests
Remove auto-retry as an option and do it by default for all errors that aren't credit issues for cline provider
Fix error retry showing for insufficient credits error
remove lastAutoRetryDelay
Fixes
Fixes
Fix
Fix
remove retrymessage for consistent UI
* Create lucky-mayflies-arrive.md
* Fix autoRetryAttempt counter not getting reset")[#6727](https://github.com/cline/cline/pull/6727)[)](/cline/cline/commit/3b636e1a76b346c5ba268a4b79077d806f308712 "Add auto-retry with exponential backof for failed API requests (#6727)
* add first version of auto-retry failed requests
Remove auto-retry as an option and do it by default for all errors that aren't credit issues for cline provider
Fix error retry showing for insufficient credits error
remove lastAutoRetryDelay
Fixes
Fixes
Fix
Fix
remove retrymessage for consistent UI
* Create lucky-mayflies-arrive.md
* Fix autoRetryAttempt counter not getting reset")

Oct 10, 2025

[.changie.yaml](/cline/cline/blob/main/.changie.yaml ".changie.yaml")

[.changie.yaml](/cline/cline/blob/main/.changie.yaml ".changie.yaml")

[chore: add changie](/cline/cline/commit/b2dd04cff3385a95967f0407f8e31edc693e8156 "chore: add changie")

Jan 29, 2025

[.env.example](/cline/cline/blob/main/.env.example ".env.example")

[.env.example](/cline/cline/blob/main/.env.example ".env.example")

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

[.gitattributes](/cline/cline/blob/main/.gitattributes ".gitattributes")

[.gitattributes](/cline/cline/blob/main/.gitattributes ".gitattributes")

[Run tests against Windows and Ubuntu (](/cline/cline/commit/1700c0e4f88e81ba39bef08e8587e466c8087a6c "Run tests against Windows and Ubuntu (#3246)
* add a matrix strategy for testing
* Handle EOL on Windows
* use bash as shell on every os and run the test-ci script
* fix tsconfig path resolution using the __dirnname
* print test results regardless of status
* Limit artifact upload to Linux
* update the test-cli
* Add windows-specific dependencies as optional dependencies
lightningcss-win32-x64-msvc
rollup-win32-x64-msvc
* Do not collect coverage on Windows
* Use UTF-8 on the Python Scripts
* force the ubuntu-latest name to be `test`")[#3246](https://github.com/cline/cline/pull/3246)[)](/cline/cline/commit/1700c0e4f88e81ba39bef08e8587e466c8087a6c "Run tests against Windows and Ubuntu (#3246)
* add a matrix strategy for testing
* Handle EOL on Windows
* use bash as shell on every os and run the test-ci script
* fix tsconfig path resolution using the __dirnname
* print test results regardless of status
* Limit artifact upload to Linux
* update the test-cli
* Add windows-specific dependencies as optional dependencies
lightningcss-win32-x64-msvc
rollup-win32-x64-msvc
* Do not collect coverage on Windows
* Use UTF-8 on the Python Scripts
* force the ubuntu-latest name to be `test`")

May 19, 2025

[.gitignore](/cline/cline/blob/main/.gitignore ".gitignore")

[.gitignore](/cline/cline/blob/main/.gitignore ".gitignore")

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
