TEMPLATE = """You are a precise information extraction system.
Extract data from the {doc_type} below and return ONLY valid JSON that matches the schema.
Use null for missing optional fields. Never invent values.

### Example
Input:
{example_input}
Output:
{example_output}

### Now process this {doc_type}
Input:
{text}
Output:"""

EXAMPLES = {
    "invoice": {
        "input": "INVOICE #A-17, 2025-03-01. From: Acme Ltd. To: Bob. 2 x Widget @ 10.00 = 20.00. Tax 2.00. Total 22.00 USD",
        "output": '{"invoice_number":"A-17","date":"2025-03-01","vendor":"Acme Ltd","customer":"Bob","items":[{"description":"Widget","quantity":2,"unit_price":10.0,"total":20.0}],"subtotal":20.0,"tax":2.0,"total_amount":22.0,"currency":"USD"}',
    },
    "resume": {
        "input": "Jane Roe, jane@mail.com. Python developer. Skills: Python, SQL. Worked at Foo Inc as Developer (2021-2023). BSc CS, MIT (2017-2021).",
        "output": '{"full_name":"Jane Roe","email":"jane@mail.com","phone":null,"summary":"Python developer","skills":["Python","SQL"],"experience":[{"company":"Foo Inc","role":"Developer","period":"2021-2023","description":null}],"education":[{"institution":"MIT","degree":"BSc CS","period":"2017-2021"}]}',
    },
}


def build_prompt(doc_type: str, text: str) -> str:
    ex = EXAMPLES[doc_type]
    return TEMPLATE.format(
        doc_type=doc_type,
        example_input=ex["input"],
        example_output=ex["output"],
        text=text,
    )