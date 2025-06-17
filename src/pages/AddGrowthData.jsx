// .src/pages/AddGrowthData.jsx
// This is a simple page to add growth data for a baby.
import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import GrowthDataForm from "../components/GrowthDataForm";

const AddGrowthData = () => {
  const { babyId } = useParams();
  const navigate = useNavigate();

  const [values, setValues] = useState({
    weight: "",
    height: "",
    headCircumference: "",
    date: "",
    
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Include babyId in the submitted record
    console.log("Growth data submitted:", { babyId, ...values });
    // Here you would add logic to save data to the backend
    // Clear the form or redirect if desired:
    navigate(`/baby/${babyId}`); // to return to the baby's profile
  };

  return (
    <div className="flex justify-center items-center w-full h-full py-10">
      <GrowthDataForm
        values={values}
        onChange={handleChange}
        onSubmit={handleSubmit}
      />
    </div>
  );
};

export default AddGrowthData;
