// .scr.components/RegisterForm.jsx
// Purpose: A registration form component for the UpNest application. Used to collect user information for account creation.
import React from "react";
import InputField from "./InputField";
import PrimaryButton from "./PrimaryButton";
import { Link } from "react-router-dom";
import SelectField from "./SelectField";

const RegisterForm = ({ values, onChange, onSubmit, onCancel }) => (
  <form
    className="bg-surface p-6 rounded-2xl shadow-md w-full max-w-xl mx-auto"
    onSubmit={onSubmit}
  >
    <h2 className="text-xl font-bold mb-4 text-primary">Register</h2>
    <InputField
      label="Name"
      name="name"
      value={values.name}
      onChange={onChange}
      placeholder="Your name"
      required
    />
    <InputField
      label="Email"
      type="email"
      name="email"
      value={values.email}
      onChange={onChange}
      placeholder="you@example.com"
      required
    />
    <InputField
      label="Password"
      type="password"
      name="password"
      value={values.password}
      onChange={onChange}
      placeholder="********"
      required
    />
    <InputField
      label="Confirm Password"
      type="password"
      name="confirmPassword"
      value={values.confirmPassword}
      onChange={onChange}
      placeholder="********"
      required
    />
    <div className="flex flex-col sm:flex-row gap-3 mt-6">
      <PrimaryButton type="submit" className="w-full">
        Register
      </PrimaryButton>
      <PrimaryButton type="button" className="w-full" onClick={onCancel} variant="cancel">
        Cancel
      </PrimaryButton>
    </div>
    <div className="mt-4 text-center">
      <span className="text-sm text-gray-600">Already have an account? </span>
      <Link to="/login" className="text-primary font-medium hover:underline">
        Login
      </Link>
    </div>
  </form>
);

export default RegisterForm;
