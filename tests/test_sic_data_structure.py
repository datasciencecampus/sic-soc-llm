import pytest

from sic_soc_llm.data_models import sic_hierarchy


def test_sic_code_alpha_code_is_string_else_error():
    with pytest.raises(TypeError):
        sic_hierarchy.SicCode(123123)


def test_sic_code_alpha_code_starts_with_letter_else_error():
    with pytest.raises(ValueError):
        sic_hierarchy.SicCode("123123")


def test_sic_code_alpha_code_starts_with_uppercase_else_error():
    with pytest.raises(ValueError):
        sic_hierarchy.SicCode("a12312")


def test_sic_code_alpha_code_short_raises_error():
    with pytest.raises(ValueError):
        sic_hierarchy.SicCode("a123")


def test_sic_code_alpha_code_long_raises_error():
    with pytest.raises(ValueError):
        sic_hierarchy.SicCode("a123123")


@pytest.mark.parametrize(
    "code,expected_digits",
    [
        ("Axxxxx", 1),
        ("A12xxx", 2),
        ("A123xx", 3),
        ("A1234x", 4),
        ("A12345", 5),
    ],
)
def test_sic_code_alpha_code_digits_parsed(code, expected_digits):
    # Given
    alpha_code = code

    # When
    code = sic_hierarchy.SicCode(alpha_code)

    # Then
    assert code.n_digits == expected_digits


@pytest.mark.parametrize(
    "code,expected_level_name",
    [
        ("Axxxxx", "section"),
        ("A12xxx", "division"),
        ("A123xx", "group"),
        ("A1234x", "class"),
        ("A12345", "subclass"),
    ],
)
def test_sic_code_alpha_code_levels_correct(code, expected_level_name):
    # Given
    alpha_code = code

    # When
    code = sic_hierarchy.SicCode(alpha_code)

    # Then
    assert code.level_name == expected_level_name


@pytest.mark.parametrize(
    "code,expected_formatted_code",
    [
        ("Axxxxx", "A"),
        ("A12xxx", "12"),
        ("A123xx", "12.3"),
        ("A1234x", "12.34"),
        ("A12345", "12.34/5"),
    ],
)
def test_sic_code_alpha_code_readable_code_correct(code, expected_formatted_code):
    # Given
    alpha_code = code

    # When
    code = sic_hierarchy.SicCode(alpha_code)

    # Then
    assert str(code) == expected_formatted_code


def test_sic_code_alpha_single_digit_raises_error():
    with pytest.raises(ValueError):
        sic_hierarchy.SicCode("A1xxxx")


@pytest.mark.parametrize(
    "section,code,level,expected_formatted_code",
    [
        ("A", "A", "section", "A"),
        ("A", "12", "division", "12"),
        ("A", "123", "group", "12.3"),
        ("A", "1234", "class", "12.34"),
        ("A", "12340", "class", "12.34"),
        ("A", "12345", "subclass", "12.34/5"),
    ],
)
def test_sic_code_from_section_code_level_valid_cases(
    section, code, level, expected_formatted_code
):
    # When
    code = sic_hierarchy.SicCode.from_section_code_level(section, code, level)

    # Then
    assert str(code) == expected_formatted_code


def test_sic_code_from_section_code_level_invalid_class():
    # Given
    section = "A"
    code = "12341"
    level = "class"

    with pytest.raises(ValueError):
        sic_hierarchy.SicCode.from_section_code_level(section, code, level)


@pytest.mark.parametrize(
    "section,code,level",
    [
        ("A", "A", "division"),
        ("A", "A", "group"),
        ("A", "A", "class"),
        ("A", "A", "subclass"),
        ("A", "12", "section"),
        ("A", "12", "group"),
        ("A", "12", "class"),
        ("A", "12", "subclass"),
        ("A", "123", "section"),
        ("A", "123", "division"),
        ("A", "123", "class"),
        ("A", "123", "subclass"),
        ("A", "1234", "section"),
        ("A", "1234", "division"),
        ("A", "1234", "group"),
        ("A", "1234", "subclass"),
        ("A", "12340", "section"),
        ("A", "12340", "division"),
        ("A", "12340", "group"),
        ("A", "12345", "section"),
        ("A", "12345", "division"),
        ("A", "12345", "group"),
        ("A", "12345", "class"),
    ],
)
def test_sic_code_from_section_code_level_invalid_levels_raise_error(
    section, code, level
):
    with pytest.raises(ValueError):
        sic_hierarchy.SicCode.from_section_code_level(section, code, level)


def test_sic_code_from_section_code_level_invalid_section_code_raises_error():
    # Given
    section = "A"
    code = "B"
    level = "section"

    with pytest.raises(ValueError):
        sic_hierarchy.SicCode.from_section_code_level(section, code, level)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("&#34;", '"'),
        ("some text &#34;here&#34;", 'some text "here"'),
        ('mixed "some" text &#34;here&#34;', 'mixed "some" text "here"'),
    ],
)
def test_clean_text_with_html_unescapes(text, expected):
    # When
    clean_text = sic_hierarchy._clean_text(text)

    # Then
    assert clean_text == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        (", see ##12.12", ""),
        ("Some text, see ##12.12", "Some text"),
        ("Some text, See ##12.12", "Some text"),
        ("Some text, see ##12.12/1", "Some text"),
        ("some text,see ##12.12", "some text"),
        ("see ##12.12", ""),
        ("##12.12", ""),
        ("some text ##12.12 different", "some text  different"),
        (", see division ##85", ""),
        ("##85", ""),
        ("some text, see division ##25", "some text"),
        ("see divisions ##12", ""),
        ("some text, see division ##25, see ##12.12, see divisions ##12", "some text"),
    ],
)
def test_clean_text_with_see_gets_trimmed(text, expected):
    # When
    clean_text = sic_hierarchy._clean_text(text)

    # Then
    assert clean_text == expected
