# 📌 Project Title

**Orvixo AI – Inventory Intelligence Service**

---

# 📌 Problem Statement

Many small and medium-sized manufacturing companies still manage their inventory using **Google Sheets or Excel**. While these tools are simple and familiar, they have several limitations:

* Inventory managers must manually search through large spreadsheets.
* There is no intelligent analysis of stock levels.
* Potential stock shortages are often identified too late.
* Employees cannot ask inventory-related questions in natural language.
* Decision-making depends on manual calculations and human experience.
* There is no centralized AI assistant to provide recommendations or business insights.

As a result, inventory management becomes time-consuming, error-prone, and reactive instead of proactive.

---

# 📌 Proposed Solution

The **Inventory Intelligence Service** is an AI-powered backend application that transforms a traditional Google Sheet into an intelligent inventory assistant.

Instead of replacing the existing inventory system, the application works on top of it by reading live inventory data through the **Google Sheets MCP (Model Context Protocol)**.

Users can ask questions in natural language, and the AI analyzes the inventory to provide meaningful insights, recommendations, and explanations.

This allows companies to continue using their existing Google Sheets workflow while benefiting from AI-powered decision support.

---

# 📌 Objectives

The main objectives of the project are:

* Build an AI-powered Inventory Assistant.
* Integrate Google Sheets using MCP.
* Analyze live inventory data.
* Detect inventory risks.
* Recommend actions for inventory management.
* Allow users to interact with inventory using natural language.
* Design a scalable architecture for future manufacturing AI services.

---

# 📌 Technologies Used

### Backend

* FastAPI
* Python

### AI

* Groq API
* Llama 3.3 70B

### Integration

* Model Context Protocol (MCP)
* Google Sheets MCP

### Database

* Supabase

  * User Management
  * Chat History
  * AI Analysis History
  * Notifications
  * Logs

### Authentication

* JWT

---

# 📌 System Architecture

```text
                User
                  │
                  ▼
        FastAPI Backend
                  │
                  ▼
        Inventory AI Agent
                  │
      Google Sheets MCP
                  │
                  ▼
          Google Sheet
                  │
                  ▼
             Groq LLM
                  │
                  ▼
         AI Generated Response
                  │
                  ▼
               Dashboard
```

---

# 📌 Workflow

### Step 1
Factory employees maintain inventory inside Google Sheets.
↓
### Step 2
A manager asks a question.
Example:
> Which materials are below minimum stock?
↓
### Step 3
The Inventory AI receives the request.
↓
### Step 4
The AI calls Google Sheets through MCP.
↓
### Step 5
The latest inventory is retrieved.
↓
### Step 6
The AI analyzes the inventory.
↓
### Step 7
The AI generates:
* Risk Level
* Explanation
* Recommendation
↓
### Step 8
The response is returned to the user.

---

# 📌 Features

### Inventory Search
Example:
> Show Steel inventory.

---
### Inventory Analysis
Example:
> Which materials require immediate attention?

---
### Risk Detection
Detects:
* Low Stock
* Critical Stock
* Overstock

---
### AI Recommendations
Example:
> Order 500 kg from Supplier A.

---
### Natural Language Queries
Example:
> What should I reorder today?

---
### Live Inventory
Always reads the latest Google Sheet.
No duplicated inventory.

---

# 📌 Why Google Sheets?

Many factories already use Google Sheets.

Instead of forcing companies to migrate to a new system, the platform integrates directly with their existing workflow using MCP.

This minimizes adoption effort while adding intelligent capabilities.

---

# 📌 Why MCP?

The Model Context Protocol acts as a secure bridge between the AI and Google Sheets.

Instead of giving the AI unrestricted access, MCP exposes specific tools such as:
* Read Inventory
* Search Inventory
* Update Inventory (if authorized)

This makes the system modular, secure, and extensible.

---

# 📌 Why AI?

Traditional inventory systems only display data.
The AI interprets the data.

For example, instead of showing:
```text
Steel = 80
Minimum = 100
```
The AI explains:
> Steel inventory is below the minimum safety stock level. At the current consumption rate, production may be affected within the next few days. It is recommended to initiate a purchase order immediately.

---

# 📌 Future Scope

The Inventory AI is the first module of the platform.
Future AI services include:
* Procurement AI
* Production Planning AI
* Quality AI
* Predictive Maintenance AI
* Workforce AI
* Supply Chain AI
* Executive AI Copilot

All services will share the same architecture while focusing on different manufacturing domains.

---

# 📌 Conclusion

The Inventory Intelligence Service demonstrates how Artificial Intelligence can enhance existing manufacturing workflows without replacing current systems.

By integrating Google Sheets through MCP and combining it with a Large Language Model, the platform enables intelligent inventory analysis, natural language interaction, and actionable recommendations.

This project serves as the foundation for a scalable AI-powered Manufacturing Intelligence Platform that can expand into procurement, production planning, quality management, maintenance, and executive decision support.