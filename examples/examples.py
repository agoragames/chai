from chai import Chai
import socket
import datetime

######################################
## Mocking sockets
######################################
def connect():
  sock = socket.socket()
  sock.bind(('127.0.0.1', 10000))
  return sock.recv(1024)

def get_host():
  return socket.gethostname()

class SocketTestCase(Chai):
    
  def test_socket(self):
    mock_socket = self.mock()
    self.mock(socket, 'socket')
    self.expect(socket.socket.__call__).returns(mock_socket)
    
    self.expect(mock_socket.bind).args(('127.0.0.1' , 10000))
    self.expect(mock_socket.recv).args(1024).returns("HELLO WORLD")
    
    self.assert_equals(connect(), "HELLO WORLD")

  def test_get_host(self):
    self.mock(socket, 'gethostname')
    self.expect(socket.gethostname.__call__).returns("my_host")
    self.assert_equals(get_host(), "my_host")


######################################
## Mocking datetime.now
######################################
def now():
  return datetime.datetime.now()

class DatetimeTestCase(Chai):
    
    def test_now(self):
      current_now = datetime.datetime.now() # Save for later

      # NOTE: In c python you are not allow to mock built types so we have to mock
      # the entire module.moc
      mock_datetime = self.mock(datetime, 'datetime')
      self.expect(mock_datetime.now).returns(current_now)
      
      self.assert_equals(now(), current_now)

if __name__ == '__main__':
  import unittest2
  unittest2.main()

