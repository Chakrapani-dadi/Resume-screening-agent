"""
generate_samples.py
--------------------
One-time helper script to generate realistic sample resumes (mix of PDF and
DOCX) so the agent has test data to run against. Not part of the agent
pipeline itself - run this once, then run main.py.
"""

import os
from docx import Document
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUT_DIR = "sample_resumes"
os.makedirs(OUT_DIR, exist_ok=True)

# (filename_without_ext, format, resume text) - mix of strong / medium / weak
# matches against the Backend Software Engineer JD.
RESUMES = [

("priya_sharma", "docx", """Priya Sharma
Backend Software Engineer

Experience:
Senior Backend Engineer, FinTech Solutions Inc. (2020-Present)
- Designed and built REST APIs and microservices using Python (FastAPI) serving 2M+ daily requests
- Optimized PostgreSQL queries, reducing average latency by 40%
- Led migration to Docker and Kubernetes-based deployment pipeline
- Set up CI/CD pipelines on AWS

Backend Developer, DataCorp (2018-2020)
- Built internal tools with Django and MySQL
- Implemented Kafka-based event streaming for order processing

Education: B.S. Computer Science, National Institute of Technology

Skills: Python, Go, FastAPI, Django, PostgreSQL, MySQL, Docker, Kubernetes, AWS, Kafka, REST API design
"""),

("arjun_mehta", "pdf", """Arjun Mehta
Software Engineer - Backend Focus

Summary: 4 years building scalable backend systems in Go and Python.

Experience:
Backend Engineer, CloudScale Systems (2021-Present)
- Built microservices in Go handling high-throughput API traffic
- Optimized SQL queries across PostgreSQL clusters
- Managed CI/CD pipelines using GitHub Actions and deployed to GCP
- Introduced RabbitMQ for async task processing

Software Engineer, StartupHub (2019-2021)
- Developed REST APIs with Flask
- Wrote unit and integration tests, improved test coverage to 85%

Education: B.Tech Computer Science, IIT Delhi

Skills: Go, Python, Flask, PostgreSQL, Docker, GCP, RabbitMQ, REST APIs, CI/CD
"""),

("neha_gupta", "docx", """Neha Gupta
Full Stack Developer

Experience:
Full Stack Developer, WebWorks (2019-Present)
- Built React frontends and connected them to Django REST backends
- Worked with PostgreSQL for data storage
- Some exposure to Docker for local development
- Occasionally helped with AWS deployments

Junior Developer, AppStudio (2017-2019)
- Built internal admin dashboards using Django

Education: B.S. Information Technology

Skills: JavaScript, React, Django, Python, PostgreSQL, basic Docker, HTML/CSS
"""),

("rahul_verma", "pdf", """Rahul Verma
DevOps Engineer

Experience:
DevOps Engineer, InfraTech (2020-Present)
- Managed Kubernetes clusters and CI/CD pipelines on AWS
- Automated infrastructure with Terraform
- Monitored production systems using Prometheus/Grafana
- Some scripting in Python for automation tasks

Systems Administrator, HostingCo (2018-2020)
- Maintained Linux servers and networking infrastructure

Education: B.S. Information Systems

Skills: Kubernetes, Docker, Terraform, AWS, Python (scripting), Linux, CI/CD, monitoring
"""),

("ananya_iyer", "docx", """Ananya Iyer
Backend Engineer

Experience:
Backend Engineer, RetailTech Solutions (2021-Present)
- Designed REST APIs in Python (Django REST Framework) for e-commerce platform
- Optimized MySQL database queries for product search, cutting response time by 30%
- Containerized services with Docker and deployed on AWS ECS
- Collaborated with DevOps on CI/CD pipeline improvements

Software Engineer Intern, TechStart (2020)
- Built internal tools using Flask

Education: M.S. Computer Science, BITS Pilani

Skills: Python, Django, Django REST Framework, MySQL, Docker, AWS, REST API design, Git
"""),

("vikram_singh", "pdf", """Vikram Singh
Marketing Manager

Experience:
Marketing Manager, BrandBoost Agency (2019-Present)
- Led digital marketing campaigns across social media platforms
- Managed a team of 5 content creators
- Analyzed campaign performance using Google Analytics
- Coordinated with design team on brand assets

Marketing Associate, AdWorks (2017-2019)
- Ran email marketing campaigns and A/B tests

Education: MBA Marketing, Delhi University

Skills: Digital Marketing, SEO, Google Analytics, Content Strategy, Team Leadership
"""),

("sophia_dsouza", "docx", """Sophia D'Souza
Data Scientist

Experience:
Data Scientist, InsightAI (2020-Present)
- Built machine learning models for customer churn prediction using Python
- Wrote SQL queries to extract and analyze data from PostgreSQL warehouses
- Some experience with Flask for deploying model APIs
- Used Docker for packaging ML models

Data Analyst, MetricsCo (2018-2020)
- Created dashboards and reports using SQL and Python

Education: M.S. Data Science, University of Pune

Skills: Python, Machine Learning, SQL, PostgreSQL, Flask (basic), Docker, Pandas, scikit-learn
"""),

("karan_patel", "pdf", """Karan Patel
Senior Backend Engineer

Experience:
Senior Backend Engineer, PayFlow Technologies (2017-Present)
- Architected microservices-based payment processing system in Go and Python
- Designed REST and gRPC APIs handling millions of transactions daily
- Deep expertise in PostgreSQL optimization, indexing, and replication
- Built and maintained Kubernetes infrastructure on GCP
- Introduced Kafka for reliable event-driven architecture
- Mentored junior engineers, ran code reviews, contributed to open-source Go libraries

Backend Developer, FinServ Corp (2014-2017)
- Built Django-based REST APIs for internal financial tools

Education: B.Tech Computer Science, IIT Bombay

Skills: Go, Python, Django, FastAPI, PostgreSQL, Kubernetes, Docker, GCP, AWS, Kafka, gRPC, CI/CD, mentoring
"""),

("emily_chen", "docx", """Emily Chen
UI/UX Designer

Experience:
UI/UX Designer, DesignHouse Studio (2019-Present)
- Designed user interfaces for mobile and web applications using Figma
- Conducted user research and usability testing
- Created design systems and component libraries
- Collaborated with frontend engineers on implementation

Junior Designer, CreativeAgency (2017-2019)
- Produced marketing graphics and branding materials

Education: B.F.A. Graphic Design

Skills: Figma, Sketch, Adobe Creative Suite, User Research, Prototyping, Design Systems
"""),

("rohan_kapoor", "pdf", """Rohan Kapoor
Backend Developer

Experience:
Backend Developer, ShopEasy (2020-Present)
- Built REST APIs using Flask and FastAPI for e-commerce checkout flow
- Wrote and optimized PostgreSQL queries for order management system
- Used Docker for local development and staging environments
- Basic exposure to AWS (EC2, S3) for deployments
- Participated in on-call rotation for production debugging

Junior Developer, WebNest (2018-2020)
- Maintained a Django monolith application

Education: B.S. Computer Science, Pune University

Skills: Python, Flask, FastAPI, Django, PostgreSQL, Docker, AWS (basic), REST APIs, Git
"""),

("meera_joshi", "docx", """Meera Joshi
QA Automation Engineer

Experience:
QA Automation Engineer, TestPro Labs (2019-Present)
- Built automated test suites using Python and Selenium
- Wrote API test scripts using Postman and pytest
- Worked with SQL databases to validate data integrity
- Some exposure to Docker for running test environments

QA Analyst, SoftCheck (2017-2019)
- Performed manual testing and wrote test plans

Education: B.S. Information Technology

Skills: Python, Selenium, pytest, SQL, Postman, Docker (basic), Test Automation
"""),
]


def make_docx(path, text):
    doc = Document()
    for line in text.strip().split("\n"):
        doc.add_paragraph(line)
    doc.save(path)


def make_pdf(path, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in text.strip().split("\n"):
        # encode to latin-1 safely for the basic FPDF font
        safe_line = line.encode("latin-1", "replace").decode("latin-1")
        if safe_line.strip() == "":
            pdf.ln(6)
        else:
            pdf.multi_cell(0, 6, safe_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.output(path)


def main():
    for name, fmt, text in RESUMES:
        if fmt == "docx":
            make_docx(os.path.join(OUT_DIR, f"{name}.docx"), text)
        elif fmt == "pdf":
            make_pdf(os.path.join(OUT_DIR, f"{name}.pdf"), text)
    print(f"Generated {len(RESUMES)} sample resumes in {OUT_DIR}/")


if __name__ == "__main__":
    main()
