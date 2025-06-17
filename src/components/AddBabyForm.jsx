import React from "react";
import InputField from "./InputField";
import PrimaryButton from "./PrimaryButton";

const AddBabyForm = ({ values, onChange, onSubmit }) => (
  <form className="bg-surface p-6 rounded-2xl shadow-md max-w-sm mx-auto" onSubmit={onSubmit}>
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
    <PrimaryButton type="submit" className="w-full mt-4">
      Save Baby
    </PrimaryButton>
  </form>
);

export default AddBabyForm;
