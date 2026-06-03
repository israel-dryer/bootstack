import bootstack as bs


def hero():
    with bs.App(title="Form", size=(680, 360), padding=20) as app:
        bs.Form(
            data={
                "name":   "Alice Smith",
                "email":  "alice@example.com",
                "age":    30,
                "active": True,
            },
            fill="x",
        )

    app.run()


def columns():
    with bs.App(title="Form — Multiple Columns", size=(680, 220), padding=20) as app:
        bs.Form(
            data={
                "street": "123 Main St",
                "city":   "Springfield",
                "state":  "IL",
                "zip":    "62701",
            },
            col_count=2,
            fill="x",
        )

    app.run()


def grouped():
    with bs.App(title="Form — Grouped Fields", size=(680, 230), padding=20) as app:
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
            fill="x",
        )

    app.run()


def tabbed():
    with bs.App(title="Form — Tabbed Layout", size=(680, 230), padding=20) as app:
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
            fill="x",
        )

    app.run()


SCENES = {
    "hero":    hero,
    "columns": columns,
    "grouped": grouped,
    "tabbed":  tabbed,
}
