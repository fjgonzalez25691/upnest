// .scr/components/LoginForm.jsx
// Purpose: A login form component for the UpNest application. Used to collect user credentials for authentication.
import React from "react";
import InputField from "./InputField";
import PrimaryButton from "./PrimaryButton";

const LoginForm = ({ onSubmit, values, onChange }) => (
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
  </form>
);

export default LoginForm;

// This LoginForm component provides a simple login interface for users to enter their email and password. It uses the InputField and PrimaryButton components for consistent styling and functionality.
