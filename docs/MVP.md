# UpNest – MVP Requirements & User Flow

## 1. Project Objective

UpNest is a web application designed to help parents track their baby's growth by securely recording and visualizing height, weight, and head circumference, with reference to WHO percentile curves. The aim is to make growth tracking simple, accessible, and science-based, especially for mature adults and neurodivergent users.

---

## 2. Scope of the MVP

- User registration and login (AWS Cognito)
- Secure data entry for baby’s growth metrics
- Visualization of growth curves with WHO percentiles (5, 50, 95)
- Simple, responsive interface for parents/tutors
- (Optional) AI-powered chat for health/growth questions (Amazon Bedrock)

---

## 3. User Types

- **Parent/Guardian**:  
  - Can register, log in, add/view/edit their baby’s data, visualize growth charts, and use the AI chat.
  - All data is private and associated only with their account.

*Future roles such as admin or pediatrician are out of scope for the MVP but may be considered in future versions.*

---

## 4. User Flow

1. **Registration**
   - User creates account with name, email, and password.

2. **Login**
   - User logs in with email and password.

3. **Dashboard**
   - View list of registered babies, add a new baby.

4. **Data Entry**
   - Select baby, input date, weight (kg), height (cm), head circumference (cm), sex.
   - Save record.

5. **Growth Visualization**
   - Display data in charts with WHO percentile curves.
   - Filter or browse records by date.

6. **AI Consultation (optional)**
   - User can ask questions about percentiles or health.
   - Receive AI-generated responses.

7. **Logout**
   - End session securely.

---

## 5. Functional Requirements

- Registration and login using AWS Cognito
- Only authenticated users can access their own data
- CRUD operations on babies and growth records
- Visualization of growth curves (Recharts or similar)
- Responsive design
- (Optional) AI chat via Bedrock

---

## 6. Technical Requirements

- **React** frontend
- **Vite** as the build too.
- **Tailwind CSS** as the CSS framework
- **AWS Lambda** (Python) backend
- **API Gateway** (REST API)
- **DynamoDB** (NoSQL database)
- **AWS Cognito** (authentication)
- **Amazon Bedrock** (optional, AI)
- **Recharts** (for charting)
- **GitHub** for source control
- Documentation in `/docs`

---

## 7. Notes & Considerations

- All data is user-scoped and private.
- MVP prioritizes essential features; future improvements will include more roles, reminders, and enhanced analytics.
- The design must be simple, intuitive, and mobile-friendly.

---

## 8. Future Ideas / Backlog

- Admin or pediatrician roles
- Push/email reminders for check-ups
- Multi-language support
- Data export (CSV/PDF)
- Integration with pediatric clinics

---

*(Last updated: YYYY-MM-DD)*
