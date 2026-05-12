import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class MovieLibrary:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 Movie Library — Личная кинотека")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        self.movies = []
        self.filename = "movies.json"

        self.create_widgets()
        self.load_from_json()

    def create_widgets(self):
        # === Верхняя панель ввода ===
        input_frame = ttk.LabelFrame(self.root, text="Добавить новый фильм", padding=10)
        input_frame.pack(fill="x", padx=10, pady=8)

        # Название
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.genre_entry = ttk.Entry(input_frame, width=20)
        self.genre_entry.grid(row=0, column=3, padx=5, pady=5)

        # Год
        ttk.Label(input_frame, text="Год:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.year_entry = ttk.Entry(input_frame, width=15)
        self.year_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Рейтинг
        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.rating_entry = ttk.Entry(input_frame, width=15)
        self.rating_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Кнопка добавить
        add_btn = ttk.Button(input_frame, text="➕ Добавить фильм", command=self.add_movie)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

        # === Фильтры ===
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Жанр:").pack(side="left", padx=5)
        self.genre_filter = ttk.Combobox(filter_frame, width=20, state="readonly")
        self.genre_filter.pack(side="left", padx=5)
        self.genre_filter.bind("<<ComboboxSelected>>", lambda e: self.filter_movies())

        ttk.Label(filter_frame, text="   Год от:").pack(side="left", padx=5)
        self.year_from = ttk.Entry(filter_frame, width=8)
        self.year_from.pack(side="left", padx=5)
        self.year_from.bind("<KeyRelease>", lambda e: self.filter_movies())

        ttk.Label(filter_frame, text="до:").pack(side="left", padx=5)
        self.year_to = ttk.Entry(filter_frame, width=8)
        self.year_to.pack(side="left", padx=5)
        self.year_to.bind("<KeyRelease>", lambda e: self.filter_movies())

        clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters)
        clear_filter_btn.pack(side="right", padx=10)

        # === Таблица ===
        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=20)

        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("title", width=400)
        self.tree.column("genre", width=150)
        self.tree.column("year", width=80)
        self.tree.column("rating", width=80)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=8)

        ttk.Button(btn_frame, text="🗑 Удалить выбранный", command=self.delete_movie).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить таблицу", command=self.refresh_table).pack(side="left", padx=5)

        # Статус
        self.status = ttk.Label(self.root, text="Готово", relief="sunken", anchor="w")
        self.status.pack(fill="x", padx=10, pady=5)

    def validate_input(self):
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year_str = self.year_entry.get().strip()
        rating_str = self.rating_entry.get().strip()

        if not title or not genre:
            messagebox.showwarning("Ошибка", "Название и жанр обязательны!")
            return None

        try:
            year = int(year_str)
            if year < 1888 or year > datetime.now().year + 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Год должен быть корректным числом!")
            return None

        try:
            rating = float(rating_str.replace(',', '.'))
            if not 0 <= rating <= 10:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Рейтинг должен быть числом от 0 до 10!")
            return None

        return {"title": title, "genre": genre, "year": year, "rating": round(rating, 1)}

    def add_movie(self):
        movie = self.validate_input()
        if not movie:
            return

        self.movies.append(movie)
        self.save_to_json()
        self.refresh_table()
        self.update_genre_filter()

        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)

        self.status.config(text=f"Фильм добавлен: {movie['title']}")

    def refresh_table(self, filtered_movies=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        movies_to_show = filtered_movies if filtered_movies is not None else self.movies

        for movie in sorted(movies_to_show, key=lambda x: x['year'], reverse=True):
            self.tree.insert("", "end", values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                movie["rating"]
            ))

    def filter_movies(self):
        genre = self.genre_filter.get()
        try:
            y_from = int(self.year_from.get()) if self.year_from.get() else 0
            y_to = int(self.year_to.get()) if self.year_to.get() else 9999
        except ValueError:
            y_from, y_to = 0, 9999

        filtered = []
        for m in self.movies:
            if (not genre or m["genre"] == genre) and (y_from <= m["year"] <= y_to):
                filtered.append(m)

        self.refresh_table(filtered)

    def update_genre_filter(self):
        genres = sorted(set(m["genre"] for m in self.movies))
        self.genre_filter['values'] = [""] + genres

    def clear_filters(self):
        self.genre_filter.set("")
        self.year_from.delete(0, tk.END)
        self.year_to.delete(0, tk.END)
        self.refresh_table()

    def delete_movie(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Внимание", "Выберите фильм для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный фильм?"):
            index = self.tree.index(selected[0])
            del self.movies[index]
            self.save_to_json()
            self.refresh_table()
            self.update_genre_filter()

    def load_from_json(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
                self.refresh_table()
                self.update_genre_filter()
                self.status.config(text=f"Загружено {len(self.movies)} фильмов")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def save_to_json(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MovieLibrary()
    app.run()