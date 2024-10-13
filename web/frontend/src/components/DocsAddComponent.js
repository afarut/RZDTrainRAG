import React, { useState } from "react";

const DocsAddComponent = () => {
  const [docLink, setDocLink] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!docLink.trim()) {
      setErrorMessage("Ссылка на документ не может быть пустой.");
      return;
    }

    // Здесь должен быть код для обработки загрузки документа
    // Например, отправка ссылки на сервер

    // Имитация успешной загрузки
    setSuccessMessage("Документ успешно загружен!");
    setErrorMessage("");
    setDocLink("");
    
    // Время задержки для сообщения об успехе
    setTimeout(() => {
      setSuccessMessage("");
    }, 3000);
  };

  return (
    <div className="flex flex-col p-4 chat-win min-h-full content-center">
      <h3 className="text-lg font-semibold mb-4">Добавить документ</h3>
      <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
        <div>
          <input
            type="url"
            value={docLink}
            onChange={(e) => setDocLink(e.target.value)}
            placeholder="Вставьте ссылку на документ"
            className="block w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <button
          type="submit"
          className="mt-2 w-full bg-blue-600 text-white py-2 button rounded-md bg-main-color  focus:outline-none"
        >
          <span>Загрузить документ</span>
        </button>
      </form>
      {errorMessage && <p className="text-red-500 mt-2">{errorMessage}</p>}
      {successMessage && <p className="text-green-500 mt-2">{successMessage}</p>}
    </div>
  );
};

export default DocsAddComponent;
