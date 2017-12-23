import socketserver as ss
import socket
import sys, os; sys.path.insert(0, os.getenv('FLOW_dir','/home/yaguo/scripts/eda2json/'))
import eda2json as ej



class ThreadedTCPRequestHandler(ss.BaseRequestHandler):
    client_addr = []
    ### server only accept below input and return it's value
        # INST + key
        # NET + key
        # PIN + key
    #def __init__(self,topHash):
    #    super().__init__(self)
    #    self.topHash = topHash
    #    #print(type(topHash),topHash["INST"]["FCFP_TIE_HI__PD_VDDCR_SOC__1528"])
    def setup(self):
        ip = self.client_address[0].strip()     #get client IP
        port = self.client_address[1]           #get clinet port
        print(ip+":"+str(port)+" is connect")   #
        #client_addr.append(self.client_address)

    def handle(self):
        self.setup()
        global topHash
        print(type(topHash),topHash["INST"]["FCFP_TIE_HI__PD_VDDCR_SOC__1528"])
        ##print("connected :", self.client_address)
        ##self.request.sendall(b"Welcome to PyServer")
        ##self.request.sendall(b"DONE")
        #data = self.request.recv(1024).strip().decode()
        #print("get data", data)
        #cmds = data.split(":")
        #if len(cmds) == 2:
        #    print("keys,value", cmds ,self.topHash[cmds[0]][cmds[1]])
        #    key = self.topHash[cmds[0]][cmds[1]]
        #    self.request.sendall(key)
        #    self.request.sendall(b"DONE")
        #
        #else:
        #    print("wrong cmd",cmds)
        ##print("{} wrote:".format(self.client_address[0]))


class ThreadedTCPServer(ss.ThreadingMixIn,ss.TCPServer):
    pass
paramHash = ej.params2Json("/proj/ariel_pd_fct3/fct_eco_runs/func_flat_normal/fct127_ECO_Func_Flat_EcoRoute_Dec18/tile.params")
nickName = paramHash["NICKNAME"]
rundir = paramHash["BASE_DIR"] +"/data/"
fctBomFile = rundir + "bom.json"
topName = paramHash["TOP_MODULE"]


topHash = {}
topHash["INST"] = ej.loadJson(rundir + topName + ".only.inst.json.gz")["INST"]
#topHash["NET"]  = ej.loadJson(rundir + topName + ".net.json.gz")
#topHash["PIN"]  = ej.loadJson(rundir + topName + ".pin.json.gz")


PORT = 1105
HOST = socket.getfqdn()

servHash = {}
servHash[nickName]= {}
servHash[nickName]["PHY"] = {}
servHash[nickName]["PHY"]["HOST"] = HOST
servHash[nickName]["PHY"]["PORT"] = PORT

ej.saveJson(servHash,rundir+"host.json")
#print("hash",topHash["INST"]["FCFP_TIE_HI__PD_VDDCR_SOC__1528"])
server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

print(server.server_address)
server.serve_forever()
