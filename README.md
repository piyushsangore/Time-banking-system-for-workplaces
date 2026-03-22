# 🚀 Workplace Time Banking & Skill Exchange System

A full-stack web application that enables employees within an organization to exchange skills and assistance using a **time-based credit system** instead of money.

This system promotes collaboration, efficient skill utilization, and peer-to-peer support by allowing users to post tasks and earn credits by helping others.

---

## 📌 Overview

Modern workplaces often face inefficiencies in internal collaboration, where employees struggle to find help for small but important tasks. Traditional systems lack a structured way to **exchange skills and time fairly**.

This project introduces a **Workplace Time Banking System** that:

* Enables employees to post tasks with credit incentives  
* Allows others to accept and complete tasks  
* Maintains a fair **credit-based exchange economy**  
* Automates task lifecycle management (live → accepted → completed → expired)  

The system ensures **transparency, accountability, and efficient collaboration** within an organization.

---

## 🎯 Key Features

### 🔐 User Authentication

* Secure user registration and login system  
* Password hashing using **Werkzeug**  
* New users receive **10 initial credits**

---

### 💰 Credit-Based Economy

* Users must have sufficient credits to post tasks  
* Credits are transferred only after successful task completion  
* Prevents misuse and ensures fairness  

---

### 📝 Task Management

* Create tasks with:
  * Title
  * Description
  * Credits
  * Deadline
  * Duration  
* Tasks are dynamically managed based on status  

---

### 🔍 Smart Task Filtering

Only shows tasks that are:

* Not accepted  
* Not expired  
* Not created by the current user  

---

### 🤝 Task Acceptance & Completion

* Users can accept available tasks  
* Task creator marks completion  
* Automatic credit transfer occurs  

---

### ⏳ Automatic Task Expiry

* Tasks past their deadline are automatically marked as `expired`  
* Ensures system integrity and avoids stale data  

---

## 🏗️ System Architecture

The system follows a **modular client-server architecture**:

* User Interface (Frontend)
* Flask Backend (Routing & Logic)
* MongoDB Database (Data Storage)

### Flow:

* User Authentication → Dashboard  
* Task Creation → Database Storage  
* Task Browsing → Filtering Logic  
* Task Acceptance → Status Update  
* Task Completion → Credit Transfer  

📌 Ensures:

* Scalability  
* Maintainability  
* Clear separation of concerns  

---

## ⚙️ Methodology

### 1️⃣ User Registration & Initialization

* User registers with email and password  
* System assigns:


credits = 10


---

### 2️⃣ Task Creation

* User submits task details  
* System validates:


user_credits >= task_credits


* Task is stored with status `live`  

---

### 3️⃣ Task Discovery

* System filters tasks based on:
  * Availability  
  * Deadline validity  
  * Ownership  

---

### 4️⃣ Task Acceptance

* Task is assigned to another user  
* Status changes:


live → accepted


---

### 5️⃣ Task Completion & Credit Transfer

Final transaction:


creator.credits -= task.credits
acceptor.credits += task.credits


Status:


accepted → completed


---

### 6️⃣ Task Expiry Handling

* Automatically checks deadlines  
* Updates:


status = expired


---

## 🖥️ Tech Stack

### 🔹 Backend

* Python  
* Flask  

### 🔹 Frontend

* HTML5  
* CSS3  
* Bootstrap  
* JavaScript  

### 🔹 Database

* MongoDB Atlas  

### 🔹 Security

* Werkzeug Password Hashing  

---

## 📊 System Highlights

* ⚡ Real-time task updates  
* 💰 Fair credit-based exchange system  
* 🔄 Complete task lifecycle management  
* ⏳ Automated expiry handling  
* 📉 Reduces dependency on centralized task allocation  

✔ Encourages collaboration  
✔ Improves productivity  
✔ Promotes skill sharing  

---

## 📁 Project Structure

```id="projstruct2"```
timebank-system/
│
├── app.py
├── config.py
│
├── database/
│   └── mongodb.py
│
├── models/
│   ├── user_model.py
│   └── task_model.py
│
├── routes/
│   ├── auth_routes.py
│   └── task_routes.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── post_task.html
│   ├── browse_tasks.html
│   └── my_tasks.html
│
├── static/
│   ├── css/
│   └── js/
│
├── requirements.txt
└── README.md
🚀 How to Run
git clone https://github.com/your-username/timebank-system.git
cd timebank-system
pip install -r requirements.txt
python app.py

Open:

http://127.0.0.1:5000/
🔒 Security & Best Practices
Passwords stored using hashing (not plain text)
Sensitive files excluded via .gitignore
Modular architecture for scalability
Clean separation of backend logic and frontend
🔮 Future Scope
🔔 Notification system
📜 Credit transaction history
🏷️ Skill-based task filtering
📱 Mobile responsive UI
🌐 Cloud deployment (AWS / Render)
🎓 Academic Context

Developed as part of the Software Engineering curriculum, focusing on:

System Design
Database Modeling
Full-Stack Development
Real-world Problem Solving
👨‍💻 Authors
Piyush Sangore
⭐ Support

If you found this project useful:

⭐ Star the repository
📢 Share with others
💼 Add it to your portfolio
