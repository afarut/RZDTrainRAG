import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { lineWobble } from "ldrs";

lineWobble.register();

const ProtectedRoute = ({ children }) => {
  const [authStatus, setAuthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem("token");

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    if (!token) {
      setAuthStatus("no_token");
    } else {
      const tokenData = JSON.parse(atob(token.split(".")[1]));
      const now = Math.floor(Date.now() / 1000);

      if (tokenData.exp < now) {
        setAuthStatus("expired");
      } else {
        setAuthStatus("authorized");
      }
    }

    return () => clearTimeout(timer);
  }, [token]);

  if (loading || authStatus === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <l-line-wobble size="100" speed="0.9" color="rgb(226 26 26)"></l-line-wobble>
      </div>
    );
  }

  if (authStatus === "no_token") {
    return <Navigate to="/register" replace />;
  }

  if (authStatus === "expired") {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
