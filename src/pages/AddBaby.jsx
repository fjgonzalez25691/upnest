// src/pages/AddBaby.jsx
// Form for adding a new baby with user authentication integration

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AddBabyForm from "../components/AddBabyForm";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { createBaby } from "../services/babyApi";

const AddBaby = () => {
  const navigate = useNavigate();
  const { userId } = useCurrentUser();
  
  const [values, setValues] = useState({
    name: "",
    dob: "",
    sex: "",
    premature: false,
    gestationalWeek: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    setValues((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
      // Si desmarcas prematuro, limpias el valor de semana
      ...(name === "premature" && !checked ? { gestationalWeek: "" } : {}),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!userId) {
      console.error("No user ID available");
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Prepare baby data with user ID
      const babyData = {
        ...values,
        userId: userId, // Associate baby with current user
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      console.log("Baby registration data:", babyData);
      
      // Call the API to create the baby
      const response = await createBaby(babyData);
      console.log("Baby created successfully:", response);
      
      alert("Baby added successfully!");
      navigate("/dashboard");
      
    } catch (error) {
      console.error("Error adding baby:", error);
      alert("Error adding baby. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    // Check if form has been modified
    const hasChanges = values.name || values.dob || values.sex || values.premature || values.gestationalWeek;
    
    if (hasChanges) {
      const confirmLeave = window.confirm(
        "You have unsaved changes. Are you sure you want to leave this page?"
      );
      if (!confirmLeave) {
        return;
      }
    }
    
    // Navigate back to dashboard
    navigate("/dashboard");
  };

  return (
    <div className="bg-background py-8 px-6 flex-1 grid place-items-center">
      <AddBabyForm 
        values={values} 
        onChange={handleChange} 
        onSubmit={handleSubmit} 
        onCancel={handleCancel}
        isSubmitting={isSubmitting}
      />
    </div>
  );
};

export default AddBaby;
