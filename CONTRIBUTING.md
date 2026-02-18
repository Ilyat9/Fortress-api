# Contributing to Fortress

Спасибо за интерес к вкладу в проект Fortress!

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/Fortress.git`
3. Navigate to the project: `cd Fortress`
4. Install dependencies: `poetry install --with dev`
5. Create a feature branch: `git checkout -b feature/amazing-feature`

## Code Style

### Linting

Run the linter before committing:

```bash
poetry run ruff check app tests
```

### Formatting

Format your code before committing:

```bash
poetry run ruff format app tests
```

### Type Checking

Run type checking:

```bash
poetry run mypy app
```

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_todos.py

# Run with verbose output
poetry run pytest -v
```

### Test Results

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database interactions
- **Coverage**: Full code coverage

## Commit Messages

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(scope): description

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Example Commits

```bash
feat(todos): add priority filtering

Implement priority-based filtering for todo list endpoint

- Add priority filter parameter
- Add priority ordering in database queries
- Add priority-related metrics

Closes #123
```

## Pull Requests

1. Ensure all tests pass
2. Run code quality checks
3. Write clear commit messages
4. Update documentation if needed
5. Open a pull request with a detailed description

### PR Checklist

- [ ] All tests pass
- [ ] Code is properly formatted
- [ ] Type checking passes
- [ ] Commit messages follow conventions
- [ ] Documentation is updated
- [ ] No console warnings or errors
- [ ] Code is reviewed

## Code of Conduct

Please be respectful and constructive in all interactions.

## Questions?

Open an issue or contact the maintainers.
