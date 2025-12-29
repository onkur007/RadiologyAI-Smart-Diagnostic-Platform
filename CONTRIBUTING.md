# Contributing Guidelines

Thank you for your interest in contributing to the AI-Powered Radiology Assistant! This document provides guidelines for contributing to the project.

## 🎯 Ways to Contribute

### 1. Report Bugs
- Use GitHub Issues to report bugs
- Include detailed description of the bug
- Provide steps to reproduce
- Include error messages and logs
- Specify your environment (OS, Python version, etc.)

### 2. Suggest Features
- Open a GitHub Issue with the "feature request" label
- Clearly describe the feature and its benefits
- Explain the use case
- Consider implementation approach

### 3. Improve Documentation
- Fix typos and grammar
- Add examples and clarifications
- Create tutorials and guides
- Improve code comments

### 4. Submit Code
- Fix bugs
- Implement new features
- Optimize performance
- Add tests

## 📝 Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/RadiologyAI.git
   cd RadiologyAI
   ```

3. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔧 Code Standards

### Python Style
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Example:
```python
def analyze_scan(scan_id: int, db: Session) -> Dict[str, Any]:
    """
    Analyze a radiology scan using AI.
    
    Args:
        scan_id: ID of the scan to analyze
        db: Database session
        
    Returns:
        Dict containing analysis results
        
    Raises:
        HTTPException: If scan not found
    """
    # Implementation here
    pass
```

### API Endpoints
- Use RESTful conventions
- Include clear docstrings
- Validate inputs with Pydantic
- Handle errors properly
- Return appropriate status codes

### Database
- Use SQLAlchemy ORM
- Define relationships clearly
- Add indexes where needed
- Use migrations for schema changes

## ✅ Before Submitting

1. **Test your changes**:
   ```bash
   pytest tests/
   ```

2. **Check code style**:
   ```bash
   flake8 app/
   ```

3. **Update documentation** if needed

4. **Add tests** for new features

5. **Commit with clear message**:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

## 📤 Pull Request Process

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub

3. **Fill in PR template** with:
   - Description of changes
   - Related issue numbers
   - Testing done
   - Screenshots (if applicable)

4. **Wait for review**
   - Address reviewer comments
   - Make requested changes
   - Keep PR up to date with main branch

## 🧪 Testing Guidelines

### Write Tests For:
- New features
- Bug fixes
- Edge cases
- Error handling

### Test Structure:
```python
def test_feature_name():
    """Test description"""
    # Arrange
    setup_data()
    
    # Act
    result = function_to_test()
    
    # Assert
    assert result == expected_value
```

## 📚 Documentation Guidelines

### Code Comments
- Explain "why", not "what"
- Keep comments up to date
- Use clear, concise language

### Docstrings
- Include for all public functions
- Describe parameters and return values
- Mention exceptions raised

### README/Guides
- Use clear headings
- Include code examples
- Add screenshots when helpful
- Keep it beginner-friendly

## 🎯 Priority Areas

Current priorities for contributions:
1. Bug fixes
2. Test coverage improvement
3. Documentation enhancements
4. Performance optimizations
5. New AI features
6. UI/Frontend development

## ❓ Questions?

- Check existing documentation
- Search existing issues
- Ask in discussions
- Contact maintainers

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🎉
