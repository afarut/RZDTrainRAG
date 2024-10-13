import React, { useState, useEffect, useRef } from "react"; 
import { TbTrain } from "react-icons/tb"; 
import { FaRobot } from "react-icons/fa"; 
import apiClient from "./apiClient";
import ChatSidebarComponent from "./ChatSidebarComponent";

const ChatComponent = () => {
  const [userMessage, setUserMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chats, setChats] = useState([]);
  const [isSending, setIsSending] = useState(false); 
  const [isAnimating, setIsAnimating] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false); // Состояние для отслеживания стриминга
  const [showMoreButton, setShowMoreButton] = useState(false);

  useEffect(() => {
    loadChats();

    // Проверяем наличие последнего чата в локальном хранилище при загрузке
    const lastChatId = localStorage.getItem("lastChatId");
    if (lastChatId) {
      loadChatHistory(lastChatId);
    }
  }, []);

  // Сохраняем в localStorage последний открытый чат
  const saveLastChatId = (chatId) => {
    localStorage.setItem("lastChatId", chatId);
  };

  const loadChats = () => {
    const token = localStorage.getItem("token");
    if (token) {
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
  
    apiClient
      .get("/api/chats")
      .then((response) => {
        const sortedChats = response.data.sort((a, b) => b.id - a.id);  // Сортировка по id в порядке убывания
        setChats(sortedChats);
      })
      .catch((error) => {
        console.error("Error fetching chats:", error);
        setErrorMessage("Не удалось загрузить чаты.");
      });
  };
  

  const loadChatHistory = (chatId) => {
    const token = localStorage.getItem("token");
    if (token) {
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }

    apiClient
      .get(`/api/chats/${chatId}`)
      .then((response) => {
        setChatHistory(response.data.messages);
        setCurrentChatId(chatId);
        saveLastChatId(chatId); // Сохраняем последний чат
      })
      .catch((error) => {
        console.error("Error fetching chat history:", error);
      });
  };

  const createNewChat = () => {
    const lastMessage = chatHistory.length > 0 ? chatHistory[chatHistory.length - 1].content : "Чат";

    const token = localStorage.getItem("token");
    if (token) {
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }

    apiClient
      .post("/api/chat", { session_name: lastMessage })
      .then((response) => {
        const newChatId = response.data.chat_id;
        setCurrentChatId(newChatId);
        loadChatHistory(newChatId);
        loadChats();
      })
      .catch((error) => {
        console.error("Error creating new chat:", error);
        setErrorMessage("Не удалось создать новый чат.");
      });
  };

  const deleteChat = (chatId) => {
    const token = localStorage.getItem("token");
    if (token) {
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }

    apiClient
      .delete(`/api/chats/${chatId}`)
      .then(() => {
        setChats((prevChats) => prevChats.filter((chat) => chat.id !== chatId));
        
        if (currentChatId === chatId) {
          setChatHistory([]);
          setCurrentChatId(null);
          localStorage.removeItem("lastChatId"); // Удаляем сохранённый ID при удалении чата
        }
      })
      .catch((error) => {
        console.error("Error deleting chat:", error);
        setErrorMessage("Не удалось удалить чат.");
      });
  };

  const sendMessage = () => {
    if (!userMessage.trim()) {
      return;
    }
  
    const token = localStorage.getItem("token");
    if (token) {
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
  
    const firstUserMessage = userMessage.trim();
  
    // Отображаем сообщение пользователя сразу в чате
    setChatHistory((prevHistory) => [
      ...prevHistory,
      { sender: "User", content: firstUserMessage },
      { sender: "Bot", content: "" } // Добавляем пустое сообщение от бота для последующего обновления
    ]);
  
    if (!currentChatId) {
      // Создание нового чата
      apiClient
        .post("/api/chat", { session_name: firstUserMessage })
        .then((response) => {
          const newChatId = response.data.chat_id;
          setCurrentChatId(newChatId);
  
          // Отправка первого сообщения и получение стримингового ответа
          return fetchStreamedResponse(firstUserMessage, newChatId);
        })
        .catch((error) => {
          console.error("Error creating chat or sending message:", error);
          setErrorMessage("Ошибка при создании чата или отправке сообщения.");
        });
    } else {
      // Отправка сообщения в существующем чате и получение стримингового ответа
      fetchStreamedResponse(firstUserMessage, currentChatId);
    }
  
    // Очищаем поле ввода
    setUserMessage('');
  };
  
  const fetchStreamedResponse = (message, chatId) => {
    setIsStreaming(true); // Устанавливаем флаг стриминга
    setShowMoreButton(false); // Скрываем кнопку "Подробнее"
  
    fetch("/api/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        message,
        session_id: chatId,
      }),
    })
      .then((response) => {
        if (!response.body) throw new Error("Нет данных от сервера.");
  
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botResponse = '';
  
        const processStream = ({ done, value }) => {
          if (done) {
            setIsStreaming(false); // Завершаем стриминг
            
            // Проверка на "Ответ не найден"
            if (botResponse.trim() !== "Ответ не найден") {
              setShowMoreButton(true); // Отображаем кнопку "Подробнее", если ответ был найден
            }
  
            return;
          }
  
          const chunk = decoder.decode(value, { stream: true });
          botResponse += chunk;
  
          // Обновляем последнее сообщение от бота и добавляем флаг isStreamed
          setChatHistory((prevHistory) => {
            const updatedHistory = [...prevHistory];
            updatedHistory[updatedHistory.length - 1].content = botResponse;
            updatedHistory[updatedHistory.length - 1].isStreamed = true; // Добавляем флаг
            return updatedHistory;
          });
  
          return reader.read().then(processStream);
        };
  
        return reader.read().then(processStream);
      })
      .catch((error) => {
        console.error("Ошибка стриминга данных:", error);
        setErrorMessage("Ошибка при получении данных от модели.");
      });
  };
  
  
  const handleMore = () => {
    fetch("/api/more", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        message: userMessage, // Используем то же сообщение
        session_id: currentChatId,
      }),
    })
      .then((response) => {
        if (!response.body) throw new Error("Нет данных от сервера.");
  
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let moreResponse = '';
  
        const processMoreStream = ({ done, value }) => {
          if (done) {
            return;
          }
  
          const chunk = decoder.decode(value, { stream: true });
          moreResponse += chunk;
  
          // Обновляем только последнее сообщение от бота
          setChatHistory((prevHistory) => {
            const updatedHistory = [...prevHistory];
            updatedHistory[updatedHistory.length - 1].content = moreResponse; // Обновляем последнее сообщение от бота
            return updatedHistory;
          });
  
          return reader.read().then(processMoreStream);
        };
  
        return reader.read().then(processMoreStream);
      })
      .catch((error) => {
        console.error("Ошибка при получении дополнительных данных:", error);
        setErrorMessage("Ошибка при получении дополнительных данных.");
      });
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen calc-height">
      <ChatSidebarComponent
        chats={chats}
        onSelectChat={loadChatHistory}
        onCreateChat={createNewChat}
        onDeleteChat={deleteChat}
        currentChatId={currentChatId}
      />
  
      <div className="flex-1 flex flex-col p-4 chat-win">
        <div className="flex-1 bg-gray-100 p-4 rounded-lg shadow-md overflow-y-auto">
          {errorMessage && <p className="text-red-500">{errorMessage}</p>}
  
          {currentChatId === null ? (
            <div className="flex flex-col items-center justify-center h-full">
              <p className="text-5xl font-bold main-color">ГИРЯ</p>
              <p className="text-lg font-medium mt-2 main-color">выполненно командой</p>
            </div>
          ) : chatHistory.length === 0 ? (
            <p className="text-gray-500">История сообщений пуста.</p>
          ) : (
            chatHistory.map((message, index) => (
              <div key={index} className={`mb-2 flex items-center ${message.sender === 'User' ? 'justify-end' : 'justify-start'}`}>
                {message.sender === "Bot" && <FaRobot className="mr-2 main-color" />}
                <div
                  className={`relative rounded-lg p-2 ${
                    message.sender === "User"
                      ? "bg-blue text-white"
                      : "bg-gray-200 text-gray-900"
                  }`}
                  style={{ wordWrap: "break-word", maxWidth: "70%" }} 
                >
                  {message.content}
  
                  {/* Условие для отображения кнопки "Подробнее" */}
                  {message.sender === "Bot" && message.content !== "Ответ не найден" && message.isStreamed && !message.isMore && (
                    <div className="text-right mt-2">
                      <button 
                        onClick={() => handleMore(message.content)} 
                        className="text-blue-500 hover:underline transition-opacity opacity-80 hover:opacity-100"
                        style={{ fontSize: "12px", position: "relative", bottom: "0", right: "0" }}
                      >
                        Подробнее
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
  
        {currentChatId && (
          <div className="flex mt-4">
            <textarea
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Введите сообщение..."
              className="block w-full resize-none rounded-l-md border-0 py-2 pl-3 pr-3 max-h-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm"
            />
            <div className="button-container"> 
              <button
                onClick={sendMessage}
                className="ml-2 relative flex items-center justify-center w-10 h-10 bg-blue rounded-r-md focus:outline-none"
              >
                <TbTrain
                  className={`text-white transform transition-transform ${
                    isSending ? "translate-x-full" : ""
                  }`}
                  style={{ transition: "transform 0.5s ease-in-out" }}
                />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
  
    
  
};

export default ChatComponent;
