// .src/components/GrowthDataForm.jsx
// Purpose: A form component for entering growth data (weight, height, head circumference, date, and sex)

import React from "react";
import InputField from "./InputField";
import PrimaryButton from "./PrimaryButton";

const GrowthDataForm = ({ values, onChange, onSubmit, onCancel }) => (
  <form className="bg-surface p-6 rounded-2xl shadow-md w-full max-w-xl mx-auto" onSubmit={onSubmit}>
    <h2 className="text-xl font-bold mb-4 text-primary">Add Growth Data</h2>
    <InputField
      label="Weight (kg)"
      type="number"
      name="weight"
      value={values.weight}
      onChange={onChange}
      step="0.01"
      min="0"
      placeholder="Enter weight"
      required
    />
    <InputField
      label="Height (cm)"
      type="number"
      name="height"
      value={values.height}
      onChange={onChange}
      step="0.1"
      min="0"
      placeholder="Enter height"
      required
    />
    <InputField
      label="Head Circumference (cm)"
      type="number"
      name="headCircumference"
      value={values.headCircumference}
      onChange={onChange}
      step="0.1"
      min="0"
      placeholder="Enter head circumference"
      required
    />
    <InputField
      label="Date"
      type="date"
      name="date"
      value={values.date}
      onChange={onChange}
      required
    />
    <div className="flex flex-col-reverse sm:flex-row gap-3 mt-6">
      <PrimaryButton 
        type="submit" 
        variant="save"
        className="flex-1"
      >
        Save Growth Data
      </PrimaryButton>
      <PrimaryButton 
        type="button"
        onClick={onCancel}
        variant="cancel"
        className="flex-1"
      >
        Cancel
      </PrimaryButton>
    </div>
   
  </form>
);

export default GrowthDataForm;