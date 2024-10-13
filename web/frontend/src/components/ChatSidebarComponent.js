  import React from "react";
  import { FaTrash } from "react-icons/fa";

  const ChatSidebarComponent = ({ chats, onSelectChat, onCreateChat, onDeleteChat, currentChatId }) => {
    return (
      <div className="w-64 bg-gray-200 p-4 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">Ваши чаты</h3>

        <button
          onClick={onCreateChat}
          className="group relative inline-flex button items-center justify-center px-4 py-2 mb-4 overflow-hidden text-sm font-medium text-white bg-main-color rounded-lg focus:outline-none focus:ring transition-transform transform active:scale-95"
        >
          <span className="relative">Создать новый чат</span>
        </button>

        {chats.length === 0 ? (
          <p className="text-gray-500">Чатов пока нет. Начните новый чат.</p>
        ) : (
          <ul>
            {chats.map((chat) => (
              <li
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`flex justify-between items-center p-2 mb-2 transition animate-slideIn rounded-lg shadow cursor-pointer hover:bg-gray-100 ${
                  currentChatId === chat.id ? "bg-gray-100 border-l-4 border-blue" : "bg-white"
                }`}
              >
                <div className="flex-1">
                  {chat.first_message || `Чат ${chat.id}`}  {/* Используем первое сообщение или ID чата */}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  className="ml-2 p-2 transition-transform transform hover:scale-105"
                >
                  <FaTrash className="hover:main-color transition-colors duration-300" />
                </button>
              </li>
            ))}
          </ul>




        )}
      </div>
    );
  };

  export default ChatSidebarComponent;
