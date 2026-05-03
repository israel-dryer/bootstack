"""Simple demonstration of PackFrame and GridFrame layout containers."""

import bootstack as bs


def main():
    app = bs.App(title="Layout Demo", theme="flatly", size=(600, 400))

    # Simple PackFrame test
    bs.Label(app, text="PackFrame (horizontal):").pack(anchor="w", padx=10, pady=(10, 5))

    pack_frame = bs.PackFrame(app, direction="horizontal", gap=10)
    pack_frame.pack(fill="x", padx=10, pady=(0, 20))

    for i in range(4):
        bs.Button(pack_frame, text=f"Button {i + 1}").pack()

    # Simple GridFrame test
    bs.Label(app, text="GridFrame (2x2):").pack(anchor="w", padx=10, pady=(10, 5))

    grid_frame = bs.GridFrame(app, rows=2, columns=2, gap=10, sticky_items="nsew")
    grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))

    for row in range(2):
        for col in range(2):
            bs.Button(grid_frame, text=f"({row}, {col})").grid(row=row, column=col)

    app.mainloop()


if __name__ == "__main__":
    main()
