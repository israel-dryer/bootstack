if __name__ == '__main__':
    import bootstack as bs

    root = bs.Window(theme="dark", size=(200, 200))

    om = bs.OptionMenu(
        root, value="Python", dropdown_button_icon="chevron-down",
        options=["Python", "Javascript", "Swift", "C#", "Go", "PHP", "Java"])
    om.pack(pady=20, padx=20, fill='x')

    om.on_changed(print)

    om = bs.OptionMenu(
        root, value="Python",
        state="disabled",
        options=["Python", "Javascript", "Swift", "C#", "Go", "PHP", "Java"])
    om.pack(pady=20, padx=20, fill='x')

    om['show_dropdown_button'] = False



    root.mainloop()