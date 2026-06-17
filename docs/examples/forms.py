"""Form — feature demo.

Demonstrates auto-generated fields, multi-column layout, grouped fields,
and tabbed layouts.

Run with:
    python docs/examples/forms.py
"""
import bootstack as bs

with bs.App(title="Form Demo", size=(700, 780), padding=20, gap=12) as app:

    # Auto-generated fields from a data dict
    bs.Label("Auto-Generated Fields", font="heading-sm")
    bs.Form(
        data={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "age": 30,
            "active": True,
        },
        horizontal="stretch",
    )

    # Multi-column layout
    bs.Label("Multiple Columns", font="heading-sm")
    bs.Form(
        data={
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
        },
        col_count=2,
        horizontal="stretch",
    )

    # Grouped fields with GroupItem
    bs.Label("Grouped Fields", font="heading-sm")
    bs.Form(
        items=[
            bs.GroupItem(
                label="Contact",
                col_count=2,
                items=[
                    bs.FieldItem(key="first_name", label="First Name"),
                    bs.FieldItem(key="last_name",  label="Last Name"),
                    bs.FieldItem(key="email",       label="Email"),
                    bs.FieldItem(key="phone",       label="Phone"),
                ],
            ),
        ],
        horizontal="stretch",
    )

    # Tabbed layout with TabsItem
    bs.Label("Tabbed Layout", font="heading-sm")
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