import React from "react";
import InputField from "./InputField";
import PrimaryButton from "./PrimaryButton";
import SelectField from "./SelectField";

const AddBabyForm = ({ values, onChange, onSubmit, onCancel, isSubmitting = false }) => (
  <form className="bg-surface p-6 rounded-2xl shadow-md max-w-xl w-full mx-auto" onSubmit={onSubmit}>
    <h2 className="text-xl font-bold mb-4 text-primary">Register Baby</h2>
    <InputField
      label="Name"
      name="name"
      value={values.name}
      onChange={onChange}
      placeholder="Baby's name"
    />
    <InputField
      label="Date of Birth"
      type="date"
      name="dob"
      value={values.dob}
      onChange={onChange}
    />
    <SelectField
      label="Sex"
      name="sex"
      value={values.sex}
      onChange={onChange}
      required
      placeholder="Select baby's sex"
      options={[
        { value: "male", label: "Male" },
        { value: "female", label: "Female" }
        
      ]}
    />

    <div className="mb-4">
      <label className="block text-textmain mb-1">
        <input
          type="checkbox"
          name="premature"
          checked={values.premature}
          onChange={onChange}
          className="mr-2"
        />
        Premature birth?
      </label>
    </div>
    {values.premature && (
      <InputField
        label="Gestational week (if premature)"
        type="number"
        name="gestationalWeek"
        value={values.gestationalWeek}
        onChange={onChange}
        min={20}
        max={37}
        placeholder="e.g. 34"
      />
    )}
    <div className="flex flex-col-reverse sm:flex-row gap-3 mt-6">
      <PrimaryButton 
        type="submit" 
        variant="save"
        className="flex-1" 
        disabled={isSubmitting}
      >
        {isSubmitting ? "Saving..." : "Save Baby"}
      </PrimaryButton>
      <PrimaryButton 
        type="button"
        onClick={onCancel}
        variant="cancel"
        className="flex-1"
        disabled={isSubmitting}
      >
        Cancel
      </PrimaryButton>
    </div>
  </form>
);

export default AddBabyForm;
