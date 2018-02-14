import os, sys,glob,re,stat
import pyLib

memConfig = "/Users/guoyapeng/work/DLM1/hw/memList.csv"


ram1p = '''
module prefix_portP_depthW_widthB_bwebBM (clk,  wrEn, csEn, addr, wrData, rdData);
parameter AddressSize = width;
parameter WordSize = depth;

input  [AddressSize-1:0] Address;
input  [WordSize-1:0] wrData;
output reg [WordSize-1:0] rdData;

input clk, wrEn, rdEn;

`ifdef TSMC28HPCP_SRAM
    TSMC28HPC_MEMORY_MODEL
`elsif SNPS28HPC_SRAM
    TSMC28HPC_MEMORY_MODEL
`else 
reg [WordSize-1:0] Mem [0:(1<<AddressSize)-1];

always @(posedge clk)
    if (rdEn)
        if (wrEn)
            Mem[Address] = Data
        else
            rdData = Mem[Address];
    else
        rdData = WordSize{1'bz}
            
endmodule
'''

ram2p = '''
module sram_portP_depthW_widthB_bwebBM ( clk, wrEn, rdEn, wrAddr, rdAddr, wrData, rdData, bweb) ;
parameter AddressSize = width;
parameter WordSize = depth;
parameter bitMask = bweb;

input clk,rdEn, wrEn,
input [AddressSize-1:0] wrAddr,
input [WordSize-1:0] wrData,

input [AddressSize-1:0] rdAddr,
output reg [WordSize-1:0] rdData


`ifdef TSMC28HPCP_SRAM
    TSMC28HPC_MEMORY_MODEL
`elsif SNPS28HPC_SRAM
    TSMC28HPC_MEMORY_MODEL
`else 

reg [WordSize-1:0] memory ;[AddressSize-1:0]

always @ (posedge clk)
    if(wrEn)        
        genvar wrBit;
        generate
        for (wrBit=0; wrBit < bitMask ; wrBit = wrBit + 1 ) begin : write_ram_data
            assgin  memory[wrAddr][wrBit] = bweb[wrBit] ? wrData[wrBit] : memory[wrAddr][wrBit]
                                                 
    if(rdEn)
        rdData<=memory[rdAddr];
endmodule
'''

with open(memConfig,"r") as fin:
    for file in fin:
        preFix,port,depth,width,bweb = file.rstrip().split(',')
        if preFix.find("prefix") < 0:
            ramName = "/Users/guoyapeng/work/DLM1/hw/rtl/sram/"+preFix+"_"+port+"P_"+depth+"W_"+width+"B_"+bweb+"BM"
            with open(ramName+".v","w") as fout:
                if int(port) == 1 :
                    ram1p = ram1p.replace("prefix",preFix)
                    ram1p = ram1p.replace("port",port)
                    ram1p = ram1p.replace("width",width)
                    ram1p = ram1p.replace("bweb",bweb)
                    #print(ram1p)
                    fout.write(ram1p)
                elif int(port) == 2 :
                    ram2p = ram2p.replace("prefix", preFix)
                    ram2p = ram2p.replace("port", port)
                    ram2p = ram2p.replace("width", width)
                    ram2p = ram2p.replace("depth", depth)
                    ram2p = ram2p.replace("bweb", bweb)
                    fout.write(ram2p)
                else:
                    print(port)

