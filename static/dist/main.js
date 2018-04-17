var term,
    protocol,
    pid,
    charWidth,
    charHeight;

var terminalContainer = document.getElementById('terminal-container');

function setTerminalSize () {
  var cols = 80,
      rows = 24,
      width = '1000px',
      height ='500px';

  terminalContainer.style.width = width;
  terminalContainer.style.height = height;
  term.resize(cols, rows);
}

createTerminal();
var sock;
function createTerminal() {
  console.log("ddd");
  // Clean terminal
  while (terminalContainer.children.length) {
    terminalContainer.removeChild(terminalContainer.children[0]);
  }
  term = new Terminal({
    cursorBlink: false,
    scrollback: 1000,
    tabStopWidth: 8
  });

  term.open(terminalContainer);
  term.fit();

  var initialGeometry = term.proposeGeometry(),
      cols = 80,
      rows = 24;
  console.log("connect1");     
  sock = io.connect('http://localhost:5000/echo');
  console.log("connect2");
  sock.on('connect', runRealTerminal);
  sock.on('disconnect', runFakeTerminal);
  // sock.on('message', function (e) {
  //       console.log(e);
  //       console.warn(e.data);
  // });
  // var host = window.location.hostname + ':' + window.location.port + '/';
  // socketURL = 'ws://'+host+'/bash';
  // console.log(socketURL)
  // socket = new WebSocket(socketURL);
  // socket.onopen = runRealTerminal;
  //     socket.onclose = runFakeTerminal;
  //     socket.onerror = runFakeTerminal;
  //     socket.onmessage = function (e) {
  //             console.log(e);
  //             console.warn(e.data);
  // }
}

function runRealTerminal() {
  sock.emit('join', {room: '001',username:'liubiao'});
  term.attach(sock);
  term._initialized = true;
}

function runFakeTerminal() {
  if (term._initialized) {
    return;
  }

  term._initialized = true;

  var shellprompt = '$ ';

  term.prompt = function () {
    term.write('\r\n' + shellprompt);
  };

  term.writeln('Welcome to xterm.js');
  term.writeln('This is a local terminal emulation, without a real terminal in the back-end.');
  term.writeln('Type some keys and commands to play around.');
  term.writeln('');
  term.prompt();

  term.on('key', function (key, ev) {
    var printable = (
      !ev.altKey && !ev.altGraphKey && !ev.ctrlKey && !ev.metaKey
    );

    if (ev.keyCode == 13) {
      term.prompt();
    } else if (ev.keyCode == 8) {
     // Do not delete the prompt
      if (term.x > 2) {
        term.write('\b \b');
      }
    } else if (printable) {
      term.write(key);
    }
  });

  term.on('paste', function (data, ev) {
    term.write(data);
  });
}
