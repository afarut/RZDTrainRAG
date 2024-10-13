import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="relative min-h-screen flex flex-col bg-white">
      <main className="relative z-10 flex-grow flex flex-col items-center justify-center text-center p-6">
        <div className="mb-6 flex flex-col items-center">
          <a href="/">
            <img
              alt="Логотип"
              src="https://universitetrzd.ru/local/media/images/logo-1.svg"
              className="h-32 transition-transform transform hover:scale-105"
            />
          </a>
          <h1 className="text-5xl font-bold my-4 main-color">QnA чат-бот</h1>
        </div>
        {/* Кнопки */}
        <div className="flex mt-4 space-x-4">
          <Link
            to="/info"
            className="bg-gray-300 text-black font-semibold button buttong py-2 px-4 rounded-md transition animate-slideIn"
          >
            <span>Узнать больше</span>
          </Link>
          <Link
            to="/chat"
            className="relative button bg-red-600 text-white font-semibold py-2 px-4 rounded-md transition animate-slideIn duration-500 hover:animate-gradientAnimation"
          >
            <span>Попробовать</span>
          </Link>
        </div>
      </main>

      <footer className="relative z-10 w-full py-4 text-center bg-transparent">
        <p className="text-gray-200">Разработан командой ГИРЯ</p>
      </footer>
    </div>
  );
};

export default Home;
