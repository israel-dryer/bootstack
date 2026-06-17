import bootstack as bs


def hero():
    with bs.App(title="Form", minsize=(720, 1), padding=20) as app:
        bs.Form(
            data={
                "name":   "Alice Smith",
                "email":  "alice@example.com",
                "age":    30,
                "active": True,
            },
            horizontal="stretch",
        )

    app.run()


def columns():
    with bs.App(title="Form — Multiple Columns", minsize=(720, 1), padding=20) as app:
        bs.Form(
            data={
                "street": "123 Main St",
                "city":   "Springfield",
                "state":  "IL",
                "zip":    "62701",
            },
            col_count=2,
            horizontal="stretch",
        )

    app.run()


def grouped():
    with bs.App(title="Form — Grouped Fields", minsize=(720, 1), padding=20) as app:
        bs.Form(
            items=[
                bs.GroupItem(
                    label="Contact",
                    col_count=2,
                    items=[
                        bs.FieldItem(key="first_name", label="First Name"),
                        bs.FieldItem(key="last_name",  label="Last Name"),
                        bs.FieldItem(key="email",      label="Email"),
                        bs.FieldItem(key="phone",      label="Phone"),
                    ],
                ),
            ],
            horizontal="stretch",
        )

    app.run()


def tabbed():
    with bs.App(title="Form — Tabbed Layout", minsize=(720, 1), padding=20) as app:
        bs.Form(
            items=[
                bs.TabsItem(tabs=[
                    bs.TabItem(
                        label="Account",
                        items=[
                            bs.FieldItem(key="username", label="Username"),
                            bs.FieldItem(key="password", label="Password", dtype="password"),
                        ],
                    ),
                    bs.TabItem(
                        label="Profile",
                        items=[
                            bs.FieldItem(key="bio",     label="Bio",     editor="textarea"),
                            bs.FieldItem(key="website", label="Website"),
                        ],
                    ),
                ]),
            ],
            horizontal="stretch",
        )

    app.run()


SCENES = {
    "hero":    hero,
    "columns": columns,
    "grouped": grouped,
    "tabbed":  tabbed,
}
