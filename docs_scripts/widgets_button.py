import bootstack as bs



app = bs.App(theme="docs-light")

# solid buttons
solid = bs.Frame(app, padding=(16, 8))
solid.pack(side='top')

bs.Label(solid, font="label", text='Solid', width=10).pack(side='left')
bs.Button(solid, text='default').pack(side='left', padx=8)
solid_active = bs.Button(solid, text='active', state='active')
solid_active.pack(side='left', padx=8)
solid_active.state(['hover'])

solid_focus = bs.Button(solid, text='focus', state='focus')
solid_focus.pack(side='left', padx=8)
solid_focus.state(['focus'])

bs.Button(solid, text='disabled', state='disabled').pack(side='left', padx=8)

# outline buttons
outline = bs.Frame(app, padding=(16, 8))
outline.pack(side='top')

bs.Label(outline, font="label", text='Outline', width=10).pack(side='left')
bs.Button(outline, text='default', bootstyle="outline").pack(side='left', padx=8)
outline_active = bs.Button(outline, text='active', state='active', bootstyle="outline")
outline_active.pack(side='left', padx=8)
outline_active.state(['hover'])

outline_focus = bs.Button(outline, text='focus', state='focus', bootstyle="outline")
outline_focus.pack(side='left', padx=8)
outline_focus.state(['focus'])

bs.Button(outline, text='disabled', state='disabled', bootstyle="outline").pack(side='left', padx=8)

# ghost buttons
ghost = bs.Frame(app, padding=(16, 8))
ghost.pack(side='top')

bs.Label(ghost, font="label", text='Ghost', width=10).pack(side='left')
bs.Button(ghost, text='default', bootstyle="ghost").pack(side='left', padx=8)
ghost_active = bs.Button(ghost, text='active', state='active', bootstyle="ghost")
ghost_active.pack(side='left', padx=8)
ghost_active.state(['hover'])

ghost_focus = bs.Button(ghost, text='focus', state='focus', bootstyle="ghost")
ghost_focus.pack(side='left', padx=8)
ghost_focus.state(['focus'])

bs.Button(ghost, text='disabled', state='disabled', bootstyle="ghost").pack(side='left', padx=8)

# link buttons
link = bs.Frame(app, padding=(16, 8))
link.pack(side='top')

bs.Label(link, font="label", text='Link', width=10).pack(side='left')
bs.Button(link, text='default', bootstyle="link").pack(side='left', padx=8)
link_active = bs.Button(link, text='active', state='active', bootstyle="link")
link_active.pack(side='left', padx=8)
link_active.state(['hover'])

link_focus = bs.Button(link, text='focus', state='focus', bootstyle="link")
link_focus.pack(side='left', padx=8)
link_focus.state(['focus'])

bs.Button(link, text='disabled', state='disabled', bootstyle="link").pack(side='left', padx=8)

# text buttons
text = bs.Frame(app, padding=(16, 8))
text.pack(side='top')

bs.Label(text, font="label", text='Text', width=10).pack(side='left')
bs.Button(text, text='default', bootstyle="text").pack(side='left', padx=8)
text_active = bs.Button(text, text='active', state='active', bootstyle="text")
text_active.pack(side='left', padx=8)
text_active.state(['hover'])

text_focus = bs.Button(text, text='focus', state='focus', bootstyle="text")
text_focus.pack(side='left', padx=8)
text_focus.state(['focus'])

bs.Button(text, text='disabled', state='disabled', bootstyle="text").pack(side='left', padx=8)

icons = bs.Frame(app, padding=(16, 8))
icons.pack(side='top')

bs.Button(icons, text='Settings', icon='gear').pack(side='left', padx=8)
bs.Button(icons, icon='gear', icon_only=True).pack(side='left', padx=8)

colors = bs.Frame(app, padding=(16, 8))
colors.pack(side='top')
for color in ['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']:
    bs.Button(colors, text=color.title(), bootstyle=color).pack(side='left', padx=8)

app.mainloop()