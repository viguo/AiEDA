import os
import shutil


#nickNames = "FP5 FP5_br3 FP6 FP6_br1 FP6_br2  FP6_br4 FP6_br4  FP6_br6  FP6_br7 FP7 FP11 FP11_br1 FP5 FP5_br1 FP10 FP12 FP13"
nickNames = " FP3 FP4 FP5 FP6 FP7  FP10  FP12 FP13 FP14 FP15 FP16 FP17 FP18"
nickNames = "OberonFP3"

if nickNames.find("Oberon") > -1 :

    newPin = "source /home/yaguo/arielc0/zcn0_Oberon_FE_pin.tcl"

else:
    newPin = '''
            source /proj/arielc0pd_fcfp02/toren/RELEASE/1204/smu_zcn0_t.tcl 
            create_bound -name bound -type hard [get_cells  zcn/zcn_xbar_wrp/zcn_xbar/u_asib_ZCN_m/u_aw_slave_port_chan_slice/u_ful_regd_slice/sel_b_reg_10_] -boundary {{250 86} {252 90}}
            '''

pathGroup = '''
foreach_in_collection scenario [all_scenarios] {
    current_scenario $scenario

    set U_rfps2p [get_cells -quiet -hier * -filter "(ref_name =~ rfps2p3*)"]
    group_path -name T_Mem -to  $U_rfps2p

    foreach_in_collection sram_inst $U_rfps2p { 
        set ramName [get_attribute $sram_inst full_name]
        set_multicycle_path -setup 2 -from [get_pins $ramName/CLK] -to  [get_pins $ramName/SI_Q_HB]
        set_multicycle_path -setup 2 -from [get_pins $ramName/CLK] -to  [get_pins $ramName/TCLK]
        group_path -name T_MEM -to    [get_cells $ramName]
        group_path -name F_MEM -from  [get_cells $ramName]

    }

     group_path -name F_RC   -from  [get_pins zcn/zcn_core/u_zcn_ffe*/u_zcn_sha_top/i_sha*_hmac_wrapper/i_sha*/i_sha*_control/RoundCounter_reg_*/CK] -to [get_clocks ZCNCLK ] -weight 10
     group_path -name F_NC   -from  [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/NextCommand_reg_*_/CK] -to [get_clocks ZCNCLK] -weight 10
     group_path -name F_KsbR -from  [get_pins zcn/zcn_core/i_ksb/i_arb_store/Pt*KsbWriteRequest0q_reg/CK] -to [get_clocks ZCNCLK] -weight 10
     group_path -name F_RgIf -from  [get_pins zcn/zcn_core/u_zcn_ri/u_zcn_axi_slave/curr_read_write_state_regif_reg_*_/CK] -to [get_clocks ZCNCLK] -weight 10
     group_path -name F_KsbM -from  [get_pins zcn/zcn_core/i_ksb/i_arb_store/ksr/mem_0_0/vl_wr_smu_zcn0_t1_sms_wrap_hdsd1p3rmrvt128x128m4bp_1/U_smu_zcn0_t1_sms_wrap_hdsd1p3rmrvt128x128m4bp_int_top/U_hdsd1p3rmrvt128x128m4bp/*CLK ] -to [get_clock ZCNCLK] -weight 10
     group_path -name F_JPM  -from  [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/VQM_JPM_QueueHead_reg_*_/CK] -to [get_clocks ZCNCLK] -weight 10
     group_path -name F_IDMA -from  [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/VQM_IDMA_QueueHead_reg_*_/CK] -to [get_clocks ZCNCLK]  -weight 10
     group_path -name F_shaS -from  [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/StateIn_Flattened_reg_*_/CK] -to  [get_clocks ZCNCLK] -weight 10
     group_path -name F_pifM -from  [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_pif0/u_zcn_mem2p8x256ps/mem_0_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_156/U_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_int_top/U_rfps2ps3rmlvt16x128m2p/*CLK ]      -weight 10
     group_path -name T_pifM -to    [get_cells zcn/zcn_core/u_zcn_ffe1/u_zcn_pif0/u_zcn_mem2p8x256ps/mem_0_*/vl_wr_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_156/U_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_int_top/U_rfps2ps3rmlvt16x128m2p]
     group_path -name F_Fifo -from  [get_pins zcn/zcn_sram0/u_zcn_axi_slave_read_channels/rd_data_resp_fifo/fifo_rptr_reg_reg_*_/CK]
     group_path -name T_Cont -to    [get_pins zcn/zcn_core/u_zcn_odma/u_zcn_arb*_*/Count_reg_*_/D]
     group_path -name F_kmbR -from  [get_pins zcn/zcn_core/uzcn_kmb/ukmb_cmdval/state_r_reg_*_/CK]
     group_path -name T_GntS -to    [get_pins zcn/zcn_core/u_zcn_odma/u_zcn_arb*_*/GntSel_reg_*_/D]
     group_path -name F_ksbM -from [get_pins zcn/zcn_core/i_ksb/i_arb_store/ksr/mem_*_*/vl_wr_smu_zcn0_t1_sms_wrap_hdsd1p3rmrvt128x128m4bp_1/U_smu_zcn0_t1_sms_wrap_hdsd1p3rmrvt128x128m4bp_int_top/U_hdsd1p3rmrvt128x128m4bp/*CLK]
     group_path -name F_Sha  -from [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/Sha3State_Result_reg_reg_*_/CK]
     group_path -name F_SDMA -from  [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/VQM_StartIdma_reg/CK] -to [get_clocks ZCNCLK]
     group_path -name F_Ptus  -from [get_pins zcn/zcn_core/u_zcn_idma_zcn_idma_q*/u_zcn_idma_qstate0/pt_unshuffle_function_en_reg/CK] 
     group_path -name F_WFQ  -from [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/WFQ_Time_out_reg_*_/CK]
     group_path -name F_CmdK  -from   [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/VqmCmdKeyPtr_r_reg_*_/CK]
     group_path -name F_upof  -from  [get_pins zcn/zcn_core/u_zcn_odma/upof_data_fifo_*/FifoEmpty_reg/CK]
     group_path -name T_SI     -to [ get_pins -hier */SI]
     group_path -name F_KeyG   -from [get_pins  zcn/zcn_core/uzcn_kmb/u_kmb_dat_top/KEYGEN/keygen_cmd_mode_r_reg_*_/CK]
     group_path -name io_to_io -weight 0.1
     
     group_path -name DBGU_0_DBUS11_SSB_DCLK0 -weight 0.1
     group_path -name DBGU_0_DBUS11_SSB_DCLK1 -weight 0.1
     group_path -name DBGU_0_DBUS11_SSB_DCLK2 -weight 0.1
     group_path -name DBGU_0_DBUS11_SSB_DCLK3 -weight 0.1

     group_path -name DBGU_0_DBUS55_SSB_DCLK0 -weight 0.1
     group_path -name DBGU_0_DBUS55_SSB_DCLK1 -weight 0.1
     group_path -name DBGU_0_DBUS55_SSB_DCLK2 -weight 0.1
     group_path -name DBGU_0_DBUS55_SSB_DCLK3 -weight 0.1
}                       
'''


I2PlaceMacroPostPlace = ''''''


I2PostFloorPlanPreOpt ='''
source /proj/arielc0pd_fcfp02/toren/RELEASE/1204/smu_zcn0_t.tcl

'''

I2PlacePreOpt = '''                      

#create_keepout_margin -type soft -outer "0.5 0 0 0 " [get_flat_cells zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_eng/*]
source /proj/arielc0pd_fct01/jehe/NLBp1/io_weight/smu_zcn0_t_IO_weight_tune_file.tcl
remove_cell I_*PUSHDOWN
group_path -name io_to_io -weight 0.1

set_clock_latency -100 [get_pins  zcn/zcn_core/u_zcn_ffe*/u_zcn_sha_top/i_sha*_hmac_wrapper/i_sha*/i_sha*_control/RoundCounter_reg_*/CK ]
set_clock_latency -50 [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/Sha3State_Result_reg_reg_*_/CK]
set_clock_latency -50 [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/StateIn_Flattened_reg_*_/CK]
set_clock_latency -100 [get_pins  zcn/zcn_core/u_zcn_busy/reset_sync_Reset_bar_inst/async_rstn0q_reg/CK ]
set_clock_latency -100 [get_pins  zcn/zcn_core/u_zcn_busy/reset_sync_Reset_ono_ffe_inst_*/async_rstn0q_reg/CK ]
set_clock_latency -100 [get_pins  zcn/zcn_core/u_zcn_busy/reset_sync_Reset_ono_core_inst_*/async_rstn0q_reg/CK ]
set_clock_latency -100  [get_pins  -hier async_rstn0q_reg/CK ]
 #create_placement_blockage -type soft -boundary {{89.9980 -344.7170} {109.2455 -364.7115}}


#source /proj/arielc0pd_fcfp02/toren/RELEASE/1204/smu_zcn0_t.tcl

 create_placement_blockage -type soft -boundary {{81.9540 -344.7170} {109.2455 -374.4720}}
 
if {[info exists P(TUNE_TILE_CATE_B)] && $P(TUNE_TILE_CATE_B)=="1"} {
    source /home/wbai/2cate.pblk.tcl
}



'''

I2CtsPreOpt = '''

set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins  zcn/zcn_core/u_zcn_ffe*/u_zcn_sha_top/i_sha*_hmac_wrapper/i_sha*/i_sha*_control/RoundCounter_reg_*/CK ]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/Sha3State_Result_reg_reg_*_/CK]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/StateIn_Flattened_reg_*_/CK]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins  zcn/zcn_core/u_zcn_busy/reset_sync_Reset_bar_inst/async_rstn0q_reg/CK ]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins  zcn/zcn_core/u_zcn_busy/reset_sync_Reset_ono_ffe_inst_*/async_rstn0q_reg/CK ]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins  zcn/zcn_core/u_zcn_busy/reset_sync_Reset_ono_core_inst_*/async_rstn0q_reg/CK ]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm16/VQM_IDMA_QueueHead_reg_*_/CK]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins zcn/zcn_core/i_ksb/i_arb_store/Pt*KsbWriteRequest0q_reg/CK]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins  -hier async_rstn0q_reg/CK ]
set_clock_balance_points -delay 100 -clock ZCNCLK -balance_points [get_pins  zcn/zcn_xbar_wrp/zcn_xbar/u_asib_ZCN_m/u_aw_slave_port_chan_slice/u_ful_regd_slice/sel_b_reg_10_/CK]


'''

I2OptCtsPreOpt = '''
set hfn [ list \
    tile_dfx/dft_clk_cntl_Cpl_ZCNCLK/dft_pulse_cnt/pulse_cnt_en_reg/QN \
    smu_zcn0_t1_clken_sync/genblk1_usync_0_/s3_u_1__genblk1_u/genblk1_genblk1_genblk1_hdsync3msfqxss1us_d0nt_sync_HC0_C1_D_0_/Q \
    zcn/zcn_xbar_wrp/zcn_xbar/u_asib_ZCN_m/u_aw_slave_port_chan_slice/u_ful_regd_slice/sel_b_reg_10_/Q \
    ]

create_buffer_trees -from $hfn
    
'''


for name in nickNames.split():

    rundir = "/proj/arielc0pd_fct03/yaguo/main/pd/tiles/"+name+"/"
    print(rundir)

    newSdc = "/proj/ariel_pd_fct1/hmyin/release/budget/relax_sdc/smu_zcn0_t/setup.FuncTT0p65v.sdc.relax_io.relax_uncer_25"
    oldSdc = rundir + "data/sdc/setup.FuncTT0p65v.sdc"
    shutil.copy2(newSdc, oldSdc)

    with open(rundir + "tune/I2FpPlaceMacros/I2FpPlaceMacros.postplace.tcl", "w") as fp:
        fp.write(newPin)


    with open(rundir+"tune/I2Place/I2PostFloorPlan.pre_opt.tcl","w") as fp:
        fp.write(I2PostFloorPlanPreOpt)

    with open(rundir+"tune/I2Place/I2Place.pre_opt.tcl","w") as fp:
        fp.write(pathGroup + "\n")
        fp.write(I2PlacePreOpt)

    with open(rundir + "tune/I2Place/I2Place.pre_report.tcl","w") as fp:
        fp.write(I2PlacePreOpt)

    with open(rundir+"tune/I2Cts/I2Cts.pre_opt.tcl","w") as fp:
        fp.write(pathGroup+ "\n")
        fp.write(I2CtsPreOpt)

    with open(rundir + "tune/I2OptCts/I2OptCts.pre_opt.tcl", "w") as fp:
        fp.write(pathGroup + "\n")
        fp.write(I2OptCtsPreOpt)

    with open(rundir+"tune/I2OptRoute/I2OptRoute.pre_opt.tcl","w") as fp:
        fp.write(pathGroup)

    I2PlaceSeparateplaceSpostplace = '''
    save_block
    save_lib -as data/place1.nlib
    '''


    I2PlaceSeparateplacePreOpt = '''
    save_block
    save_lib -as data/place2.nlib
    '''
    with open(rundir+"tune/I2Place/I2Place.separateplace.postplace.tcl","w") as fp:
        fp.write(I2PlacePreOpt)
        fp.write(I2PlaceSeparateplaceSpostplace)

    I2PlaceSeparateplacePre_opt = '''
    save_block
    save_lib -as data/place2.nlib
    '''
    with open(rundir+"tune/I2Place/I2Place.separateplace.pre_opt.tcl","w") as fp:
        fp.write(I2PlaceSeparateplacePreOpt)

    DgSynthesizebeforeCompile1 = '''
          group_path -name F_RC   -from  [get_pins zcn/zcn_core/u_zcn_ffe*/u_zcn_sha_top/i_sha*_hmac_wrapper/i_sha*/i_sha*_control/RoundCounter_reg_*/CK] -to [get_clocks ZCNCLK ] -weight 10
          group_path -name F_NC   -from  [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/NextCommand_reg_*_/CK] -to [get_clocks ZCNCLK] -weight 10
          group_path -name F_KsbR -from  [get_pins zcn/zcn_core/i_ksb/i_arb_store/Pt*KsbWriteRequest0q_reg/CK] -to [get_clocks ZCNCLK] -weight 10
          group_path -name F_RgIf -from  [get_pins zcn/zcn_core/u_zcn_ri/u_zcn_axi_slave/curr_read_write_state_regif_reg_*_/CK] -to [get_clocks ZCNCLK] -weight 10
          group_path -name F_KsbM -from  [get_pins zcn/zcn_core/i_ksb/i_arb_store/ksr/mem_0_0/vl_wr_smu_zcn0_t1_sms_wrap_hdsd1p3rmrvt128x128m4bp_1/U_smu_zcn0_t1_sms_wrap_hdsd1p3rmrvt128x128m4bp_int_top/U_hdsd1p3rmrvt128x128m4bp/*CLK ] -to [get_clock ZCNCLK] -weight 10
          group_path -name F_JPM  -from  [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/VQM_JPM_QueueHead_reg_*_/CK] -to [get_clocks ZCNCLK] -weight 10
          group_path -name F_IDMA -from  [get_pins zcn/zcn_core/u_zcn_vqm_i_vsm*/VQM_IDMA_QueueHead_reg_*_/CK] -to [get_clocks ZCNCLK]  -weight 10
          group_path -name F_405  -from  [get_pins zcn/zcn_core/u_zcn_ffe1/u_zcn_sha_top/i_sha3_hmac_wrapper/i_sha3/i_sha3_control/StateIn_Flattened_reg_*_/CK] -to  [get_clocks ZCNCLK] -weight 10
          group_path -name M2M    -from  [get_pins  zcn/zcn_core/u_zcn_ffe1/u_zcn_pif0/u_zcn_mem2p8x256ps/mem_0_0/vl_wr_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_156/U_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_int_top/U_rfps2ps3rmlvt16x128m2p/CLK ] \
                                   -to   [get_pins  zcn/zcn_core/u_zcn_ffe1/u_zcn_pif0/u_zcn_mem2p8x256ps/mem_0_0/vl_wr_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_156/U_smu_zcn0_t1_sms_wrap_rfps2ps3rmlvt16x128m2p_int_top/U_rfps2ps3rmlvt16x128m2p/MEB ] \
                                    -weight 10


             puts "relax io timing at  [get_attribute $scenario name]"
             ##relax reason: i2o group, half cycle path, slack is less than -400ps, path optizated fine
             remove_output_delay [get_ports {FCFP_SSB_DBUS11_35_for_dbgsoc_lane_*_stage_*_S*_hop_39_NET}]
             remove_input_delay  [get_ports {FCFP_SSB_DBUS11_35_for_dbgsoc_lane_*_stage_*_S*_hop_18_NET}]

             set_output_delay 0 -clock [get_clocks {virtual_thru_DBGU_0_DBUS11_SSB_DCLK2_r}] -max [get_ports {FCFP_SSB_DBUS11_35_for_dbgsoc_lane_*_stage_*_S*_hop_39_NET}]
             set_input_delay  0 -clock [get_clocks {virtual_thru_DBGU_0_DBUS11_SSB_DCLK2_f}] -clock_fall -max [get_ports {FCFP_SSB_DBUS11_35_for_dbgsoc_lane_*_stage_*_S*_hop_18_NET}]

             ##relax reason: i2o group, slack is less than -200ps, output delay is a little big
             remove_output_delay [get_ports FE_FEEDX_MFT__1__smu_zcn0_t__smu_mp4_t__scf_smn__ScfSmnRouterR1_VSOC_ScfSmnTniuCLKA0_flit_RespVC]
             set_output_delay  800 -clock [get_clocks {virtual_thru_SMNCLK_r}] -max [get_ports {FE_FEEDX_MFT__1__smu_zcn0_t__smu_mp4_t__scf_smn__ScfSmnRouterR1_VSOC_ScfSmnTniuCLKA0_flit_RespVC}]

             remove_output_delay [get_ports FE_FEEDX_MFT__1__smu_zcn0_t__smu_mp4_t__scf_smn__ScfSmnRouterR1_VSOC_ScfSmnTniuCLKA0_flit_RespFlitData__9]
             set_output_delay  800  -clock [get_clocks {virtual_thru_SMNCLK_r}] -max [get_ports {FE_FEEDX_MFT__1__smu_zcn0_t__smu_mp4_t__scf_smn__ScfSmnRouterR1_VSOC_ScfSmnTniuCLKA0_flit_RespFlitData__9}]

             remove_output_delay [get_ports FE_FEEDX_MFT__1__smu_zcn0_t__smu_zcn2_t__scf_smn__ScfSmnRouterR2_VSOC_ScfSmnRouterR1_VSOC_flit_RespFlitData__15 ]
             set_output_delay  600 -clock [get_clocks {virtual_thru_SMNCLK_r}] -max [get_ports {FE_FEEDX_MFT__1__smu_zcn0_t__smu_zcn2_t__scf_smn__ScfSmnRouterR2_VSOC_ScfSmnRouterR1_VSOC_flit_RespFlitData__15}]

             ## relax reason: i2r group, slack is about 3-50ps ,input delay is huge
             remove_input_delay [get_ports XBAR_ZCN_s_axi_arid[12]]
             set_input_delay  1000 -clock [get_clocks {virtual_from_ZCNCLK_r_combo12}] -max -add_delay [get_ports {XBAR_ZCN_s_axi_arid[12]}]
             remove_input_delay [get_ports {XBAR_ZCN0_m_axi_rdata[216]}]
             set_input_delay  500 -clock [get_clocks {virtual_from_ZCNCLK_r}] -max [get_ports {XBAR_ZCN0_m_axi_rdata[216]}]
     '''
     #with open(rundir+"tune/DgSynthesize/DgSynthesize.beforeCompile1.tcl","w") as fp:
     #    fp.write(DgSynthesizebeforeCompile1)

