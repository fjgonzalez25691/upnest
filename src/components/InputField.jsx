// .src/components/InputField.jsx
// Purpose: A reusable input field component for the UpNest application. Used for forms and user input.

import React from "react";

const InputField = ({
  label,
  type = "text",
  name,
  value,
  onChange,
  placeholder,
  className = "",
  ...props
}) => (
  <div className={`mb-4 ${className}`}>
    {label && <label className="block text-textmain mb-1">{label}</label>}
    <input
      type={type}
      name={name}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="w-full p-3 rounded-lg border border-gray-300 text-textmain placeholder-textsubtle focus:outline-none focus:ring-2 focus:ring-primary"
      {...props}
    />
  </div>
);

export default InputField;
