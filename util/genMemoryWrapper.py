import os, sys,glob,re,stat
import pyLib
import math

#memConfig = "/Users/guoyapeng/work/DLM1/hw/memList.csv"
memConfig = "./memList.csv"
outDir = "/home/yaguo/works/pnr/1.mem/"

ram1p = '''
module prefix_portP_depthW_widthB_bwebBM (clk, wrEn, csEn, addr, wrData, rdData,sd,slp);
//parameter AddressSize = width;
//parameter WordSize = depth;

input  [AddressSize-1:0] addr;
input  [width-1:0] wrData;
input  clk, wrEn, csEn;
input  sd, slp;
output [width-1:0] rdData;


`ifdef T28HPCP_TSMC_SRAM
T28HPCP_TSMC_SRAM_MODEL
`elsif SNPS28HPC_SRAM
    TSMC28HPC_MEMORY_MODEL
`else 
   reg [WordSize-1:0] Mem [0:width-1];
   reg [width-1:0]  rdDataReg
   always @(posedge clk)
       if (csEn)
           if (wrEn)
               Mem[addr] = wrData ;
           else
               rdData = Mem[addr];
       else
           rdDataReg = WordSize'b0;
    assign rdData = rdDataReg;
`endif            
endmodule
'''

ram2p = '''
module prefix_portP_depthW_widthB_bwebBM ( clk, wrEn, rdEn, wrAddr, rdAddr, wrData, rdData, wrMask) ;
//parameter AddressSize = width;
//parameter WordSize = depth;
//parameter bitMask = bweb;

input clk,rdEn, wrEn;
input sd, slp;
input [AddressSize-1:0] wrAddr;
input [width-1:0] wrData, wrMask;

input [AddressSize-1:0] rdAddr;
reg [width-1:0] rdDataReg;
output [width-1:0] rdData;


`ifdef TSMC28HPCP_SRAM
    TSMC28HPC_MEMORY_MODEL
`elsif SNPS28HPC_SRAM
    TSMC28HPC_MEMORY_MODEL
`else 

reg [WordSize-1:0] memory [AddressSize-1:0] ;

wire [width-1:0] wrDataTemp;

genvar wrBit;
generate
  for (wrBit=0; wrBit < bitMask ; wrBit = wrBit + 1 ) 
    begin : write_ram_data
      assign wrDataTemp[wrBit] = wrMask[wrBit] ? wrData[wrBit] : memory[wrAddr][wrBit] ;
    end
endgenerate

always @ (posedge clk) begin
    if(wrEn)        
        memory[wrAddr] = wrDataTemp;
                                                 
    if(rdEn)
        rdDataReg = memory[rdAddr];
end
assign rdData = rdDataReg;
`endif
endmodule
'''

tsmc1prfModel = '''
  TS5N28HPCPSVTA_depth_X_width_M2S ram_N_(.CLK(clk), 
                                   .CEB(csEn), 
                                   .WEB(wrEn),
                                   .SLP(slp),
                                   .SD(sd),
                                   .A(addr_N_), 
                                   .D(wrData_N_),
                                   .Q(rdData_N_));  
'''

with open(memConfig,"r") as fin:
    for file in fin:
        preFix,port,depth,width,bweb = file.rstrip().split(',')

        if preFix.find("prefix") < 0:
            addrSize = str(math.ceil(math.log2(int(depth))))

            ramName = outDir+preFix+"_"+port+"P_"+depth+"W_"+width+"B_"+bweb+"BM"
            with open(ramName+".v","w") as fout:
                if int(port) == 1 :
                    targetRam = ram1p.replace("prefix",preFix)
                    targetRam = targetRam.replace("port",port)
                    targetRam = targetRam.replace("depth", depth)
                    targetRam = targetRam.replace("width",width)
                    targetRam = targetRam.replace("WordSize",depth)
                    targetRam = targetRam.replace("AddressSize",addrSize)
                    targetRam = targetRam.replace("bweb",bweb)
                    ### insert tsmc memory
                    tsmc1pMaxWidth = 144
                    tsmc1pMaxDepth = 128
                    widthSplitCount = math.ceil(int(width) / tsmc1pMaxWidth)
                    depthSplitCount = math.ceil(int(depth) / tsmc1pMaxDepth)

                    tsmcMemLogic = ""
                    newWidth = int(math.ceil(int(width)/widthSplitCount / 2) * 2)
                    newDepth = int(math.ceil(int(depth)/depthSplitCount / 2) * 2)

                    newWidthStr = str(newWidth)
                    newDepthStr = str(newDepth)

                    newAddr = str(int(int(addrSize) - math.log(depthSplitCount,2)))
                    dataSplitLogic = ""

                    for i in range(0,widthSplitCount):

                        instMemLogic = ""

                        dataSplitLogic += " assign " + "wrData"+str(i) + "[" + str(newWidth-1)+ ":0] = wrData[" +str(newWidth*(i+1) -1)+":"+str(newWidth*i) + "]\n"
                        dataSplitLogic += " assign " + "rdData" + "[" + str(
                            newWidth*(i+1) - 1) + ":" + str(newWidth*i) + "] = rdData" + str(i) + "[" + str(newWidth  - 1) + ":0] \n"

                        for j in range(0,depthSplitCount):
                            numb = "_"+str(i) +"_"+str(j)
                            addrSplitLogic = ""
                            addrSplitLogic +=  " assign addr" + numb + "[" + newAddr+":0] = addr["+newAddr +":0] \n"
                            addrSplitLogic +=  " assign rdData" + numb + "[" + newWidthStr + ":0] = rdData[" + newWidthStr + ":0] \n"
                            addrSplitLogic +=  " assign wrData" + numb + "[" + newWidthStr + ":0] = wrData[" + newWidthStr + ":0] \n"

                            instMemLogic = tsmc1prfModel
                            instMemLogic = instMemLogic.replace("_width_",newWidthStr)
                            instMemLogic = instMemLogic.replace("_depth_", newDepthStr)
                            instMemLogic = instMemLogic.replace("_N_", numb)

                            tsmcMemLogic +=  addrSplitLogic + instMemLogic
                    enSplitLogic = ""
                    enSplitLogic += "case(addr["+ width +":"+str(int(width)-int(newWidth)) + "]\n"
                    for i in range(0,widthSplitCount):
                        for j in range(0,depthSplitCount):
                            enSplitLogic += str(depthSplitCount) + "\'d:\n"


                            #print(tsmcMemLogic)
                    targetRam = targetRam.replace("T28HPCP_TSMC_SRAM_MODEL",dataSplitLogic + tsmcMemLogic)
                    fout.write(targetRam)

                elif int(port) == 2 :
                    targetRam = ram2p.replace("prefix", preFix)
                    targetRam = targetRam.replace("port", port)
                    targetRam = targetRam.replace("width", width)
                    targetRam = targetRam.replace("depth", depth)
                    targetRam = targetRam.replace("AddressSize",addrSize)
                    targetRam = targetRam.replace("WordSize",depth)
                    targetRam = targetRam.replace("bitMask",bweb)
                    targetRam = targetRam.replace("bweb", bweb)
                    fout.write(targetRam)
                else:
                    print(port)

