"""
Demo for the ListView widget

This demo showcases the ListView widget's features including:
- Virtual scrolling for efficient rendering of large datasets
- Multiple selection modes (single, multi, none)
- Selection controls (checkboxes/radio buttons)
- Remove functionality
- Focus states
- Interactive features (chevron, drag handles)
"""

import bootstack as bs
from bootstack.widgets.composites import ListView, MemoryDataSource


def create_sample_data(count=1000):
    """Create sample data for the ListView."""
    return [
        {
            'id': i,
            'title': f'Item {i}',
            'text': f'This is the description for item {i}',
            'caption': f'Created: 2024-0{(i % 9) + 1}-{(i % 28) + 1:02d}'
        }
        for i in range(count)
    ]


def main():
    """Main demo application."""
    root = bs.App(title="ListView Widget Demo", theme="docs-dark", size=(1200, 700))
    root.geometry("1200x700")

    # Main container
    main_container = bs.Frame(root, padding=20)
    main_container.pack(fill='both', expand=True)

    # Title
    title = bs.Label(
        main_container,
        text="ListView Widget Demo",
        font=('Helvetica', 18, 'bold')
    )
    title.pack(pady=(0, 15), anchor='w')

    # Create three columns for different ListView examples
    columns = bs.Frame(main_container)
    columns.pack(fill='both', expand=True)

    # Column 1: Simple ListView
    col1 = bs.Frame(columns, padding=10)
    col1.pack(side='left', fill='both', expand=True)

    bs.Label(col1, text="Simple ListView", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0, 5))
    bs.Label(col1, text="Basic list with 1000 items", font=('Helvetica', 9)).pack(anchor='w', pady=(0, 10))

    simple_data = create_sample_data(1000)
    simple_list = ListView(
        col1,
        items=simple_data,
        show_separator=True,
        selection_mode='single',
    )
    simple_list.pack(fill='both', expand=True)

    # Add counter for simple list
    simple_label = bs.Label(col1, text=f"Total: {len(simple_data)} items")
    simple_label.pack(pady=(5, 0), anchor='w')

    # Column 2: Multi-select ListView
    col2 = bs.Frame(columns, padding=10)
    col2.pack(side='left', fill='both', expand=True)

    bs.Label(col2, text="Multi-Select ListView", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0, 5))
    bs.Label(col2, text="Select multiple items", font=('Helvetica', 9)).pack(anchor='w', pady=(0, 10))

    multi_data = create_sample_data(500)
    multi_list = ListView(
        col2,
        items=multi_data,
        selection_mode='multi',
        show_selection_controls=True,
        enable_focus=True,
        show_separator=True,
        show_chevron=True
    )
    multi_list.pack(fill='both', expand=True)

    # Add controls for multi-select list
    multi_controls = bs.Frame(col2)
    multi_controls.pack(pady=(5, 0), fill='x')

    selected_label = bs.Label(multi_controls, text="Selected: 0")
    selected_label.pack(side='left')

    def update_multi_selection(event=None):
        selected = multi_list.get_selected()
        selected_label.config(text=f"Selected: {len(selected)}")

    multi_list.bind('<<SelectionChange>>', update_multi_selection)

    bs.Button(
        multi_controls,
        text="Select All",
        command=lambda: (multi_list.select_all(), update_multi_selection()),
        accent='secondary',
        variant='outline',
        width=12
    ).pack(side='right', padx=(5, 0))

    bs.Button(
        multi_controls,
        text="Clear",
        command=lambda: (multi_list.clear_selection(), update_multi_selection()),
        accent='secondary',
        variant='outline',
        width=12
    ).pack(side='right')

    # Column 3: Feature-rich ListView
    col3 = bs.Frame(columns, padding=10)
    col3.pack(side='left', fill='both', expand=True)

    bs.Label(col3, text="Feature-rich ListView", font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0, 5))
    bs.Label(col3, text="With remove & single-select", font=('Helvetica', 9)).pack(anchor='w', pady=(0, 10))

    feature_data = create_sample_data(300)
    feature_list = ListView(
        col3,
        items=feature_data,
        selection_mode='single',
        show_selection_controls=True,
        enable_focus=True,
        show_separator=True,
        enable_dragging=True,
        enable_removing=True,
        show_chevron=True
    )
    feature_list.pack(fill='both', expand=True)

    # Add controls for feature list
    feature_controls = bs.Frame(col3)
    feature_controls.pack(pady=(5, 0), fill='x')

    feature_label = bs.Label(feature_controls, text=f"Total: {len(feature_data)} items")
    feature_label.pack(side='left')

    def update_feature_count(event=None):
        datasource = feature_list.get_datasource()
        count = datasource.total_count()
        feature_label.config(text=f"Total: {count} items")

    feature_list.bind('<<ItemDelete>>', update_feature_count)

    bs.Button(
        feature_controls,
        text="Add Item",
        command=lambda: (
            feature_list.insert_item({
                'title': f'New Item {feature_list.get_datasource().total_count() + 1}',
                'text': 'Newly added item',
                'caption': 'Just now'
            }),
            update_feature_count()
        ),
        accent='success',
        variant='outline',
        width=12
    ).pack(side='right', padx=(5, 0))

    bs.Button(
        feature_controls,
        text="Scroll Top",
        command=feature_list.scroll_to_top,
        accent='secondary',
        variant='outline',
        width=12
    ).pack(side='right', padx=(5, 0))

    bs.Button(
        feature_controls,
        text="Scroll Bottom",
        command=feature_list.scroll_to_bottom,
        accent='secondary',
        variant='outline',
        width=12
    ).pack(side='right')

    # Instructions
    bs.Separator(main_container).pack(fill='x', pady=(15, 10))

    instructions_frame = bs.Frame(main_container)
    instructions_frame.pack(fill='x')

    bs.Label(
        instructions_frame,
        text="Features:",
        font=('Helvetica', 11, 'bold')
    ).pack(anchor='w', pady=(0, 5))

    instructions = [
        "• Virtual scrolling efficiently handles thousands of items",
        "• Use mouse wheel or scrollbar to navigate",
        "• Tab key navigates between focusable items",
        "• Click selection controls or items to select",
        "• Remove button removes items from the list"
    ]

    for instruction in instructions:
        bs.Label(instructions_frame, text=instruction, font=('Helvetica', 9)).pack(anchor='w', padx=10)

    # Demonstrate click events (fires when item is clicked, before selection changes)
    simple_list.on_item_click(lambda x: print(f"[Click] {x.data['title']} - selected: {x.data['selected']}"))
    multi_list.on_item_click(lambda x: print(f"[Click] {x.data['title']} - selected: {x.data['selected']}"))
    feature_list.on_item_click(lambda x: print(f"[Click] {x.data['title']} - selected: {x.data['selected']}"))

    # Demonstrate selection events (fires after selection state changes)
    multi_list.on_selection_changed(lambda x: print(f"[Selection Changed] Multi-list now has {len(multi_list.get_selected())} selected"))
    feature_list.on_selection_changed(lambda x: print(f"[Selection Changed] Feature-list now has {len(feature_list.get_selected())} selected"))

    root.mainloop()


if __name__ == '__main__':
    main()