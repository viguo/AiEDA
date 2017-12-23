import os
'''
zcn1ColorModule = {}
zcn1ColorModule["blue"]   = "zcn_ffe3_1/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_upper/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_1/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"
zcn1ColorModule["green"]  = "zcn_ffe3_1/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_lower/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_0/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"
zcn1ColorModule["orange"] = "zcn_ffe3_1/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_upper/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_0/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"
zcn1ColorModule["purple"] = "zcn_ffe3_1/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_lower/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_1/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"

zcn1ColorModule["light_blue"] = "zcn_ffe3_0/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_upper/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_1/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"
zcn1ColorModule["light_green"]  = "zcn_ffe3_0/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_lower/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_0/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"
zcn1ColorModule["light_orange"] = "zcn_ffe3_0/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_upper/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_0/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"
zcn1ColorModule["light_purple"] = "zcn_ffe3_0/u_zcn_pt/u_zcn_pt_unshuffle_addr_parsing/u_zcn_pt_unshuffle/zcn_pt_unshuffle_mem_ram_lower/gen_mem_inst_*_u_zcn_mem2p8x256b8ns/mem_0_1/vl_wr_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_1/U_smu_zcn1_t1_sms_wrap_rfps2ps3rmlvt16x128m2bn_int_top/U_rfps2ps3rmlvt16x128m2bn"



fp = open("/home/yaguo/arielc0/zcn1_hight.tcl","w")

for color in zcn1ColorModule:
    hiCommand = "gui_change_highlight -color " + color + " -collection [get_cells {" + zcn1ColorModule[color] + " }]"
    fp.writelines(hiCommand+"\n")

fp.close()
'''

            

zcn0ColorModule = {}
zcn0ColorModule["orange"]= "zcn/zcn_core/u_zcn_jpm_zcn_jpm_be_*/*"
zcn0ColorModule["blue"] = "zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_eng/*"
zcn0ColorModule["green"] = "zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/*"
zcn0ColorModule["light_blue"] = "zcn/zcn_core/u_zcn_ffe1/u_zcn_pif0/u_zcn_mem2p8x256ps/mem_0_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_156/U_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_int_top/U_rfps2ps3rmlvt16x128m2p"

zcn0ColorModule["purple"] = "zcn/zcn_core/uaxi_fifo_m0/*"
zcn0ColorModule["light_green"] = "zcn/zcn_core/u_zcn_jpm_zcn_jpm_fe_q*"
#zcn0ColorModule["light_blue"] = "tile_dfx/smu_zcn0_t_edt_i/*"
#zcn0ColorModule["light_orange"] = "zcn/zcn_sram1/*"
#zcn0ColorModule["light_green"] = "zcn/zcn_core/u_zcn_ri/*"

fp = open("/home/yaguo/arielc0/zcn0_hight.tcl","w")

for color in zcn0ColorModule:
    hiCommand = "gui_change_highlight -color " + color + " -collection [get_flat_cells {" + zcn0ColorModule[color] + " }]"
    fp.writelines(hiCommand+"\n")


zcn0ColorRam1 = {
    "yellow"        :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_10_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "orange"        :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_11_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "red"           :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_12_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "purple"        :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_13_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "green"         :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_14_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_orange"  :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_15_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_red"     :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_16_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_green"   :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_17_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_blue"    :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_18_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_purple"  :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_19_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*"
}
fp = open("/home/yaguo/arielc0/zcn0_ram1_hight.tcl","w")
#print("/home/yaguo/arielc0/zcn0_ram1_1_hight.tcl")
for color in zcn0ColorRam1:
    hiCommand = "gui_change_highlight -color " + color + " -collection [get_flat_cells {" + zcn0ColorRam1[color] + " }]"
    fp.writelines(hiCommand+"\n")


zcn0ColorRam0_1 = {
    "yellow"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_0_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "orange"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_1_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "red"           :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_2_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "purple"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_3_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "green"         :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_4_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_orange"  :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_5_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_red"     :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_6_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_green"   :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_7_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_blue"    :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_8_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_purple"  :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_9_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*"
}
fp = open("/home/yaguo/arielc0/zcn0_ram0_1_hight.tcl","w")

with open("/home/yaguo/arielc0/zcn0_ram0_1_hight.tcl","w") as fp:
    for color in zcn0ColorRam0_1:
        hiCommand = "gui_change_highlight -color " + color + " -collection [get_flat_cells {" + zcn0ColorRam0_1[color] + " }]"
        fp.writelines(hiCommand+"\n")


zcn0ColorRam0_2 = {
    "yellow"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_10_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "orange"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_11_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "red"           :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_12_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "purple"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_13_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "green"         :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_14_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_orange"  :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_15_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_red"     :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_16_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_green"   :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_17_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_blue"    :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_18_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_purple"  :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_19_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*"
}
with open("/home/yaguo/arielc0/zcn0_ram0_2_hight.tcl","w") as fp:
    for color in zcn0ColorRam0_2:
        hiCommand = "gui_change_highlight -color " + color + " -collection [get_flat_cells {" + zcn0ColorRam0_2[
            color] + " }]"
        fp.writelines(hiCommand + "\n")


zcn0ColorRam0_3 = {
    "yellow"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_20_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "orange"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_21_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "red"           :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_22_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "purple"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_23_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "green"         :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_24_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_orange"  :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_25_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_red"     :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_26_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_green"   :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_27_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_blue"    :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_28_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*",
    "light_purple"  :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_29_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps*"
}
with open("/home/yaguo/arielc0/zcn0_ram0_3_hight.tcl","w") as fp:
    for color in zcn0ColorRam0_3:
        hiCommand = "gui_change_highlight -color " + color + " -collection [get_flat_cells {" + zcn0ColorRam0_3[
            color] + " }]"
        fp.writelines(hiCommand + "\n")



zcn0ColorRam0_3 = {
    "yellow"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_*_0/vl_wr_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp*/U_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp_int_top/U_rfps2p3rmlvt1024x104m4k2bp",
    "orange"        :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_*_1/vl_wr_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp*/U_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp_int_top/U_rfps2p3rmlvt1024x104m4k2bp",
    "green"         :  "zcn/zcn_sram0/zcn_mem2p22528x256b8ps_inst/mem_*_2/vl_wr_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt1024x48m4k2bp*/U_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt1024x48m4k2bp_int_top/U_rfps2ps3rmlvt1024x48m4k2bp",
    "red"           :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_*_0/vl_wr_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp*/U_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp_int_top/U_rfps2p3rmlvt1024x104m4k2bp",
    "purple"        :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_*_1/vl_wr_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp*/U_smu_zcn0_t1_sms_wrap_rfps2p3rmlvt1024x104m4k2bp_int_top/U_rfps2p3rmlvt1024x104m4k2bp",
    "light_red"  :  "zcn/zcn_sram1/zcn_mem2p22528x256b8ps_inst/mem_*_2/vl_wr_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt1024x48m4k2bp*/U_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt1024x48m4k2bp_int_top/U_rfps2ps3rmlvt1024x48m4k2bp",

}
with open("/home/yaguo/arielc0/zcn0_ram_hight.tcl","w") as fp:
    for color in zcn0ColorRam0_3:
        hiCommand = "gui_change_highlight -color " + color + " -collection [get_flat_cells {" + zcn0ColorRam0_3[color] + " }]"
        fp.writelines(hiCommand + "\n")

