import sys,os
sys.path.append(os.path.join(os.getcwd(),'roop\\'))
sys.path.append(os.path.join(os.getcwd(),'venv\\Scripts\\'))
sys.path.append(os.path.join(os.getcwd(),'venv\\Lib\\site-packages\\'))
print(sys.path)
from roop import core

if __name__ == '__main__':
    core.run()