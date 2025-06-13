# UpNest

> Track your baby's growth with ease. Securely record, visualize, and understand key growth milestones using WHO percentiles. Built for all families—especially mature adults and neurodivergent users.

---

## Table of Contents

- [UpNest](#upnest)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Features](#features)
  - [User Flow](#user-flow)
  - [Tech Stack](#tech-stack)
  - [Getting Started](#getting-started)
  - [MVP Requirements](#mvp-requirements)
  - [Screenshots](#screenshots)
  - [License](#license)
  - [Future Roadmap](#future-roadmap)
  - [Acknowledgements](#acknowledgements)

---

## Project Overview

**UpNest** is a web application designed to help parents track their baby's height, weight, and head circumference, displaying results against WHO growth percentile charts. With simple, secure authentication (AWS Cognito), users can store and view personalized growth data, and ask AI-powered questions about their baby's health and development.

---

## Features

- **Secure registration and login (AWS Cognito)**
- **Add multiple babies per account**
- **Record weight, height, head circumference, and more**
- **Visualize growth on interactive WHO percentile curves (5, 50, 95)**
- **AI-powered Q&A for parents' health and growth questions (Amazon Bedrock, optional)**
- **Responsive and intuitive UI**
- **All data private and user-specific**

---

## User Flow

1. Register a new account
2. Log in securely
3. Add your baby’s information
4. Record and review growth data (weight, height, head circumference, date, sex)
5. Visualize progress on percentile curves
6. Ask questions to the AI assistant (optional)
7. Log out safely

---

## Tech Stack

- **Frontend:** React (JavaScript + SWC)
- **Build tool:** Vite
- **Styles:** Tailwind CSS
- **Authentication:** AWS Cognito
- **Backend:** AWS Lambda (Python)
- **API Gateway:** For connecting frontend and backend
- **Database:** DynamoDB
- **AI:** Amazon Bedrock (optional)
- **Charting:** Recharts
- **Source Control:** Git, GitHub

---

## Getting Started

1. Clone the repo:
    ```bash
    git clone https://github.com/fjgonzalez25691/upnest.git
    cd upnest
    ```
2. Install dependencies:
    ```bash
    npm install
    ```
3. Configure environment variables (`.env`) as needed.
4. Start the development server:
    ```bash
    npm run dev
    ```
5. Open [http://localhost:5173](http://localhost:5173) in your browser.

> For full backend and AWS setup, see `/docs/requirements.md` and future deployment instructions.

---

## MVP Requirements

See [`/docs/MVP.md`](./docs/MVP.md) for detailed requirements, scope, and user stories.

---

## Screenshots

*Add here screenshots or screen mockups as you develop!*

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

## Future Roadmap

- Admin or pediatrician roles
- Multi-language support
- Automated reminders for check-ups
- Data export options (CSV/PDF)
- Integration with healthcare providers

---

## Acknowledgements

- Built for the AWS Hackathon 2025
- Inspired by real-life parenting challenges and neurodiversity
- Uses WHO growth standards and modern AWS technologies

---

