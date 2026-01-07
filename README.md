# todiane.com – Portfolio of Indie Developer Diane Corriette

![todiane.com header](https://github.com/djangify/todiane/blob/4616c26c7d9867b0ee031f251d1548edead7bfc2/todiane-header.png)

<p align="center">
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  </a>
  <a href="https://www.django-rest-framework.org/">
    <img src="https://img.shields.io/badge/Django%20REST%20Framework-ff1709?style=for-the-badge&logo=django&logoColor=white" alt="Django REST Framework">
  </a>
  <a href="https://tailwindcss.com/">
    <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  </a>
  <a href="https://www.hardenize.com/">
    <img src="https://img.shields.io/badge/VPS%20Hosting-Self%20Managed-blue?style=for-the-badge&logo=linux&logoColor=white" alt="VPS Hosting">
  </a>
  <a href="https://www.perplexity.ai/">
    <img src="https://img.shields.io/badge/AI%20Search%20Readiness-Enabled-success?style=for-the-badge&logo=openai&logoColor=white" alt="AI Search Readiness">
  </a>
</p>

---

## 💻 Project Overview

**todiane.com** is the professional portfolio of **Diane Corriette**, a Django Indie Software Developer & creator of the **Djangify eCommerce Site Builder**.

This project demonstrates:
- A **clean Django + Tailwind CSS** architecture  
- Integration with **PostgreSQL** on **self-managed VPS hosting**
- Dynamic **AI-Search-Ready sitemap** and **robots.txt** files  
- Blog, portfolio, and documentation systems powered by Django apps  
- A practical approach to **ethical visibility** and **AI-indexed content**

---

## 🌍 1. Files Included

| File | Purpose |
|------|----------|
| `todiane/sitemap.py` | Defines sitemaps for static pages, blog posts, and portfolio projects |
| `core/views.py` | Generates a dynamic `robots.txt` with AI & search-engine visibility rules |
| `todiane/urls.py` | Registers sitemap and robots.txt routes |
| `core/home.html` | Hero, about, and skills sections built with Tailwind v4 |
| `core/ai-search-readiness.html` | Cluster page explaining AI Search Readiness principles |

---

## 🧩 2. How It Works

### Sitemap
Each public page is automatically indexed with crawl frequency and priority weights.

| Section | Priority | Changefreq | Notes |
|----------|-----------|-------------|-------|
| Static pages | 1.0 | weekly | Homepage, AI-Search guides, policy pages |
| Blog posts | 0.9 | weekly | Dynamic list of all published blog articles |
| Portfolio | 0.8 | monthly | Dynamic list of all published projects |

→ Visit **[https://todiane.com/sitemap.xml](https://todiane.com/sitemap.xml)** to see it live.

### Robots.txt
A dynamic, human-readable file built from the current domain:

- ✅ Allows all public sections (`/`, `/blog/`, `/portfolio/`)  
- 🚫 Blocks private areas (`/admin/`, `/accounts/`, `/checkout/`)  
- 🤖 Explicitly includes AI & answer-engine bots:
  - GPTBot, ChatGPT-User  
  - ClaudeBot, PerplexityBot  
  - Google-Extended, Bingbot, Anthropic-AI  

→ Visit **[https://todiane.com/robots.txt](https://todiane.com/robots.txt)** to verify.

---

## 🔍 3. Search Engine Verification

### Google Search Console
1. Go to [search.google.com/search-console](https://search.google.com/search-console).  
2. Add your property (Domain type).  
3. Submit `/sitemap.xml` under **Indexing → Sitemaps**.

### Bing Webmaster Tools
1. Visit [bing.com/webmasters](https://www.bing.com/webmasters/).  
2. Add and verify your site.  
3. Submit `/sitemap.xml` as above.

Both will confirm when the sitemap is successfully crawled.

---

## 🧠 4. Why AI-Search Readiness Matters

Traditional SEO gets your site **ranked**.  
**AI-Search Readiness** gets your content **chosen** — in AI overviews, summaries, and answer engines like:

- Google AI Overviews  
- Bing Copilot  
- ChatGPT Browse  
- Perplexity Answers  
- Claude Artifacts  

Structured data, schema markup, and concise FAQs make your content machine-readable and discoverable across these platforms.

---

## ⚙️ 5. Tech Stack

| Layer | Tool | Purpose |
|--------|------|----------|
| Backend | Django 5 | Core framework & admin |
| API | Django REST Framework | Data endpoints |
| Frontend | Tailwind CSS v4 | Styling & layout |
| Database | PostgreSQL | Production-ready persistence |
| Hosting | Self-Managed VPS (Linux + Nginx + Gunicorn) | Deployment |
| Editor | TinyMCE + Custom Policies | Blog content creation |
| AI Visibility | Structured Data + FAQ Schema + Cluster Pages | AI readiness |

---

## 🧰 6. Maintenance Tips

- Django auto-updates the sitemap when new posts or projects are published.  
- Verify changes by visiting `/sitemap.xml`.  
- Use [Google’s URL Inspection tool](https://search.google.com/search-console) to test AI snippet coverage.  
- Review `robots.txt` after domain or hosting changes.  

---

## 👩‍💻 Author

**Diane Corriette**  
Backend Django Developer & Creator of the Mini eCommerce Site Builder  
🌐 [https://todiane.com](https://todiane.com)  
💼 [LinkedIn @ todianedev](https://www.linkedin.com/in/todianedev)  
🛠️ Focus: Django + Tailwind Development, AI-Search-Ready Design, Ethical Visibility  

---

## 📄 License

This repository is provided for learning and demonstration purposes.  
Please credit the author if you adapt or reuse significant portions of the structure or content.

---

> **“AI-Search-Ready development means building websites humans love — and machines understand.”**
