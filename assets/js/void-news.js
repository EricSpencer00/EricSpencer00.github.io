(() => {
  const board = document.querySelector('.void-board');
  if (!board) return;
  board.querySelector('.void-compose').hidden = false;
  const button = board.querySelector('.void-stop');
  button.addEventListener('click', () => {
    const replies = board.querySelector('.void-replies');
    for (const [direction, text] of [
      ['sent', 'STOP'],
      ['received', 'You have successfully unsubscribed from the void. The void is taking this personally.']
    ]) {
      const message = document.createElement('div');
      message.className = `message message-${direction} message-tail`;
      const content = document.createElement('div');
      content.className = 'message-content';
      const bubble = document.createElement('div');
      bubble.className = 'message-bubble';
      const body = document.createElement('div');
      body.className = 'message-text';
      body.textContent = text;
      bubble.append(body);
      content.append(bubble);
      message.append(content);
      replies.append(message);
    }
    button.disabled = true;
    button.textContent = 'Unsubscribed';
    board.querySelector('.void-compose > span').textContent = 'left the void on read.';
  }, { once: true });
})();
