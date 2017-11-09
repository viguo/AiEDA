
def json2def(jsonFile, ecoFile):
    #support componets only

    tile = """VERSION 5.7 ;
DIVIDERCHAR "/" ;
BUSBITCHARS "[]" ;
DESIGN smu_zcn1_t ;
UNITS DISTANCE MICRONS 2000 ;
COMPONENTS 100 ; """
    defHash = load_json(jsonFile)

    with open(ecoFile,"w") as fp:

        fp.writelines(tile + "\n")
        for dict_key in defHash.keys():
            if dict_key == "ADD":
                print "not suport add cell"
            elif dict_key == "CHANGE":
                for instName in defHash[dict_key].keys():
                    setStatus = "set_placement_status placed [get_flat_cell  "+ instName + " ]"
                    location = " ".join(defHash[dict_key][instName]["LOCATION"])
                    #print "oritation: ", type(defHash[dict_key][instName]["ORITATION"])
                    #print "instName:", type(instName)
                    defLine = " - " + instName + " " +  defHash[dict_key][instName]["REFNAME"]  + \
                              " + " +  defHash[dict_key][instName]["STATUS"] +  \
                              " ( " + location + " ) " + defHash[dict_key][instName]["ORITATION"] + " ;"
                    #setRef    = "size_cell "+ instName + defHash[dict_key][instName]["REFNAME"]
                    #setLocation = "move_object [get_flat_cell" + instName + "]" + "-to" + "{" + +"}"
                    #setLocation = "move_object [get_flat_cell " + instName + "]" + " -to" + " { "  + location + " } "
                    fp.writelines(defLine + "\n" )
                    #fp.writelines(defHash[dict_key][instName]["LOCATION"])

                    #fp.write(setRef)
                    #fp.write(setLocation + "\n")
        fp.writelines("END COMPONENTS" + "\n" + "END DESIGN" + "\n")