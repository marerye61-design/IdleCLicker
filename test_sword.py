import tkinter as tk

root = tk.Tk()
c = tk.Canvas(root, width=400, height=400, bg="#2c1a12")
c.pack()

x, y = 200, 200

# Ostrze - dół (Ciemniejszy stalowy)
c.create_polygon(x, y, x+100, y, x+80, y+8, x, y+8, fill="#7f8c8d", outline="#2c3e50", width=2)
# Ostrze - góra (Jasny stalowy - odbicie światła)
c.create_polygon(x, y-8, x+80, y-8, x+100, y, x, y, fill="#bdc3c7", outline="#2c3e50", width=2)
# Zbrocze (Rów na środku ostrza)
c.create_line(x, y, x+70, y, fill="#2c3e50", width=2)

# Jelec (Złoty krzyż)
c.create_polygon(x-8, y-25, x, y-30, x+4, y-25, x+4, y+25, x, y+30, x-8, y+25, fill="#f1c40f", outline="#e67e22", width=2)
# Klejnot w jelcu
c.create_oval(x-5, y-5, x+5, y+5, fill="#e74c3c", outline="#c0392b", width=2)

# Rękojeść (Brązowa skóra)
c.create_rectangle(x-35, y-5, x-8, y+5, fill="#8b4513", outline="#5c2e0e", width=2)
# Oplot rękojeści
for i in range(x-30, x-10, 5):
    c.create_line(i, y-5, i+5, y+5, fill="#5c2e0e", width=2)

# Głowica (Złota gałka)
c.create_oval(x-45, y-8, x-35, y+8, fill="#f1c40f", outline="#e67e22", width=2)

root.after(2000, root.destroy)
root.mainloop()
