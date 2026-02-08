from tkinter import Button,Frame, Label, Text
from pathlib import Path

ASSET_PATH = f"{Path(__file__).parent}/assets/frame0/"

class SlidePanel(Frame):
    def __init__(self, parent, start_pos, end_pos):
        super().__init__(master = parent)
        self.start_pos = start_pos + 0.04
        self.end_pos = end_pos - 0.03
        self.width = abs(start_pos - end_pos)
        self.pos = self.start_pos
        self.in_start_pos = True

        self.place(relx = self.start_pos, rely = 0.05, relwidth = self.width, relheight = 0.9)

        self.create_elements()


    def create_elements(self):
        self.title = Label(self, text="Contenido del Contenedor", padx=5, pady=5)
        self.title.pack()

        self.content = Text(self, bd=0, bg="#FFFFFF", fg="#000000")
        self.content.place(x=10, y=30, width=150, height=250)

        self.button_accept = Button(
                                master=self,
                                text="Edit",
                                borderwidth=2,
                                fg="black",
                                bg="gray",
                                highlightthickness=0,
                                compound="center"
                            )
        self.button_accept.bind("<Enter>", lambda e: self.button_accept.config(cursor="hand2"))
        self.button_accept.bind("<Leave>", lambda e: self.button_accept.config(cursor="arrow"))
        self.button_accept.place(x=50, y=300)


    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backwards()


    def animate_forward(self):
        if self.pos > self.end_pos:
            self.pos -= 0.008
            self.place(relx = self.pos, rely = 0.05, relwidth = self.width, relheight = 0.9)
            self.after(10, self.animate_forward)
        else:
            self.in_start_pos = False


    def animate_backwards(self):
        if self.pos < self.start_pos:
            self.pos += 0.008
            self.place(relx = self.pos, rely = 0.05, relwidth = self.width, relheight = 0.9)
            self.after(10, self.animate_backwards)
        else:
            self.in_start_pos = True