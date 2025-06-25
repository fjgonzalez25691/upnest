import axiosClient from "./axiosClient";

/**
 * Sends baby growth data to the backend to calculate weight percentile.
 * @param {Object} data - Baby measurement data
 * @returns {Object} response containing percentile, z-score, and LMS values
 * @throws {Error} if the request fails or the backend returns an error
 */
export async function calculatePercentile(data) {
  try {
    const response = await axiosClient.post("/upnest-percentile", data);
    return response.data;
  } catch (error) {
    const msg =
      error.response?.data?.error ||
      error.message ||
      "Unknown API error";
    throw new Error(msg);
  }
}
