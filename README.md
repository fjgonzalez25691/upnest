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
  - [API Specification](#api-specification)
    - [OpenAPI (Swagger) Specification](#openapi-swagger-specification)
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

## API Specification

UpNest exposes its backend percentile calculation through a RESTful HTTP API via AWS API Gateway.

- **API Endpoint:** *[To be added after deployment, e.g., **`https://xxxx.execute-api.eu-south-2.amazonaws.com/percentile`**]*
- **Request method:** `POST`
- **Request/response format:** See below

The current MVP implements only weight percentile calculation; additional metrics may be added in future versions.

### OpenAPI (Swagger) Specification

The full OpenAPI YAML can be found at [`/aws/lambdas/percentile/openapi.yaml`](./aws/lambdas/percentile/openapi.yaml). A summary is below:

```yaml
openapi: 3.0.3
info:
  title: UpNest Percentile API
  description: API for calculating baby weight percentiles using WHO standards. (MVP: weight only)
  version: "1.0.0"
servers:
  - url: https://ukm4je3juj.execute-api.eu-south-2.amazonaws.com
    description: AWS API Gateway endpoint (replace with your URL)
paths:
  /upnest-percentile:
    post:
      summary: Calculate weight percentile
      operationId: calculatePercentile
      requestBody:
        description: Input data for percentile calculation
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - weight
                - height
                - date_birth
                - sex
                - date_measurement
              properties:
                weight:
                  type: number
                  example: 5.35
                  description: Baby's weight in kilograms
                height:
                  type: number
                  example: 56
                  description: Baby's height in centimeters (future use)
                date_birth:
                  type: string
                  format: date
                  example: "2025-03-25"
                  description: Date of birth (YYYY-MM-DD)
                sex:
                  type: string
                  enum: [male, female]
                  example: "female"
                  description: Sex of the baby
                date_measurement:
                  type: string
                  format: date
                  example: "2025-06-22"
                  description: Date of the measurement (YYYY-MM-DD)
      responses:
        '200':
          description: Successful percentile calculation
          content:
            application/json:
              schema:
                type: object
                properties:
                  percentile:
                    type: number
                    example: 42.3
                    description: Calculated percentile for weight
                  zscore:
                    type: number
                    example: -0.7
                    description: Z-score for weight
                  LMS:
                    type: object
                    properties:
                      L:
                        type: number
                        example: 0.044
                      M:
                        type: number
                        example: 5.7969
                      S:
                        type: number
                        example: 0.12641
                  success:
                    type: boolean
                    example: true
        '400':
          description: Invalid input data
        '500':
          description: Internal server error
```

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

