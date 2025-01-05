import pytest
from bs4 import BeautifulSoup
from html_fragmenter.msg_split import split_message, MAX_LEN
from html_fragmenter.exceptions import FragmentationError

def read_test_file(filename):
    with open(f"tests/data/{filename}", "r", encoding="utf-8") as f:
        return f.read()

def is_valid_html(html_string):
    """Check if HTML string is valid by parsing it with BeautifulSoup."""
    try:
        soup = BeautifulSoup(html_string, 'html.parser')
        return True
    except:
        return False

def test_simple_split():
    """Test splitting simple HTML with basic tags."""
    html = read_test_file("simple.html")
    fragments = list(split_message(html, max_len=200))
    
    # Check number of fragments
    assert len(fragments) > 0, "Should create at least one fragment"
    
    # Check each fragment
    for fragment in fragments:
        # Verify fragment size
        assert len(fragment) <= 200, f"Fragment exceeds max length: {len(fragment)}"
        # Verify HTML validity
        assert is_valid_html(fragment), "Fragment should be valid HTML"
        # Verify tag closure
        assert fragment.count('<') == fragment.count('>'), "All tags should be properly closed"

def test_nested_tags():
    """Test splitting HTML with nested tag structure."""
    html = read_test_file("nested.html")
    fragments = list(split_message(html, max_len=300))
    
    # Check fragments
    for fragment in fragments:
        # Verify size
        assert len(fragment) <= 300, "Fragment should not exceed max length"
        # Verify HTML validity
        assert is_valid_html(fragment), "Fragment should be valid HTML"
        
        # Check tag nesting
        soup = BeautifulSoup(fragment, 'html.parser')
        # Verify strong tags are properly nested in their parents
        for strong in soup.find_all('strong'):
            assert strong.parent is not None, "Strong tags should have parent elements"
        # Verify code tags are properly nested
        for code in soup.find_all('code'):
            assert code.parent is not None, "Code tags should have parent elements"

def test_complex_document():
    """Test splitting complex HTML document with various tags and attributes."""
    html = read_test_file("complex.html")
    fragments = list(split_message(html, max_len=500))
    
    # Verify fragments
    for fragment in fragments:
        # Check size
        assert len(fragment) <= 500, "Fragment should not exceed max length"
        # Verify HTML validity
        assert is_valid_html(fragment), "Fragment should be valid HTML"
        
        # Parse fragment
        soup = BeautifulSoup(fragment, 'html.parser')
        
        # Check attribute preservation
        for tag in soup.find_all(True):
            if 'class' in tag.attrs:
                assert isinstance(tag['class'], list), "Class attributes should be preserved"
            if 'href' in tag.attrs:
                assert tag['href'].startswith('http'), "href attributes should be preserved"
            if 'id' in tag.attrs:
                assert tag['id'].startswith('U'), "ID attributes should be preserved"

def test_max_len_exceeded():
    """Test handling of content that cannot be split within max_len."""
    # Create HTML with a very long non-splittable content
    long_html = f'<p>{"x" * (MAX_LEN + 100)}</p>'
    
    # Should raise FragmentationError
    with pytest.raises(FragmentationError):
        list(split_message(long_html))

def test_empty_input():
    """Test handling of empty input."""
    fragments = list(split_message(""))
    assert len(fragments) == 0, "Empty input should produce no fragments"

def test_whitespace_handling():
    """Test proper handling of whitespace."""
    html = "  <p>  Some    spaced    content  </p>  "
    fragments = list(split_message(html, max_len=100))
    assert len(fragments) > 0, "Should handle whitespace correctly"
    # Check whitespace normalization
    assert not any(f.startswith('  ') for f in fragments), "Should not start with multiple spaces"
    assert not any(f.endswith('  ') for f in fragments), "Should not end with multiple spaces"

def test_tag_attributes():
    """Test preservation of tag attributes."""
    html = read_test_file("complex.html")
    fragments = list(split_message(html, max_len=400))
    
    for fragment in fragments:
        soup = BeautifulSoup(fragment, 'html.parser')
        # Check class attributes
        class_tags = soup.find_all(class_=True)
        for tag in class_tags:
            assert 'class' in tag.attrs, "Class attributes should be preserved"
        
        # Check href attributes
        links = soup.find_all('a')
        for link in links:
            assert 'href' in link.attrs, "href attributes should be preserved"

def test_unicode_handling():
    """Test handling of unicode characters."""
    html = '<div>🚀 Test with emoji and русский текст</div>'
    fragments = list(split_message(html, max_len=100))
    assert len(fragments) > 0, "Should handle unicode correctly"
    assert '🚀' in fragments[0], "Should preserve emoji"
    assert 'русский' in fragments[0], "Should preserve non-Latin characters"