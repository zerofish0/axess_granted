import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import axess
from PIL import Image, ImageTk

# CONFIG
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Bienvenue sur Axess Granted", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Nom d'utilisateur")
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Mot de passe", show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self, text="Connexion", command=self.login)
        self.login_button.pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            session = axess.Axess(username, password)
            self.app.show_dashboard(session)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la connexion : {e}")

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, session):
        super().__init__(master)
        self.session = session
        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        infos = self.session.getInformations()
        grades = self.session.getGrades()

        name = infos.get("name", "Utilisateur")
        ctk.CTkLabel(self, text=f"Bonjour {name} 👋", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        # Moyenne générale
        avg = grades['global_avg']
        progress = ctk.CTkProgressBar(self, width=200)
        progress.set(avg / 20)
        ctk.CTkLabel(self, text=f"Moyenne générale : {avg:.2f}/20").grid(row=0, column=1, padx=20, pady=10)
        progress.grid(row=1, column=1, padx=20, sticky="n")

        # To-do list des devoirs
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        homeworks = self.session.getHomeworks(tomorrow)
        hw_box = ctk.CTkFrame(self)
        hw_box.grid(row=2, column=0, padx=20, pady=20, sticky="nw")
        ctk.CTkLabel(hw_box, text="📌 Devoirs pour demain :", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        for matiere, tasks in homeworks.items():
            for task in tasks:
                ctk.CTkLabel(hw_box, text=f"- {matiere} : {task}", wraplength=300).pack(anchor="w")

        # Cours de demain
        planner_date = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        courses = self.session.getPlanner(planner_date)
        demain = datetime.now() + timedelta(days=1)
        next_day = demain.strftime("%A")
        day_map = {
            "Monday": "lundi",
            "Tuesday": "mardi",
            "Wednesday": "mercredi",
            "Thursday": "jeudi",
            "Friday": "vendredi",
            "Saturday": "samedi",
            "Sunday": "dimanche"
        }
        next_day = day_map[next_day]
        course_list = courses.get(next_day, [])
        course_box = ctk.CTkFrame(self)
        course_box.grid(row=2, column=1, padx=20, pady=20, sticky="n")
        ctk.CTkLabel(course_box, text="📚 Cours de demain :", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        for course in course_list:
            ctk.CTkLabel(course_box, text=f"• {course}").pack(anchor="w")

        # Graphique des moyennes
        self.draw_chart(grades)

    def draw_chart(self, grades):
        del grades["global_avg"]
        subjects = []
        averages = []
        for matiere in grades.keys():
            avg = grades[matiere]["average"]
            subjects.append(matiere)
            averages.append(avg)


        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.bar(subjects, averages, color="#2CC985")
        ax.set_title("Moyennes par matière",color="white")
        ax.set_ylim(0, 20)
        ax.set_ylabel("Note /20",color="white")
        ax.set_xticks([])
        fig.tight_layout()
        fig.patch.set_facecolor("#2B2B2B")
        ax.set_facecolor("#2B2B2B")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        for spine in ax.spines.values():
            spine.set_color("white")
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, padx=20, pady=20)

class AxessApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Axess Granted")
        self.geometry("480x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.login_page = LoginPage(self, self)
        self.dashboard_page = None



    def show_dashboard(self, session):
        self.login_page.destroy()
        self.dashboard_page = DashboardPage(self, session)

if __name__ == "__main__":
    app = AxessApp()
    app.configure(bg="#000000")
    app.mainloop()
