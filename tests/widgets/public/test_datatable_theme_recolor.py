"""DataTable theme-colored glyphs recolor on a theme change, no interaction.

The per-row selection-marker icons (and group chevrons / sort arrows) are
theme-colored PhotoImages cached by color and held on the Treeview rows. The ttk
style rebuild doesn't touch them, so without an explicit re-render they keep
their old-theme tint until something (a selection/sort) re-triggers rendering.
`_on_theme_changed` must re-render them on the theme toggle alone.
"""
import bootstack as bs


def _marker_image(tv):
    first = tv._tree.get_children("")[0]
    return tv._tree.item(first, "image")


def test_selection_marker_recolors_on_theme_change(app):
    # The app fixture restores the theme on teardown.
    bs.set_theme("bootstrap-light")
    table = bs.DataTable(
        rows=[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        selection_mode="multi",
        show_selection_controls=True,
    )
    tv = table._internal
    tv.update_idletasks()
    tv._tree.selection_set(tv._tree.get_children("")[0])
    tv._update_selection_markers()
    before_img = _marker_image(tv)
    before_fg = tv._marker_icon_specs()[1]
    assert before_img, "marker image should be set on the selected row"

    # Toggle the theme and turn the loop once — NO table interaction.
    bs.set_theme("bootstrap-dark")
    app.tk.update_idletasks()
    app.tk.update()

    after_img = _marker_image(tv)
    after_fg = tv._marker_icon_specs()[1]
    assert before_fg != after_fg, "marker foreground color should change with theme"
    assert before_img != after_img, "marker image should re-render on theme change"
