// .scr/components/SelectField.jsx
// Purpose: A reusable select field component for the UpNest application. Used for forms and user input.

import React from "react";

const SelectField = ({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
  className = "",
  ...props
}) => (
  <div className={`mb-4 ${className}`}>
    {label && (
      <label htmlFor={name} className="block mb-1 font-medium">
        {label}
      </label>
    )}
    <select
      id={name}
      name={name}
      value={value}
      onChange={onChange}
      required={required}
      className="w-full border rounded px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-primary"
      {...props}
    >
      <option value="">Select</option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  </div>
);

export default SelectField;