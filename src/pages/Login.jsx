// src/pages/Login.jsx
import React, { useState } from "react";
import LoginForm from "../components/LoginForm";



const Login = () => {
  const [values, setValues] = useState({
    email: "",
    password: ""
  });

  const handleChange = (e) => {
    setValues({
      ...values,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // authentication logic goes here
    console.log("Email:", values.email);
    console.log("Password:", values.password);
  };

  return (
    <div className=" flex items-center justify-center bg-background">
      <LoginForm values={values} onChange={handleChange} onSubmit={handleSubmit} />
    </div>
  );
};

export default Login;
