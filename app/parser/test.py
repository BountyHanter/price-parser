from app.parser.create_tasks import read_tasks_from_excel
from app.parser.memory_structure import build_memory_structure


tasks = read_tasks_from_excel(
    "template.xlsx",
    start_row=3
)

data = build_memory_structure("template.xlsx", tasks)

print(len(data["rows"]))
first_key = next(iter(data["rows"]))
print(first_key)
print(data["rows"][first_key])