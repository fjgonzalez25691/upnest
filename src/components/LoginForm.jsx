// .scr/components/LoginForm.jsx
// Purpose: A login form component for the UpNest application. Used to collect user credentials for authentication.
import React from "react";
import { Link } from "react-router-dom";
import InputField from "./InputField";
import PrimaryButton from "./PrimaryButton";

const LoginForm = ({ onSubmit, values, onChange, onCancel }) => (
  <form className="bg-surface p-6 rounded-2xl shadow-md max-w-sm mx-auto" onSubmit={onSubmit}>
    <h2 className="text-xl font-bold mb-4 text-primary">Login</h2>
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
    <PrimaryButton type="submit" className="w-full mt-4">
      Log In
    </PrimaryButton>
    <PrimaryButton 
      type="button" 
      className="w-full mt-4" 
      onClick={onCancel}
      variant="cancel">
      Cancel
    </PrimaryButton>
    <div className="text-center mt-4">
      <span className="text-textsubtle">
        Don't have an account?{" "}
        <Link to="/register" className="text-primary underline hover:text-primary/80">Register</Link>
      </span>
    </div>
  </form>
);

export default LoginForm;
