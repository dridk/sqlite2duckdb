from sqlite2duckdb.sqlite_to_duckdb import _brackets_to_quotes


def test_translates_bracket_identifiers():
    assert (
        _brackets_to_quotes("CREATE INDEX [i] ON [my table] ([a], [b])")
        == 'CREATE INDEX "i" ON "my table" ("a", "b")'
    )


def test_leaves_string_literals_alone():
    assert (
        _brackets_to_quotes("CREATE INDEX [i] ON t (x) WHERE y = 'a [b] c'")
        == "CREATE INDEX \"i\" ON t (x) WHERE y = 'a [b] c'"
    )


def test_leaves_already_quoted_identifiers_alone():
    assert _brackets_to_quotes('CREATE INDEX i ON "a [b]" (c)') == (
        'CREATE INDEX i ON "a [b]" (c)'
    )


def test_escapes_double_quotes_inside_brackets():
    assert _brackets_to_quotes('SELECT [a"b]') == 'SELECT "a""b"'


def test_leaves_unterminated_bracket_alone():
    assert _brackets_to_quotes("SELECT [oops") == "SELECT [oops"
