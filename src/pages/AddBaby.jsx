// .src/pages/AddBaby.jsx
// Form for adding a new baby

import React, { useState } from "react";
import AddBabyForm from "../components/AddBabyForm";

const AddBaby = () => {
  const [values, setValues] = useState({
    name: "",
    dob: "",
    premature: false,
    gestationalWeek: "",
  });

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    setValues((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
      // Si desmarcas prematuro, limpias el valor de semana
      ...(name === "premature" && !checked ? { gestationalWeek: "" } : {}),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Baby registration values:", values);
    // Aquí irá la lógica real de registro
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <AddBabyForm values={values} onChange={handleChange} onSubmit={handleSubmit} />
    </div>
  );
};

export default AddBaby;
