# 🧠 Word Learning Telegram Bot
**High-performance asynchronous bot for personal vocabulary building and progress tracking.**

---

### 🛠 Tech Stack & Architecture

* **Language:** Python 3.10+
* **Core Framework:** `aiogram 3.x` (Asynchronous Telegram Bot API)
* **Database:** `PostgreSQL` with `asyncpg` (High-speed non-blocking driver)
* **Concurrency:** Asynchronous **Connection Pooling** for efficient DB resource management.
* **State Management:** `FSM` (Finite State Machine) for multi-step user interactions.
* **Key Logic:** Integrated **Dynamic Pagination** for large word lists and automated user statistics.

---

### 🎥 How it works

#### 🟢 Interactive Learning Process
Experience active recall through interactive quizzes. The bot tracks your answers and provides instant feedback on whether your translation is correct.
> **[ ![Learning Process](./assets/Recording_Training.gif) ]**

#### 🟡 View & Add Vocabulary
Browse your personal dictionary using **dynamic pagination** or quickly add new word pairs. The system includes real-time validation to prevent duplicates and ensure correct formatting.

> ![View and Add Words](./assets/Recording_View_Add.gif)

#### 🟠 Edit & Delete Entries
Maintain your dictionary by modifying existing records. You can **rewrite** translations or **permanently delete** mastered words to keep your learning list relevant and clean.

> ![Edit and Delete Words](./assets/Recording_Edit_Delete.gif)

#### 🔵 Statistics & Analytics
Monitor your learning efficiency. This section displays your total word count, percentage of "learned" words, and detailed accuracy ratios based on your training history.
> **[ ![Statistics View](./assets/Recording_Statistics.gif) ]**

---

### 🏗 Database Schema
The system relies on a relational structure to ensure data integrity:
* **`words`**: Stores vocabulary pairs with `status` (new/learned) and creation timestamps.
* **`statistics`**: Tracks individual user performance, including correct answer ratios and last activity dates.

---

### 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/myfish-code/Word-Learning-Tg-Bot
   cd Word-Learning-Tg-Bot

2. **Install dependencies:**
   ```bash
   pip install aiogram asyncpg python-dotenv
  
3. **Environment Setup:**
   *Create a .env file in the root directory and paste this:*
   ```bash
   BOT_TOKEN=your_tg_token
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname

5. **Run the bot:**
   ```bash
   python main.py
