// src/pages/Register.jsx
// Description: Register page component for UpNest application
// Purpose: This page allows users to register for a new account in the UpNest application.
import React, { useState} from "react";  
import RegisterForm from "../components/RegisterForm";



const Register = () => {
  const [values, setValues] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e) => {
    setValues({ ...values, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Register values:", values);
    // Registration logic goes here
  };

  return (
    <div className=" flex items-center justify-center w-full max-w-xl mx-auto bg-background">
      <RegisterForm values={values} onChange={handleChange} onSubmit={handleSubmit} />
    </div>
  );
};

export default Register;
