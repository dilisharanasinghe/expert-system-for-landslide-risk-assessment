import ScrolledText
from Tkinter import *
import threading
import time


class Application:
    def __init__(self, reset_callback=None):
        self.__root = None
        self.__output_window = None
        self.__output_window_2 = None
        self.__entry = None
        self.__output_label = None
        self.__output_label_var = None
        self.__output_label_2 = None
        self.__output_label_var_2 = None
        self.__reset_button = None

        self.__waiting_for_input = False
        self.__last_user_input = ''

        self.__reset_callback = reset_callback

    def create_widgets(self):
        self.__root = Tk()
        self.__root.geometry('1250x750+375+125')
        self.__root.title("Landslide Risk Assessment - Expert System")

        MAIN_BG_COLOR = 'azure'
        MAIN_FG_COLOR = 'black'
        MAIN_BUTTON_BG_COLOR = 'white'

        frame_l = Frame(self.__root, bg=MAIN_BG_COLOR)
        frame_l.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=1.0)

        frame_r = Frame(self.__root, bg=MAIN_BG_COLOR)
        frame_r.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=1.0)

        self.__output_window = ScrolledText.ScrolledText(frame_l)
        self.__output_window.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

        self.__entry = Entry(frame_r)
        self.__entry.place(relx=0.02, rely=0.02, relwidth=0.56, relheight=0.05)

        enter_button = Button(frame_r, text="Answer", command=self.entry_button_callback, bg=MAIN_BUTTON_BG_COLOR)
        enter_button.place(relx=0.60, rely=0.02, relwidth=0.38, relheight=0.05)

        unknown_button = Button(frame_r, text="Unknown", command=self.unknown_button_callback, bg=MAIN_BUTTON_BG_COLOR)
        unknown_button.place(relx=0.02, rely=0.10, relwidth=0.43, relheight=0.05)

        why_button = Button(frame_r, text="Why", command=self.why_button_callback, bg=MAIN_BUTTON_BG_COLOR)
        why_button.place(relx=0.02, rely=0.17, relwidth=0.43, relheight=0.05)

        q_button = Button(frame_r, text="?", command=self.q_button_callback, bg=MAIN_BUTTON_BG_COLOR)
        q_button.place(relx=0.55, rely=0.10, relwidth=0.43, relheight=0.05)

        help_button = Button(frame_r, text="Help", command=self.help_button_callback, bg=MAIN_BUTTON_BG_COLOR)
        help_button.place(relx=0.55, rely=0.17, relwidth=0.43, relheight=0.05)

        fixed_string_0 = StringVar()
        fixed_string_0.set('--------------------------------------- Findings for regulatory state ----------------'
                           '-----------------------')
        output_label_fixed = Label(frame_r, textvariable=fixed_string_0, bg=MAIN_BG_COLOR, fg=MAIN_FG_COLOR)
        output_label_fixed.place(relx=0.02, rely=0.30, relwidth=0.96, relheight=0.03)

        fixed_string_3 = StringVar()
        fixed_string_3.set('National Building Research Organization Approval :')
        label_fixed_3 = Label(frame_r, textvariable=fixed_string_3, anchor='w', bg=MAIN_BG_COLOR, fg=MAIN_FG_COLOR)
        label_fixed_3.place(relx=0.02, rely=0.35, relwidth=0.55, relheight=0.03)

        # self.__output_label_var = StringVar()
        # self.__output_label = Label(frame_r, textvariable=self.__output_label_var, relief=SUNKEN, bg='white', anchor='w')
        self.__output_label = ScrolledText.ScrolledText(frame_r)
        self.__output_label.place(relx=0.57, rely=0.35, relwidth=0.41, relheight=0.08)

        fixed_string_3 = StringVar()
        fixed_string_3.set('Additional Recommendations :')
        label_fixed_3 = Label(frame_r, textvariable=fixed_string_3, anchor='w', bg=MAIN_BG_COLOR, fg=MAIN_FG_COLOR)
        label_fixed_3.place(relx=0.02, rely=0.44, relwidth=0.96, relheight=0.03)

        self.__output_window_2 = ScrolledText.ScrolledText(frame_r)
        self.__output_window_2.place(relx=0.02, rely=0.48, relwidth=0.96, relheight=0.10)

        canvas = Canvas(frame_r, width=300, height=200)
        img = PhotoImage(file="Images/contour.png")
        canvas.create_image(0, 0, anchor=NW, image=img)
        canvas.place(relx=0.02, rely=0.60, relwidth=0.48, relheight=0.30)

        canvas1 = Canvas(frame_r, width=300, height=200)
        img1 = PhotoImage(file="Images/cantilevered-retaining-wall.png")
        canvas1.create_image(0, 0, anchor=NW, image=img1)
        canvas1.place(relx=0.50, rely=0.60, relwidth=0.48, relheight=0.30)

        fixed_string_1 = StringVar()
        fixed_string_1.set('A house in contour present land')
        label_fixed_0 = Label(frame_r, textvariable=fixed_string_1, bg=MAIN_BG_COLOR, fg=MAIN_FG_COLOR)
        label_fixed_0.place(relx=0.02, rely=0.85, relwidth=0.48, relheight=0.05)

        fixed_string_2 = StringVar()
        fixed_string_2.set('A vertical cut in land with retaining wall')
        label_fixed_1 = Label(frame_r, textvariable=fixed_string_2, bg=MAIN_BG_COLOR, fg=MAIN_FG_COLOR)
        label_fixed_1.place(relx=0.50, rely=0.85, relwidth=0.48, relheight=0.05)

        self.__reset_button = Button(frame_r, text="Reset", command=self.reset_button_callback, bg=MAIN_BUTTON_BG_COLOR)
        self.__reset_button.place(relx=0.02, rely=0.92, relwidth=0.43, relheight=0.05)

        self.__root.bind("<KeyPress-Return>", self.on_enter_key_press)

        self.__root.mainloop()

    def enable_reset_button(self):
        if self.__reset_button:
            self.__reset_button['state'] = 'normal'

    def disable_reset_button(self):
        if self.__reset_button:
            self.__reset_button['state'] = 'disabled'

    def reset_button_callback(self):
        if self.__reset_callback:
            self.__reset_callback()
            self.__output_window.delete('1.0', 'end')
            self.__output_window_2.delete('1.0', 'end')
            self.__output_label.delete('1.0', 'end')

    def on_enter_key_press(self, event):
        self.entry_button_callback()

    def entry_button_callback(self):
        if self.__entry:
            s = self.__entry.get()
            if len(s) > 0:
                self.__last_user_input = s
                self.insert_text(s)
                self.__waiting_for_input = False

            self.__entry.delete(0, 'end')

    def unknown_button_callback(self):
        s = 'unknown'
        self.__last_user_input = s
        self.insert_text(s)
        self.__waiting_for_input = False

        self.__entry.delete(0, 'end')

    def why_button_callback(self):
        s = 'why'
        self.__last_user_input = s
        self.insert_text(s)
        self.__waiting_for_input = False

        self.__entry.delete(0, 'end')

    def help_button_callback(self):
        s = 'help'
        self.__last_user_input = s
        self.insert_text(s)
        self.__waiting_for_input = False

        self.__entry.delete(0, 'end')

    def q_button_callback(self):
        s = '?'
        self.__last_user_input = s
        self.insert_text(s)
        self.__waiting_for_input = False

        self.__entry.delete(0, 'end')

    def insert_text(self, text):
        if self.__output_window:
            self.__output_window.insert(INSERT, '{0}\n\n'.format(text))
            self.__output_window.see("end")

    def get_input(self, text):
        self.insert_text(text)
        self.__waiting_for_input = True
        while True:
            if not self.__waiting_for_input:
                break

            time.sleep(0.25)

        return self.__last_user_input

    def set_approval_state(self, text):
        if self.__output_label:
            # self.__output_label_var.set(text)
            self.__output_label.insert(INSERT, '{0}\n'.format(text))

    def set_suggestions(self, text):
        if self.__output_window_2:
            self.__output_window_2.insert(INSERT, '{0}\n\n'.format(text))
            # self.__output_window_2.see("end")

    def run(self):
        thread = threading.Thread(target=self.create_widgets)
        thread.start()


if __name__ == '__main__':
    app = Application()
    app.run()

    time.sleep(1.0)
    for i in range(10):
        out = app.get_input('say some thing?')
        print(out)