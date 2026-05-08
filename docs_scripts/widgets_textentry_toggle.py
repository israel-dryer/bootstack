
import bootstack as bs

app = bs.App()

def run_search(): pass

search = bs.TextEntry(app, label="Find")

match_case = bs.BooleanVar(value=False)
search.insert_addon(
    bs.CheckButton,
    position="after",
    text="Aa",
    variable=match_case,
    name="case-toggle",
)

app.mainloop()