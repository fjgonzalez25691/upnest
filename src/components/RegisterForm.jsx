// .scr.components/RegisterForm.jsx
// Purpose: A registration form component for the UpNest application. Used to collect user information for account creation.
import React from "react";
import { Link } from "react-router-dom";
import InputField from "./InputField";
import PrimaryButton from "./PrimaryButton";

const RegisterForm = ({ onSubmit, values, onChange }) => (
  <form className="bg-surface p-6 rounded-2xl shadow-md w-full max-w-sm mx-auto" onSubmit={onSubmit}>
    <h2 className="text-xl font-bold mb-4 text-primary">Register</h2>
    <InputField
      label="Name"
      name="name"
      value={values.name}
      onChange={onChange}
      placeholder="Your name"
    />
    <InputField
      label="Email"
      type="email"
      name="email"
      value={values.email}
      onChange={onChange}
      placeholder="you@example.com"
    />
    <InputField
      label="Password"
      type="password"
      name="password"
      value={values.password}
      onChange={onChange}
      placeholder="********"
    />
    <InputField
      label="Confirm Password"
      type="password"
      name="confirmPassword"
      value={values.confirmPassword}
      onChange={onChange}
      placeholder="********"
    />
    <PrimaryButton type="submit" className="w-full mt-4">
      Register
    </PrimaryButton>
    <div className="text-center mt-4">
      <span className="text-textsubtle">
        Already have an account?{" "}
        <Link to="/login" className="text-primary underline hover:text-primary/80">Login</Link>
      </span>
    </div>
  </form>
);

export default RegisterForm;
