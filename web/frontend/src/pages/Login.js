import React, { useState } from "react";
import apiClient from "../components/apiClient";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (event) => {
    event.preventDefault();
    setErrorMessage("");

    apiClient
      .post("/auth/login", { email, password })
      .then((response) => {
        const token = response.data.token;
        localStorage.setItem("token", token);
        apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        console.log("Login successful:", response.data);
        navigate("/chat");
      })
      .catch((error) => {
        if (error.response && error.response.data.message === "Invalid credentials") {
          setErrorMessage("Неверные учетные данные. Попробуйте еще раз.");
        } else {
          setErrorMessage("Ошибка входа. Попробуйте позже.");
        }
        console.error("Error logging in:", error);
      });
  };

  return (
    <div className="flex min-h-screen flex-1 flex-col justify-center px-6 py-12 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <div className="flex-shrink-0 text-center">
          <h1 className="text-3xl font-bold main-color">ГИРЯ</h1>
        </div>
        <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
          Войти в аккаунт
        </h2>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium leading-6 text-gray-900"
            >
              Email адрес
            </label>
            <div className="mt-2">
              <input
                id="email"
                name="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset px-2 ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium leading-6 text-gray-900"
            >
              Пароль
            </label>
            <div className="mt-2">
              <input
                id="password"
                name="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset px-2 ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6"
              />
            </div>
          </div>

          {errorMessage && (
            <div className="text-red-600 text-sm">{errorMessage}</div>
          )}

          <div>
            <button
              type="submit"
              className="flex w-full justify-center button rounded-md bg-main-color px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-main-color focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              <span>Войти</span>
            </button>
          </div>
        </form>

        <p className="mt-10 text-center text-sm text-gray-500">
          Нет аккаунта?{" "}
          <a
            href="/register"
            className="font-semibold leading-6 main-color hover:main-color"
          >
            Регистрация здесь
          </a>
        </p>
      </div>
    </div>
  );
};

export default Login;
