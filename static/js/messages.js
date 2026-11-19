(() => {
  const panel = document.querySelector(".chat-panel");
  if (!panel || typeof io !== "function") return;

  const conversationId = Number(panel.dataset.conversationId);
  const currentUserId = Number(panel.dataset.currentUserId);
  const messageList = document.getElementById("chat-messages");
  const status = document.getElementById("chat-status");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-body");
  const socket = io();

  const appendMessage = (message) => {
    if (messageList.querySelector(`[data-message-id="${message.id}"]`)) return;
    const article = document.createElement("article");
    article.className = `chat-message ${message.sender_id === currentUserId ? "mine" : ""}`;
    article.dataset.messageId = message.id;
    const sender = document.createElement("b");
    sender.textContent = message.sender_name;
    const body = document.createElement("p");
    body.textContent = message.body;
    const time = document.createElement("time");
    time.textContent = message.created_at;
    article.append(sender, body, time);
    messageList.append(article);
    messageList.scrollTop = messageList.scrollHeight;
  };

  socket.on("connect", () => {
    status.textContent = "Connected";
    socket.emit("join_conversation", { conversation_id: conversationId });
  });
  socket.on("disconnect", () => { status.textContent = "Reconnecting…"; });
  socket.on("chat_joined", () => { status.textContent = "Private chat connected"; });
  socket.on("chat_error", (event) => { status.textContent = event.message; });
  socket.on("new_message", appendMessage);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const body = input.value.trim();
    if (!body) return;
    socket.emit("send_message", { conversation_id: conversationId, body });
    input.value = "";
  });
  messageList.scrollTop = messageList.scrollHeight;
})();
