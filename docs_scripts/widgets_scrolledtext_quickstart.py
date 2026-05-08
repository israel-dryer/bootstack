import bootstack as bs

app = bs.App()

st = bs.ScrolledText(app, height=10)
st.pack(fill="both", expand=True, padx=20, pady=20)

st.insert("end", "Insert your text here.\n" * 20)

app.mainloop()