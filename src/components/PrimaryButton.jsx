// .src/components/PrimaryButton.jsx
// Pourpose: A reusable primary button component for the UpNest application. Used for primary actions like submitting forms or confirming actions.

import React from "react";

const variantStyles = {
  save:
    "[background:var(--color-primary)] text-white " +
    "hover:[background:color-mix(in_srgb,var(--color-primary)80%,black_20%)]",
  cancel:
    "[background:var(--color-cancel)] text-white " +
    "hover:[background:color-mix(in_srgb,var(--color-cancel)80%,black_20%)]",
  danger:
    "[background:var(--color-danger)] text-white " +
    "hover:[background:color-mix(in_srgb,var(--color-danger)80%,black_20%)]",
};
;


const PrimaryButton = ({
  children,
  variant = "save",
  className = "",
  ...props
}) => (
  <button
    type={props.type || "button"}
    className={
      `flex-1 rounded-lg px-4 py-2 font-semibold transition ${variantStyles[variant] || ""} ${className}`
    }
    {...props}
  >
    {children}
  </button>
);

export default PrimaryButton;
