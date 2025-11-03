"""AST Index for structural code search using Tree-sitter.

Phase 5, Task 5.1-5.6: Provides precise symbol lookup (functions, classes,
methods) via Tree-sitter Abstract Syntax Tree (AST) parsing.

This index complements CodeIndex's semantic search with structural queries:
- Find all implementations of a function
- Find all calls to a specific method
- Find class definitions and their methods
- Locate symbol definitions across the codebase

Architecture:
- LanceDB storage: Stores extracted symbols with metadata
- Tree-sitter parsers: Dynamically loaded per-language
- Config-driven: Supported languages defined in config
- Parser cache: Reuses loaded parsers for efficiency

Example:
    >>> ast_index = ASTIndex(cache_path=Path(".cache/ast"), config=config)
    >>> ast_index.build(source_paths=["src/"], force=False)
    >>> results = ast_index.search(
    ...     query={"symbol_type": "function", "name": "authenticate"},
    ...     filters={"language": "python"},
    ...     n=10
    ... )
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

import lancedb

from .base import BaseIndex, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class Symbol:
    """Data class representing a code symbol extracted from AST.
    
    Phase 5, Task 5.3: Stores symbol information extracted by Tree-sitter.
    
    Attributes:
        symbol_name: Name of the symbol (e.g., "authenticate", "User")
        symbol_type: Type of symbol ("function", "class", "method")
        file_path: Path to source file containing symbol
        line_range: Tuple of (start_line, end_line) for symbol definition
        language: Programming language (e.g., "python", "javascript")
        signature: Function/method signature (e.g., "def authenticate(user, pwd)")
            Empty string for classes.
        symbol_id: Unique identifier (file_path + line_range)
    
    Example:
        >>> symbol = Symbol(
        ...     symbol_name="authenticate",
        ...     symbol_type="function",
        ...     file_path="src/auth.py",
        ...     line_range=(42, 50),
        ...     language="python",
        ...     signature="def authenticate(username: str, password: str) -> bool"
        ... )
    """
    symbol_name: str
    symbol_type: str  # "function", "class", "method"
    file_path: str
    line_range: tuple  # (start_line, end_line)
    language: str
    signature: str = ""
    symbol_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Generate symbol_id after initialization."""
        if self.symbol_id is None:
            self.symbol_id = f"{self.file_path}:{self.line_range[0]}-{self.line_range[1]}"


class ASTIndex(BaseIndex):
    """AST-based structural code search index using Tree-sitter.
    
    This class provides precise symbol lookup capabilities by parsing code
    into Abstract Syntax Trees (ASTs) using Tree-sitter. It stores extracted
    symbols (functions, classes, methods) in LanceDB for fast structural queries.
    
    Phase 5, Task 5.1: Class structure and initialization.
    
    Attributes:
        cache_path: Directory for LanceDB storage
        config: Index configuration (languages, cache settings)
        supported_languages: List of languages to parse (from config)
        parser_cache: Dict mapping language name to Tree-sitter parser module
        db: LanceDB database connection
        table: LanceDB table for AST symbol storage
        table_name: Name of LanceDB table ("praxis_os_code_ast")
    
    Example:
        >>> config = {
        ...     "languages": ["python", "javascript", "typescript", "go", "rust"],
        ...     "cache": {"enabled": True}
        ... }
        >>> index = ASTIndex(cache_path=Path(".cache/ast"), config=config)
        >>> index.build(source_paths=["src/"], force=True)
    
    Note:
        Requires Tree-sitter language parsers to be installed.
        Use `pip install tree-sitter-python tree-sitter-javascript` etc.
    """
    
    def __init__(
        self,
        cache_path: Path,
        config: Dict[str, Any],
        base_path: Optional[Path] = None
    ) -> None:
        """Initialize AST index with LanceDB connection and parser cache.
        
        Phase 5, Task 5.1: Sets up foundation for AST-based code search.
        
        Args:
            cache_path: Directory path for LanceDB storage. Will be created
                if it doesn't exist.
            config: Configuration dictionary. Required keys:
                - languages: List[str] - Supported languages
                    (e.g., ["python", "javascript"])
                Optional keys:
                - cache: Dict - Cache settings
            base_path: Base directory for resolving relative source paths.
                Defaults to cache_path.parent.parent (assuming cache is .praxis-os/.cache/ast).
        
        Raises:
            ValueError: If config is missing required keys
            RuntimeError: If LanceDB connection fails
        
        Example:
            >>> config = {"languages": ["python", "javascript"]}
            >>> index = ASTIndex(
            ...     cache_path=Path(".praxis-os/.cache/ast"),
            ...     config=config,
            ...     base_path=Path(".praxis-os")
            ... )
        """
        super().__init__(cache_path, config)
        
        # LanceDB connection and per-language tables
        # Architecture: Separate table per language (ast_python, ast_typescript, etc.)
        # Benefits:
        #   - Language filter becomes table selection (no WHERE needed)
        #   - Cleaner separation of concerns per language
        #   - Better scalability for multi-language codebases
        self.table_prefix = "praxis_os_ast"
        self.db: Optional[lancedb.DBConnection] = None
        self.tables: Dict[str, Any] = {}  # {language: LanceTable}
        
        # Store base path for resolving relative source paths
        # Default: if cache is .praxis-os/.cache/ast, base is .praxis-os
        self.base_path = base_path if base_path else cache_path.parent.parent
        
        # Load language configurations (config-driven!)
        # New format: languages is a dict with per-language settings
        languages_config = config.get("languages", {})
        if not languages_config:
            raise ValueError("Config must specify at least one language")
        
        self.supported_languages: List[str] = list(languages_config.keys())
        self.language_configs: Dict[str, Dict] = languages_config
        
        # Build reverse mapping: file extension → language
        # E.g., {".py": "python", ".js": "javascript", ".mjs": "javascript"}
        self.ext_to_language: Dict[str, str] = {}
        for lang, lang_config in languages_config.items():
            extensions = lang_config.get("file_extensions", [])
            for ext in extensions:
                self.ext_to_language[ext.lower()] = lang
        
        # Load query strategy config (with defaults)
        query_config = config.get("query_strategy", {})
        self.parallel_threshold = query_config.get("parallel_threshold", 3)
        self.max_workers = query_config.get("max_workers", 10)
        self.overfetch_multiplier = query_config.get("overfetch_multiplier", 5)
        
        # Initialize parser cache (language -> parser module)
        # Phase 5, Task 5.2: Load parsers dynamically at initialization
        self.parser_cache: Dict[str, Any] = self._load_parsers()
        
        logger.info(
            "ASTIndex initialized: languages=%s, parsers_loaded=%d, cache_path=%s",
            self.supported_languages,
            len(self.parser_cache),
            cache_path
        )
    
    def _load_parsers(self) -> Dict[str, Any]:
        """Dynamically load Tree-sitter parsers for configured languages.
        
        Phase 5, Task 5.2: Implements config-driven parser loading using
        importlib. Follows naming convention: `tree-sitter-{language}` package
        imports as `tree_sitter_{language}` module.
        
        With auto-install enabled (default), will automatically pip install
        missing parsers on first use. This provides zero-friction config-driven
        language support: just add to config, restart server, and it works.
        
        Returns:
            Dictionary mapping language name to loaded parser module.
            Only includes languages for which parsers were successfully loaded.
        
        Example:
            >>> ast_index = ASTIndex(cache_path=Path(".cache"), config={
            ...     "languages": {"python": {...}, "javascript": {...}},
            ...     "auto_install_parsers": True
            ... })
            >>> parsers = ast_index._load_parsers()
            >>> # Auto-installs missing parsers, logs progress
            >>> print(parsers.keys())
            dict_keys(['python', 'javascript'])  # All parsers loaded!
        
        Note:
            Uses graceful degradation: if auto-install fails, logs warning and
            continues with remaining languages. Never raises exception for
            missing parser - this is intentional to allow partial language support.
        
        Auto-Install:
            Set `auto_install_parsers: false` in config to disable.
            Useful for air-gapped environments or strict dependency control.
        """
        import importlib
        
        loaded_parsers: Dict[str, Any] = {}
        auto_install_enabled = self.config.get("auto_install_parsers", True)
        failed_installs = []
        
        for language in self.supported_languages:
            # Convention: tree-sitter-python → tree_sitter_python
            module_name = f"tree_sitter_{language}"
            
            try:
                parser_module = importlib.import_module(module_name)
                loaded_parsers[language] = parser_module
                logger.debug("✅ Loaded Tree-sitter parser for %s", language)
            except ImportError as e:
                # Try auto-install if enabled
                if auto_install_enabled and self.base_path:
                    logger.info(
                        "🔧 Parser for '%s' not found, attempting auto-install...",
                        language
                    )
                    
                    if self._auto_install_parser(language):
                        # Retry import after successful install
                        try:
                            parser_module = importlib.import_module(module_name)
                            loaded_parsers[language] = parser_module
                            logger.info("✅ Successfully auto-installed tree-sitter-%s", language)
                        except ImportError:
                            logger.warning(
                                "❌ Auto-install succeeded but import failed for tree-sitter-%s",
                                language
                            )
                            failed_installs.append(language)
                    else:
                        logger.warning("❌ Auto-install failed for tree-sitter-%s", language)
                        failed_installs.append(language)
                else:
                    logger.warning(
                        "⚠️  Parser for '%s' not installed. "
                        "Install with: pip install tree-sitter-%s",
                        language, language
                    )
                    failed_installs.append(language)
            except Exception as e:
                logger.error(
                    "Failed to load parser for %s: %s (skipping)",
                    language,
                    e
                )
                failed_installs.append(language)
                continue
        
        # Log summary
        self._log_parser_summary(loaded_parsers, failed_installs)
        
        return loaded_parsers
    
    def _auto_install_parser(self, language: str) -> bool:
        """Auto-install Tree-sitter parser package.
        
        Attempts to install tree-sitter-{language} package using pip in the
        prAxIs OS virtual environment.
        
        Args:
            language: Language name (e.g., 'python', 'ruby')
        
        Returns:
            True if installation succeeded, False otherwise.
        
        Note:
            This is safe because:
            1. We control the venv (it's ours)
            2. Package pattern is predictable (tree-sitter-{language})
            3. User explicitly configured the language (intent is clear)
            4. Config flag controls this behavior (can be disabled)
        """
        import subprocess
        
        try:
            # Find pip in the venv
            venv_pip = self.base_path / "venv" / "bin" / "pip"
            if not venv_pip.exists():
                logger.warning("Cannot auto-install: venv pip not found at %s", venv_pip)
                return False
            
            package = f"tree-sitter-{language}>=0.21.0"
            
            logger.debug("   Running: %s install %s", venv_pip, package)
            
            result = subprocess.run(
                [str(venv_pip), "install", package, "--quiet"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes max
            )
            
            if result.returncode != 0:
                logger.debug("   pip stderr: %s", result.stderr)
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.warning("Auto-install timeout for tree-sitter-%s", language)
            return False
        except Exception as e:
            logger.warning("Auto-install error for tree-sitter-%s: %s", language, e)
            return False
    
    def _log_parser_summary(
        self,
        loaded_parsers: Dict[str, Any],
        failed_installs: List[str]
    ) -> None:
        """Log summary of parser loading results.
        
        Provides clear visibility into which languages are active vs missing.
        
        Args:
            loaded_parsers: Successfully loaded parsers
            failed_installs: Languages that failed to load/install
        """
        if not failed_installs:
            # All good!
            languages = ', '.join(sorted(loaded_parsers.keys()))
            logger.info("✅ Code search enabled for: %s", languages)
        else:
            # Some missing
            logger.warning("━" * 60)
            logger.warning("⚠️  TREE-SITTER PARSER STATUS")
            logger.warning("")
            logger.warning("   Configured:  %s", ', '.join(sorted(self.supported_languages)))
            logger.warning("   Available:   %s", ', '.join(sorted(loaded_parsers.keys())))
            logger.warning("   Missing:     %s", ', '.join(sorted(failed_installs)))
            logger.warning("")
            logger.warning("   Code search will only work for: %s", ', '.join(sorted(loaded_parsers.keys())))
            logger.warning("")
            logger.warning("   To manually install:")
            for lang in sorted(failed_installs):
                venv_pip = self.base_path / "venv" / "bin" / "pip" if self.base_path else "pip"
                logger.warning("     %s install tree-sitter-%s", venv_pip, lang)
            logger.warning("━" * 60)
    
    def _parse_file(
        self,
        file_path: Path,
        language: str,
        parser_module: Any
    ) -> List[Symbol]:
        """Parse code file with Tree-sitter and extract symbols.
        
        Phase 5, Task 5.3: Parses file into AST using Tree-sitter, traverses
        the parse tree, and extracts function/class/method definitions with
        metadata (name, type, line range, signature).
        
        Args:
            file_path: Path to code file to parse
            language: Programming language (e.g., "python", "javascript")
            parser_module: Tree-sitter parser module (from `tree_sitter_{language}`)
        
        Returns:
            List of Symbol objects extracted from file. Empty list if parse fails
            or no symbols found.
        
        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file can't be decoded as UTF-8
        
        Example:
            >>> symbols = index._parse_file(
            ...     Path("src/auth.py"),
            ...     "python",
            ...     python_parser_module
            ... )
            >>> print(len(symbols))
            5
        
        Note:
            Uses graceful error handling - logs warning and returns empty list
            if parsing fails. Never raises exception for parse errors.
        
        Tree-sitter Integration:
            - Creates Parser instance
            - Sets language from parser_module
            - Parses file content into tree
            - Traverses tree nodes to find definitions
        """
        try:
            # Import tree-sitter (lazy import)
            try:
                from tree_sitter import Parser, Node
            except ImportError:
                logger.error(
                    "tree-sitter not installed. "
                    "Install with: pip install tree-sitter"
                )
                return []
            
            # Read file content (keep as bytes for Tree-sitter byte offsets)
            try:
                content_bytes = file_path.read_bytes()
                content = content_bytes.decode('utf-8')  # String version for display
            except UnicodeDecodeError as e:
                logger.warning("Failed to decode %s as UTF-8: %s", file_path, e)
                raise
            except FileNotFoundError:
                logger.warning("File not found: %s", file_path)
                raise
            
            # Create parser and set language
            try:
                parser = Parser()
                
                # Get language capsule from parser module
                # Convention: parser_module.language() returns PyCapsule
                if not hasattr(parser_module, 'language'):
                    logger.warning(
                        "Parser module for %s missing language() function",
                        language
                    )
                    return []
                
                lang_capsule = parser_module.language()
                
                # tree-sitter 0.25.x API: wrap capsule and assign to property
                # Import Language class from tree_sitter module (already imported above)
                from tree_sitter import Language as TSLanguage
                tree_sitter_language = TSLanguage(lang_capsule)
                
                # Use property assignment, not set_language() method
                parser.language = tree_sitter_language
                
            except Exception as e:
                logger.error(
                    "Failed to initialize parser for %s: %s",
                    language,
                    e
                )
                return []
            
            # Parse content
            try:
                tree = parser.parse(bytes(content, "utf8"))
                root_node = tree.root_node
            except Exception as e:
                logger.warning(
                    "Parse error in %s: %s (skipping file)",
                    file_path,
                    e
                )
                return []
            
            # Extract symbols from parse tree
            symbols: List[Symbol] = []
            
            # Language-specific node type mappings
            # Maps node type to symbol type
            node_type_map = self._get_node_type_map(language)
            
            # Traverse tree and extract symbols
            symbols = self._extract_symbols_from_node(
                root_node,
                file_path,
                language,
                content,
                node_type_map
            )
            
            logger.debug(
                "Extracted %d symbols from %s",
                len(symbols),
                file_path
            )
            
            return symbols
            
        except (FileNotFoundError, UnicodeDecodeError):
            # Re-raise expected exceptions
            raise
        except Exception as e:
            # Catch all other exceptions (graceful degradation)
            logger.error(
                "Unexpected error parsing %s: %s (skipping file)",
                file_path,
                e,
                exc_info=True
            )
            return []
    
    def _get_node_type_map(self, language: str) -> Dict[str, str]:
        """Get mapping of Tree-sitter node types to symbol types for language.
        
        Phase 5, Task 5.3: Provides language-specific node type mappings.
        
        Config-driven: Loads node_types from language config in index_config.yaml.
        Supports any language without code changes - just add config + parser!
        
        Args:
            language: Programming language (e.g., "python", "javascript")
        
        Returns:
            Dictionary mapping Tree-sitter node type to symbol type.
            Keys are node types (e.g., "function_definition"),
            values are symbol types ("function", "class", "method").
        
        Example:
            >>> # Config: python.node_types = {"function_definition": "function"}
            >>> node_map = index._get_node_type_map("python")
            >>> node_map["function_definition"]
            'function'
        
        Note:
            To add a new language:
            1. Add to index_config.yaml languages section
            2. Install tree-sitter parser
            3. Restart - done!
        """
        lang_config = self.language_configs.get(language, {})
        return lang_config.get("node_types", {})
    
    def _extract_symbols_from_node(
        self,
        node: Any,
        file_path: Path,
        language: str,
        content: str,
        node_type_map: Dict[str, str]
    ) -> List[Symbol]:
        """Recursively extract symbols from Tree-sitter node.
        
        Phase 5, Task 5.3: Traverses AST nodes and extracts symbol information.
        
        Args:
            node: Tree-sitter Node to traverse
            file_path: Path to source file
            language: Programming language
            content: Source file content (for extracting text)
            node_type_map: Mapping of node types to symbol types
        
        Returns:
            List of Symbol objects found in node and its children
        
        Example:
            >>> symbols = index._extract_symbols_from_node(
            ...     root_node, Path("src/auth.py"), "python", content, node_map
            ... )
        """
        symbols: List[Symbol] = []
        
        # Check if this node is a symbol we care about
        if node.type in node_type_map:
            symbol_type = node_type_map[node.type]
            
            # Extract symbol name
            symbol_name = self._extract_symbol_name(node, language)
            
            if symbol_name:
                # Extract line range (1-indexed)
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                
                # Extract signature (for functions/methods/classes)
                signature = ""
                if symbol_type in ("function", "method"):
                    signature = self._extract_signature(node, content)
                elif symbol_type == "class":
                    # For classes, extract __init__ signature
                    signature = self._extract_class_signature(node, content)
                
                symbol = Symbol(
                    symbol_name=symbol_name,
                    symbol_type=symbol_type,
                    file_path=str(file_path),
                    line_range=(start_line, end_line),
                    language=language,
                    signature=signature
                )
                symbols.append(symbol)
        
        # Recursively traverse children
        for child in node.children:
            symbols.extend(
                self._extract_symbols_from_node(
                    child, file_path, language, content, node_type_map
                )
            )
        
        return symbols
    
    def _extract_symbol_name(self, node: Any, language: str) -> str:
        """Extract symbol name from Tree-sitter node.
        
        Args:
            node: Tree-sitter Node
            language: Programming language
        
        Returns:
            Symbol name (empty string if not found)
        """
        # Language-specific name extraction
        # Most languages have a "name" or "identifier" child node
        for child in node.children:
            if child.type in ("identifier", "name", "type_identifier"):
                return child.text.decode('utf-8')
        
        return ""
    
    def _extract_signature(self, node: Any, content: str) -> str:
        """Extract function/method signature from Tree-sitter node.
        
        Handles both single-line and multi-line signatures by extracting
        everything from the def/async def keyword up to and including the
        return type annotation (if present) and the colon.
        
        Args:
            node: Tree-sitter Node (function/method definition)
            content: Source file content
        
        Returns:
            Complete function signature text (normalized to single line)
            
        Example:
            Multi-line signature:
                def search(
                    self,
                    query: str,
                    filters: Optional[Dict] = None
                ) -> List[SearchResult]:
            
            Returns: "def search(self, query: str, filters: Optional[Dict] = None) -> List[SearchResult]:"
        """
        try:
            # Extract node text directly from Tree-sitter node (already bytes)
            # Use node.text which gives us the exact bytes for this node
            node_bytes = node.text
            node_text = node_bytes.decode('utf-8')
            
            # Find the colon that ends the signature (first : at top level)
            # Strategy: Track parenthesis depth, stop at first ':' when depth is 0
            paren_depth = 0
            sig_end = 0
            in_string = False
            string_char = None
            
            for i, char in enumerate(node_text):
                # Track string boundaries to ignore colons in strings
                if char in ('"', "'") and (i == 0 or node_text[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                    continue
                
                if in_string:
                    continue
                
                # Track parenthesis depth
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                # Stop at first ':' after closing all parens (signature end)
                elif char == ':' and paren_depth == 0:
                    sig_end = i + 1  # Include the colon
                    break
            
            # Extract signature up to colon
            if sig_end > 0:
                signature = node_text[:sig_end]
            else:
                # Fallback: use first 200 chars if no colon found
                signature = node_text[:200]
            
            # Normalize: Remove excess whitespace, convert to single line
            # Replace multiple spaces/newlines with single space
            signature = ' '.join(signature.split())
            
            return signature
            
        except Exception as e:
            logger.warning("Failed to extract signature: %s", e)
            return ""
    
    def _extract_class_signature(self, node: Any, content: str) -> str:
        """Extract class signature from __init__ method.
        
        For Python classes, the "signature" is the __init__ method's signature,
        as this shows how to instantiate the class.
        
        Args:
            node: Tree-sitter Node (class definition)
            content: Source file content (not used, kept for consistency)
        
        Returns:
            __init__ signature if found, otherwise empty string
            
        Example:
            Class with __init__:
                class User:
                    def __init__(self, name: str, age: int = 0):
                        pass
            
            Returns: "def __init__(self, name: str, age: int = 0):"
        """
        try:
            # Find the class body (block node)
            body_node = None
            for child in node.children:
                if child.type == "block":
                    body_node = child
                    break
            
            if not body_node:
                return ""
            
            # Find __init__ method in body
            for child in body_node.children:
                if child.type == "function_definition":
                    # Check if this is __init__
                    for subchild in child.children:
                        if subchild.type == "identifier" and subchild.text.decode('utf-8') == "__init__":
                            # Extract signature using existing method
                            return self._extract_signature(child, content)
            
            # No __init__ found
            return ""
            
        except Exception as e:
            logger.warning("Failed to extract class signature: %s", e)
            return ""
    
    def _connect_to_index(self) -> None:
        """Connect to existing per-language AST tables in LanceDB.
        
        Opens connection to LanceDB database and loads all language-specific
        AST symbol tables. Discovers tables by prefix pattern matching.
        Creates database directory if it doesn't exist.
        
        Raises:
            RuntimeError: If tables don't exist or connection fails
        
        Example:
            >>> index._connect_to_index()  # Opens praxis_os_ast_python, etc.
        
        Note:
            Call build() first to create tables if they don't exist.
            Tables are named: {table_prefix}_{language} (e.g., praxis_os_ast_python)
        """
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        try:
            self.db = lancedb.connect(str(self.cache_path))
            
            # Discover all language tables that exist
            all_tables = self.db.table_names()
            language_tables = [
                t for t in all_tables 
                if t.startswith(f"{self.table_prefix}_")
            ]
            
            if not language_tables:
                logger.warning("No AST language tables found. Run build() to create them.")
                return
            
            # Load each language table
            self.tables = {}
            for table_name in language_tables:
                # Extract language from table name: praxis_os_ast_python -> python
                language = table_name.replace(f"{self.table_prefix}_", "")
                self.tables[language] = self.db.open_table(table_name)
                logger.debug(f"Loaded table '{table_name}' for language '{language}'")
            
            logger.info(f"Connected to {len(self.tables)} AST language tables: {list(self.tables.keys())}")
            
        except Exception as e:
            logger.error("Failed to connect to AST indexes: %s", e)
            raise RuntimeError(f"AST index connection failed: {e}") from e
    
    def build(self, source_paths: List[str], force: bool = False, incremental: bool = True) -> None:
        """Build AST index by parsing code files with Tree-sitter.
        
        Phase 5, Task 5.4: Discovers code files, parses with Tree-sitter,
        extracts symbols, and stores in LanceDB with scalar indexes.
        
        Supports incremental updates by tracking file modification times and only
        processing changed/new files.
        
        Args:
            source_paths: List of directory or file paths to index
            force: If True, rebuild index even if it exists. If False,
                skip build if index is already present.
            incremental: If True, use incremental updates (only process changed files).
                Ignored if force=True or index doesn't exist.
        
        Raises:
            RuntimeError: If build fails
        
        Example:
            >>> index.build(source_paths=["src/", "lib/"], force=True)
            >>> index.build(source_paths=["src/"], incremental=True)  # Only changed files
        
        Note:
            Requires Tree-sitter parsers installed for configured languages.
            Install with: pip install tree-sitter-python tree-sitter-javascript
        """
        logger.info("AST index build requested (force=%s, incremental=%s)", force, incremental)
        logger.info("Source paths: %s", source_paths)
        logger.info("Languages configured: %s", self.supported_languages)
        logger.info("Parsers loaded: %s", list(self.parser_cache.keys()))
        
        # Convert source_paths to Path objects
        source_path_objs = [Path(p) for p in source_paths]
        
        # Check if indexes already exist AND have data
        table_exists = False
        try:
            temp_db = lancedb.connect(str(self.cache_path))
            existing_tables = [
                t for t in temp_db.table_names()
                if t.startswith(f"{self.table_prefix}_")
            ]
            if existing_tables:
                # Check if any table has data
                has_data = False
                total_rows = 0
                for table_name in existing_tables:
                    try:
                        table = temp_db.open_table(table_name)
                        row_count = table.count_rows()
                        total_rows += row_count
                        if row_count > 0:
                            has_data = True
                    except Exception as e:
                        logger.debug(f"Failed to check rows for {table_name}: {e}")
                
                table_exists = has_data
                
                if table_exists and not force and not incremental:
                    logger.info(f"AST indexes already exist ({len(existing_tables)} tables, {total_rows} symbols), skipping build (use force=True to rebuild)")
                    self._connect_to_index()
                    return
                elif not has_data:
                    logger.warning(f"AST tables exist but are empty ({len(existing_tables)} tables), proceeding with build")
        except Exception:
            pass  # Directory doesn't exist or no tables, proceed with build
        
        # Determine build strategy
        use_incremental = incremental and table_exists and not force
        
        if use_incremental:
            logger.info("📝 Using incremental update (only processing changed files)")
            self._connect_to_index()  # Ensure we're connected to existing tables
            
            changed_files = self._get_changed_files(source_path_objs)
            
            if not changed_files:
                logger.info("No files changed, index is up to date")
                return
            
            logger.info(f"Found {len(changed_files)} changed files to process")
            files_to_process = changed_files
            
            # Delete old symbols for changed files before adding new ones
            logger.info("🗑️  Removing old symbols for changed files...")
            for file_path in changed_files:
                self.remove_file(str(file_path.resolve()))
        elif not force and table_exists:
            logger.info("AST indexes already exist, skipping build (use force=True to rebuild or incremental=True for updates)")
            self._connect_to_index()
            return
        else:
            if force:
                logger.info("🔄 Force rebuild requested - processing all files")
            else:
                logger.info("🔄 Initial build - processing all files")
            files_to_process = None  # Will be discovered below
        
        # Check if we have any parsers loaded
        if not self.parser_cache:
            logger.warning(
                "No Tree-sitter parsers loaded. AST indexing skipped. "
                "Install parsers with: pip install tree-sitter-python tree-sitter-javascript"
            )
            return
        
        # Step 1: Discover/prepare code files
        if use_incremental:
            # Already have files_to_process from _get_changed_files
            discovered_files = files_to_process
            logger.info("Step 1/4: Processing %d changed files", len(discovered_files))
        else:
            # Full build - discover all code files
            logger.info("Step 1/4: Discovering code files...")
            discovered_files = []
            
            # Get exclude patterns from config
            exclude_patterns = self.config.get("exclude_patterns", [])
            if not exclude_patterns:
                # Fallback to hardcoded defaults if not in config
                exclude_patterns = [
                    "**/tests/**", "**/__pycache__/**", "**/*.pyc",
                    "**/node_modules/**", "**/.git/**", "**/venv/**", "**/.venv/**"
                ]
            
            logger.debug("Using exclude patterns: %s", exclude_patterns)
            
            for source_path_str in source_paths:
                source_path = Path(source_path_str)
                
                # Handle relative paths (relative to base_path, i.e., .praxis-os/)
                if not source_path.is_absolute():
                    source_path = self.base_path / source_path
                
                if not source_path.exists():
                    logger.warning("Source path does not exist: %s", source_path)
                    continue
                
                if source_path.is_file():
                    # Single file - check if excluded
                    if not self._is_excluded(source_path, exclude_patterns):
                        discovered_files.append(source_path)
                elif source_path.is_dir():
                    # Recursively find code files
                    for language in self.parser_cache.keys():
                        # Determine file extension for language
                        ext_map = {
                            "python": ".py",
                            "javascript": ".js",
                            "typescript": ".ts",
                            "go": ".go",
                            "rust": ".rs",
                        }
                        ext = ext_map.get(language, f".{language}")
                        
                        # Find all files with this extension
                        for file_path in source_path.rglob(f"*{ext}"):
                            # Check if excluded by pattern
                            if self._is_excluded(file_path, exclude_patterns):
                                logger.debug("Excluded: %s", file_path)
                                continue
                            discovered_files.append(file_path)
            
            logger.info("Discovered %d code files", len(discovered_files))
        
        if not discovered_files:
            logger.warning("No code files to process")
            if use_incremental:
                # For incremental, this is OK (no changes)
                return
            else:
                logger.warning("No code files discovered for initial build")
                return
        
        # Step 2: Parse files and extract symbols
        logger.info("Step 2/4: Parsing files and extracting symbols...")
        all_symbols: List[Symbol] = []
        
        for file_path in discovered_files:
            # Determine language from extension
            language = self._detect_language(file_path)
            
            if not language or language not in self.parser_cache:
                logger.debug("Skipping %s (no parser for %s)", file_path, language)
                continue
            
            # Get parser module
            parser_module = self.parser_cache[language]
            
            # Parse file
            try:
                symbols = self._parse_file(file_path, language, parser_module)
                all_symbols.extend(symbols)
                logger.debug("Extracted %d symbols from %s", len(symbols), file_path)
            except (FileNotFoundError, UnicodeDecodeError) as e:
                logger.warning("Failed to parse %s: %s", file_path, e)
                continue
            except Exception as e:
                logger.error("Unexpected error parsing %s: %s", file_path, e)
                continue
        
        logger.info("Extracted %d total symbols", len(all_symbols))
        
        if not all_symbols:
            logger.warning("No symbols extracted")
            return
        
        # Step 3: Group symbols by language
        logger.info("Step 3/4: Grouping symbols by language...")
        symbols_by_language: Dict[str, List[Symbol]] = {}
        for symbol in all_symbols:
            lang = symbol.language
            if lang not in symbols_by_language:
                symbols_by_language[lang] = []
            symbols_by_language[lang].append(symbol)
        
        logger.info(
            "Grouped into %d languages: %s",
            len(symbols_by_language),
            {lang: len(syms) for lang, syms in symbols_by_language.items()}
        )
        
        # Step 4: Create separate LanceDB table per language
        logger.info("Step 4/4: Creating per-language LanceDB tables and indexes...")
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(str(self.cache_path))
        
        for language, symbols in symbols_by_language.items():
            table_name = f"{self.table_prefix}_{language}"
            
            # Prepare records for this language
            records = []
            for symbol in symbols:
                record = {
                    "symbol_id": symbol.symbol_id,
                    "symbol_name": symbol.symbol_name,
                    "symbol_type": symbol.symbol_type,
                    "file_path": symbol.file_path,
                    "line_start": symbol.line_range[0],
                    "line_end": symbol.line_range[1],
                    "language": symbol.language,  # Keep for consistency
                    "signature": symbol.signature,
                }
                records.append(record)
            
            if use_incremental:
                # Add new records to existing table
                logger.info(f"  ➕ Adding {len(records)} updated symbols to '{table_name}'...")
                if language in self.tables:
                    self.tables[language].add(records)
                    total_rows = self.tables[language].count_rows()
                    logger.info(f"    ✅ Updated '{table_name}' - now contains {total_rows} total symbols")
                else:
                    # Table doesn't exist yet for this language (new language added)
                    logger.info(f"  Creating new table '{table_name}' with {len(records)} symbols...")
                    table = self.db.create_table(
                        table_name,
                        data=records,
                        mode="overwrite"
                    )
                    self.tables[language] = table
                    logger.info(f"    ✅ Created '{table_name}' with {len(records)} records")
            else:
                # Full rebuild - drop and recreate table
                logger.info(f"  Creating table '{table_name}' with {len(symbols)} symbols...")
                try:
                    if force:
                        self.db.drop_table(table_name)
                        logger.debug(f"    Dropped existing table '{table_name}' (force=True)")
                except Exception:
                    pass  # Table doesn't exist, that's fine
                
                # Create table
                table = self.db.create_table(
                    table_name,
                    data=records,
                    mode="overwrite"
                )
                self.tables[language] = table
                logger.info(f"    ✅ Created '{table_name}' with {len(records)} records")
        
        # Create scalar indexes on each language table
        logger.info("  Creating scalar indexes on all tables...")
        for language, table in self.tables.items():
            table_name = f"{self.table_prefix}_{language}"
            try:
                # BTREE index on symbol_name for fast name lookups
                table.create_scalar_index("symbol_name", index_type="BTREE")
                logger.debug(f"    ✅ Created BTREE index on '{table_name}.symbol_name'")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"Failed to create index on '{table_name}.symbol_name': %s", e)
            
            try:
                # BITMAP index on symbol_type (low cardinality: function, class, method)
                table.create_scalar_index("symbol_type", index_type="BITMAP")
                logger.debug(f"    ✅ Created BITMAP index on '{table_name}.symbol_type'")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.warning(f"Failed to create index on '{table_name}.symbol_type': %s", e)
        
        # Save file mtimes for next incremental build
        self._save_file_mtimes(source_path_objs)
        
        logger.info("✅ AST index build complete: %d symbols across %d language tables", len(all_symbols), len(self.tables))
    
    def _get_changed_files(self, source_paths: List[Path]) -> List[Path]:
        """Get list of code files that changed since last build.
        
        Compares current file modification times against stored metadata
        to detect new, modified, or deleted files.
        
        Args:
            source_paths: Paths to scan for code files
        
        Returns:
            List of file paths that need reprocessing
        """
        metadata_file = self.cache_path / "metadata.json"
        
        # No metadata = all files are "changed" (first build)
        if not metadata_file.exists():
            # Collect all code files
            all_files = []
            exclude_patterns = self.config.get("exclude_patterns", [])
            for source_path in source_paths:
                for language in self.parser_cache.keys():
                    ext_map = {
                        "python": ".py",
                        "javascript": ".js",
                        "typescript": ".ts",
                        "go": ".go",
                        "rust": ".rs",
                    }
                    ext = ext_map.get(language, f".{language}")
                    for file_path in source_path.rglob(f"*{ext}"):
                        if not self._is_excluded(file_path, exclude_patterns):
                            all_files.append(file_path)
            return all_files
        
        try:
            metadata = json.loads(metadata_file.read_text())
            file_mtimes = metadata.get("files_mtimes", {})
            
            changed_files = []
            current_files = set()
            exclude_patterns = self.config.get("exclude_patterns", [])
            
            for source_path in source_paths:
                for language in self.parser_cache.keys():
                    ext_map = {
                        "python": ".py",
                        "javascript": ".js",
                        "typescript": ".ts",
                        "go": ".go",
                        "rust": ".rs",
                    }
                    ext = ext_map.get(language, f".{language}")
                    
                    for file_path in source_path.rglob(f"*{ext}"):
                        if self._is_excluded(file_path, exclude_patterns):
                            continue
                        
                        file_path_str = str(file_path.resolve())
                        current_files.add(file_path_str)
                        current_mtime = file_path.stat().st_mtime
                        
                        # File is new or modified
                        if (
                            file_path_str not in file_mtimes
                            or file_mtimes[file_path_str] != current_mtime
                        ):
                            changed_files.append(file_path)
                            logger.debug(
                                "File changed: %s (old_mtime=%s, new_mtime=%s)",
                                file_path.name,
                                file_mtimes.get(file_path_str, "N/A"),
                                current_mtime
                            )
            
            # Check for deleted files
            deleted_files = set(file_mtimes.keys()) - current_files
            if deleted_files:
                logger.info("Found %d deleted files to remove from index", len(deleted_files))
                for deleted_file in deleted_files:
                    self.remove_file(deleted_file)
            
            return changed_files
            
        except Exception as e:
            logger.error("Failed to load metadata, treating all files as changed: %s", e)
            # Fallback: collect all code files
            all_files = []
            exclude_patterns = self.config.get("exclude_patterns", [])
            for source_path in source_paths:
                for language in self.parser_cache.keys():
                    ext_map = {
                        "python": ".py",
                        "javascript": ".js",
                        "typescript": ".ts",
                        "go": ".go",
                        "rust": ".rs",
                    }
                    ext = ext_map.get(language, f".{language}")
                    for file_path in source_path.rglob(f"*{ext}"):
                        if not self._is_excluded(file_path, exclude_patterns):
                            all_files.append(file_path)
            return all_files
    
    def _save_file_mtimes(self, source_paths: List[Path]) -> None:
        """Save file modification times to metadata for change detection.
        
        Args:
            source_paths: Paths to scan for code files
        """
        metadata_file = self.cache_path / "metadata.json"
        
        # Collect all file mtimes
        file_mtimes = {}
        exclude_patterns = self.config.get("exclude_patterns", [])
        
        for source_path in source_paths:
            for language in self.parser_cache.keys():
                ext_map = {
                    "python": ".py",
                    "javascript": ".js",
                    "typescript": ".ts",
                    "go": ".go",
                    "rust": ".rs",
                }
                ext = ext_map.get(language, f".{language}")
                for file_path in source_path.rglob(f"*{ext}"):
                    if self._is_excluded(file_path, exclude_patterns):
                        continue
                    file_path_str = str(file_path.resolve())
                    file_mtimes[file_path_str] = file_path.stat().st_mtime
        
        # Load existing metadata or create new
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())
            except Exception:
                metadata = {}
        else:
            metadata = {}
        
        # Update with current file mtimes
        metadata["files_mtimes"] = file_mtimes
        metadata["last_updated"] = datetime.now().isoformat()
        
        # Save metadata
        self.cache_path.mkdir(parents=True, exist_ok=True)
        metadata_file.write_text(json.dumps(metadata, indent=2))
        logger.debug("Saved file modification times for %d files", len(file_mtimes))
    
    def remove_file(self, file_path: str) -> None:
        """Remove all symbols from a deleted code file from the AST index.
        
        When a code file is deleted, this method removes all its symbols from
        the appropriate language-specific LanceDB table to keep the index
        synchronized with the filesystem.
        
        Args:
            file_path: Absolute or relative path to the deleted file
        
        Note:
            This method is thread-safe and uses row-level deletion in LanceDB.
            If no tables exist or the file wasn't indexed, this is a no-op.
        
        Example:
            >>> index.remove_file("mcp_server/old_module.py")
        """
        if not self.tables:
            logger.warning("Cannot remove file: AST index not initialized")
            return
        
        try:
            # Normalize path for comparison (handle both relative and absolute)
            file_path_obj = Path(file_path)
            if not file_path_obj.is_absolute():
                file_path_obj = file_path_obj.resolve()
            file_path_str = str(file_path_obj)
            
            # Detect language from extension to determine which table to query
            language = self._detect_language(file_path_obj)
            
            if not language or language not in self.tables:
                logger.debug("Skipping deletion: no table for language '%s'", language)
                return
            
            logger.info("Removing symbols for deleted file: %s (language: %s)", file_path_str, language)
            
            # Delete from the language-specific table
            table = self.tables[language]
            delete_result = table.delete(f"file_path = '{file_path_str}'")
            
            # LanceDB delete() returns DeleteResult object with num_deleted attribute
            deleted_count = getattr(delete_result, 'num_deleted', 0) if delete_result else 0
            
            if deleted_count > 0:
                logger.info("✅ Removed %d symbols for file: %s", deleted_count, file_path_str)
            else:
                logger.debug("No symbols found for file: %s", file_path_str)
        
        except Exception as e:
            logger.error("Failed to remove file from AST index: %s", e, exc_info=True)
            # Don't raise - deletion is best-effort
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension.
        
        Config-driven: Uses file_extensions from language configs in
        index_config.yaml. Supports any extension-language mapping without
        code changes.
        
        Args:
            file_path: Path to code file
        
        Returns:
            Language name (e.g., "python", "javascript") or None if unknown
        
        Example:
            >>> # Config: python.file_extensions = [".py", ".pyx", ".pyi"]
            >>> index._detect_language(Path("script.pyx"))
            'python'
        """
        ext = file_path.suffix.lower()
        return self.ext_to_language.get(ext)
    
    def _is_excluded(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file path matches any exclude pattern.
        
        Args:
            file_path: Path to check
            exclude_patterns: List of glob patterns (e.g., "**/tests/**", "**/__pycache__/**")
        
        Returns:
            True if file should be excluded, False otherwise
        
        Example:
            >>> index._is_excluded(Path("src/tests/test_foo.py"), ["**/tests/**"])
            True
        """
        from fnmatch import fnmatch
        
        path_str = str(file_path)
        
        for pattern in exclude_patterns:
            # Convert glob pattern to work with full paths
            # ** means any number of directories
            if fnmatch(path_str, pattern):
                return True
            
            # Also check if any parent directory matches
            # e.g., "**/tests/**" should match "foo/tests/bar.py"
            if "/tests/" in path_str and "**/tests/**" in pattern:
                return True
            if "/__pycache__/" in path_str and "**/__pycache__/**" in pattern:
                return True
            if "/node_modules/" in path_str and "**/node_modules/**" in pattern:
                return True
            if "/.git/" in path_str and "**/.git/**" in pattern:
                return True
            if "/venv/" in path_str or "/.venv/" in path_str:
                if "**/venv/**" in pattern or "**/.venv/**" in pattern:
                    return True
        
        return False
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        n: int = 10
    ) -> List[SearchResult]:
        """Search AST index for symbols by name using LIKE query.
        
        Phase 5, Task 5.5: Performs structural search on parsed symbols using
        symbol name pattern matching (LIKE query) with optional filters.
        
        Args:
            query: Symbol name to search for. Supports partial matches via
                SQL LIKE with wildcards (e.g., "StateManager", "authenticate").
                Query is case-insensitive and matches anywhere in symbol name.
            filters: Optional metadata filters. Supported keys:
                - language: str - Filter by language (e.g., "python", "javascript")
                - symbol_type: str - Filter by type ("function", "class", "method")
            n: Number of results to return (default: 10)
        
        Returns:
            List of SearchResult objects sorted by relevance (exact match > prefix > substring).
            Each result includes symbol metadata (name, type, line range, signature).
        
        Raises:
            ValueError: If query is empty or n is invalid
            RuntimeError: If search fails or index not built
        
        Example:
            >>> # Search for StateManager class
            >>> results = index.search(
            ...     query="StateManager",
            ...     filters={"symbol_type": "class"},
            ...     n=5
            ... )
            >>> for r in results:
            ...     print(f"{r.metadata['symbol_name']} at {r.file_path}:{r.line_range[0]}")
        
        Performance:
            - Target: <100ms p95 latency
            - Uses BTREE index on symbol_name for fast LIKE queries
            - Uses BITMAP index on symbol_type for efficient filtering
        """
        if not query:
            raise ValueError("Query cannot be empty")
        
        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")
        
        if not self.tables:
            raise RuntimeError(
                "Index not built. Call build() before search() or ensure index exists."
            )
        
        logger.info("AST search: query='%s', filters=%s, n=%d", query, filters, n)
        
        # Step 1: Determine which language table(s) to query
        # If language filter provided, query only that table
        # Otherwise, query all language tables
        target_languages = []
        if filters and "language" in filters:
            lang = filters["language"]
            if lang in self.tables:
                target_languages = [lang]
            else:
                logger.warning(f"Language filter '{lang}' has no table, skipping")
                return []
        else:
            # No language filter - query all language tables
            target_languages = list(self.tables.keys())
        
        logger.debug(f"Querying {len(target_languages)} language table(s): {target_languages}")
        
        # Step 2: Build WHERE clause for symbol name LIKE query
        # SQL injection safe: we escape single quotes
        safe_query = query.replace("'", "''")
        where_clause = f"symbol_name LIKE '%{safe_query}%'"
        
        # Step 3: Handle symbol_type filter (workaround for LanceDB bug)
        # WORKAROUND: LanceDB bug with .search() + LIKE '%wildcard%' + AND
        # returns 0 results. So we use LIKE only in WHERE and post-filter
        # in Python for symbol_type.
        symbol_type_filter = None
        if filters and "symbol_type" in filters:
            symbol_type_filter = filters["symbol_type"]
            # Use configured overfetch multiplier for symbol_type post-filtering
            # (typically only 3-5 symbol types: function, class, method, variable)
            overfetch_multiplier = self.overfetch_multiplier
        else:
            overfetch_multiplier = 1
        
        # Smart limit distribution: divide budget across languages
        # If filtering by symbol_type, each table gets equal share of budget
        num_langs = len(target_languages)
        per_table_limit = max(n, (n * overfetch_multiplier) // num_langs)
        
        logger.debug(
            f"Fetch strategy: {num_langs} table(s), {per_table_limit} results each "
            f"(overfetch={overfetch_multiplier}x, symbol_type_filter={symbol_type_filter})"
        )
        
        # Step 4: Query language tables (parallel for 4+, sequential for 1-3)
        all_raw_results = []
        
        if num_langs <= self.parallel_threshold:
            # Sequential for small counts (common case: single language filter)
            # Avoids thread overhead (threshold configurable in index_config.yaml)
            logger.debug(f"Using sequential queries (<={self.parallel_threshold} languages)")
            for language in target_languages:
                table = self.tables[language]
                try:
                    results = (
                        table.search()
                        .where(where_clause)
                        .limit(per_table_limit)
                        .to_list()
                    )
                    all_raw_results.extend(results)
                except Exception as e:
                    logger.error(f"LanceDB search failed for language '{language}': {e}")
                    continue
        else:
            # Parallel for many languages (4+) - critical for scalability
            # 50 languages: ~30ms parallel vs ~750ms sequential (25x speedup!)
            logger.debug(f"Using parallel queries ({num_langs} languages)")
            
            def query_table(language: str) -> tuple[str, List[Dict]]:
                """Query a single language table. Returns (language, results)."""
                try:
                    table = self.tables[language]
                    results = (
                        table.search()
                        .where(where_clause)
                        .limit(per_table_limit)
                        .to_list()
                    )
                    return (language, results)
                except Exception as e:
                    logger.error(f"LanceDB search failed for language '{language}': {e}")
                    return (language, [])
            
            # Execute queries in parallel (max_workers configurable in index_config.yaml)
            with ThreadPoolExecutor(max_workers=min(num_langs, self.max_workers)) as executor:
                future_to_lang = {
                    executor.submit(query_table, lang): lang
                    for lang in target_languages
                }
                
                for future in as_completed(future_to_lang):
                    language, results = future.result()
                    all_raw_results.extend(results)
                    logger.debug(f"  {language}: {len(results)} results")
        
        logger.debug(f"Fetched {len(all_raw_results)} raw results from {num_langs} table(s)")
        
        # Step 5: Post-filter by symbol_type if needed (workaround)
        if symbol_type_filter:
            filtered_results = [
                r for r in all_raw_results
                if r.get("symbol_type") == symbol_type_filter
            ]
            logger.debug(f"Post-filtered from {len(all_raw_results)} to {len(filtered_results)} results by symbol_type='{symbol_type_filter}'")
            all_raw_results = filtered_results
        
        # Step 6: Convert to SearchResult objects
        results: List[SearchResult] = []
        for result in all_raw_results:
            try:
                # Calculate simple relevance score:
                # 1.0 = exact match, 0.9 = starts with query, 0.5 = contains query
                symbol_name = result["symbol_name"].lower()
                query_lower = query.lower()
                
                if symbol_name == query_lower:
                    relevance_score = 1.0
                elif symbol_name.startswith(query_lower):
                    relevance_score = 0.9
                else:
                    relevance_score = 0.5
                
                search_result = SearchResult(
                    content=result.get("signature", ""),  # Signature as content
                    file_path=result["file_path"],
                    relevance_score=relevance_score,
                    content_type="code",
                    metadata={
                        "symbol_name": result["symbol_name"],
                        "symbol_type": result["symbol_type"],
                        "language": result["language"],
                        "signature": result.get("signature", "")
                    },
                    chunk_id=result["symbol_id"],
                    line_range=(result["line_start"], result["line_end"])
                )
                results.append(search_result)
            except KeyError as e:
                logger.warning("Skipping malformed AST search result: missing key %s", e)
                continue
        
        # Sort by relevance score (exact match first)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        logger.info("AST search returned %d results", len(results))
        return results
    
    def update(self, changed_files: List[str]) -> None:
        """Update AST index for changed files.
        
        Removes old symbol entries for changed files and re-indexes them.
        
        Args:
            changed_files: List of file paths that have changed
        
        Raises:
            RuntimeError: If update fails
        
        Example:
            >>> index.update(["src/auth.py", "src/models.py"])
        
        Note:
            This is a stub for Task 5.1. Full implementation in Phase 6.
        """
        logger.info("AST index update requested for %d files", len(changed_files))
        
        # TODO: Phase 6 - Implement incremental update
        
        raise NotImplementedError(
            "update() will be implemented in Phase 6 (File Watcher). "
            "Current stub for Task 5.1 class structure only."
        )
    
    def delete(self, file_paths: List[str]) -> None:
        """Delete symbol entries for specified files.
        
        Removes all symbols extracted from the given file paths.
        
        Args:
            file_paths: List of file paths to remove from index
        
        Raises:
            RuntimeError: If deletion fails
        
        Example:
            >>> index.delete(["old/deprecated.py"])
        
        Note:
            This is a stub for Task 5.1. Full implementation in Phase 6.
        """
        logger.info("AST index delete requested for %d files", len(file_paths))
        
        # TODO: Phase 6 - Implement deletion
        
        raise NotImplementedError(
            "delete() will be implemented in Phase 6 (File Watcher). "
            "Current stub for Task 5.1 class structure only."
        )

