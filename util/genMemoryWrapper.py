#!/tools/python/anaconda3/bin/python3
import os, sys,glob,re,stat
import pyLib
import math
import platform

if ( (os.uname()[0]) == "Darwin" ) :
    outDir = "/Users/guoyapeng/work/DLM1/hw/rtl/rams/"
else:
    outDir = "./"

#memConfig = "/Users/guoyapeng/work/DLM1/hw/memList.csv"
memConfig = "./memList.csv"

print("outputs to ", outDir)
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
    T28HPCP_SNPS_SRAM_MODEL
`else 
   reg [WordSize-1:0] Mem [0:width-1];
   reg [width-1:0]  rdDataReg;
   always @(posedge clk)
       if (csEn)
           if (wrEn)
               Mem[addr] = wrData ;
           else
               rdDataReg = Mem[addr];
       else
           rdDataReg = WordSize'b0;
    assign rdData = rdDataReg;
`endif            
endmodule
'''

ram2p = '''
module prefix_portP_depthW_widthB_bwebBM ( clk, wrEn, rdEn, sd, slp, wrAddr, rdAddr, wrData, rdData, wrMask) ;
//parameter AddressSize = width;
//parameter WordSize = depth;
//parameter bitMask = bweb;

input clk,rdEn, wrEn;
input sd, slp;
input [AddressSize:0] wrAddr;
input [width-1:0] wrData, wrMask;

input [AddressSize:0] rdAddr;
reg [width-1:0] rdDataReg;
output [width-1:0] rdData;


`ifdef T28HPCP_TSMC_SRAM
T28HPCP_TSMC_SRAM_MODEL
`elsif SNPS28HPC_SRAM    
T28HPCP_SNPS_SRAM_MODEL
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
                                   .CEB(csEn_N_), 
                                   .WEB(wrEn_N_),
                                   .SLP(slp),
                                   .SD(sd),
                                   .A(addr_N_), 
                                   .D(wrData_N_),
                                   .Q(rdData_N_));  
'''

tsmc2prfModel = '''
  TS6N28HPCPSVTA_depth_X_width_M4S ram_N_(.CLKR(clk), 
                                   .CLKW(clk),
                                   .REB(rdEn_N_), 
                                   .WEB(wrEn_N_),
                                   .SLP(slp),
                                   .SD(sd),
                                   .AA(addrR_N_), 
                                   .AB(addrW_N_),
                                   .D(wrData_N_),
                                   .Q(rdData_N_));  
'''

tsmc1pMaxWidth = 144
tsmc1pMaxDepth = 512


tsmc2pMaxWidth = 144
tsmc2pMaxDepth = 512


with open(memConfig,"r") as fin:
    for file in fin:
        preFix,port,depth,width,bweb = file.rstrip().split(',')

        if preFix.find("prefix") < 0:
            addrSize = str(math.ceil(math.log2(int(depth))) -1)
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

                    widthSplitCount = math.ceil(int(width) / tsmc1pMaxWidth)
                    depthSplitCount = math.ceil(int(depth) / tsmc1pMaxDepth)

                    tsmcMemLogic = ""
                    newWidth = int(math.ceil(int(width)/widthSplitCount / 2) * 2)
                    newDepth = int(math.ceil(int(depth)/depthSplitCount / 2) * 2)

                    newWidthStr = str(newWidth-1)
                    newDepthStr = str(newDepth-1)

                    newAddr = str(int(int(addrSize) - math.log(depthSplitCount,2)))
                    dataSplitLogic = ""

                    wireDeclare = ""

                    for i in range(0,widthSplitCount):

                        instMemLogic = ""
                        for j in range(0,depthSplitCount):
                            numb = "_"+str(i) +"_"+str(j)
                            wireDeclare += "    wire addr" +numb +";\n"
                            wireDeclare += "    wire " + "[" + newWidthStr + ":0]  rdData" + numb +";\n"
                            wireDeclare += "    wire " + "[" + newWidthStr + ":0]  wrData" + numb + ";\n"

                            addrSplitLogic = ""
                            addrSplitLogic +=  " assign addr" + numb + "[" + newAddr+":0] = addr["+newAddr +":0] ;\n"
                            addrSplitLogic +=  " assign rdData[" + newWidthStr + ":0] = rdData" + numb + "[" + newWidthStr + ":0] ; \n"
                            addrSplitLogic +=  " assign wrData" + numb + "[" + newWidthStr + ":0] = wrData[" + newWidthStr + ":0] ; \n"

                            instMemLogic = tsmc1prfModel
                            instMemLogic = instMemLogic.replace("_width_",newWidthStr)
                            instMemLogic = instMemLogic.replace("_depth_", newDepthStr)
                            instMemLogic = instMemLogic.replace("_N_", numb)

                            tsmcMemLogic +=  addrSplitLogic + instMemLogic
                    enSplitLogic = ""

                    csSelWidth = math.ceil(math.log(depthSplitCount,2))

                    ### first loop depth ,then loop width
                    #print("splitted into ", widthSplitCount)
                    enSplitLogic += "  case(addr[" + addrSize + ":" + str(int(addrSize) - int(csSelWidth) + 1) + "])\n"
                    for i in range(0,depthSplitCount):
                        enSplitLogic += "    " + str(csSelWidth) + "\'d" + str(i) + ":\n"
                        enSplitLogic += "    begin \n"
                        for j in range(0,widthSplitCount):
                            numb = "_"+str(j) +"_"+str(i)
                            wireDeclare += "    wire wrEn" +numb + ";\n"
                            wireDeclare += "    wire csEn" + numb + ";\n"

                            enSplitLogic += "       assign wrEn" +numb + "=wrEn ;\n"
                            enSplitLogic += "       assign csEn" +numb + "=csEn ;\n"
                            enSplitLogic += "       assign " + "rdData" + "[" + str(
                                newWidth * (j + 1) - 1) + ":" + str(newWidth * j) + "] = rdData"+numb + ";\n"
                        enSplitLogic += "    end\n"
                    enSplitLogic += "  endcase\n"

                            #print(tsmcMemLogic)
                    targetRam = targetRam.replace("T28HPCP_TSMC_SRAM_MODEL",wireDeclare + dataSplitLogic + enSplitLogic + tsmcMemLogic)
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

                    widthSplitCount = math.ceil(int(width) / tsmc2pMaxWidth)
                    depthSplitCount = math.ceil(int(depth) / tsmc2pMaxDepth)

                    tsmcMemLogic = ""
                    newWidth = int(math.ceil(int(width) / widthSplitCount / 2) * 2)
                    newDepth = int(math.ceil(int(depth) / depthSplitCount / 2) * 2)

                    newWidthStr = str(newWidth)
                    newDepthStr = str(newDepth)

                    newAddr = str(int(int(addrSize) - math.log(depthSplitCount, 2)  ))
                    dataSplitLogic = ""
                    wireDeclare = ""

                    for i in range(0, widthSplitCount):

                        instMemLogic = ""
                        for j in range(0, depthSplitCount):
                            numb = "_" + str(i) + "_" + str(j)
                            wireDeclare += "    wire addr" + numb + ";\n"
                            wireDeclare += "    wire rdData" + numb + ";\n"
                            wireDeclare += "    wire wrData" + numb + ";\n"
                            wireDeclare += "    wire" + "[" + newAddr + ":0]   addrR" + numb  + ";\n"
                            wireDeclare += "    wire" + "[" + newAddr + ":0]   addrW" + numb  + ";\n"

                            addrSplitLogic = ""
                            addrSplitLogic += " assign addrR" + numb + "[" + newAddr + ":0] = rdAddr[" + newAddr + ":0] ;\n"
                            addrSplitLogic += " assign addrW" + numb + "[" + newAddr + ":0] = wrAddr[" + newAddr + ":0] ;\n"

                            addrSplitLogic += " assign rdData" + numb + "[" + newWidthStr + ":0] = rdData[" + newWidthStr + ":0] ; \n"
                            addrSplitLogic += " assign wrData" + numb + "[" + newWidthStr + ":0] = wrData[" + newWidthStr + ":0] ; \n"

                            instMemLogic = tsmc2prfModel
                            instMemLogic = instMemLogic.replace("_width_", newWidthStr)
                            instMemLogic = instMemLogic.replace("_depth_", newDepthStr)
                            instMemLogic = instMemLogic.replace("_N_", numb)

                            tsmcMemLogic += addrSplitLogic + instMemLogic
                    wrEnSplitLogic = ""
                    rdEnSplitLogic = ""

                    csSelWidth = math.ceil(math.log(depthSplitCount, 2))

                    ### first loop depth ,then loop width
                    #print("splitted into ", widthSplitCount)
                    rdEnSplitLogic += "  case (rdAddr[" + addrSize + ":" + str(int(addrSize) - int(csSelWidth) + 1) + "])\n"
                    wrEnSplitLogic += "  case (wrAddr[" + addrSize + ":" + str(
                        int(addrSize) - int(csSelWidth) + 1) + "])\n"
                    for i in range(0, depthSplitCount):
                        rdEnSplitLogic += "    " + str(csSelWidth) + "\'d" + str(i) + ":\n"
                        wrEnSplitLogic += "    " + str(csSelWidth) + "\'d" + str(i) + ":\n"
                        rdEnSplitLogic += "    begin \n"
                        wrEnSplitLogic += "    begin \n"
                        for j in range(0, widthSplitCount):
                            numb = "_" + str(j) + "_" + str(i)
                            wireDeclare  += "    wire wrEn" + numb +";\n"
                            wireDeclare += "    wire rdEn" + numb + ";\n"

                            rdEnSplitLogic += "       assign rdEn" + numb + "=rdEn ;\n"
                            wrEnSplitLogic += "       assign wrEn" + numb + "=wrEn ;\n"

                            rdEnSplitLogic += "       assign " + "rdData" + "[" + str(
                                newWidth * (j + 1) - 1) + ":" + str(newWidth * j) + "] = rdData" + numb + ";\n"
                            wrEnSplitLogic += "       assign "  + "wrData" + numb + " = wrData" + "[" + str(
                                newWidth * (j + 1) - 1) + ":" + str(newWidth * j) + "]  ;\n"

                        rdEnSplitLogic += "    end\n"
                        wrEnSplitLogic += "    end\n"


                    rdEnSplitLogic += "  endcase\n"
                    wrEnSplitLogic += "  endcase\n"
                    # print(tsmcMemLogic)
                    targetRam = targetRam.replace("T28HPCP_TSMC_SRAM_MODEL",
                                                  wireDeclare + dataSplitLogic + rdEnSplitLogic  + wrEnSplitLogic + tsmcMemLogic)
                    fout.write(targetRam)
                else:
                    print(port)

