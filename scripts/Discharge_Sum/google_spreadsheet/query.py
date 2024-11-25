chunk = """
LAMBDA(sheet_name,
    LAMBDA(rows,
    MAP(
        SEQUENCE(rows),
        LAMBDA(row, {sheet_name, INDIRECT("'" & sheet_name & "'!A" & row+1 & ":BD" & row+1)})
    )
    )(COUNTA(INDIRECT("'" & sheet_name & "'!A:BD"))-1)
)("Form Responses """

def chunk_i(i): return chunk + f'{i}");'

def write_all(END):
    empt = ""
    for i in range(1, END):
        empt += chunk_i(i)

    res = """=QUERY(
    {
        {"Form no", INDIRECT("'Form Responses 1'!A1:BD1")};""" + empt + """
        LAMBDA(sheet_name,
        LAMBDA(rows,
            MAP(
            SEQUENCE(rows),
            LAMBDA(row, {sheet_name, INDIRECT("'" & sheet_name & "'!A" & row+1 & ":BD" & row+1)})
            )
        )(COUNTA(INDIRECT("'" & sheet_name & "'!A:BD"))-1)
        )("Form Responses """ + f'{END}")' + """
    },
    "select * where Col2 is not null",
    1
    )
    """
    return res
print(write_all(944))