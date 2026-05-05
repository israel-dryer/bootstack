from bootstack.datasource import MemoryDataSource

# Create datasource with page size
ds = MemoryDataSource(page_size=10)

# Load data
ds.set_data([
    {"name": "Alice", "age": 30, "department": "Engineering"},
    {"name": "Bob", "age": 25, "department": "Sales"},
    {"name": "Charlie", "age": 35, "department": "Engineering"},
])

# Get first page
page = ds.get_page(0)

print(page)