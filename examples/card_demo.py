"""
Card Widget Demo

Demonstrates the Card widget — a bordered, elevated container
for grouping related content.
"""

import bootstack as bs


def main():
    app = bs.App(theme='rose-light', title='Card Demo', minsize=(600, 600))

    container = bs.Frame(app, padding=20)
    container.pack(fill='both', expand=True)

    bs.Label(container, text='Card Widget Demo', font='heading-xl').pack(
        anchor='w', pady=(0, 16)
    )

    # Basic card
    card1 = bs.Card(container, padding=20)
    card1.pack(fill='x', pady=(0, 12))
    bs.Label(card1, text='Basic Card', font='heading-md').pack(anchor='w')
    bs.Label(card1, text='A simple card with text content.').pack(anchor='w', pady=(4, 0))

    # Card with interactive content
    card2 = bs.Card(container, padding=20)
    card2.pack(fill='x', pady=(0, 12))
    bs.Label(card2, text='User Profile', font='heading-md').pack(anchor='w')
    bs.Label(card2, text='Configure your account settings below.').pack(
        anchor='w', pady=(4, 12)
    )
    row = bs.Frame(card2)
    row.pack(fill='x')
    bs.Label(row, text='Name').pack(side='left', padx=(0, 10))
    bs.Entry(row).pack(side='left', fill='x', expand=True)

    row2 = bs.Frame(card2)
    row2.pack(fill='x', pady=(8, 0))
    bs.Label(row2, text='Email').pack(side='left', padx=(0, 12))
    bs.Entry(row2).pack(side='left', fill='x', expand=True)

    bs.Button(card2, text='Save', accent='primary').pack(anchor='e', pady=(12, 0))

    # Side-by-side cards
    row3 = bs.Frame(container)
    row3.pack(fill='both', expand=True)

    card3 = bs.Card(row3, padding=20)
    card3.pack(side='left', fill='both', expand=True, padx=(0, 6))
    bs.Label(card3, text='Stats', font='heading-md').pack(anchor='w')
    bs.Label(card3, text='Total items: 42').pack(anchor='w', pady=(8, 0))
    bs.Label(card3, text='Active: 38').pack(anchor='w')
    bs.Progressbar(card3, value=90).pack(fill='x', pady=(8, 0))

    card4 = bs.Card(row3, padding=20)
    card4.pack(side='left', fill='both', expand=True, padx=(6, 0))
    bs.Label(card4, text='Status', font='heading-md').pack(anchor='w')
    bs.Label(card4, text='All systems operational.').pack(anchor='w', pady=(8, 0))
    bs.CheckButton(card4, text='Enable notifications').pack(anchor='w', pady=(8, 0))
    bs.CheckButton(card4, text='Auto-update').pack(anchor='w')

    app.mainloop()


if __name__ == '__main__':
    main()
