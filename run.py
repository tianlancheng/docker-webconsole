# -*- coding: utf-8 -*-
from flask import Flask, render_template,session
from flask_socketio import SocketIO, emit,send
from flask_socketio import join_room, leave_room
import docker
from threading import Lock
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode='gevent'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='1.35',timeout=10)



def isActive(sock):
	try:
		sock.getpeername()
		return True
	except:
		return False


def background_thread(sock,room):
	"""Example of how to send server generated events to clients."""
	try:
		while True:
			resp = sock.recv(1024)
			# print('recv:'+resp)
			if resp:
				socketio.send({'data': resp},room=room,namespace='/echo')
			else:
				print 'quit'
				break;
	except Exception,e:
		print(e)
	finally:
		print("close sock")
		try:
			sock.send('exit\n')
			sock.close()
		except:
			sock.close()

thread_lock = Lock()
def create_exec(room):
	with thread_lock:
		try:
			container=docker_client.containers.get(room)
			if(container.status != 'running'):
				container.restart
		except:
			container = docker_client.containers.run(image='python:2', command="/bin/bash", 
				name=room,remove=False, detach=True,stdin_open=True, tty=True)

	print('start thread:'+room)
	command = ["/bin/sh","-c",'TERM=xterm-256color; export TERM; [ -x /bin/bash ] && ([ -x /usr/bin/script ] && /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) || exec /bin/sh']
	sock = container.exec_run(cmd=command,tty=True,stdin=True,detach=False,stream=False,socket=True).output
	sock.settimeout(600)
	oldsock=session.get('sock',None)
	close_sock()
	session['sock']=sock
	socketio.start_background_task(target=background_thread,sock=sock,room=room) 

def close_sock():
	sock=session.get('sock',None)
	if(sock):
		if(isActive(sock)):
			sock.send('exit\n')
		sock.close

@app.route('/')
def index():
	return render_template('index.html')

@socketio.on('message', namespace='/echo')
def test_message(message):
	# print("dddd:"+message)
	sock=session.get('sock',None)
	if(sock and isActive(sock)):
		sock.send(message)
	else:
		send({'data': 'disconnect to container'})

@socketio.on('connect', namespace='/echo')
def test_connect():
	print('connect')
	# send({'data': 'Connected'})

@socketio.on('disconnect', namespace='/echo')
def test_disconnect():
	close_sock()
	print('Client disconnected')

@socketio.on('join', namespace='/echo')
def on_join(data):
	print(' entered the room:'+data['room'])
	room = data['room']
	join_room(room)
	session['username']=data.get('username',"unknown")
	session['room']=room
	close_sock()
	create_exec(room)
			
@socketio.on('leave', namespace='/echo')
def on_leave(data):
	username = data['username']
	room = data['room']
	leave_room(room)
	print(username + ' has left the room.')

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print("dd:"+e)

if __name__ == '__main__':
	socketio.run(app)