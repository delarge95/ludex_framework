const WebSocket = require('ws');
const http = require('http');

const ws = new WebSocket('ws://127.0.0.1:9091/ws');

ws.on('open', function open() {
  console.log('Connected to WebSocket');
  
  // Trigger generation
  const data = JSON.stringify({
    concept: "Cyberpunk farming sim",
    genre: "Simulation"
  });

  const req = http.request({
    hostname: '127.0.0.1',
    port: 9091,
    path: '/start',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  }, (res) => {
    console.log(`Start request status: ${res.statusCode}`);
    res.on('data', (d) => {
      process.stdout.write(d);
    });
  });

  req.on('error', (error) => {
    console.error('Error triggering generation:', error);
  });

  req.write(data);
  req.end();
});

ws.on('message', function incoming(data) {
  const message = JSON.parse(data);
  console.log('Received:', message.type);
  
  if (message.type === 'tool_call_started') {
    console.log('Tool Started:', message.tool);
  } else if (message.type === 'tool_call_completed') {
    console.log('Tool Completed:', message.tool);
  } else if (message.type === 'status' && message.status === 'completed') {
    console.log('Generation Completed!');
    ws.close();
    process.exit(0);
  } else if (message.type === 'error') {
    console.error('Error:', message.message);
    ws.close();
    process.exit(1);
  }
});

ws.on('error', function error(err) {
  console.error('WebSocket error:', err);
});

