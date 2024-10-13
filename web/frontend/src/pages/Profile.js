import React, { useEffect, useState } from "react";
import apiClient from "../components/apiClient";
import { useNavigate } from "react-router-dom";
import NavbarComponent from "../components/NavbarComponent";
const Profile = () => {
  const [charts, setCharts] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedChart, setSelectedChart] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }

    apiClient
      .get("/api/profile")
      .then((response) => {
        setCharts(response.data.charts);
        setErrorMessage("");
      })
      .catch((error) => {
        setErrorMessage("Failed to load charts.");
        console.error("Error loading charts:", error);
      });
  }, []);

  const handleChartClick = (chart) => {
    setSelectedChart(chart);
    navigate(`/chart/${chart.id}`);
  };

  return (
    <div>
      <NavbarComponent />
      <div className="flex flex-col items-center justify-center p-4 calc-height">
        <div className="w-full max-w-4xl bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4">Ваши диаграммы</h2>
          {errorMessage && <p className="text-red-500">{errorMessage}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {charts.length > 0 ? (
              charts.map((chart, index) => (
                <div
                  key={index}
                  className="bg-gray-100 p-4 rounded-lg shadow-md cursor-pointer hover:bg-gray-200"
                  onClick={() => handleChartClick(chart)}
                >
                  <h3 className="text-lg font-semibold truncate">
                    {chart.title}
                  </h3>
                  <p className="text-gray-500">
                    Нажмите, чтобы просмотреть детали
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500">
                У вас пока нет сохраненных диаграмм.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
