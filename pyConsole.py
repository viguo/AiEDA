import sys, os; sys.path.insert(0, os.getenv('FLOW_dir','/home/yaguo/scripts/eda2json/'))
import pyLib as ej
import socket


#paramHash = ej.params2Json("/proj/ariel_pd_fct3/fct_eco_runs/func_flat_normal/fct127_ECO_Func_Flat_EcoRoute_Dec18/tile.params")
paramHash = ej.params2Json("./tile.params")
nickName = paramHash["NICKNAME"]
rundir = paramHash["BASE_DIR"] +"/data/"
fctBomFile = rundir + "bom.json"
topName = paramHash["TOP_MODULE"]

hostHash = ej.loadJson("./data/host.json")
hostName = hostHash[nickName]["PHY"]["HOST"]
hostPort = hostHash[nickName]["PHY"]["PORT"]

#print(hostName,hostPort)


server = (hostName,hostPort)

topHash = {}
topHash["HOST"] =  server

instName = "I2TopCts_cts_buf_118595122153"
c = ej.get_cell(topHash,instName)


#while True:
#    dataAll = ""
#    i = 0
#    while i < 5:
#        data = py.recv(4096).decode()
#        #print ("rev data",data)
#        if data.find("DONE") > -1:
#            print(dataAll)
#            break
#        else :
#            dataAll += data
#        i += 1
#    try:
#        message = input("pt_shell: \n")
#
#        py.sendall(message.encode())
#        if message is "shutdown":
#            break
#
#    except ValueError:
#        print("wrong command")
#
#ej.loadJson()

#rpt = ej.report_timing()
#print(rpt)

#ej.report_timing()
#ej.pt_shell()


#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#with open("/home/yaguo/zoo/eda2json/ptServer","r") as fp:
#    ip, port =fp.readline().rstrip().split()
#server = (ip,int(port))
#s.connect(server)
#s.close()
