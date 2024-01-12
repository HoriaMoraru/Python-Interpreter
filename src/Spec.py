SPEC = [
    ('LITERAL_NUMBER', r'[0-9]+'),
    ('LAMBDA', r'lambda'),
    ('LITERAL', r'([a-z]|[A-Z])+'),
    ('WHITE_SPACE', r'\ +'),
    ('TAB', '\t+'),
    ("NEW_LINE", '\n+'),
    ('EMPTY_LIST', r'\(\)'),
    ('SUM', r'+'),
    ('CONCAT', r'++'),
    ('OPEN_PARENTHESIS', r'\('),
    ('CLOSED_PARENTHESIS', r'\)'),
    ('FUNCTION_DEFINITION', r':')
]
